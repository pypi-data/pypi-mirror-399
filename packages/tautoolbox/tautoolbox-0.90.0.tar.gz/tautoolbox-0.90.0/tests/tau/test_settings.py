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

from tautoolbox.tau import settings

__author__ = "José Matos"
__copyright__ = "José Matos"
__license__ = "lgpl3"


def test_settings():
    options = settings()
    assert options.degree == 31
