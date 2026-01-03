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

"""
This module provides functions used in the Tautoolbox.

The functions provided try to take into account what is the first argument.
"""

from functools import singledispatch

import numpy as _np

from .polynomial import FPolynomial, Polynomial


# Functions shared between Polynomial and numpy.array
@singledispatch
def cos(x):
    return _np.cos(x)


@cos.register(Polynomial)
def _(x):
    return x.cos()


@singledispatch
def cosh(x):
    return _np.cosh(x)


@cosh.register(Polynomial)
def _(x):
    return x.cosh()


@singledispatch
def exp(x):
    return _np.exp(x)


@exp.register(Polynomial)
def _(x):
    return x.exp()


@singledispatch
def sin(x):
    return _np.sin(x)


@sin.register(Polynomial)
def _(x):
    return x.sin()


@singledispatch
def sinh(x):
    return _np.sinh(x)


@sinh.register(Polynomial)
def _(x):
    return x.sinh()


# Integro-differential operator/functions
@singledispatch
def diff(y, *a, **b):
    return y.diff(*a, **b)


@diff.register(_np.ndarray)
def _(y, *a, **b):
    return _np.diff(y, *a, **b)


@singledispatch
def fractionalIntegral(y, order):
    r"""
    Compute the fractional integral of order `order`. When `order` is integer
    the result is the standard indefinite integral of order `order`.

    Parameters
    ----------
    order : scalar
        The order of the integral.

    Returns
    -------
    Polynomial
        The fractional Integral of order `order`.

    Examples
    --------
    Using ChebyshevT basis in the [-1,1] domain:

    >>> from tautoolbox.polynomial import Polynomial
    >>> from tautoolbox.functions import fractionalIntegral
    >>> p = Polynomial(lambda x: x + 2 * x * 3 * x**2 - x**3)
    >>> fractionalIntegral(p, 2.6).coeff
    array([-0.87894491, -1.01386727, -0.06663148,  0.05632403, -0.00652738,
            0.00543948])
    """

    return y.fractionalIntegral(order)


@fractionalIntegral.register(Polynomial)
def _(y, order):
    return FPolynomial(y).fractionalIntegral(order)


@singledispatch
def integral(y, *a):
    return y.integral(*a)


@singledispatch
def fred(y, *a, **b):
    return y.fred(*a, **b)


@singledispatch
def fred1(y, *a, **b):
    return y.fred(*a, **b)


@singledispatch
def volt(y, *a, **b):
    return y.volt(*a, **b)


@singledispatch
def linspace(start, stop, num=100, endpoint=True, retstep=False, dtype=None, axis=0):
    return _np.linspace(start, stop, num, endpoint, retstep, dtype, axis)


@linspace.register(Polynomial)
def _(y, n=100):
    return y.linspace(n)


@singledispatch
def log(x):
    return _np.log(x)


@log.register(Polynomial)
def _(x):
    return x.log()
