import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

problem = tau.problem(
    lambda u: u.diff((0, 1)) - 0.1 * u.diff((2, 0)) - u.diff((1, 0)),
    domain=[[-3, 3], [0, 6]],
)
problem.dbc = lambda x: np.sin(np.pi * x) * (x / 6 + 1 / 2) ** 2
problem.rbc = 0
problem.lbc = "neumann"  # or  lambda y, u: u.diff()

u = tau.solve(problem)

fig = plt.figure(figsize=(6, 6))
ax = u.plot()
ax.view_init(elev=20, azim=-130)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.locator_params(nbins=5)
plt.show()
