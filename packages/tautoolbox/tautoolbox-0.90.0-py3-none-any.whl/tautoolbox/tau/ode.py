# Copyright (C) 2021-2025, University of Porto and Tau Toolbox developers.
#
# This file is part of Tautoolbox package.
#
# Tautoolbox is free software: you can redistribute it and/or modify it
# under the terms of version 3 of the GNU Lesser General Public License as
# published by the Free Software Foundation.
#
# Tau Toolbox is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.

from collections.abc import Iterable
from warnings import warn

import numpy as np
from numpy import linalg as lin
from scipy.linalg import lu
from scipy.optimize import fminbound

from ..polynomial.polynomial1 import Polynomial
from .matrix import chooseOperator
from .operator import Operator
from .problem import Problem
from .utils import linearSystemSolver

eps = np.spacing(1)  # the same as sys.float_info.epsilon


def solve(problem: Problem, **kwargs):
    if not isinstance(problem, Problem):
        raise TypeError("Tautoolbox: the input argument must be a tau.problem")

    if problem.kind == "fred1":
        return problem.kernel.fredholm1(problem.rhs, **kwargs)

    if problem.nequations == 1:
        if problem.isLinearized:
            return nonlinear(problem)
        return linear(problem)

    # solutions for systems
    if problem.isLinearized:
        return nonlinearSystem(problem)

    return linearSystem(problem)


def matrix(op, problem, h):
    op = chooseOperator(op)
    if not isinstance(problem, Problem):
        raise TypeError("Tautoolbox: the 2nd argument must be a tau.problem")

    # set definitions
    equations = problem.equations
    conditions = problem.conditions

    # define for convenience (shorter to type and read)
    nequations = problem.nequations
    n = problem.n

    nu = problem.nconditions
    h = np.max(problem.height)

    he = np.zeros(problem.nequations, dtype=int)
    for i in range(problem.nequations):
        he[i] = max(problem.height[i])
    he += 1
    cols = np.arange(n).reshape(1, -1) + (n + nu + h) * np.arange(nequations).reshape(-1, 1)

    if op in "condition c".split():
        return conditions_matrix_block(problem.basis, conditions, n)[0]

    x = Polynomial(basis=problem.basis)
    y = Operator(problem.basis, n + nu + h)

    if op in ["operator", "d"]:
        out = np.zeros((0, np.prod(cols.shape)))
        for neq in range(nequations):
            D = problem.equations[neq].lhs(x, y).mat
            rows = np.arange(n - problem.condpart[neq]).reshape(-1, 1)
            out = np.r_[out, D[rows, cols.reshape(1, -1)]]
        return out

    if op in ["taumatrix", "t"]:
        out = conditions_matrix_block(problem.basis, conditions, n)[0]
        for neq in range(nequations):
            D = problem.equations[neq].lhs(x, y).mat
            rows = np.arange(n - problem.condpart[neq]).reshape(-1, 1)
            out = np.r_[out, D[rows, cols.reshape(1, -1)]]
        return out

    if op in ["taurhs", "b"]:
        out = conditions_matrix_block(problem.basis, conditions, n)[1]
        for neq in range(nequations):
            rows = np.arange(n - problem.condpart[neq])
            out = np.r_[
                out, Polynomial.interp1p_coeff(equations[neq].rhs, rows[-1] + 1, problem.basis)
            ]
        return out.reshape(-1, 1)
    if op in ["tauresidual", "r"]:
        out = np.zeros((0, np.prod(cols.shape)))
        for neq in range(nequations):
            D = problem.equations[neq].lhs(x, y).mat
            rows = np.arange(n, n + 1 + he[neq]).reshape(-1, 1)
            out = np.r_[out, D[rows, cols.reshape(1, -1)]]
        return out
    if op in ["multiplication", "m"]:
        return problem.basis.matrixM(n + h)
    if op in ["differentiation", "n"]:
        return problem.basis.matrixN(n + h)
    if op in ["integration", "o"]:
        return problem.basis.matrixO(n + h)


def conditions_matrix_row(basis, cnd, n):
    C = np.zeros((len(cnd.coeff), n * cnd.nvars), dtype=basis.dtype)

    for j in range(len(cnd.coeff)):
        if not (basis.domain[0] <= cnd.point[j] <= basis.domain[1]):
            continue

        idx = (cnd.var[j] - 1) * n + np.arange(n)

        C[j, idx] = cnd.coeff[j] * basis.vander(
            cnd.point[j], n, cnd.order[j], cnd.order[j]
        )

    return sum(C)


def conditions_matrix_block(basis, conds, n):
    nu = len(conds)
    if nu == 0:
        return np.array([], dtype=basis.dtype), np.array([], dtype=basis.dtype)

    C = np.zeros((nu, n * conds[0].nvars), dtype=basis.dtype)
    b = np.zeros(nu, dtype=basis.dtype)

    for k in range(nu):
        C[k] = conditions_matrix_row(basis, conds[k], n)
        b[k] = conds[k].value
    return C, b


def linear(problem):
    if not isinstance(problem, Problem):
        raise TypeError("Tautoolbox: the input argument must be a tau.problem")

    equation = problem.equations[0]
    n = problem.n
    nu = problem.nconditions
    h = problem.height[0][0]

    T = np.zeros((n + nu + n, n))

    C, bs = conditions_matrix_block(problem.basis, problem.conditions, n)

    D = equation.lhs(Polynomial(basis=problem.basis), Operator(problem.basis, n + h)).mat
    T = np.r_[C, D[:, :n]]

    bf = Polynomial.interp1p_coeff(equation.rhs, n - nu, problem.basis)
    b = np.r_[bs, bf]

    yn = Polynomial(np.linalg.solve(T[:n], b), basis=problem.basis)

    residual_v = T[:n] @ yn.coeff - b
    tauresidual_v = T[n:] @ yn.coeff
    info = {
        "cond": lin.cond(T[:n, :n]),
        "residual": lin.norm(residual_v),
        "tauresidual": lin.norm(tauresidual_v),
    }

    return (
        yn,
        info,
        Polynomial(residual_v, basis=problem.basis),
        Polynomial(np.r_[np.zeros(n - nu), tauresidual_v], basis=problem.basis),
    )


def Schur(
    problem,
    InitialLU: int = 32,
    MaxDim: int = 256,
    Precision: float = 10 * eps,
    SizeBlock: int = 10,
):
    if not isinstance(problem, Problem):
        raise TypeError("Tautoolbox: the input argument must be a tau.problem")

    equation = problem.equations[0]
    conditions = problem.conditions

    N = MaxDim

    n = InitialLU
    m = SizeBlock
    nu = problem.nconditions

    T = np.zeros((N, N))
    b = np.zeros(N)

    C, b[:nu] = conditions_matrix_block(problem.basis, conditions, n)
    D = equation.lhs(Polynomial(basis=problem.basis), Operator(problem.basis, N))

    T[:nu] = C
    T[nu:] = D.mat[:-nu]
    b[nu:n] = Polynomial.interp1p_coeff(equation.rhs, n - nu, problem.basis)
    P, L, U = lu(T[:n, :n])
    a = lin.solve(U, lin.solve(L, P @ b[:n]))
    tau_res = lin.norm(T[n : n + 1 + m, :n] @ a)

    while tau_res > Precision and n + m <= MaxDim:
        n = n + m
        a = np.linalg.solve(T[:n, :n], b[:n])
        tau_res = lin.norm(T[n : n + m, :n] @ a)

    if tau_res > Precision:
        warn("Tautoolbox: Required accuracy not achieved. you may increase parameter MaxDim")

    return Polynomial(a, basis=problem.basis)


def linearSystem(problem):
    if not isinstance(problem, Problem):
        raise TypeError("Tautoolbox: the input argument must be a tau.problem")

    equations = problem.equations
    conditions = problem.conditions

    nequations = problem.nequations
    n = problem.n
    nu = problem.nconditions

    # incorporate the conditions in the system matrix and independent vector
    C, bs = conditions_matrix_block(problem.basis, conditions, n)

    T = C
    b = bs

    h = np.max(problem.height)
    cols = np.arange(n).reshape(1, -1) + (n + nu + h) * np.arange(nequations).reshape(-1, 1)

    for neq in range(nequations):
        x = Polynomial(basis=problem.basis)
        y = Operator(problem.basis, n + nu + h, problem.nequations)
        D = problem.equations[neq].lhs(x, y).mat

        rows = np.arange(n - problem.condpart[neq]).reshape(-1, 1)
        T = np.r_[T, D[rows, cols.reshape(1, -1)]]

        b = np.r_[
            b, Polynomial.interp1p_coeff(equations[neq].rhs, rows[-1, 0] + 1, problem.basis)
        ]  # rows[-1, 0] + 1

    # Solving the associated linear system

    coeffs = linearSystemSolver(T, b, problem.nequations)
    return Polynomial(coeffs, basis=problem.basis)


def fredholm1(funs, method="tsve", delta=1e-2, eta=1):
    r"""
    Compute the solution of Fredholm integral  equation of the first kind.

    Parameters
    ----------
    funs : Iterable
        The three functions. The first is a Polynomial2 representing k(s,t),the
        second is a Polynomial representing x(t) and the third is a Polynomial
        representing g(s)
    method : TYPE, optional
        The method to solve the equation. Can be either 'tsve' or 'tr'.
        The default is 'tsve'.
    delta : TYPE, optional
        DESCRIPTION. The default is 1e-2.

    Raises
    ------
    TypeError
        DESCRIPTION.

    Returns
    -------
    None.

    Notes
    -----
    This compute the Fredholm integral equation of the first kind
    .. math::
        \int_{\Omega_1}k(s,t)x(t)dt=g(s), \quad s \in \Omega_2

    with a square integrable kernel k. The :math:`\Omega_i, i=1,2` are subsets
    of :math:`\mathbb{R}`.
    This equation is solved using truncated singular value expansion method
    (tsve) or Tikhonov regularization method.
    """
    if not (isinstance(funs, Iterable) and len(funs) == 3):
        raise TypeError("funs must be an Iterable with ")
    ke, f, g = funs

    # adding continuous noise to g
    noise = Polynomial.randnPol(g.basis, 0.01)  # generate noise
    ng = g.norm()  # compute norm of rhs

    noise = delta * noise * ng / noise.norm()  # adjust norm of the noise
    g_delta = g + noise  # add noise to rhs
    nnoise = noise.norm()  # compute norm of noise

    psi, ks, phi = ke.svd()
    rk = len(ks)  # maximal rank of the separable approximation
    if method == "tsve":
        beta = np.zeros([rk, 1])
        for i in range(rk):
            beta[i] = (phi[i] * g_delta).definite_integral() / ks[i]
            xk = psi[0 : i + 1] * beta[0 : i + 1]

            if ((ke.T * xk).sum(axis=1) - g_delta).norm() < eta * nnoise:
                break
        relative_error_TSVE = (xk - f).norm() / f.norm()
        return xk, relative_error_TSVE.item()

    elif method == "tr":

        def errlambda1(lam, sigma, gnoise, psi, ke, rk, eta, e, dd):
            beta = dd * sigma / (sigma**2 + lam**2)
            x = psi * beta.reshape(-1, 1)
            return abs((((ke.T * x).sum(1) - gnoise).norm()) ** 2 - eta**2 * e**2)

        dd = (phi * g_delta).sum()

        # Solving minimization problem for lambda
        eta = 1
        lam = fminbound(
            lambda x: errlambda1(x, ks, g_delta, psi, ke, rk, eta, nnoise, dd),
            0,
            2,
            xtol=1e-12,
        )
        beta2 = ks / (ks**2 + lam**2)
        # xtol = 1e-5
        beta = (dd * beta2).reshape(-1, 1)

        # Tikonov relative error
        xlam = psi * beta
        rel_error_tikhonov = (xlam - f).norm() / f.norm()
        return xlam, rel_error_tikhonov.item()
    else:
        raise ValueError("Possible methods are 'tsve' and 'tr")


def nonlinear(problem): ...


def nonlinearSystem(problem): ...
