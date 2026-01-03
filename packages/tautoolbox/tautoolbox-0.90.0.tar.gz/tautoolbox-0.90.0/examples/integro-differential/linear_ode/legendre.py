import matplotlib.pyplot as plt
import numpy as np

from tautoolbox import tau
from tautoolbox.functions import diff, linspace

# Parameter of the problem
a = 0.4


def equation(x, y):
    return (
        (a**4 - 4 * a**3 * x + 4 * a**2 * x**2 + 2 * a**2 - 4 * a * x + 1) * diff(y, 2)
        - a * (-2 * a * x + a**2 + 1) * diff(y)
        - 2 * a**2 * y
    )


def conditions(y):
    return [y(-1) - 1 / (1 + a), y(1) - 1 / (1 - a)]


domain = [-1, 1]
options = tau.settings(degree=50)

problem = tau.problem(equation, domain, conditions, options)
yn = tau.solve(problem)[0]

# plot solution
xx = linspace(yn)
plt.semilogy(xx, np.abs(yn(xx) - (1 - 2 * a * xx + a**2) ** -0.5))
plt.show()
