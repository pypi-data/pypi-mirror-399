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

import numbers
from copy import deepcopy

import numpy as np

from ..polynomial import Polynomial, Polynomial2


class Operator:
    """Class that allows to transform a differential problem into
    an algebraic formulation"""

    def __init__(self, basis, n, nequations=1):
        self.basis = basis
        self.domain = basis.domain
        self.nequations = nequations

        self.n = n
        if self.nequations == 1:
            self.activeVar = [1]
            self.opMat = [np.eye(n)]

        else:
            self.activeVar = [False] * self.nequations
            self.opMat = [None] * self.nequations

        self.hdiff = [None] * self.nequations
        self.odiff = [None] * self.nequations
        self.hasIntegral = [False] * self.nequations

        for k in range(self.nequations):
            self.hdiff[k] = np.zeros((1, 2), dtype=int)
            self.odiff[k] = 0

        self.N = self.basis.matrixN(self.n)

        # Non trivial (different from the identity) arguments
        self.ntArguments = [[]] * self.nequations

        # Number of terms in the equation
        self.n_terms = 1
        # List of kernels (Fredholm and Volterra, respectively)
        self.fred_kernels = []
        self.volt_kernels = []

    def diff(self, order=1):
        result = deepcopy(self)

        for k in range(result.nequations):
            if result.activeVar[k] == 0:
                continue
            result.odiff[k] += order
            for i in range(result.hdiff[k].shape[0]):
                result.hdiff[k][i, 0] += order

            result.opMat[k] = np.linalg.matrix_power(result.N, order) @ result.opMat[k]
        return result

    def integral(self, order=1):
        result = deepcopy(self)

        matO = self.basis.matrixO(self.n)
        for k in range(result.nequations):
            if result.activeVar[k] == 0:
                continue
            result.odiff[k] -= order
            for i in range(result.hdiff[k].shape[0]):
                result.hdiff[k][i, 0] -= order
            result.opMat[k] = np.linalg.matrix_power(matO, order) @ result.opMat[k]
            result.hasIntegral[k] = True
        return result

    def fred(self, K=lambda x, y: 1, domain=None):
        result = deepcopy(self)

        if not domain:
            domain = self.domain

        if callable(K):
            K = Polynomial2(K, bases=self.basis)
        result.fred_kernels.append(K)
        K = K.coeff

        Pa, Pb = result.basis.vander(domain, self.n)
        for k in range(result.nequations):
            if self.activeVar[k] == 0:
                continue
            result.odiff[k] -= 1
            for i in range(result.hdiff[k].shape[0]):
                result.hdiff[k][i, 0] -= 1
                result.hdiff[k][i, 1] += K.shape[0]

            # Compute the fredholm terms
            opmat = np.zeros((result.n, result.n))

            matO = result.basis.matrixO(self.n)
            for i in range(K.shape[1]):
                for j in range(K.shape[0]):
                    coeff = np.zeros(j + 1)
                    coeff[j] = 1
                    PjM = result.basis.polyvalmM(coeff, self.n)
                    opmat += K[j, i] * (Operator.epow(i, result.n) @ [Pb - Pa] @ matO @ PjM)
            result.opMat[k] = opmat @ result.opMat[k]
            result.hasIntegral[k] = True
        return result

    def volt(self, K=1, domain=None):
        result = deepcopy(self)

        if not domain:
            domain = result.domain
        if callable(K):
            K = Polynomial2(K, bases=self.basis).coef

        self.volt_kernels.append(K)
        Pa = result.basis.vander(domain[0], self.n)
        for k in range(result.nequations):
            if self.activeVar[k] == 0:
                continue
            result.odiff[k] -= 1
            for i in range(result.hdiff[k].shape[0]):
                result.hdiff[k][i, 0] -= 1
                result.hdiff[k][i, 1] += K.shape[0]

            # Compute the fredholm terms
            matO = result.basis.matrixO(self.n)
            firstrow = np.zeros(result.n)
            for j in range(result.n - 1):
                firstrow[j] = result.basis(np.r_[0, matO[1 : j + 2, j]], domain[0])

            matO[0, :] = firstrow
            opmat = np.zeros((result.n, result.n))
            for i in range(K.shape[1]):
                coeff = np.zeros(i + 1)
                coeff[i] = 1
                PiM = result.basis.polyvalmM(coeff, self.n)
                for j in range(K.shape[0]):
                    coeff = np.zeros(j + 1)
                    coeff[j] = 1
                    PjM = result.basis.polyvalmM(coeff, self.n)
                    opmat += K[j, i] * ((PiM - Operator.epow(i, result.n) @ Pa) @ matO @ PjM)
            result.opMat[k] = opmat @ result.opMat[k]
            result.hasIntegral[k] = True
        return result

    def __add__(self, rhs):
        result = deepcopy(self)

        if all([isinstance(result, Operator), isinstance(rhs, Operator)]):
            for k in range(result.nequations):
                if result.activeVar[k] and rhs.activeVar[k]:
                    result.hdiff[k] = np.r_[result.hdiff[k], rhs.hdiff[k]]
                    result.odiff[k] = max(result.odiff[k], rhs.odiff[k])
                    result.opMat[k] = result.opMat[k] + rhs.opMat[k]
                    result.hasIntegral[k] = result.hasIntegral[k] or rhs.hasIntegral[k]
                    result.ntArguments[k].extend(rhs.ntArguments)
                elif rhs.activeVar[k]:
                    result.activeVar[k] = 1
                    result.hdiff[k] = rhs.hdiff[k]
                    result.odiff[k] = rhs.odiff[k]
                    result.opMat[k] = rhs.opMat[k]
                    result.hasIntegral[k] = rhs.hasIntegral[k]
                    result.ntArguments[k] = rhs.ntArguments[k]
            self.n_terms += rhs.n_terms
        elif isinstance(rhs, Polynomial):
            return result
        else:
            raise TypeError("tautoolbox: you can only sum two operator objects")

        return result

    def __pos__(self):
        return deepcopy(self)

    def __neg__(self):
        result = deepcopy(self)
        for k in range(result.nequations):
            if result.activeVar[k]:
                result.opMat[k] = -result.opMat[k]
        return result

    def __sub__(self, rhs):
        return self + (-rhs)

    def __mul__(self, rhs):
        result = deepcopy(self)
        if isinstance(rhs, Operator):
            raise ValueError(
                "Tautoolbox: support for non linear terms "
                " is not yet automatic. Please linearize the equation "
            )

        if isinstance(rhs, numbers.Number):
            for k in range(result.nequations):
                if result.activeVar[k]:
                    result.opMat[k] *= rhs

        elif isinstance(rhs, Polynomial):
            for k in range(result.nequations):
                if result.activeVar[k]:
                    result.hdiff[k][-1, 1] += len(rhs.coeff)
                    result.opMat[k] = (
                        result.basis.polyvalmM(rhs.coeff, self.n) @ result.opMat[k]
                    )

        else:
            raise TypeError("An Operator can only be multiplied by a number or a Polynomial")
        return result

    def __rmul__(self, lhs):
        return self * lhs

    def __truediv__(self, rhs):
        if not isinstance(rhs, numbers.Number):
            raise TypeError("A Operator can only be divided by a scalar")

        result = deepcopy(self)
        for k in range(result.nequations):
            if result.activeVar[k]:
                result.opMat[k] = result.opMat[k] / rhs
        return result

    def opHeight(self):
        return [max(max(hd[:, 1] - hd[:, 0]), 0) for hd in self.hdiff]

    @staticmethod
    def epow(i, n):
        f = np.zeros((n, 1))
        if i >= 0 and i < n:
            f[i, 0] = 1
        return f

    def __call__(self, argument):
        """functional argument (take the Operator in the given argument)"""
        result = deepcopy(self)

        result.ntArguments.append(argument)
        if argument.degree == 1:
            a = argument(0)
            q = argument(1) - a

            # if the argument is approximatelly equal to the identity
            # function skip this (because the argument is trivial)
            if np.isclose(q, 1) and np.abs(a) < np.spacing(1):
                return result

            # Consider the dilation term in the associated operator matrix
            for k, val in enumerate(result.activeVar):
                if not val:
                    continue

                result.opMat[k] = result.basis.matrixL(result.n, a, q)

        return result

    def __getitem__(self, index):
        result = deepcopy(self)
        # if isinstance(index, slice):
        #     start = 0 if index.start == None else index.start
        #     stop = self._size if index.stop == None else index.stop
        #     step = 1 if index.step == None else index.step

        #     if type(step) == type(stop) == type(step) == int:
        #         tmp = LinkedList()
        #         f
        #     else:
        #         raise TypeError("All slice attributes must be integer or None")

        if result.nequations == 1:
            if index == 1:
                return result

            raise IndexError(
                f"Index out of range - the index must be at most {result.nequations}"
            )

        if any(result.activeVar):
            raise IndexError("Tautoolbox: operation already defined")

        if index <= result.nequations:
            result.activeVar[index - 1] = True
            result.opMat[index - 1] = np.eye(result.n)
        else:
            raise IndexError(
                f"Index out of range - the index must be at most {result.nequations}"
            )

        return result

    @property
    def mat(self):
        m = np.zeros((self.n, self.nequations * self.n))

        for k in range(self.nequations):
            if self.activeVar[k]:
                m[:, k * self.n : (k + 1) * self.n] = self.opMat[k]
        return m
