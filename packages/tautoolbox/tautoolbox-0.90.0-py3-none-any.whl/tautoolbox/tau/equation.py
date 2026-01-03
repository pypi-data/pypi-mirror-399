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

import re
from copy import deepcopy
from inspect import getsource

from ..polynomial.polynomial1 import Polynomial


class Equation:
    def __new__(cls, formula, rhs=None):
        if isinstance(formula, cls):
            return formula.copy()  # copy constructor
        if isinstance(formula, (list, tuple)):
            return cls(*formula)
        return super().__new__(cls)  # proceed to __init__

    def __init__(self, formula, rhs=None):
        if isinstance(formula, (self.__class__, list, tuple)):
            return

        if callable(formula):
            self.lhs = formula
            self._lhs_st = re.sub(r"(\s{2})+|,\n", "", getsource(formula))

            self.rhs = rhs if rhs else lambda x: x * 0
            if isinstance(self.rhs, Polynomial):
                self._rhs_st = repr(self.rhs)
            else:
                self._rhs_st = re.sub(r"(\s{2})+|,\n", "", getsource(self.rhs))
        else:
            raise ValueError("Tautoolbox: wrong equation argument")

    def __str__(self):
        st = (
            f"Equation:\n    Left hand side:\n        {self._lhs_st}\n"
            f"     Right hand side:\n        {self._rhs_st}"
        )
        return st

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return deepcopy(self)
