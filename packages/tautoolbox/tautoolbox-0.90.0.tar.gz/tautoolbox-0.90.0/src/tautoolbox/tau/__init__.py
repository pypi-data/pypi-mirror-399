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
tautoolbox: Tau Toolbox for Python
==================================

Provides
  1. Solvers for integro-differential problems.
  2. Associated classes to make easy to operate in the Tau Lanczos method.

Documentation
-------------

Each function and class is documented in place. That documentation is part of
the References Guide.

There are examples available that show how these functions can be used together.

Available sub-packages
---------------------

There are several packages available but they can all be imported from the
tautoolbox namespace.

The recommended way to use this package is to use ``from tautoolbox import tau``

Utilities
---------
version
    tautoolbox version
"""

__all__ = [
    # modules
    "eig",
    "ode",
    "pde",
    "solvers",
    "utils",
    # factories
    "basis",
    "matrix",
    "polynomial",
    "problem",
    "settings",
    "solve",
    # classes
    #  operators
    "Condition",
    "Equation",
    "Operator",
    "Operator2",
    #  problems
    "Problem",
    "Problem2",
]

from . import eig, ode, pde, solvers, utils
from .condition import Condition
from .equation import Equation
from .matrix import matrix
from .operator import Operator
from .operator2 import Operator2
from .options import settings
from .problem import Problem
from .problem2 import Problem2
from .solvers import solve
from .utils import basis, polynomial, problem
