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

import numpy as np

from tautoolbox import polynomial, tau
from tautoolbox.polynomial import ChebyshevT
from tautoolbox.polynomial.bases import BASES

# The sets of domains to test
domains = [[-1, 1], [0, 1]]
# The sets of coefficients to test
coeffs = [np.arange(1, 5), np.arange(12).reshape(3, 4)]
# The sets of values to test
values = [1, np.arange(4), np.arange(9).reshape(3, 3)]

# %% testing basis 'ChebyshevT' in the domain [-1,1]
bas = ChebyshevT(domain=domains[0])

# Test in the case the coefficients which are a vector that represents a poly-
# nomial in this basis


def test_eval_scalar():
    assert bas(coeffs[0], values[0]) == 10


def test_eval_vector():
    assert (bas(coeffs[0], values[1]) == np.array([-2.0, 10.0, 130.0, 454.0])).all()


def test_eval_matrix():
    assert (
        bas(coeffs[0], values[2])
        == np.array(
            [
                [-2.000e00, 1.000e01, 1.300e02],
                [4.540e02, 1.078e03, 2.098e03],
                [3.610e03, 5.710e03, 8.494e03],
            ]
        )
    ).all()


# Test for the case coefficients  are a matrix in which each rows represents
# one Polynomial


def test_eval_scalar_polynomial():
    assert (bas(coeffs[1], values[0]) == np.array([6.0, 22.0, 38.0])).all()


def test_eval_vector_polynomial():
    assert (
        bas(coeffs[1], values[1])
        == np.array(
            [
                [-2.0, 6.0, 94.0, 334.0],
                [-2.0, 22.0, 238.0, 814.0],
                [-2.0, 38.0, 382.0, 1294.0],
            ]
        )
    ).all()


def test_eval_matrix_polynomial():
    assert (
        bas(coeffs[1], values[2])
        == np.array(
            [
                [
                    [-2.0000e00, 6.0000e00, 9.4000e01],
                    [3.3400e02, 7.9800e02, 1.5580e03],
                    [2.6860e03, 4.2540e03, 6.3340e03],
                ],
                [
                    [-2.0000e00, 2.2000e01, 2.3800e02],
                    [8.1400e02, 1.9180e03, 3.7180e03],
                    [6.3820e03, 1.0078e04, 1.4974e04],
                ],
                [
                    [-2.0000e00, 3.8000e01, 3.8200e02],
                    [1.2940e03, 3.0380e03, 5.8780e03],
                    [1.0078e04, 1.5902e04, 2.3614e04],
                ],
            ]
        )
    ).all()


def test_basis_info():
    for cmd in ["all", "supported", "experimental"]:
        output = polynomial.bases.available(cmd)
        assert isinstance(output, list)
        if len(BASES):
            assert isinstance(output[0], str)

    assert sorted(polynomial.bases.available("all")) == sorted(
        polynomial.bases.available("supported") + polynomial.bases.available("experimental")
    )


def test_basis_factory():
    assert isinstance(tau.basis(domain=[0, 1]), polynomial.bases.T3Basis)
    for basis in polynomial.bases.available("all"):
        assert isinstance(tau.basis(basis=basis), polynomial.bases.T3Basis)
