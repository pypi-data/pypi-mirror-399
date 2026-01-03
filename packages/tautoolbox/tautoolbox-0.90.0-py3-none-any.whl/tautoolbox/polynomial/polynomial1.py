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
This module provides objects related with polynomial functions used by Tautoolbox.

"""

import warnings
from collections.abc import Iterable
from copy import deepcopy
from math import ceil, floor
from numbers import Number
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import eigvals, qr
from scipy.sparse import spdiags
from scipy.sparse.linalg import spsolve

from ..utils import get_shape
from .bases import (
    ChebyshevU,
    LegendreP,
    family_basis,
    leg2chebt,
    standard_chop,
)
from .options import Settings, numericalSettings


class Polynomial:
    r"""
    A class used to represent a polynomial in one variable. Implemented using
    three-terms based polynomial families.

    Attributes
    ----------
    source : array_like or function
        An array like representing the coefficients of the polynomial in the
        given basis and domain or the function to be approximated
    domain : array_like, optional
        A 2 by 2 array_like object where each row is the domain of an
        independent variable in the order given by bases (default is [-1, 1]).
    basis : an orthogonal basis, optional
        The names of the basis for the independent variable.
    options : polynomial.Settings

    Notes
    -----
    This is the form of representing a Polynomial
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]` and

    .. math::
        \P (x) =a_{0}P_0(x) + a_{1}P_1(x) + ... + a_{n}P_n.
        \quad (x) \in [a,b]

    Therefore the coefficients are represented by :math:`[a_{i}]_{n}`
    """

    __array_priority__ = 1000
    istranspose = False

    def __new__(
        cls,
        source=None,
        domain=(-1, 1),
        *,
        basis=None,
        options=None,
        **kwargs,
    ):
        if isinstance(source, cls):
            return source.copy()  # copy constructor

        basis = Polynomial.choose_basis(basis, domain, options)
        # in the case where coeff is not an array_like of numbers
        if get_shape(source) is None and isinstance(source, (list, tuple)):
            coeff_list = [Polynomial(y, basis=basis).coeff for y in source]
            max_len = max(len(v) for v in coeff_list)
            coeff = np.zeros((len(coeff_list), max_len))
            for i, vec in enumerate(coeff_list):
                coeff[i, : len(vec)] = vec
            return Polynomial(coeff, basis=basis)

        if callable(source):
            if kwargs:
                return Polynomial.interp1(source, basis, **kwargs)

            # try first the polynomial version
            try:
                result = source(Polynomial(basis=basis))
                if isinstance(result, cls):
                    return result
                if isinstance(result, Number):
                    return Polynomial(result, basis=basis)
                raise ValueError(f"Wrong type: {type(result)}")
            except (ValueError, TypeError):
                # If the above fails use a low rank approximation
                return Polynomial.interp1(source, basis, **kwargs)

        return super().__new__(cls)  # proceed to __init__

    def __init__(
        self,
        source: Optional[np.ndarray] = None,
        domain=(-1, 1),
        options=None,
        *,
        basis=None,
        nequations=1,
        **kwargs,
    ):
        shape = get_shape(source)
        if (shape is None and isinstance(source, (list, tuple))) or callable(source):
            return

        self.basis = Polynomial.choose_basis(basis, domain, options)
        if source is None:
            # Construct the identity Polynomial
            coeff = self.basis.x1

            if nequations > 1:
                coeff = np.array([self.basis.x1 for i in range(nequations)])
        # If source is a single number
        elif isinstance(source, Number):
            coeff = np.array([source], dtype="float64")
        # Coeff is an array_like
        elif shape is not None:
            coeff = np.array(source)
        else:
            raise TypeError(
                f"tautoolbox: Polynomial -{type(source)} cannot be the 1st argument"
            )

        # Check if coeff has the right dimensions
        if coeff.ndim > 2:
            raise ValueError("The dimension of the coefficients must at most be 2")
        vals = kwargs.get("vals", False)
        if vals:
            n = coeff.shape[-1]
            ab, *_ = self.basis.nodes(n)
            self.coeff = self.basis.interp_from_values(coeff, ab)
        else:
            self.coeff = coeff.copy()

    @staticmethod
    def choose_basis(basis, domain, options):
        if basis is None:
            options = Settings.read(options)

            domain = np.array(domain)
            basis = family_basis(options.basis, domain)
        elif isinstance(basis, str):
            domain = np.array(domain)
            basis = family_basis(basis, domain)
        else:
            basis = basis.copy()
        return basis

    @property
    def domain(self):
        return self.basis.domain

    @property
    def n(self):
        """
        Compute the length of the coefficients array of a Polynomial.

        Returns
        -------
        n : int
            Length of the coefficients array

        Examples
        --------
        Approximate cos(x) on [-1, 0] using Legendre basis:

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(np.cos, basis="LegendreP", domain=[-1, 0])
        >>> p
        <class 'tautoolbox.polynomial.polynomial1.Polynomial'> object with 1 column:
          degree         : 12
          domain         : [-1.00  0.00]
          end values     : [0.54 1.00]
          vertical scale : 1.0
          basis          : LegendreP
        >>> p.n
        13

        """
        return self.coeff.shape[-1]

    @property
    def degree(self):
        """
        Compute the polynomial degree.

        Returns
        -------
        degree : int
            The polynomial degree

        """
        return self.n - 1

    @property
    def nequations(self):
        """
        Compute the number of polynomials.

        Returns
        -------
        nequations : int
            Number of polynomials

        """
        if self.coeff.ndim == 1:
            return 1
        return self.coeff.shape[0]

    @property
    def T(self):
        """
        Compute the transpose of a polynomial.

        Returns
        -------
        polynomial
            Transpose of a polynomial

        """
        result = self.copy()
        result.istranspose = not result.istranspose
        return result

    def append(self, p):
        """
        Append polynomial p to self. Only appends if both are columns or
        rows polynomials.

        Parameters
        ----------
        p : polynomial
            Polynomial to append to ``self``.

        Raises
        ------
        TypeError
            This occurs when ``p`` is not a polynomial. It also happens when
            both self and p are polynomials, but one is a column polynomial
            and the other is a row polynomial, or vice versa. It can also occur
            when they are both column or row polynomials but do not share the
            same options.

        Returns
        -------
        polynomial
            A polynomial with the rows or columns of ``p`` added to it.

        Examples
        ---------
        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(np.cos)
        >>> p.n
        15
        >>> q = Polynomial(np.sin)
        >>> q.n
        14
        >>> # Since the polynomials have different lengths, a zero will
        >>> # be appended to the end of the shorter polynomial in the
        >>> # corresponding column (or row).
        >>> pq = p.append(q)
        >>> pq.n
        15

        """

        if not isinstance(p, Polynomial):
            raise TypeError("Only two polynomials can be appended.")

        if self.istranspose != p.istranspose:
            raise TypeError("You are trying to append polynomial columns with polynomial rows.")

        if self.basis != p.basis:
            raise TypeError("Both polynomials must share the same options")

        if p.n == self.n:
            coeff = np.r_["0,2", self.coeff, p.coeff]
        elif p.n > self.n:
            coeff = np.r_["0,2", self.extend(p.n).coeff, p.coeff]
        else:
            coeff = np.r_["0,2", self.coeff, p.extend(self.n).coeff]

        return Polynomial(coeff, basis=self.basis)

    def __repr__(self):
        """
        This is a representation only for summary purpose.

        Returns
        -------
        str
            Representation of the object

        """
        return self.info(type(self))

    def info(self, dtype=None):
        """
        This is a representation only for summary purpose.

        Returns
        -------
        str
            Representation of the object
        """

        if self.size == 1 and self.coeff.ndim == 2:
            return self[0].__repr__()

        tr = "row" if self.istranspose else "column"
        with np.printoptions(
            precision=2, legacy=False, formatter={"float": lambda x: f"{x:0.2f}"}
        ):
            if self.size == 1:
                return (
                    f"{dtype} object with 1 {tr}:\n"
                    f"  degree         : {self.n - 1}\n"
                    f"  domain         : {self.domain}\n"
                    f"  end values     : {self(self.domain)}\n"
                    f"  vertical scale : {self.vscale:.3}\n"
                    f"  basis          : {self.basis.name}\n"
                )

            info = f"{dtype} object with {self.size} {tr}s:\n"
            for i in range(self.size):
                info += (
                    f"\n  {tr} {i + 1}:\n"
                    f"    degree         : {self.n - 1}\n"
                    f"    domain         : {self.domain}\n"
                    f"    end values     : {self(self.domain)[i]}\n"
                    f"    vertical scale : {self.vscale[i]:.3}\n"
                    f"    basis          : {self.basis.name}\n"
                )
            return info

    @staticmethod
    def significantTerms(cn, tol=None):
        """
        Returns the length of the array of coefficients from which
        all the coefficients are less than ``tol`` in absolute value.

        Parameters
        ----------
        cn : ndarray
        tol : float, optional
            Tolerance. When not given, machine eps is used. The default
            is None.

        Returns
        -------
        int
            Number of significant terms

        Examples
        --------
        Compute the significant terms of cos(x) with the standard options,
        using a tolerance of 1e-14

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(np.cos)
        >>> p.n
        15
        >>> Polynomial.significantTerms(p.coeff, 1e-14)
        13

        """
        if tol is None:
            tol = np.spacing(1)
        pos = np.argwhere(abs(cn) > tol)[:, -1]
        return 1 if pos.size == 0 else max(pos) + 1

    def __add__(self, rhs):
        """
        Parameters
        ----------
        rhs : array_like
            can be a list, a tuple or a Tau polynomial object

        Returns
        -------
        Polynomial
            Sum is a Tau polynomial object

        Examples
        --------
        a and b are instances of Tau polynomial:

        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial([[1, 0, 1], [2, 0, 1], [3, 0, 1]])
        >>> a.coef
        array([[1,0,1],
               [2,0,1],
               [3,0,1]])
        >>> b = Polynomial([[1, 0, 1, 0], [2, 0, 1, 0], [3, 0, 1, 0]])
        >>> b.coef
        array([[1, 0, 1, 0],
               [2, 0, 1, 0],
               [3, 0, 1, 0]])
        >>> c = a + b
        >>> c.coef
        array([[2,0,2],
               [4,0,2],
               [6,0,2]])

        a is a Tau polynomial and b is a list congruent to a matrix where the
        list represents the coefficients of a Tau polynomial in the same basis:

        >>> b = Polynomial([[1, 0, 1, 0], [2, 0, 1, 0], [3, 0, 1, 0]])
        >>> c = a + b
        >>> c.coef
        array([[2, 0, 2],
               [4, 0, 2],
               [6, 0, 2]])

        a is a Tau polynomial and b is a scalar representing the degree 0
        polynomial:

        >>> c = a + 2
        >>> c.coeff
        array([[3., 0., 1.],
               [4., 0., 1.],
               [5., 0., 1.]])

        """
        result = self.copy()
        if isinstance(rhs, Number):
            result.coeff[..., 0] = result.coeff[..., 0] + rhs
            return result

        if not isinstance(rhs, Polynomial):
            raise TypeError(
                "tautoolbox: you can only sum a Tau polynomial with an rhs Tau polynomial"
            )
            # the coefficients must be congruent to a matrix or vector

        result.coeff = result.basis.add(result.coeff, rhs.coef)
        return result.trim()

    def __radd__(self, lhs):
        return self + lhs

    def __pos__(self):
        """
        to enable operations like b = +a

        Returns
        -------
        polynomial


        """
        return self

    def __neg__(self):
        """
        The same as -a

        Returns
        -------
        Polynomial
            -1 times the polynomial

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial([[1, 0, 1], [2, 0, 1], [3, 0, 1]])
        >>> a.coef
        array([[1, 0, 1],
               [2, 0, 1],
               [3, 0, 1]])

        >>> b = -a
        >>> b.coef
        array([[-1,  0, -1],
               [-2,  0, -1],
               [-3,  0, -1]])

        >>> a = Polynomial([1, 0, 1])
        >>> a.coef
        array([1, 0, 1])

        >>> b = -a
        >>> b.coef
        array([-1,  0, -1])

        """

        result = self.copy()
        result.coeff = -result.coeff
        return result

    def __sub__(self, rhs):
        """
        Parameters
        ----------
        rhs : array_like
            can be a list, a tuple or a Tau polynomial object

        Returns
        -------
        Polynomial
            Subtraction is a Tau polynomial object

        Examples
        --------
        a and b are instances of Tau polynomial:

        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial([[1, 0, 1], [2, 0, 1], [3, 0, 1]])
        >>> b = Polynomial([[1, 0, 1, 0], [2, 0, 1, 0], [3, 0, 1, 0]])
        >>> c = a - b
        >>> c.coef
        array([[0],
               [0],
               [0]])
        >>> c = b - a
        >>> c.coef
        array([[0],
               [0],
               [0]])

        """

        if isinstance(rhs, Iterable):
            rhs = np.array(rhs)

        return self + (-rhs)

    def __rsub__(self, lhs):
        return -self + lhs

    def __mul__(self, rhs):
        """
        Parameters
        ----------
        rhs : array_like
            can be a list, a tuple or a Polynomial object

        Returns
        -------
        Polynomial
            the sum is a tau Polynomial object

        Examples
        --------

        """
        # The case when you multiply a polynomial by a constant
        if isinstance(rhs, Number):
            # When rhs is 0 must return a null polynomial
            if rhs == 0:
                result = self.copy()
                result.coeff = result.coeff[..., :1]
                result.coeff[:] = 0
                return result
            result = self.copy()
            result.coeff *= rhs
            return result

        # This import really needs to be here to avoid circular import
        from .polynomial2 import Polynomial2  # noqa

        if isinstance(rhs, Polynomial2):
            if self.basis != rhs.basis_y:
                raise TypeError(
                    "Polynomial2 options in the y direction must be "
                    "the same as the Polynomial options"
                )

            result = rhs.copy()
            result.cols = result.cols * self
            return result

        if not isinstance(rhs, Polynomial):
            return rhs * self

        if self.istranspose == rhs.istranspose:
            # in the case where is two Polynomials they must have same basis

            if self.basis != rhs.basis:
                raise TypeError("The two polynomial must share the same basis")

            # The case When at least one of the polynomials are null
            if np.all(self.iszero()):
                return self.copy()

            if np.all(rhs.iszero()):
                return rhs.copy()

            # The case when at least one the polynomials are constant
            if self.n == 1:
                result = self.copy()
                result.coeff = result.coeff * rhs.coeff
                return result

            if rhs.n == 1:
                result = rhs.copy()
                result.coeff = result.coeff * self.coeff
                return result

            bas = self.basis
            result = Polynomial(bas.productv2(self.coeff, rhs.coeff), basis=bas).trim()
            result.istranspose = self.istranspose

            return result

        if rhs.istranspose:
            if self.size != rhs.size:
                raise ValueError("Inconsistent size")
            # In this case return a Polynomial2 which cols are self and
            # rows are rhs

            p = Polynomial2()
            p.basis_x = rhs.bases
            p.basis_y = self.basis
            p.cols = self.copy()
            p.rows = rhs.T
            p.diag = np.ones(self.size)
            return p

        # default
        return self.inner_product(rhs)

    def __rmul__(self, lhs):
        return self * lhs

    def __truediv__(self, rhs):
        if rhs == 0:
            raise ZeroDivisionError("division by zero")
        result = self.copy()
        result.coeff = result.coeff / rhs
        return result

    def __pow__(self, order):
        if order != int(order) or order < 0:
            raise ValueError("order must be a positive integer or zero.")

        base = self.copy()
        if order == 0:
            base.coeff = np.ones_like(base.coeff[..., :1])
        if order < 2:
            return base

        result = None
        exponent = int(order)
        while exponent > 0:
            if exponent % 2 == 1:
                if result is None:
                    result = base.copy()
                else:
                    result = result * base

            if exponent > 1:  # Avoid unnecessary computation on last iteration
                base = base * base

            exponent //= 2
        return result

    @staticmethod
    def interp1(fx, basis):
        """
        Parameters
        ----------
        fx : a function to interpolate
        basis : T3Basis
            a tau basis object from which we want to work.

        Returns
        -------
        cn : Polynomial
            a Tau polynomial approximation of the function in the working basis
            case x is a non polynomial function or an exact representation
            otherwise.

        Examples
        --------

        a) fx is a polynomial function, using the default basis 'ChebyshevT'

        >>> from tautoolbox.polynomial import Polynomial
        >>> np.set_printoptions(precision=3)
        >>> a = Polynomial(lambda x: x**5 + x**3 + 1)

        b) fx is a non polynomial function

        >>> Polynomial.interp1(np.cos, polynomial.ChebyshevT()).coeff
        array([ 7.652e-01, -1.830e-17, -2.298e-01,  1.830e-17,  4.953e-03,
                1.003e-17, -4.188e-05, -4.365e-18,  1.884e-07, -7.972e-18,
               -5.261e-10, -1.070e-17,  1.000e-12,  1.297e-17, -1.371e-15])

        c) fx is a polynomial function, using 'LegendreP':

        >>> Polynomial.interp1(lambda x: x**5 + x**3 + 1, polynomial.LegendreP()).coeff
        array([1.   , 1.029, 0.   , 0.844, 0.   , 0.127])

        """

        try:
            x = Polynomial(basis=basis)
            return fx(x) + 0 * x
        except (ValueError, TypeError):
            return Polynomial.interp1f(fx, basis)

    @staticmethod
    def interp1f(fx, basis, tol=None, **kwargs):
        """
        Parameters
        ----------
        fx : function
            Function to approximate by a polynomial.
        basis : polynomial.bases.T3Basis
        **kwargs : optional arguments
            see polynomial.bases.T3Basis.interp1f

        Returns
        -------
        array_like
            an array with the coefs of the polynomial approximation of the
            function in the working basis.

        Examples
        --------

        working with the default basis 'ChebyshevT':

        >>> from tautoolbox.polynomial import Polynomial
        >>> np.set_printoptions(precision=3)
        >>> Polynomial.interp1f(np.cos, polynomial.ChebyshevT()).coeff
        array([ 7.652e-01, -1.830e-17, -2.298e-01,  1.830e-17,  4.953e-03,
                1.003e-17, -4.188e-05, -4.365e-18,  1.884e-07, -7.972e-18,
               -5.261e-10, -1.070e-17,  1.000e-12,  1.297e-17, -1.371e-15])

        working with 'LegendreP':

        >>> y = Polynomial.interp1f(lambda x: x**10 + 2 * x + 1, polynomial.LegendreP())
        >>> y.coeff
        array([1.091e+00,  2.000e+00,  3.497e-01, -1.613e-16,  3.357e-01,
                1.090e-16,  1.711e-01,  3.218e-17,  4.711e-02,  1.013e-16,
                5.542e-03])

        >>> y = Polynomial.interp1f(np.cos, polynomial.ChebyshevT())
        >>> y.coeff
        array([ 7.652e-01, -1.830e-17, -2.298e-01,  1.830e-17,  4.953e-03,
                1.003e-17, -4.188e-05, -4.365e-18,  1.884e-07, -7.972e-18,
               -5.261e-10, -1.070e-17,  1.000e-12,  1.297e-17, -1.371e-15])
        """
        if tol is None:
            tol = numericalSettings.interpRelTol
        n = 4
        nd = 8

        while n < numericalSettings.interpMaxDim and nd >= n:
            n *= 2
            f, *_ = basis.interp1f(fx, n=n, **kwargs)
            # Get the n when the coefficients has hit a plateau below or tol
            nd = standard_chop(f, tol)

        if n >= numericalSettings.interpMaxDim:
            warnings.warn(
                "Tautoolbox: Polynomial.interp1: did not converge."
                "You can change interpRelTol or interpMaxDim from numericalSettings"
            )
        return Polynomial(f[..., :nd], basis=basis)

    @staticmethod
    def interp1p_coeff(fx, n, basis):
        try:
            x = Polynomial(basis=basis)
            y = fx(x) + 0 * x
            f = y.coeff
            if len(f) < n:
                f = np.r_[f, np.zeros(n - len(f))]

            if y.n <= n:
                return f
            return f[:n]

        except (TypeError, ValueError):
            return basis.interp1f(fx, n=n)[0]

    def arccos(self):
        """
        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            arccos function with a Tau polynomial in the working basis, being
            'ChebyshevT' the default basis.

        Examples
        --------

        The case when p is the identity function:

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial()

        In this case the interpolation did not converge with the default options:

        >>> p.arccos().coef[:5]
        array([ 1.571e+00, -1.273e+00, -5.152e-19, -1.415e-01, -1.084e-17])

        """
        return Polynomial(lambda x: np.arccos(self(x)), basis=self.basis)

    def arccosh(self):
        """
        The function arccosh(x) has domain [1, +oo[ and is not smooth in the
            neighborhood of 1.


        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            arccosh function with a Tau polynomial in the working basis, being
            'ChebyshevT' the default basis.

        Examples
        --------

        The case when p is the identity using default settings and domain
        [2, 6]:

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(domain=[2, 6])
        >>> p.arccosh().coef
        array([ 1.985e+00,  5.624e-01, -8.271e-02,  1.692e-02, -4.043e-03,
                1.063e-03, -2.990e-04,  8.826e-05, -2.702e-05,  8.508e-06,
               -2.739e-06,  8.975e-07, -2.984e-07,  1.004e-07, -3.412e-08,
                1.169e-08, -4.038e-09,  1.403e-09, -4.905e-10,  1.723e-10,
               -6.079e-11,  2.153e-11, -7.656e-12,  2.731e-12, -9.770e-13,
                3.505e-13, -1.260e-13,  4.545e-14, -1.649e-14,  5.916e-15,
               -2.126e-15,  7.284e-16, -3.140e-16])

        """
        return Polynomial(lambda x: np.arccosh(self(x)), basis=self.basis)

    def cos(self):
        """
        Returns
        -------
        result : Polynomial
            returns a Tau Polynomial representation of the composition of the
            cosine function with a Tau polynomial in the working basis, being
            'ChebyshevT' the default basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a.cos().coef
        array([ 7.652e-01, -1.830e-17, -2.298e-01,  1.830e-17,  4.953e-03,
                1.003e-17, -4.188e-05, -4.365e-18,  1.884e-07, -7.972e-18,
               -5.261e-10, -1.070e-17,  1.000e-12,  1.297e-17, -1.371e-15])
        """
        return Polynomial(lambda x: np.cos(self(x)), basis=self.basis)

    def arcsin(self):
        """
        This function arcsin(x) has domain [-1 , 1] ans is not smooth in the
        neighborhood of -1 and 1.

        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            arcsin function with a Tau polynomial in the working basis, being
            'ChebyshevT' the default basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(domain=[-0.5, 0.5])
        >>> p.arcsin().coef
        array([ 2.24158799e-17,  5.17315809e-01, -9.53073127e-18,  6.07901609e-03,
                -6.33748428e-18,  1.95205291e-04, -4.04032921e-18,  8.31669941e-06,
                4.01467383e-18,  4.05616478e-07, -1.92341409e-18,  2.14178546e-08,
                -6.20516420e-18,  1.19167469e-09,  1.45648262e-18,  6.88084592e-11,
                -2.44819959e-18,  4.08447050e-12, -4.82932725e-18,  2.47709838e-13,
                2.61226315e-18,  1.52770895e-14, -2.05408418e-18,  9.52428779e-16,
                2.24066320e-19,  6.08094524e-17])
        """
        return Polynomial(lambda x: np.arcsin(self(x)), basis=self.basis)

    def cosh(self):
        """
        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            cosine hyperbolic function with a Tau polynomial in the working basis,
            being 'ChebyshevT' the default basis.

        Examples
        --------

        The case when p is the identity function in the default settings:

        >>> p = polynomial.Polynomial()
        >>> p.cosh().coef
        array([1.266e+00,  3.396e-17,  2.715e-01, -2.650e-17,  5.474e-03,
                1.093e-17,  4.498e-05, -1.435e-17,  1.992e-07, -1.040e-17,
                5.506e-10,  7.476e-18,  1.039e-12, -3.770e-17,  1.409e-15])

        """
        return Polynomial(lambda x: np.cosh(self(x)), basis=self.basis)

    def sin(self):
        """
        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            sine function with a Tau polynomial in the working basis, being
            'ChebyshevT' the default basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a.sin().coef
        array([ 3.318e-17,  8.801e-01, -3.443e-17, -3.913e-02,  3.092e-19,
                4.995e-04,  3.899e-19, -3.005e-06, -1.453e-17,  1.050e-08,
                1.967e-17, -2.396e-11,  1.160e-17,  3.852e-14])
        """
        return Polynomial(lambda x: np.sin(self(x)), basis=self.basis)

    def sinh(self):
        """
        Returns
        -------
        result : Polynomial
            returns a Tau polynomial representation of the composition of the
            sine hyperbolic function with a Tau polynomial in the working basis,
            being 'ChebyshevT' the default basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a.sinh().coef
        array([5.573e-17,  1.130e+00, -2.454e-17,  4.434e-02, -2.281e-17,
                5.429e-04, -7.121e-18,  3.198e-06, -1.242e-17,  1.104e-08,
                1.394e-17,  2.498e-11, -3.019e-18,  3.996e-14])
        """
        return Polynomial(lambda x: np.sinh(self(x)), basis=self.basis)

    def exp(self):
        """
        Returns
        -------
        Polynomial
            returns a Tau polynomial representation of the composition of the
            exponential function with a Tau polynomial in the working basis,
            being 'ChebyshevT' the default basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a.exp().coef
        array([1.266e+00, 1.130e+00, 2.715e-01, 4.434e-02, 5.474e-03, 5.429e-04,
               4.498e-05, 3.198e-06, 1.992e-07, 1.104e-08, 5.506e-10, 2.498e-11,
               1.039e-12, 3.990e-14, 1.398e-15])
        """
        return Polynomial(lambda x: np.exp(self(x)), basis=self.basis)

    def linspace(self, n=None):
        """
        Parameters
        ----------
        n : int, optional
            number of samples to generate. If n is none the number of point is
            50.

        Returns
        -------
        array
            an array with n samples equally spaced across the domain.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a.linspace(21)
        array([-1. , -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1,  0.,
                0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9,  1. ])
        """
        if n is None:
            return np.linspace(*self.domain, 100)
        return np.linspace(*self.domain, n)

    def trim(self, tol=np.spacing(1)):
        result = self.copy()
        ind = np.where(abs(result.coeff) > tol)[-1]
        if ind.size == 0:
            result.coeff = result.coeff[..., :1] * 0
        else:
            result.coeff = result.coeff[..., : max(ind) + 1]

        return result

    def __call__(self, x):
        """
        Parameters
        ----------
        x : array_like or a number
            an array, or any list congruent with an array, or a number.

        Returns
        -------
        array_like or a number
            if the input is a number then the output is a number. If the input
            is array_like then the output is an array of the same dimension.

        Examples
        --------

        x is a number:

        >>> from tautoolbox.polynomial import Polynomial
        >>> a = Polynomial()
        >>> a(2)
        array(2.)

        x is one-dimensional  array_like:

        >>> a([1, 2])
        array([1., 2.])

        x is two-dimensional array_like:

        >>> a([[1, 2], [1, 3]])
        array([[1., 2.],
               [1., 3.]])

        """

        # if self.coef.ndim == 1:
        #     return self.basis(self.coef, x)

        # return np.array(
        #     [self.basis(self.coef[i], x) for i in range(self.nequations)]
        # )
        x = np.array(x)  # convert input to numerical array

        return self.basis(self.coeff, x)

    def diff(self, order=1, kind=None):
        """
        Differentiate a polynomial to the given order.

        Parameters
        ----------
        order : Integer, optional
            The default is 1. The order of differentiation.

        Returns
        -------
        Polynomial
            A Tau polynomial which is the result of the derivation

        """
        # When the order is integer
        if round(order) == order:
            order = round(order)  # ensure that order is an integer
            if order == 0:
                return self

            result = self.copy()
            result.coeff = result.coeff @ np.linalg.matrix_power(result.basis.matrixN(result.n).T, order)
            return result

        # When the order is fractional
        fpolynomial = FPolynomial(self.copy())
        return fpolynomial.fractionalDerivative(order, kind)

    def integrate(self, order=1, k=None):
        """
        Integrate the Polynomial to the given order where k are the constants
        of integration. The first constant are the constant of the first
        integration, the second constant are the constant of the second inte-
        gration and so on


        Parameters
        ----------
        order : Integer, optional
            The default is 1. The order of integration
        k : Number or list, optional
            DESCRIPTION. The default is []. The constants of integration. The
            first constant corresponds to the first integration constant the
            second constant corresponds to the second integration constant and
            so on.

        Returns
        -------
        Polynomial
            A Polynomial which is the result of the integration

        """

        if order < 0 or int(order) != order:
            raise ValueError(f"The degree must be a non-negative integer was given {order}.")
        if k is None:
            k = []
        if isinstance(k, list):
            if k == []:
                k = [0] * order
            else:
                k = k + [0] * (order - len(k))
        if isinstance(k, int):
            k = [k] + [0] * (order - 1)

        if len(k) > order:
            raise ValueError(
                "The Number of integration constants must be less than the integration order"
            )

        p = self.copy()
        result = p.coeff
        for i in range(order):
            result = np.r_["-1", result, np.zeros_like(result[..., :1])]
            result = result @ self.basis.matrixO(self.n + i + 1).T
            result[..., 0] = result[..., 0] - self.basis(result, 0) + k[i]

        p.coeff = result
        return p

    @property
    def power_coef(self):
        """
        Returns an array_like object where the entries are the coefficients of
        each row in the power basis

        Returns
        -------
        Array_like
            The coefficients in the power basis

        Examples
        --------

        using the basis ChebyshevT  and the domain [-1,1]:

        >>> from tautoolbox.polynomial import Polynomial
        >>> coef = np.eye(3)
        >>> p = Polynomial(coef)
        >>> p.power_coef
        array([[ 1.,  0.,  0.],
               [ 0.,  1.,  0.],
               [-1.,  0.,  2.]])

        now using the basis ChebyshevU and domain [-1,1]:

        >>> p = Polynomial(coef, basis="ChebyshevU")
        >>> p.power_coef
        array([[ 1.,  0.,  0.],
               [ 0.,  2.,  0.],
               [-1.,  0.,  4.]])

        now using LegendreP basis and domain [-3,0]:

        >>> coef = np.arange(9).reshape(3, 3)
        >>> coef
        array([[0, 1, 2],
               [3, 4, 5],
               [6, 7, 8]])
        >>> p = Polynomial(coef, basis="LegendreP", domain=[-3, 0])
        >>> p.power_coef
        array([[ 3.        ,  4.66666667,  1.33333333],
               [12.        , 12.66666667,  3.33333333],
               [21.        , 20.66666667,  5.33333333]])

        """
        return self.basis.to_power_coeff(self.coeff)

    def plot(self, ax=None, **kwargs):
        """
        Plots a Polynomial
        """
        plt.style.use("ggplot")
        if ax is None:
            ax = plt.gca()
        xx = self.linspace()
        yy = self(xx)
        if self.size > 1:
            xx = np.repeat(xx.reshape(1, -1), self.size, axis=0)
        ax.plot(xx.T, yy.T, **kwargs)
        return ax

    def __len__(self):
        """
        Computes the length.

        Returns
        -------
        n : int
            Length

        """

        return self.n

    @property
    def size(self):
        """Returns the number of coordinates of the vector.
        For a scalar function the size is 1."""
        return self.nequations

    def definite_integral(self, bounds=None, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with the
        interval set in bounds

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable, optional
            The default is None. A real valued iterable with
            2 elements. When the bounds are not given we assumes the bounds
            as the domain of the polynomial.

        Returns
        -------
        Number or an array of numbers
            The result of the definite integral, can be a
            number of an array of numbers in the case the polynomial has more
            than one row.

        Examples
        --------

        using the default settings:

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(np.arange(6).reshape(2, 3))
        >>> p.definite_integral()
        array([-1.33333333,  2.66666667])

        Now considering the ChebyshevU basis, compute the definite integral
        between 0 an 1:

        >>> p = Polynomial(np.arange(6).reshape(2, 3), basis="ChebyshevU")
        >>> p.definite_integral((0, 1))
        array([1.66666667, 8.66666667])

        """
        if bounds is None:
            bounds = self.domain

        return self.basis.definite_integral(bounds, self.coeff, fast)

    def inner_product(self, other, broadcast=False):
        """
        Compute the L2 inner product of two Polynomials

        When broadcast is false does simply the definite integral of self*other
        over the domain, otherwise the result is a matrix whose i,j entry is the
        inner product of the ith row of self with the jth column of other.

        Parameters
        ----------
        other : TYPE
        broadcast : bool
           If broadcast is true then the
           result is a matrix whose i,j entry is the inner product of the ith
           row of self with the jth column of other.

        Returns
        -------

        """

        self.istranspose = other.istranspose

        return np.array(
            [(self * other[i]).definite_integral() for i in range(other.size)]
        ).reshape(self.size, other.size)

    def inner_product2(self, other):
        x = Polynomial(np.tile(self.coeff, (other.size, 1)), basis=self.basis)
        y = Polynomial(
            np.repeat(other.coeff.reshape(self.size, -1), self.size, axis=0),
            basis=other.basis,
        )
        return (x * y).definite_integral()

    def __getitem__(self, index):
        if not isinstance(index, (int, slice, list)):
            raise TypeError("The index must an integer or a slice object")

        result = self.coeff.copy()
        if result.ndim == 1:
            result = result.reshape(1, -1)

        if isinstance(index, (slice, list)):
            if result.size == 0:
                raise IndexError("Cannot return a Polynomial with these slice parameters")
            result = result[index]

            result = Polynomial(result, basis=self.basis)
            result.istranspose = self.istranspose
            return result

        if index < -self.size or index >= self.size:
            raise IndexError(f"Index out of bound the Polynomial only have {self.size} rows")
        result = Polynomial(result[index], basis=self.basis)
        result.istranspose = self.istranspose
        return result

    def get_coef(self, n=None):
        if n is None:
            return self.coef
        if not (isinstance(n, Number) and int(n) == n):
            raise TypeError("n must be a positive integer.")
        n = int(n)
        if n < 1:
            raise ValueError("n must be a positive integer.")

        lc = self.n  # the number of coefficients

        if n <= lc:
            return self.coeff[..., :n].copy()

        pad = [[0, 0]] * self.coeff.ndim
        pad[-1] = [0, n - lc]
        return np.pad(self.coeff, pad)

    def coef_to_val(self, **kwargs):
        # Compute the values of the function on the ChebyshevU points
        if self.n == 1:
            return self.coeff.copy()

        bas = ChebyshevU(domain=self.domain)
        return self(bas.nodes(self.n)[0])

    def simplify(self, tol=None):
        if tol is None:
            tol = numericalSettings.interpRelTol

        vs = self.vscale
        toli = tol * np.max(vs) / vs
        if self.coeff.ndim == 1:
            m = standard_chop(self.coeff, toli)
        else:
            m = max([standard_chop(p.coeff, t) for t, p in zip(toli, self)])
        return self.extend(m)

    @property
    def vscale(self):
        """
        Returns an estimate of the maximum of the absolute value of self

        Parameters
        ----------
        type : TYPE, optional
            The default is None.

        Returns
        -------
        vs : TYPE

        """

        return np.max(abs(self.coef_to_val()), axis=-1)

    def iszero(self, tol=None):
        if tol is None:
            tol = self.vscale * numericalSettings.defaultPrecision

        if isinstance(tol, np.ndarray):
            tol = tol.reshape(-1, 1)

        res = np.all(self(self.domain) <= tol, axis=-1)
        if np.any(res):
            res &= np.all(self.coeff == 0, axis=-1)
        return res

    def roots(self, kind=None, tol=None, htol=None, **kwargs):
        """
        Estimates of the roots of a polynomial

        Parameters
        ----------
        kind : str, optional
            Can be 'real' or 'complex' if not is given assumes 'real'
        htol : scalar, optional
            A tolerance on the extremes of the domain
        **kwargs :

        Returns
        -------
        r :

        """
        if tol is None:
            tol = numericalSettings.interpRelTol
        if kind is None:
            kind = "real"
        kind = kind.lower()

        if htol is None:
            htol = 1e-12
        co = self.coeff

        dom = self.domain
        if self.size == 1:
            if co.ndim == 2:
                co = co.flatten()
            # Find the position in which all coefficients from this position are
            # in the neighborhood of zero
            nzPos = np.argwhere(abs(co) > tol)

            # The trivial case where all coefficients are 0 so the function is zero
            # function so pick a  point in the domain we choose the mid-point of
            # the domain

            n = None if nzPos.size == 0 else np.max(nzPos)

            # The trivial case with zero function. the root can be every point on
            # the domain we choose the mid-point
            if n is None:
                r = np.array([0])

            # The non-zero constant function
            elif n == 0:
                r = np.zeros(0)

            # the case when f= mx+b

            else:
                r = eigvals(self.basis.companion(co[: n + 1]))
                if kind == "real":
                    r = r[r.imag == 0].real
            # Scale the roots to the interval
            if (dom != [-1, 1]).any():
                r = (np.sum(dom) + np.diff(dom) * r) / 2
            r = r[(r > dom[0] - htol) & (r < dom[1] + htol)]
            r.sort()

            r[abs(r - dom[0]) < htol] = dom[0]
            r[abs(r - dom[1]) < htol] = dom[1]
            return r

        r_list = [self[i].roots() for i in range(self.size)]
        le = list(map(len, r_list))
        r = np.empty((self.size, max(le)))
        r[:] = np.nan
        for i, el in enumerate(le):
            if el > 0:
                r[i, :el] = r_list[i]
        return r

    def critical(self):
        """
        The critical points of a Polynomial. These are the roots of the
        first derivative plus the extremes of the domain.

        Returns
        -------
        array_like
            the critical points of the polynomial

        """

        return self.diff().roots()

    def max(self, glob=True):
        """
        Computes the max of a Polynomial

        Parameters
        ----------
        glob :  optional

        Returns
        -------

        """
        dom = self.domain
        if glob:
            if self.size == 1:
                crit = np.array(list(set(np.r_[dom, self.critical()])))
                vals = self(crit)
                max_pos = vals.argmax()
                return np.array([vals[max_pos], crit[max_pos]])
            else:
                return np.array([self[i].max() for i in range(self.size)])

        else:
            if self.size == 1:
                crit = self.critical()
                vals = self.diff(2)(crit)
                max_pos = np.where(vals < 0)
                vals = self(crit[max_pos])
                crit = crit[max_pos]
                if np.isscalar(vals):
                    vals = np.array([vals])
                ext_vals = self(dom)
                ext_max = np.argmax(ext_vals)
                if (vals < ext_vals[ext_max]).all():
                    vals = np.r_[vals, ext_vals[ext_max]]
                    crit = np.r_[crit, dom[ext_max]]

                sort_ind = crit.argsort()

                return vals[sort_ind], crit[sort_ind]

            else:
                return [self[i].max(glob=False) for i in range(self.size)]

    def min(self, glob=True):
        """
        Computes the min of a Polynomial

        Parameters
        ----------
        glob :  optional

        Returns
        -------

        """
        # The min of a polynomial p are the max of -p
        return (-self).max(glob=glob)

    def sign(self):
        if self.size == 1:
            part = np.array(list(set(self.roots()).union(self.domain)))
            part.sort()

            mid = (part[:-1] + part[1:]) / 2
            vals = self(mid)
            sig = np.ones_like(mid, dtype=int)
            sig[vals < 0] = -1
            return part, sig
        else:
            return [self[i].sign() for i in range(self.size)]

    def norm(self, ord=None):
        """
        Compute the norm of order ``ord``.

        Parameters
        ----------
        ord : integer or str, optional
            A integer or string representing the order of the norm

        Returns
        -------
        scalar or vector
            The norm of each row of the Polynomials

        """
        if isinstance(ord, str):
            ord = ord.lower()

        # the norm   is sqrt(integral(p^2))  in the domain
        if ord in [None, "fro"]:
            ord = 2

        # The norm max(abs(p)). This occur in the critical points or in the ex-
        # tremes of the domain
        if ord in ["inf", np.inf]:
            if self.size == 1:
                return np.max(np.abs(self(np.r_[self.critical(), self.domain])))
            else:
                return np.array([self[i].norm(ord=np.inf) for i in range(self.size)])

        # the norm is min(abs(p))
        elif ord in ["-inf", -np.inf]:
            if self.size == 1:
                # If the Polynomial has at lest one zero so its norm(-inf)
                # must zero

                if len(self.roots()) > 0:
                    return 0

                # Otherwise it may occur on the on the critical points or
                # extreme of the domain
                return np.min(np.abs(self(np.r_[self.critical(), self.domain])))
            else:
                return np.array([self[i].norm(ord=-np.inf) for i in range(self.size)])

        # when ord is n the result is integral(abs(p**n))**(1/n)
        elif isinstance(ord, int):
            # The case where the order is even
            if ord % 2 == 0:
                if ord == 2:
                    return np.sqrt((self * self).sum())
                return (self**ord).sum() ** (1 / ord)

            # When the order is odd
            else:
                if self.size == 1:
                    bounds, sign = self.sign()
                    return sum(
                        [(self**ord).sum(bounds[i : i + 2]) * sign[i] for i in range(len(sign))]
                    ) ** (1 / 3)
                else:
                    return np.array([self[i].norm(ord) for i in range(self.size)])

        else:
            raise ValueError(
                "Possible orders are: None, 1,2,'fro','-inf','inf',"
                "np.inf,-np.inf, or an integer positive."
            )

    def mean(self):
        r"""
        Returns de mean of the function over the domain. This means:

        .. math::
            \frac{1}{b-a}\int_a^b p(x)dx


        Returns
        -------
        scalar or vector
            The mean of the function over the domain

        """

        return self.definite_integral() / np.diff(self.domain)

    def cumsum(self, order=1):
        r"""
        Computes the nth order indefinite integral of a Polynomial in such way that
        this integral evaluated at the left extreme of the domain is zero; i.e.
        Q(a)=0 where Q is this integral. This is not to be confused with the
        method integrate where we can specify the constant of integration.

        Parameters
        ----------
        order : optional
            The default is 1.

        Returns
        -------


        """
        if order < 0:
            raise ValueError(f"order must be greater than 0 was given {order}.")

        if int(order) != order:
            return FPolynomial(self.copy()).fractionalIntegral(order)

        result = self.copy()

        for _ in range(order):
            result = result.integrate()
            result = result - result(result.domain[0])

        return result.trim()

    def extractBoundaryRoots(self, numRoots=None):
        result = self.copy()
        m = result.size

        # The multiplicity of the roots
        rootsLeft, rootsRight = np.zeros((2, m))
        # Tolerance for root (we will this with each run of the loop below if)
        # there are multiple roots)
        tol = 1e3 * result.vscale

        # Values at endpoints
        endValues = abs(result(result.domain))

        if np.all(np.min(endValues, axis=-1) > tol):
            return result, rootsLeft, rootsRight

        # Get the coefficients
        c = result.coef

        while (numRoots is None and np.any(np.min(endValues, axis=-1) <= tol)) or np.any(
            numRoots > 0
        ):
            if numRoots is None:
                # Roots at the left
                ind = np.where(endValues[..., 0] <= tol)[-1]
                if ind.size > 0:
                    sgn = 1
                    rootsLeft[ind] += 1

                else:
                    sgn = -1
                    ind = np.where(endValues[..., 1] <= tol)[-1]
                    rootsRight[ind] += 1
            else:
                if np.any(numRoots[..., 0]):
                    # Roots at the left
                    ind = endValues[..., 0] <= tol
                    indNumRoots = numRoots[..., 0] > 0
                    if ind == indNumRoots:
                        sgn = 1
                        numRoots[ind, 0] -= 1
                        rootsLeft += 1
                    else:
                        numRoots[..., 0] = 0
                        continue
                elif np.any(numRoots[..., 1]):
                    # Roots at the right
                    ind = endValues[..., 1] <= tol
                    indNumRoots = numRoots[..., 1] > 0
                    if ind == indNumRoots:
                        sgn = -1
                        numRoots[ind, 1] -= 1
                        rootsRight += 1
                    else:
                        numRoots[..., 1] = 0
                        continue
            # Construct the matrix of recurrence

            n = result.n
            e = np.ones(n - 1)
            d = spdiags(
                [np.r_[1, 0.5 * e[1:]], sgn * e, 0.5 * e],
                [0, 1, 2],
                n - 1,
                n - 1,
                format="csc",
            )

            # Compute the new coefficients

            c[ind, :-1] = sgn * spsolve(d, c[ind, 1:].T).T

            # Pad zero at the highest coefficients

            c[ind, -1] = 0
            endValues = abs(result(result.domain))
            # Loosen the tolerance for checking multiple roots
            tol *= 1e2

        return result.simplify(), rootsLeft, rootsRight

    def extend(self, n):
        r"""
        This method return a polynomial that add zeros to the columns from
        self.n to n if n > self.n; otherwise a polynomial that are self trimmed
        at n.

        Parameters
        ----------
        n : int
            The number of coefficients the columns must have

        Returns
        -------
        result : Polynomial
            A polynomial identical to self but with exactly n coefficients per
            column

        Examples
        --------

        Using ChebyshevT basis in the [-1,1] domain:

        >>> from tautoolbox.polynomial import Polynomial
        >>> p = Polynomial(lambda x: x + 2 * x * 3 * x**2 - x**3 + 5 * x**4)
        >>> p.coef
        array([1.875, 4.75 , 2.5  , 1.25 , 0.625])
        >>> p.extend(7).coef
        array([1.875, 4.75 , 2.5  , 1.25 , 0.625, 0.   , 0.   ])
        >>> p.extend(3).coef
        array([1.875, 4.75 , 2.5  ])

        """
        result = self.copy()
        # The length of the polynomial
        sn = result.n
        if n > sn:
            # When n is greater than the length of polynomial pad with zeros
            pad = [[0, 0]] * result.coeff.ndim
            pad[-1] = [0, n - sn]
            result.coeff = np.pad(result.coeff, pad)
        else:
            # Cut the coefficients at n
            result.coeff = result.coeff[..., :n]
        return result

    def qr(self):
        r"""
        QR factorization of array_like Polynomial. where self is Polynomial
        with n rows, produces a Polynomial Q with n orthonormal rows and an
        n x n upper triangular matrix R such that A = Q*R.

        Returns
        -------
        q : TYPE
            DESCRIPTION.
        r : TYPE
            DESCRIPTION.

        """
        # The trivial case when self has only one row
        if self.size == 1:
            r = np.sqrt(self.inner_product(self))
            if r != 0:
                q = self / r
            else:
                q = 1 / np.sqrt(np.diff(self.domain).item()) + 0 * self

            return q, r
        if self.basis.name == "ChebyshevT":
            # for reason and don't know this method only work with ChebyshevT
            q_coef, r = self._qr_builtin()

        else:
            q_coef, r = self._qr_builtin1()

        q = Polynomial(q_coef.T, basis=self.basis)
        return q, r

    def _qr_builtin(self):
        result = self.copy()
        n, m = result.size, result.n
        if m < n:
            result = result.extend(n)
            m = n
        co = result.coeff
        # Compute the weighted QR factorization
        bas = self.basis.copy()
        bas.domain = [-1, 1]

        b = LegendreP()
        x, wl, *_ = b.nodes(m)
        # Weighted QR with Gauss Legendre weighs.
        w = (wl) ** (1 / 2)
        # Undo the weights used for QR
        winv = (wl) ** (-1 / 2)

        converted = (Polynomial(co, basis=bas)(x) * w).T

        q, r = qr(converted)

        s = np.sign(np.diag(r))

        s[s is False] = 1

        q = (q.T * winv).T * s
        q = leg2chebt(b.idlt(q.T))

        r = (r.T * s).T
        rescale_factor = 0.5 * np.diff(self.domain)
        q = q / rescale_factor ** (1 / 2)
        r = r * rescale_factor ** (1 / 2)

        return q.T, r

    def _qr_builtin1(self):
        """ """
        result = self.copy()
        n, m = result.size, result.n
        if m < n:
            result = result.extend(n)
            m = n
        co = result.coeff

        # Compute the weighted QR factorization
        bas = self.basis.copy()
        bas.domain = [-1, 1]

        x, wl, *_ = bas.nodes(m)
        # Weighted QR with Gauss Legendre weighs.
        w = (wl) ** (1 / 2)
        # Undo the weights used for QR
        winv = (wl) ** (-1 / 2)

        converted = (Polynomial(co, basis=bas)(x) * w).T

        q, r = qr(converted)

        s = np.sign(np.diag(r))

        s[s is False] = 1

        q = (q.T * winv).T * s
        q = bas.interp_from_values(q.T, x)

        r = (r.T * s).T
        rescale_factor = 0.5 * np.diff(self.domain)
        q = q / rescale_factor ** (1 / 2)
        r = r * rescale_factor ** (1 / 2)

        return q.T, r

    def multiply_matrix(self, rhs: np.ndarray):
        # When rhs is an array_like object it must have the same numbers of rows
        rhs = np.array(rhs)
        if np.prod(rhs.shape) == 1:
            return Polynomial(rhs.item() * self.coeff, basis=self.basis)

        # Do a broadcasting so the coefficients
        if rhs.ndim == 1:
            return Polynomial(self.coeff * rhs[..., np.newaxis], basis=self.basis)

        # Because we implements Polynomial in rows
        # what we find here is the transpose of what is supposed in
        # Tautoolbox matlb

        return Polynomial(rhs.T @ self.coeff, basis=self.basis)

    def sample(self, n=None):
        if n is None:
            n = self.n

        return self(self.basis.nodes(n)[0])

    @staticmethod
    def randnPol(basis, lam=1, n=1, trig=False, big=False):
        r"""
        returns a Polynomial with settings given by options with maximum
        frequency <= 2pi/lam and distribution N(0,1). Can be seen as the path
        of a standard Gaussian process

        Parameters
        ----------
        lam : scalar, optional
            the inverse frequency
        n : integer, optional
            the numbers of columns of the Polynomial
        trig : bool, optional
            In this case  return the coefficients of a trigonometric series
            i.e. Fourier series in the domain given by settings
        big : bool, optional
            Normalize the output by dividing it by (lam/2)**(1/2).
            The default is False.

        Returns
        -------
        Polynomial or, array_like

        """
        if trig:
            L = np.diff(basis.domain).item()
            m = floor(L / lam)
            c = np.random.randn(2 * m + 1, 2 * n)
            ii = np.concatenate((np.arange(2 * m, -1, -2), np.arange(1, 2 * m, 2)))
            c = c[ii, :].T
            c = (c[:n, :] + 1j * c[n : 2 * n, :]) * 2 ** (-1 / 2)
            c = (c + np.flip(c.conjugate(), axis=1)) * 2 ** (-1 / 2)

            if big:
                c = c * L ** (-1 / 2)
            else:
                c = c * (2 * m + 1) ** (-1 / 2)

            return c

        else:
            domain = basis.domain
            dom = domain[0] + np.r_[0, 1.2 * np.diff(domain)]
            m = (np.diff(domain).item() / lam).__round__()
            new_basis = basis.copy()
            new_basis.domain = dom
            c = Polynomial.randnPol(basis, lam=lam, n=n, trig=True, big=big)
            x, *_ = new_basis.nodes(5 * m + 20)
            v = new_basis.trigeval(c, x, dom)
            p = Polynomial(v, basis=basis, vals=True)

            return p.simplify(1e-13)

    def copy(self):
        return deepcopy(self)

    def flipud(self):
        r"""
        returns a Polynomial P_1 which is the original Polynomial P_0 flipped
        180 degrees in the domain [a,b] of P_0; i.e. P_1(x)=P_0(a+b-x). If P_0
        are row Polynomials, flip the order of the rows.

        Returns
        -------
        Polynomial
            as described above

        """
        if self.istranspose:
            return self.T.fliplr().T
        result = self.copy()
        result.coeff[..., 1::2] = -result.coeff[..., 1::2]
        return result

    def fliplr(self):
        r"""
        returns a Polynomial P_1 which is the original Polynomial P_0 flipped
        180 degrees in the domain [a,b] of P_0, if P_0 are row Polynomials, i.e.
        P_1(x)=P_0(a+b-x). If P_0 are column Polynomials, flip the order of
        the columns.

        Returns
        -------
        Polynomial
            as described above

        """

        if self.istranspose:
            return self.T.flipud().T
        result = self.copy()
        if result.size > 1:
            result.coeff = np.flip(result.coeff, axis=0)
        return result

    def flip(self, axis=None):
        r"""
        Flip according with the axis 0 meaning flipud and 1 meaning fliplr.

        Parameters
        ----------
        axis : int, optional
            When axis is None flip acaccording if the Polynomial are columns or
            rows . The default is None.

        Raises
        ------
        ValueError
            When axis is not in [None,0,1].

        Returns
        -------
        Polynomial
            As described above.

        """
        if axis not in [None, 0, 1]:
            raise ValueError(f"Axis must in [None,0,1] was given {axis}")
        if self.istranspose:
            if axis is None or axis == 1:
                return self.fliplr()
            return self.flipud()
        else:
            if axis is None or axis == 0:
                return self.flipud()
            return self.fliplr()

    # Aliases
    # from here to below will add aliases to some properties and methods

    # concat is an alias to append
    concat = append

    # sum is an alias to definite_integral
    def sum(self, bounds=None, axis=None):
        r"""

        Parameters
        ----------
        bounds : , optional
            A tuple with the limits of integration, when not given we assume
            the boundaries  of the domain. The default is None.
        axis : int, optional
            Either 0 or 1 when not given simple compute the defini-
            te integral over the domain. If self is a polynomial in columns
            axis=0 compute the definite integral over ``bounds`` and axis=1
            compute a polynomial with one columns whose coefficients are the sum
            of the array of coefficients in the axis=1.
            When self is a polynomial in rows it is the opposite.

        Raises
        ------
        ValueError
            When the axis is neither 0 nor 1 or when the axis do not match co-
            lumns/rows

        Returns
        -------
        Polynomial,number, or ndarray
            The definite integral or a Polynomial depending on the axis.

        """
        if axis is None:
            return self.definite_integral(bounds)

        if self.istranspose:
            if axis == 1:
                return self.T.sum(bounds)
            elif axis == 0:
                return self.T.sum(bounds, axis=1).T
            else:
                raise ValueError(f"Axis can be only 0, 1 or None was Given {axis}.")

        if axis == 1:
            if bounds is not None:
                raise ValueError("Cannot integrate over this axis")
            result = self.copy()
            if result.coeff.ndim > 1:
                result.coeff = result.coeff.sum(axis=0)
            return result
        elif axis == 0:
            return self.definite_integral(bounds)

        else:
            raise ValueError(f"Axis can be only 0, 1 or None was Given {axis}.")

    @property
    def coef(self):
        """
        Gets the coefficients of a Polynomial

        Parameters
        ----------
        glob :  optional

        Returns
        -------

        """
        return self.coeff

    coeffs = coef


polynomial = Polynomial  # convert later into a factory: noqa


class FPolynomial:
    r"""
    Class for functions of the form of :math:`(x+1)^\alpha*P(x)*(x-1)^\beta`
    """

    def __init__(self, poly: Polynomial, exponents=None):
        self.polynomial = poly.copy()
        if exponents is None:
            self.exponents = np.zeros(2)
        else:
            self.exponents = np.array(exponents)

    def __call__(self, x):
        res = self.polynomial(x)
        if not any(self.exponents):
            return res
        dom = self.polynomial.domain
        xc = (2 * x - sum(dom)) / np.diff(dom).item()
        res *= (xc + 1) ** self.exponents[0] * (xc - 1) ** self.exponents[1]
        return res

    def __repr__(self):
        rep = self.polynomial.info(type(self))
        with np.printoptions(precision=2):
            rep += f"  exponents      : {self.exponents.tolist()}\n"
        return rep

    @property
    def coeff(self):
        return self.polynomial.coeff

    def copy(self):
        return deepcopy(self)

    def diff(self, order=1, kind=None):
        """
        Differentiate a polynomial to the given order.

        Parameters
        ----------
        order : Integer, optional
            The default is 1. The order of differentiation.

        Returns
        -------
        Polynomial
            A Tau polynomial which is the result of the derivation

        """
        # When the order is integer
        if round(order) == order:
            result = self.copy()
            for _ in range(order):
                result = result.integerDerivative()
            return result

        # When the order is fractional
        return self.fractionalDerivative(order, kind)

    def fractionalDerivative(self, order, kind=None):
        """
        Fractional derivative of a polynomial to the given order.

        Parameters
        ----------
        order :
            The order of fractional differentiation.

        Returns
        -------
        tau.FPolynomial
            A Tau fractional polynomial which is the result of the fractional derivation
        """
        if order == round(order):
            return self.diff(order)

        if kind is None:
            kind = "c"
        elif kind.lower() in ["c", "caputo"]:
            kind = "c"
        elif kind.lower() in ["rl", "r-l", "riemann-liouville"]:
            kind = "r"
        else:
            raise ValueError(
                "kind must be in ['c','caputo'] for Caputo fractional derivati"
                "ve or in ['rl','r-l','Riemann-Liouville'] for Riemann-Liouvil"
                f"le fractional derivative. '{kind}' is given."
            )

        n = ceil(order)
        # Caputo fractional Derivative
        if kind == "c":
            res = self.diff(n).fractionalIntegral(n - order)
        else:
            res = self.fractionalIntegral(n - order).diff(n)

        if res.polynomial.iszero():
            return res.polynomial
        else:
            return res

    fracDiff = fractionalDerivative

    def integerDerivative(self):
        """
        Integer derivative of a fractional polynomial.

        Returns
        -------
        tau.FPolynomial
            A Tau fractional polynomial which is the derivative of the original
        """
        bas = self.polynomial.basis.copy()
        bas.domain = [-1, 1]

        t = Polynomial(self.polynomial.coeff, basis=bas)
        u = t.copy()
        s = FPolynomial(t.diff(), self.exponents.copy())

        if self.exponents[0]:
            t *= self.exponents[0]
            t.exponents = self.exponents.copy()
            t.exponents[0] -= 1
            s = s.singAdd(t)

        if self.exponents[1]:
            u *= -self.exponents[1]
            u.exponents = self.exponents.copy()
            u.exponents[1] -= 1
            s = s.singAdd(u)
        sex = s.exponents
        rescale_factor = 0.5 * np.diff(self.polynomial.domain)

        s = Polynomial(s.polynomial.coeff / rescale_factor, basis=self.polynomial.basis)
        return FPolynomial(s, sex)

    def singAdd(self, q):
        tolex = 1e-12
        p = self.polynomial.copy()
        pex = self.exponents.copy()

        bas = p.basis.copy()
        bas.domain = [-1, 1]

        if isinstance(q, Number):
            q = Polynomial(q, basis=self.polynomial.basis)
            qex = np.zeros(2)
        else:
            qex = q.exponents

        if p.iszero():
            return FPolynomial(q.copy(), qex)

        if q.iszero():
            return FPolynomial(p, pex)

        if all(abs(pex - qex) < tolex):
            # The functions have the same exponents
            p.coeff = p.basis.add(p.coeff, q.coef)
            return FPolynomial(p.trim(), pex)

        if all(abs(np.round(pex - qex) - (pex - qex)) < tolex):
            # The exponents differ by integers
            fP = Polynomial(1, basis=bas)
            fQ = Polynomial(1, basis=bas)
            nEx = np.zeros(2)

            for i in range(2):
                ind = np.argsort([pex[i], qex[i]])
                e = np.sort([pex[i], qex[i]])
                nEx[i] = e[0]

                # The quotient factor is the difference in the exponents
                if i == 0:
                    nF = Polynomial(lambda x: (1 + x) ** np.diff(e).item(), basis=bas)
                else:
                    nF = Polynomial(lambda x: (1 - x) ** np.diff(e).item(), basis=bas)

                # Who had the algebraically smaller exponent? the other one
                # gets the factor

                if ind[0] == 0:
                    fQ = fQ * nF
                else:
                    fP = fP * nF

            s = Polynomial(p.coeff, basis=bas) * fP + Polynomial(q.coeff, basis=bas) * fQ

            if s.iszero():
                return Polynomial(0, basis=self.polynomial.basis)

            s = Polynomial(s.coeff, basis=self.polynomial.basis)

            return FPolynomial(s, nEx)

        raise ValueError(
            "We cannot add two singular functions when the difference "
            "in the exponents are not integer."
        )

    def fractionalIntegral(self, order):
        r"""
        Compute the fractional integral of order `order`. When `order` is inte
        ger the result is the standard indefinite integral of order `order`.

        Parameters
        ----------
        order : scalar
            The order of the integral.

        Returns
        -------
        Polynomial
            The fractional Integral of order `order`.

        Examples
        --------
        Using ChebyshevT basis in the [-1,1] domain:

        >>> from tautoolbox.functions import fractionalIntegral
        >>> p = polynomial.Polynomial(lambda x: x + 2 * x * 3 * x**2 - x**3)
        >>> fractionalIntegral(p, 2.6).coeff
        array([-0.87894491, -1.01386727, -0.06663148,  0.05632403, -0.00652738,
                0.00543948])
        """
        m = floor(order)  # The integer part of the order
        μ = order - m  # The part fractional of the order

        p = FPolynomial(self.polynomial.copy().cumsum(m), self.exponents.copy())

        if μ == 0:
            return p

        b = self.polynomial.basis.copy()
        if any(p.exponents):
            p = p.simplifyExponents()

            p.polynomial.coeff = b.fractionalIntegral(p.polynomial.coeff, μ, p.exponents[0])
            p.exponents += [μ, 0]

            if p.exponents[0]:
                p = p.simplifyExponents()
        else:
            p.polynomial.coeff = b.fractionalIntegral(p.polynomial.coeff, μ)
            p.exponents += [μ, 0]
        return p.trim(np.spacing(1))

    # Alias for fractionalIntegral
    fracInt = fractionalIntegral

    def simplifyExponents(self):
        result = self.copy()

        bas = result.polynomial.basis.copy()
        bas.domain = [-1, 1]

        exps = result.exponents.copy()
        sm = Polynomial(result.polynomial.coeff, basis=bas)

        tol = 100 * np.spacing(1) * sm.vscale
        exps[abs(exps) < tol] = 0
        result.exponents[:] = exps

        idx = abs(np.round(exps) - exps) < tol
        exps[idx] = np.round(exps[idx])

        ind = exps >= (1 - tol)
        if not any(ind):
            return result

        # Sort out the new exponents and the order of the boundary roots which
        # need to be absorbed into the smooth part
        newExps = exps.copy()
        newExps[ind] = exps[ind] - np.floor(exps[ind])
        pw = exps - newExps

        mult = Polynomial(lambda x: (1 + x) ** pw[0] * (1 - x) ** pw[1], basis=bas)

        p_c = (mult * sm).coeff
        p = Polynomial(p_c, basis=self.polynomial.basis)

        p.exponents = newExps
        return p

    def singInt(self):
        result = Polynomial(self.basis.to_chebyshevT_coeff(self.coeff))
        flip = False
        # When the singularity is at the extreme right of the interval, flip
        # so that the singularity is at the extreme left of the interval
        if self.exponents[1]:
            result = result.flip()
            flip = True

        ex = self.exponents
        xs = result * Polynomial(lambda x: 1 + x)
        a = -ex[0]
        ra = max(round(a), 1)

        # If the size of xs is less than ra+3 we pad xs to size ra+3
        n = xs.n
        oldn = n
        if n < ra + 3:
            n = ra + 3
            xs = xs.extend(n)

        aa = xs.coeff

        # Recurrence relation to solve for the coefficients u', i.e.,c_k.
        c = np.zeros_like(aa[..., :-1])

        c[..., n - 2] = 2 * aa[..., n - 1] / (1 - a / (n - 1))
        c[..., n - 3] = 2 * (aa[..., n - 2] - c[..., n - 2]) / (1 - a / (n - 2))
        for i in range(n - 4, ra - 1, -1):
            c[..., i] = (
                2
                * (aa[..., i + 1] - c[..., i + 1] - c[..., i + 2] * 0.5 * (1 + a / (i + 1)))
                / (1 - a / (i + 1))
            )

        # Compute Cm
        Cm = 2 ** (ra - 1) * (aa[..., ra] - c[..., ra] - c[..., ra + 1] * (1 + a / ra) / 2)

        # Compute the polynomial representation of (x+1)**[a] in [-1,1]
        xa = Polynomial(lambda x: (1 + x) ** ra)

        # Intermediate result for temporary use
        aa[..., : ra + 1] = aa[..., : ra + 1] - Cm * np.flip(xa.coeff, axis=-1)

        # Compute the rest of the coefficients
        for i in range(ra - 2, -1, -1):
            c[..., i] = (
                2
                * (aa[..., i + 1] - c[..., i + 1] - c[..., i + 2] * 0.5 * (1 + a / (i + 1)))
                / (1 - a / (i + 1))
            )

        # Compute the Chebyshev coefficients of u from those of u'
        kk = np.arange(1, n)
        c = 0.5 * c
        dd1 = c / kk
        dd2 = -c[..., 2:] / kk[:-2]

        pad = np.zeros_like(c[..., :1])
        cc = np.r_["-1", pad, dd1 + np.r_["-1", dd2, pad, pad]]

        # Choose first coefficient so that u(-1) =(x+1)*f(-1)=0
        cc[..., 0] = np.sum(cc[..., 1::2], axis=-1) - np.sum(cc[..., 2::2], axis=-1)

        # Remove the padding we put in
        if n > oldn + 2:
            cc = cc[..., : oldn + 1]

        # Drop the leading zeros in the coefficients
        ind = np.where(cc != 0)[-1]

        if ind.size == 0:
            cc = pad
        else:
            cc = cc[..., : max(ind) + 1]

        u = Polynomial(cc)

        tol = np.spacing(1) * result.vscale

        if abs(ra - a) > tol:
            CM = Cm / (ra - a)

            if u.iszero() and abs(CM) > tol * result.vscale:
                p = Polynomial(lambda x: CM)
                p.exponents = p.exponents + [ra - a, 0]
            elif not u.iszero() and abs(CM) < tol:
                p, rootsLeft, rootsRight = u.extractBoundaryRoots(np.array([1, 0]))
                p.exponents = ex + [rootsLeft.item(), rootsRight.item()]
            else:
                # The general case where where both terms are non trivial
                p, rootsLeft, rootsRight = (u + CM * xa).extractBoundaryRoots(np.array([1, 0]))
                p.exponents = ex + [rootsLeft.item(), rootsRight.item()]
        elif abs(Cm) < tol:
            # No log term: fractional poles with non-constant smooth part
            p, rootsLeft, rootsRight = u.extractBoundaryRoots(np.array([1, 0]))
            p.exponents = ex + [rootsLeft.item(), rootsRight.item()]
        else:
            # Log term: Integer poles with constant or non constant smooth part:
            # TODO: Construct a representation of log
            raise ValueError(
                "cumsum does not support the case where the singular"
                "indefinite integral has a logarithmic therm."
            )

        if flip:
            p = -p.flip()

        # Ensure p(-1)=0
        if p.exponents[0] >= 0:
            p.coeff[..., 0] = p.coeff[..., 0] - p(-1)

        # scale to the domain
        rescale_factor = 0.5 * np.diff(self.domain)
        p.coeff = rescale_factor * p.coef
        n = p.coeff.shape[-1]

        p.coeff = self.basis.from_chebyshevT_coeff(p.coeff)

        ex = p.exponents
        p = Polynomial(p.coeff, basis=self.basis)
        p.exponents = ex

        return p

    def cumsum(self, order=1):
        r"""
        Computes the nth order indefinite integral of a Polynomial in such way that
        this integral evaluated at the left extreme of the domain is zero; i.e.
        Q(a)=0 where Q is this integral. This is not to be confused with the
        method integrate where i can specify the constant of integration.

        Parameters
        ----------
        order : optional
            The default is 1.

        Returns
        -------


        """
        if order < 0:
            raise ValueError(f"order must be greater than 0 was given {order}.")

        if int(order) != order:
            return self.fractionalIntegral(order)

        result = self.copy()

        if any(result.exponents):
            for _ in range(order):
                result = result.singInt()
        else:
            for _ in range(order):
                result = result.integrate()
                result = result - result(result.domain[0])

        return result.trim()

    def trim(self, tol=np.spacing(1)):
        result = self.copy()
        result.polynomial = result.polynomial.trim(tol)

        return result

    def plot(self, ax=None, **kwargs):
        """
        Plots a Polynomial
        """
        plt.style.use("ggplot")
        if ax is None:
            ax = plt.gca()
        xx = self.polynomial.linspace()
        yy = self(xx)
        if self.polynomial.size > 1:
            xx = np.repeat(xx.reshape(1, -1), self.polynomial.size, axis=0)
        ax.plot(xx.T, yy.T, **kwargs)
        return ax
