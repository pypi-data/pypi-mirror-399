import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

#  Poisson equation with zero Dirichlet conditions: u(+-1,y)=u(x,+-1)=0
#  lap(u) -1 =0,  in [[-1, 1],[-1, 1]]                      #

problem = tau.problem(lambda u: u.laplacian() - 1, [[-1, 1], [-1, 1]])
problem.bc = 0

u = tau.solve(problem)

# Plot
x, y = np.linspace(*u.domain[0], 100), np.linspace(*u.domain[1], 100)
fig = plt.figure()
ax = u.plot(cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")

plt.show()
