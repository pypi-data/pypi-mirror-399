# Describe the problem to be solved
import matplotlib.pyplot as plt
import numpy as np

from tautoolbox import tau
from tautoolbox.functions import cos, diff, exp, fred, linspace, sin, sinh

equation = [
    lambda x, y: (
        exp(x) * diff(y, 2)
        + cos(x) * diff(y)
        + sin(x) * y
        + fred(y, lambda x, t: exp((x + 1) * t))
    ),
    lambda x: (cos(x) + sin(x) + exp(x)) * exp(x) + 2 * sinh(x + 2) / (x + 2),
]
conditions = [
    lambda y: y(1) + y(-1) - np.exp(1) - exp(-1),
    lambda y: y(1) + y(-1) - diff(y, 1, -1) - exp(1),
]
options = tau.settings(basis="ChebyshevT", degree=20)
problem = tau.problem(equation, [-1, 1], conditions, options)
[yn, info, residual, tauresidual] = tau.solve(problem)

data = np.array(
    [
        [-1.00, 0.36788, 0.36788, 4.66223e-10],
        [-0.75, 0.47237, 0.47237, 1.03457e-09],
        [-0.25, 0.77880, 0.77880, 1.78144e-09],
        [0.25, 1.28403, 1.28403, 1.63789e-09],
        [0.75, 2.11700, 2.11700, 9.42890e-10],
        [1.00, 2.71828, 2.71828, 4.66223e-10],
    ]
)

xx = linspace(yn, 100)
yy = yn(xx)

plt.semilogy(xx, abs(yy - np.exp(xx)), label="Tau Toolbox")
plt.plot(data[:, 0], data[:, -1], ls=":", label="AliAbadi (2002)")
plt.legend(loc="center right")
plt.show()
