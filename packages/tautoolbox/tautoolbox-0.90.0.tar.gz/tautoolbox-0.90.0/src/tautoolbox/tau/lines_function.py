# Copyright (C) 2022-2025, University of Porto and Tau Toolbox developers.
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

import numbers
from collections.abc import Iterable

import numpy as np
from scipy.sparse import diags


def mol_derivatives(y, order=1, method_points=5, step_size=None, domain=None):
    """


    Parameters
    ----------
    y : array_like
        An array or list of numbers
    order : int, optional
        The order of the derivative
    method_points : int, optional
        The number of steps to use in the finite differences
    step_size : float, optional
        The step size for the discretization grid
    domain : array_like, optional
        Must be one-dimensional array_like of numbers

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    result : array_like
        A one dimensional numpy array

    """
    # check if y an iterable of  numbers
    if isinstance(y, Iterable):
        if all(isinstance(i, numbers.Number) for i in y):
            y = np.array(y)

    if not isinstance(y, np.ndarray):
        raise TypeError(
            "The first argument must be an one-dimensional "
            f"iterable like object but received a {type(y)}"
        )

    if domain is None and step_size is None:
        raise ValueError("Tautoolbox: domain and step_size cannot be None at the same time")
    elif step_size is None:
        step_size = (domain[1] - domain[0]) / (len(y) - 1)

    switcher = {
        (1, 3): threePointsCenteredFirstOrderDiff(y, step_size),
        (2, 3): threePointsCenteredSecondOrderDiff(y, step_size),
        (1, 5): fivePointsCenteredFirstOrderDiff(y, step_size),
        (2, 5): fivePointsCenteredSecondOrderDiff(y, step_size),
        (1, 7): sevenPointsCenteredFirstOrderDiff(y, step_size),
        (2, 7): sevenPointsCenteredSecondOrderDiff(y, step_size),
    }

    result = switcher.get(
        (order, method_points),
        f"Not yet implemented for {{ order:{order}, method_points:{method_points}}}",
    )
    if isinstance(result, str):
        raise ValueError(result)
    return result


def threePointsCenteredCenteredFirstOrderDmat(x):
    n = len(x)
    h = np.diff(x)[0]
    mat = 1 / (2 * h) * diags([-1, 0, 1], [-1, 0, 1], (n, n)).toarray()
    mat[0, :3] = np.array([-3, 4, -1]) * mat[0, 1]
    mat[-1, -3:] = -np.flip(mat[0, :3])
    return mat


def threePointsCenteredCenteredSecondOrderDmat(x):
    n = len(x)
    h = np.diff(x)[0]
    mat = 1 / (h**2) * diags([1, -2, 1], [-1, 0, 1], (n, n)).toarray()
    mat[0, :3] = mat[1, :3]
    mat[-1, -3:] = mat[-2, -3:]
    # mat[0, -1] = 1
    # mat[-1, 0] = 1
    return mat


def threePointsCenteredSecondOrderDiff(x, h=None):
    mat = (
        np.r_[
            x[0] - 2 * x[1] + x[2],
            x[:-2] - 2 * x[1:-1] + x[2:],
            x[-1] - 2 * x[-2] + x[-3],
        ]
        / h**2
    )
    # mat[0] = (x[0] + x[2] - 2 * x[1]) / h ** 2
    # mat[-1] = (x[-1] + x[-3] - 2 * x[-2]) / h ** 2
    return mat


def threePointsCenteredFirstOrderDiff(x, h=None):
    mat = np.r_[
        -3 * x[0] + 4 * x[1] - x[2],
        x[:-2] + x[2:],
        x[-3] - 4 * x[-2] + 3 * x[-1],
    ] / (2 * h)
    # mat[0] = (x[0] + x[2] - 2 * x[1]) / h ** 2
    # mat[-1] = (x[-1] + x[-3] - 2 * x[-2]) / h ** 2
    return mat


def threePointsVariableStepFirstOrderCenteredFiniteDiff(y, x):
    "three points variable step first order centered finite difference"
    h = np.diff(x)

    mat = np.zeros_like(x)
    mat[1:-1] = (
        -(h[1:] / h[:-1]) * y[:-2]
        + (h[:-1] / h[1:]) * y[2:]
        + 1 / (h[:-1] * h[1:]) * (h[1:] ** 2 - h[:-1] ** 2) * y[1:-1]
    ) / (h[:-1] + h[1:])
    mat[0] = (
        -(h[0] ** 2) * y[2]
        + (h[0] ** 2 - (h[0] + h[1]) ** 2) * y[0]
        + (h[0] + h[1]) ** 2 * y[1]
    ) / (h[0] * h[1] * (h[0] + h[1]))

    mat[-1] = (
        h[-1] ** 2 * y[-3]
        - (h[-1] ** 2 - (h[-1] + h[-2]) ** 2) * y[-1]
        - (h[-1] + h[-2]) ** 2 * y[-2]
    ) / (h[-1] * h[-2] * (h[-1] + h[-2]))

    return mat


def threePointsVariableStepSecondOrderCenteredFiniteDiff(y, x):
    "three points variable step second order centered finite difference"
    h = np.diff(x)

    mat = np.zeros_like(x)

    # for therms k=1,...,K-1
    mat[1:-1] = (
        2
        * (h[1:] * y[:-2] + h[:-1] * y[2:] - (h[:-1] + h[1:]) * y[1:-1])
        / (h[:-1] * h[1:] * (h[:-1] + h[1:]))
    )
    # for first term
    mat[0] = (
        2 * (h[1] * y[0] - (h[0] + h[1]) * y[1] + h[0] * y[2]) / (h[0] * h[1] * (h[0] + h[1]))
    )

    # for last term
    mat[-1] = (
        2
        * (h[-2] * y[-1] - (h[-1] + h[-2]) * y[-2] + h[-1] * y[-3])
        / (h[-1] * h[-2] * (h[-1] + h[-2]))
    )

    return mat


def threeStepsFirstOrderDiff(x, h):
    mat = np.r_[
        -11 * x[0] + 18 * x[1] - 9 * x[2] + 2 * x[3],
        -2 * x[0] - 3 * x[1] + 6 * x[2] - x[3],
        x[:-3] - 6 * x[1:-2] + 3 * x[2:-1] + 2 * x[3:],
        11 * x[-1] - 18 * x[-2] + 9 * x[-3] - 2 * x[-4],
    ] / (6 * h)
    # mat[0] = (x[0] + x[2] - 2 * x[1]) / h ** 2
    # mat[-1] = (x[-1] + x[-3] - 2 * x[-2]) / h ** 2
    return mat


def threeStepsSecondOrderDiff(x, h):
    mat = (
        np.r_[
            2 * x[0] - 5 * x[1] + 4 * x[2] - x[3],
            x[0] - 2 * x[1] + x[2],
            x[1:-2] - 2 * x[2:-1] + x[3:],
            2 * x[-1] - 5 * x[-2] + 4 * x[-3] - x[-4],
        ]
        / h**2
    )
    # mat[0] = (x[0] + x[2] - 2 * x[1]) / h ** 2
    # mat[-1] = (x[-1] + x[-3] - 2 * x[-2]) / h ** 2
    return mat


def fivePointsCenteredFirstOrderDiff(x, h):
    """

     Parameters
     ----------
     x : array_like
         An one dimensional numpy array to perform the finite differences
     h : float
         The step size for the finite differences

     Returns
     -------
     x : array_like
         An one dimensional array with the finite differences

    Description
    -----------
    u_{xx} at the interior points k=4, 5, ,K-1, where K=len(x).

    Develops a set of fourth order differentiation formulas for the first
    derivative u_{xx}. We consider the formula

    a*u[k-2] +b*u[k-1] + c*u[k] + d*u[k+1] +e*u[k+2] , k=2,...,K-2        (1)

    In this expression we replace  u[k-2], u[k-1], u[k+1] and [k+2] by their
    Taylor series expansion around x_k. From this linear combination we want
    to cancel all the coefficients of the derivatives but the first and we get
    the following system

    -2*a - b + d + 2*e = 1
    4*a + b + d + 4*e = 0
    -8*a - b + d + 8*e = 0
    16*a + b + d + 16*e = 0


    The above system have as solution {a: 1/12, b: -2/3, d: 2/3, e: -1/12}. with
    these coefficients we get the following formula for the first derivative

    u'_k = (u[k-2] - 8*u[k-1] + 8*u[k+1] - u[k+2])/(12*h),
    k=2,...,K-2.

    for the first and last grid points we have

    a*u[0] + b*u[1] + c*u[2] + d*u[3] + e*u[4]                          (2)

    In the above expression we replace u[1], u[2], u[3] and u[4] for their
    fourth order Taylor series expansion around x_0. One more time we cancel
    the the coefficients of all the derivatives but the first and we get the
    system

    b + 2*c + 3*d + 4*e = 1
    b + 4*c + 9*d + 16*e = 0
    b + 8*c + 27*d + 64*e = 0
    b + 16*c + 81*d + 256*e = 0

    The above system has solution : {b: 4, c: -3, d: 4/3, e: -1/4}

    Replacing the coefficients in (2) we get

    u_0 =(-25*u[0] + 48*u[1] - 36*u[2] + 16*u[3] - 3*u[4])/(12*h).

    The last term is minus the  first term written from the end of the grid
    in reverse order.
    u'_K =(3*u{K-4} - 16*u[K-3] + 36*u[K-2] - 48*u[K-1] + 25*u[K])/(12*h)


    For the second and the penultimate therm replace u[0], u[2], u[3]
    and u[4] for their fourth order Taylor series expansion around x_1. One
    more time we cancel the the coefficients of all the derivatives but the
    second and we get the system

    -a + c + 2*d + 3*e = 1
    a + c + 4*d + 9*e = 0
    -a + c + 8*d + 27*e = 0
    a + c + 16*d + 81*e = 0

    The above system has solution : {a: -1/4, c: 3/2, d: -1/2, e: 1/12}

    Replacing the coefficients in (2) we get:

    u'_1 = (-3*u[0] - 10*u[1] + 18*u[2] - 6*u[3] + u[4])/(12*h)

    The penultimate term is minus the second term written from the end of the
    grid in reverse
    order
    u'_{K-1} = (-u[K-4] + 6*u[K-3] - 18*u[K-2] + 10*u[K-1] + 3*u[K])/(12*h)


    """

    mat = np.r_[
        [[-25, 48, -36, 16, -3], [-3, -10, 18, -6, 1]] @ x[:5],
        [1, -8, 8, -1] @ np.array([x[:-4], x[1:-3], x[3:-1], x[4:]]),
        [[-1, 6, -18, 10, 3], [3, -16, 36, -48, 25]] @ x[-5:],
    ] / (12 * h)
    # mat[0] = (x[0] + x[2] - 2 * x[1]) / h ** 2
    # mat[-1] = (x[-1] + x[-3] - 2 * x[-2]) / h ** 2
    return mat


def fivePointsUpWindFirstOrderDiff(u, h):
    """

     Parameters
     ----------
     x : array_like
         An one dimensional numpy array to perform the finite differences
     h : float
         The step size for the finite differences

     Returns
     -------
     x : array_like
         An one dimensional array with the finite differences

    Description
    -----------
    u_{xx} at the interior points k=4, 5, ,K-1, where K=len(x).

    Develops a set of fourth order differentiation formulas for the first
    derivative u_{xx}. We consider the formula

    a*u[k-4] +b*u[k-3] + c*u[k-2] + d*u[k-1] +e*u[k]                      (1)

    In this expression we replace  u[k-4], u[k-3], u[k-2] and [k-1] by their
    Taylor series expansion around x_k. From this linear combination we want
    to cancel all the coefficients of the derivatives but the first and we get
    the following system

    -4*a -3*b -2*c -d =1
    16*a +9*b +4*c +d =0
    -64*a -27*b -8*c -d =0
    4**4*a +3**4*b +2**4*c +d =0

    The above system have as solution {a: 1/4, b: -4/3, c: 3, d: -4}. with
    these coefficients we get the following formula for the first derivative

    u'_k = (3*u[k-4] -16 *u[k-3] +36*u[k-2] -48*u[k-1] +25 u[k])/12,
    k=4,...,K.

    for the first term we consider the following formula

    a*u[0] +b*u[1] + c*u[2] + d*u[3] +e*u[4]                              (2)

    In the above expression we replace u[1], u[2], u[3] and u[4] for their
    fourth order Taylor series expansion around x_0. One more time we cancel
    the the coefficients of all the derivatives but the first and we get the
    system

    b + 2*c + 3*d + 4*e = 1
    b + 4*c + 9*d + 16*e = 0
    b + 8*c + 27*d + 64*e = 0
    b + 16*c + 81*d + 256*e =0

    The above system has solution : {b: 4, c: -3, d: 4/3, e: -1/4}

    Replacing the coefficients in (2) we get

    u'_0 =(-25*u[0] +48*u[1]-36*u[2] + 16*u[3] -3*u[4])/12

    For the second therm replace u[0], u[2], u[3] and u[4] for their
    fourth order Taylor series expansion around x_1. One more time we cancel
    the the coefficients of all the derivatives but the first and we get the
    system

    -a + c + 2*d + 3*e = 1
    a + c + 4*d + 9*e = 0
    -a + c + 8*d + 27*e =0
    a + c + 16*d + 81*e =0

    The above system has solution : {a: -1/4, c: 3/2, d: -1/2, e: 1/12}

    Replacing the coefficients in (2) we get:

    u'_1 = (-3*u[0] -10*u[1] +18*u[2] -6*u[3]+ u[4])/12

    For the third  therm  we replace u[0], u[1], u[3] and u[4] for their
    fourth order Taylor series expansion around x_2. One more time we cancel
    the the coefficients of all the derivatives but the first and we get the
    system

    -2*a - b + d + 2*e = 1
    4*a + b + d + 4*e = 0
    -8*a - b + d + 8*e = 0
    16*a + b + d + 16*e = 0

    The above system has solution : {a: 1/12, b: -2/3, d: 2/3, e: -1/12}

    Replacing the coefficients in (2) we get:

    u'_2 = (u[0] - 8*u[1] + 8*u[3] - u[4])/12


    For the fourth  therm  we replace u[0], u[1], u[2] and u[4] for their
    fourth order Taylor series expansion around x_3. One more time we cancel
    the the coefficients of all the derivatives but the first and we get the
    system

    -3*a - 2*b - c + e = 1
    9*a + 4*b + c + e=0
    -27*a - 8*b - c + e=0
    81*a + 16*b + c + e =0

    The above system has solution : {a: -1/12, b: 1/2, c: -3/2, e: 1/4}

    Replacing the coefficients in (2) we get:

    u'_3 = (-u[0] + 6*u[1] - 18*u[2] + 10*u[3] + 3*u[4])/12

    """

    return np.r_[
        [
            [-25, 48, -36, 16, -3],
            [-3, -10, 18, -6, 1],
            [1, -8, 0, 8, -1],
            [-1, 6, -18, 10, 3],
        ]
        @ u[:5],
        [3, -16, 36, -48, 25] @ np.array([u[:-4], u[1:-3], u[2:-2], u[3:-1], u[4:]]),
    ] / (12 * h)


def fivePointsCenteredSecondOrderDiff(x, h):
    """

     Parameters
     ----------
     x : array_like
         An one dimensional numpy array to perform the finite differences
     h : float
         The step size for the finite differences

     Returns
     -------
     x : array_like
         An one dimensional array with the finite differences

    Description
    -----------
    u_{xx} at the interior points k=2, 5, ,K-2, where K=len(x).

    Develops a set of fourth order differentiation formulas for the first
    derivative u_{xx}. We consider the formula

    a*u[k-2] +b*u[k-1] + c*u[k] + d*u[k+1] +e*u[k+2] , k=2,...,K-2        (1)

    In this expression we replace  u[k-2], u[k-1], u[k+1] and [k+2] by their
    Taylor series expansion around x_k. From this linear combination we want
    to cancel all the coefficients of the derivatives but the second and we get
    the following system

    -2*a - b + d + 2*e = 0
    4*a + b + d + 4*e = 2
    -8*a - b + d + 8*e = 0
    16*a + b + d + 16*e = 0


    The above system have as solution {a: -1/12, b: 4/3, d: 4/3, e: -1/12}. with
    these coefficients we get the following formula for the second derivative

    u''_k = (-u[k-2] + 16*u[k-1] - 30*u[k] + 16*u[k+1] - u[k+2])/(12*h**2),
    k=2,...,K-2.

    for the first and last grid points we have

    a*u[0] + b*u[1] + c*u[2] + d*u[3] + e*u[4]  + f*u[5]                  (2)

    In the above expression we replace u[1], u[2], u[3], u[4] and u[5] for their
    fifth order Taylor series expansion around x_0. One more time we cancel
    the the coefficients of all the derivatives but the second and we get the
    system

    b + 2*c + 3*d + 4*e + 5*f = 0
    b + 4*c + 9*d + 16*e + 25*f = 2
    b + 8*c + 27*d + 64*e + 125*f = 0
    b + 16*c + 81*d + 256*e + 625*f = 0
    b + 32*c + 243*d + 1024*e + 3125*f =0

    The above system has solution : {b: -77/6, c: 107/6, d: -13, e: 61/12, f: -5/6}

    Replacing the coefficients in (2) we get

    u''_0 =(45*u[0] - 154*u[1] + 214*u[2] - 156*u[3] + 61*u[4] - 10*u[5])/(12*h**2).

    The last term is the first term written from the end in reverse order
    u''_K =(-10*u[K-5] + 61*u[K-4] - 156*u[K-3] + 214*u[K-2] - 154*u[K-1]
            + 45*u[K])/(12*h**2)


    For the second and the penultimate therm replace u[0], u[2], u[3], u[4]
    and u[5] for their fourth order Taylor series expansion around x_1. One
    more time we cancel the the coefficients of all the derivatives but the
    second and we get the system

    -a + c + 2*d + 3*e + 4*f = 0
    a + c + 4*d + 9*e + 16*f = 2
    -a + c + 8*d + 27*e + 64*f = 0
    a + c + 16*d + 81*e + 256*f = 0
    -a + c + 32*d + 243*e + 1024*f =0

    The above system has solution : {a: 5/6, c: -1/3, d: 7/6, e: -1/2, f: 1/12}

    Replacing the coefficients in (2) we get:

    u'_1 = (10*u[0] - 15*u[1] - 4*u[2] + 14*u[3] - 6*u[4] + u[5])/(12*h**2)

    The penultimate term is the second term written from the end in reverse
    order
    u'_{K-1} = (u[K-5] - 6*u[K-4] +14*u[K-3] -4*u[K-2] -15*u[K-1] +10*u[K])/(12*h**2)


    """

    return np.r_[
        [[45, -154, 214, -156, 61, -10], [10, -15, -4, 14, -6, 1]] @ x[:6],
        [-1, 16, -30, 16, -1] @ np.array([x[:-4], x[1:-3], x[2:-2], x[3:-1], x[4:]]),
        [[1, -6, 14, -4, -15, 10], [-10, 61, -156, 214, -154, 45]] @ x[-6:],
    ] / (12 * h**2)


def sevenPointsCenteredFirstOrderDiff(x, h):
    """

      Parameters
      ----------
      x : array_like
          An one dimensional numpy array to perform the finite differences
      h : float
          The step size for the finite differences

      Returns
      -------
      array_like
          An one dimensional array with the finite differences

     Description
     -----------
     u_{x} at the interior points k=3, 4, ...,K-3, where K=len(x).

     Develops a set of fourth order differentiation formulas for the first
     derivative u_{xx}. We consider the formula

    a*u[k-3] + b*u[k-2] +c*u[k-1] + d*u[k] + e*u[k+1] +f*u[k+2] + g*u[k+3],
    k=3,...,K-3        (1)

     In this expression we replace  u[k-3], u[k-2], u[k-1], u[k+1], u[k+2] and
     u[k+3] by their sixth order Taylor series expansion around x_k. From this
     linear combination we want to cancel all the coefficients of the derivati-
     ves but the first and we get the following system

     -3*a - 2*b - c + e + 2*f + 3*g = 1
     9*a + 4*b + c + e + 4*f + 9*g = 0
     -27*a - 8*b - c + e + 8*f + 27*g = 0
     81*a + 16*b + c + e + 16*f + 81*g = 0
     -243*a - 32*b - c + e + 32*f + 243*g = 0
     729*a + 64*b + c + e + 64*f + 729*g = 0

     The above system have as solution {a: -1/60, b: 3/20, c: -3/4, e: 3/4,
     f: -3/20, g: 1/60}. with these coefficients we get the following formula
     for the first derivative

     u'_k = (-1*u[k-3] + 9*u[k-2] - 45*u[k-1] + 45*u[k+1] - 9*u[k+2] +
              u[k+3])/(60*h), k=-3,...,K-3.

     for the first and last grid points we have

     a*u[0] + b*u[1] + c*u[2] + d*u[3] + e*u[4]  + f*u[5] + g*u[6]         (2)

     In the above expression we replace u[1], u[2], u[3], u[4], u[5] and u[6]
     for their fifth order Taylor series expansion around x_0. One more time we
     cancel the the coefficients of all the derivatives but the second and we
     get the system

     b + 2*c + 3*d + 4*e + 5*f + 6*g = 1
     b + 4*c + 9*d + 16*e + 25*f + 36*g = 0
     b + 8*c + 27*d + 64*e + 125*f + 216*g = 0
     b + 16*c + 81*d + 256*e + 625*f + 1296*g = 0
     b + 32*c + 243*d + 1024*e + 3125*f + 7776*g = 0
     b + 64*c + 729*d + 4096*e + 15625*f + 46656*g = 0

     The above system has solution : {b: 6, c: -15/2, d: 20/3, e: -15/4,
                                      f: 6/5, g: -1/6}

     Replacing the coefficients in (2) we get

     u'_0 =(-147*u[0] + 360*u[1] - 450*u[2] + 400*u[3] - 225*u[4] + 72*u[5]
     - 10*u[6])/(60*h)

     The last term is the first term written from the end in reverse order
     u'_K =(10*u[K-6] - 72*u[K-5] + 225*u[K-4] - 400*u[K-3] + 450*u[K-2] -
     360*u[K-1] + 147*u[K])/(60*h)


     For the second and the penultimate therm replace u[0], u[2], u[3], u[4],
     u[5] and u[6] for their sixth order Taylor series expansion around x_1.
     One more time we cancel the the coefficients of all the derivatives but
     the first and we get the system

     -a + c + 2*d + 3*e + 4*f + 5*g = 1
     a + c + 4*d + 9*e + 16*f + 25*g = 0
     -a + c + 8*d + 27*e + 64*f + 125*g = 0
     a + c + 16*d + 81*e + 256*f + 625*g = 0
     -a + c + 32*d + 243*e + 1024*f + 3125*g = 0
     a + c + 64*d + 729*e + 4096*f + 15625*g = 0

     The above system has solution : {a: -1/6, c: 5/2, d: -5/3, e: 5/6,
                                      f: -1/4, g: 1/30}

     Replacing the coefficients in (2) we get:

     u'_1 = ([-10*u[0] - 77*u[1] + 150*u[2] - 100*u[3] + 50*u[4] - 15*u[5] +
     2*u[6]])/(60*h)

     The penultimate term is the second term written from the end in reverse
     order
     u'_{K-1} = (-2*u[K-6] + 15*u[K-5] - 50*u[K-4] + 100*u[K-3] - 150*u[K-2] +
     77*u[K-1] + 10*u[K])/(60*h)

     For the third and the antepenultimate therm we replace u[0], u[1], u[3], u[4],
     u[5] and u[6] for their sixth order Taylor series expansion around x_2 in
     (2). One more time we cancel the the coefficients of all the derivatives
     but the first and we get the system

     -2*a - b + d + 2*e + 3*f + 4*g = 1
     4*a + b + d + 4*e + 9*f + 16*g = 0
     -8*a - b + d + 8*e + 27*f + 64*g = 0
     16*a + b + d + 16*e + 81*f + 256*g = 0
     -32*a - b + d + 32*e + 243*f + 1024*g = 0
     64*a + b + d + 64*e + 729*f + 4096*g = 0

     The above system has solution : {a: 1/30, b: -2/5, d: 4/3, e: -1/2,
                                      f: 2/15, g: -1/60}

     Replacing the coefficients in (2) we get:

     u'_2 = (2*u[0] - 24*u[1] - 35*u[2] + 80*u[3] - 30*u[4] + 8*u[5] - u[6]])/(60*h)

     The penultimate term is the second term written from the end in reverse
     order
     u'_{K-2} = (u[K-6] - 8*u[K-5] + 30*u[K-4] - 80*u[K-3] + 35*u[K-2] + 24*u[K-1] - 2*u[K])/(60*h)


    """

    return np.r_[
        [
            [-147, 360, -450, +400, -225, +72, -10],
            [-10, -77, +150, -100, +50, -15, +2],
            [2, -24, -35, 80, -30, 8, -1],
        ]
        @ x[:7],
        [-1, 9, -45, 45, -9, 1] @ np.array([x[:-6], x[1:-5], x[2:-4], x[4:-2], x[5:-1], x[6:]]),
        [
            [1, -8, 30, -80, 35, 24, -2],
            [-2, 15, -50, 100, -150, 77, 10],
            [10, -72, 225, -400, 450, -360, 147],
        ]
        @ x[-7:],
    ] / (60 * h)


def sevenPointsCenteredSecondOrderDiff(x, h):
    """

      Parameters
      ----------
      x : array_like
          An one dimensional numpy array to perform the finite differences
      h : float
          The step size for the finite differences

      Returns
      -------
      array_like
          An one dimensional array with the finite differences

     Description
     -----------
     u_{xx} at the interior points k=3, 4, ...,K-3, where K=len(x).

     Develops a set of fourth order differentiation formulas for the first
     derivative u_{xx}. We consider the formula

    a*u[k-3] + b*u[k-2] +c*u[k-1] + d*u[k] + e*u[k+1] +f*u[k+2] + g*u[k+3],
    k=3,...,K-3        (1)

     In this expression we replace  u[k-3], u[k-2], u[k-1], u[k+1], u[k+2] and
     u[k+3] by their sixth order Taylor series expansion around x_k. From this
     linear combination we want to cancel all the coefficients of the derivati-
     ves but the first and we get the following system

    -3*a - 2*b - c + e + 2*f + 3*g = 0
    9*a + 4*b + c + e + 4*f + 9*g = 2
    -27*a - 8*b - c + e + 8*f + 27*g = 0
    81*a + 16*b + c + e + 16*f + 81*g = 0
    -243*a - 32*b - c + e + 32*f + 243*g = 0
    729*a + 64*b + c + e + 64*f + 729*g = 0

     The above system have as solution {a: 1/90, b: -3/20, c: 3/2, e: 3/2,
                                        f: -3/20, g: 1/90}.
     with these coefficients we get the following formula for the first
     derivative

     u''_k = (2*u[k-3] - 27*u[k-2] + 270*u[k-1] - 490*u[k] + 270*u[k+1] -
              27*u[k+2] + 2*u[k+3])/(180*h**2), k=-3,...,K-3.

     for the first and last grid points we have

     a*u[0] + b*u[1] + c*u[2] + d*u[3] + e*u[4]  + f*u[5] + g*u[6] +h*u[7] (2)

     In the above expression we replace u[1], u[2], u[3], u[4], u[5], u[6] and
     u[7] for their seventh order Taylor series expansion around x_0. One more
     time we cancel the the coefficients of all the derivatives but the second
     and we get the system

    b + 2*c + 3*d + 4*e + 5*f + 6*g + 7*h = 0
    b + 4*c + 9*d + 16*e + 25*f + 36*g + 49*h = 2
    b + 8*c + 27*d + 64*e + 125*f + 216*g + 343*h = 0
    b + 16*c + 81*d + 256*e + 625*f + 1296*g + 2401*h = 0
    b + 32*c + 243*d + 1024*e + 3125*f + 7776*g + 16807*h = 0
    b + 64*c + 729*d + 4096*e + 15625*f + 46656*g + 117649*h = 0
    b + 128*c + 2187*d + 16384*e + 78125*f + 279936*g + 823543*h = 0

     The above system has solution : {b: -223/10, c: 879/20, d: -949/18,
                                      e: 41, f: -201/10, g: 1019/180,
                                      h: -7/10}

     Replacing the coefficients in (2) we get

     u'_0 = (938*u[0] - 4014*u[1] + 7911*u[2] - 9490*u[3] + 7380*u[4] -
     3618*u[5] + 1019*u[6] - 126*u[7])/(180*h**2)

     The last term is the first term written from the end in reverse order
     u'_K =(-126*u[K-7] + 1019*u[K-6] - 3618*u[K-5] + 7380*u[K-4] -
     9490*u[K-3] + 7911*u[K-2] - 4014*u[K-1] + 938*u[K])/(180*h**2)


     For the second and the penultimate therm replace u[0], u[2], u[3], u[4],
     u[5], u[6] and u[7] for their seventh order Taylor series expansion around
     x_1. One more time we cancel the the coefficients of all the derivatives
     but the second and we get the system

     -a + c + 2*d + 3*e + 4*f + 5*g + 6*h = 0
     a + c + 4*d + 9*e + 16*f + 25*g + 36*h = 2
     -a + c + 8*d + 27*e + 64*f + 125*g + 216*h = 0
     a + c + 16*d + 81*e + 256*f + 625*g + 1296*h = 0
     -a + c + 32*d + 243*e + 1024*f + 3125*g + 7776*h = 0
     a + c + 64*d + 729*e + 4096*f + 15625*g + 46656*h = 0
     -a + c + 128*d + 2187*e + 16384*f + 78125*g + 279936*h = 0

     The above system has solution : {a: 7/10, c: -27/10, d: 19/4, e: -67/18,
                                      f: 9/5, g: -1/2, h: 11/180}

     Replacing the coefficients in (2) we get:

     u'_1 = ([126*u[0] - 70*u[1] - 486*u[2] + 855*u[3] - 670*u[4] + 324*u[5]
     - 90*u[6] + 11*u[7])/(180*h**2)

     The penultimate term is the second term written from the end in reverse
     order
     u'_{K-1} = (-2*u[K-6] + 15*u[K-5] - 50*u[K-4] + 100*u[K-3] - 150*u[K-2] +
     77*u[K-1] + 10*u[K])/(60*h)

     For the third and the antepenultimate therm we replace u[0], u[1], u[3], u[4],
     u[5], u[6] and u[7] for their seventh order Taylor series expansion around x_2 in
     (2). One more time we cancel the the coefficients of all the derivatives
     but the second and we get the system

     -2*a - b + d + 2*e + 3*f + 4*g + 5*h = 0
     4*a + b + d + 4*e + 9*f + 16*g + 25*h = 2
     -8*a - b + d + 8*e + 27*f + 64*g + 125*h = 0
     16*a + b + d + 16*e + 81*f + 256*g + 625*h = 0
     -32*a - b + d + 32*e + 243*f + 1024*g + 3125*h = 0
     64*a + b + d + 64*e + 729*f + 4096*g + 15625*h = 0
     -128*a - b + d + 128*e + 2187*f + 16384*g + 78125*h = 0

     The above system has solution : {a: -11/180, b: 107/90, d: 13/18,
                                      e: 17/36, f: -3/10, g: 4/45, h: -1/90}

     Replacing the coefficients in (2) we get:

     u'_2 = (-11*u[0] + 214*u[1] - 378*u[2] + 130*u[3] + 85*u[4] -54*u[5] +
     16*u[6] - 2*u[7])/(180*h**2)

     The antepenultimate term is the second term written from the end in reverse
     order
     u'_{K-2} = ([-2*u[K-7] + 16*u[K-6] - 54*u[K-5] + 85*u[K-4] + 130*u[K-3] -
     378*u[K-2] + 214*u[K-1] - 11* u[K]])/(180*h**2)
    """

    return np.r_[
        [
            [938, -4014, 7911, -9490, 7380, -3618, 1019, -126],
            [126, -70, -486, 855, -670, 324, -90, 11],
            [-11, 214, -378, 130, 85, -54, 16, -2],
        ]
        @ x[:8],
        [2, -27, 270, -490, 270, -27, 2]
        @ np.array([x[:-6], x[1:-5], x[2:-4], x[3:-3], x[4:-2], x[5:-1], x[6:]]),
        [
            [-2, 16, -54, 85, 130, -378, 214, -11],
            [11, -90, 324, -670, 855, -486, -70, 126],
            [-126, 1019, -3618, 7380, -9490, 7911, -4014, 938],
        ]
        @ x[-8:],
    ] / (180 * h**2)


def sevenPointsUpWindFirstOrderDiff(x, h):
    """


    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    h : TYPE
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """

    return 2
