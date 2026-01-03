import matplotlib.pyplot as plt
import numpy as np

from tautoolbox import tau
from tautoolbox.functions import diff

ode = [
    lambda x, y: diff(y[1], 2) + diff(y[2], 2) + y[1] + y[2],
    lambda x, y: diff(y[1], 2) - diff(y[2], 2) - diff(y[1]) - diff(y[2]),
]


# conditions = ["y1(0)=0", "y2(0)=1", "y1'(0)=1", "y2'(0)=0"]
def conditions(y):
    return [
        y[1](0),
        y[2](0) - 1,
        y[1].diff(1, 0) - 1,
        y[2].diff(1, 0),
    ]


domain = [0, 2 * np.pi]
options = tau.settings(degree=20, basis="LegendreP")
problem = tau.problem(ode, domain, conditions, options)
yn = tau.solve(problem)

solution = tau.polynomial([np.sin, np.cos], domain=domain, options=options)

fig = plt.figure(figsize=(12, 4))

# Plot approximate solution
ax = fig.add_subplot(121)
yn.plot(ax=ax)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.legend(["$y_1 $ ", "$y_2$"])
ax.set_title("Approximate Solution")

# Plot error
ax = fig.add_subplot(122)
(yn - solution).plot(ax=ax)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.legend(["$y_1 $ ", "$y_2$"])
ax.set_title("Error")

plt.show()
