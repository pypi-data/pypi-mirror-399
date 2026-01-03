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

import matplotlib.pyplot as plt
import numpy as np

from ..polynomial import Polynomial, Polynomial2
from ..polynomial.bases import family_basis
from ..utils import get_required_args_count
from .options import Settings, settings
from .problem import Problem
from .problem2 import Problem2


def basis(domain=(-1, 1), options=None, **kwargs):
    """
    Parameters
    ----------
    options : tau.settings, optional
        All the different options used in tautoolbox. The default is None.

    Returns
    -------
    tau.bases.T3Basis
        Orthogonal Polynomials base class.
        All the different classes returned are derived from the base
        class tau.bases.T3Basis.

    """
    if not options:
        options = settings()

        if "basis" not in kwargs:
            family = options.basis
        else:
            family = kwargs["basis"]
    elif isinstance(options, Settings):
        options = settings(options)
        family = options.basis
    elif isinstance(options, str):
        family = options
    else:
        family = "ChebyshevT"

    return family_basis(family, np.array(domain), **kwargs)


def linearSystemSolver(T, b, nequations):
    """
    Solve a linear system equation, or system of linear scalar equations,
    using Gauss elimination.

    Parameters
    ----------
    T : Coefficient matrix
    b : Independent terms

    Returns
    -------
    x : Polynomial
        Solution to the system Tx = b

    """
    return np.linalg.solve(T, b).reshape(nequations, -1)


def polynomial(*args, **kwargs):
    """A convenience function to create the (orthogonal) polynomials"""
    if "source" in kwargs:
        source = kwargs["source"]
    elif args:
        source = args[0]
    else:
        source = None

    if callable(source):
        if get_required_args_count(source) == 1:
            return Polynomial(*args, **kwargs)
        if get_required_args_count(source) == 2:
            return Polynomial2(*args, **kwargs)
    return Polynomial(*args, **kwargs)


def problem(equation, domain, conditions=None, options=None, **kwargs):
    """A convenience function to create a differential problem"""
    if np.array(domain).ndim == 2:
        return Problem2(equation, domain, conditions, options, **kwargs)
    return Problem(equation, domain, conditions, options, **kwargs)


def spy(T):
    m, n = T.shape
    nnz = np.count_nonzero(T)
    d = 0.1
    fig = plt.figure()
    ax = fig.gca(projection="3d")
    # ax = Axes3D(fig)
    for i in range(m):
        for j in range(n):
            if not T[i, j] == 0:
                ax.plot_surface(
                    np.array(
                        [
                            [j - 0.5 + d, j + 0.5 - d],
                            [j - 0.5 + d, j + 0.5 - d],
                        ]
                    ),
                    np.array(
                        [
                            [i - 0.5 + d, i - 0.5 + d],
                            [i + 0.5 - d, i + 0.5 - d],
                        ]
                    ),
                    np.array([[T[i, j], T[i, j]], [T[i, j], T[i, j]]]),
                    shade=True,
                )

                # ax.bar3d(j+1,i+1, 0, d,d,T[i,j], color='b')
    # ax.xaxis.set_major_locator(MultipleLocator(1))
    # ax.xaxis.set_minor_locator(MultipleLocator(d))
    plt.xlabel(f"nz = {nnz}")
    # plt.xlim((1-d,m +d))
    # plt.xticks(range(1,m+1))
    # plt.ylim((1-d,n +d))
    # plt.yticks(range(1,n+1))
    # plt.colorbar(ax)
    ax.colorbar(shrink=0.5, aspect=5)
    ax.view_init(azim=0, elev=90)
    plt.show()


if __name__ == "__main__":
    x = np.random.randn(20, 20)
    x[5, :] = 0.0
    x[:, 12] = 0.0
    Lx, Ly = x.shape
    plt.matshow(x, cmap="PiYG", origin="lower", extent=[0, Lx, 0, Ly])
    plt.colorbar(orientation="vertical")
