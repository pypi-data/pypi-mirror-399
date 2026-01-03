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

from tautoolbox.functions import cos, sin
from tautoolbox.polynomial import Polynomial
from tautoolbox.polynomial.bases import ChebyshevU, GegenbauerC, LegendreP

# Polynomial construction


def test_ChebyshevT_cos():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    assert ((p(p.linspace()) - cos(p.linspace())) < 1e-15).all()


def test_ChebyshevU_cos():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    assert ((p(p.linspace()) - cos(p.linspace())) < 1e-15).all()


def test_LegendreP_cos():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    assert ((p(p.linspace()) - cos(p.linspace())) < 1e-15).all()


def test_GegenbauerC():
    "Using GegenbauerC basis with alpha = 0.5 in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC())

    assert ((p(p.linspace()) - cos(p.linspace())) < 1e-15).all()


def test_GegenbauerC_07():
    "Using GegenbauerC basis with alpha = 0.7 in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.7))

    assert ((p(p.linspace()) - cos(p.linspace())) < 1e-15).all()


# Polynomial Operation: Product


def test_ChebyshevT_product():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    q = Polynomial(sin)
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert bool(np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15)


def test_ChebyshevT_product_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    q = Polynomial(sin, domain=[0, 1])
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_product():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    q = Polynomial(sin, basis=LegendreP())
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_product_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    q = Polynomial(sin, basis=LegendreP(domain=[0, 1]))
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevU_product():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    q = Polynomial(sin, basis=ChebyshevU())
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevU_product_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    q = Polynomial(sin, basis=ChebyshevU(domain=[0, 1]))
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1.5e-15


def test_GegenbauerC_06_product():
    "Using GegenbauerC basis (alpha=0.6) in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    q = Polynomial(sin, basis=GegenbauerC(alpha=0.6))
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_GegenbauerC_06_product_01():
    "Using GegenbauerC basis (alpha=0.6) in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))

    q = Polynomial(sin, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))
    ptq = p * q

    def f(x):
        return cos(x) * sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevT_sum():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    q = Polynomial(sin)
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevT_sum_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    q = Polynomial(sin, domain=[0, 1])
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_sum():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    q = Polynomial(sin, basis=LegendreP())
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_sum_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    q = Polynomial(sin, basis=LegendreP(domain=[0, 1]))
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-14


def test_ChebyshevU_sum():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    q = Polynomial(sin, basis=ChebyshevU())
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevU_sum_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    q = Polynomial(sin, basis=ChebyshevU(domain=[0, 1]))
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-14


def test_GegenbauerC_06_sum():
    "Using GegenbauerC with alpha=0.6 in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    q = Polynomial(sin, basis=GegenbauerC(alpha=0.6))
    paq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(paq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_GegenbauerC_06_sum_01():
    "Using GegenbauerC basis in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))
    q = Polynomial(sin, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))
    ptq = p + q

    def f(x):
        return cos(x) + sin(x)

    assert np.max(abs(ptq(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevT_power():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-14


def test_ChebyshevT_power_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_power():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-15


def test_LegendreP_power_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-14


def test_ChebyshevU_power():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevU_power_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-14


def test_GegenbauerC_06_power():
    "Using GegenbauerC with alpha=0.6 in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-15


def test_GegenbauerC_06_power_01():
    "Using GegenbauerC basis with alpha=0.6 in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))

    pp = p**3

    def f(x):
        return cos(x) ** 3

    assert np.max(abs(pp(p.linspace()) - f(p.linspace()))) < 1e-15


def test_ChebyshevT_derivative():
    "Using ChebyshevT basis in the domain [-1,1]"
    p = Polynomial(cos)

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_ChebyshevT_derivative_01():
    "Using ChebyshevT basis in the domain [0,1]"
    p = Polynomial(cos, domain=[0, 1])

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_LegendreP_derivative():
    "Using LegendreP basis in the domain [-1,1]"
    p = Polynomial(cos, basis=LegendreP())

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_LegendreP_derivative_01():
    "Using LegendreP basis in the domain [0,1]"
    p = Polynomial(cos, basis=LegendreP(domain=[0, 1]))

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_ChebyshevU_derivative():
    "Using ChebyshevU basis in the domain [-1,1]"
    p = Polynomial(cos, basis=ChebyshevU())

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_ChebyshevU_derivative_01():
    "Using ChebyshevU basis in the domain [0,1]"
    p = Polynomial(cos, basis=ChebyshevU(domain=[0, 1]))

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-10


def test_GegenbauerC_06_derivative():
    "Using GegenbauerC with alpha=0.6 in the domain [-1,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6))

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-12


def test_GegenbauerC_06_derivative_01():
    "Using GegenbauerC basis in the domain [0,1]"
    p = Polynomial(cos, basis=GegenbauerC(alpha=0.6, domain=[0, 1]))

    # Derivative of integer order
    pd = p.diff(2)

    def f(x):
        return -cos(x)

    assert np.max(abs(pd(p.linspace()) - f(p.linspace()))) < 1e-10
