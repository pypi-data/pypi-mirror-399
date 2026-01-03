# Copyright (C) 2023-2025, University of Porto and Tau Toolbox developers.
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

from tautoolbox.functions import cos
from tautoolbox.polynomial import Polynomial
from tautoolbox.polynomial.bases import ChebyshevU, GegenbauerC, LegendreP

# Test values for the derivative of order 2.7 in the Caputo sense in [-1,1]
test1c = np.array(
    [
        -0.0,
        -0.52217039,
        -0.53002519,
        -0.45295069,
        -0.32149584,
        -0.15239877,
        0.04069979,
        0.24508131,
        0.44854762,
        0.63956442,
    ]
)

# Test values for the derivative of order 2.7 in the Caputo sense in [0,1]
test2c = np.array(
    [
        -0.0,
        0.04918294,
        0.1205123,
        0.20249086,
        0.29096917,
        0.38317776,
        0.47690665,
        0.5702447,
        0.66147549,
        0.74903217,
    ]
)


# Test values for the derivative of order 2.7 in the Riemann-Liouville sense in
# [-1,1]
test1r = np.array(
    [
        np.inf,
        8.89366861,
        0.28927861,
        -0.44282233,
        -0.46278117,
        -0.32306298,
        -0.12885984,
        0.08480793,
        0.29923724,
        0.50086021,
    ]
)

# Test values for the derivative of order 2.7 in the Riemann-Liouville sense in
# [0,1]
test2r = np.array(
    [
        np.inf,
        148.49692047,
        22.24711374,
        7.20582884,
        3.25382682,
        1.82359763,
        1.22168559,
        0.95571661,
        0.84518799,
        0.81254399,
    ]
)


def test_ChebyshevT_derivative_caputo():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1c)


def test_ChebyshevT_derivative_rl():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1r)


def test_ChebyshevT_derivative_caputo_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test2c)


def test_ChebyshevT_derivative_rl_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test2r)


def test_LegendreP_derivative_caputo():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1c)


def test_LegendreP_derivative_rl():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1r)


def test_LegendreP_derivative_caputo_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test2c)


def test_LegendreP_derivative_rl_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))
    assert np.allclose(pdev, test2r)


def test_ChebyshevU_derivative_caputo():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1c)


def test_ChebyshevU_derivative_rl():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1r)


def test_ChebyshevU_derivative_caputo_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test2c)


def test_ChebyshevU_derivative_rl_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))
    assert np.allclose(pdev, test2r)


def test_GegenbauerC_06_derivative_caputo():
    "Using GegenbauerC in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1c)


def test_GegenbauerC_06_derivative_rl():
    "Using GegenbauerC in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test1r)


def test_GegenbauerC_06_derivative_caputo_01():
    "Using GegenbauerC basis in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))
    # Derivative of fractional order in the Caputo sense
    pd = p.diff(2.7)
    pdev = pd(p.linspace(10))

    assert np.allclose(pdev, test2c)


def test_GegenbauerC_06_derivative_rl_01():
    "Using GegenbauerC basis in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))

    # Derivative of fractional order in the Riemann-Liuville sense
    pd = p.diff(2.7, "rl")
    pdev = pd(p.linspace(10))
    assert np.allclose(pdev, test2r)
