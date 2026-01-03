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
from copy import deepcopy
from numbers import Number

import numpy as np

from ..polynomial import Polynomial2


class Operator2:
    """Class that allows to transform a differential problem for functions
    of 2 variables into an algebraic formulation"""

    def __new__(cls, func=None, **kwargs):
        if func is None or isinstance(func, Polynomial2):
            return super().__new__(cls)  # proceed to __init__
        return Operator2(Polynomial2(func, **kwargs))

    def __init__(self, func=None, **kwargs):
        # The empty operator
        if func is None:
            self.func = None
            self.jacobian = None
            self.domain = None
            return
        if isinstance(func, Polynomial2):
            self.func = func
            self.jacobian = np.array([[1]], dtype="O")
            self.domain = func.domain
            self.bases = func.bases

    def cos(self):
        result = deepcopy(self)
        result.func = result.func.cos()
        result.jacobian = -result.func.sin() * result.jacobian
        return result

    def diff(self, order=1):
        result = deepcopy(self)
        result.func = result.func.diff(order)
        # Check if order is a number
        if isinstance(order, Number):
            order = (order, 0)

        if isinstance(order, Iterable):
            if len(order) == 2 and all(
                [isinstance(o, Number) and o >= 0 and int(o) == o for o in order]
            ):
                x_order, y_order = order
            else:
                raise ValueError(
                    "When the order is an iterable it must have "
                    "length 2 and all entries integers"
                )
        else:
            raise TypeError("Order can be only an integer or a length 2 iterable of integers")
        # Update information of the derivatives
        mj, nj = result.jacobian.shape
        njac = np.zeros((y_order + mj, x_order + nj), dtype="O")

        # Differentiate in the x direction shift the derivative information
        # to the bottom while differentiate in the y direction shift de deri-
        # vative information to the right
        njac[-mj:, -nj:] = result.jacobian
        result.jacobian = njac
        return result

    def diffx(self, order):
        return self.diff((order, 0))

    def diffy(self, order):
        return self.diff((0, order))

    def gradient(self):
        return np.array([self.diff((1, 0)), self.diff((0, 1))])

    def laplacian(self):
        return self.diff((2, 0)) + self.diff((0, 2))

    def isempty(self):
        return self.func is None

    def __neg__(self):
        result = deepcopy(self)
        result.func = -result.func
        result.jacobian = -result.jacobian
        return result

    def __pos__(self):
        return deepcopy(self)

    def __add__(self, rhs):
        if self.isempty():
            return deepcopy(self)

        result = deepcopy(self)
        if isinstance(rhs, Operator2):
            # The function is the sum of the of the two Polynomial2
            result.func = result.func + rhs.func
            # The resulting derivatives will have the dimensions of the maximum
            # of the dimensions of en each direction of the input derivatives
            m_lhs, n_lhs = result.jacobian.shape
            m_rhs, n_rhs = rhs.jacobian.shape
            jac_lhs = np.zeros((max(m_lhs, m_rhs), max(n_lhs, n_rhs)), dtype=object)
            jac_rhs = deepcopy(jac_lhs)
            jac_lhs[:m_lhs, :n_lhs] = result.jacobian
            jac_rhs[:m_rhs, :n_rhs] = rhs.jacobian
            result.jacobian = jac_lhs + jac_rhs
            return result
        elif isinstance(rhs, (Number, Polynomial2)):
            result.func = result.func + rhs
            return result
        else:
            raise TypeError(f"Cannot add {type(self)} and {type(rhs)} ")

    def __radd__(self, lhs):
        return self + lhs

    def __sub__(self, rhs):
        return self + (-rhs)

    def __rsub__(self, lhs):
        return -self + lhs

    def __mul__(self, rhs):
        if self.isempty():
            return Operator2()
        result = deepcopy(self)
        if isinstance(rhs, Number):
            result.func = rhs * result.func
            result.jacobian = result.jacobian * rhs
            return result
        elif isinstance(rhs, Polynomial2):
            result.func = result.func * rhs

            for i in range(result.jacobian.shape[0]):
                for j in range(result.jacobian.shape[1]):
                    if result.jacobian[i, j] != 0:
                        result.jacobian[i, j] = result.jacobian[i, j] * rhs

            return result
        else:
            raise TypeError(
                f"The operation * is not defined for types {type(result)} and {type(rhs)}"
            )

    def __rmul__(self, lhs):
        return self * lhs
