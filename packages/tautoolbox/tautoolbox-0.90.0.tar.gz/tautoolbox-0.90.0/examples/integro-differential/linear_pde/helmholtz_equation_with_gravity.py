import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

# Helmholtz equation with gravity
#  laplacian(u) - 10*y**2*u =0, in [[-1,1],[-3,0]]
#  u(+-1,y)=u(x,-3)=u(x,0)=1

optx = tau.settings(basis="ChebyshevT")
opty = tau.settings(basis="ChebyshevT")
problem = tau.problem(
    lambda x, y, u: u.laplacian() - 10 * y**2 * u,
    domain=[[-1, 1], [-3, 0]],
    options=(optx, opty),
)
problem.bc = 1

u = tau.solve(problem)

x, y = np.linspace(*u.domain[0], 100), np.linspace(*u.domain[1], 100)

# Plots
plt.figure()
ax = u.plot()
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")

plt.locator_params(nbins=5)
plt.show()
