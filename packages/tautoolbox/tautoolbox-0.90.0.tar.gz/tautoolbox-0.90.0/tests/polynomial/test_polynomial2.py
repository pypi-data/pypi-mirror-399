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

from tautoolbox.functions import cos, exp
from tautoolbox.polynomial import ChebyshevU, GegenbauerC, LegendreP, Polynomial2

# The construction of Polynomial2


def test_adaptive_grid_exp():
    "f(x,y) = exp(-100*(x**2 - x*y + 2*y**2 – 1/2)**2)"

    def f(x, y):
        return exp(-100 * (x**2 - x * y + 2 * y**2 - 1 / 2) ** 2)

    p = Polynomial2(f, domain=[[-1, 1], [-1, 1]])

    assert p.sampletest(f, 1e-11)


def test_adaptive_grid_cos():
    "f(x,y) = cos(10*x*(1+y**2))"

    def f(x, y):
        return cos(10 * x * (1 + y**2))

    p = Polynomial2(f, domain=[[0, 1], [0, 1]])

    assert p.sampletest(f, 1e-13)


def test_adaptive_grid_cos_UP():
    "f(x,y) = cos(10*x*(1+y**2)) with different bases for x and y"
    basis_x = ChebyshevU(domain=[0, 1])
    basis_y = LegendreP(domain=[-1, 1])

    def f(x, y):
        return cos(10 * x * (1 + y**2))

    p = Polynomial2(f, bases=(basis_x, basis_y))

    assert p.sampletest(f, 1e-13)


def test_adaptive_grid_polynomial_CC():
    "f(x,y)= x**2+2*x*y**2 + 5*x**3*y +x*y"
    basis_x = GegenbauerC(domain=[0, 1], alpha=0.6)
    basis_y = GegenbauerC(domain=[-1, 1], alpha=1.2)

    def f(x, y):
        return x**2 + 2 * x * y**2 + 5 * x**3 * y + x * y

    p = Polynomial2(f, bases=(basis_x, basis_y))

    assert p.sampletest(f, 1e-13)


def test_adaptive_grid_cos_UP2():
    "f(x,y) = cos(10*x*(1+y**2))"
    basis_x = ChebyshevU(domain=[0, 1])
    basis_y = LegendreP(domain=[-1, 1])

    def f(x, y):
        return cos(10 * x * (1 + y**2))

    p = Polynomial2(f, bases=(basis_x, basis_y))

    assert p.sampletest(f, 1e-13)


def test_fixed_grid_exp_aca():
    "f(x,y) = exp(-100*(x**2 - x*y + 2*y**2 – 1/2)**2)"
    "Using aca with a fixed grid"
    bases = (LegendreP(), LegendreP())

    def f(x, y):
        return exp(-100 * (x**2 - x * y + 2 * y**2 - 1 / 2) ** 2)

    p = Polynomial2(f, bases=bases, method="aca", grid_shape=(200, 100))

    assert p.sampletest(f, 1e-7)


def test_fixed_grid_exp_svd():
    "f(x,y) = exp(-100*(x**2 - x*y + 2*y**2 – 1/2)**2)"
    # Using aca with a fixed grid
    bases = (LegendreP(), LegendreP())

    def f(x, y):
        return exp(-100 * (x**2 - x * y + 2 * y**2 - 1 / 2) ** 2)

    p = Polynomial2(f, bases=bases, method="svd", grid_shape=(200, 100))
    assert p.sampletest(f, 1e-7)


def test_polynomial2_product():
    "Testing the product"
    # f(x,y) = cos(10*x*(1+y**2)) and g(x,y) = (1+10*(x+2*y)**2)**-1

    def f(x, y):
        return cos(10 * x * (1 + y**2))

    def g(x, y):
        return (1 + 10 * (x + 2 * y) ** 2) ** -1

    basis_x = ChebyshevU(domain=[0, 1])
    basis_y = LegendreP(domain=[-1, 1])
    bases = (basis_x, basis_y)

    fp = Polynomial2(f, bases=bases)
    gp = Polynomial2(g, bases=bases)

    def fm(x, y):
        return f(x, y) * g(x, y)

    pm = fp * gp

    assert pm.sampletest(fm, 1e-12)


def test_polynomial2_sum():
    "testing the addition"
    # f(x,y) = cos(10*x*(1+y**2)) and g(x,y) = (1+10*(x+2*y)**2)**-1

    def f(x, y):
        return cos(10 * x * (1 + y**2))

    def g(x, y):
        return (1 + 10 * (x + 2 * y) ** 2) ** -1

    basis_x = ChebyshevU(domain=[0, 1])
    basis_y = LegendreP(domain=[-1, 1])
    bases = (basis_x, basis_y)
    fp = Polynomial2(f, bases=bases)
    gp = Polynomial2(g, bases=bases)

    def fm(x, y):
        return f(x, y) + g(x, y)

    pm = fp + gp
    assert pm.sampletest(fm, 1e-11)
