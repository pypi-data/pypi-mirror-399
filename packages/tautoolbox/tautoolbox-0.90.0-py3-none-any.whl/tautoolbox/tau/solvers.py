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
This module provides solvers used by the Tautoolbox.

"""

from . import eig, ode
from .problem import Problem
from .problem2 import Problem2


def solve(problem: Problem, **kwargs):
    """Default hub for Tautoolbox solvers"""
    if not isinstance(problem, (Problem, Problem2)):
        raise ValueError("The input argument must be a tau.Problem*")

    if isinstance(problem, Problem2):
        return problem.solve(**kwargs)

    if problem.kind in ["fred1", "ide", "ode"]:
        return ode.solve(problem, **kwargs)

    # problem.kind == "eig":
    return eig.solve(problem, **kwargs)
