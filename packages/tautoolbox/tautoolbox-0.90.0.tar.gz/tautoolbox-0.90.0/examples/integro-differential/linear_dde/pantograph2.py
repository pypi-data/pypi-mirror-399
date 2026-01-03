import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm

from tautoolbox import tau
from tautoolbox.functions import diff, exp

# Nonhomogeneous first-order linear pantograph differential equation
# y′(x)+y(x)−0.1y(qx) = −0.1e−0.2x, 0≤x≤1, y(0) = 1, q = 0.2, y(x)= e^(−x)

# set parameters
n = 12
q = 0.2
domain = [0, 1]


equation = [
    lambda x, y: diff(y) + y(x) - 0.1 * y(q * x),
    lambda x: -0.1 * exp(-0.2 * x),
]


def conditions(y):
    return y(0) - 1


options = tau.settings(degree=n - 1, basis="ChebyshevT")
problem = tau.problem(equation, domain, conditions, options)

# solve the problem
yn, *info = tau.solve(problem)


# compare the approximation with the analytic solution
def exact(x):
    return np.exp(-x)


xx = np.linspace(domain[0], domain[1])

plt.plot(xx, exact(xx) - yn(xx), linewidth=1.6)
plt.title(f"norm of the error is {norm(yn(xx) - exact(xx)):.1e}")
plt.show()
