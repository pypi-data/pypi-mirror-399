# Describe the problem to be solved
import matplotlib.pyplot as plt

from tautoolbox import tau
from tautoolbox.functions import cos, diff, exp, fred, sin, sinh

# Set the problem
equation = [
    lambda x, y: exp(x) * diff(y, 2)
    + cos(x) * diff(y)
    + sin(x) * y
    + fred(y, lambda x, t: exp((x + 1) * t)),
    lambda x: (cos(x) + sin(x) + exp(x)) * exp(x) + 2 * sinh(x + 2) / (x + 2),
]
conditions = [
    lambda y: y(1) + y(-1) - exp(1) - exp(-1),
    lambda y: y(1) + y(-1) - diff(y, 1, -1) - exp(1),
]
options = tau.settings(basis="ChebyshevT", degree=20)
problem = tau.problem(equation, [-1, 1], conditions, options)

# Solve the problem
[yn, info, residual, tauresidual] = tau.solve(problem)
yn.plot()
plt.show()
