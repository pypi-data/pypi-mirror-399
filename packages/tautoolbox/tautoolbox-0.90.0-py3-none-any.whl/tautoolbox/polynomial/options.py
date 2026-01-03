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
This module provides options used by polynomial classes from Tautoolbox.

"""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np


@dataclass
class Settings:
    """Settings related with the polynomial handling"""

    basis: str = "ChebyshevT"

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def read(options):
        """Functions as a wrapper for the class"""
        if options:
            if isinstance(options, Settings):
                return options
            if isinstance(options, dict):
                return Settings(**options)
            return Settings(basis=options.basis)
        return Settings()


@dataclass
class NumericalSettings:
    """Settings related with the polynomial handling"""

    defaultPrecision: float = np.spacing(1)  # the same as sys.float_info.epsilon
    interpMaxDim: int = 2**9
    interpRelTol: float = np.spacing(1)


numericalSettings = NumericalSettings()
