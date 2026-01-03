# Copyright (C) 2025, University of Porto and Tau Toolbox developers.
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
This module provides solvers for eigenvalue differential problems.

"""

from .problem import Problem


def solve(problem: Problem, **kwargs):
    if problem.kind != "eig":
        raise ValueError("This solver only supports eigenvalue problems")

    # Currently eigenproblem only works for 1 equation
    if problem.nequations > 1:
        raise ValueError("tautoolbox: not yet prepared for differential eigenvalues problem")


def matrix(op: str, problem: Problem, h: int): ...
