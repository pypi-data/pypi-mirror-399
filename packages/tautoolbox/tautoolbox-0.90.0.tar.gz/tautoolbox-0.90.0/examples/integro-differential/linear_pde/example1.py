import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

# lap(u) =0 in [[-1,1]]*2
# exact solution is f(x,y)= exp(x-y)cos(x+y)


def f(x, y):
    return np.exp(x - y) * np.cos(x + y)


problem = tau.problem(lambda u: u.laplacian(), domain=[[-1, 2], [-1, 1]], conditions=f)

u = tau.solve(problem)

x = np.linspace(*u.domain[0])
y = np.linspace(*u.domain[1])
xx, yy = np.meshgrid(x, y)

ex = f(xx, yy)  # Exact values are evaluated on the grid
ap = u.evalm(x, y)
err = ex - ap

# Exact solution
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(121, projection="3d")
u.plot(ax=ax, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.set_title("$u=P(x,y)$")
ax.locator_params(nbins=5)

# Error
ax = fig.add_subplot(122, projection="3d")
ax.plot_surface(xx, yy, err, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.set_title("$u=P(x,y) -f(x,y)$")
ax.locator_params(nbins=5)
ax.set_facecolor("w")
plt.show()
