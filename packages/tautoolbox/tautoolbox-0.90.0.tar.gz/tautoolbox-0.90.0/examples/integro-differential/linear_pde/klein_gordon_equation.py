import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

# Klein-Gordon equation
#   diif(u,0,2) -diff(u,2,0) + 5u=0
#   lbc=0, rbc=0, dbc=[u-np.exp(-30*x**2), u.diff()]

problem = tau.problem(
    lambda u: u.diff((0, 2)) - u.diff((2, 0)) + 5 * u, domain=[[-1, 1], [0, 3]]
)
problem.lbc = problem.rbc = 0
# problem.dbc = lambda x, u: [u - (-30 * x**2).exp(), u.diff()]
# here the first functions means dirichlet boundary condition and the second
# function means neuman boundary conditions
problem.dbc = [lambda x: np.exp(-30 * x**2), lambda x: 0]

u = tau.solve(problem)

ax = u.plot()

ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.locator_params(nbins=5)
plt.show()
