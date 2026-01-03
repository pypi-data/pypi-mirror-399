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

import inspect
from collections.abc import Iterable
from numbers import Number


def get_shape(a):
    """
    Returns the shape of `a`, if `a` has a regular array-like shape.

    Otherwise returns None.
    """

    if isinstance(a, Number):
        return ()

    if not isinstance(a, Iterable) or isinstance(a, str):
        return None

    shapes = [get_shape(item) for item in a]
    if len(shapes) == 0:
        return (0,)
    if any(shape is None for shape in shapes):
        return None
    if not all(shapes[0] == shape for shape in shapes[1:]):
        return None
    return (len(shapes),) + shapes[0]


def get_required_args_count(func):
    """Return the number of required (non-default) arguments for a function."""
    sig = inspect.signature(func)
    required_count = 0

    for param in sig.parameters.values():
        if (
            param.default == inspect.Parameter.empty
            and param.kind != inspect.Parameter.VAR_POSITIONAL
            and param.kind != inspect.Parameter.VAR_KEYWORD
        ):
            required_count += 1

    return required_count
