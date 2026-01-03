import matplotlib.pyplot as plt
import numpy as np

from tautoolbox import tau
from tautoolbox.functions import diff, linspace


# Example of a differential equation with conditions given at the boundary
# equation = "diff(y, 2) + y=0"
def equation(x, y):
    return diff(y, 2) + y


def conditions(y):
    return [y(0) - 1, y.diff(1, 2 * np.pi)]


domain = [0, 2 * np.pi]
options = tau.settings(degree=20, basis="ChebyshevU")
problem = tau.problem(equation, domain, conditions, options)
[yn, info, residual, tauresidual] = tau.solve(problem)

xx = linspace(yn, 100)
y_p, residual_p, tauresidual_p = (yn(xx), residual(xx), tauresidual(xx))

fig = plt.figure(figsize=plt.figaspect(0.5))
ax = fig.add_subplot(1, 3, 1, title="Solution")
ax.plot(xx, y_p)
ax = fig.add_subplot(1, 3, 2, title="residual")
ax.plot(xx, residual_p)
ax = fig.add_subplot(1, 3, 3, title="tauresidual")
ax.plot(xx, tauresidual_p)
plt.show()
