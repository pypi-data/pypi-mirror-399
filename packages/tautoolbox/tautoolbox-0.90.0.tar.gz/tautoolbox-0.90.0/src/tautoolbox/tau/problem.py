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

import warnings

import numpy as np

from ..polynomial.bases import family_basis
from ..polynomial.polynomial1 import Polynomial
from ..utils import get_required_args_count
from .condition import Condition
from .equation import Equation
from .operator import Operator
from .options import settings


class Problem:
    """Class that allows to analysed and then solve differential problems"""

    validkinds = ["auto", "eig", "ide", "ode"]

    def __init__(self, equation, domain, conditions=None, options=None, kind="auto"):
        options = settings() if options is None else options.copy()
        self.domain = domain

        self.basis = family_basis(options.basis, domain=self.domain)
        self.n = options.degree + 1

        # process equation
        if callable(equation):
            equation = [equation]

        if len(equation) == 2 and all([callable(form) for form in equation]):
            if any([isinstance(form, Polynomial) for form in equation]) or any(
                [get_required_args_count(form) == 1 for form in equation]
            ):
                equation = [equation]

        self.nequations = len(equation)

        hasIntegral = 0
        isEig = np.zeros(self.nequations)

        self.derivOrder = np.zeros((self.nequations, self.nequations), dtype=int)
        self.height = [None] * self.nequations
        self.equations = [None] * self.nequations

        self.isLinearized = False
        self.n_terms = []
        self.fred_kernels = []

        for k in range(self.nequations):
            self.equations[k] = Equation(equation[k])

            if get_required_args_count(self.equations[k].lhs) == 3:
                self.isLinearized = True

            info = self.inspect_equation(self.equations[k])

            self.height[k] = info["height"]
            self.derivOrder[k, :] = info["derivOrder"]
            isEig[k] = info["isEig"]
            hasIntegral = hasIntegral or info["hasIntegral"]
            self.n_terms.append(info["n_terms"])
            self.fred_kernels.append(info["fred_kernels"])

        # Process conditions

        if callable(conditions):
            conditions = conditions(Condition(nvars=self.nequations))

        if isinstance(conditions, (str, Condition)):
            conditions = [conditions]
        elif conditions is None:
            conditions = []

        self.nconditions = len(conditions)
        self.conditions = [None] * self.nconditions
        self.isGIVP = True

        for k in range(self.nconditions):
            self.conditions[k] = Condition(conditions[k], nvars=self.nequations)
            if any(self.conditions[k].point < self.domain[0]) or any(
                self.conditions[k].point > self.domain[1]
            ):
                raise ValueError(
                    f"Tautoolbox: error in condition {k}, a point "
                    "is outside of of the domain of integration"
                )
            if not self.conditions[k].isGIVP(self.domain):
                self.isGIVP = False

        if kind == "auto":
            if any(isEig):
                self.kind = "eig"
            elif self.nequations == 1 and self.n_terms[0] == len(self.fred_kernels[0]):
                self.kind = "fred1"
                self.kernel = sum(self.fred_kernels[0])
                self.rhs = Polynomial(self.equations[0].rhs, basis=self.basis)
            elif hasIntegral:
                self.kind = "ide"
            else:
                self.kind = "ode"
        else:
            self.kind = kind

        # Validate problem components
        # If possible recover issuing a warning, if not issue an error
        if self.derivOrder.max(initial=0).sum() != self.nconditions:
            warnings.warn(
                "Tau Toolbox: the Number of conditions does not fit with order of equations"
            )

        # Assign the number of conditions to be distributed by each equation
        self.condpart = self.derivOrder.max(1)

    def inspect_equation(self, equation):
        x = Polynomial(basis=self.basis)
        y = Operator(self.basis, 2, self.nequations)

        # check if equation.lhs have only 2 variables with non default arguments
        if get_required_args_count(equation.lhs) == 2:
            D = equation.lhs(x, y)
        else:
            D = equation.lhs(x, y, x)
        res = {
            "derivOrder": D.odiff,
            "isEig": isinstance(equation.rhs, list),
            "height": D.opHeight(),
            "hasIntegral": any(D.hasIntegral),
            "n_terms": D.n_terms,
            "fred_kernels": D.fred_kernels,
        }

        if res["isEig"]:
            for i in range(len(equation.rhs)):
                if equation.rhs[i] is not None:
                    D = equation.rhs[i](
                        Polynomial(basis=self.basis), Operator(self.basis, self.n)
                    )
                    res["height"] = max(res.height, D.opHeight())
        return res

    def __str__(self):
        if self.kind == "fred1":
            st = (
                "Fredholm integral equation of the first kind:\n\n"
                "kernel:\n"
                f"{self.kernel}\n\n"
                "rhs:\n"
                f"{self.rhs}"
            )
            return st

        st = f"Tau problem of type {self.kind}:\n"
        st += f" * Integration domain: {self.domain}\n"
        if self.nequations == 1:
            st += " * 1 equation:\n"
            st += f"   lhs:  {self.equations[0]._lhs_st}\n\n"
            st += f"   rhs:  {self.equations[0]._rhs_st}\n\n"
        else:
            st += f"System of {self.nequations}:\n"
            for k in range(self.nequations):
                st += f"   Equation #{k}:\n"
                st += f"     lhs:  {self.equations[k]._lhs_st}\n\n"
                st += f"     rhs:  {self.equations[k]._rhs_st}\n\n"
        if self.nconditions == 0:
            st += " * No condition/constraints\n"
        elif self.nconditions == 1:
            st += " * 1 condition/constraints\n"
            st += f"      {self.conditions[0]}"
        else:
            st += f" * {self.nconditions} conditions\\constraints\n"
            for k in range(self.nconditions):
                st += f"    #{k}: {self.conditions[k]}\n\n"
        return st

    def __repr__(self):
        return str(self)

    @staticmethod
    def isKind(kind):
        return kind in Problem.validkinds
