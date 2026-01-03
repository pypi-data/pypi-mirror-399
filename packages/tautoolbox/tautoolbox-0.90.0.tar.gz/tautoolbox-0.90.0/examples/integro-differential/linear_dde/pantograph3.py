import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm

from tautoolbox import tau
from tautoolbox.functions import diff, exp

# Nonhomogeneous 2nd-order pantograph delay differential equation
# y''(x)−0.5y−e^(−x/2)y(x/2) = −2e^(−x), 0<x<1, y(0) = 0,
# y(1) = e^(−1), y(x) = xe^(−x)

# specify the problem
n = 15
domain = [0, 1]
equation = [
    lambda x, y: diff(y(x), 2) - 0.5 * y(x) - exp(-x / 2) * y(0.5 * x),
    lambda x: -2 * exp(-x),
]


def conditions(y):
    return [y(0), y(1) - exp(-1)]


# set the problem in Tau toolbox and solve
options = tau.settings(degree=n - 1)
problem = tau.problem(equation, domain, conditions, options)
yn, *info = tau.solve(problem)


# compare the approximation with the analytic solution
def exact(x):
    return x * np.exp(-x)


xx = np.linspace(domain[0], domain[1])

plt.plot(xx, exact(xx) - yn(xx), linewidth=1.6)
plt.title(f"norm of the error is {norm(yn(xx) - exact(xx)):.1e}")
plt.show()
