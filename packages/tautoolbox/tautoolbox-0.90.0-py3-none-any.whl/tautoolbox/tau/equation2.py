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

import sympy as sp
from sympy.core.function import AppliedUndef


class Equation2:
    def __init__(self, eq):
        if isinstance(eq, str):
            sides = eq.split("=")
            if len(sides) == 1:
                sides = sp.sympify(sides[0])
                self.ind_vars = [str(i) for i in sides.free_symbols]
                self.dep_var = set(
                    [
                        str(i.func)
                        for i in sides.atoms(sp.Function)
                        if isinstance(i, AppliedUndef)
                    ]
                )
                args = sp.Add.make_args(sides)
                rhs = []
                for arg in args:
                    if (
                        len(
                            [
                                f.func
                                for f in arg.atoms(sp.Function)
                                if isinstance(f, AppliedUndef)
                            ]
                        )
                        == 0
                    ):
                        rhs.append(arg)
                        args.remove(arg)
                self.lhs = sum(args)
                self.rhs = -sum(rhs)
                diff_terms = self.lhs.atoms(sp.Derivative)
                self.diff_terms = diff_terms
                self.deriv_order = {
                    (str(vo.args[-1][0]), int(vo.args[-1][1])) for vo in diff_terms
                }
