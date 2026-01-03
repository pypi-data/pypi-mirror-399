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

from difflib import get_close_matches

from . import eig, ode
from .options import Settings, settings
from .problem import Problem
from .utils import basis as Basis

__opList = [
    "m",
    "multiplication",
    "n",
    "differentiation",
    "o",
    "integration",
    "c",
    "condition",
    "d",
    "operator",
    "t",
    "taumatrix",
    "r",
    "tauresidual",
    "b",
    "taurhs",
    "v",
    "orth2pow",
    "w",
    "pow2orth",
]


def chooseOperator(op):
    """
    chooseOperator - returns a cell list of operators where op fits

    input (required):
       op         = operator (string)

    output:
       opSel      = cell arrays of candidates that satisfy condition

    """

    op = op.lower()

    # test exact match
    if op in __opList:
        return op

    # test approximate match
    opSel = get_close_matches(op, __opList, len(op))

    if len(opSel) == 1:
        return opSel[0]

    if len(opSel) == 0:
        raise ValueError(
            "the 1st input argument must be a prescribed operation ( see help(tau.matrix))"
        )

    hints = ", ".join(__opList)
    raise ValueError(f'operator name "{op}" is ambiguous possible matches are: {hints}')


def matrix(op, problem=None, h=None):
    op = chooseOperator(op)

    if problem is None:
        problem = settings()

    if isinstance(problem, Problem):
        if h is None:
            h = problem.height

        if problem.kind in ["ide", "ode"]:
            return ode.matrix(op, problem, h)
        elif problem.kind == "eig":
            return eig.matrix(op, problem, h)
    elif isinstance(problem, Settings):
        basis = Basis(problem)

        if op in ["m", "multiplication"]:
            return basis.matrixM()
        elif op in ["n", "differentiation"]:
            return basis.matrixN()
        elif op in ["o", "integration"]:
            return basis.matrixO()
        elif op in ["v", "orth2pow"]:
            return basis.orth2powmatrix()
        elif op in ["w", "pow2orth"]:
            return basis.pow2orthmatrix()

    else:
        raise TypeError(
            f"Tautoolbox: the operator {op} requires a tau.problem as second argument"
        )
