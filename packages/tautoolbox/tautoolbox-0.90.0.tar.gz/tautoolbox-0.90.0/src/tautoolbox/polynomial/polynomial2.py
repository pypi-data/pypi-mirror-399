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

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from numbers import Number
from typing import Optional
from warnings import warn

import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft, ifft
from scipy.optimize import fminbound
from scipy.special import beta

from ..utils import get_shape
from .bases import (
    ChebyshevU,
    T3Basis,
    family_basis,
    standard_chop,
)
from .options import Settings, numericalSettings
from .polynomial1 import Polynomial

np.seterr(divide="ignore")


@dataclass
class Interp2Values:
    p_cols: Polynomial
    pivot_vals: np.ndarray
    p_rows: Polynomial
    piv_pos: Optional[np.ndarray]
    vscale: float


class Polynomial2:
    r"""
    A class used to represent a polynomial in 2D. Implemented using
    Low rank approximation of bivariate functions in the vein of Chebfun.
    Reference: Townsend and L. N. Trefethen, "An extension of Chebfun to two
    dimensions", SIAM Journal on Scientific Computing, 35 (2013), C495-C518.

    Attributes
    ----------
    coef : array_like
        A bidimensional array like representing the coefficients of the poly-
        nomial in the given bases and domain
    bases : list or tuple
        A list with the names of the basis for each independent variable must
        have length 2. The default is ["ChebyshevT"] * 2.
    domain : array_like, optional
        A 2 by 2 array_like object where each row is the domain of an independent
        variable in the order given by bases. The default is [[-1, 1]] * 2.

    Notes
    -----
    This is the form of representing a Polynomial in a Polynomial in two
    dimensions when each variable are represented in one orthogonal basis.
    The basis for each variable can be the same of different. Suppose we
    have two bases of length :math:`m+1` and :math:`n+1` respectively
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]` and
    :math:`\mathcal{Q_n}(y) =[Q_0(y),\ \dots,\ Q_n(y)]\ y\in [c,d]`,
    then a Polynomial can be be written in the those bases as:

    .. math::
        \Xi (x,y) =a_{0,0}P_0(x)Q_0 + a_{0,1}P_1Q_0 + ... + a_{n,m}P_mQ_n.
        \quad (x,y) \in [a,b]\times [c,d]

    Therefore the coefficients are represented by :math:`[a_{i,j}]_{n\times m}`
    """

    __array_priority__ = 1000
    cols = None
    rows = None
    pivots = None
    __vscale = None

    def __new__(
        cls,
        source=None,
        domain=((-1, 1), (-1, 1)),
        *,
        bases=None,
        options=None,
        **kwargs,
    ):
        if isinstance(source, cls):
            return source.copy()  # copy constructor

        if not callable(source):
            return super().__new__(cls)  # proceed to __init__

        bases = Polynomial2.choose_basis(bases, domain, options)
        if kwargs:
            return Polynomial2.interp2d(source, bases=bases, **kwargs)

        # try first the polynomial version
        try:
            x = Polynomial2(Polynomial(basis=bases[0]).coeff.reshape(1, -1), bases=bases)
            y = Polynomial2(Polynomial(basis=bases[1]).coeff.reshape(-1, 1), bases=bases)

            return source(x, y)
        except (ValueError, TypeError):
            # If the above fails use a low rank approximation
            return Polynomial2.interp2d(source, bases=bases)

    def __init__(
        self,
        source=None,
        domain=((-1, 1), (-1, 1)),
        *,
        bases=None,
        options=None,
        **kwargs,
    ):
        r"""


        The constructor. When ``source`` is callable and have no Polynomial
        structure it uses interpolation to construct it

        Parameters
        ----------
        source : array_like, scalar or callable
            Can be the coefficients of a Polynomial,
            a function to be approximated by a Polynomial or
            a scalar representing a constant function.
        domain : array_like, optional
            Each row is the domain of an independent variable in the order
            given by bases. The default is [[-1, 1]] * 2.
        bases : Iterable
            An iterable with two string elements representing the basis
            for each variable. The default is ["ChebyshevT"] * 2.

        Other Parameters
        ----------------
        method : str
            The method to use for interpolation when needed. If not specified
            the default is 'aca'.
        grid_shape : int or iterable
            Used to specify a fixed grid dimension. When `int` means a square
            grid of dimension n*n. When not specified we assumes an adaptive
            grid
        Raises
        ------
        ValueError
            When ``source`` is an array with dimension not equal to 2, when do-
            main is not a 2x2 array_like object, when bases is not a length 2
            iterable of strings.

        TypeError
            When ``source`` is a ragged nested sequence, or when ``source`` is
            not a: scalar, array_like, callable.

        Returns
        -------
        None.

        Notes
        -----
        This is the form of representing a Polynomial in a Polynomial in two
        dimensions when each variable are represented in one orthogonal basis.
        The basis for each variable can be the same of different. Suppose we
        have two bases of length :math:`m` and :math:`n` respectively
        :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]` and
        :math:`\mathcal{Q_n}(y) =[Q_0(y),\ \dots,\ Q_n(y)]\ y\in [c,d]`,
        then a Polynomial can be be written in the those bases as:

        .. math::
            \Xi (x,y) =a_{0,0}P_0(x)Q_0 + a_{0,1}P_1Q_0 + ... + a_{n,m}P_mQ_n.
            \quad (x,y) \in [a,b]\times [c,d]

        Therefore the coefficients are represented by
        :math:`[a_{i,j}]_{n\times m}`

        """
        # If source is a Polynomial2D return a copy of source
        if isinstance(source, self.__class__) or callable(source):
            return

        if isinstance(source, Interp2Values):
            self.cols = source.p_cols
            self.diag = source.pivot_vals
            self.rows = source.p_rows
            self.pivot_locations = source.piv_pos
            self.__vscale = source.vscale
            return

        # default case
        if source is None:
            source = 0

        # When the source is an array like object
        coef_shape = get_shape(source)

        if coef_shape is None:
            raise TypeError(
                "Tautoolbox: source must be a number, a two variable callable,"
                " a Polynomial2 object or a bidimensional array_like object"
                " representing the coefficients"
            )
        if coef_shape == ():
            coef = np.array([[source]])
        elif len(coef_shape) == 1:
            coef = np.array(source)[np.newaxis]
        elif len(coef_shape) == 2:
            coef = np.array(source)
        elif len(coef_shape) > 2 or not isinstance(source, np.ndarray):
            raise ValueError("Tautoolbox: wrong source format")

        bases = Polynomial2.choose_basis(bases, domain, options)
        self.cols, self.diag, self.rows = self.set_coef(coef, bases)

    @property
    def domain(self):
        return np.array([self.rows.domain, self.cols.domain])

    @property
    def bases(self):
        return [self.rows.basis, self.cols.basis]

    @property
    def basis_x(self):
        return self.rows.basis

    @property
    def basis_y(self):
        return self.cols.basis

    @property
    def coef(self):
        result = (self.cols.coeff.T * self.diag) @ self.rows.coeff
        result[np.abs(result) < 1e-15] = 0
        return result

    def set_coef(self, coef, bases=None):
        if bases is None:
            bases = self.bases
        u, s, vh = np.linalg.svd(coef)

        rk = np.sum(s > 1e-15)
        if rk == 0:
            rk += 1

        cols = Polynomial(u[:, :rk].T, basis=bases[1])
        rows = Polynomial(vh[:rk, :], basis=bases[0])
        diag = s[:rk]
        return cols.trim(1e-15), diag, rows.trim(1e-15)

    @staticmethod
    def choose_basis(bases, domain, options):
        """Return the Polynomail2 bases from the constructor arguments"""
        if isinstance(bases, T3Basis):
            bases = (bases, bases)

        if bases is None:
            # Processing  x and y options
            if isinstance(options, Iterable) and not isinstance(options, dict):
                optx = options[0]
                opty = options[1]
            else:
                optx = options
                opty = options

            optx = Settings.read(optx)
            opty = Settings.read(opty)
            domain = np.array(domain)
            if domain.ndim == 1:
                domain = np.vstack([domain, domain])
            basis_x = family_basis(optx.basis, domain=domain[0])
            basis_y = family_basis(opty.basis, domain=domain[1])
            bases = (basis_x, basis_y)
        return bases

    def __call__(self, x, y):
        r"""
        Evaluate the Polynomial in the abscissas ``x`` and ordinates ``y``

        Parameters
        ----------
        x : Number or array_Like
            The the value of the first variable. Can be a Number or an
            array_like structure of numbers.
        y : Number or array_Like
            The the value of the first variable. Can be a Number or an
            array_like structure of numbers

        Returns
        -------
        Number or array_like
            The value or values of the Polynomials in the point or points x, y

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial2
        >>> a = np.arange(9).reshape(3, 3)
        >>> v = Polynomial2(a)
        >>> v(a, a)
        array([[0.00000e+00, 3.60000e+01, 6.40000e+02],
               [3.10800e+03, 9.50400e+03, 2.26600e+04],
               [4.61760e+04, 8.44200e+04, 1.42528e+05]])

        >>> x = np.linspace(-1, 1, 5)
        >>> v(x, x)
        array([ 4.00000000e+00, -1.55431223e-15, -2.22044605e-15, -2.00000000e+00,
        3.60000000e+01])

        >>> v(0, 2)
        array([-20.])
        """

        if isinstance(x, Iterable) and not isinstance(x, np.ndarray):
            try:
                x = np.stack(x)
                if not np.issubdtype(x.dtype, np.number):
                    raise ValueError(
                        "When the first argument is an iterable all "
                        " sub-datatype  must be numbers"
                    )

            except ValueError:
                raise ValueError(
                    "When the first argument is an iterable, "
                    "the iterable must be an array_like structure"
                )
        if isinstance(y, Iterable) and not isinstance(y, np.ndarray):
            try:
                y = np.stack(y)
                if not np.issubdtype(y.dtype, np.number):
                    raise ValueError(
                        "When the second argument is an iterable all "
                        " sub-datatype  must be numbers"
                    )
            except ValueError:
                raise ValueError(
                    "When the first argument is an iterable, "
                    "the iterable must be an array_like structure"
                )
        m = n = None
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray) and x.size != y.size:
            m, n = x.size, y.size
            x = np.repeat(x, y.size)
            y = np.tile(y, (x.size, 1)).flatten()

        if isinstance(x, (int, float)):
            x = np.array(x)
        if isinstance(y, (int, float)):
            y = np.array(y)

        if x is None and y is None:
            raise ValueError("Both arguments cannot be None at the same time ")

        if not (x is None or isinstance(x, np.ndarray)) or not (
            y is None or isinstance(y, np.ndarray)
        ):
            raise TypeError("The possible arguments are None, numbers or array_like objects")

        if y is None:
            x = x.flatten()
            result = ((self.cols.coeff.T * self.diag) @ self.rows(x)).T
            if result.shape[0] == 1:
                result = result.flatten()

            return Polynomial(result, basis=self.basis_y)

        if x is None:
            y = y.flatten()
            result = (self.cols(y).T * self.diag) @ self.rows.coeff
            if result.shape[0] == 1:
                result = result.flatten()
            return Polynomial(result, basis=self.basis_x)

        if x.ndim == 2:
            # in this case x and y are a mesh grid
            if (x == x[0]).all() and (y.T == y.T[0]).all():
                return self.evalm(x[0], y[:, 0])

            return np.einsum("i,ijk->jk", self.diag, (self.cols(y) * self.rows(x)))
        else:
            result = self.cols(y) * self.rows(x)
            if np.isscalar(result):
                result = self.diag.item() * result
            else:
                result = self.diag @ result
            if m is not None:
                return result.reshape(m, n).T
            return result

    def copy(self):
        return deepcopy(self)

    @property
    def T(self):
        result = self.copy()
        result.cols = self.rows.copy()
        result.rows = self.cols.copy()
        return result

    def __repr__(self):
        dom = self.domain.round(2).tolist()
        vscale = self.vscale

        cv = self(*np.meshgrid(self.domain[0], self.domain[1])).round(2).flatten().tolist()

        st = (
            "Polynomial2 object:\n"
            f"  bases          :  {self.bases}\n"
            f"  domain         :  {dom[0]} x {dom[1]}\n"
        )

        st += (
            f"  rank           :  {len(self)}\n"
            f"  shape          :  {self.cols.n} x {self.rows.n}\n"
            f"  corner values  :  {cv}\n"
            f"  vertical scale :  {vscale:.2f}"
        )

        return st

    @staticmethod
    def sum_coef(c1, c2):
        result1 = c1.copy()
        result2 = c2.copy()
        result1_shape, result2_shape = result1.shape, result2.shape
        coef = np.zeros(np.maximum(result1_shape, result2_shape))
        coef[: result1_shape[0], : result1_shape[1]] = result1
        coef[: result2_shape[0], : result2_shape[1]] += result2
        return coef

    def __add__(self, rhs):
        result = self.copy()
        result.__vscale = None
        # For the case the sum is a Polynomial and a scalar
        if isinstance(rhs, Number):
            coef = result.coef
            coef[0, 0] += rhs
            result.cols, result.diag, result.rows = result.set_coef(coef)
        # The case of two Polynomial2
        elif isinstance(rhs, Polynomial2):
            # Check if the Polynomials2 has the same family bases and domain
            if result.bases != rhs.bases:
                raise ValueError("The Polynomials2 must have the same options")
            coef = Polynomial2.sum_coef(result.coef, rhs.coef)

            result.cols, result.diag, result.rows = result.set_coef(coef)
        else:
            return rhs + self
        return result

    def __radd__(self, lhs):
        return self + lhs

    def __pos__(self):
        return self.copy()

    def __neg__(self):
        result = self.copy()
        result.cols = -result.cols
        return result

    def __sub__(self, rhs):
        return -(rhs + (-self))

    def __rsub__(self, lhs):
        return -self + lhs

    def __mul__(self, rhs):
        r"""
        Parameters
        ----------
        rhs : Number, Polynomial,Operator2 or Polynomial2.
            The right hand side of the operator.

        Raises
        ------
        ValueError
            When rhs is a Polynomial2 and its options are not equal to
            self options or when rhs is a Polynomial and its options is not
            equal to the options of self in the x direction.
        TypeError
            When the rhs is None of the above types

        Returns
        -------
        Polynomial2 or Operator2
            DESCRIPTION.

        """
        # For the case the sum is a Polynomial and a scalar
        if isinstance(rhs, Number):
            if rhs == 0:
                return Polynomial2(0, bases=(self.basis_x, self.basis_y))
            result = self.copy()
            result.diag = result.diag * rhs

        # The case of two Polynomial2
        elif isinstance(rhs, Polynomial2):
            # Check if the Polynomials2d  has the same bases and domain
            if self.bases != rhs.bases:
                raise ValueError(
                    "The corresponding variable in each polynomial must have the same options."
                )
            if self.iszero():
                return self.copy()
            elif rhs.iszero():
                return rhs.copy()

            if len(self) <= len(rhs):
                bx, by = self.bases

                cols, diag, rows = self.cols, self.diag, self.rows
                result = rhs.copy()
                col_el = np.sqrt(np.abs(diag[0]))
                row_el = np.sign(diag[0]) * col_el
                co = by.productv2(cols.coeff[0, :] * col_el, rhs.cols.coeff)
                ro = bx.productv2(rows.coeff[0, :] * row_el, rhs.rows.coeff)
                coef = (co.T * rhs.diag) @ ro

                for i in range(1, len(diag)):
                    col_el = np.sqrt(np.abs(diag[i]))
                    row_el = np.sign(diag[i]) * col_el

                    co = by.productv2(cols.coeff[i, :] * col_el, rhs.cols.coeff)
                    ro = bx.productv2(rows.coeff[i, :] * row_el, rhs.rows.coeff)

                    coef = coef + (co.T * rhs.diag) @ ro

                result.cols, result.diag, result.rows = result.set_coef(coef)

            else:
                return rhs * self
        elif isinstance(rhs, Polynomial):
            if self.bases[0] != rhs.basis:
                raise ValueError(
                    "Polynomial2 options in the x direction must be "
                    "the same of the Polynomial options"
                )

            result = self.copy()
            result.rows = result.rows * rhs
            return result

        else:
            return rhs * self
        return result

    def __rmul__(self, lhs):
        r"""
        When self is in the right hand side of the operator

        Parameters
        ----------
        lhs : Number, Polynomial,Operator2 or Polynomial2
            The left hand side of the operator

        Returns
        -------
        TYPE
            Polynomial2 or Operator2

        """

        return self * lhs

    def __pow__(self, n):
        r"""
        Compute the power of ``self``with exponent ``n``.
        Parameters
        ----------
        n : Integer
            an integer exponent of ``self``

        Raises
        ------
        ValueError
            When ``n`` is not an integer.

        Returns
        -------
        Polynomial2
            A polynomial2 which is self**n

        """
        if n < 0 or n != int(n):
            raise ValueError(
                f"Polynomial2: n must be a non-negative integer but {n=} was given"
            )

        if n == 0:
            return Polynomial2([[1]], bases=(self.basis_x, self.basis_y))

        base = self.copy()
        if n == 1 or self.iszero():
            return base

        result = None
        exponent = int(n)
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
    def eval_from_coef(coef, x, y, options=None):
        r"""
        A method the receives the coefficients ``coef`` of a 2-dimensional
        Polynomial in the bases ``bases`` and evaluate it on the abscissas
        ``x`` and ordinates ``y``. The bases can be any of the bases implemen-
        ted in tau.basis and can be two different bases



        Parameters
        ----------
        coef : scalar or array_like
            The coefficients of the Polynomial to evaluate.
        x : scalar or array_like
            The abscissas to evaluate, when an array it can be at most bidimensional.
        y : scalar or array_like
            The ordinates  to evaluate, when an array it can be at most bidimensional.
        options : settings, dict,list or tuple
            The options for the first and second independent variables.The
            default is None

        Raises
        ------
        TypeError
            When `coef` is a ragged nested sequence.
            When `x` is a ragged nested sequence.
        ValueError
            When `coef` has more than 2 dimensions.
            When `x` has more than two dimensions.

        Returns
        -------
        scalar or array_like
            The result of the evaluations

        Notes
        -----
        We have two bases :math:`\mathcal{P}=[P_0(x),\ P_1(x),\ \dots]` and
        :math:`\mathcal{Q}=[Q_0(y),\ Q_1(y),\ \dots]`. Those  bases can be used
        to write Polynomial in 2D as :

        .. math:: \Xi (x,y)=[a_{i,j}]_{n,m}\cdot (\mathcal{P}_m \otimes \mathcal{Q}_n^T),

        where :math:`\cdot` represents the  Hadamard product and :math:`\otimes`
        means the Kronecker product. Here the bases are truncated in the
        dimension m and n respectively.
        """

        if options is None or isinstance(options, (dict, Settings)):
            options = [options] * 2

        # Check if coef are well posed
        coef_shape = get_shape(coef)
        if coef_shape is None:
            raise TypeError("Coef must be an bidimensional array_like structure or a scalar")
        elif len(coef_shape) == 0:
            m = n = 1
        elif len(coef_shape) == 2:
            m, n = coef_shape
        else:
            raise ValueError("Coef must be an bidimensional array_like structure or a scalar")
        bas = [family_basis(opt.basis, domain=opt.domain) for opt in options]

        x_sha = get_shape(x)
        if x_sha is None:
            raise TypeError("x must be a scalar or a vector")

        if len(x_sha) == 0:
            xval = bas[0].vander(x, n=n)
            yval = np.reshape(bas[1].vander(y, n=m), (-1, 1))

            return np.sum(coef * yval * xval)
        elif len(x_sha) == 1:
            xval = bas[0].vander(x, n=n)
            yval = bas[1].vander(y, n=m)

            return np.einsum("ij,kij->k", coef, np.einsum("ij,ik->ikj", xval, yval))
        elif len(x_sha) == 2:
            xval = bas[0].vander(x, n=n)
            yval = bas[1].vander(y, n=m)
            # Here we use Einstein tensor summation notation because is faster
            return np.einsum("ij,klij->kl", coef, np.einsum("ijk,ijl->ijlk", xval, yval))

        else:
            ValueError("Not yet implemented when x has dimension 3 or more")

    def trim(self, tol=0):
        """
        Trim the Polynomial in the position i,j from which the absolute value
        are less than or equal to tol.

        Parameters
        ----------
        tol : Number, optional
            The tol to compare the coefficients of the Polynomial2.

        Returns
        -------
        result : Polynomial2
            A copy of the Polynomial2 trimmed.

        Examples
        --------
        Example where some coefficients are non zero

        >>> from tautoolbox.polynomial import Polynomial2
        >>> a = np.zeros((5, 5))
        >>> a[(1, 2, 1), (1, 3, 3)] = [1, 2, 4]
        >>> a
        array([[0., 0., 0., 0., 0.],
               [0., 1., 0., 4., 0.],
               [0., 0., 0., 2., 0.],
               [0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.]])

        >>> p = Polynomial2(a)
        >>> p2 = p.trim()
        >>> p2.coef
        array([[0., 0., 0., 0.],
               [0., 1., 0., 4.],
               [0., 0., 0., 2.]])

        Example where the coefficients are all zeros

        >>> a = np.zeros((5, 5))
        >>> a
        array([[0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.]])

        >>> p = Polynomial2(a)
        >>> p2 = p.trim()
        >>> p2.coef
        array([[0]])

        """
        # Check the positions where the abs of the value is greater than tol
        gt_abs_tol_pos = np.argwhere(np.abs(self.coef) > tol)
        if len(gt_abs_tol_pos) == 0:
            coef = np.array([[0]])
        else:
            # trim the coef array in the max of the columns and max of the rows
            # the positions positions have values greater than tol
            coef = self.coef[
                : np.max(gt_abs_tol_pos[:, 0]) + 1,
                : np.max(gt_abs_tol_pos[:, 1]) + 1,
            ]
        return Polynomial2(coef, bases=self.bases)

    @property
    def power_coef(self):
        """
        Returns  an array with the coefficients of this Polynomial converted to
        power basis in all variables

        Returns
        -------
        ndarray
            An array which are the coefficients of the Polynomial with each
            variables in power basis, that means the PowerX basis.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial2
        >>> a = np.arange(12).reshape(3, 4)
        >>> a
        array([[ 0,  1,  2,  3],
               [ 4,  5,  6,  7],
               [ 8,  9, 10, 11]])

        >>> Polynomial2(a).power_coef
        array([[  0.,  16., -16., -32.],
               [ -2., -16.,  12.,  28.],
               [ -4., -48.,  40.,  88.]])

        """
        m, n = self.shape

        res = (
            self.cols.basis.orth2powmatrix(m) @ self.coef @ self.rows.basis.orth2powmatrix(n).T
        )
        res[np.abs(res) < 1e-15] = 0
        return res

    # this is an alias
    coeff = coef

    @staticmethod
    def from_power_coef(coef, options=None):
        r"""
        Returns a Polynomial2 where the  new coefficients are converted from
        the given coefficients in power bases to a Polynomial2 with the options
        given by ``options``


        Parameters
        ----------
        coef : array_like
            A bidimensional array with the coefficients of the polynomials in
            the basis where the polynomial have the form c_{0,0}P_0Q_0 +
            c_{1,0}P_1Q_0 + ... + c_{m,n}P_mQ_n. Therefore coef=[c_{i,j}]_{m,n}
        options: settings, dict, tuple or list
            The options in the first and second variable to construct the Polynomial2

        Returns
        -------
        Polynomial2
            A Polynomial2 in the given basis and domain where the coefficients
            are converted from power basis to the given basis.

        See Also
        --------
        power_coef

        Examples
        --------

        Converting from power coefficients to Chebyshev in all variables in the
        standard domain:

        >>> from tautoolbox.polynomial import Polynomial2
        >>> a = [[0, 16, -16, -32], [-2, -16, 12, 28], [-4, -48, 40, 88]]
        >>> p = Polynomial2.from_power_coef(a)
        >>> p.coef
        array([[ 0.,  1.,  2.,  3.],
               [ 4.,  5.,  6.,  7.],
               [ 8.,  9., 10., 11.]])


        """
        if options is None or isinstance(options, (dict, Settings)):
            options = [options] * 2

        # Parse coef
        # When coef is array like
        if not (
            isinstance(coef, Iterable)
            and all([isinstance(co, Iterable) for co in coef])
            and all([len(co) == len(coef[0]) for co in coef])
            and all([all([isinstance(c, Number) for c in co]) for co in coef])
        ):
            raise ValueError("Polynomial2: coef must be a m x n array_like object")

        power_coef = coef if isinstance(coef, np.ndarray) else np.array(coef)

        bases_ = [Polynomial(opt).basis for opt in options]
        m, n = power_coef.shape
        new_coef = bases_[0].pow2orthmatrix(m) @ power_coef @ bases_[1].pow2orthmatrix(n).T

        return Polynomial2(new_coef, options=options)

    def diff(self, order=1):
        """
        Returns the derivative of the Polynomial2 object where order is a
        tuple or list with two elements indicating the order of the derivative
        in each variable.

        Parameters
        ----------
        order : tuple or list
            A tuple or list of numbers indicating the order of the derivatives
            in each variable

        Returns
        -------
        Polynomial2
            The Polynomial2 which is the partial derivative with the order
            given by the order parameter.

        Examples
        --------
        >>> from tautoolbox.polynomial import Polynomial2
        >>> a = np.arange(15).reshape(3, 5)
        >>> a
        array([[ 0,  1,  2,  3,  4],
               [ 5,  6,  7,  8,  9],
               [10, 11, 12, 13, 14]])

        >>> p = Polynomial2(a)

        It is easier to see the correctness of the result in the power series
        bases

        >>> p.power_coef
        array([[ -10.,   20.,   60.,  -40.,  -80.],
               [   7.,  -18.,  -58.,   32.,   72.],
               [  24.,  -56., -176.,  104.,  224.]])
        >>>
        >>> # To compute the d^3/(dx^2 dy)
        >>> p_deriv = p.diff((2, 1))
        >>> p_deriv.power_coef
        array([[-116.,  192.,  864.,    0.,    0.],
               [-704., 1248., 5376.,    0.,    0.],
               [   0.,    0.,    0.,    0.,    0.]])



        """
        # Check if order is a number
        if isinstance(order, int):
            order = (order, 0)

        if isinstance(order, Iterable):
            if len(order) == 2 and all(
                [np.isscalar(o) and o >= 0 and int(o) == o for o in order]
            ):
                x_order, y_order = order

            else:
                raise ValueError(
                    "When the order is an iterable it must have "
                    "length 2 and all entries integers"
                )
        else:
            raise TypeError("Order can be only an integer or a length 2 iterable of integers")

        result = self.copy()

        if y_order >= self.cols.n or x_order >= self.rows.n:
            return Polynomial2(
                np.zeros((self.cols.n, self.rows.n)),
                bases=(self.rows.basis, self.cols.basis),
            )

        result.cols = result.cols.diff(y_order)
        result.rows = result.rows.diff(x_order)

        return result

    @staticmethod
    def _power_mul(lhs, rhs):
        r"""
        This method multiply two arrays of coefficients when the two variables
        are in power series.

        Parameters
        ----------
        lhs : array_like
            A bidimensional array of coefficients representing a Polynomial in
            two variables in power basis

        rhs : array_like
            A bidimensional array of coefficients representing a Polynomial in
            two variables in power  basis

        Returns
        -------
        result : array_like
            A bidimensional array_like which coefficients are the result of the
            product of  two polynomials in two variables which each variable are
            in power basis

        """
        lhs_shape = lhs.shape
        rhs_shape = rhs.shape

        result = np.zeros(
            (
                np.prod(lhs_shape),
                *[sum(i) - 1 for i in zip(lhs_shape, rhs_shape)],
            )
        )
        for i, j in zip(*np.nonzero(lhs)):
            result[
                i * lhs.shape[1] + j,
                i : i + rhs_shape[0],
                j : j + rhs_shape[1],
            ] = lhs[i, j] * rhs

        result = np.sum(result, axis=0)

        return result

    def plot(self, *args, x_lim=None, y_lim=None, n=None, ax=None, **kwargs):
        r"""
        Plot the polynomial inside the limits given by x_lim and y_lim.
        The density of

        Parameters
        ----------
        x_lim : array_like, optional
            The endpoints of values in the x-axis. The default is None.
        y_lim : array_like, optional
            The endpoints values in y-direction. The default is None.
        n : int , optional
            The number of points in each direction to construct the mesh grid.
            The default is None.
        ax : AxesSubplot
            to put the figure in a particular axes. The default is None.
        *args : TYPE
            These are the args of matplotlib plot_surface
        **kwargs : TYPE
            Those are the kwargs of matplotlib plot_surface
         : TYPE
            DESCRIPTION.

        Returns
        -------
        ax : AxesSubplot
            The axessubplot where these plot are drawn

        Examples
        --------
        Using the function f(x,y)=x**2+y**2 with the default basis and domain:

        >>> p = polynomial.Polynomial2(lambda x, y: x**2 + y**2)
        >>> p.contour()  # doctest: +SKIP
        """
        kwargs.setdefault("cmap", "winter_r")
        kwargs.setdefault("cstride", 1)
        kwargs.setdefault("rstride", 1)
        kwargs.setdefault("antialiased", False)

        if ax is None:
            ax = plt.axes(projection="3d")

        if x_lim is None:
            x_lim = self.domain[0]
        if y_lim is None:
            y_lim = self.domain[1]
        if n is None:
            n = 100
        plt.style.use("ggplot")
        ax.set_facecolor("w")
        x = np.linspace(*x_lim, n)
        y = np.linspace(*y_lim, n)
        X, Y = np.meshgrid(x, y)
        ax.plot_surface(X, Y, self.evalm(x, y), *args, **kwargs)
        return ax

    def contour(
        self,
        plot_points=200,
        pivots=False,
        ax=None,
        **kwargs,
    ):
        r"""
        Draw the contour plot of a Polynomial2

        Parameters
        ----------
        plot_points : Integer, optional
            The Number of points to create the mesh grid. so the grid will have
            dimension ``plot_points``x``plot_points``. The default is 200.
        pivots : Boolean, optional
            Plot the pivot values. This only make sense when the Polynomial2 are
            generated using ACA. The default is False.
        ax : AxesSubplot, optional
            If the plot must be drawn in a specific axes. The default is None.
        **kwargs : TYPE
            These are the others parameters that the function contourf from
            ``matplotlib`` can accept.

        Returns
        -------
        ax : AxesSubplot
            Return the plot as an AxesSubplot object

        Examples
        --------
        Using the function f(x,y)=x**2+y**2 with the default basis and domain:

        >>> p = polynomial.Polynomial2(lambda x, y: x**2 + y**2)
        >>> p.contour()  # doctest: +SKIP

        Using the function f(x,y)=cos(x**2+y**2) with the default LegendreP
        basis in all variables and the default domain:

        >>> bases = (polynomial.LegendreP(),) * 2
        >>> p = polynomial.Polynomial2(lambda x, y: np.cos(x**2 + y**2), bases=bases)
        >>> p.contour(pivots=True)  # doctest: +SKIP

        """
        if ax is None:
            ax = plt.gca()
        x = np.linspace(*self.domain[0], plot_points)
        y = np.linspace(*self.domain[1], plot_points)
        xx, yy = np.meshgrid(x, y)
        zz = self.evalm(x, y)
        plt.style.use("ggplot")

        # Default colormap
        kwargs.setdefault("cmap", "ocean")

        ax.contourf(xx, yy, zz, **kwargs)
        if pivots:
            ax.plot(
                self.pivot_locations[:, 0],
                self.pivot_locations[:, 1],
                ".",
                color="red",
            )

        return ax

    @staticmethod
    def nodes2d(m, n, basis_x, basis_y):
        nodes_x, *_ = basis_x.nodes(n)
        nodes_y, *_ = basis_y.nodes(m)

        return np.meshgrid(nodes_x, nodes_y)

    @staticmethod
    def interp2d(
        f,
        bases,
        method=None,
        grid_shape=None,
    ):
        r"""
        Interpolate the bivariate function ``f`` with ``bases``.

        Parameters
        ----------
        f : callable
            A callable which we want to interpolate
        bases : tuple
            A tuple with the two bases for each variable
        method : str, optional
            The method used to Interpolate. When not given we use ACA. The de
            fault is None.
        grid_shape : tuple or list, optional
            The dimension of the grid. This is only specified if we want a
            fixed grid. When not given we assume an adaptive grid. The default
            is None.

        Raises
        ------
        ValueError
            When the method is not  ACA we need to specify a grid_shape because
            for methods other than ACA until now we only works with fixed grid.

        Returns
        -------
        Polynomial2 or the components of a Polynomial2
            The result of the interpolation.
        """
        method = "aca" if method is None else method.lower()

        if grid_shape is None and method != "aca":
            raise ValueError("When the method is not 'aca' you need to specify a grid_shape")

        if method == "aca":
            if grid_shape is None:
                return Polynomial2.interp2d_aca_adaptive_grid(f, bases)

            else:
                (
                    col_vals,
                    pivot_vals,
                    row_vals,
                    piv_pos,
                    vscale,
                    rtol,
                ) = Polynomial2.interp2d_aca_fixed_grid(f, bases, grid_shape=grid_shape)
        elif method == "svd":
            (
                col_vals,
                pivot_vals,
                row_vals,
                vscale,
                rtol,
            ) = Polynomial2.interp2d_svd(f, bases, grid_shape=grid_shape)
            piv_pos = None
        else:
            raise ValueError("Methods implemented yet are 'aca' and 'svd'.")

        # Transform the n columns in n one dimensional Polynomials
        # To be consistent with x in vertical and y in horizontal i transpose
        # i interchange the variable  x with y

        if (pivot_vals != 0).any():
            p_rows = bases[0].interp_from_values(row_vals)

            # pivot_vals = pivot_vals[: min(p_cols.shape)]

            # Transform the n rows in n one dimensional Polynomials
            p_cols = bases[1].interp_from_values(col_vals.T)
        else:
            p_cols, p_rows = np.array([[0]]), np.array([[0]])

        p_cols = Polynomial(p_cols, basis=bases[1])
        p_rows = Polynomial(p_rows, basis=bases[0])

        # When using adaptive grid trim  the coefficients at rtol
        if grid_shape is None:
            p_cols = p_cols.trim(rtol)
            p_rows = p_rows.trim(rtol)

        result = Interp2Values(p_cols, pivot_vals, p_rows, piv_pos, vscale)
        return Polynomial2(result, bases=bases)

    @staticmethod
    def interp2d_aca_fixed_grid(f, bases, grid_shape=(16, 16)):
        level = np.spacing(1)  # The same as np.finfo(float).eps

        domain = np.array([bases[0].domain, bases[1].domain])

        # Construct a ChebyshevU Grid
        xx, yy = Polynomial2.nodes2d(
            *grid_shape, ChebyshevU(domain=bases[0].domain), ChebyshevU(domain=bases[1].domain)
        )

        values = f(xx, yy)
        # For the case the function passed is a constant
        if isinstance(values, Number):
            values = values * np.ones(xx.shape)

        # The maximum of the abs of the elements of vales

        # Scale of V
        vmax = np.max(np.abs(values))
        # Raise an exception if the max is
        if vmax == np.inf:
            raise Exception("The function encountered infinite when evaluating")
        if np.any(np.isnan(values)):
            raise Exception("The function encountered not a number when evaluating")

        rtol, atol = get_tol(xx, yy, values, domain, level)

        (
            pivot_vals,
            pivot_pos,
            row_vals,
            col_vals,
            fail,
        ) = adaptive_cross_approx(values, atol, np.float64(0))
        piv_pos = np.stack([xx[0, pivot_pos[:, 1]], yy[pivot_pos[:, 0], 0]], axis=1)
        return col_vals, 1 / pivot_vals, row_vals, piv_pos, vmax, rtol

    @staticmethod
    def interp2d_aca_adaptive_grid(f, bases):
        r"""


        Parameters
        ----------
        f : callable
            A callable in two independent variables which we want to interpolate
            in two variables
        bases : tuple
            tuple with the bases for the two variables
        Raises
        ------
        ValueError
            DESCRIPTION.
        Exception
            DESCRIPTION.

        Returns
        -------
        Polynomial2
            A Polynomial2 result of the interpolation

        """
        domain = np.array([bases[0].domain, bases[1].domain])
        min_samples = np.array([2, 2]) ** 4 + 1  # The max matrix to operate a 128 x 128 matrix
        max_samples = np.array([2, 2]) ** 16 + 1
        max_rank = np.array([513, 513])
        # where to start
        level = numericalSettings.interpRelTol
        factor = 4
        enough = 0
        failure = 0
        rtol = None
        atol = None
        vscale = None
        p = Polynomial2()
        while not enough and not failure:
            grid = min_samples
            # The grid points and their values to interpolate
            basis_Ux = ChebyshevU(domain=bases[0].domain)
            basis_Uy = ChebyshevU(domain=bases[1].domain)
            xx, yy = Polynomial2.nodes2d(*grid, basis_Ux, basis_Uy)

            values = f(xx, yy)
            # For the case the function passed is a constant
            if isinstance(values, Number):
                values = values * np.ones(xx.shape)
            if np.isnan(values).any() or np.isinf(values).any():
                raise ValueError("Encountered NaN or inf when evaluating the function.")

            # The maximum of the abs of the elements of vales
            # Check if all values is 0
            if (values == 0).all():
                return np.array([[0]]), np.array([0]), np.array([[0]]), 0

            # Scale of V
            vmax = np.max(abs(values))
            vscale = vmax
            # Raise an exception if the max is
            if vmax == np.inf:
                raise Exception("The function encountered infinite when evaluating")
            if np.any(np.isnan(values)):
                raise Exception("The function encountered not a number when evaluating")

            rtol, atol = get_tol(xx, yy, values, domain, level)

            ##### Step one #####

            (
                pivot_vals,
                pivot_pos,
                row_vals,
                col_vals,
                fail,
            ) = adaptive_cross_approx(values, atol, factor)
            strike = 1

            while fail and np.all(grid <= factor * (max_rank - 1) + 1) and strike < 3:
                # Refine the grid  and do a resampling and repeat the above process
                grid[:] = [refine_grid(el)[0] for el in grid]
                xx, yy = Polynomial2.nodes2d(*grid, basis_Ux, basis_Uy)
                values = f(xx, yy)
                vmax = np.max(abs(values))
                vscale = vmax
                rtol, atol = get_tol(xx, yy, values, domain, level)

                (
                    pivot_vals,
                    pivot_pos,
                    row_vals,
                    col_vals,
                    fail,
                ) = adaptive_cross_approx(values, atol, factor)
                # Stop if the function is 0 + noise
                if np.abs(pivot_vals[0]) < 1e4 * vmax * rtol:
                    strike += 1
            # The function algorithm stop if the rank of the function is
            # greater than max_rank

            if (grid > factor * (max_rank - 1) + 1).any():
                warn("Polynomial2: The functions is not a low-rank function")
                failure = 1

            col_hscale = np.linalg.norm(domain[1], np.inf)
            row_hscale = np.linalg.norm(domain[0], np.inf)

            resolved_cols, *_ = readiness_check(
                np.sum(col_vals, axis=1),
                vscale=vmax,
                hscale=col_hscale,
                tol=numericalSettings.interpRelTol,
                basis=basis_Ux,
            )

            resolved_rows, *_ = readiness_check(
                np.sum(row_vals, axis=0),
                vscale=vmax,
                hscale=row_hscale,
                tol=numericalSettings.interpRelTol,
                basis=basis_Uy,
            )

            enough = resolved_cols and resolved_rows

            piv_pos = np.stack((xx[0, pivot_pos[:, 1]], yy[pivot_pos[:, 0], 0]), axis=1)
            pp = pivot_pos

            ###### Phase 2 ########

            m, n = grid

            while not enough and not failure:
                if not resolved_cols:
                    # Double the sampling along columns
                    n, nest = refine_grid(n)
                    # Find the location of pivots on new grid
                    pp[:, 0] = nest[pp[:, 0]]

                xx, yy = np.meshgrid(piv_pos[:, 0], nodes(n, domain[1]))
                col_vals = f(xx, yy)

                if not resolved_rows:
                    m, nest = refine_grid(m)
                    # Find the location of pivots in the new grid
                    pp[:, 1] = nest[pp[:, 1]]

                xx, yy = np.meshgrid(nodes(m, domain[0]), piv_pos[:, 1])
                row_vals = f(xx, yy)

                # Do Gaussian Elimination on the skeleton to update slices
                nn = pivot_vals.size

                for i in range(nn - 1):
                    col_vals[:, i + 1 :] -= (
                        col_vals[:, [i]]
                        @ row_vals[i : i + 1, pp[i + 1 : nn, 1]]
                        / pivot_vals[i]
                    )
                    row_vals[i + 1 :, :] -= (
                        col_vals[pp[i + 1 : nn, [0]], i] @ row_vals[[i], :] / pivot_vals[i]
                    )
                if not resolved_cols:
                    resolved_cols, *_ = readiness_check(
                        np.sum(col_vals, axis=1), vscale=vmax, hscale=col_hscale, basis=basis_Uy
                    )
                if not resolved_rows:
                    resolved_rows, *_ = readiness_check(
                        np.sum(row_vals, axis=0), vscale=vmax, hscale=row_hscale, basis=basis_Ux
                    )
                enough = resolved_rows and resolved_cols

                if not (np.array((m, n)) < np.array(max_samples)).all():
                    warn(
                        f"Polynomial2: Unresolved with respect to maximum length: {max_samples}"
                    )
                    failure = 1

            p_rows = bases[0].interp_from_values(row_vals)
            p_cols = bases[1].interp_from_values(col_vals.T)

            # Create an empty Polynomial2
            p = Polynomial2(bases=bases)

            # The columns of the Polynomial2
            p.cols = Polynomial(p_cols, basis=bases[1])

            # The rows of the Polynomial2
            p.rows = Polynomial(p_rows, basis=bases[0])

            # The diagonal
            p.diag = 1 / pivot_vals

            # The locations of the pivots
            p.pivot_locations = piv_pos

            # Construct a grid to compare with the original function
            # to see if we have a sufficiently small error

            enough = p.sampletest(f, atol)
            # If the error is not  sufficiently small duplicate the grid
            # dimensions
            if not enough:
                min_samples = (
                    refine_grid(min_samples[0])[0],
                    refine_grid(min_samples[1])[0],
                )
        min_tol = numericalSettings.interpRelTol

        p.cols = p.cols.trim(min_tol)
        p.rows = p.rows.trim(min_tol)
        p.__vscale = vscale
        return p

    @staticmethod
    def interp2d_svd(f, bases, grid_shape=(60, 60)):
        r"""


        Parameters
        ----------
        f : callable
            A callable in two independent variables which we want to interpolate
            in two variables
        bases : tuple
            A tuple with the two bases for each variable
        grid_shape : integer,tuple or list, optional
            The dimension of the grid. The default is (60, 60).

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.
        rtol : TYPE
            DESCRIPTION.

        """
        if isinstance(grid_shape, int):
            grid_shape = (grid_shape,) * 2

        level = np.spacing(1)  # The same as np.finfo(float).eps

        domain = np.array([bases[0].domain, bases[1].domain])

        # Construct a ChebyshevU Grid
        basis_Ux = ChebyshevU(domain=bases[0].domain)
        basis_Uy = ChebyshevU(domain=bases[1].domain)
        xx, yy = Polynomial2.nodes2d(*grid_shape, basis_Ux, basis_Uy)

        values = f(xx, yy)
        # For the case the function passed is a constant
        if isinstance(values, Number):
            values = values * np.ones(xx.shape)

        # The maximum of the abs of the elements of vales

        # Scale of V
        vmax = np.max(abs(values))
        vscale = vmax
        # Raise an exception if the max is
        if vmax == np.inf:
            raise Exception("The function encountered infinite when evaluating")
        if np.any(np.isnan(values)):
            raise Exception("The function encountered not a number when evaluating")

        rtol, atol = get_tol(xx, yy, values, domain, level)
        u, s, vh = np.linalg.svd(values)

        # The rank of values
        k = sum(s > rtol)
        return u[:, :k], s[:k], vh[:k, :], vscale, rtol

    @staticmethod
    def vals_to_coef(vals, bases, **kwargs):
        r'''
        """
        Converts a matrix of values to orthogonal coefficients. The matrix
        are the values of the evaluation of a mesh grid in xy indexing
        of second kind Chebyshev points.

        Parameters
        ----------
        vals : Array_like or Iterable.
            DESCRIPTION. A matrix representing the values of evaluation
            or an length 3 Iterable with a low rank representation (u,s,vh) of
            the evaluation  such that (u*s)@vh is the matrix of the evaluation.
        bases : tuple
            tuple with the bases for each variable
        **kwargs : TYPE
            kind1x: bool
                If the values are the images of ChebyshevT nodes. This only ma-
                tter when the basis in x is ChebyshevT. When False if the basis
                is ChebyshevT the nodes that are considered is the nodes of
                ChebyshevU
            kind1y: bool
                If the values are the images of ChebyshevT nodes. This only ma-
                tter when the basis in y is ChebyshevT. When False if the basis
                is ChebyshevT the nodes that are considered is the nodes of
                ChebyshevU
        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        kind1x = kwargs.get("kind1x", False)
        kind1y = kwargs.get("kind1y", False)

        u, s, vh = np.linalg.svd(vals)

        rk = np.sum(s > 100 * np.spacing(1))
        u = u[:, :rk]
        vh = vh[:rk, :]
        s = s[:rk]

        p_rows = bases[0].interp_from_values(vh, kind1=kind1x)
        p_cols = bases[1].interp_from_values(u.T, kind1=kind1y)

        return (p_cols.T * s) @ p_rows

    def iszero(self):
        r"""
        Return true if ``self`` is zero, false otherwise.

        Returns
        -------
        bool
            Whether ``self`` is zero or not.

        Examples
        --------
        >>> a = np.arange(15).reshape(3, 5)
        >>> a
        array([[ 0,  1,  2,  3,  4],
               [ 5,  6,  7,  8,  9],
               [10, 11, 12, 13, 14]])
        >>>
        >>> p = polynomial.Polynomial2(a)
        >>> p.iszero()
        False

        Now doing the partial derivative in x direction of order 5.

        >>> p.diff((5, 0)).iszero()
        True
        """
        diag = self.diag
        domain = self.domain

        if np.linalg.norm(diag, np.inf) == 0:
            return True

        # Quick check over a small grid
        x = np.linspace(*domain[0], 10)
        y = np.linspace(*domain[1], 10)

        vals = self(x, y)

        if np.linalg.norm(vals, np.inf) > 0:
            return False

        # Otherwise check if either columns or rows are 0

        return np.all(self.cols.iszero()) or np.all(self.rows.iszero())

    def __len__(self):
        r"""
        The rank of the Polynomial2

        Returns
        -------
        int
            The rank of the Polynomial2

        """
        return len(self.diag)

    @property
    def shape(self):
        r"""
        Gives a pair representing the length of the columns and the rows.

        Returns
        -------
        int
            The length of the columns of ``self``.
        int
            The length of the rows of ``self``.

        """
        return self.cols.n, self.rows.n

    def interpf(self, fun):
        r"""
        This method compose ``fun`` with ``self``.

        Parameters
        ----------
        fun : callable
            A callable we want to compose in the form fun(self).

        Returns
        -------
        Polynomial2
            A Polynomial2 which is the approximation of fun(self).

        Examples
        --------

        Using the the function f(x,y)=cos(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.cos(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.interpf(np.cos)

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """
        return Polynomial2(lambda x, y: fun(self(x, y)), bases=(self.basis_x, self.basis_y))

    def get_coef(self, dims=None, fact=False):
        r"""
        This method  when ``fact``  is False returns a bidimensional array of
        coefficients of dimensions ``dims``=(m1,n1), considering that ``self``
        has shape(m,n) if m1>m the position from m are filled with zeros, the
        happen if n1>m. When ``fact=True`` the process is similar but return the
        low rank factorization of the array.

        Parameters
        ----------
        dims : int tuple or list, optional
            The dimensions of the array of coefficients
        fact : bool, optional
            If we want the array in a low rank factorization. If so returns
            the components of the factorization.

        Raises
        ------
        ValueError
            When ``dims`` is neither an integer nor a tuple.

        Returns
        -------
        array or tuple
            An array or a low rank factorization of the array.

        Examples
        --------

        Using the the function f(x,y)=x**2 + y**2 in the standard domain
        and basis, i.e. ChebyshevT in [-1, 1]:

        >>> p = polynomial.Polynomial2(lambda x, y: x**2 + y**2)
        >>> p.coef
        array([[1. , 0. , 0.5],
               [0. , 0. , 0. ],
               [0.5, 0. , 0. ]])

        >>> p.get_coef()
        array([[1. , 0. , 0.5],
               [0. , 0. , 0. ],
               [0.5, 0. , 0. ]])

        getting an array of coefficients with shape (4, 3), this will trun-
        cate in x direction and fill with zeros in y direction.

        >>> p.get_coef((4, 3))
        array([[1. , 0. , 0.5],
               [0. , 0. , 0. ],
               [0.5, 0. , 0. ],
               [0. , 0. , 0. ]])

        Doing the same but now getting the components.

        >>> p.get_coef((4, 3), fact=True)
        (array([[-0.92387953,  0.        , -0.38268343,  0.        ],
                [-0.38268343,  0.        ,  0.92387953,  0.        ]]),
        array([1.20710678, 0.20710678]),
        array([[-0.92387953,  0.        , -0.38268343],
               [ 0.38268343,  0.        , -0.92387953]]))
        """

        if dims is None or isinstance(dims, int):
            dims = (dims,) * 2
        if not isinstance(dims, (list, tuple)):
            raise ValueError(
                "'dims' must be an integer when we want square array of coeffi"
                "cients or a tuple or list with the dimensions in y and x axis."
            )

        d = self.diag
        m, n = dims
        c, r = self.cols.get_coef(m), self.rows.get_coef(n)

        if fact is False:
            result = (c.T * d) @ r
            result[np.abs(result) < numericalSettings.defaultPrecision] = 0
            return result
        return c, d, r

    def cos(self):
        r"""
        This compute the cosine of a Polynomial2

        Returns
        -------
        Polynomial2
            The cosine approximation of a Polynomial2

        Examples
        --------

        Using the the function f(x,y)=cos(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.cos(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.cos()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """

        return self.interpf(np.cos)

    def sin(self):
        r"""
        This compute the sine of a Polynomial2

        Returns
        -------
        Polynomial2
            The cosine approximation of a Polynomial2

        Examples
        --------

        Using the the function f(x,y)=sin(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.sin(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.sin()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """
        return self.interpf(np.sin)

    def exp(self):
        r"""
        This compute the exponential of a Polynomial2

        Returns
        -------
        Polynomial2
            The cosine approximation of a Polynomial2

        Examples
        --------

        Using the the function f(x,y)=exp(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.exp(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.exp()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """
        return self.interpf(np.exp)

    def cosh(self):
        r"""
        This compute the cosine hyperbolic of a Polynomial2

        Returns
        -------
        Polynomial2
            The cosine approximation of a Polynomial2

        Examples
        --------

        Using the the function f(x,y)=cosh(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.cosh(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.cosh()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """

        return self.interpf(np.cosh)

    def sinh(self):
        r"""
        This compute the sine hyperbolic of a Polynomial2

        Returns
        -------
        Polynomial2
            The cosine approximation of a Polynomial2

        Examples
        --------

        Using the the function f(x,y)=sinh(x**2 + y**2) in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> g = lambda x, y: np.sinh(f(x, y))
        >>> p = polynomial.Polynomial2(f)
        >>> ep = p.sinh()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> ep.sampletest(g, 1e-14)
        True
        """

        return self.interpf(np.sinh)

    def laplacian(self):
        r"""
        This apply the Laplacian operator to ``self`` i.e. :math:`\nabla^2p`.

        Returns
        -------
        Polynomial2
            A Polynomial2 which is the result of applying the Laplacian operator
            to ``self``.

        Examples
        --------

        Using the the function f(x,y)=x**3+y**2 in the standard domain
        and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**3 + y**2

        The Laplacian of f is g(x,y) = 6x+2

        >>> g = lambda x, y: 6 * x + 2
        >>> p = polynomial.Polynomial2(f)
        >>> lp = p.laplacian()

        Asserting that the error in the norm at infinity sense is less than
        1e-14:

        >>> lp.sampletest(g, 1e-14)
        True
        """
        return self.diff((2, 0)) + self.diff((0, 2))

    def cdr(self):
        r"""
        Give the low rank components of the approximation:
        Let :math:`k` be the rank of the approximation and :math:`\mathbf{c}=
        (c_0(y),\dots,c_{k-1}(y)),\ \mathbf{d}=(d_0,\dots,d_{k-1}),\ \mathbf{r}=
        (r_0(x),\dots,r_{k-1}(x))` be a vector of polynomials in the variable
        :math:`y` a vector of scalar and vector of polynomials in the variable
        :math:`x` respectively, this method returns the components of :math:`p`:
        :math:`\mathbf{c, \ d,\ r}` such that:

        .. math::
            p(x,y)=\sum_{i=0}^{k-1}r_{i}(x)d_{i}c_i(y)

        Returns
        -------
        Polynomial
            The separable component in the y direction.
        vector
            A vector which is the diagonal elements of the diagonal matrix
            of the low rank approximation.
        Polynomial
            The separable component in the x direction.

        """
        return self.cols, self.diag, self.rows

    def sample(self, grid_shape=None, components=False):
        r"""
        Evaluate the function at an n x m ChebyshevU grid. If not given
        we assumes the length in x direction and in y direction

        Parameters
        ----------
        grid_shape : int or Iterable, optional
            An Iterable with two integer elements representing the shape of
            the grid.
        components : bool
            If you want the values in the cols c(y) and the values in the diago
            nal d and values in the rows r(x) of self such (c(y).T * d) @ r(x)
            equals to self(meshgrid(x,y))

        Raises
        ------
        TypeError
            When grid shape is not int or an array_like object with 2
            elements

        Returns
        -------
        TYPE : array_like or tuple
            The values to return according to components

        Examples
        --------

        Using the standard domain and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> domain = [[-1, 1]] * 2
        >>> p = polynomial.Polynomial2(f)
        >>> sample = p.sample((3, 4))
        >>> sample
        array([[1.60355339, 0.89644661, 0.89644661, 1.60355339],
               [0.85355339, 0.14644661, 0.14644661, 0.85355339],
               [1.60355339, 0.89644661, 0.89644661, 1.60355339]])

        Now giving the components:

        >>> c, d, r = p.sample((3, 4), components=True)
        >>> ((c.T * d) @ r == sample).all()
        True
        """

        if grid_shape is None:
            m, n = self.shape
        elif isinstance(grid_shape, Iterable):
            m, n, *_ = grid_shape
        else:
            m = n = grid_shape

        if not (isinstance(m, int) and isinstance(n, int)):
            raise TypeError(
                "Polynomial2: grid_shape must be a integer representing "
                "the dimension of a square grid or an iterable with two"
                "integers when the grid is rectangular"
            )

        c, d, r = self.cdr()
        cv, rv = c.sample(m), r.sample(n)
        if components:
            return cv, d, rv

        return (cv.T * d) @ rv

    @property
    def vscale(self):
        r"""
        This is an estimation of the max(abs(self))

        Returns
        -------
        float
            the estimation of the maximum of the absolute value of the
            Polynomial2

        """
        if self.__vscale is None:
            m, n = self.shape

            # If m if of low degree then oversample
            m = min(max(m, 9), 2000)
            n = min(max(n, 9), 2000)  # Cannot afford to go over 2000x2000
            self.__vscale = np.max(np.abs(self.sample((m, n))))
        return self.__vscale

    def truncate(self, shape):
        r"""
        This method truncates the polynomial to the given shape

        Parameters
        ----------
        shape : int, tuple or list
            The shape of the new Polynomial2

        Returns
        -------
        result : Polynomial2
            A polynomial2 truncated with the given shape

        Examples
        --------
        >>> f = lambda x, y: np.cos(10 * x * (1 + y**2))

        >>> basis_x = polynomial.ChebyshevU(domain=[0, 1])
        >>> basis_y = polynomial.LegendreP(domain=[-1, 1])

        >>> fp = polynomial.Polynomial2(f, bases=(basis_x, basis_y))
        >>> fp
        Polynomial2 object:
          bases          :  [ChebyshevU(domain=array([0., 1.])), LegendreP(domain=array([-1.,  1.]))]
          domain         :  [0.0, 1.0] x [-1.0, 1.0]
          rank           :  16
          shape          :  129 x 91
          corner values  :  [1.0, 0.41, 1.0, 0.41]
          vertical scale :  1.00

        Truncate the polynomial with a new (20, 30) shape:

        >>> fp.truncate((20, 30))
        Polynomial2 object:
          bases          :  [ChebyshevU(domain=array([0., 1.])), LegendreP(domain=array([-1.,  1.]))]
          domain         :  [0.0, 1.0] x [-1.0, 1.0]
          rank           :  16
          shape          :  20 x 30
          corner values  :  [1.0, 0.4, 1.0, 0.4]
          vertical scale :  1.00
        """
        result = self.copy()
        if isinstance(shape, int):
            shape = [shape] * 2

        m, n = shape
        result.cols = result.cols.extend(m)
        result.rows = result.rows.extend(n)
        return result

    def definite_integral(self, bounds=None):
        r"""
        Computes the definite integral with the given bounds.

        Parameters
        ----------
        bounds : tuple or list, optional
            The intervals in each variable where we want to compute the definite
            integral. When not given we assume the extremes to be the domain of
            each variable.

        Returns
        -------
        float
            The definite integral over ``bounds``.

        Examples
        --------
        >>> f = lambda x, y: np.cos(10 * x * (1 + y**2))

        >>> domain = [[0, 1], [-1, 1]]
        >>> basis_x = polynomial.ChebyshevU(domain=[0, 1])
        >>> basis_y = polynomial.LegendreP(domain=[-1, 1])

        >>> fp = polynomial.Polynomial2(f, bases=(basis_x, basis_y))
        >>> fp
        Polynomial2 object:
          bases          :  [ChebyshevU(domain=array([0., 1.])), LegendreP(domain=array([-1.,  1.]))]
          domain         :  [0.0, 1.0] x [-1.0, 1.0]
          rank           :  16
          shape          :  129 x 91
          corner values  :  [1.0, 0.41, 1.0, 0.41]
          vertical scale :  1.00

        Computing the definite integral over [0, 1] x [-1, 1]:

        >>> fp.definite_integral()
        -0.0563153056630981

        Computing the definite integral over [0, .5] x [-1, 0]:

        >>> fp.definite_integral(((0, 0.5), (-1, 0)))
        -0.01715587996634457
        """

        if bounds is None:
            return self.rows.definite_integral().T * self.diag @ self.cols.definite_integral()
        else:
            return (
                self.rows.definite_integral(bounds[0]).T
                * self.diag
                @ self.cols.definite_integral(bounds[1])
            )

    def sum(self, axis=None):
        r"""
        Compute the definite integral over one or both axis of a Polynomial2.
        If axis=None integrate in booth directions, if axis=0 integrate in the
        variable y if axis=1 integrate in the variable x.

        Parameters
        ----------
        axis : scalar, optional
            Can be either None, 0 or 1. The default is None.

        Raises
        ------
        ValueError
            When the axis are neither None, 0 or 1

        Returns
        -------
        Polynomial or Polynomial2
            If ``axis`` is None returns a Polynomial2, if axis=0 return a Poly
            nomial in the variable x and if axis=1 return a Polynomial in the
            variable y.

        Examples
        --------
        >>> f = lambda x, y: np.cos(10 * x * (1 + y**2))

        >>> basis_x = polynomial.ChebyshevU(domain=[0, 1])
        >>> basis_y = polynomial.LegendreP(domain=[-1, 1])
        >>> bases = (basis_x, basis_y)

        >>> fp = polynomial.Polynomial2(f, bases=bases)
        >>> fp
        Polynomial2 object:
          bases          :  [ChebyshevU(domain=array([0., 1.])), LegendreP(domain=array([-1.,  1.]))]
          domain         :  [0.0, 1.0] x [-1.0, 1.0]
          rank           :  16
          shape          :  129 x 91
          corner values  :  [1.0, 0.41, 1.0, 0.41]
          vertical scale :  1.00

        Integrating in the y variable we get a Polynomial in the variable x:

        >>> fp.sum(axis=0)
        <class 'tautoolbox.polynomial.polynomial1.Polynomial'> object with 1 column:
          degree         : 90
          domain         : [0.00 1.00]
          end values     : [2.00 -0.03]
          vertical scale : 2.0
          basis          : ChebyshevU

        Integrating in the x variable we get a Polynomial in the variable y:

        >>> fp.sum(axis=1)
        <class 'tautoolbox.polynomial.polynomial1.Polynomial'> object with 1 column:
          degree         : 128
          domain         : [-1.00 1.00]
          end values     : [0.05 0.05]
          vertical scale : 0.0912
          basis          : LegendreP

        Integrating in both variables:

        >>> fp.sum()
        -0.0563153056630981
        """
        if axis is None:
            return self.definite_integral()
        elif axis == 0:
            c, d, r = self.cdr()
            coef = np.einsum("ij,i->j", r.coeff, (c.sum().T * d).flatten())
            return Polynomial(coef, basis=r.basis)
        elif axis == 1:
            c, d, r = self.cdr()
            coef = np.einsum("ij,i->j", c.coeff, (r.sum().T * d).flatten())
            return Polynomial(coef, basis=c.basis)
        else:
            raise ValueError(
                "axis can be: 0, meaning integrating only over y "
                "1, meaning integrating only over x and None meaning "
                "all variables"
            )

    def qr(self):
        c, d, r = self.cdr()

        # Balance out the scaling
        sign = np.sign(d)
        c = c.multiply_matrix(sign * abs(d) ** (1 / 2))
        r = r.multiply_matrix(abs(d) ** (1 / 2))

        # QR of the columns
        q, rc = c.qr()

        # Form R
        r = r.multiply_matrix(rc.T)
        return q, r.T

    def svd(self):
        c, d, r = self.cdr()

        q_left, r_left = c.qr()
        q_right, r_right = r.qr()
        u, s, v = np.linalg.svd((r_left * d) @ r_right.T)
        u = q_left.multiply_matrix(u)
        v = q_right.multiply_matrix(v.T)
        return u, s, v

    def evalm(self, x, y):
        r"""
        This is the same as evaluate self at a meshgrig(x,y).
        this function is useful because is a fast way of evaluate a
        mesh grid since it evaluate x over the rows of ``self`` and
        y over the columns of self and the values of the meshgrid(x,y) is the
        product broadcasting of the y values and the x values.
        This function is used to make the plot grid and for estimating the error
        in the norm at infinity sense.

        Parameters
        ----------
        x : array_like
            A set o points in the x-axis
        y : array_like
            A set of points in the y-axis

        Returns
        -------
        array_like
            The same as self(meshgrid(x,y))

        Examples
        --------

        Using the standard domain and basis i.e. ChebyshevT in [-1, 1]:

        >>> f = lambda x, y: x**2 + y**2
        >>> domain = [[-1, 1]] * 2
        >>> p = polynomial.Polynomial2(f)
        >>> x, y = [np.linspace(*domain[0])] * 2
        >>> xx, yy = np.meshgrid(x, y)
        >>> np.max(abs(p.evalm(x, y) - f(xx, yy)))
        6.661338147750939e-16
        """

        return (self.cols(y).T * self.diag) @ self.rows(x)

    def sampletest(self, fun, atol):
        r"""
        This method is a fast way to test the accuracy of the Approximation

        Parameters
        ----------
        fun : callable
            A function from which to approximate
        atol : scalar
            The absolute tolerance

        Returns
        -------
        bool
            whether the approximation complies with the tolerance or not

        Examples
        --------

        Testing if the error of the approximation of cos(x**2 + y**2) in the
        standard domain and basis i.e. ChebyshevT in [-1, 1] is less than 1e-14:

        >>> f = lambda x, y: np.cos(x**2 + y**2)
        >>> domain = [[-1, 1]] * 2
        >>> p = polynomial.Polynomial2(f)
        >>> x, y = [np.linspace(*domain[0])] * 2
        >>> xx, yy = np.meshgrid(x, y)
        >>> p.sampletest(f, 1e-14)
        True
        """
        n = 100
        x = np.linspace(*self.domain[0], n)
        y = np.linspace(*self.domain[1], n)
        xx, yy = np.meshgrid(x, y)

        return np.max(abs(self.evalm(x, y) - fun(xx, yy))) < atol

    def fredholm1(self, rhs, method="tsve", alpha=0, eta=1, xtol=1e-05, maxfun=500):
        r"""
        Compute the solution of Fredholm integral equation of the first kind
        that have ``self`` as kernel.


        Parameters
        ----------
        rhs : Polynomial.
            The right hand side of the first equation (see notes).
        method : str, optional
            The method for solving the equation. The default is "tsve".
        alpha : scalar, optional
            The noise level. The default is 0.
        eta : scalar, optional
            Related with the discrepancy principle, eta>=1 (see notes). The de
            fault is 1.
        xtol : float, optional
            The convergence tolerance (fminbound function).
            The default value is 1e-5.
        maxfun : int, optional
            Maximum number of function evaluations allowed (fminbound function).
            The default value is 500.

        Returns
        -------
        Polynomial
            The approximate solution.


        Notes
        -----
        This compute the Fredholm integral equation of the first kind

        .. math::
            \int_{\Omega_1}k(s,t)x(t)dt=g(s), \quad s \in \Omega_2
        with a square integrable kernel k. The :math:`\Omega_i, i=1,2` are subsets
        of :math:`\mathbb{R}`.
        This equation is solved using truncated singular value expansion method
        (tsve) or Tikhonov regularization method. The parameters ``eta`` and
        ``alpha``, which interferes on the computation of ``delta'',
        are for the discrepancy principle:

        .. math::
            \left\|\int_{\Omega_1}k(s,t)x(t)-g^{\delta}(s)\right\|\le\eta\delta

        """
        g = rhs
        if not isinstance(g, Polynomial):
            g = Polynomial(g, basis=self.basis_x)

        # adding continuous noise to g
        noise = Polynomial.randnPol(self.basis_x, 0.01)  # generate noise
        ng = g.norm()  # compute norm of rhs

        noise = alpha * noise * ng / noise.norm()  # adjust norm of the noise
        g_delta = g + noise  # add noise to rhs
        delta = noise.norm()  # compute norm of noise

        psi, ks, phi = self.svd()
        rk = len(ks)  # maximal rank of the separable approximation

        if method == "tsve":
            beta = np.zeros([rk, 1])
            for i in range(rk):
                beta[i] = (phi[i] * g_delta).definite_integral() / ks[i]
                xk = psi[0 : i + 1].multiply_matrix(beta[0 : i + 1])

                if ((self.T * xk).sum(axis=1) - g_delta).norm() < eta * delta:
                    break

            return xk[0]

        elif method == "tr":

            def errlambda(lam, sigma, gnoise, psi, ke, rk, eta, e, dd):
                beta = dd * sigma / (sigma**2 + lam**2)
                x = psi.multiply_matrix(beta.reshape(-1, 1))
                return abs((((ke.T * x).sum(1) - gnoise).norm()) ** 2 - eta**2 * e**2)

            dd = (phi * g_delta).sum()

            # Solving minimization problem for lambda
            eta = 1
            lam = fminbound(
                lambda x: errlambda(x, ks, g_delta, psi, self, rk, eta, delta, dd),
                0,
                2,
                xtol=xtol,
                maxfun=maxfun,
            )
            beta2 = ks / (ks**2 + lam**2)
            beta = (dd * beta2).reshape(-1, 1)

            # tikonov relative error
            xlam = psi.multiply_matrix(beta)

            return xlam[0]
        else:
            raise ValueError("Possible methods are 'tsve' and 'tr")


def readiness_check(
    values,
    vscale=0,
    hscale=1,
    state="standard",
    tol=np.spacing(1),
    basis=None,
):
    vscale = max(vscale, np.max(np.abs(values)))
    n = values.shape[-1]

    # The abscissas are the nodes of ChebyshevU basis
    coef = interp_from_values(values, basis=basis)

    if coef.ndim == 1:
        coef = coef.reshape(1, -1)
        values = values.reshape(1, -1)
    m = coef.shape[0]
    if state == "standard":
        vscaleF = np.max(np.abs(values), axis=1)
        if vscaleF.size == 1:
            vscaleF = vscaleF[0]

        tol = tol * np.maximum(hscale, vscale / vscaleF)
        is_ok = np.zeros(m, dtype=bool)
        cutoff = np.zeros(m)
        for i in range(m):
            cutoff[i] = standard_chop(coef[i], tol)
            # Check readiness
            is_ok[i] = cutoff[i] < n
            # Exit if any column is not ok
            if not is_ok[i]:
                break
        return np.all(is_ok), np.max(cutoff)


def interp_from_values(values, basis, abscissas=None):
    r"""
    Get the coefficients of a Polynomial approximation in a given orthogonal
    basis of a function with the values evaluated at the abscissas.


    Parameters
    ----------
    values : scalar or array_like
        The values of a function evaluated at the abscissas.
    abscissas : scalar or array_like, optional
        The abscissas corresponding to the values.
    **kwargs : dict
        bases : str
            The bases we want the coefficients
        domain : array_like
            The domain of the basis
        alpha : scalar
            This only make sense for Gegenbauer bases
    Returns
    -------
    TYPE
        DESCRIPTION.
    """
    n = values.shape[-1]

    # When abscissas are not given assumes that the values are evaluated at
    # ChebyshevU nodes
    if abscissas is None:
        abscissas, *_ = ChebyshevU(domain=basis.domain).nodes(n)
    A = basis.vander(abscissas, n=n)

    return np.linalg.solve(A, values.T).T


def nodes(n, domain=[-1, 1]):
    """
    Parameters
    ----------
    n : Integer
        DESCRIPTION. The Number of nodes
    domain : Iterable, optional
        DESCRIPTION. The default is [-1, 1]. A length 2 iterable of numbers

    Returns
    -------
    Array_like
        DESCRIPTION. An array like object of of numbers which are the nodes

    """
    return ChebyshevU(domain=domain).nodes(n)[0]


def get_tol(xx, yy, values, domain=[[-1, 1]] * 2, level=np.finfo(float).eps):
    m, n = xx.shape
    if isinstance(values, Number):
        values = values * np.ones((m, n))

    grid = max(m, n)
    dfdx = 0
    dfdy = 0
    if m > 1 and n > 1:
        # Pad  the arrays to guarantee df/dx and df/dy have the same size.
        dfdx = np.diff(values[: m - 1, :]) / np.diff(xx[: m - 1, :])
        dfdy = np.diff(values[:, : n - 1], axis=0) / np.diff(yy[:, : n - 1], axis=0)
    elif m > 1 and n == 1:
        # Constant in the y direction
        dfdy = np.diff(values) / np.diff(yy)
    elif m == 1 and n > 1:
        # constant in the x direction
        dfdx = np.diff(values, axis=0) / np.diff(xx, axis=0)

    # Approximation for the norm of the gradient over the domain
    jac_norm = np.max((np.max(np.abs(dfdx)), np.max(np.abs(dfdy))))

    vscale = np.max(np.abs(values))

    rtol = grid ** (2 / 3) * level
    atol = np.max(np.abs(domain)) * np.max((jac_norm, vscale)) * rtol
    return rtol, atol


def adaptive_cross_approx(V, atol, factor):
    m, n = V.shape
    width = np.min((m, n))
    pivot_vals = []  # Store an unknown number of pivots
    pivot_pos = []  # store the positions of the pivots
    fail = True  # assume we fail

    # Main algorithm
    zero_rows = 0  # Count the number of zero rows
    ind = np.argmax(np.abs(V))
    row, col = np.unravel_index(ind, V.shape)
    inf_norm = np.abs(V[row, col])

    # Bias toward diagonal for square matrices
    if m == n and np.max(np.abs(np.diag(V))) - inf_norm > -atol:
        ind = np.argmax(np.abs(np.diag(V)))
        inf_norm = np.abs(np.diag(V))[ind]
        col = ind
        row = ind

    rows = np.zeros((0, n))
    cols = np.zeros((m, 0))

    while inf_norm > atol and zero_rows < width / factor and zero_rows < width:
        # Extract the row and the column

        rows = np.concatenate([rows, V[[row], :]])
        cols = np.concatenate([cols, V[:, [col]]], axis=1)

        piv_val = V[row, col]
        V -= cols[:, [zero_rows]] @ (rows[[zero_rows], :] / piv_val)

        # Keep track of progress
        zero_rows += 1  # One more row is zero
        pivot_vals.append(piv_val)  # Store the value of the pivot
        pivot_pos.append([row, col])  # Store the position of the pivot

        # Next pivot
        ind = np.argmax(np.abs(V))
        row, col = np.unravel_index(ind, V.shape)
        inf_norm = np.abs(V[row, col])

        if m == n and np.max(np.abs(np.diag(V))) - inf_norm > -atol:
            ind = np.argmax(np.abs(np.diag(V)))
            inf_norm = np.abs(np.diag(V))[ind]

            row = ind
            col = ind

    if inf_norm <= atol:
        fail = False

    if zero_rows >= width / factor:
        fail = True

    return (
        np.array(pivot_vals),
        np.array(pivot_pos, dtype=int),
        rows,
        cols,
        fail,
    )


def refine_grid(n, fun_type=None):
    if fun_type in ["trig", "periodic"]:
        n = 2 ** (np.floor(np.log2(n)) + 1)
    else:
        n = 2 ** (np.floor(np.log2(n)) + 1) + 1

    nest = np.arange(0, n, 2)
    return int(n), nest


def parse_domain(domain):
    if not (
        isinstance(domain, Iterable)
        and len(domain) == 2
        and all(
            [
                isinstance(i, Iterable)
                and len(i) == 2
                and all([isinstance(j, Number) for j in i])
                for i in domain
            ]
        )
    ):
        raise ValueError("Domain must be an 2X2 array_like object of numbers")

    domain = np.array(domain)
    if domain[0, 0] >= domain[0, 1] or domain[1, 0] >= domain[1, 1]:
        raise ValueError(
            "The left hand boundaries of the domains must be "
            "less than the right hand boundaries "
        )
    return domain


def parse_bases(bases):
    if not (
        isinstance(bases, Iterable)
        and len(bases) == 2
        and all([isinstance(b, str) for b in bases])
    ):
        raise ValueError(
            "Polynomial2: bases must be an Iterable with "
            "two string elements e.g., ['ChebyshevT','LegendreP']"
        )
    return bases if isinstance(bases, list) else list(bases)


def antidiag_ind_flatened(m, n):
    A = np.arange(m * n).reshape(m, -1)
    result = []
    for col in range(n):
        startcol = col
        startrow = 0

        while startcol >= 0 and startrow < m:
            result.append(A[startrow][startcol])

            startcol -= 1
            startrow += 1

    # For each row start column is N-1
    for row in range(1, m):
        startrow = row
        startcol = n - 1

        while startrow < m and startcol >= 0:
            result.append(A[startrow][startcol])

            startcol -= 1
            startrow += 1

    return result


def fastHankelMul(a, b, x=None):
    if x is None:
        x = b.copy()
        n = len(x)
        b = np.r_[a[-1], np.zeros(n - 1)]

    n = len(x)
    return ifft(fft(np.r_[b, 0, a[:-1]]) * fft(np.r_[x[::-1], np.zeros(n)]))[:n].real


def fastToeplitzMul(a, b, x=None):
    a = a.copy()
    a[0] *= 2
    if x is None:
        x = b
        b = a

    n = len(a)
    return ifft(fft(np.r_[a, 0, np.flip(b[1:])]) * fft(np.r_[x, np.zeros(n)]))[:n].real


def computeWeights(e, n):
    c1 = e + 1
    c2 = 0.5
    c3 = e + c2
    c4 = c1 + c2
    c0 = (2**c3) * beta(c1, c2)

    w = np.zeros(n)

    w[0] = 1

    if n > 1:
        w[1] = c3 / c4

        for i in range(2, n):
            w[i] = (2 * c3 * w[i - 1] + (i - 1 - c4) * w[i - 2]) / (c3 + i)

    return c0 * w
