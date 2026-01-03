import matplotlib.pyplot as plt

from tautoolbox import tau
from tautoolbox.functions import diff

# First-order linear homogeneous pantograph differential equation
# y′(x)+40y(x)−20y(qx) = 0, x>0, y(0) = 1, 0 < q < 1

# specify the problem
n = 25  # degree approximation
q = 0.9  # equation parameters
domain = [0, 3]  # domain


# differential equation
def equation(x, y):
    return diff(y) + 40 * y - 20 * y(q * x)


# initial condition
def conditions(y):
    return y(0) - 1


# set the problem in Tau toolbox and solve
options = tau.settings(degree=n - 1)  # set options
problem = tau.problem(equation, domain, conditions, options)
yn, *info = tau.solve(problem)

yn.plot()
plt.show()
