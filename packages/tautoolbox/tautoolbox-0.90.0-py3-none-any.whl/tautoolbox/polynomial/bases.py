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

"""A module for efficiently deal with orthogonal Polynomial basis.

Within the documentation for this module, a "finite power series,"
i.e., a Polynomial (also referred to simply as a "series") is
represented by a 1-D numpy array of the Polynomial's coefficients,
ordered from lowest order term to highest.  For example,
``np.array([1,2,3])`` represents ``P_0 + 2*P_1 + 3*P_2``, where P_n is
the n-th order basis Polynomial applicable to the specific module in
question, e.g., `Polynomial` (which "wraps" the "standard" basis) or
`Chebyshev`.

For optimal performance, all operations on Polynomials, including
evaluation at an argument, are implemented as operations on the
coefficients.

Additional (module-specific) information can be found in the docstring
for the module of interest.
"""

from abc import abstractmethod
from copy import deepcopy
from numbers import Number
from warnings import warn

import numpy as np
from numpy.linalg import eig
from numpy.polynomial import legendre
from scipy.fft import fft, ifft
from scipy.linalg import hankel, toeplitz
from scipy.sparse import csr_matrix, spdiags
from scipy.sparse import eye as speye
from scipy.sparse.linalg import spsolve
from scipy.special import beta, binom, comb, factorial, gamma, loggamma


class T3Basis:
    r"""
    A class used to represent a polynomial basis in one variable.
    Implemented using three-terms based polynomial families.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters (like alpha for Gegenbauer or alpha and beta for Jacobi).

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(
        self,
        domain: np.ndarray | tuple = (-1, 1),
        params: dict = {},
        dtype=np.float64,
        **kwargs,
    ):
        self.name = "T3Basis"
        self.dtype = dtype
        self.params = params
        self.p1 = np.array([-self.beta(0) / self.alpha(0), 1 / self.alpha(0)], self.dtype)
        self.domain = np.array(domain, self.dtype)

        self.support = np.array([-1, 1], self.dtype)

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and all(self.domain == other.domain)
            and (self.params == other.params)
        )

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, value):
        self.__domain = np.array(value, self.dtype)
        if self.domain.size != 2:
            raise ValueError(f"Invalid domain = {self.domain}")

        self.c1 = 2 / np.diff(self.domain).item()
        self.c0 = -sum(self.domain) / np.diff(self.domain).item()

        A = [[1, self.p1[1] * self.c0 + self.p1[0]], [0, self.p1[1] * self.c1]]
        self.x1 = np.linalg.solve(np.array(A, self.dtype), np.array([0, 1], self.dtype))

    @abstractmethod
    def alpha(self, n):
        pass

    @abstractmethod
    def beta(self, n):
        pass

    @abstractmethod
    def gamma(self, n):
        pass

    @abstractmethod
    def eta(self, i, j):
        pass

    @abstractmethod
    def theta(self, n):
        pass

    def matrixM(self, n):
        r"""
        If C is an orthogonal series then this method give the matrix product
        of C and x such that :math:`Cx=MC`.

        Parameters
        ----------
        n : int, optional
            The dimension of the matrix,when not given we take the default di-
            mension of the basis options. The default is None.

        Returns
        -------
        M : array_like
            The ``n``x``n`` product matrix.

        See Also
        --------

        Examples
        --------
        Using ChebyshevT basis in the default domain [-1,1]:

        >>> b = polynomial.ChebyshevT()
        >>> c = np.arange(5)
        >>> c
        array([0, 1, 2, 3, 4])

        >>> m = b.matrixM(6)
        >>> m
        array([[0. , 0.5, 0. , 0. , 0. , 0. ],
               [1. , 0. , 0.5, 0. , 0. , 0. ],
               [0. , 0.5, 0. , 0.5, 0. , 0. ],
               [0. , 0. , 0.5, 0. , 0.5, 0. ],
               [0. , 0. , 0. , 0.5, 0. , 0.5],
               [0. , 0. , 0. , 0. , 0.5, 0. ]])

        >>> m @ np.r_[c, 0]
        array([0.5, 1. , 2. , 3. , 1.5, 2. ])
        """
        f2 = 1 / self.c1
        f3 = -self.c0 / self.c1

        e0 = np.arange(n, dtype=self.dtype)
        e1 = np.arange(n - 1, dtype=self.dtype)
        M = (
            np.diag(f2 * self.alpha(e1) + 0 * e1, -1)
            + np.diag(f2 * self.beta(e0) + f3 + 0 * e0)
            + np.diag(f2 * self.gamma(e1 + 1) + 0 * e1, 1)
        )

        return M

    def matrixN(self, n):
        r"""
        Gives the derivative matrix in the basis. This method is based in the
        paper 'Avoiding Similarity Transformations in the tau method - 2015
        -(José Matos et al.), and builds the M matrix in the basis used. Here,
        we also implemented the orthogonal shift.

        Parameters
        ----------
        n : int, optional
            The dimension of the matrix, When not given we take the default
            dimension in the basis options:The default is None.

        Returns
        -------
        N : array_like
            The ``n`` x ``n`` derivative matrix.

        See Also
        --------
        matrixO: The integration matrix
        matrixM: The product by x matrix in the basis

        Examples
        --------
        >>> b = polynomial.LegendreP()
        >>> c = np.arange(5)
        >>> c
        array([0, 1, 2, 3, 4])

        >>> n = b.matrixN(5)

        >>> # The differentiation matrix
        >>> n
        array([[0., 1., 0., 1., 0.],
               [0., 0., 3., 0., 3.],
               [0., 0., 0., 5., 0.],
               [0., 0., 0., 0., 7.],
               [0., 0., 0., 0., 0.]])

        >>> # The derivative of the series in the Legendre basis
        >>> n @ c
        array([ 4., 18., 15., 28.,  0.])
        """

        N = np.zeros((n, n), self.dtype)

        for j in range(1, n):
            N[:j, j] = self.c1 * self.eta(np.arange(j, dtype=self.dtype), j + 1)

        return N

    def matrixO(self, n):
        r"""
        Matrix related with integration. This function makes use of paper:
        Avoiding Similarity Transformations in the tau method - 2015 -(José
        Matos et al.), and consists in to build the O matrix in the basis used.
        Here, we also implemented the orthogonal shift.

        Parameters
        ----------
        n : int, optional
            The dimension of the matrix. When not given we take the default
            dimension of the basis options.The default is None.

        Returns
        -------
        arrayLike
            The ``n`` x ``n`` matrix of integration.

        See Also
        --------
        matrixN
        matrixM


        """

        f2 = 1 / self.c1
        v = f2 * self.theta(n)
        return np.diag(v[0, 0:-1], -1) + np.diag(v[1, :]) + np.diag(v[2, 1:], 1)

    def orth2powmatrix(self, n):
        r"""
        Returns the V matrix such that :math:`XV = P`, where
        :math:`X = [x^0, x^1, ...]` is the power series and
        :math:`P = [P_1, P_2, ...]` is the orthogonal basis.

        Parameters
        ----------
        n : int, optional
            The dimension of the matrix. When n is None we take the default
            of the basis options. The default is None.

        Returns
        -------
        V : array_like
            The matrix of conversion from orthogonal basis to power basis

        See Also
        --------
        pow2orthmatrix: The matrix of conversion from power basis to orthogonal
        basis.

        Example
        -------

        Using ChebyshevT basis in the domain [-1,1]:

        >>> p = polynomial.ChebyshevT()
        >>> p.orth2powmatrix(5)
        array([[ 1.,  0., -1., -0.,  1.],
               [ 0.,  1.,  0., -3., -0.],
               [ 0.,  0.,  2.,  0., -8.],
               [ 0.,  0.,  0.,  4.,  0.],
               [ 0.,  0.,  0.,  0.,  8.]])

        Using LegendreP basis in the domain [0,1]:

        >>> p = polynomial.LegendreP(domain=[0, 1])
        >>> p.orth2powmatrix(5)
        array([[   1.,   -1.,    1.,   -1.,    1.],
               [   0.,    2.,   -6.,   12.,  -20.],
               [   0.,    0.,    6.,  -30.,   90.],
               [   0.,    0.,    0.,   20., -140.],
               [   0.,    0.,    0.,    0.,   70.]])
        """
        V = np.zeros((n, n), dtype=self.dtype)

        V[0, 0] = 1
        if n == 1:
            return V

        V[0, 1] = (self.c0 - self.beta(0)) / self.alpha(0)
        V[1, 1] = self.c1 / self.alpha(0)
        if n == 2:
            return V

        for m in range(2, n):
            V[0, m] = (
                (self.c0 - self.beta(m - 1)) * V[0, m - 1] - self.gamma(m - 1) * V[0, m - 2]
            ) / self.alpha(m - 1)

            V[1 : m + 1, m] = (
                self.c1 * V[0:m, m - 1]
                + (self.c0 - self.beta(m - 1)) * V[1 : m + 1, m - 1]
                - self.gamma(m - 1) * V[1 : m + 1, m - 2]
            ) / self.alpha(m - 1)

        return V

    def pow2orthmatrix(self, n):
        r"""
        Returns the inverse of matrix V, where V is such that
        :math:`XV = P, X = [x^0, x^1, ...]` is the power series and
        :math:`P = [P_1, P_2, ...]` is the orthogonal basis. This is more
        stable than to compute :math:`V^-1, inv(V) or I\V`.
        Parameters
        ----------
        n : int, optional
            The dimension of the matrix. When ``n`` is None we take the de-
            fault that is in the basis options. The default is None.

        Returns
        -------
        W : array_like
            The matrix of conversion from power basis to orthogonal basis.

        See Also
        --------
        orth2powmatrix: The matrix of conversion from orthogonal basis to power
        basis

        Examples
        --------

        Using ChebyshevU in the domain [0,2]:

        >>> b = polynomial.ChebyshevU(domain=[0, 2])
        >>> b.pow2orthmatrix(5)
        array([[1.    , 1.    , 1.25  , 1.75  , 2.625 ],
               [0.    , 0.5   , 1.    , 1.75  , 3.    ],
               [0.    , 0.    , 0.25  , 0.75  , 1.6875],
               [0.    , 0.    , 0.    , 0.125 , 0.5   ],
               [0.    , 0.    , 0.    , 0.    , 0.0625]])
        """

        W = np.zeros((n, n), self.dtype)
        M = self.matrixM(n)
        W[0, 0] = 1

        for i in range(1, n):
            W[:, i] = M @ W[:, i - 1]

        return W

    def matrixQ(self, n, q):
        """Evaluate a dilation matrix of order `n` and scale `q`"""
        return self.matrixL(n, 0, q)

    def matrixL(self, n, a, q):
        """Evaluate the linear translation operator matrix"""
        xx = self.nodes(n)[0]
        TT = self.vander(xx, n)
        TTq = self.vander(a+q*xx, n)
        return np.linalg.solve(TT, TTq)

    def matrixQs(self, n, q):
        """Evaluate a dilation matrix of order `n` and scale `q` using
        the similarity transformation"""
        return self.pow2orthmatrix(n) @ np.diag(q ** np.arange(n)) @ self.orth2powmatrix(n)

    def matrixLs(self, n, a, q):
        """Evaluate the linear translation operator matrix using a
        similarity transformation"""
        A = np.zeros((n, n))
        for j in range(n):
            for i in range(j + 1):
                # comb <-> nchoosek
                A[i, j] = comb(j, i) * a ** (j - i)

        Q = np.diag(q ** np.arange(n))
        W = self.pow2orthmatrix(n)
        V = self.orth2powmatrix(n)

        return W @ A @ Q @ V

    def __call__(self, coef, x, n=None):
        r"""
        Evaluates the polynomial with coefficients ``coef`` at the points ``x``

        Parameters
        ----------
        coef : array_like
            The coefficients of a Polynomial
        x : scalar or array_like
            The abscissas to evaluate
        n : int, optional
            Trim ``coef`` at the column ``n+1``

        Returns
        -------
        scalar or array_like
            sum(a_iP_i(xx)), i = 0:len(a)

        Examples
        --------
        In the case x is a number:

        >>> coef = np.arange(1, 5)
        >>> bas = polynomial.ChebyshevT()
        >>> bas(coef, 1)
        10.0

        In the case x is a one-dimensional array_like object:

        >>> x = np.arange(1, 5)
        >>> bas(coef, x)
        array([  10.,  130.,  454., 1078.])

        In the case x is a by-dimensional array_like object:

        >>> x = np.arange(9).reshape(3, 3)
        >>> bas(coef, x)
        array([[-2.000e+00,  1.000e+01,  1.300e+02],
               [ 4.540e+02,  1.078e+03,  2.098e+03],
               [ 3.610e+03,  5.710e+03,  8.494e+03]])

        """
        if isinstance(coef, Number):
            coef = np.array([coef], self.dtype)
        m = coef.shape[-1]
        if n is None:
            n = m - 1

        if n < 0 or not isinstance(n, int) or n > m - 1:
            raise ValueError(
                "n must be an integer greater or equal to zero and lesser or "
                f" equal to the degree of the polynomial was given{n}"
            )
        P0 = np.ones(np.shape(x), self.dtype)

        v = coef[..., :1][:, np.newaxis] * P0

        if n > 0:
            # Linear transformation from the domain
            z = self.c1 * x + self.c0

            # we are taking into account the linear transformation
            # or else the code would be simply: P1 = p1[1]*x + p1[0];
            P1 = self.p1[1] * z + self.p1[0]
            v += coef[..., 1:2][:, np.newaxis] * P1

            for k in range(1, n):
                P2 = ((z - self.beta(k)) * P1 - self.gamma(k) * P0) / self.alpha(k)
                v += coef[..., k + 1 : k + 2][:, np.newaxis] * P2
                P0 = P1
                P1 = P2
        return v.reshape(np.shape(coef[..., 0]) + np.shape(x))

    def polyvalm(self, a, x, n=None):
        """
        Orthogonal evaluation for matrices. f = polyvalm(x, a, M) returns the
        value of a Polynomial evaluated (orthogonally) at M: f = sum(a_iP_i).

        Parameters
        ----------
        a : array_like
            The coefficients of a Polynomial in the self basis
        x : scalar or array_like
            Input for evaluation must be a square matrix

        n : int, optional
            Where to stop when n is not given we assumes n=len(co)-1.
            The default is None.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        scalar or array_like
            The sum(co_iP_i(x)), i in range(n)

        See Also
        --------
        __call__ and vander

        Examples
        --------

        """
        if isinstance(x, Number):
            x = np.array([[x]], self.dtype)
        if isinstance(x, list):
            x = np.array(x, self.dtype)

        p, q = x.shape

        if p != q:
            raise ValueError("x argument must be a square matrix")

        if isinstance(a, list) and all(isinstance(el, (int, float)) for el in a):
            a = np.array(a, self.dtype)

        if not (isinstance(a, np.ndarray) and a.ndim == 1):
            raise ValueError(
                "a must be a list with numeric entries or a one dimensional numpy array"
            )

        if n is None:
            n = len(a) - 1

        iden = np.eye(x.shape[0], dtype=self.dtype)

        P0 = iden
        v = a[0] * P0

        if n == 0:
            return v

        # linear transformation from domain
        z = self.c1 * x + self.c0 * iden

        # we are taking into account the linear transformation
        # or else the code would be simply: P1 = p1(1)*x + p1(2)* P0
        P1 = self.p1[1] * z + self.p1[0] * iden
        v = v + a[1] * P1
        if n == 1:
            return v

        for k in range(1, n):
            P2 = ((z - self.beta(k) * iden) @ P1 - self.gamma(k) * P0) / self.alpha(k)
            v += a[k + 1] * P2
            P0 = P1
            P1 = P2

        return v.item() if v.size == 1 else v

    def polyvalmM(self, a, n):
        """
        Evaluation for matrices M.
        v = polyvalmM(x, a) returns the value of
        a Polynomial evaluated (orthogonally) at matrix M.
        M is the matrix associated with the multiplication
        operator in the Tau method: v = sum(a_iP_i).
        This function exists because it is possible to use specialized
        formulas that take into account the errors that happen
        due to the discretization of an infinite operator.
        The idea of this function is similar to the relation between
        functions log and log1p where the later evaluates log more
        accurately in the neighborhood of zero.


        Parameters
        ----------
        co : array_like
            The coefficients of a Polynomial in the self basis

        Returns
        -------
        array_like
            The sum(co_iP_i(M)), i in range(len(co))

        """

        return self.polyvalm(a, self.matrixM(n))

    def vander(self, x, n, dmin=0, dmax=0):
        r"""
        Evaluates the first ``n`` orthogonal Polynomials at point ``x``.

        That is return :math:`(P_0(x),P_1(x),\dots,P_{n-1}(x))` in the
        simplest case.

        Returns a vector of values such that if c is the coefficients
        of a Polynomial in the basis ``self`` so
        ``sum(self.vander(x) * c`` is the value of the Polynomial
        evaluated at x.

        With other optional arguments it returns not only the function
        but but also the values of derivatives of the basis
        Polynomials at point x.

        This function is useful, for instance, to build the C block
        for the initial/boundary conditions.

        The optional arguments are useful if we want to establish the
        continuity of the functions and derivatives of the function at
        end points with a piecewise solution.

        Parameters
        ----------
        x : scalar or vector
            The values we want to compute their images at the basis Polynomials
        n : int
            The first n basis Polynomials to evaluate.
        dmin : int, optional
            The minimum order of the derivatives. The default is 0.
        dmax : int, optional
            The maximum order of the derivatives. The default is 0.

        Raises
        ------
        TypeError
            DESCRIPTION.

        Returns
        -------
        np.array
            values of the Polynomials in the points given

        See Also
        --------
        polyvalm
        """

        if isinstance(x, Number):
            x = np.array([x], self.dtype)
        else:
            x = np.array(x, self.dtype)

        if x.dtype == np.dtype("O"):
            raise TypeError(
                "tautoolbox: x argument should be either a scalar or a vector"
                " or a numeric plain list"
            )

        if dmax < dmin:
            return np.zeros((0, n), self.dtype)

        x_shape = x.shape
        v = np.zeros((*x_shape, n), self.dtype)

        P0 = np.ones(x.shape, self.dtype)
        v[..., 0] = P0  # Polynomial with 1 term - degree 0

        if n > 1:
            # Transformation from the domain
            z = self.c1 * x + self.c0

            # We are taking into account the linear transformation or else
            # the code would be simply: P1 = p1[1] * x + p1[0]
            P1 = self.p1[1] * z + self.p1[0]
            v[..., 1] = P1  # Polynomial with 2 terms - degree 1

        for k in range(1, n - 1):
            v[..., k + 1] = (
                (z - self.beta(k)) * v[..., k] - self.gamma(k) * v[..., k - 1]
            ) / self.alpha(k)

        # Evaluate derivatives now

        # for k in range(dmin):
        #     v = v @ self.matrixN(n)
        if dmin > 0:
            v = v @ np.linalg.matrix_power(self.matrixN(n), dmin)
        if dmin == dmax:
            return v
        V = v.copy()
        for k in range(dmin + 1, dmax + 1):
            v = v @ self.matrixN(n)
            V = np.concatenate((V, v), axis=x.ndim - 1)

        return V

    # Points where to evaluate the functions (ideally those should be the
    # zeros of the orthogonal Polynomial
    def nodes(self, n):
        if n > 0:
            return self._rec(n)
        return [None] * 4

    def _rec(self, n):
        r"""
        Nodes for Legendre basis based on the Greg von Winckel algorithm.
        compute the quadrature points, quadrature weights, barycentric weights
        and the angles for the Legendre basis.

        Parameters
        ----------
        n : int
            The number of nodes.

        Returns
        -------
        Tuple
            the quadrature points, quadrature weights, tricentennial weights
            and the angle

        """

        dom = self.domain
        if n == 1:
            # Nodes, quadrature Weights, tricentennial weights, angles
            x, w, b, a = sum(dom) / 2, np.diff(dom).item(), 1, np.pi / 2
            return x, w, b, a

        n = n - 1
        N1 = n + 1
        N2 = n + 2
        xu = np.linspace(-1, 1, N1, dtype=self.dtype)

        # Inicial guess
        L = np.zeros((N1, N2), self.dtype)
        if L.size == 0:
            return L

        y = np.cos((2 * np.arange(n + 1, dtype=self.dtype) + 1) * np.pi / (2 * n + 2)) + (
            0.27 / N1
        ) * np.sin(np.pi * xu * n / N2)

        # Legendre-Gauss Vandermonde Matrix

        # Compute the zeros of the N+1 Legendre Polynomial using the recursion
        # relation and the Newton-Raphson method
        y0 = 2

        # Iterate until new points are uniformly within epsilon of old points
        while np.max(np.abs(y - y0)) > np.spacing(1):
            L[:, 0] = 1
            L[:, 1] = y

            for k in range(2, N1 + 1):
                L[:, k] = ((2 * k - 1) * y * L[:, k - 1] - (k - 1) * L[:, k - 2]) / k

            # Derivatives of L
            Ld = N2 * (L[:, N1 - 1] - y * L[:, N2 - 1]) / (1 - y**2)

            # Update
            y0 = y

            # Newton-Raphson iteration
            y = y0 - L[:, N2 - 1] / Ld

        # Shift from [-1, 1] to [a, b]

        x = np.sort((sum(dom) + np.diff(dom) * y) / 2)

        w = np.diff(dom).item() / ((1 - y**2) * Ld**2) * (N2 / N1) ** 2
        v = 1 / abs(Ld)
        v = v / max(v)
        v[1::2] = -v[1::2]

        return (x, w, v, np.arccos(np.sort(y)))

    def _gw_alg(self, n):
        r"""
        Based in Golub and Welsh

        Parameters
        ----------
        n : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        Tuple
            The quadrature points, quadrature weights, barycentric weights
            and the angle

        """

        dom = self.domain
        if n == 1:
            # Nodes, quadrature Weights, barycentric weights, angles
            x, w, b, a = sum(dom) / 2, np.diff(dom).item(), 1, np.pi / 2
            return x, w, b, a

        ni = np.arange(1, n, dtype=self.dtype)
        # Tree term recurrence relation for the coefficients
        beta = ni / np.sqrt(((2 * ni) ** 2 - 1))
        # Jacoby matrix
        J = np.diag(beta, -1) + np.diag(beta, 1)
        # The nodes are the eigenvalues of J
        x, vects = eig(J)
        # Indexes of eigenvalues sorted
        ix = np.argsort(x)
        x = x[ix]
        w = 2 * vects[0, ix] ** 2
        b = np.sqrt(1 - x**2) * abs(vects[0, ix])

        # Enforce symmetry
        si = np.r_[0 : n // 2]
        x = x[si]
        w = w[si]
        b_m = b[n // 2]
        b = b[si]

        if n % 2:
            # n is odd
            x = np.r_[x, 0, -x[-1::-1]]
            w = np.r_[w, 2 - sum(2 * w), w[-1::-1]]
            b = np.r_[b, b_m, b[-1::-1]]

        else:
            # n is even
            x = np.r_[x, -x[-1::-1]]
            w = np.r_[w, w[-1::-1]]
            b = np.r_[b, b[-1::-1]]

        # Normalize the barycentric weights
        b = abs(b)
        b = b / max(b)
        b[1::2] = -b[1::2]

        # The angles
        a = np.arccos(x)

        # Shift and scale the nodes from [-1,1] to [a,b]
        x = (sum(dom) + np.diff(dom) * x) / 2
        # Scale the quadrature Weights
        w = np.diff(dom) * w / 2

        return x, w, b, a

    def productv2(self, p, q):
        r"""
        Does the product of two orthogonal Polynomials where ``p`` and ``q`` are the
        coefficients of those Polynomials in the ``self`` basis.

        Parameters
        ----------
        p : array_like
            The coefficients of the first polynomial with shape (m, ).
        q : array_like
            The coefficients of the second Polynomial with shape(n, )

        Returns
        -------
        ndarray
            The coefficients of the Polynomial which are the product of the po-
            lynomials with coefficients ``p`` and ``q``respectively.

        Notes
        -----
        Compute the coefficients of product p*q, where
        p and q are both the vector of coefficients in orthogonal basis, i.e.

        .. math::
            P(x) = & p_0P_0(x) + ... + p_m*P_m(x),\\
            Q(t) = & q_0P_0(x) + ... + q_nP_n(x).

        Then, the result will be the vector of coefficients y such that

        .. math::
            P(x)Q(x) = f_0*P_0(x) + ... + f_{m+n}P_{m+n}(x).

        Examples
        --------
        Using the basis ``ChebyshevU`` :

        >>> p = np.arange(4)
        >>> q = np.arange(3)
        >>> p
        array([0, 1, 2, 3])
        >>> q
        array([0, 1, 2])
        >>> b = polynomial.ChebyshevU()
        >>> b.productv2(p,q)
        array([ 5., 10.,  8., 10.,  7.,  6.])

        Using the basis ``LegendreP`` :

        >>> b = polynomial.LegendreP()
        >>> b.productv2(p,q)
        array([1.133, 3.143, 3.095, 4.   , 3.771, 2.857])
        """

        m = np.min([len(p), len(q)]) - 1
        n = np.max([len(p), len(q)]) - 1
        p = np.concatenate((p, np.zeros(n, dtype=self.dtype)))
        p = p[: n + 1]
        q = np.concatenate((q, np.zeros(n, dtype=self.dtype)))
        q = q[: n + 1]
        a = self.alpha(np.arange(2 * n + 1, dtype=self.dtype)) + np.zeros(
            2 * n + 1, dtype=self.dtype
        )
        b = self.beta(np.arange(2 * n + 1, dtype=self.dtype)) + np.zeros(
            2 * n + 1, dtype=self.dtype
        )
        c = self.gamma(np.arange(2 * n + 1, dtype=self.dtype)) + np.zeros(
            2 * n + 1, dtype=self.dtype
        )
        L = np.zeros((2 * n + 1, 2 * n + 1, 2 * n + 1), dtype=self.dtype)
        for k in range(2 * n + 1):
            L[k, 0, k] = 1
            L[0, k, k] = 1
            L[k, 1, k] = (b[k] - b[0]) / a[0]
            L[1, k, k] = L[k, 1, k]

        for k in range(2 * n):
            L[k + 1, 1, k] = c[k + 1] / a[0]
            L[1, k + 1, k] = L[k + 1, 1, k]
            L[k, 1, k + 1] = a[k] / a[0]
            L[1, k, k + 1] = L[k, 1, k + 1]

        for j in range(1, 2 * n):
            for i in range(j + 1, 2 * n):
                L[i, j + 1, :] = (
                    c[i] * L[i - 1, j, :]
                    - c[j] * L[i, j - 1, :]
                    + (b[i] - b[j]) * L[i, j, :]
                    + a[i] * L[i + 1, j, :]
                ) / a[j]

            for i in range(j + 2, 2 * n):
                L[j + 1, i, :] = L[i, j + 1, :]

        # y = p*q
        y = np.zeros(2 * n + 1)

        for i in range(n + 1):
            # P_i *P_i
            for k in range(2 * i + 1):
                y[k] = y[k] + p[i] * q[i] * L[i, i, k]
            for j in range(i):  # P_i*P_{j}
                for k in range(i + j + 1):
                    y[k] = y[k] + (p[i] * q[j] + p[j] * q[i]) * L[i, j, k]

        return y[: m + n + 1]

    def _prodx(self, p):
        r"""
        Multiply the polynomial that have p as coefficients by x and return
        the coefficients of the product of the polynomial by x in the [-1,1]
        domain

        Parameters
        ----------
        p : array_like
            The coefficients of the polynomial multiplied by x

        Returns
        -------
        array_like
            The coefficients of a series in this basis multiplied by x.

        """
        # this is needed when you have more than one row
        fi = 0 if p.ndim == 1 else np.zeros((len(p), 1), dtype=self.dtype)
        p = np.r_["-1", p, fi]
        n = p.shape[-1]

        e0 = np.arange(n, dtype=self.dtype)

        M = spdiags(
            [
                self.alpha(e0) + 0 * e0,
                self.beta(e0) + 0 * e0,
                self.gamma(e0) + 0 * e0,
            ],
            [-1, 0, 1],
            n,
            n,
        )

        return (M @ p.T).T

    def _ultraProduct(self, p, q, alpha_):
        # Check if we only n rows x n rows, 1 row x n rows, or n rows x 1 row
        # inputs
        if p.ndim > 2 or q.ndim > 2:
            raise ValueError("p and q must have at most 2 dimensions.")

        # Shape of the arrays
        shp = p.shape
        shq = q.shape
        if p.ndim == q.ndim == 2:
            if shq[0] > 1 and shq[0] > 1 and shq[0] != shq[0]:
                raise ValueError(
                    "You can only add two array of coefficients "
                    "when one of them have one row or when they "
                    "have the same number of rows"
                )

        # Product by a constant
        if shp[-1] == 1:
            return p * q
        elif shq[-1] == 1:
            return q * p

        # Other cases
        if shp[-1] > shq[-1]:
            c = q.copy()
            xs = p.copy()
        else:
            c = p.copy()
            xs = q.copy()

        if c.shape[-1] == 2:
            c0 = c[..., :1] * xs
            c1 = c[..., 1:2] * xs
        else:
            nd = c.shape[-1]
            c0 = c[..., -2:-1] * xs
            c1 = c[..., -1:] * xs

            for i in range(3, c.shape[-1] + 1):
                tmp = c0
                nd -= 1
                c0 = self.sub(c[..., -i : -i + 1] * xs, c1 * ((nd + 2 * alpha_ - 2) / nd))
                c1 = self.add(tmp, self._prodx(c1) * (2 * (nd - 1 + alpha_) / nd))

        return self.add(c0, self._prodx(c1) * (2 * alpha_))

    def _chebThreeTermsRecurrence(self, p, q):
        # Check if we only n rows x n rows, 1 row x n rows, or n rows x 1 row
        # inputs
        if p.ndim > 2 or q.ndim > 2:
            raise ValueError("p and q must have at most 2 dimensions.")

        # Shape of the arrays
        shp = p.shape
        shq = q.shape
        if p.ndim == q.ndim == 2:
            if shq[0] > 1 and shq[0] > 1 and shq[0] != shq[0]:
                raise ValueError(
                    "You can only add two array of coefficients "
                    "when one of them have one row or when they "
                    "have the same number of rows"
                )

        # Product by a constant
        if shp[-1] == 1:
            return p * q
        elif shq[-1] == 1:
            return q * p

        # Other cases
        if shp[-1] > shq[-1]:
            c = q.copy()
            xs = p.copy()
        else:
            c = p.copy()
            xs = q.copy()

        if c.shape[-1] == 2:
            c0 = c[..., :1] * xs
            c1 = c[..., 1:2] * xs
        else:
            c0 = c[..., -2:-1] * xs
            c1 = c[..., -1:] * xs

            for i in range(3, c.shape[-1] + 1):
                tmp = c0
                c0 = self.sub(c[..., -i : -i + 1] * xs, c1)
                c1 = self.add(tmp, self._prodx(c1) * 2)

        return c0, c1

    def add(self, c1, c2):
        r"""
        Add the coefficients ``c1`` and ``c2``.

        Parameters
        ----------
        c1 : ndarray
            A one dimensional or bidimensional array.
        c2 : ndarray
            A one dimensional or bidimensional array.

        Raises
        ------
        ValueError
            When ``c1`` and ``c2`` are bidimensional arrays with more than one
            row and don't have the same number of rows.

        Returns
        -------
        TYPE
            an array of coefficients which are the result of the sum of ``c1``
            and ``c2``.

        """
        if c1.ndim == 1 and c2.ndim == 1:
            m, n = len(c1), len(c2)
            if m >= n:
                res = c1.copy().astype(self.dtype)
                res[:n] += c2
                return res
            else:
                return self.add(c2, c1)

        if c1.ndim == 1:
            c1 = c1.reshape(1, -1).copy()

        if c2.ndim == 1:
            c2 = c2.reshape(1, -1).copy()

        sh1 = c1.shape
        sh2 = c2.shape
        if len(sh1) == len(sh1) == 2:
            if sh1[0] > 1 and sh2[0] > 1 and sh1[0] != sh2[0]:
                raise ValueError(
                    "You can only add two array of coefficients "
                    "when one of them have one row or when they "
                    "have the same number of rows"
                )

            if sh1[1] >= sh2[1]:
                res = np.zeros((max(sh1[0], sh2[0]), max(sh1[1], sh2[1])), dtype=self.dtype)
                res[...] = c1
                res[..., : sh2[1]] += c2
                return res

            else:
                return self.add(c2, c1)
        else:
            raise ValueError("Coefficients must have at most dimension 2.")

    def sub(self, c1, c2):
        r"""
        subtract the coefficients ``c1`` and ``c2``.

        Parameters
        ----------
        c1 : ndarray
            A one dimensional or bidimensional array.
        c2 : ndarray
            A one dimensional or bidimensional array.

        Raises
        ------
        ValueError
            When ``c1`` and ``c2`` are bidimensional arrays with more than one
            row and don't have the same number of rows.

        Returns
        -------
        TYPE
            an array of coefficients which are the result of the subtraction of
            ``c1`` and ``c2``.

        """

        return self.add(c1, -c2)

    def interp1f(self, fx, n, poly=lambda x: x):
        r"""
        Compute the coefficients of the Polynomial which are the approximation
        of fx(poly) in the basis ``self`` with ``n`` therms.

        Parameters
        ----------
        fx : TYPE
            DESCRIPTION.
        poly : TYPE, optional
            DESCRIPTION. The default is None.
        n : TYPE, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        TypeError
            DESCRIPTION.
        ValueError
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        """
        interp1f - Orthogonal Polynomial interpolation.
           f = interp1f(basis, fx) interpolates an expression

        inputs:
           self  = tau orthogonal basis (polynomial.bases.T3Basis object).
           fx = function to interpolate (function handle).

        inputs(optional):
           poly  = Polynomial where to evaluate a composed function fx(poly(..))
           n     = polynomial order to approximate

        output:
           f     = interpolation coefficients (double vector).
           esys  = error in the linear system (double vector).
           eeval = (max.) error in the evaluation (double scalar).
           edom  = error in the full domain (double vector).
        """

        if not callable(fx):
            raise TypeError("tautoolbox: the 1st argument must be callable in one variable.")

        if not callable(poly):
            raise TypeError("tautoolbox: poly must be a callable with one argument.")

        # The abscissas for the interpolations
        nods, *_ = self.nodes(n)

        b = fx(poly(nods)).T

        if any(np.isnan(b)) or any(np.isinf(b)):
            raise ValueError("Encountered inf or NaN when evaluating.")

        if self.name == "ChebyshevT":
            return (self.vals1tocoeffs(b.T),)
        if self.name == "ChebyshevU":
            return (chebt2kind(self.vals2tocoeffs(b.T)),)

        A = self.vander(nods, n=n)
        f = np.linalg.solve(A, b)

        esys = np.max(np.abs(A @ f - b).T, axis=-1)

        return f.T, esys

    def to_power_coeff(self, coeff):
        """
        Returns an array_like object where the entries are the coefficients of
        each row in the power basis.
        """

        n = coeff.shape[-1]
        return coeff @ self.orth2powmatrix(n).T

    def from_power_coeff(self, coeff):
        """
        Returns an array_like object where the entries are the
        coefficients in the given basis converted from the power
        basis.
        """

        n = coeff.shape[-1]
        return coeff @ self.pow2orthmatrix(n).T

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        coeff = np.array(coeff)
        n = coeff.shape[-1]
        result = np.r_["-1", coeff, np.zeros_like(coeff[..., :1])]
        result = result @ self.matrixO(n + 1).T
        return self(result, bounds[1]) - self(result, bounds[0])

    @abstractmethod
    def to_chebyshevT_coeff(self, coeff):
        """
        Returns an array_like object where the entries are the coefficients of
        each row in the ChebyshevT basis.
        """

    @abstractmethod
    def from_chebyshevT_coeff(self, coeff):
        """
        Returns an array_like object where the entries are the coefficients of
        each row in given basis converted from the ChebyshevT basis.
        """

    @staticmethod
    def idlt(f=None, dtype=np.float64):
        r"""
        Returns the inverse discrete Legendre transform.


        Parameters
        ----------
        f : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """

        if f is None:
            return np.zeros(0)

        if np.isscalar(f):
            f = np.array([f])

        N = f.shape[-1]
        if N == 1:
            return 1 + 0 * f
        x, w, *_ = LegendreP().nodes(N)
        c = w * f

        pm1 = 1 + 0 * x
        p = x
        v = np.zeros_like(c)
        v[..., 0] = np.sum(c, axis=-1)
        v[..., 1] = x @ c.T

        for i in range(N - 2):
            pp1 = (2 - 1 / (i + 2)) * (p * x) - (1 - 1 / (i + 2)) * pm1
            pm1 = p
            p = pp1
            v[..., i + 2] = p @ c.T

        return (np.arange(N, dtype=dtype) + 0.5) * v

    @staticmethod
    def idct(f):
        """
        Inverse Fast Chebyshev Transform
        Discrete Chebyshev Transform Coefficients.
        Function values evaluated at Chebyshev Gauss Lobatto nodes
        with nodes ordered increasingly x_i=[-1,...,1}
        for i=1,2...,N

        Based in  Allan P. Engsig-Karup, apek@imm.dtu.dk.

        Parameters
        ----------
        f : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        N = f.size
        u = fft(
            np.r_[
                f[0],
                np.r_[f[1 : N - 1], f[N - 1] * 2, f[N - 2 : 0 : -1]] * 0.5,
            ]
        )
        # Reverse order due to fft
        u = u[N - 1 :: -1]
        return u.real

    def interp_from_values(self, values, abscissas=None, **kwargs):
        n = values.shape[-1]
        if abscissas is None:
            abscissas, *_ = ChebyshevU(domain=self.domain).nodes(n)
        A = self.vander(abscissas, n=n)

        return np.linalg.solve(A, values.T).T

    @staticmethod
    def trigeval(c, x, domain=None):
        if domain is not None:
            x = (2 * x - sum(domain)) / np.diff(domain).item()
        N = c.shape[-1]
        nrows = 1 if c.ndim == 1 else c.shape[0]
        n = ((N - 1) / 2).__ceil__()
        c = c[..., n::-1]
        a = c.real
        b = c.imag
        b.flags["WRITEABLE"] = True

        e = np.ones(x.size)
        if N % 2 == 0:
            a[..., n] = a[..., n] / 2
            b[..., n] = 0

        if N == 1:
            return c * e

        u = np.tile(np.cos(np.pi * x), (nrows, 1))
        v = np.tile(np.sin(np.pi * x), (nrows, 1))

        co = a[..., n : n + 1] * e
        si = b[..., n : n + 1] * e

        for i in range(n - 1, 0, -1):
            temp = a[..., i : i + 1] * e + u * co + v * si

            si = b[..., i : i + 1] * e + u * si - v * co
            co = temp

        res = a[..., :1] * e + 2 * (u * co + v * si)

        if nrows == 1:
            res = res.reshape(x.shape)
        return res

    @staticmethod
    def vals1tocoeffs(vals, dtype=np.float64):
        r"""
        This methods give the coefficients of the polynomial expansion in
        the Chebyshev of the first kind basis where the coefficients are given
        by interpolation  over the Nodes of Chebyshev of the first kind poly-
        nomials

        Parameters
        ----------
        vals : array_like
            A vector (m,) or a matrix (n,m) where the values in each row is the
            interpolate separately over the nodes.

        Returns
        -------
        coeffs : array_like
            A vector or matrix where each row represents the coefficients of
            a polynomial.

        Notes
        -----
        In input is an array  :math:`C^{n\times n}'  where n is the number of
        rows such that:
            .. math::
                P_i(x) = C_{i,0}T_0(x) +\cdots + C_{i,m-1}T_{m-1}(x),
                i=1,\cdots, n


        """
        n = vals.shape[-1]
        isEven = np.max(abs(vals - np.flip(vals, axis=-1)), axis=-1) == 0
        isOdd = np.max(abs(vals + np.flip(vals, axis=-1)), axis=-1) == 0
        w = 2 * np.exp(1j * np.arange(n, dtype=dtype) * np.pi / (2 * n))
        tmp = np.r_["-1", vals[..., ::-1], vals]
        coeffs = ifft(tmp)
        # truncate, flip
        coeffs = w * coeffs[..., :n]

        # scale the coefficients
        coeffs[..., 0] = coeffs[..., 0] / 2
        if np.all(np.isreal(vals)):
            coeffs = coeffs.real
        elif np.all(np.isreal(1j * vals)):
            coeffs = 1j * coeffs.imag

        # adjust for dosimetry
        coeffs[isEven, 1::2] = 0
        coeffs[isOdd, ::2] = 0

        return coeffs

    @staticmethod
    def vals2tocoeffs(vals):
        r"""
        This methods give the coefficients of the polynomial expansion in
        the Chebyshev of the first kind basis where the coefficients are given
        by interpolation over the Nodes of Chebyshev of the second kind poly-
        nomials

        Parameters
        ----------
        vals : array_like
            A vector (m,) or a matrix (n,m) where the values in each row is the
            interpolate separately over the nodes.

        Returns
        -------
        coeffs : array_like
            A vector or matrix where each row represents the coefficients of
            a polynomial.

        Notes
        -----
        In input is an array  :math:`C^{n\times n}'  where n is the number of
        rows such that:
            .. math::
                P_i(x) = C_{i,0}T_0(x) +\cdots + C_{i,m-1}T_{m-1}(x),
                i=1,\cdots, n


        """
        n = vals.shape[-1]

        # Check for dosimetry
        isEven = np.max(abs(vals - np.flip(vals, axis=-1)), axis=-1) == 0
        isOdd = np.max(abs(vals + np.flip(vals, axis=-1)), axis=-1) == 0

        # Mirror the values
        tmp = np.r_["-1", vals[..., :0:-1], vals[..., : n - 1]]

        if np.all(np.isreal(vals)):
            # The case when vals are real
            coef = ifft(tmp).real
        elif np.all(np.isreal(1j * vals)):
            # For the case when vals are imaginary
            coef = 1j * ifft(tmp.imag).real
        else:
            # General Case
            coef = ifft(tmp)

        # Truncate the coefficients
        coef = coef[..., :n]

        # Scale the inner coefficients
        coef[..., 1 : n - 1] *= 2

        # Adjust the coefficients for symmetry
        coef[isEven, 1::2] = 0
        coef[isOdd, ::2] = 0

        return coef

    def copy(self):
        return deepcopy(self)

    def __repr__(self):
        params = [f"{par}={self.params[par]}" for par in self.params.keys()]
        params = ", " + ", ".join(params) if params else ""
        return f"{self.__class__.__name__}(domain={self.domain!r}{params})"

    def fractionalIntegral(self, c, mu, b=0):
        r"""
        Returns the smooth part (polynomial coefficients) of a
        Fractional Polynomial for the Fractional Integral in the
        given basis.

        .. math::
            I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

        Parameters
        ----------
        c : array_like
            The coefficients of a polynomial in the given basis.
        mu : scalar
            A scalar between ]0,1[ corresponding to the order of the fractional integral.

        Returns
        -------
        array_like
            The smooth part of the fractional integral of order `mu` coefficients.
        """


class BesselY(T3Basis):
    r"""
    A class used to represent a Bessel polynomial basis in one variable.
    The Bessel polynomials are an orthogonal sequence of polynomials.
    The definition favored by mathematicians is given by the series:
    :math:`y_{n}(x)=\sum _{k=0}^{n}{\frac {(n+k)!}{(n-k)!k!}}\,\left({\frac {x}{2}}\right)^{k}.`

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "BesselY"

    def alpha(self, n):
        return 1 / (2 * n + 1)

    def beta(self, n):
        return -1 * (n == 0)

    def gamma(self, n):
        return -1 / (2 * n + 1)

    def eta(self, i, j):
        return (i - j + 1) * (i + j) * (i + 1 / 2) * (-1) ** (-1 + i + j)

    def theta(self, n):
        return np.array(
            [
                1
                / (
                    np.arange(1, n + 1, dtype=self.dtype)
                    * np.arange(1, 2 * n, 2, dtype=self.dtype)
                ),
                np.concatenate(
                    (
                        [0],
                        1
                        / (
                            np.arange(1, n, dtype=self.dtype)
                            * np.arange(2, n + 1, dtype=self.dtype)
                        ),
                    )
                ),
                np.concatenate(
                    (
                        [0] * 2,
                        1
                        / (
                            np.arange(2, n, dtype=self.dtype)
                            * np.arange(5, 2 * n, 2, dtype=self.dtype)
                        ),
                    )
                ),
            ]
        )


class ChebyshevT(T3Basis):
    r"""
    A class used to represent a Chebyshev polynomial basis of the first kind in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ChebyshevT"

    def alpha(self, n):
        return 1 / 2 + 1 / 2 * (n == 0)

    def beta(self, n):
        return 0

    def gamma(self, n):
        return 1 / 2

    def eta(self, i, j):
        return 2 * ((i + j - 1) % 2) * (j - 1) / (1 + (i == 0))

    def theta(self, n):
        return np.array(
            [
                np.concatenate(([1], 1 / np.arange(4, 2 * n + 1, 2, dtype=self.dtype))),
                np.zeros(n, dtype=self.dtype),
                np.concatenate(
                    (
                        np.zeros(2, dtype=self.dtype),
                        -1 / np.arange(2, 2 * n - 3, 2, dtype=self.dtype),
                    )
                ),
            ]
        )

    def nodes(self, n):
        dom = self.domain
        if n > 0:
            if n == 1:
                x = 0
                w = 2
                v = 1
                a = 0.5 * np.pi
            else:
                # Computing the quadrature points
                x = np.cos((np.arange(n, 0, -1, dtype=self.dtype) - 1 / 2) * np.pi / n)
                # Computing the quadrature weight
                m = 2 / np.r_[1, 1 - np.r_[2:n:2] ** 2]

                # Mirror the vector for use of ifft
                # n is odd
                if n % 2:
                    c = np.r_[m, -m[(n - 1) // 2 : 0 : -1]]
                else:
                    c = np.r_[m, 0, -m[n // 2 - 1 : 0 : -1]]

                c = c * np.exp(1j * np.r_[0:n] * np.pi / n)
                w = np.fft.ifft(c).real

                # Computing the quadrature points
                l = np.r_[0:n]
                m = np.minimum(l, n - l)
                r = 2 / (1 - 4 * m**2)
                s = np.sign(n / 2 - l)
                v = s * r * np.exp(1j * np.pi / n * l)
                w = ifft(v).real

                # Computing  the barycentric weights
                v = np.sin((np.r_[n - 1 : -1 : -1] + 0.5) * np.pi / n)
                v[: n // 2] = v[: n - n // 2 - 1 : -1]
                v[-2::-2] = -v[-2::-2]

                # The angles
                a = np.r_[n - 0.5 : -0.5 : -1] * np.pi / n

            # Scaling and shifting
            x = (sum(dom) + np.diff(dom).item() * x) / 2
            w = (np.diff(dom).item() / 2) * w
            v = v / np.max(abs(v))

            return x, w, v, a

        return [None] * 4

    def _gw_alg(self, n):
        dom = self.domain
        # Tree term recurrence relation for the coefficients
        beta = np.sqrt(np.r_[1 / 2, [1 / 4] * (n - 2)])
        # Jacoby matrix
        J = np.diag(beta, -1) + np.diag(beta, 1)
        # The nodes are the eigenvalues of J
        x, vects = eig(J)
        # Indexes of eigenvalues sorted

        w = 2 * vects[0, :] ** 2
        b = np.sqrt(1 - x**2) * abs(vects[0, :])

        # Enforce symmetry
        si = np.r_[0 : n // 2]
        x = x[si]
        w = w[si]
        b_m = b[n // 2]
        b = b[si]

        if n % 2:
            # n is odd
            x = np.r_[x, 0, -x[-1::-1]]
            w = np.r_[w, 2 - sum(2 * w), w[-1::-1]]
            b = np.r_[b, b_m, b[-1::-1]]

        else:
            # n is even
            x = np.r_[x, -x[-1::-1]]
            w = np.r_[w, w[-1::-1]]
            b = np.r_[b, b[-1::-1]]

        # Normalize the barycentric weights
        b = abs(b)
        b = b / max(b)
        b[1::2] = -b[1::2]

        # The angles
        a = np.arccos(x)

        # Shift and scale the nodes from [-1,1] to [a,b]
        x = (sum(dom) + np.diff(dom) * x) / 2
        # Scale the quadrature Weights
        w = np.diff(dom) * w / 2

        return x, w, b, a

    def product(self, p, q):
        r"""
        Does the product of two orthogonal Polynomials where ``p`` and ``q`` are the
        coefficients of those Polynomials in the Chebyshev of the first kind
        basis.

        Parameters
        ----------
        p : array_like
            The coefficients of the first polynomial with shape (m, ).
        q : array_like
            The coefficients of the second Polynomial with shape(n, )

        Returns
        -------
        ndarray
            The coefficients of the Polynomial which are the product of the po-
            lynomials with coefficients ``p`` and ``q``respectively.

        Notes
        -----
        Compute the coefficients of product p*q, where
        p and q are both the vector of coefficients in orthogonal basis, i.e.

        .. math::
            P(x) = & p_0P_0(x) + ... + p_m*P_m(x),\\
            Q(t) = & q_0P_0(x) + ... + q_nP_n(x).

        Then, the result will be the vector of coefficients y such that

        .. math::
            P(x)Q(x) = f_0*P_0(x) + ... + f_{m+n}P_{m+n}(x).

        Examples
        --------

        """
        if len(p) == 1:
            return p[0] * q
        if len(q) == 1:
            return q[0] * p

        m = min([len(p), len(q)]) - 1
        n = max([len(p), len(q)]) - 1
        p = np.concatenate((p, np.zeros(n)))
        p = p[: n + 1]
        q = np.concatenate((q, np.zeros(n)))
        q = q[: n + 1]

        # y = p*q
        f = np.zeros(2 * n + 1)
        f[0] = p[0] * q[0] + p[1 : n + 1] @ q[1 : n + 1] / 2

        for k in range(n):
            # y_k
            f[k + 1] = (
                p[: n - k] @ q[k + 1 : n + 1]
                + p[k + 1 : n + 1] @ q[: n - k]
                + p[: k // 2 + 1] @ q[k + 1 : k - k // 2 : -1]
                + p[k + 1 : k - k // 2 : -1] @ q[: k // 2 + 1]
            ) / 2

        for k in range(n, 2 * n - 1):
            # y_k

            f[k + 1] = (
                p[k - n + 1 : k // 2 + 1] @ q[n : k - k // 2 : -1]
                + p[n : k - k // 2 : -1] @ q[k - n + 1 : k // 2 + 1]
            ) / 2

        f[2 : 2 * n - 1 : 2] = f[2 : 2 * n - 1 : 2] + p[1:n] * q[1:n] / 2
        f[2 * n] = p[n] * q[n] / 2
        f = f[: m + n + 1]

        return f

    def productv3(self, p, q):
        r"""
        Does the product for the basis Chebyshev of the first kind
        ``ChebyshevT`` . Here ``p`` and ``q`` are the coefficients of two  poly-
        nomials in this basis with the same domain.

        Parameters
        ----------
        p : array_like
            The coefficients of the first polynomial with shape (m, ).
        q : array_like
            The coefficients of the second Polynomial with shape(n, )

        Returns
        -------
        ndarray
            The coefficients of the Polynomial which are the product of the po-
            lynomials with coefficients ``p`` and ``q``respectively.

        Notes
        -----
        Compute the coefficients of product p*q, where
        p and q are both the vector of coefficients in orthogonal basis, i.e.

        .. math::
            P(x) = & p_0P_0(x) + ... + p_m*P_m(x),\\
            Q(t) = & q_0P_0(x) + ... + q_nP_n(x).

        Then, the result will be the vector of coefficients y such that

        .. math::
            P(x)Q(x) = f_0*P_0(x) + ... + f_{m+n}P_{m+n}(x).

        Examples
        --------
        Using the basis ``ChebyshevU`` :
        """
        lp = 1 if p.ndim == 1 else len(p)
        lq = 1 if q.ndim == 1 else len(q)

        if lp > lq:
            return self.productv2(q, p)

        vector = False
        if p.ndim == 1 and q.ndim == 1:
            vector = True
            p = p.reshape(1, -1)
            q = q.reshape(1, -1)
        elif p.ndim == 1:
            p = p.reshape(1, -1)
        elif q.ndim == 1:
            q = q.reshape(1, -1)

        if lp > 1 and lq > 1 and lp != lq:
            raise ValueError(
                "You can only multiply an matrix with the same "
                "Numbers of rows or one with one row by another "
                "with one or more rows"
            )

        l = max(lp, lq)
        if p.shape[1] == 1:
            res = p[:, 0] * q
            if vector:
                return res[0]
            return res
        if q.shape[1] == 1:
            res = q[:, 0] * p

            if vector:
                return res[0]
            return res

        m = min(p.shape[1], q.shape[1]) - 1
        n = max(p.shape[1], q.shape[1]) - 1

        p = np.c_[p, np.zeros((lp, n + 1 - p.shape[1]))]

        q = np.c_[q, np.zeros((lq, n + 1 - q.shape[1]))]

        f = np.zeros((l, 2 * n + 1))

        # Case at least one Polynomial have only one column
        if lp == 1:
            f[:, 0] = p[:, 0] * q[:, 0] + p[:, 1 : n + 1] @ q[:, 1 : n + 1].T / 2

            for k in range(n):
                # y_k
                f[:, k + 1] = (
                    p[:, : n - k] @ q[:, k + 1 : n + 1].T
                    + p[:, k + 1 : n + 1] @ q[:, : n - k].T
                    + p[:, : k // 2 + 1] @ q[:, k + 1 : k - k // 2 : -1].T
                    + p[:, k + 1 : k - k // 2 : -1] @ q[:, : k // 2 + 1].T
                ) / 2

            for k in range(n, 2 * n - 1):
                # y_k
                f[:, k + 1] = (
                    p[:, k - n + 1 : k // 2 + 1] @ q[:, n : k - k // 2 : -1].T
                    + p[:, n : k - k // 2 : -1] @ q[:, k - n + 1 : k // 2 + 1].T
                ) / 2

        # The case where all Polynomials the same number of columns and the
        # number of columns are more than one
        else:
            f[:, 0] = (
                p[:, 0] * q[:, 0] + np.einsum("ij,ij->i", p[:, 1 : n + 1], q[:, 1 : n + 1]) / 2
            )

            for k in range(n):
                # y_k
                f[:, k + 1] = (
                    np.einsum("ij,ij->i", p[:, : n - k], q[:, k + 1 : n + 1])
                    + np.einsum("ij,ij->i", p[:, k + 1 : n + 1], q[:, : n - k])
                    + np.einsum(
                        "ij,ij->i",
                        p[:, : k // 2 + 1],
                        q[:, k + 1 : k - k // 2 : -1],
                    )
                    + np.einsum(
                        "ij,ij->i",
                        p[:, k + 1 : k - k // 2 : -1],
                        q[:, : k // 2 + 1],
                    )
                ) / 2

            for k in range(n, 2 * n - 1):
                # y_k
                f[:, k + 1] = (
                    np.einsum(
                        "ij,ij->i",
                        p[:, k - n + 1 : k // 2 + 1],
                        q[:, n : k - k // 2 : -1],
                    )
                    + np.einsum(
                        "ij,ij->i",
                        p[:, n : k - k // 2 : -1],
                        q[:, k - n + 1 : k // 2 + 1],
                    )
                ) / 2

        f[:, 2 : 2 * n - 1 : 2] = f[:, 2 : 2 * n - 1 : 2] + p[:, 1:n] * q[:, 1:n] / 2
        f[:, 2 * n] = p[:, n] * q[:, n] / 2

        if vector:
            return f[0, : m + n + 1]

        return f[:, : m + n + 1]

    def productv2(self, p, q):
        r"""
        Does the product for the basis Chebyshev of the first kind
        ``ChebyshevU`` . Here ``p`` and ``q`` are the coefficients of two  poly-
        nomials in this basis with the same domain.

        Parameters
        ----------
        p : array_like
            The coefficients of the first polynomial with shape (m, ).
        q : array_like
            The coefficients of the second Polynomial with shape(n, )

        Returns
        -------
        ndarray
            The coefficients of the Polynomial which are the product of the po-
            lynomials with coefficients ``p`` and ``q``respectively.

        Notes
        -----
        Compute the coefficients of product p*q, where
        p and q are both the vector of coefficients in orthogonal basis, i.e.

        .. math::
            P(x) = & p_0P_0(x) + ... + p_m*P_m(x),\\
            Q(t) = & q_0P_0(x) + ... + q_nP_n(x).

        Then, the result will be the vector of coefficients y such that

        .. math::
            P(x)Q(x) = f_0*P_0(x) + ... + f_{m+n}P_{m+n}(x).

        Examples
        --------
        Using the basis ``ChebyshevU`` :
        """
        lp = 1 if p.ndim == 1 else len(p)
        lq = 1 if q.ndim == 1 else len(q)

        if lp > lq:
            return self.productv2(q, p)

        if lp > 1 and lq > 1 and lp != lq:
            raise ValueError(
                "You can only multiply an matrix with the same "
                "Numbers of rows or one with one row by another "
                "with one or more rows"
            )

        m = p.shape[-1]
        n = q.shape[-1]
        p_pad = [(0, 0)] * p.ndim
        p_pad[-1] = (0, n - 1)
        q_pad = [(0, 0)] * q.ndim
        q_pad[-1] = (0, m - 1)

        p = np.pad(p, p_pad, mode="constant", constant_values=0)
        q = np.pad(q, q_pad, mode="constant", constant_values=0)

        t = np.concatenate((2 * p[..., :1], p[..., 1:]), axis=-1)
        x = np.concatenate((2 * q[..., :1], q[..., 1:]), axis=-1)

        tp = fft(np.concatenate((t, t[..., :0:-1]), axis=-1))
        xp = fft(np.concatenate((x, x[..., :0:-1]), axis=-1))

        result = ifft(tp * xp).real

        result = 0.25 * np.concatenate(
            (result[..., :1], result[..., 1:] + result[..., :0:-1]), axis=-1
        )
        return result[..., : m + n - 1]

    def companion(self, c):
        """Return the scaled companion matrix of c.
        The basis Polynomials are scaled so that the companion matrix is
        symmetric when `c` is a Chebyshev basis Polynomial. This provides
        better eigenvalue estimates than the unscaled case and for basis
        Polynomials the eigenvalues are guaranteed to be real if
        `numpy.linalg.eigvalsh` is used to obtain them.

        Parameters
        ----------
        c : array_like
            An 1-D array of Chebyshev coefficients ordered from the low to high
            degree

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        array_like
            a 2-D scaled companion matrix of dimension (len(c)-1, len(c)-1)

        References
        ----------

        """

        # c is a trimmed copy

        if len(c) < 2:
            raise ValueError("Series must have maximum degree of at least 1.")
        if len(c) == 2:
            return np.array([[-c[0] / c[1]]])

        n = len(c) - 1
        mat = np.zeros((n, n))
        scl = np.array([1.0] + [np.sqrt(0.5)] * (n - 1))
        top = mat.reshape(-1)[1 :: n + 1]
        bot = mat.reshape(-1)[n :: n + 1]
        top[0] = np.sqrt(0.5)
        top[1:] = 1 / 2
        bot[...] = top
        mat[:, -1] -= (c[:-1] / c[-1]) * (scl / scl[-1]) * 0.5

        return mat

    def interp_from_values(self, values, abscissas=None, **kwargs):
        kind1 = kwargs.get("kind1", False)

        if abscissas is None:
            if kind1:
                return self.vals1tocoeffs(values)
            return self.vals2tocoeffs(values)

        return super().interp_from_values(values, abscissas=None, **kwargs)

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        n = coeff.shape[-1]
        # This is based in the fact that \int_{-1}^{1}T_{n}(x)dx=2/(1-n**2)
        # for n even
        return (
            (1 - np.arange(0, n, 2, dtype=self.dtype) ** 2) ** -1
            @ coeff[..., ::2].T
            * np.diff(self.domain).item()
        )

    def matrixQ2(self, n, q):
        if n > 25:
            warn("results may be innacurate due to large value of n")

        table_factorial = factorial(np.arange(2 * n - 1))

        Q = np.zeros((n, n), dtype=self.dtype)
        Q[0, 0] = 1

        for m in range(1, n):
            # first row
            j = 0
            result = (-1) ** m / m
            for k in range(1, m + 1):
                result += (
                    (-1) ** (m - k)
                    * q**k
                    * np.prod(np.arange(m - k + 1, m + k))
                    / table_factorial[k] ** 2
                )

            Q[j, m] = m * result

            # other rows
            for j in range(1, m + 1):
                result = 0
                for k in range(j, m + 1):
                    result += (
                        (-1) ** (m - k)
                        * q**k
                        * np.prod(np.arange(m - k + 1, m + k))
                        / table_factorial[k - j]
                        / table_factorial[k + j]
                    )
                Q[j, m] = 2 * m * result

        return Q

    def fractionalIntegral(self, c, mu, b=0):
        r"""
        Returns the smooth part (polynomial coefficients) of a
        Fractional Polynomial for the Fractional Integral in the
        ChebyshevT basis.

        .. math::
            I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

        Parameters
        ----------
        c : array_like
            The coefficients of a polynomial in the given basis.
        mu : scalar
            A scalar between ]0,1[ corresponding to the order of the fractional integral.

        Returns
        -------
        array_like
            The smooth part of the fractional integral of order `mu` coefficients.

        Notes
        -----
        When :math:`\alpha=0.5` we use the particular relation:

        .. math::
            \left(n+\frac{1}{2}\right)(1+x)^\frac{1}{2}\int_{-1}^x (x-t)
            ^\frac{-1}{2}P_n(t)dt = T_n(x) +T_{n+1}(x),
        where :math:`P_n` are the Legendre polynomials and :math:`T_n`
        the Chebyshev polynomials of the first kind.

        For all the other cases, the values of math:`\mu \neq 0.5`,
        the general formula that works for all math:`\mu` values is used:

        .. math::
            \frac{(1-x)^{\alpha + \mu}P_n^{(\alpha+\mu,\ \beta -\mu)}(x)}
            {\Gamma(\alpha +\mu+n+1)}=\int_x^1 \frac{(1-y)^\alpha
            P_n^{(\alpha,\ \beta)}(y)\ (y-x)^{\mu -1}}{\Gamma(\alpha +n+1)
            \Gamma(\mu)}dy,\quad \mu >0, -1 <x<1,
        where :math:`P_n^{(\alpha,\ \beta)}` are the Jacoby polynomials with
        parameters :math:`\alpha` and :math:`\beta` respectively.
        These formulas can be found in [1, p.456 ].

        References
        ----------
        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        Cambridge University Press, New York, NY, 2010.
        """

        n = c.shape[-1]

        # Scale to the domain
        sc = (np.diff(self.domain) / 2) ** mu

        if b == 0:
            # Conversion to the Legendre basis
            cl = chebt2leg(c)

            # Coefficients of the half integral
            if mu == 0.5:
                c_sc = cl / ((np.arange(n) + 0.5) * gamma(0.5))

                # The new coefficients
                cn = np.concatenate(
                    (
                        c_sc[..., :1],
                        c_sc[..., 1:] + c_sc[..., :-1],
                        c_sc[..., -1:],
                    ),
                    axis=-1,
                )

                # For consistency with mu != .5, we must divide by (1+x).
                if n == 1:
                    d = spdiags([1], [0], 1, 1, format="csc")
                else:
                    e = np.ones(n)
                    d = spdiags(
                        np.array([np.concatenate(((1,), 0.5 * e[1:])), e, 0.5 * e]),
                        [0, 1, 2],
                        n,
                        n,
                        format="csc",
                    )
                cout = np.concatenate(
                    (spsolve(d, cn[..., 1:].T).T, np.zeros_like(cn[..., :1])),
                    axis=-1,
                )
            # Coefficients of fractional integral
            else:
                # The coefficients in Jacoby basis
                cj = (cl * beta(np.arange(1, n + 1), mu)) / gamma(mu)
                cout = jac2chebt(cj, -mu, mu)

        else:
            cj1 = jac2jac(c / scl(0, n - 1), -0.5, -0.5, 0, b)
            cj2 = (cj1 * beta(np.arange(n) + b + 1, mu)) / gamma(mu)

            cout = jac2chebt(cj2, -mu, b + mu)

        return cout * sc

    def to_chebyshevT_coeff(self, coeff):
        return coeff

    def from_chebyshevT_coeff(self, coeff):
        return coeff


class ChebyshevU(T3Basis):
    r"""
    A class used to represent a Chebyshev polynomial basis of the second kind in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ChebyshevU"

    def alpha(self, n):
        return 1 / 2

    def beta(self, n):
        return 0

    def gamma(self, n):
        return 1 / 2

    def eta(self, i, j):
        return 2 * ((i + j - 1) % 2) * (i + 1)

    def theta(self, n):
        return np.array(
            [
                1 / np.arange(2, 2 * n + 1, 2),
                np.zeros(n),
                np.concatenate((np.zeros(2), -1 / np.arange(6, 2 * n + 1, 2))),
            ]
        )

    def nodes(self, n):
        r"""
        Quadrature  points and weights for second kind Chebyshev Polynomials. Those are
        the ``n``  points and weights for the Clenshaw-Curtis quadrature.


        Parameters
        ----------
        n : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.

        """

        dom = self.domain

        if n > 0:
            if n == 1:
                x = 0
                w = 2

            else:
                x = np.concatenate(
                    (
                        [-1],
                        np.cos(np.arange(n - 2, 0, -1) * np.pi / (n - 1)),
                        [1],
                    )
                )
                c = 2 / np.concatenate(([1], 1 - np.arange(2, n, 2) ** 2))
                c = np.concatenate((c, c[n // 2 - 1 : 0 : -1]))
                w = ifft(c)
                w = np.concatenate((w[:1] / 2, w[1:], w[:1] / 2)).real

            # Scale and shifting of the Nodes
            x = (sum(dom) + np.diff(dom).item() * x) / 2
            # Scale the weights
            w = (np.diff(dom).item() / 2) * w
            return x, w
        return None, None

    def productv2(self, p, q):
        r"""
        Does the product of ``p`` and ``q`` where ``p``and ``q`` are coeffi-
        cients of two polynomials P and Q in Legendre basis and the output is
        the coefficients of P*Q.


        Parameters
        ----------
        p : array_like
            The coefficients of a polynomial in Legendre basis.
        q : array_like
            The coefficients of a polynomial in Legendre basis.

        Raises
        ------
        ValueError
            When we do not have: 1 row x n rows, n rows x 1 row, or n rows x
            n rows.

        Returns
        -------
        array_like
            The coefficients of P*Q which.

        Examples
        --------
        >>> b = polynomial.LegendreP()
        >>> p = np.arange(4)
        >>> q = np.arange(3)
        >>> b.productv2(p, q)
        array([1.1333, 3.1429, 3.0952, 4.    , 3.7714, 2.8571])
        """
        return self._ultraProduct(p, q, 1)

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        n = coeff.shape[-1]
        # This is based in the fact that \int_{-1}^{1}U_{n}(x)dx=2/(n+1)
        # for n even
        return (
            np.arange(1, n + 1, 2, dtype=self.dtype) ** -1
            @ coeff[..., ::2].T
            * np.diff(self.domain).item()
        )

    def interp_from_values(self, values, abscissas=None, **kwargs):
        if abscissas is None:
            return chebt2kind(self.vals2tocoeffs(values))

        return super().interp_from_values(values, abscissas=None, **kwargs)

    def fractionalIntegral(self, c, mu, b=0):
        r"""
        Returns the smooth part (polynomial coefficients) of a
        Fractional Polynomial for the Fractional Integral in the
        ChebyshevU basis.

        Here ``c`` is the vector of the coefficients of a polynomial
        in the given basis.  We compute the Riemann-Liouville Integral
        based on the formula:

        .. math::
            I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

        Parameters
        ----------
        c : array_like
            The coefficients of a polynomial in the given basis.
        mu : scalar
            A scalar between ]0,1[ corresponding to the order of the fractional integral.
            In the documentation below we refer to this value as :math:`\alpha`.

        Returns
        -------
        array_like
            The smooth part of the fractional integral of order `mu` coefficients.

        Notes
        -----
        The calculations are done taking advantage that math:`U_n(x)` is up to
        the product with a scalar constant the same as the Jacobi polynomial
        math:`P_n^{(1,1)}(x)`.

        For all the other cases, the values of math:`\alpha \neq 0.5`,
        the general formula that works for all math:`\alpha values is used:

        .. math::
            \frac{(1-x)^{\alpha + \mu}P_n^{(\alpha+\mu,\ \beta -\mu)}(x)}
            {\Gamma(\alpha +\mu+n+1)}=\int_x^1 \frac{(1-y)^\alpha
            P_n^{(\alpha,\ \beta)}(y)\ (y-x)^{\mu -1}}{\Gamma(\alpha +n+1)
            \Gamma(\mu)}dy,\quad \mu >0, -1 <x<1,
        where :math:`P_n^{(\alpha,\ \beta)}` are the Jacoby polynomials with
        parameters :math:`\alpha` and :math:`\beta` respectively.
        These formulas can be found in [1, p.456 ].

        References
        ----------
        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        Cambridge University Press, New York, NY, 2010.

        """
        sc = (np.diff(self.domain) / 2) ** mu
        n = c.shape[-1]

        # alpha = 1 for ChebyshevU
        al = 1

        # For Legendre the scale factor is 0
        cj1 = jac2jac(c / scl(al, n - 1), al - 0.5, al - 0.5, 0, b)
        cj2 = (cj1 * beta(np.arange(n, dtype=self.dtype) + b + 1, mu)) / gamma(mu)
        cout = jac2jac(cj2, -mu, b + mu, al - 0.5, al - 0.5) * scl(al, n - 1)
        return cout * sc

    def to_chebyshevT_coeff(self, coeff):
        n = coeff.shape[-1]
        return jac2chebt(coeff / scl(1, n - 1), 0.5, 0.5)

    def from_chebyshevT_coeff(self, coeff):
        return chebt2kind(coeff)


class ChebyshevV(T3Basis):
    r"""
    A class used to represent a Chebyshev polynomial basis of the third kind in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ChebyshevV"

    def alpha(self, n):
        return 1 / 2

    def beta(self, n):
        return 1 / 2 * (n == 0)

    def gamma(self, n):
        return 1 / 2

    def eta(self, i, j):
        return 2 * ((i + j - 1) % 2) * (i + 1 / 2) + j - i - 1

    def theta(self, n):
        return np.array(
            [
                np.concatenate(([0.5], 1 / np.arange(4, 2 * n + 1, 2))),
                np.concatenate(([0], -0.5 / (np.arange(1, n) * np.arange(2, n + 1)))),
                np.concatenate((np.zeros(2), -1 / np.arange(4, 2 * n - 1, 2))),
            ]
        )

    # def nodes(self, n):
    #     x = np.cos((np.arange(n, 0, -1) - 1 / 2) * np.pi / (n + 1 / 2))
    #     return ((self.domain[0] * (1 - x) + self.domain[1] * (1 + x)) / 2,)

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        n = coeff.shape[-1]
        # This is based in the fact that \int_{-1}^{1}T_{n}(x)dx=2/(n+1)
        # for n even and -2/n for n odd
        c = np.arange(1, n + 1, 2, dtype=self.dtype) ** -1
        result = np.zeros(n)
        result[::2] = c
        result[1::2] = -c[: n // 2]
        return result @ coeff.T * np.diff(self.domain).item()

    def fractionalIntegral(self, c, mu, b=0):
        r"""
                Returns the smooth part (polynomial coefficients) of a
                Fractional Polynomial for the Fractional Integral in the
                ChebyshevV basis.

                .. math::
                    I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

                Parameters
                ----------
                c : array_like
                    The coefficients of a polynomial in the given basis.
                mu : scalar
                    A scalar between ]0,1[ corresponding to the order of the fractional integral.

                Returns
                -------
                array_like
                    The smooth part of the fractional integral of order `mu` coefficients.

                Notes
                -----
                .. math::
        -            V_n=\frac{n!^2 2^{2n}}{(2n)!}P_n^{(\frac{1}{2},\ \frac{-1}{2})}
        -        where :math:`P_n` are the Jacoby polynomials and :math:`V_n` are the
        -        Chebyshev polynomials of the third kind.

                 References
        -        ----------
        -        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        -        Cambridge University Press, New York, NY, 2010.
        -        [2] Kamal Aghigh, et al. A survey on third and fourth kind of Chebyshev
        -        polynomials and their applications. Journal of Applied Mathematics and
        -        Computation, 2008.
        """
        # Conversion to Legendre basis

        n = c.shape[-1]

        # Scale to the domain
        sc = (np.diff(self.domain) / 2) ** mu

        # The coefficients in Legendre basis.
        cl = jac2jac(c / scl(0, n - 1), -0.5, 0.5, 0, b)

        # The coefficients in Jacoby basis
        cj = (cl * beta(np.arange(1, n + 1) + b, mu)) / gamma(mu)

        cout = jac2jac(cj, -mu, b + mu, -0.5, 0.5) * scl(0, n - 1)

        return cout * sc

    def productv2(self, p, q):
        r"""
        Does the product of ``p`` and ``q`` where ``p``and ``q`` are coeffi-
        cients of two polynomials P and Q in ChebyshevW basis and the output is
        the coefficients of P*Q.


        Parameters
        ----------
        p : array_like
            The coefficients of a polynomial in Legendre basis.
        q : array_like
            The coefficients of a polynomial in Legendre basis.

        Raises
        ------
        ValueError
            When we do not have: 1 row x n rows, n rows x 1 row, or n rows x
            n rows.

        Returns
        -------
        array_like
            The coefficients of P*Q which.

        Examples
        --------

        Using Legendre basis in the  default domain [-1,1]:

        >>> b = polynomial.LegendreP()
        >>> p = np.arange(4)
        >>> p
        array([0, 1, 2, 3])

        >>> q = np.arange(3)
        >>> q
        array([0, 1, 2])

        >>> b.productv2(p, q)
        array([1.1333, 3.1429, 3.0952, 4.    , 3.7714, 2.8571])
        """

        res = self._chebThreeTermsRecurrence(p, q)
        if isinstance(res, tuple):
            c0, c1 = res
            return self.add(c0, self.add(-c1, self._prodx(c1) * 2))
        return res

    def to_chebyshevT_coeff(self, coeff):
        n = coeff.shape[-1]
        return jac2chebt(coeff / scl(0, n - 1), -0.5, 0.5)

    def from_chebyshevT_coeff(self, coeff):
        return chebt2kind(coeff, 3)


class ChebyshevW(T3Basis):
    r"""
    A class used to represent a Chebyshev polynomial basis of the fourth kind in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ChebyshevW"

    def alpha(self, n):
        return 1 / 2

    def beta(self, n):
        return -1 / 2 * (n == 0)

    def gamma(self, n):
        return 1 / 2

    def eta(self, i, j):
        return (2 * ((i + j - 1) % 2) * (i + 1 / 2) + j - 1 - i) * (-1) ** (i + j)

    def theta(self, n):
        return np.array(
            [
                1 / np.arange(2, 2 * n + 1, 2),
                np.r_[0, 1 / 2 * 1 / (np.arange(1, n) * np.arange(2, n + 1))],
                np.r_[0, 0, -1 / np.arange(4, 2 * n - 1, 2)],
            ]
        )

    # def nodes(self, n):
    #     x = np.cos(np.arange(n, 0, -1) * np.pi / (n + 1 / 2))
    #     return ((self.domain[0] * (1 - x) + self.domain[1] * (1 + x)) / 2,)

    def productv2(self, p, q):
        r"""
        Does the product of ``p`` and ``q`` where ``p``and ``q`` are coeffi-
        cients of two polynomials P and Q in ChebyshevW basis and the output is
        the coefficients of P*Q.


        Parameters
        ----------
        p : array_like
            The coefficients of a polynomial in Legendre basis.
        q : array_like
            The coefficients of a polynomial in Legendre basis.

        Raises
        ------
        ValueError
            When we do not have: 1 row x n rows, n rows x 1 row, or n rows x
            n rows.

        Returns
        -------
        array_like
            The coefficients of P*Q which.

        Examples
        --------

        Using Legendre basis in the  default domain [-1,1]:

        >>> b = polynomial.LegendreP()
        >>> p = np.arange(4)
        >>> p
        array([0, 1, 2, 3])

        >>> q = np.arange(3)
        >>> q
        array([0, 1, 2])

        >>> b.productv2(p, q)
        array([1.1333, 3.1429, 3.0952, 4.    , 3.7714, 2.8571])
        """

        res = self._chebThreeTermsRecurrence(p, q)
        if isinstance(res, tuple):
            c0, c1 = res
            return self.add(c0, self.add(c1, self._prodx(c1) * 2))
        return res

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        n = coeff.shape[-1]
        # This is based in the fact that \int_{-1}^{1}W_{n}(x)dx=2/(n+1)
        # for n even and 2/n for n odd
        result = np.repeat(np.arange(1, n + 1, 2, dtype=self.dtype) ** -1, 2)[:n]
        return result @ coeff.T * np.diff(self.domain).item()

    def fractionalIntegral(self, c, mu, b=0):
        r"""
                Returns the smooth part (polynomial coefficients) of a
                Fractional Polynomial for the Fractional Integral in the
                ChebyshevW basis.

                .. math::
                    I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

                Parameters
                ----------
                c : array_like
                    The coefficients of a polynomial in the given basis.
                mu : scalar
                    A scalar between ]0,1[ corresponding to the order of the fractional integral.

                Returns
                -------
                array_like
                    The smooth part of the fractional integral of order `mu` coefficients.

                Notes
                -----

                .. math::
        -            W_n=\frac{n!^2 2^{2n}}{(2n)!}P_n^{(\frac{-1}{2},\ \frac{1}{2})}
        -        where :math:`P_n` are the Jacoby polynomials and :math:`W_n`  are the
        -        Chebyshev polynomials of the fourth kind.

                 References
        -        ----------
        -        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        -        Cambridge University Press, New York, NY, 2010.
        -        [2] Kamal Aghigh, et al. A survey on third and fourth kind of Chebyshev
        -        polynomials and their applications. Journal of Applied Mathematics and
        -        Computation, 2008.
        """
        # Conversion to Legendre basis
        n = c.shape[-1]

        # Scale to the domain
        sc = (np.diff(self.domain) / 2) ** mu

        # Conversion based in [2, p.7]
        # The coefficients in Legendre basis.
        cj1 = jac2jac(c / scl(0, n - 1), 0.5, -0.5, 0, b)

        # The coefficients in Jacoby basis
        cj2 = (cj1 * beta(np.arange(1, n + 1) + b, mu)) / gamma(mu)

        cout = jac2jac(cj2, -mu, b + mu, 0.5, -0.5) * scl(0, n - 1)

        return cout * sc

    def to_chebyshevT_coeff(self, coeff):
        n = coeff.shape[-1]
        return jac2chebt(coeff / scl(0, n - 1), 0.5, -0.5)

    def from_chebyshevT_coeff(self, coeff):
        return chebt2kind(coeff, 4)


class GegenbauerC(T3Basis):
    r"""
    A class used to represent a Gegenbauer polynomial basis in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters, alpha.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        if "params" not in kwargs or "alpha" not in kwargs["params"]:
            kwargs["params"] = {"alpha": 0.5}
        if "alpha" in kwargs:
            kwargs["params"]["alpha"] = kwargs.pop("alpha")
        super().__init__(**kwargs)
        self.name = "GegenbauerC"

    def alpha(self, n):
        return (n + 1) / (n + self.params["alpha"]) / 2

    def beta(self, n):
        return 0

    def gamma(self, n):
        return 1 - self.alpha(n)

    # why we have (i+j+1)%2 while in the other bases we have (i+j-1)%2
    def eta(self, i, j):
        return 2 * ((i + j + 1) % 2) * (i + self.params["alpha"])

    def theta(self, n):
        return np.array(
            [
                1 / (2 * self.params["alpha"] + np.arange(0, 2 * n - 1, 2)),
                np.zeros(n),
                np.r_[
                    0,
                    0,
                    -1 / (2 * self.params["alpha"] + np.arange(4, 2 * n - 1, 2)),
                ],
            ]
        )

    def productv2(self, p, q):
        r"""
        Does the product of ``p`` and ``q`` where ``p``and ``q`` are coeffi-
        cients of two polynomials P and Q in Legendre basis and the output is
        the coefficients of P*Q.


        Parameters
        ----------
        p : array_like
            The coefficients of a polynomial in Legendre basis.
        q : array_like
            The coefficients of a polynomial in Legendre basis.

        Raises
        ------
        ValueError
            When we do not have: 1 row x n rows, n rows x 1 row, or n rows x
            n rows.

        Returns
        -------
        array_like
            The coefficients of P*Q which.

        Examples
        --------
        >>> b = polynomial.LegendreP()
        >>> p = np.arange(4)
        >>> q = np.arange(3)
        >>> b.productv2(p, q)
        array([1.1333, 3.1429, 3.0952, 4.    , 3.7714, 2.8571])
        """
        return self._ultraProduct(p, q, self.params["alpha"])

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        n = coeff.shape[-1]
        al = self.params["alpha"]
        # This is based in the fact that \int_{-1}^{1} C_{n}^{\alpha}(x)dx=
        # \binom{2\alpha+n-2}{n}/(n+1) if n even
        c = np.arange(0, n, 2)
        result = binom(2 * al + c - 2, c) / (c + 1)
        if np.isnan(result[0]):
            result[0] = 1
        return result @ coeff[..., ::2].T * np.diff(self.domain).item()

    def fractionalIntegral(self, c, mu, b=0):
        r"""
        Returns the smooth part (polynomial coefficients) of a
        Fractional Polynomial for the Fractional Integral in the
        GegenbauerC basis with parameter param.alpha.

        .. math::
            I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

        Parameters
        ----------
        c : array_like
            The coefficients of a polynomial in the given basis.
        mu : scalar
            A scalar between ]0,1[ corresponding to the order of the fractional integral.

        Returns
        -------
        array_like
            The smooth part of the fractional integral of order `mu` coefficients.

        Notes
        -----
        When :math:`\alpha=0.5` we use the particular relation:

        .. math::
            \left(n+\frac{1}{2}\right)(1+x)^\frac{1}{2}\int_{-1}^x (x-t)
            ^\frac{-1}{2}P_n(t)dt = T_n(x) +T_{n+1}(x),
        where :math:`P_n` are the Legendre polynomials and :math:`T_n`
        the Chebyshev polynomials of the first kind.

        For all the other cases, the values of math:`\mu \neq 0.5`,
        the general formula that works for all math:`\mu` values is used:

        .. math::
            \frac{(1-x)^{\alpha + \mu}P_n^{(\alpha+\mu,\ \beta -\mu)}(x)}
            {\Gamma(\alpha +\mu+n+1)}=\int_x^1 \frac{(1-y)^\alpha
            P_n^{(\alpha,\ \beta)}(y)\ (y-x)^{\mu -1}}{\Gamma(\alpha +n+1)
            \Gamma(\mu)}dy,\quad \mu >0, -1 <x<1,
        where :math:`P_n^{(\alpha,\ \beta)}` are the Jacoby polynomials with
        parameters :math:`\alpha` and :math:`\beta` respectively.
        These formulas can be found in [1, p.456 ].

        References
        ----------
        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        Cambridge University Press, New York, NY, 2010.
        """
        sc = (np.diff(self.domain) / 2) ** mu
        n = c.shape[-1]

        # Conversion to Legendre basis
        al = self.params["alpha"]

        # For Legendre the scale factor is 0
        cj1 = jac2jac(c / scl(al, n - 1), al - 0.5, al - 0.5, 0, b)
        cj2 = (cj1 * beta(np.arange(n, dtype=self.dtype) + b + 1, mu)) / gamma(mu)
        cout = jac2jac(cj2, -mu, b + mu, al - 0.5, al - 0.5) * scl(al, n - 1)
        return cout * sc

    def to_chebyshevT_coeff(self, coeff):
        n = coeff.shape[-1]
        α = self.params["alpha"]
        return jac2chebt(coeff / scl(α, n - 1), α - 0.5, α - 0.5)

    def from_chebyshevT_coeff(self, coeff):
        n = coeff.shape[-1]
        α = self.params["alpha"]
        return jac2jac(coeff / scl(0, n - 1), -0.5, -0.5, α - 0.5, α - 0.5) * scl(α, n - 1)


class HermiteH(T3Basis):
    r"""
    A class used to represent a Hermite polynomial basis in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters, alpha.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "HermiteH"
        self.c1 = 1
        self.c0 = 0
        self.support = np.array([np.inf, np.inf])

    def alpha(self, n):
        return 1 / 2

    def beta(self, n):
        return 0

    def gamma(self, n):
        return 2 * n

    def eta(self, i, j):
        return 2 * (j - 1) * ((j - 2) == i)

    def theta(self, n):
        return np.array([1 / np.arange(2, 2 * n + 1, 2), np.zeros(n), np.zeros(n)])


class LaguerreL(T3Basis):
    r"""
    A class used to represent a Laguerre polynomial basis in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters, alpha.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "LaguerreL"
        self.support = np.array([0, np.inf])
        self.c1 = 1
        self.c0 = -self.domain[0]
        self.x1 = np.array([1 + self.domain[0], -1])

    def alpha(self, n):
        return -n - 1

    def beta(self, n):
        return 2 * n + 1

    def gamma(self, n):
        return -n

    def eta(self, i, j):
        return -1

    def theta(self, n):
        return np.array([-np.ones(n), np.r_[0, np.ones(n - 1)], np.zeros(n)])

    def _gw_alg(self, n):
        # In the future alpha must be a parameter for generalized Laguerre
        # polynomials
        alpha = 0
        a = np.arange(1, 2 * n, 2) + alpha
        b = np.sqrt(np.arange(1, n) * (np.arange(1, n) + alpha))
        A = np.diag(b, -1) + np.diag(a) + np.diag(b, 1)
        w, v = eig(A)
        ind = np.argsort(w)

        return w[ind], v[0, ind] ** 2


class LegendreP(T3Basis):
    r"""
    A class used to represent a Legendre polynomial basis in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters, alpha.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "LegendreP"

    def alpha(self, n):
        return (n + 1) / (2 * n + 1)

    def beta(self, n):
        return 0

    def gamma(self, n):
        return n / (2 * n + 1)

    def eta(self, i, j):
        return 2 * ((i + j + 1) % 2) * (i + 1 / 2)

    def theta(self, n):
        return np.array(
            [
                1 / np.arange(1, 2 * n, 2),
                np.zeros(n),
                np.concatenate(([0] * 2, -1 / np.arange(5, 2 * n, 2))),
            ]
        )

    def product(self, p, q):
        return legendre.legmul(p, q)

    def productv2(self, p, q):
        r"""
        Does the product of ``p`` and ``q`` where ``p``and ``q`` are coeffi-
        cients of two polynomials P and Q in Legendre basis and the output is
        the coefficients of P*Q.


        Parameters
        ----------
        p : array_like
            The coefficients of a polynomial in Legendre basis.
        q : array_like
            The coefficients of a polynomial in Legendre basis.

        Raises
        ------
        ValueError
            When we do not have: 1 row x n rows, n rows x 1 row, or n rows x
            n rows.

        Returns
        -------
        array_like
            The coefficients of P*Q which.

        Examples
        --------
        >>> b = polynomial.LegendreP()
        >>> p = np.arange(4)
        >>> q = np.arange(3)
        >>> b.productv2(p, q)
        array([1.1333, 3.1429, 3.0952, 4.    , 3.7714, 2.8571])
        """
        return self._ultraProduct(p, q, 0.5)

    def companion(self, c):
        """Return the scaled companion matrix of c.


        The basis Polynomials are scaled so that the companion matrix is
        symmetric when `c` is an Legendre basis Polynomial. This provides
        better eigenvalue estimates than the unscaled case and for basis
        Polynomials the eigenvalues are guaranteed to be real if
        `numpy.linalg.eigvalsh` is used to obtain them.
        Parameters
        ----------
        c : array_like
            1-D array of Legendre series coefficients ordered from low to high
            degree.
        Returns
        -------
        mat : ndarray
            Scaled companion matrix of dimensions (len(c)-1, len(c)-1).

        """
        # c is a trimmed copy
        c = c.copy()
        if len(c) < 2:
            raise ValueError("Series must have maximum degree of at least 1.")
        if len(c) == 2:
            return np.array([[-c[0] / c[1]]])

        n = len(c) - 1
        mat = np.zeros((n, n))
        scl = 1.0 / np.sqrt(2 * np.arange(n) + 1)
        top = mat.reshape(-1)[1 :: n + 1]
        bot = mat.reshape(-1)[n :: n + 1]
        top[...] = np.arange(1, n) * scl[: n - 1] * scl[1:n]
        bot[...] = top
        mat[:, -1] -= (c[:-1] / c[-1]) * (scl / scl[-1]) * (n / (2 * n - 1))
        return mat

    def quad_weights(self, n):
        r"""
        Compute the ``n``  Gauss-Legendre quadrature weights points.

        Parameters
        ----------
        n : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        TYPE
            DESCRIPTION.

        Notes
        -----
        This implementation is based on the formulas given by the website:
            https://pomax.github.io/bezierinfo/legendre-gauss.html

        """
        if n > 0:
            # get the abscesses x_i for the quadrature
            xi, *_ = self.nodes(n)
            # Get  P'_n(x_i)
            coeff = np.zeros(n + 1)
            coeff[n] = 1.0
            bi = self(coeff @ self.matrixN(n + 1).T, xi)
            w = 2 / ((1 - xi**2) * bi**2)
            # scale to domain
            return (np.diff(self.domain).item() / 2) * w

    def bary_weights(self, n):
        if n > 0:
            # get the abscesses x_i for the quadrature
            xi, *_ = self.nodes(n)
            # Get  P'_n(x_i)
            coeff = np.zeros(n + 1)
            coeff[n] = 1.0
            bi = self(coeff @ self.matrixN(n + 1).T, xi)
            v = 1 / abs(bi)
            v = v / max(v)
            v[1::2] = -v[1::2]
            return v

    def definite_integral(self, bounds, coeff, fast=True):
        r"""(
        Computes the definite integral of a Polynomial with coefficients
        ``coeff`` the interval set in ``bounds``

        .. math::
            \int_a^bp(x)d(x)

        Parameters
        ----------
        bounds : iterable
            A real valued iterable with 2 elements, the bounds of integration.

        coeff : iterable
            The coefficients of the integrand polynomial.

        fast : boolean
             If possible take of special formulas when the domain of
             orthogonality is the same as the bounds.

        Returns
        -------
        Number
            The result of the definite integral.
        """

        if not fast or any(bounds != self.domain):
            return super().definite_integral(bounds, coeff)

        # This is based in the fact that \int_{-1}^{1}P_{n}(x)dx=0 if n>0
        # and 2*T_{0}(x) if n=0
        return np.diff(self.domain) @ coeff[..., :1].T

    def fractionalIntegral(self, c, mu, b=0):
        r"""
        Returns the smooth part (polynomial coefficients) of a
        Fractional Polynomial for the Fractional Integral in the
        LegendreP basis.

        .. math::
            I^\mu f(x)=\frac{1}{\Gamma(\mu)}\int_a^x f(t)(x-t)^{\mu-1}dt

        Parameters
        ----------
        c : array_like
            The coefficients of a polynomial in the given basis.
        mu : scalar
            A scalar between ]0,1[ corresponding to the order of the fractional integral.

        Returns
        -------
        array_like
            A scalar between ]0,1[ corresponding to the order of the fractional integral.

        Notes
        -----
        The general formula that works for all math:`\mu` values is used:

        .. math::
            \frac{(1-x)^{\alpha + \mu}P_n^{(\alpha+\mu,\ \beta -\mu)}(x)}
            {\Gamma(\alpha +\mu+n+1)}=\int_x^1 \frac{(1-y)^\alpha
            P_n^{(\alpha,\ \beta)}(y)\ (y-x)^{\mu -1}}{\Gamma(\alpha +n+1)
            \Gamma(\mu)}dy,\quad \mu >0, -1 <x<1,
        where :math:`P_n^{(\alpha,\ \beta)}` are the Jacoby polynomials with
        parameters :math:`\alpha` and :math:`\beta` respectively.
        These formulas can be found in [1, p.456 ].

        References
        ----------
        [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
        Cambridge University Press, New York, NY, 2010.
        """

        n = c.shape[-1]
        sc = (np.diff(self.domain) / 2) ** mu
        if b == 0:
            # Coefficients of half integral in Chebyshev basis
            if mu == 0.5:
                c_sc = c / ((np.arange(n) + 0.5) * gamma(0.5))

                # The new coefficients
                cn = np.r_[
                    "-1",
                    c_sc[..., :1],
                    c_sc[..., 1:] + c_sc[..., :-1],
                    c_sc[..., -1:],
                ]

                # For consistency with mu != .5, we must divide by (1+x).
                if n == 1:
                    d = spdiags([1], [0], 1, 1, format="csc")
                else:
                    e = np.ones(n)
                    d = spdiags(
                        np.r_["0,2", np.r_[1, 0.5 * e[1:]], e, 0.5 * e],
                        [0, 1, 2],
                        n,
                        n,
                        format="csc",
                    )
                ct = np.r_[
                    "-1",
                    spsolve(d, cn[..., 1:].T).T,
                    np.zeros_like(cn[..., :1]),
                ]
                return chebt2leg(ct) * sc
            # Coefficients of fractional integral
            else:
                # The coefficients in Jacoby basis
                cj = (c * beta(np.arange(1, n + 1), mu)) / gamma(mu)
                return jac2jac(cj, -mu, mu, 0, 0) * sc

        else:
            # For Legendre the scale factor is 0
            cj1 = jac2jac(c, 0, 0, 0, b)
            cj2 = (cj1 * beta(np.arange(n) + b + 1, mu)) / gamma(mu)
            cout = jac2jac(cj2, -mu, b + mu, 0, 0)
        return cout * sc

    def to_chebyshevT_coeff(self, coeff):
        return leg2chebt(coeff)

    def from_chebyshevT_coeff(self, coeff):
        return chebt2leg(coeff)


class PowerX(T3Basis):
    r"""
    A class used to represent the power basis in one variable.

    Attributes
    ----------
    dtype: Type, optional
        A `numpy` data type (default: `np.float64`)
    domain : array_like, optional
        An  array_like object where each row with the domain of an independent
        variable in the order given by bases. The default is [-1, 1].
    params : dict, optional
        Family parameters, alpha.

    Notes
    -----
    This is the form of representing a Polynomial in one variable
    :math:`\mathcal{P_m}(x)=[P_0(x),\ \dots,\ P_m(x)],\ x \in [a,b]`

    Therefore the coefficients are represented by :math:`[a_{i}]_{m}`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "PowerX"

    def alpha(self, n):
        return 1

    def beta(self, n):
        return 0

    def gamma(self, n):
        return 0

    def eta(self, i, j):
        return (j - 1) * ((j - 2) == i)

    def theta(self, n):
        return np.array([1 / np.arange(n) + 1, np.zeros(n), np.zeros(n)])

    def to_power_coeff(self, coeff):
        return coeff

    def from_power_coeff(self, coeff):
        return coeff


def available(kind: str = "supported"):
    supported = ["ChebyshevT", "ChebyshevU", "LegendreP", "GegenbauerC", "PowerX"]
    experimental = ["BesselY", "HermiteH", "LaguerreL", "ChebyshevV", "ChebyshevW"]

    options = {
        "supported": supported,
        "experimental": experimental,
        "all": supported + experimental,
    }
    return sorted(options.get(kind, "supported"))


def jac2chebt_rec(cj, a, b):
    r"""
    This function convert Jacobi coefficients with parameters ``a`` and ``b``
    into ChebyshevT Coefficients. here we use the 3 therms recurrence relation
    to compute the coefficients in ChebyshevT basis.This method is a translation
    to python of the method ``jac2cheb_direct`` of matlab system chebfun.

    Parameters
    ----------
    cj : array_like
        The coefficients of the polynomial in Jacobi basis.
    a : scalar
        The parameter :math:`\alpha` of the Jacobi basis.
    b : scalar
        The parameter :math:`\beta` of the Jacobi basis.

    Returns
    -------
    array_like
        The coefficients in ChebyshevT basis

    """
    n = cj.shape[-1]

    # The trivial case
    if n < 2:
        return cj

    bs = ChebyshevT()
    x, *_ = bs.nodes(n)  # Nodes of the ChebyshevT

    # Make the Jacobi-Chebyshev Vandermonde matrix
    apb, aa, bb = a + b, a * a, b * b
    P = np.zeros((n, n))
    P[:, 0] = 1
    P[:, 1] = 0.5 * (2 * (a + 1) + (apb + 2) * (x - 1))

    for i in range(2, n):
        i2 = 2 * i
        i2apb = i2 + apb
        q1 = i2 * (i + apb) * (i2apb - 2)
        q2 = (i2apb - 1) * (aa - bb)
        q3 = (i2apb - 2) * (i2apb - 1) * i2apb
        q4 = 2 * (i + a - 1) * (i + b - 1) * i2apb
        P[:, i] = ((q2 + q3 * x) * P[:, i - 1] - q4 * P[:, i - 2]) / q1

    vc = cj @ P.T  # Values on the Chebyshev Grid
    return bs.vals1tocoeffs(vc)


def jac2chebt(cj, alpha, beta):
    r"""
    Convert coefficients in Jacobi basis with parameters ``alpha`` and ``beta``
    to coefficients in ChebyshevT basis. This method is based in the matlab
    system chebfun of the same name.

    Parameters
    ----------
    cj : array_like
        The coefficients in Jacobi basis.
    alpha : scalar
        The parameter :math:`\alpha` of the Jacobi basis.
    beta : scalar
        The parameter :math:`\beta` of the Jacobi basis.

    Returns
    -------
    array_like
        The coefficients in ChebyshevT basis

    """
    # The case when Jacobi basis match Legendre basis
    if alpha == beta == 0:
        return leg2chebt(cj)

    n = cj.shape[-1]

    # when n is small
    if n < 512:
        return jac2chebt_rec(cj, alpha, beta)

    # Call jac2jac  and then convert jacobi(-.5,-.5) to ChebyshevT
    else:
        # Convert P_n^(alpha,beta) to P_n^(-.5.-.5).
        cj = jac2jac(cj, alpha, beta, -0.5, -0.5)
        # Convert  P_n^(-.5.-.5) to T_n.
        scl = np.r_[1, np.cumprod(np.arange(0.5, 0.5 + n - 1) / np.arange(1, n))]
        return scl * cj


def chebt2leg_mat(n):
    """
    Construct the conversion matrix from Chebyshev of the first kind coeffi-
    cients to Legendre coefficients

    Parameters
    ----------
    n : int
        The Dimension of the conversion matrix.

    Returns
    -------
    res : array_like
        A n*n conversion matrix

    """
    vals = np.zeros(2 * n)
    vals[0] = np.pi ** (1 / 2)
    vals[1] = 2 / vals[0]
    for i in range(2, 2 * n - 1, 2):
        vals[i] = vals[i - 2] * (1 - 1 / i)
        vals[i + 1] = vals[i - 1] * (1 - 1 / (i + 1))

    res = np.zeros((n, n))
    for i in range(n):
        if i + 2 < n:
            res[i, i + 2 : n : 2] = (
                -np.arange(i + 2, n, 2)
                * (i + 0.5)
                * (vals[: n - i - 2 : 2] / (np.arange(i + 2, n, 2) - i))
                * (vals[2 * i + 1 : n + i - 1 : 2] / (np.arange(i + 2, n, 2) + i + 1))
            )
    c = np.sqrt(np.pi) / 2
    res[np.arange(1, n), np.arange(1, n)] = c / vals[2 : 2 * (n - 1) + 2 : 2]
    res[0, 0] = 1
    return res


def leg2chebt_mat(n):
    """
    Conversion matrix from Legendre coefficients to Chebyshev of the first
    kind

    Parameters
    ----------
    n : int
        The Dimension of the conversion matrix

    Returns
    -------
    res : array_like
        A n*n conversion matrix.

    """
    vals = np.zeros(2 * n)
    vals[0] = np.sqrt(np.pi)
    vals[1] = 2 / vals[0]
    for i in range(2, 2 * n - 1, 2):
        vals[i] = vals[i - 2] * (1 - 1 / i)
        vals[i + 1] = vals[i - 1] * (1 - 1 / (i + 1))

    res = np.zeros((n, n))
    for i in range(n):
        res[i, i:n:2] = 2 / np.pi * vals[0 : n - i : 2] * vals[2 * i : n + i : 2]

    res[0, :] = 0.5 * res[0, :]
    return res


def chebt2leg(coef):
    """
    Convert a vector of ChebyshevT coefficients to a vector of LegendreP coe-
    fficients. If coef is a bidimensional array applies the conversion to each row.

    Parameters
    ----------
    X : array_like
        One or two dimensional array of numbers.


    Returns
    -------
    array_like
        The coefficients in LegendreP basis.

    """

    if isinstance(coef, Number):
        return coef
    if not isinstance(coef, np.ndarray):
        coef = np.array(coef)
        if not np.issubdtype(coef.dtype, np.number):
            raise ValueError("The array must contains only numbers")

    n = coef.shape[-1]
    # Since the coefficients are in the rows
    res = coef @ chebt2leg_mat(n).T
    res[np.abs(res) < np.spacing(1)] = 0
    return res


def leg2chebt(coef):
    """
    Convert LegendreP coefficients to ChebyshevT coefficients.
    If coef is a bidimensional array apply the conversion to each row.

    Parameters
    ----------
    X : array_like
        One or two dimensional array of numbers.


    Returns
    -------
    array_like
        The coefficients in ChebyshevT basis.

    """

    if isinstance(coef, Number):
        return coef
    if not isinstance(coef, np.ndarray):
        coef = np.array(coef)
        if not np.issubdtype(coef.dtype, np.number):
            raise ValueError("The array must contains only numbers")

    n = coef.shape[-1]
    # Since the coefficients are in the rows
    res = coef @ leg2chebt_mat(n).T
    return res


def chebt2ultra(c):
    """
    Convert ChebyshevT coefficients to GegenbauerC with parameter alpha =3/2
    coefficients

    Parameters
    ----------
    coef : array_like
        A matrix or an array representing the coefficients.
        When a matrix applies the conversion to each row.

    Raises
    ------
    ValueError
        DESCRIPTION.
    TypeError
        DESCRIPTION.

    Returns
    -------
    array_like
        A vector or a matrix in accordance with the input

    """
    if isinstance(c, Number):
        return c
    if not isinstance(c, np.ndarray):
        c = np.array(c)
        if not np.issubdtype(c.dtype, np.number):
            raise ValueError("The array must contains only numbers")

    n = c.shape[-1]
    return chebt2leg(c) @ leg2ultra_mat(n).T


def chebt2ultra2(c):
    """
    Convert ChebyshevT coefficients to GegenbauerC with parameter alpha =3/2
    coefficients

    Parameters
    ----------
    coef : array_like
        A matrix or an array representing the coefficients.
        When a matrix applies the conversion to each row.

    Raises
    ------
    ValueError
        DESCRIPTION.
    TypeError
        DESCRIPTION.

    Returns
    -------
    array_like
        A vector or a matrix in accordance with the input

    """
    if isinstance(c, Number):
        return c
    if not isinstance(c, np.ndarray):
        c = np.array(c)
        if not np.issubdtype(c.dtype, np.number):
            raise ValueError("The array must contains only numbers")

    n = c.shape[-1]
    if n == 1:
        return c
    l = chebt2leg(c)
    lam = 1 / 2
    dg = lam / (lam + np.arange(2, n))
    v = np.concatenate(([1, lam / (lam + 1)], dg))

    return l * v + np.concatenate([-dg * l[..., 2:], np.zeros_like(c[..., :2])], axis=-1)


def leg2ultra_mat(n):
    lam = 1 / 2
    dg = lam / (lam + np.arange(2, n))
    v = np.concatenate([[1, lam / (lam + 1)], dg])
    w = np.concatenate(([0, 0], -dg))
    return spdiags(np.array([v, w]), [0, 2], n, n)


def ultra1mx2chebt(coef):
    """
    Convert a vector of (1-x**2)^(3/2) coefficients to Chebyshev of the first
    kind. If X is a bidimensional array applies the conversion to each column

    Parameters
    ----------
    X : array_like
        One or two dimensional array of numbers.


    Returns
    -------
    array_like
        The first-kind Chebyshev coefficients.

    """

    if not isinstance(coef, np.ndarray):
        coef = np.array(coef)

    if not np.issubdtype(coef.dtype, np.number):
        raise TypeError("The array must contains only numbers")
    if coef.ndim > 2:
        raise ValueError("The array must be one or two dimensional")

    # First convert the matrix of (1-x^2)C^(3/2)(x) coefficients to
    # Legendre coefficients and then convert the Legendre coefficients
    # in to Chebyshev coefficients of the first kind
    return leg2chebt(coef @ ultra1mx2leg_mat(coef.shape[-1]).T)


def ultra1mx2leg_mat(n):
    """
    Conversion matrix from Legendre coefficients to C**(3/2).

    Parameters
    ----------
    n : int
        The dimension of the matrix

    Returns
    -------
    m : array_like
        The conversion matrix

    """
    d = np.ones(n)
    S = spdiags(
        np.arange(1, n + 1) * np.arange(2, n + 2) / 2 / np.arange(3 / 2, n + 1),
        0,
        n,
        n,
    )

    return spdiags(np.array([d, -d]), [0, -2], n, n) @ S


def ultra2ultra(coef, alpha_in, alpha_out):
    r"""
    This method Convert coefficients in :math:`C^{(\alpha_{in})}` into coeffic
    ients in :math:`C^{(\alpha_{in})}`. This method is based on chebfun method
    of the same name.

    Parameters
    ----------
    coef : array_like
        The coefficients with parameter `alpha_in`.
    alpha_in : scalar
        The parameter of the input coefficients.
    alpha_out : scalar
        The parameter of the output coefficients

    Returns
    -------
    array_like
        The coefficients in C^{(\alpha_{out})}

    References
    ----------
    [1] A. Townsend, M. Webb, and S. Olver, "Fast polynomial transforms
    based on Toeplitz and Hankel matrices", submitted, 2016.
    [2] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
    Cambridge University Press, New York, NY, 2010.


    """

    n = coef.shape[-1] - 1
    coef = coef / scl(alpha_in, n)

    coef = jac2jac(coef, alpha_in - 0.5, alpha_in - 0.5, alpha_out - 0.5, alpha_out - 0.5)

    return coef * scl(alpha_out, n)


def scl(alpha, n):
    r"""
    Scale Jacobi polynomials to ultraspherical polynomials.


    Parameters
    ----------
    alpha : scalar
        The Parameter of the ultraspherical polynomial.
    n : integer
        The degree of polynomial.

    Returns
    -------
    array_like
        The scales for the coefficients

    Notes
    -----
    This conversion is based on the Table. 18.3.1. [1, P.439]

    References
    ----------
    [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
    Cambridge University Press, New York, NY, 2010.
    """
    if alpha == 0:
        nn = np.arange(n)
        return np.r_[1, np.cumprod((nn + 0.5) / (nn + 1))]
    else:
        nn = np.arange(n + 1)
        return (gamma(2 * alpha) / gamma(alpha + 0.5)) * np.exp(
            loggamma(alpha + 0.5 + nn) - loggamma(2 * alpha + nn)
        )


def jac2jac(coef, alpha, beta, gam, delta):
    coef, a, b = jacobiIntegerConversion(coef, alpha, beta, gam, delta)

    if abs(a - gam) > 1e-15:
        coef = jacobiFractionalConversion(coef, a, b, gam)
    if abs(b - delta) > 1e-15:
        # Use reflection formula for Jacobi Polynomials
        coef.reshape(-1)[1::2] = -coef.reshape(-1)[1::2]
        coef = jacobiFractionalConversion(coef, b, gam, delta)
        coef.reshape(-1)[1::2] = -coef.reshape(-1)[1::2]

    return coef


def UpJacobiConversion(v_in, a, b):
    # n = v.shape[-1]
    # d1 = np.r_[
    #    1,
    #    (a + b + 2) / (a + b + 3),
    #    np.r_[a + b + 3 : a + b + n + 1] / np.r_[a + b + 5 : a + b + 2 * n : 2],
    # ]
    # d2 = np.r_[a + 1 : a + n] / np.r_[a + b + 3 : a + b + 2 * n : 2]

    # c = 0 if v.ndim == 1 else np.zeros((v.shape[0], 1))
    # return v * d1 + np.r_["-1", d2 * v[..., 1:], c]
    v = np.asarray(v_in)  # Ensure v is a numpy array
    N, M = v.shape

    if N == 0:
        return np.array([]).reshape(0, M)  # Handle empty input

    # Calculate diagonal elements (d1)
    # d1 has N elements
    d1 = np.zeros(N, dtype=float)
    if N > 0:
        d1[0] = 1.0
    if N > 1:
        d1[1] = (a + b + 2.0) / (a + b + 3.0)
    if N > 2:
        # Numerators for d1[2], ..., d1[N-1] (elements 3 to N)
        # Original MATLAB: (a+b+3 : a+b+N)
        num_range_d1 = np.arange(a + b + 3, a + b + N + 1)
        # Denominators for d1[2], ..., d1[N-1]
        # Original MATLAB: (a+b+5 : 2 : a+b+2*N-1)
        den_range_d1 = np.arange(a + b + 5, a + b + 2 * N - 1 + 1, 2)
        if len(num_range_d1) == len(den_range_d1):  # Should always be true if N > 2
            d1[2:] = num_range_d1 / den_range_d1
        elif len(num_range_d1) > 0:  # Should not happen if N > 2 and logic is correct
            # This case might occur if N is small, e.g. N=3 makes num_range_d1 potentially longer
            # than den_range_d1 if not careful with ranges.
            # However, for N > 2, num_range_d1 has N-2 elements, den_range_d1 also has N-2 elements.
            # Example: N=3. num_range_d1 = [a+b+3]. den_range_d1 = [a+b+5]. Correct.
            # Example: N=4. num_range_d1 = [a+b+3, a+b+4]. den_range_d1 = [a+b+5, a+b+7]. Correct.
            d1[2 : 2 + len(num_range_d1)] = num_range_d1 / den_range_d1[: len(num_range_d1)]

    # Calculate superdiagonal elements (d2)
    # d2 has N-1 elements
    if N > 1:
        # Numerators for d2[0], ..., d2[N-2] (elements 1 to N-1 of d2)
        # Original MATLAB: (a+1 : a+N-1)
        num_range_d2 = np.arange(a + 1, a + N - 1 + 1)  # Corrected to a+N
        # Denominators for d2[0], ..., d2[N-2]
        # Original MATLAB: (a+b+3 : 2 : a+b+2*N-1)
        # This denominator range is for N-1 elements.
        den_range_d2 = np.arange(a + b + 3, a + b + 2 * (N - 1) - 1 + 1, 2)
        # A more direct way for denominator of d2, matching MATLAB's (a+b+3:2:a+b+2*N-1) which has N-1 elements
        den_range_d2_alt = np.arange(
            a + b + 3, a + b + 2 * N - 1 + 1 - 2, 2
        )  # up to 2*(N-1)-1 for the last term for d2

        # The MATLAB denominator for d2 is (a+b+3:2:a+b+2*N-1). This has N-1 terms.
        # Example N=2: num (a+1), den (a+b+3).
        # Example N=3: num (a+1, a+2), den (a+b+3, a+b+5).
        den_for_d2 = np.arange(a + b + 3, a + b + 3 + 2 * (N - 1 - 1) + 1, 2)  # N-1 terms
        if len(num_range_d2) == len(den_for_d2):
            d2 = num_range_d2 / den_for_d2
        else:  # Fallback or error, lengths must match
            # This part needs to be robust. The MATLAB (a+b+3:2:a+b+2*N-1) has N-1 elements.
            den_final_d2 = np.arange(a + b + 3, a + b + 3 + 2 * (len(num_range_d2) - 1) + 1, 2)
            d2 = num_range_d2 / den_final_d2

    else:
        d2 = np.array([])

    # Apply conversion matrix operations
    # v_out = D1*v + [ D2*v[1:,:]; zeros(1,M) ]
    # D1*v is equivalent to element-wise multiplication by d1 (broadcasted)
    v_out = d1[:, np.newaxis] * v

    if N > 1 and d2.size > 0:  # d2.size > 0 check is important if N=1 led to empty d2
        # D2*v[1:,:] is equivalent to element-wise multiplication
        # of v[1:,:] by d2 (broadcasted)
        term2_product = d2[:, np.newaxis] * v[1:, :]

        # Pad with a row of zeros at the bottom
        # Ensure dtype of zeros matches v_out or v to avoid type issues
        padded_term2 = np.vstack((term2_product, np.zeros((1, M), dtype=v.dtype)))
        v_out += padded_term2
    elif N == 1 and M > 0:  # If N=1, the second term is effectively all zeros.
        # The first term v_out = d1[0]*v is already correct.
        # No explicit addition of zeros needed if v_out is initialized from d1*v.
        pass


def DownJacobiConversion(v, a, b):
    n = v.shape[-1]
    topRow = np.r_[
        1,
        (a + 1) / (a + b + 2),
        (a + 1)
        / (a + b + 2)
        * np.cumprod(np.r_[a + 2 : a + n] / np.r_[a + b + 3 : a + b + n + 1]),
    ]
    topRow *= (-1) ** np.r_[0:n]
    tmp = v * topRow
    vecsum = np.flip(np.cumsum(np.flip(tmp, axis=-1), axis=-1), axis=-1)

    ratios = (np.r_[a + b + 5 : a + b + 2 * n : 2] / np.r_[a + b + 3 : a + b + n + 1]) * (
        1 / topRow[2:]
    )
    ratios = np.r_[1, -(a + b + 3) / (a + 1), ratios]
    return ratios * vecsum


def RightJacobiConversion(v, a, b):
    v = v.copy()
    v.reshape(-1)[1::2] = -v.reshape(-1)[1::2]
    v = UpJacobiConversion(v, b, a)
    v.reshape(-1)[1::2] = -v.reshape(-1)[1::2]
    return v


def LeftJacobiConversion(v, a, b):
    v = v.copy()
    v.reshape(-1)[1::2] = -v.reshape(-1)[1::2]
    v = DownJacobiConversion(v, b, a)
    v.reshape(-1)[1::2] = -v.reshape(-1)[1::2]
    return v


def jacobiIntegerConversion(coef, alpha, beta, gam, delta):
    while alpha <= gam - 1:
        coef = RightJacobiConversion(coef, alpha, beta)
        alpha += 1

    while alpha >= gam + 1:
        coef = LeftJacobiConversion(coef, alpha - 1, beta)
        alpha -= 1

    while beta <= delta - 1:
        coef = UpJacobiConversion(coef, alpha, beta)
        beta += 1

    while beta >= delta + 1:
        coef = DownJacobiConversion(coef, alpha, beta - 1)
        beta -= 1

    return coef, alpha, beta


def jacobiFractionalConversion(v, alpha, beta, gam):
    def lam1(z):
        return np.exp(loggamma(z + alpha + beta + 1) - loggamma(z + gam + beta + 2))

    def lam2(z):
        return np.exp(loggamma(z + alpha - gam) - loggamma(z + 1))

    def lam3(z):
        return np.exp(loggamma(z + beta + gam + 1) - loggamma(z + beta + 1))

    def lam4(z):
        return np.exp(loggamma(z + beta + 1) - loggamma(z + alpha + beta + 1))

    vect = False
    if v.ndim == 1:
        v = v[np.newaxis]
        vect = True

    m, n = v.shape

    if n == 1:
        return v

    d1 = (2 * np.r_[:n] + gam + beta + 1) * lam3(np.r_[1, 1:n])
    d1[0] = 1

    d2 = 1 / gamma(alpha - gam) * lam4(np.r_[1, 1:n])
    d2[0] = 0
    # Symbol of the Hankel part
    vals = lam1(np.r_[1, 1 : 2 * n])

    vals[0] = 0

    d = vals[::2]
    pivotValues = []
    c = np.zeros((0, n))
    tol = 1e-14 * np.log(n)
    idx = d.argmax()
    mx = d[idx]

    while mx > tol:
        newRow = vals[idx : idx + n]

        if c.size > 0:
            newRow = newRow - (c[:, idx] * pivotValues) @ c

        pivotValues += [1 / mx]
        c = np.r_["0,2", c, newRow]
        d = d - newRow**2 / mx
        idx = d.argmax()
        mx = d[idx]

    c = (c.T * np.sqrt(pivotValues)).T

    T_row = lam2(np.r_[1, 1:n])
    T_row[0] = gamma(alpha - gam + 1) / (alpha - gam)
    z = np.r_[T_row[0], [0] * (n - 1)]
    a = fft(np.r_[z, T_row[:0:-1]])

    coef = v * d2

    for i in range(m):
        tmp1 = c * coef[i]

        f1 = fft(tmp1, 2 * n - 1)

        tmp2 = f1 * a
        b = ifft(tmp2).real

        coef[i] = d1 * np.sum(c * b[..., :n], axis=0)
    matrow1 = gamma(gam + beta + 2) / gamma(beta + 1) * d2 * T_row * vals[:n]
    coef[..., 0] = v @ matrow1 + v[..., 0]

    if vect:
        return coef.reshape(-1)

    return coef


def chebt2chebu(coef):
    r"""
    This method convert coefficients of Chebyshev polynomials of the
    first kind to Chebyshev polynomials of the second kind.

    Parameters
    ----------
    coef : array_like
        The coefficients to convert.

    Returns
    -------
    array_like
        The converted coefficients

    Notes
    -----
    This method is based in the relation  18.9.9 found in [1, P.446]
    :math:`T_n(x)=1/2(U_n(x)+U_{n-1}(x))`. Where :math:`T_n(x)` are the
    Chebyshev polynomials of the first kind and :math:`U_n(x)` the Cheby
    shev polynomials of the second kind.


    References
    ----------
    [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
    Cambridge University Press, New York, NY, 2010.
    """
    sh = list(coef.shape)
    sh[-1] += 2
    result = np.zeros(sh)
    result[..., :-2] = coef
    result[..., 0] = 2 * coef[..., 0]
    result = 0.5 * (result[..., :-2] - result[..., 2:])
    return result


def chebt2chebv(coef):
    r"""
    This method convert coefficients of Chebyshev polynomials of the
    first kind to Chebyshev polynomials of the fourth kind.

    Parameters
    ----------
    coef : array_like
        The coefficients to convert.

    Returns
    -------
    array_like
        The converted coefficients

    Notes
    -----
    This method is based in the relation  18.9.11 found in [1, P.446]
    :math:`T_n(x)=1/2(V_n(x)+V_{n-1}(x))`. Where :math:`T_n(x)` are the Cheby
    shev polynomials of the first kind and :math:`W_n(x)` the Chebyshev polyno
    mials of the fourth kind.


    References
    ----------
    [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
    Cambridge University Press, New York, NY, 2010.

    """

    sh = list(coef.shape)
    sh[-1] += 1
    result = np.zeros(sh)
    result[..., :-1] = coef
    result[..., 0] = 2 * coef[..., 0]
    result = 0.5 * (result[..., :-1] + result[..., 1:])

    return result


def chebt2chebw(coef):
    r"""
    This method convert coefficients of Chebyshev polynomials of the
    first kind to Chebyshev polynomials of the fourth kind.

    Parameters
    ----------
    coef : array_like
        The coefficients to convert.

    Returns
    -------
    array_like
        The converted coefficients

    Notes
    -----
    This method is based in the relation  18.9.11 found in [1, P.446]
    :math:`T_n(x)=1/2(W_n(x)-W_{n-1}(x))`. Where :math:`T_n(x)` are the Cheby
    shev polynomials of the first kind and :math:`W_n(x)` the Chebyshev polyno
    mials of the fourth kind.


    References
    ----------
    [1] F.W.J. Olver et al., editors. NIST Handbook of Mathematical Functions.
    Cambridge University Press, New York, NY, 2010.

    """

    sh = list(coef.shape)
    sh[-1] += 1
    result = np.zeros(sh)
    result[..., :-1] = coef
    result[..., 0] = 2 * coef[..., 0]
    result = 0.5 * (result[..., :-1] - result[..., 1:])

    return result


def chebt2kind(c, kind=2):
    r"""
    Convert Chebyshev of the first kind on another kind.

    Parameters
    ----------
    c : ndarray
        An array with the coefficients of a polynomial in ChebyshevT basis.
    kind : int, optional
        The kind to convert the coefficients. The default is 2.

    Raises
    ------
    ValueError
        When the kind is not 2,3 or 4.

    Returns
    -------
    res : ndarray
        The  coefficients in the ``kind`` basis.

    """
    switch = {2: chebt2chebu(c), 3: chebt2chebv(c), 4: chebt2chebw(c)}
    res = switch.get(kind, None)
    if res is None:
        raise ValueError(f"'kind' must be an integer 1,2 or 3, was given {kind} ")

    return res


def chebw2chebu(coef):
    r"""
    This method convert coefficients of Chebyshev polynomials of the
    fourth kind to Chebyshev polynomials of the second  kind.

    Parameters
    ----------
    coef : array_like
        The coefficients to convert.

    Returns
    -------
    array_like
        The converted coefficients

    Notes
    -----
    This method is based in the relation :math:`W_n(x)=U_n(x)+U_{n-1}(x)`. Whe
    re :math:`W_n(x)` are the Chebyshev polynomials of the fourth kind and
    :math:`U_n(x)` the Chebyshev polynomials of the second kind.


    References
    ----------
    [1] Kamal Aghigh, et al. A survey on third and fourth kind of Chebyshev
    polynomials and their applications. Journal of Applied Mathematics and
    Computation, 2008.

    """

    sh = list(coef.shape)
    sh[-1] += 1
    result = np.zeros(sh)
    result[..., :-1] = coef

    return result[..., :-1] + result[..., 1:]


def chebv2chebu(coef):
    r"""
    This method convert coefficients of Chebyshev polynomials of the
    third kind to Chebyshev polynomials of the second  kind.

    Parameters
    ----------
    coef : array_like
        The coefficients to convert.

    Returns
    -------
    array_like
        The converted coefficients

    Notes
    -----
    This method is based in the relation :math:`V_n(x)=U_n(x)-U_{n-1}(x)`. Whe
    re :math:`W_n(x)` are the Chebyshev polynomials of the fourth kind and
    :math:`U_n(x)` the Chebyshev polynomials of the second kind.


    References
    ----------
    [1] Kamal Aghigh, et al. A survey on third and fourth kind of Chebyshev
    polynomials and their applications. Journal of Applied Mathematics and
    Computation, 2008.

    """

    sh = list(coef.shape)
    sh[-1] += 1
    result = np.zeros(sh)
    result[..., :-1] = coef

    return result[..., :-1] - result[..., 1:]


def ultraS_convertmat(n, k1, k2):
    """
    Conversion matrix used in the ultraspherical spectral method.
    computes the N-by-N matrix realization of the
    conversion operator between two bases of ultraspherical Polynomials.  The
    matrix S maps N coefficients in a C^{(K1)} basis to N coefficients in a
    C^{(K2 + 1)} basis, where, C^{(K)} denotes ultraspherical Polynomial basis
    with parameter K.  If K2 < K1, S is the N-by-N identity matrix.
    This function is meant for internal use only and does not validate its
    inputs.



    Parameters
    ----------
    n : int
        The dimension of the conversion matrix
    k1 :  int
        The parameter in the the first Gegenbauer basis C^{(k1)}

    alpha2 : int
        The parameter in the the first Gegenbauer basis C^{(k2)}

    Returns
    -------
    array:like
        The conversion matrix used in the ultraspherical basis.

    Notes
    -----
    Based on chebfun, Copyright 2017 by The University of Oxford and
    The Chebfun Developers

    """
    S = speye(n)

    for s in np.arange(k1, k2 + 1):
        S = ultraS_spconvert(n, s) @ S
    return S


def ultraS_spconvert(n, lam):
    """
    SPCONVERT   Compute sparse representation for conversion operators.
    CONVERMAT(N, LAM) returns the truncation of the operator that transforms
    C^{lam} (Ultraspherical Polynomials) to C^{lam+1}.  The truncation gives
    back a matrix of size n x n.
    Relation is: C_n^(lam) = (lam/(n+lam))(C_n^(lam+1) - C_{n-2}^(lam+1))



    Parameters
    ----------
    n : integer
        The dimension of the matrix
    lam : numeric
        The parameter of Gegenbauer basis in C^{(lam)}



    Returns
    -------
    array_like
        The matrix representing the conversion operator.

    Notes
    -----
    Based on chebfun, Copyright 2017 by The University of Oxford and
    The Chebfun Developers

    """
    if lam == 0:
        return spdiags(
            np.array([[1, 0.5] + [0.5] * (n - 2), [0, 0] + [-0.5] * (n - 2)]),
            [0, 2],
            n,
            n,
        )
    else:
        dg = lam / (lam + np.arange(2, n))
        return spdiags(
            np.array(
                [
                    np.concatenate(([1, lam / (lam + 1)], dg)),
                    np.concatenate(([0, 0], -dg)),
                ]
            ),
            [0, 2],
            n,
            n,
        )


def ultraS_difmat(n, m=1):
    """
    DIFFMAT   Differentiation matrices for ultraspherical spectral method.
    returns the differentiation matrix that takes N Chebyshev
    coefficients and returns N C^{(M)} coefficients that represent the derivative
    of the Chebyshev series. Here, C^{(K)} is the ultraspherical Polynomial basis
    with parameter K.
    Parameters
    ----------
    n : int
        The dimension of the matrix
    m : number, optional
        The parameter of the ultraspherical basis. The default is 1.

    Returns
    -------
    array:like
        the differentiation matrix

    Notes
    -----
    Based on chebfun, Copyright 2017 by The University of Oxford and
    The Chebfun Developers


    """

    # Create the differentiation matrix
    if m > 0:
        D = spdiags(np.arange(n), 1, n, n)
        for i in range(1, m):
            D = spdiags([2 * i] * (n), 1, n, n) @ D
        return D
    else:
        return speye(n)


def ultraS_multmat(n, p, lam):
    a = np.array(p)

    # Multiplying by a scalar is easy
    if a.size == 1:
        return a * speye(n)

    # Prolong or truncate the coefficients
    if a.size < n:
        a = np.concatenate((a, [0] * (n - a.size)))  # Prolong
    else:
        a = a[:n]  # Truncate

    # Multiplication in ChebyshevT Coefficients
    if lam == 0:
        a = a / 2
        M = csr_matrix(toeplitz(np.r_[2 * a[0], a[1:]], np.r_[2 * a[0], a[1:]]))
        H = csr_matrix(hankel(a[1:]))

        M[1 : a.size, : a.size - 1] += H
        return M

    # Multiplication in ChebyshevU coefficients
    elif lam == 1:
        M = csr_matrix(toeplitz(np.r_[2 * a[0], a[1:]], np.r_[2 * a[0], a[1:]])) / 2
        M[: a.size - 2, : a.size - 2] -= csr_matrix(hankel(a[2:] / 2))
        return M
    else:
        # Want the C^{lam}C^{lam} Cheb Multiplication matrix.

        # Convert ChebT of a to ChebC^{lam}
        a = ultraS_convertmat(n, 0, lam - 1) @ a
        m = 2 * n
        M0 = speye(m)
        d1 = np.r_[1, 2 * lam : 2 * lam + m - 1] / np.r_[1, 2 * np.r_[lam + 1 : lam + m]]
        d2 = np.r_[1 : m + 1] / (2 * np.r_[lam : lam + m])
        B = np.r_["0,2", d2, [0] * m, d1]
        Mx = spdiags(B, [-1, 0, 1], m, m)

        M1 = 2 * lam * Mx

        # Construct the multiplication operator by a three-term recurrence.
        M = a[0] * M0
        M += a[1] * M1
        for i in range(a.size - 2):
            M2 = 2 * (i + 1 + lam) / (i + 2) * Mx @ M1 - (i + 2 * lam) / (i + 2) * M0
            M += a[i + 2] * M2
            M0 = M1
            M1 = M2
            if (np.abs(a[i + 3 :]) < np.spacing(1)).all():
                break
        return M.tocsr()[:n, :n]


def standard_chop(coef, tol):
    if tol >= 1:
        return 1

    n = len(coef)
    cutoff = n

    if n < 17:
        return n
    b = np.abs(coef)
    m = b[-1] * np.ones(n)

    for i in range(n - 2, -1, -1):
        m[i] = np.maximum(b[i], m[i + 1])

    if m[0] == 0:
        return 1

    envelope = m / m[0]

    for i in range(2, n):
        i2 = round(1.25 * i + 5)
        if i2 > n:
            # There is no plateau
            return cutoff

        e1 = envelope[i - 1]
        e2 = envelope[i2 - 1]
        r = 3 * (1 - np.log(e1) / np.log(tol))
        plateau = (e1 == 0) or (e2 / e1 > r)
        if plateau:
            plateau_point = i - 1
            break

    if envelope[plateau_point - 1] == 0:
        cutoff = plateau_point
    else:
        i3 = np.sum(envelope >= tol ** (7 / 6))
        if i3 < i2:
            i2 = i3 + 1
            envelope[i2 - 1] = tol ** (7 / 6)
        cc = np.log10(envelope[:i2])

        cc += np.linspace(0, (-1 / 3) * np.log10(tol), i2)
        d = np.argmin(cc)
        cutoff = np.maximum(d, 1)
    return cutoff


def family_basis(family, domain, **kwargs):
    """Returns the corresponding polynomial family"""
    if isinstance(family, str):
        if family not in BASES:
            raise ValueError(f"Polynomial family {family} not known")

        return BASES[family](domain=domain, **kwargs)

    if isinstance(family, T3Basis):
        return family

    raise ValueError(f"Polynomial family {family} of the wrong type")


BASES = {
    "ChebyshevT": ChebyshevT,
    "ChebyshevU": ChebyshevU,
    "ChebyshevV": ChebyshevV,
    "ChebyshevW": ChebyshevW,
    "LegendreP": LegendreP,
    "GegenbauerC": GegenbauerC,
    "BesselY": BesselY,
    "HermiteH": HermiteH,
    "LaguerreL": LaguerreL,
    "PowerX": PowerX,
}
