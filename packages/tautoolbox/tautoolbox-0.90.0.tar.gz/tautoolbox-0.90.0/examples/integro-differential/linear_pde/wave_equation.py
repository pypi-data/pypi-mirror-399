import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

# wave equation
#  u_yy = u_xx, x in [0, 1], y in [0,4]
#  u(x,0) =0, u_y(x,0) = pi*cos(pi*x), u(0,y) = -u(1,y) = sin(pi*y)
#  exact solution: cos(pi*x)sin(pi*t)


# exact solution
def f(x, y):
    return np.cos(np.pi * x) * np.sin(np.pi * y)


problem = tau.problem(lambda u: u.diff((0, 2)) - u.diff((2, 0)), domain=[[0, 1], [0, 4]])
problem.lbc = lambda y: np.sin(np.pi * y)
problem.rbc = lambda y: -np.sin(np.pi * y)
problem.dbc = [lambda x: 0, lambda x: np.pi * np.cos(np.pi * x)]
# dbc can also be put as
# problem.dbc = [lambda x, u: u, lambda x, u: u.diff() - np.pi * (np.pi * x).cos()]

u = tau.solve(problem)

# Plots
x = np.linspace(*u.domain[0])
y = np.linspace(*u.domain[1])
xx, yy = np.meshgrid(x, y)

ex = f(xx, yy)  # Exact values evaluated on the grid
ap = u.evalm(x, y)
err = ex - ap

# Plot of the exact solution
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(121, projection="3d")
u.plot(ax=ax, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.set_title("$u=P(x,y)$")
ax.locator_params(nbins=5)

# Plot of the error
ax = fig.add_subplot(122, projection="3d")
ax.plot_surface(xx, yy, err, cmap="winter_r")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.set_title("$u=P(x,y) -f(x,y)$")
ax.locator_params(nbins=5)
ax.set_facecolor("w")
plt.show()
