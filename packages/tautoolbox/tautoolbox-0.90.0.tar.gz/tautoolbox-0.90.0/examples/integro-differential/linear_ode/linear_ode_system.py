import matplotlib.pyplot as plt

from tautoolbox import tau
from tautoolbox.functions import diff

# Describe the problem to be solved
equations = (
    lambda x, y: y[2] - diff(y[1]),
    lambda x, y: y[3] - diff(y[2]),
    (
        lambda x, y: (
            (x**2 + 1) * diff(y[3]) - (x**2 + 3 * x) * diff(y[2]) + 5 * x * y[2] - 5 * y[1]
        ),
        lambda x: 60 * x**2 - 10,
    ),
)

domain = [-1, 1]


def conditions(y):
    return (y[1](-1) - 4, y[2](1) - 2, y[3](0))


options = tau.settings(degree=10)
problem = tau.problem(equations, domain, conditions, options)
yn = tau.solve(problem)

# exact solution
y = tau.polynomial((lambda x: x**5 - 3 * x + 2, lambda x: 5 * x**4 - 3, lambda x: 20 * x**3))
# the error will be also a Polynomial
error = y - yn

# evaluate the error over the interval
xx = yn.linspace(100)
yy = yn(xx)
y_error = error(xx)

# Plot both the solution and the error for all (3) components
fig = plt.figure(figsize=plt.figaspect(0.5))
ax = fig.add_subplot(1, 2, 1, title="Solution")
ax.plot(xx, yy[0], label="$y_1$", color="red")
ax.plot(xx, yy[1], label="$y_2$", color="green")
ax.plot(xx, yy[2], label="$y_3$", color="blue")
ax.legend()

ax = fig.add_subplot(1, 2, 2, title="Error")
ax.plot(xx, y_error[0], label="$y_1$ error", color="red")
ax.plot(xx, y_error[1], label="$y_2$ error", color="green")
ax.plot(xx, y_error[2], label="$y_3$ error", color="blue")
ax.legend(loc="lower right")

plt.show()
