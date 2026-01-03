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

"""A module to deal with integro-differential conditions.

These conditions can be of different types:

* initial;
* boundary;
* interior.

"""

import numbers
from copy import deepcopy

import numpy as np


class Condition:
    """Class to deal with the conditions of integro-differential equations."""

    def __new__(cls, cond=None, nvars=1):
        if isinstance(cond, cls):
            return cond.copy()  # copy constructor
        if callable(cond):
            return cond(cls(nvars=nvars))
        return super().__new__(cls)  # proceed to __init__

    def __init__(self, cond=None, nvars=1):
        if isinstance(cond, self.__class__) or callable(cond):
            return
        if cond is None:
            self.coeff = np.array([1])
            self.order = np.array([0])
            self.point = np.array([])
            self.value = 0
            self.xmin = np.nan
            self.xmax = np.nan
            self.nvars = nvars
            self.var = [1] if self.nvars == 1 else []
            self.varname = "y"
            return
        raise TypeError("Tautoolbox: unknown argument")

    def __call__(self, index):
        result = deepcopy(self)
        if all([len(result.var), len(result.point)]):
            raise TypeError("Tautoolbox: forbidden operation")
        if len(result.var):
            result.point = np.r_[result.point, index]
            result.xmin = result.xmax = index
        else:
            result.var = result.nvars = index

        return result

    def copy(self):
        return deepcopy(self)

    def diff(self, order=None, point=None):
        """Apply derivative to condition variable"""
        result = deepcopy(self)
        if order is None:
            order = 1
        result.order += order
        if point is not None:
            result.point = np.array([point])
        return result

    def __add__(self, rhs):
        result = deepcopy(self)
        if isinstance(rhs, self.__class__):
            result.var = np.r_[result.var, rhs.var]
            result.coeff = np.r_[result.coeff, rhs.coeff]
            result.order = np.r_[result.order, rhs.order]
            result.point = np.r_[result.point, rhs.point]
            result.value += rhs.value
            result.xmax = max(result.xmax, rhs.xmax)
            result.xmin = max(result.xmin, rhs.xmin)
            result.nvars = max(result.var)
        elif isinstance(rhs, numbers.Number):
            result.value -= rhs
        else:
            raise ArithmeticError(
                f"Tautoolbox: You cannot add a Condition with a {type(rhs)} object"
            )
        return result

    def __radd__(self, lhs):
        return self + lhs

    def __pos__(self):
        return deepcopy(self)

    def __neg__(self):
        result = deepcopy(self)
        result.coeff = -result.coeff
        result.value = -result.value
        return result

    def __sub__(self, rhs):
        return self + (-rhs)

    def __rsub__(self, lhs):
        return -self + lhs

    def __mul__(self, rhs):
        result = deepcopy(self)

        result.coeff *= rhs
        result.value *= rhs
        return result

    def __rmul__(self, lhs):
        return self * lhs

    def __truediv__(self, rhs):
        result = deepcopy(self)

        result.coeff = result.coeff / rhs
        result.value = result.value / rhs
        return result

    def isGIVP(self, domain):
        return self.xmax <= domain[1]

    def __str__(self):
        st = ""
        if self.point.size == 0:
            return st

        for k in range(len(self.coeff)):
            if k > 0 and self.coeff[k] > 0:
                st += " + "
            if self.coeff[k] == -1:
                st += "-" if k == 0 else " - "
            elif self.coeff[k] != 1:
                st += f"{self.coeff[k]}"

            vname = f"{self.varname}{self.var[k]}"

            if self.order[k] < 4:
                result = "'"
                st += f"{vname}{result * self.order[k]}"
            else:
                st += f"diff({vname}, {self.order[k]})"
            st += f"({self.point[k]})"
        return st + f" = {self.value}"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        result = deepcopy(self)
        if result.nvars == 1:
            if index == 0:
                return result

            raise IndexError(
                f"Index out of range - the index must be at most {result.nvars - 1}"
            )

        if index < 0 and int(index) != index or index > result.nvars:
            raise ValueError("Index must be a non-negative integer.")
        result.var = [int(index)]
        return result
