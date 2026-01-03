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
from numbers import Number
from warnings import filterwarnings, warn

import numpy as np
import numpy.linalg as la
import scipy.sparse as sp
from scipy.linalg import lu, qz, solve_sylvester
from scipy.sparse import issparse, spdiags
from scipy.sparse.linalg import inv as spinv
from scipy.sparse.linalg import spsolve
from scipy.special import ellipj, ellipk

from ..polynomial import Polynomial, Polynomial2
from ..polynomial.bases import (
    ChebyshevT,
    chebt2ultra,
    family_basis,
    ultra1mx2chebt,
    ultraS_convertmat,
    ultraS_difmat,
    ultraS_multmat,
)
from ..polynomial.options import numericalSettings
from ..polynomial.polynomial2 import nodes
from ..utils import get_required_args_count
from .equation import Equation
from .operator2 import Operator2
from .options import settings

filterwarnings("ignore", message="spsolve is more efficient when sparse b ")
filterwarnings("ignore", message="splu converted its input to CSC format")
filterwarnings(
    "ignore",
    message="Changing the sparsity structure of"
    " a csr_matrix is expensive. lil_matrix is more efficient",
)


class Problem2:
    """Class that allows to analysed and then solve differential problems
    of functions of 2 variables"""

    def __init__(
        self,
        func,
        domain,
        conditions=None,
        options=None,
        tol=np.spacing(1),
    ):
        """
        A class for representing linear partial differential problems

        Parameters
        ----------
        func : callable
            An anonymous function representing the operator.
        domain : array_like
            A 2x2 array_like object representing the domain.
        bc : callable, Number or dict, optional
            A dictionary with the boundary conditions or a callable.
            If it is a Number assume a constant function.
            When bc are not given assumes Dirichlet zero condition.
        bases : iterable, optional
            An iterable with two strings elements representing the bases.
            The default is ["ChebyshevT"] * 2.
        tol : number, optional
            the tolerance. The default is np.spacing(1).


        Raises
        ------
        ValueError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        a Problem2 object.

        Notes
        _____
        This class solves linear PDEs on a rectangular domain that have
        unique and globally smooth solutions.

        There is two possible representation of the problem:

        PR = Problem2(func=lambda u: u.op(),...) construct the problem by the operator
        given by lambda u: u.op() acting on functions of two variables and ;


        PR) Problem2(func=lambda u,x,y: u.op(x,y),...) .

        Examples
        ________

        Poisson with zero Dirichlet conditions. lap(u(x,y)) =1:

        >>> domain = ((-1, 1),) * 2
        >>> problem = tau.Problem2(lambda u: u.diff((2, 0)) + u.diff((0, 2)) - 1, domain)

        Poisson equation with general Dirichlet condition and rhs
        lap(u(x,y)) =cos(x*y) with  lbc= -y^2, rbc = y^2 , ubc= x, dbc =x
        in the domain [-1,1]:

        >>> conditions = {
        ...     "lbc": lambda y: -(y**2),
        ...     "rbc": lambda y: y**2,
        ...     "ubc": lambda x: x,
        ...     "dbc": lambda x: x,
        ... }
        >>> problem = tau.Problem2(
        ...     lambda x, y, u: u.laplacian() - np.cos(x * y), domain, conditions
        ... )
        >>> u = tau.solve(problem)
        >>> u.plot()
        """
        self._ubc = None  # Up boundary condition
        self._lbc = None  # Left boundary condition(s).
        self._rbc = None  # Right boundary condition(s).
        self._dbc = None  # Down boundary condition(s).
        self.dim = None  # Size of the system (number of equations).
        self.scale = None  # Relative solution scale.
        self.coef = None  # Matrix storing constant coefficients.
        self.x_order = 0  # Diff order in the x-variable.
        self.y_order = 0  # Diff order in the y-variable.

        # Processing  x and y options
        if options is None:
            options = settings()

        if isinstance(options, Iterable):
            optx = options[0]
            opty = options[1]
        else:
            optx = options
            opty = options

        self.basis_x = family_basis(optx.basis, domain=domain[0])
        self.basis_y = family_basis(opty.basis, domain=domain[1])

        if func is None:

            def identity(u):
                "Identity function"
                return u

            func = identity

        # Set the identity operator on the domain
        if callable(func):
            if get_required_args_count(func) == 1:
                # The PDE has constant coefficients since the rhs depends on x,y
                x = Polynomial2(lambda x, y: x, bases=(self.basis_x, self.basis_y))
                self.rhs = -func(0 * x)

                u = Operator2(
                    Polynomial2(lambda x, y: x * y, bases=(self.basis_x, self.basis_y))
                )

                def fh(u):
                    return func(u) + self.rhs

                v = fh(u)
                A = v.jacobian
                # Low rank form of the partial differential operator.
                self.U, self.S, self.V = None, None, None
            elif get_required_args_count(func) == 2:
                raise ValueError("Did you mean mean an equation in x,y,u?")
            elif get_required_args_count(func) == 3:
                x = Polynomial2(lambda x, y: x, bases=(self.basis_x, self.basis_y))
                y = Polynomial2(lambda x, y: y, bases=(self.basis_x, self.basis_y))
                u = Operator2(
                    Polynomial2(lambda x, y: x * y, bases=(self.basis_x, self.basis_y))
                )

                self.rhs = -func(x, y, 0 * x)

                def fh(x, y, u):
                    return func(x, y, u) + self.rhs

                v = fh(x, y, u)

                A = v.jacobian
                # Low rank form of the partial differential operator
                self.U, self.S, self.V = Problem2.separable_format(A, *(A.shape), bases=x.bases)
            else:
                raise ValueError("The problem equation must depend either on u or on x,y,u")
        else:
            raise TypeError(
                "The first argument must be a function representing the problem equation"
            )
        # Sometimes the coefficients are obtained with small rounding errors
        # so is important to remove the very small to have the correct rank(A)

        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if isinstance(A[i, j], Number) and np.abs(A[i, j]) < 10 * tol:
                    A[i, j] = 0

        self.prob = fh
        self.coef = A

        if conditions is not None:
            self.bc = conditions

        # Compute x_order of the PDE
        # Find the differential order of the PDE
        all_numbers = all([isinstance(el, Number) for els in A for el in els])
        if not all_numbers:
            self.x_order = A.shape[1] - 1
            self.y_order = A.shape[0] - 1
        elif min(A.shape) > 1:
            self.x_order = np.max(np.argwhere(np.sum(np.abs(A), axis=0) > 100 * tol))
            self.y_order = np.max(np.argwhere(np.sum(np.abs(A), axis=1) > 100 * tol))
        else:
            if A.shape[0] == 1:
                self.x_order = 0
                self.y_order = A.shape[1] - 1
            else:
                self.x_order = A.shape[0] - 1
                self.y_order = 0

    @property
    def domain(self):
        return np.array([self.basis_x.domain, self.basis_y.domain])

    @property
    def bases(self):
        return self.basis_x, self.basis_y

    @property
    def bc(self):
        return {
            "lbc": self._lbc,
            "rbc": self._rbc,
            "dbc": self._dbc,
            "ubc": self._ubc,
        }

    @bc.setter
    def bc(self, cond):
        domain = self.domain

        # This is when the problem has zero Dirichlet boundary condition.
        if isinstance(cond, str):
            cond = cond.lower()
            if cond != "dirichlet":
                raise ValueError("When boundary condition is a string it must be 'dirichlet'.")
            cond = 0
        if isinstance(cond, Number):
            self.lbc = self.rbc = self.ubc = self.dbc = cond

        # Evaluate the Polynomial 2 along the boundaries.
        # This means general Dirichlet boundary conditions.
        elif isinstance(cond, Polynomial2):
            self.lbc = cond(domain[0, 0], None)
            self.rbc = cond(domain[0, 1], None)
            self.ubc = cond(None, domain[1, 1])
            self.dbc = cond(None, domain[1, 0])

        # Construct lambda functions  along the boundaries in one variable.
        # This also means general Dirichlet boundary conditions.
        elif callable(cond):
            if get_required_args_count(cond) == 2:
                self.lbc = lambda y: cond(domain[0, 0], y)
                self.rbc = lambda y: cond(domain[0, 1], y)
                self.ubc = lambda x: cond(x, domain[1, 1])
                self.dbc = lambda x: cond(x, domain[1, 0])

            else:
                raise ValueError(
                    "When a callable is passed to the method bc t must have two arguments."
                )
        # This is when you specify the boundary conditions as e.g.
        # bc={'lbc': 'dirichlet', 'rbc': lambda x: x**2,'dbc':'neumann'}.
        elif isinstance(cond, dict):
            self.lbc = cond.get("lbc", None)
            self.rbc = cond.get("rbc", None)
            self.dbc = cond.get("dbc", None)
            self.ubc = cond.get("ubc", None)
        else:
            raise TypeError(
                "bc only can be passed a callable with two arguments a scalar or a dict."
            )

    @property
    def lbc(self):
        return self._lbc

    @lbc.setter
    def lbc(self, lbc):
        domain = self.domain[1]
        self._lbc = process_ind_bc(lbc, domain)

    @property
    def rbc(self):
        return self._rbc

    @rbc.setter
    def rbc(self, rbc):
        domain = self.domain[1]
        self._rbc = process_ind_bc(rbc, domain)

    @property
    def dbc(self):
        return self._dbc

    @dbc.setter
    def dbc(self, dbc):
        domain = self.domain[0]
        self._dbc = process_ind_bc(dbc, domain)

    @property
    def ubc(self):
        return self._ubc

    @ubc.setter
    def ubc(self, ubc):
        domain = self.domain[0]
        self._ubc = process_ind_bc(ubc, domain)

    def ispoisson(self):
        """
        Determine whether the PDE represents a Poisson equation.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        A = self.coef
        all_numbers = all([isinstance(el, Number) for els in A for el in els])
        if not all_numbers:
            return False
        m, n = A.shape

        return (
            m >= 3
            and n >= 3
            and len(np.argwhere(A != 0)) == 2
            and A[2, 0] == 1
            and A[0, 2] == 1
        )

    @staticmethod
    def _setup_laplace(basis_x, basis_y):
        return Problem2(lambda u: u.laplacian(), options=(basis_x, basis_y))

    @staticmethod
    def separable_format(A, x_order, y_order, bases):
        domain = np.array([bases[0].domain, bases[1].domain])

        n = 10
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if isinstance(A[i, j], Polynomial2):
                    x_n, y_n = A[i, j].shape
                    n = max(x_n, y_n, n) + 1

        # Get the needed Chebyshev nodes
        x = nodes(x_order + 1)
        s = nodes(n, domain[0])
        y = nodes(y_order + 1)
        t = nodes(n, domain[1])

        xx, ss, yy, tt = np.meshgrid(x, s, y, t, indexing="ij")
        newx, newy = np.meshgrid(s, t)

        H = 0 * xx
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if isinstance(A[i, j], Number) and A[i, j] != 0:
                    H = H + A[i, j] * xx**j * yy**i
                elif isinstance(A[i, j], Polynomial2):
                    v = np.zeros((1, n, 1, n))
                    v[0, :, 0, :] = A[i, j](newx, newy).T
                    out = np.tile(v, (x_order + 1, 1, y_order + 1, 1))
                    H = H + out * xx**j * yy**i

        A = H.reshape(n * (x_order + 1), n * (y_order + 1), order="F")

        u, s, vh = la.svd(A)
        rk = np.sum(s / s[0] > 1000 * np.spacing(1))
        s = s[:rk]
        u = u[:, :rk]
        vh = vh[:rk, :]
        # We have the splitting rank of the PDO, now we want the corresponding
        # separable representation. The following is tricky to get right...
        arr_u = np.zeros((y_order + 1, rk), dtype="O")
        arr_v = np.zeros((x_order + 1, rk), dtype="O")

        # Matrices to convert ChebT -> monomials:
        converty = Polynomial(np.eye(y_order + 1)).power_coef
        convertx = Polynomial(np.eye(x_order + 1)).power_coef
        bases_d = ((ChebyshevT(domain=(-1, 1)),)) * 2
        for i in range(rk):
            # This is giving  us the 1D ODEs that go on the right in the generalized
            # Sylvester matrix equation:
            f1 = Polynomial2.vals_to_coef(u[:, i].reshape(x_order + 1, n, order="F"), bases_d)
            f1 = f1.T @ convertx
            for j in range(x_order + 1):
                arr_v[j, i] = Polynomial(f1[:, j], domain=domain[0])

            # This is giving  us the 1D ODEs that go on the left in the generalized
            # Sylvester matrix equation:
            f2 = Polynomial2.vals_to_coef(vh[i, :].reshape(y_order + 1, n, order="F"), bases_d)
            f2 = f2.T @ converty
            for j in range(x_order + 1):
                arr_u[j, i] = Polynomial(f2[:, j], domain=domain[1])
        return arr_u, s, arr_v

    def solve(self, rhs=None, m=None, n=None):
        if rhs is not None:
            au = self.rhs

            if isinstance(rhs, (Polynomial2, Number)):
                self.rhs = self.rhs + rhs

            elif callable(rhs):
                if get_required_args_count(rhs) != 2:
                    raise ValueError("When rhs is a lambda function it must have 2 arguments.")
                self.rhs = self.rhs + Polynomial2(rhs, bases=(self.basis_x, self.basis_y))

            else:
                raise TypeError(
                    "The right hand side of the equation must be a "
                    "Polynomial2, a callable with two arguments or a number"
                )

        tol = 1e-14

        max_discretise_x = max_discretise_y = 1026
        min_sample = 9

        if m is not None:
            if not isinstance(m, Number):
                raise TypeError(f"'m' must be a positive integer was given '{m}")
            elif m < 1 or int(m) != m:
                raise ValueError(f"'m' must be a positive integer was given '{m}")

        if n is not None:
            if not isinstance(n, Number):
                raise TypeError(f"'n' must be a positive integer was given '{n}")
            elif n < 1 or int(n) != n:
                raise ValueError(f"'n' must be a positive integer was given '{n}")

        # find out what grid to start, and witch directions to do adaptivity.
        if m is None and n is None:
            # Adaptive solver in both directions
            m = n = min_sample
            adaptive_x = adaptive_y = True

        elif m is None:
            m = min_sample
            adaptive_x, adaptive_y = False, True
            max_discretise_x = n + 1
        elif n is None:
            n = min_sample
            adaptive_x, adaptive_y = True, False
            max_discretise_y = m + 1
        else:
            adaptive_x = adaptive_y = False
            max_discretise_x, max_discretise_y = n + 1, m + 1

        # Adaptive solver

        Resolved_x = Resolved_y = False
        Resolved = Resolved_x and Resolved_y
        # Get the resolution of the BCs?
        bctype, g = self.__check_bc(2, 2)

        while not Resolved and m < max_discretise_y and n < max_discretise_x:
            x = self.dense_solve(m, n)

            old_m, old_n = m, n

            if adaptive_y:
                # Resolved in the y-direction?
                Resolved_y, m = resolved_check(
                    x.T, old_m, old_n, tol, self.lbc, self.rbc, bctype
                )
            else:
                Resolved_y = True

            if adaptive_x:
                # Resolved in the x-direction?
                Resolved_x, n = resolved_check(x, old_n, old_m, tol, self.dbc, self.ubc, bctype)
            else:
                Resolved_x = True

            # Update the tolerances

            tol = update_tolerance(tol, m, n)
            Resolved = Resolved_x & Resolved_y

        # Did we stop without resolving
        if m > max_discretise_y or n > max_discretise_x:
            warn("Problem2:solve: Maximum discretization reached without an accurate solution.")

        u = Polynomial2(x, bases=(self.basis_x, self.basis_y))
        if len(u) > 50:
            rk = np.sum(u.diag > 6e-15)

            u.diag = u.diag[:rk]
            u.cols = u.cols[:rk]
            u.rows = u.rows[:rk]
        if rhs is not None:
            self.rhs = au
        return u

    def __check_bc(self, m, n):
        bctype = 0
        g = None

        ltype, lbc = get_bc(self.lbc, self.basis_y)
        rtype, rbc = get_bc(self.rbc, self.basis_y)
        dtype, dbc = get_bc(self.dbc, self.basis_x)
        utype, ubc = get_bc(self.ubc, self.basis_x)

        if all([ltype, rtype, dtype, utype]) and check_corners(lbc, rbc, dbc, ubc):
            bctype = 1
            g = interp_bc(lbc, rbc, dbc, ubc, m, n)
        return bctype, g

    def poisson(self, rhs, bc=None, grid_shape=None, method=None):
        r"""
        Fast solver for Poisson equation. Let :math:`p` be a Polynomial2
        approximation of a function :math:`f` in two independent variables and
        :math:`u` an unknown function in the same variables, this method is a
        fast approximation of the Poisson equation:

        .. math::
            \nabla^2u=f

        Parameters
        ----------
        bc : scalar,Polynomial2,dict, optional
            The boundary conditions. When not given we assume Dirichlet zero
            boundary conditions, The default is None.
        grid_shape : integer, tuple or list, optional
            The size of the polynomial in y and x direction. When not given
            we assume an adaptive grid. The default is None.
        method : str, optional
            The method to be used to solve the problem. When not given it chooses
            the best suitable method between 'adi' and 'fadi'
            The default is None.
        Raises
        ------
        ValueError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        Polynomial2
            The approximate solution of the problem.

        """

        domain = rhs.domain
        x_scale = (2 / (domain[0, 1] - domain[0, 0])) ** 2
        y_scale = (2 / (domain[1, 1] - domain[1, 0])) ** 2

        if bc is None:
            N = Problem2._setup_laplace(rhs.basis_x, rhs.basis_y)
            N.bc = 0
            N.rhs = rhs.copy()
            return N.solve(*grid_shape)

        if grid_shape is None:
            N = Problem2._setup_laplace(domain)
            N.bc = bc
            N.rhs = rhs.copy()
            return N.solve()

        if np.isscalar(grid_shape):
            # In this case imply a N*N discretization grid
            m = grid_shape
            if m < 1 or int(m) != m:
                raise ValueError(
                    "grid_shape must be an array_like object with "
                    " two positive positive integers or a positive integer"
                )
            m = n = int(m)

        elif isinstance(grid_shape, Iterable):
            if len(grid_shape) == 2 and all([np.isscalar(el) for el in grid_shape]):
                m, n = grid_shape
                if m < 1 or n < 1 or int(n) != n or int(m) != m:
                    raise ValueError(
                        "grid_shape must be an array_like object with "
                        " two positive positive integers or a positive integer"
                    )
                m, n = int(m), int(n)
            else:
                raise ValueError(
                    "grid_shape must be an array_like object with "
                    " two positive positive integers or a positive integer"
                )
        else:
            raise ValueError(
                "grid_shape must be an array_like object with "
                " two positive positive integers or a positive integer"
            )

        # Compute the coefficients of the right hand side
        tol = numericalSettings.defaultPrecision
        Cp, Dp, Rp = rhs.get_coef(dims=(m, n), fact=True)

        if isinstance(bc, Number) or callable(bc):
            bc = Polynomial2(bc, bases=rhs.bases)

        if not isinstance(bc, Polynomial2):
            raise TypeError("The boundary condition must be a Number or a function")

        if bc.basis_x != rhs.basis_x or bc.basis_y != rhs.basis_y:
            raise ValueError(
                "The boundary condition and the function must have the same domain"
            )

        lap_bc = bc.laplacian()

        if not lap_bc.iszero():
            Cbc, Dbc, Rbc = lap_bc.get_coef(dims=(m, n), fact=True)
            Cp = np.r_[Cp, Cbc]
            Dp = np.r_[Dp, -Dbc]
            Rp = np.r_[Rp, Rbc]

        # Convert the rhs to C**(3/2) coefficients

        Cp = chebt2ultra(Cp)
        Rp = chebt2ultra(Rp)
        # Construct M, the multiplication matrix for (1-x**2) in the basis
        # C**(3/2)
        jj = np.r_[0:n]
        dsub = -1 / (2 * (jj + 3 / 2)) * (jj + 1) * (jj + 2) * 1 / 2 / (5 / 2 + jj)
        dsup = -1 / (2 * (jj + 3 / 2)) * (jj + 1) * (jj + 2) * 1 / 2 / (1 / 2 + jj)
        d = -dsub - dsup
        Mn = spdiags(np.r_["0,2", dsub, d, dsup], [-2, 0, 2], n, n)
        # Construct D^{-1}, which undoes the scaling from the Laplacian identity
        InvDn = spdiags(-1 / (jj * (jj + 3) + 2), 0, n, n)

        # Construct T= Dn^(-1)*Mn
        Tn = y_scale * InvDn @ Mn

        jj = np.r_[0:m]
        dsub = -1 / (2 * (jj + 3 / 2)) * (jj + 1) * (jj + 2) * 1 / 2 / (5 / 2 + jj)
        dsup = -1 / (2 * (jj + 3 / 2)) * (jj + 1) * (jj + 2) * 1 / 2 / (1 / 2 + jj)
        d = -dsub - dsup
        Mm = spdiags(np.r_["0,2", dsub, d, dsup], [-2, 0, 2], m, m)

        # Construct D^{-1}, which undoes the scaling from the Laplacian identity
        InvDm = spdiags(-1 / (jj * (jj + 3) + 2), 0, m, m)

        # Construct T= Dm^(-1)*Mm
        Tm = x_scale * InvDm @ Mm
        # A = Basis(opty).matrixN(m) @ Cp.T
        # B = Basis(opty).matrixN(n) @ Rp.T
        Cp = InvDm @ Cp.T
        Rp = InvDn @ Rp.T

        if isinstance(method, str):
            method = method.lower()

        if method == "bartelsstewart":
            ######################################
            ######  Bartels-Stewart method  #######
            ######################################
            # Solve Tm@X + X@Tn.T = F using Bartels-Stewart, which requires O(n**3)
            # operations
            pass
        elif method is None or method in ("adi", "fadi"):
            ######################################################
            ######  Alternating direction implicit method  #######
            ######################################################
            # Solve Tm@X + XTn = F using Bartels-Stewart, which requires
            # O(n**2log(n)log(1/eps)) operations:

            # An ADI method will be used (either given by the user, or selected
            # by us.)

            # Compute Adi shifts
            a = -4 / np.pi**2 * y_scale
            b = -39 * n**-4 * y_scale
            c = 39 * m**-4 * x_scale
            d = 4 / np.pi**2 * x_scale

            [p, q] = Problem2.adiShifts(a, b, c, d, tol)

            if method is None:
                # Try to pick a good method to use
                # Test if we should use ADI or FADI
                rho = Cp.shape[1]  # Rank of rhs
                adi_test = min(m, n) < rho * p.size / 2  # Worth doing fadi
                method = "adi" if adi_test else "fadi"

            if method == "adi":
                # Use the ADI method
                X = Problem2.adi(Tm, -Tn.T, (Cp * Dp) @ Rp.T, p, q)
                # Convert back to ChebyshevT
                X = ultra1mx2chebt(ultra1mx2chebt(X).T).T

                u = Polynomial2(X, bases=rhs.bases)

            else:
                # Use the FADI method

                UX, DX, VX = Problem2.fadi(Tm, -Tn, Cp * Dp, Rp, p, q)

                UX, VX = ultra1mx2chebt(UX.T), ultra1mx2chebt(VX.T)
                u = Polynomial2()
                u.cols = Polynomial(UX, basis=rhs.basis_y)
                u.rows = Polynomial(VX, basis=rhs.basis_x)
                u.diag = DX

        else:
            raise ValueError("Invalid method supplied.")

        return u + bc

    def dense_solve(self, m, n):
        # Check if we can use a fast Poisson solver
        bctype, g = self.__check_bc(m, n)

        if self.ispoisson() and bctype == 1:
            u = self.poisson(self.rhs, bc=g, grid_shape=(m, n))
            return u.get_coef((m, n))
        else:
            # Use a general PDE solver

            # Construct discretization for PDE

            CC, RHS, bb, gg, Px, Py, xsplit, ysplit = self.discretize(m, n)

            # Rank-1 discretization PDE
            if CC.shape[0] == 1:
                A = CC[0, 0]
                B = CC[0, 1]
                Y = la.solve(A, RHS)
                X = la.solve(B, Y.T).T
                X = impose_boundary_conditions(X, bb, gg, Px, Py, m, n)

            # rank-2 PDE operator
            elif CC.shape[0] == 2:
                # Extract out generalized matrix equation
                A = CC[0, 0]
                B = CC[0, 1]
                C = CC[1, 0]
                D = CC[1, 1]

                # Don't solve for sub-problems if we have lots of bcs on one edge
                if any(min(el.shape) > 1 for el in bb):
                    warn(f"{xsplit=} {ysplit=}")
                    xsplit = 0
                    ysplit = 0

                # xsplit and ysplit tell the solver if it is possible to solve
                # sub-problems. Wrap in a try-catch statement in case LYAP is not on the
                # MATLAB path.

                X = solve_sylvester(
                    spsolve(C, A).toarray(),
                    spsolve(B, D).T.toarray(),
                    spsolve(B, spsolve(C, RHS).T).T,
                )
                # X = Problem2.bartelsStwart(A, B, C, D, RHS, xsplit, ysplit)
                if np.linalg.norm(X.imag, np.inf) < np.sqrt(np.spacing(1)):
                    X = X.real

                # Impose the boundary conditions

                X = impose_boundary_conditions(X, bb, gg, Px, Py, m, n)
            else:
                # Do full n**2 by n**2 matrix Kronecker product
                # Make a massive mn x mn matrix
                sz = CC[0, 0].shape[0] ** CC[0, 1].shape[1]
                if sz > 65**2:
                    raise ValueError("Solution unresolved on 65x65 grid.")

                A = np.zeros(sz, sz)
                for j in len(CC):
                    A = A + np.kron(CC[j, 1], CC[j, 0])

            return X

    @staticmethod
    def adi(A, B, F, p, q):
        """
        Solves the Silvester equation A*X + X*B =F using the ADI method
        where p and q are the shift parameters

        Parameters
        ----------
        A : Array_like
            DESCRIPTION.
        B : Array_like
            DESCRIPTION.
        F : TYPE
            DESCRIPTION.
        p : TYPE
            DESCRIPTION.
        q : TYPE
            DESCRIPTION.

        Returns
        -------
        X : TYPE
            DESCRIPTION.

        Reference
        ---------
        [1] Lu, An, and Eugene L. Wachspress.
         "Solution of Lyapunov equations by alternating direction implicit iteration."
         Comp. & Math. with Appl., 21.9 (1991): pp. 43-58.
        """
        m = A.shape[0]

        n = B.shape[0]
        X = np.zeros((m, n))
        Im = sp.eye(m)
        In = sp.eye(n)

        for i in range(p.size):
            X = (F - (A + q[i] * Im) @ X) @ spinv(B + q[i] * In)

            X = spsolve(A + p[i] * Im, F - X @ (B + p[i] * In))

        return X

    def adiShifts(a, b, c, d, e, tol=numericalSettings.defaultPrecision):
        gam = (c - a) * (d - b) / (c - b) / (d - a)  # Cross-ratio of a,b,c,d

        # Compute Mobius transform T:{-alp,-1-1,alp} -> {a,b,c,d} form some alp:
        alp = -1 + 2 * gam + 2 * np.sqrt(gam**2 - gam)
        A = la.det([[-a * alp, a, 1], [-b, b, 1], [c, c, 1]])
        B = la.det([[-a * alp, -alp, a], [-b, -1, b], [c, 1, c]])
        C = la.det([[-alp, a, 1], [-1, b, 1], [1, c, 1]])
        D = la.det([[-a * alp, -alp, 1], [-b, -1, 1], [c, 1, 1]])

        def T(z):
            return (A * z + B) / (C * z + D)

        J = np.ceil(np.log(16 * gam) * np.log(4 / tol) / np.pi**2)

        if alp > 1e7:
            result = 2 * np.log(2) + np.log(alp)
            K = result + (-1 + result) / alp**2 / 4
            u = np.r_[1 / 2 : J] * K / J
            sech = 1 / np.cosh(u)
            dn = sech + (np.sinh(u) * np.cosh(u) + u) * np.tanh(u) * sech / (4 * alp**2)
        else:
            K = ellipk(1 - 1 / alp**2)
            [_, _, dn, _] = ellipj(np.r_[1 / 2 : J] * K / J, 1 - 1 / alp**2)

        return T(-alp * dn), T(alp * dn)

    @staticmethod
    def fadi(A, B, M, N, p, q):
        """
        Solves the Sylvester equation
        A @ X - X @ B =M @ N.T using the fadi  method with adi shifts p and q.
        The righthand side must be given  in low-rank form, i.e. M and N where
        rhs=M @ N

        Parameters
        ----------
        A : TYPE
            DESCRIPTION.
        B : TYPE
            DESCRIPTION.
        M : TYPE
            DESCRIPTION.
        N : TYPE
            DESCRIPTION.
        p : TYPE
            DESCRIPTION.
        q : TYPE
            DESCRIPTION.

        Returns
        -------
        A : TYPE
            DESCRIPTION.
        B : TYPE
            DESCRIPTION.
        M : TYPE
            DESCRIPTION.

        Reference
        ---------
        [1] Benner, Peter, Ren-Cang Li, and Ninoslav Truhar.
        "On the ADI method for Sylvester equations." J. of Comp. and App. Math.
         233.4 (2009): 1035-1045.

        """
        m, rho = M.shape
        n = N.shape[0]
        sol_rank = rho * p.size
        UX = np.zeros((m, sol_rank))
        VX = np.zeros((n, sol_rank))
        DX = np.kron(q - p, np.ones(rho))
        Im = sp.eye(m)
        In = sp.eye(n)

        UX[:, :rho] = spsolve(A + p[0] * Im, M).reshape(-1, rho)
        VX[:, :rho] = spsolve(B + q[0] * In, N).reshape(-1, rho)
        for i in range(p.size - 1):
            UX[:, (i + 1) * rho : (i + 2) * rho] = (
                (A + q[i] * Im) @ spsolve(A + p[i + 1] * Im, UX[:, i * rho : (i + 1) * rho])
            ).reshape(-1, rho)
            VX[:, (i + 1) * rho : (i + 2) * rho] = (
                (B + p[i] * In) @ spsolve(B + q[i + 1] * In, VX[:, i * rho : (i + 1) * rho])
            ).reshape(-1, rho)

        return UX, DX, VX

    @staticmethod
    def bartelsStwart(A, B, C, D, E, x_split, y_split):
        """
        Compute the solution to the generalized Silvestre matrix equation
        AXB^T + CXD^T =E. This method is based in Gardiner et all. (1992)

        Parameters
        ----------
        A : array_like
            An array representing the matrix A in the above equation
        B : array_like
            An array representing the matrix B in the above equation
        C : array_like
            An array representing the matrix C in the above equation
        D : array_like
            An array representing the matrix D in the above equation
        E : array_like
            An array representing the matrix E in the above equation
        x_split : bool
            DESCRIPTION.
        y_split : bool
            DESCRIPTION.

        Returns
        -------
        None.
        """

        tol = numericalSettings.defaultPrecision
        if la.norm(E) < 10 * tol:
            return np.zeros_like(E)

        if sp.issparse(A):
            A = A.toarray()
        if sp.issparse(B):
            B = B.toarray()
        if sp.issparse(D):
            D = D.toarray()

        if sp.issparse(C):
            C = C.toarray()

        # If the equation is even/odd in the x-direction then we can split the problem
        # into two sub-problems. We enforce P and S as upper triangular because they
        # are up to rounding errors, and we need to do back substitution with
        # them.

        if y_split:
            P, S, Q1, Z1 = qzsplit(A, C)

            P = np.triu(P)
            S = np.triu(S)
        else:
            P, S, Q1, Z1 = qz(A, C, output="complex")
            Q1 = Q1.T

            P = np.triu(P)
            S = np.triu(S)

        # If the PDE is even/odd in the y-direction then we can split (further)
        # into double as many sub-problems.
        if A.shape[1] < 10:
            print(D)
            print(B)

        if x_split:
            T, R, Q2, Z2 = qzsplit(D, B)

        else:
            T, R, Q2, Z2 = qz(D, B, output="complex")
            Q2 = Q2.T

        # Now use the generalised Bartels--Stewart solver found in Gardiner et al.
        # (1992).  The Sylvester matrix equation now contains quasi upper-triangular
        # matrices and we can do a backwards substitution.

        # transform the right hand side
        F = Q1 @ E @ Q2.T

        # The solution will be a m*n matrix
        m, n = A.shape[0], B.shape[0]
        Y = np.zeros((m, n), dtype=complex)

        # Do a backwards substitution type algorithm to construct the solution.
        k = n - 1
        PY = np.zeros((m, n), dtype=complex)
        SY = np.zeros((m, n), dtype=complex)

        # Construct columns n,n-1,...,3,2 of the transformed solution.  The first
        # column is treated as special at the end.

        while k > 0:
            if T[k, k - 1] == 0:
                # Simple case (almost always end up here)
                rhs = F[:, k]

                if k < n - 1:
                    P @ Y[:, k + 1]
                    PY[:, k + 1] = P @ Y[:, k + 1]
                    SY[:, k + 1] = S @ Y[:, k + 1]

                    for j in range(k + 1, n):
                        rhs = rhs - R[k, j] * PY[:, j] - T[k, j] * SY[:, j]

                # Find the kth column of the transformed solution

                Y[:, k] = la.solve(R[k, k] * P + T[k, k] * S, rhs)

                # Go the the next column
                k -= 1
            else:
                # This is a straight copy from the Gardiner et al. paper, and just
                # solves for two columns at once. (works because of
                # quasi-triangular matrices.

                # Operator reduction.
                rhs1, rhs2 = F[:, k - 1], F[:, k]

                for j in range(k + 1, n):
                    yj = Y[:, j]

                    rhs1 = rhs1 - R[k - 1, j] * P @ yj - T[k - 1, j] * S @ yj
                    rhs2 = rhs2 - R[k, j] * P @ yj - T[k, j] * S @ yj

                # 2 by 2 system
                SM = np.zeros((2 * n, 2 * n))
                up = slice(0, n)
                down = slice(n, 2 * n)

                SM[up, up] = R[k - 1, k - 1] * P + T[k - 1, k - 1] * S
                SM[up, down] = R[k - 1, k] * P + T[k - 1, k] * S
                SM[down, up] = R[k, k - 1] * P + T[k, k - 1] * S
                SM[down, down] = R[k, k] * P + T[k, k] * S

                # Permute the columns and rows
                Sper = np.zeros((2 * n, 2 * n))
                Sper[: 2 * n : 2, : 2 * n : 2] = SM[:n, :n]
                Sper[1 : 2 * n : 2, 1 : 2 * n : 2] = SM[n : 2 * n, n : 2 * n]

                # Solve

                UM = la.solve(Sper, np.r_[rhs1, rhs2])

                Y[:, k - 1] = UM[up]
                Y[:, k] = UM[down]

                PY[:, k] = P @ Y[:, k]
                PY[:, k - 1] = P @ Y[:, k - 1]
                SY[:, k] = S @ Y[:, k]
                SY[:, k - 1] = S @ Y[:, k - 1]

                # We solved for two columns so go two columns further
                k -= 2

        if k == 0:
            rhs = F[:, 0]

            PY[:, 1] = P @ Y[:, 1]
            SY[:, 1] = S @ Y[:, 1]

            for j in range(1, n):
                rhs = rhs - R[0, j] * PY[:, j] - T[0, j] * SY[:, j]

            Y[:, 0] = la.solve(R[0, 0] * P + T[0, 0] * S, rhs)

        return Z1 @ Y @ Z2.T

    @staticmethod
    def fredholm1(kernel, rhs, options=None, **kwargs):
        r"""
        Compute the solution of Fredholm integral  equation of the first kind
        with the kernel ``kernel``.


        Parameters
        ----------
        kernel : callable
            A callable with two arguments
        rhs : Polynomial.
            The right hand side of the first equation (see notes).
        options : Iterable
            An iterable with two elements that are the options for the first
            variable and the second variable.
        **kwargs :
            method : str, optional
                The method to use for solving the equation. The default is "tsve".
            delta : scalar, optional
                The noise level. The default is 1e-2.
            eta : scalar, optional
                Haves to do with the last equation in the notes (see notes). The de
                fault is 1.

        Returns
        -------
        Polynomial
            The approximate solution.


        Notes
        -----
        This compute the Fredholm integral equation of the first kind

        .. math::
            \int_{\Omega_1}k(s,t)x(t)dt=g(s), \quad s \in \Omega_2
        with a square integrable kernel k. The :math:`\Omega_i, i=1,2` are subsets
        of :math:`\mathbb{R}`.
        This equation is solved using truncated singular value expansion method
        (tsve) or  Tikhonov regularization method. The parameters ``delta`` and
        ``eta`` have to do with this equation:

        .. math::
            \left\|\int_{\Omega_1}k(s,t)x(t)-g^{\delta}(s)\right\|=\eta\delta

        """

        if isinstance(kernel, Polynomial2):
            return kernel.fredholm1(rhs, **kwargs)
        kernel = Polynomial2(kernel, options)
        return kernel.fredholm1(rhs, **kwargs)

    def discretize(self, m, n, flag=0):
        A = self.coef
        dom = self.domain
        tol = numericalSettings.defaultPrecision
        x_order, y_order = self.x_order, self.y_order

        # check if all the coefficients in the coefficients are constants
        doesNotDependOnXorY = all([isinstance(el, Number) for el in A.flatten()])
        if not doesNotDependOnXorY:
            A = A.copy().T

        if self.V is None or self.U is None:
            if not doesNotDependOnXorY:
                counter = 0
                U = {}
                V = {}

                for i in range(A.shape[0]):
                    for j in range(A.shape[1]):
                        a = A[i, j]
                        if isinstance(a, Polynomial2):
                            if a.vertical_scale > tol:
                                c, d, r = a.cdr()
                                for col in range(c.size):
                                    U[i, counter] = c[col] * d[col]
                                    V[j, counter] = r[col]
                                    counter += 1
                        elif abs(a) > tol:
                            U[i, counter] = a
                            V[j, counter] = 1
                            counter += 1

                na, rk = np.max(np.array(list(U.keys())), axis=0) + [1, 1]
                S = np.ones(rk)
                nb = (np.max(np.array(list(V.keys())), axis=0) + [1, 1])[0]
            else:
                # Compute the svd of the coefficient matrix
                U, S, V = la.svd(A.astype(float))
                V = V.T

                # Find the rank of A, which is also the rank of the PDE operator
                # and construct the low rank expansion of A.
                rk = np.max(np.argwhere(S > tol)) + 1
                S = S[:rk]
                U = U[:, :rk]
                V = V[:, :rk]
                nb, na = A.shape
        else:
            rk = len(self.S)
            U = self.U.copy()
            V = self.V.copy()
            S = self.S.copy()
            na, nb = U.shape[0], V.shape[0]

        # Left =np.zeros((m,m)); Right =np.zeros((n,n))
        # Construct the discretization in matrix equation form
        CC = np.zeros((rk, 2), dtype="O")
        for i in range(rk):
            RIGHT = unconstrained_matrix_equation(V, i, n, x_order, dom[0])
            LEFT = unconstrained_matrix_equation(U, i, m, y_order, dom[1])

            singval = np.sqrt(S[i])

            CC[i, 1] = singval * RIGHT

            CC[i, 0] = singval * LEFT

        # Test to see if we can solve sub-problems. This checks if the PDE operator
        # contains differential terms of the same parity.
        ysplit, xsplit = 0, 0
        if (
            isinstance(U, np.ndarray)
            and isinstance(V, np.ndarray)
            and all([isinstance(el, Number) for el in U.flatten()])
            and all([isinstance(el, Number) for el in V.flatten()])
        ):
            if min(la.norm(U[:na:2, :]), la.norm(V[1:na:2, :])) < 10 * tol:
                ysplit = 1

            if min(la.norm(U[:nb:2, :]), la.norm(V[1:nb:2, :])) < 10 * tol:
                xsplit = 1

        # We have a discretisation for the PDE operator, now let's find a
        # discretisation for the boundary conditions.

        # If no boundary conditions is prescribed then make it empty.

        bcLeft = bcRight = upVal = downVal = np.zeros((0, n))
        leftVal = rightVal = bcUp = bcDown = np.zeros((0, m))

        if self.lbc is not None:
            bcLeft, leftVal = construct_bc(self.lbc, -1, m, n, dom[1], dom[0], x_order)

        if self.rbc is not None:
            bcRight, rightVal = construct_bc(self.rbc, 1, m, n, dom[1], dom[0], x_order)
        if self.ubc is not None:
            bcUp, upVal = construct_bc(self.ubc, 1, n, m, dom[0], dom[1], y_order)
        if self.dbc is not None:
            bcDown, downVal = construct_bc(self.dbc, -1, n, m, dom[0], dom[1], y_order)

        # For the down and up BCs we have B^TX = g^T.
        By = np.r_["0,2", bcUp, bcDown]

        Gy = np.r_["0,2", upVal, downVal]

        By, Gy, Py = canonical_bc(By, Gy)

        # For the left and right BCs we have X*B = g. We do the LU to B^T.
        Bx = np.r_["0,2", bcLeft, bcRight]
        Gx = np.r_["0,2", leftVal, rightVal]

        Bx, Gx, Px = canonical_bc(Bx, Gx)
        # Transpose so that X@B = g
        Bx, Gx = Bx.T, Gx.T

        # Construct the RHS of the Sylvester matrix equation.
        E = np.zeros((m, n))
        n1, n2 = self.rhs.shape

        F = self.rhs.coef

        # Map the RHS to the right ultraspherical space.

        lmap = ultraS_convertmat(n1, 0, y_order - 1)
        rmap = ultraS_convertmat(n2, 0, x_order - 1)

        F = lmap @ F @ rmap.T

        # Map the RHS to the right ultraspherical space.
        n1, n2 = min(n1, m), min(n2, n)
        E[:n1, :n2] = F[:n1, :n2]

        # print(By, "\n\n", Gy, "\n\n", Bx.T, "\n\n", Gx.T, "\n\n")
        # Impose boundary conditions

        if not flag:
            # Use the eliminated boundary condition to place zeros in the co-
            # lumns of the matrix equation discretization. There are rk co-
            # lumns to zero out.
            for i in range(rk):
                C, E = zero_dof(CC[i, 0], CC[i, 1], E, By, Gy)
                CC[i, 0] = C
                C, E = zero_dof(CC[i, 1], CC[i, 0], E.T, Bx.T, Gx.T)
                CC[i, 1] = C
                E = E.T

            # Remove degrees of freedom
            nn = n - max(x_order, y_order)
            mm = m - max(x_order, y_order)
            df1 = max(0, x_order - y_order)
            df2 = max(0, y_order - x_order)

            for i in range(rk):
                CC[i, 0] = CC[i, 0][:mm, y_order : m - df1]
                CC[i, 1] = CC[i, 1][:nn, x_order : n - df2]

            # Truncation of right hand side
            rhs = E[:mm, :nn]
        else:
            rhs = E

        # Pass back the eliminated boundary conditions
        bb = [bcLeft, bcRight, bcUp, bcDown]
        gg = [leftVal, rightVal, upVal, downVal]

        # Check boundary continuity conditions.

        # check the bc at corners
        allbc = 0
        if (
            not bcUp.size == 0
            and not upVal.size == 0
            and not bcRight.size == 0
            and not rightVal.size == 0
        ):
            if la.norm(rightVal[-5:], np.inf) < np.sqrt(tol) and la.norm(
                upVal[-5:], np.inf
            ) < np.sqrt(tol):
                allbc += la.norm(upVal @ bcRight - bcUp @ rightVal)

        if (
            not bcUp.size == 0
            and not upVal.size == 0
            and not bcLeft.size == 0
            and not leftVal.size == 0
        ):
            if la.norm(leftVal[-5:], np.inf) < np.sqrt(tol) and la.norm(
                upVal[-5:], np.inf
            ) < np.sqrt(tol):
                allbc += la.norm(upVal @ bcLeft - bcUp @ leftVal)

        if (
            bcDown is not None
            and downVal is not None
            and bcRight is not None
            and rightVal is not None
        ):
            if la.norm(rightVal[-5:], np.inf) < np.sqrt(tol) and la.norm(
                downVal[-5:], np.inf
            ) < np.sqrt(tol):
                allbc += la.norm(downVal @ bcRight - bcDown @ rightVal)

        if (
            bcDown is not None
            and downVal is not None
            and bcLeft is not None
            and leftVal is not None
        ):
            if la.norm(leftVal[-5:], np.inf) < np.sqrt(tol) and la.norm(
                downVal[-5:], np.inf
            ) < np.sqrt(tol):
                allbc += la.norm(downVal @ bcLeft - bcDown @ leftVal)
        # if n < 16:
        #     print(CC[0, 0].toarray(), "\n")
        #     print(CC[0, 1].toarray(), "\n")
        #     print(CC[1, 0].toarray(), "\n")
        #     print(CC[1, 1].toarray(), "\n")

        return CC, rhs, bb, gg, Px, Py, xsplit, ysplit


def get_bc(bc, basis):
    bctype = bcfun = 0
    if bc is not None:
        if isinstance(bc, Polynomial):
            bctype = 1
            bcfun = bc
        elif callable(bc):
            if get_required_args_count(bc) == 1:
                bctype = 1
                bcfun = Polynomial(bc, basis=basis)

    return bctype, bcfun


def check_corners(lbc, rbc, dbc, ubc):
    tol = numericalSettings.interpRelTol
    dx = ubc.domain
    dy = lbc.domain
    match = (
        abs(lbc(dy[0]) - dbc(dx[0]))
        + abs(lbc(dy[1]) - ubc(dx[0]))
        + abs(rbc(dy[0]) - dbc(dx[1]))
        + abs(rbc(dy[1]) - ubc(dx[1]))
    )

    return match < 100 * np.sqrt(tol)


def interp_bc(lbc, rbc, dbc, ubc, m, n):
    lbc_coef = lbc.get_coef(m)

    rbc_coef = rbc.get_coef(m)
    dbc_coef = dbc.get_coef(n)
    ubc_coef = ubc.get_coef(n)

    G = np.zeros((m, n))
    G[0, :] = (ubc_coef + dbc_coef) / 2
    G[1, :] = (ubc_coef - dbc_coef) / 2
    G[:2, 0] = (rbc_coef[:2] + lbc_coef[:2]) / 2 - np.sum(G[:2, 2::2], axis=1)
    G[:2, 1] = (rbc_coef[:2] - lbc_coef[:2]) / 2 - np.sum(G[:2, 3::2], axis=1)
    G[2:, 0] = (rbc_coef[2:] + lbc_coef[2:]) / 2
    G[2:, 1] = (rbc_coef[2:] - lbc_coef[2:]) / 2

    return Polynomial2(G, bases=(ubc.basis, lbc.basis))


def resolved_check(coef, m, n, tol, lbc, rbc, bctype):
    """
    Basic resolution check

    Parameters
    ----------
    coef : TYPE
        DESCRIPTION.
    m : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.
    tol : TYPE
        DESCRIPTION.
    lbc : TYPE
        DESCRIPTION.
    rbc : TYPE
        DESCRIPTION.
    bctype : TYPE
        DESCRIPTION.

    Returns
    -------
    Resolved : TYPE
        DESCRIPTION.
    newDisc : TYPE
        DESCRIPTION.
    """

    Resolved = (np.max(np.abs(coef[:, -9:]), axis=0) < 20 * m * tol).all()

    # Check resolution of the Dirichlet BCs
    if bctype == 1:
        lval = (-1) ** np.r_[:n] @ coef
        lbc_cfs = lbc.get_coef(m)
        rval = ([1] * n) @ coef
        rbc_cfs = rbc.get_coef(m)
        Resolved = Resolved and la.norm(lval - lbc_cfs) < tol and la.norm(rval - rbc_cfs) < tol

    if not Resolved:
        newDisc = 2 ** (int(np.log2(m)) + 1) + 1

    else:
        newDisc = m

    return Resolved, newDisc


def update_tolerance(tol, m, n):
    """
    Increases the tolerance so that weak corner singularities causes less
    Problem

    Parameters
    ----------
    tol : TYPE
        DESCRIPTION.
    m : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.

    Returns
    -------
    None.
    """
    if max(m, n) > 250:
        return max(tol, 1e-11)
    return tol


def unconstrained_matrix_equation(ode, j, n, order, dom):
    B = sp.csc_array((n, n))

    for i in range(ode.shape[0]):
        # Get conversion and Differentiation matrix
        S = ultraS_convertmat(n, i, order - 1)

        D = (2 / np.diff(dom).item()) ** i * ultraS_difmat(n, i)
        if isinstance(ode[i, j], Polynomial):
            # Variable coefficient term
            c = ode[i, j].coeff
            M = ultraS_multmat(n, c, i)
            A = S @ M @ D
        elif isinstance(ode[i, j], Number):
            # Constant coefficient term
            A = ode[i, j] * S @ D
        else:
            A = np.zeros((n, n))
        B += A
    return B


def construct_bc(bc, bcpos, een, bcn, dom, scl, order):
    """
    Discretizes the boundary conditions

    Parameters
    ----------
    bc : Polynomial
        Linear constraint
    bcpos : int
        Position of constraint in the other variable.

    een bcn : TYPE
        DESCRIPTION.
    dom : TYPE
        DESCRIPTION.
    scl : TYPE
        DESCRIPTION.
    order : TYPE
        DESCRIPTION.

    Returns
    -------
    None.
    """
    if isinstance(bc, Polynomial):
        # Dirichlet conditions are sorted out here
        if bcpos == -1:
            # Dirichlet conditions at x= -1 (or y =- 1)
            bcrow = (-1) ** np.r_[:bcn]
        elif bcpos == 1:
            # Dirichlet conditions at x= 1 (or y = 1)
            bcrow = np.ones(bcn)
        else:
            # Dirichlet conditions at x=bcpos (or y = bcpos)
            bcrow = np.cos(np.r_[:bcn] * np.arccos(bcpos))
        return bcrow, resize(bc.coeff, een)

    elif callable(bc):
        if get_required_args_count(bc) == 2:
            # This permits dirichlet and neumann zero conditions
            x = Polynomial(lambda x: x, domain=dom)
            p = -bc(x, 0 * x)

            # TODO: must be improved to work with all bases
            # the evaluation of the order will fail
            order = Equation(bc).info(settings())["derivOrder"][0]
            if order == 0:
                return construct_bc(p, bcpos, een, bcn, dom, scl, order)
            elif order == 1:
                return process_neumann(p, bcpos, een, bcn, dom, scl)
        else:
            p = Polynomial(bc, domain=dom)
            return construct_bc(p, bcpos, een, bcn, dom, scl, order)

    elif isinstance(bc, str):
        bc = bc.lower()
        # If the boundary conditions are 'periodic' then try and setup the
        # right bcrows.
        if bc == "periodic":
            bcrow = np.zeros((bcn, order))
            bcvalue = np.zeros((een, order))
            for i in range(order):
                bcrow[:, i] = chebvalues(i, bcn, 1) - chebvalues(i, bcn, -1)
            return bcrow, bcvalue
        elif bc == "neumann":
            return process_neumann(0, bcpos, een, bcn, dom, scl)

            # dx_scaling = abs(2 / np.diff(scl))

            # bcrow = dx_scaling * chebvalues(1, bcn, bcpos)
            # bcvalue = np.zeros(een)
            # return bcrow, bcvalue

        else:
            raise ValueError("Unrecognized boundary value string.")
    elif isinstance(bc, Iterable):
        if len(bc) != 2:
            raise ValueError(
                "At the moment we only support dirichlet and nemann boundary conditions."
            )
        if all([isinstance(b, Polynomial) for b in bc]):
            bcvalue = np.zeros(((2, een)))
            bcrow = np.zeros((2, bcn))
            bcrow[0], bcvalue[0] = construct_bc(bc[0], bcpos, een, bcn, dom, scl, order)
            bcrow[1], bcvalue[1] = process_neumann(bc[1], bcpos, een, bcn, dom, scl)
            return bcrow, bcvalue

        if all([isinstance(b, str) for b in bc]):
            p = Polynomial(0, domain=dom)
            return construct_bc([p, p], bcpos, een, bcn, dom, scl, order)

        if (
            callable(bc[0])
            and get_required_args_count(bc[0]) == 1
            and callable(bc[1])
            and get_required_args_count(bc[1]) == 1
        ):
            p0 = Polynomial(bc[0], domain=dom)
            p1 = Polynomial(bc[1], domain=dom)
            return construct_bc([p0, p1], bcpos, een, bcn, dom, scl, order)
        if (
            callable(bc[0])
            and get_required_args_count(bc[0]) == 2
            and callable(bc[1])
            and get_required_args_count(bc[1]) == 2
        ):
            order0 = Equation(bc[0]).info(settings())["derivOrder"][0]
            order1 = Equation(bc[1]).info(settings())["derivOrder"][0]
            if order0 != 0 or order1 != 1:
                raise ValueError(
                    "The first condition must be Dirichlet and the second "
                    "condition must Neumann"
                )

            x = Polynomial(lambda x: x, domain=dom)
            p0 = -bc[0](x, 0 * x)
            p1 = -bc[1](x, 0 * x)
            return construct_bc([p0, p1], bcpos, een, bcn, dom, scl, order)

        if callable(bc[0]) and get_required_args_count(bc[0]) == 2:
            order = Equation(bc[0]).info(settings())["derivOrder"][0]

            if callable(bc[1]) and get_required_args_count(bc[1]) == 1:
                p = Polynomial(bc[1], domain=dom)

            if isinstance(bc[1], Number):
                p = Polynomial(bc[1], domain=dom)

            if isinstance(p, Polynomial):
                if order == 0:
                    return construct_bc(bc[1], bcpos, een, bcn, dom, scl, order)
                else:
                    return process_neumann(p, bcpos, een, bcn, dom, scl)

    else:
        raise ValueError("Unrecognized boundary condition Syntax")


def process_neumann(bc, bcpos, een, bcn, dom, scl):
    if not isinstance(bc, Polynomial):
        bc = Polynomial(bc, domain=dom)
    bcvalue = bc.get_coef(een)
    dx_scaling = abs(2 / np.diff(scl))
    bcrow = dx_scaling * chebvalues(1, bcn, bcpos)

    return bcrow, bcvalue


def process_ind_bc(bc, dom):
    if callable(bc) and get_required_args_count(bc) == 1:
        bc = Polynomial(bc, domain=dom)

    if isinstance(bc, Number):
        bc = Polynomial(bc, domain=dom)

    if isinstance(bc, Polynomial):
        if not (bc.domain == dom).all():
            raise TypeError(f"The left boundary condition must have domain: {dom}")

    return bc


def resize(v, n):
    if len(v) < n:
        return np.r_[v, [0] * (n - len(v))]
    else:
        return v[:n]


def chebvalues(k, n, x):
    """
    Return the values of Chebyshev {T0^(k)(x),..Tn^(k)(x)}, x being  1 or -1.

    Parameters
    ----------
    k : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if k == 0:
        return x ** (np.r_[:n])

    ll, kk = np.meshgrid(np.arange(n), np.arange(k))
    return x ** np.r_[1 : n + 1] * np.prod((ll**2 - kk**2) / (2 * kk + 1), axis=0)


def canonical_bc(B, G):
    """
    Form a linear combination of the boundary conditions
    so that they can be used for imposing on the PDE.


    Parameters
    ----------
    B : TYPE
        DESCRIPTION.
    G : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.
    P : TYPE
        DESCRIPTION.

    """
    P = nonsingular_permute(B)
    B = B @ P
    L, B = lu(B, permute_l=True)
    G = la.solve(L, G)

    # Scale so that B is unit upper triangular
    if min(B.shape) > 1:
        D = (1 / np.diag(B))[:, np.newaxis]
    elif B is not None:
        D = 1 / B[0, 0]
    else:
        D = np.zeros((0, 0))

    return D * B, D * G, P


def nonsingular_permute(B):
    """
    Permute the columns of B to ensure that the principal
    m*m sub-matrix of B is non-singular, where m = size(B, 1).

    Note: This is needed for solving the matrix equations with linear
    constraints, see DPhil thesis of Alex Townsend (section 6.5).


    Parameters
    ----------
    B : array_like
        DESCRIPTION.

    Returns
    -------
    None.

    """
    m = B.shape[0]
    k = 0

    while la.matrix_rank(B[:, k : m + k]) < m:
        k += 1
        if m + k > B.shape[1]:
            raise ("Boundary conditions are  linearly dependent")

    P = np.eye(B.shape[1])
    return sp.csr_matrix(P[:, np.r_[k : m + k, :k, m + k : P.shape[1]]])


def zero_dof(C1, C2, E, B, G):
    """
    Eliminate so degrees of freedom in the matrix equation can be
    removed.

    Parameters
    ----------
    C1 : TYPE
        DESCRIPTION.
    C2 : TYPE
        DESCRIPTION.
    E : TYPE
        DESCRIPTION.
    B : TYPE
        DESCRIPTION.
    G : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    C1 = C1.todense()

    E = E.copy()

    for i in range(B.shape[0]):
        for j in range(C1.shape[0]):
            if abs(C1[j, i]) > 10 * np.spacing(1):
                c = C1[j, i]
                C1[j, :] -= c * B[i, :]
                E[j, :] -= c * G[i, :] @ C2.T

    return sp.csr_matrix(C1), E


def impose_boundary_conditions(X, bb, gg, Px, Py, m, n):
    """
    imposes the boundary condition on the solution


    Parameters
    ----------
    X : array_like
        Solution with conditions
    bb : list
        List of linear constraints
    gg : list
        List of data
    Px : array_like
        Permutation matrix, identifying the non singular block in left/right bcs
    Py : array_like
        Permutation matrix, identifying the non singular block in top/bottom bcs
    m : int
        Discretization size in the second variable
    n : int
        Discretization size in the first variable

    Returns
    -------
    None.
    """

    # bb = [el.reshape(-1, 1) if el.ndim == 1 else el for el in bb]
    # bb = [el.T if el.shape[0] == 0 else el for el in bb]

    # cs = bb[2].shape[1] + bb[3].shape[1]
    # rs = bb[0].shape[1] + bb[1].shape[1]
    By = np.c_[bb[2].T, bb[3].T]
    Gy = np.c_[gg[2].T, gg[3].T]
    cs = By.shape[-1]

    Bx = np.c_[bb[0].T, bb[1].T]
    rs = Bx.shape[1]

    if not By.dtype == object:
        By = Py.T @ By  # Gy= Gy *Py

        result = Gy[rs : X.shape[1] + rs, :].T - By[cs : X.shape[0] + cs, :].T @ X
        X12 = la.solve(By[:cs, :].T, result)
        X = np.r_[X12, X]

    Gx = np.c_[gg[0].T, gg[1].T]

    if not Bx.dtype == object:
        Bx = Px.T @ Bx  # Gx= Px.T *Gx
        X2 = la.solve(
            Bx[:rs, :].T,
            Gx[: X.shape[0], :].T - Bx[rs : X.shape[1] + rs, :].T @ X.T,
        ).T
        X = np.c_[X2, X]

    # Pad with zero coefficients
    if X.shape[0] < m:
        X = np.r_[X, np.zeros((m - X.shape[0], X.shape[1]))]

    if X.shape[1] < n:
        X = np.c_[X, np.zeros((X.shape[0], n - X.shape[1]))]

    if not Px.size == 0:
        X = X @ Px.T
    if not Py.size == 0:
        X = Py @ X
    return X


def qzsplit(A, C):
    """
    A faster qz factorization for problems that decouple.

    This is equivalent to standard qz, except we take account of symmetry to
    reduce the computational requirements of the QZ factorization.
    """

    if issparse(A):
        A = A.A
    if issparse(C):
        C = C.A

    A1 = A[::2, ::2]
    C1 = C[::2, ::2]

    P1, S1, Q1, Z1 = qz(A1, C1)

    A2 = A[1::2, 1::2]
    C2 = C[1::2, 1::2]
    P2, S2, Q2, Z2 = qz(A2, C2)

    # Initialize all the variables.
    hf1 = len(P1)
    n = 2 * hf1 - 1
    P = np.zeros((n, n))
    S = np.zeros((n, n))
    Q = np.zeros((n, n))
    Z = np.zeros((n, n))

    # Push the sub-problem back together.

    P[:hf1, :hf1] = P1
    P[hf1:, hf1:] = P2

    S[:hf1, :hf1] = S1
    S[hf1:, hf1:] = S2

    Q[:hf1, ::2] = Q1
    Q[hf1:, 1::2] = Q2

    Z[::2, :hf1] = Z1
    Z[1::2, hf1:] = Z2

    return P, S, Q, Z
