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

from warnings import warn

import numpy as np
import numpy.linalg as la


def solve(A, b, tol=1e-6, scheme="balanced"):
    """
    A linear solver with special LU factorization for tau method on the solution
    of PDE's

    Parameters
    ----------
    A : array_like
        m*n Tau matrix
    b : array_like
        the right hand side
    tol : number, optional
        The tolerance. The default is 1e-6.
    scheme : str, optional
        A scheme to use. The default is 'balanced'.

    Returns
    -------
    None.

    """
    n = A.shape[1]
    L, U, p = lu(A, tol=tol, scheme=scheme)

    if (np.abs(np.diag(U)) < np.spacing(1)).any():
        warn("Upper factor has at least one null diagonal element")
        an = backsubstitution(U, la.solve(L[:n, :], b[p[:n]]))
    else:
        an = la.solve(U, la.solve(L[:n, :], b[p[:n]]))
    return an


def lu(A, tol=1e-6, scheme="balanced"):
    m, n = A.shape
    p = np.arange(m)

    for k in range(n - 1):
        if scheme == "balanced":
            if k < m - n:  # In condition equations
                ell = np.abs(A[k : m - n, k]).argmax()
                # Check if the operator rows needs to enter in the process
                if abs(A[ell, k]) <= tol:
                    ell = np.where(np.abs(A[k:m, k]) > tol)[0].min()

            else:
                ell = np.abs(A[k:, k]).argmax()
        else:
            ell = np.where(np.abs(A[k:, k]) > tol)[0].min()

        ell += k

        # Check for elimination skip
        if A[ell, k] != 0:
            # Swap rows
            if ell != k:
                A[[k, ell], :] = A[[ell, k], :]
                p[[k, ell]] = p[[ell, k]]

            # Multipliers computation
            i = np.c_[k + 1 : m]
            A[i, k] = A[i, k] / A[k, k]
            # Update the remainder of the matrix
            j = np.r_[k + 1 : n]

            A[i, j] = A[i, j] - A[i, [k]] @ A[[[k]], j]

    # Test low-right corner value A[n-1,n-1]
    if abs(A[n - 1, n - 1]) < tol:
        ell = np.where(np.abs(A[n - 1 :, n - 1]) > tol)[0].min()
        ell += n - 1
    if ell != n - 1:
        A[[n - 1, ell], :] = A[[ell, n - 1], :]
        p[[n - 1, ell]] = p[[ell, n - 1]]

    # separate L and U matrices and cut for appropriate dimension
    L = np.tril(A, -1) + np.eye(m, n)
    U = np.triu(A)[:n, :]

    return L, U, p


def backsubstitution(U, b):
    """
    Performs back substitution bearing in mind small diagonal elements in U
    from special LU2 strategy. Solves the linear equation U*x=b

    Parameters
    ----------
    U : array_like
        a m*n matrix
    b : array_like
        a (m,) vector.

    Returns
    -------
    None.

    """
    n = U.shape[0]
    if abs(U[n - 1, n - 1]) < 10 * np.spacing(1):
        b[n - 1] = 0
    else:
        b[n - 1] = b[n - 1] / U[n - 1, n - 1]

    for k in range(n - 1, 0, -1):
        j = np.arange(k, n)
        if abs(U[k - 1, k - 1]) < 10 * np.spacing(1):
            b[k - 1] = 0
        else:
            b[k - 1] = (b[k - 1] - U[k - 1, j] @ b[j]) / U[k - 1, k - 1]

    return b


def LU2FromF90(A, b):
    zeropiv = 1e-6
    m, n = A.shape
    nb = n
    # ipiv = np.arange(n)
    for i in range(n):
        aux = np.zeros(m)
        for j in range(m):
            s = 0
            for k in range(i):
                s += A[j, k] * A[k, i]
            aux[j] = A[j, i] - s

        # ... max and pivoting
        pivot = abs(aux[i])
        # ell = i
        for k in range(i + 1, m - nb):
            if pivot < abs(aux[k]):
                pivot = abs(aux[k])
                # ell = k

        # if the pivot is null pass to the operating block
        if pivot < zeropiv:
            k = m - nb
            while zeropiv >= abs(aux[k]) and k < m - 1:
                k += 1
            if abs(aux[k]) > zeropiv:
                pivot = abs(aux[k])
                # ell = k
