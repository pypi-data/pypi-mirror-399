import numpy as np
from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

#  Poisson equation with zero Dirichlet conditions: u(+-1,y)=u(x,+-1)=0
#  lap(u) -2 = 0,  in [[-1, 1],[-1, 1]]
#  This is also known as the Saint Venant equation

problem = tau.problem(lambda u: u.laplacian() + 2, [[-1, 1], [-1, 1]])
problem.bc = 0

u = tau.solve(problem)

# Approximate solution
x, y = np.linspace(*u.domain[0], 100), np.linspace(*u.domain[1], 100)
xx, yy = np.meshgrid(x, y)
taupy_sol = u.evalm(x, y)

# Exact solution
k = np.arange(40)
kk = 2 * k + 1
u_ex = (
    lambda x, y: np.sum(
        (
            (-1) ** k
            / kk**3
            * (1 - np.cosh(kk * y * np.pi / 2) / np.cosh(kk * np.pi / 2))
            * np.cos(kk * x * np.pi / 2)
        )
    )
    * 32
    / np.pi**3
)
e_sol = np.zeros_like(xx)
m, n = xx.shape

for i in range(m):
    for j in range(n):
        e_sol[i, j] = u_ex(xx[i, j], yy[i, j])

fig = plt.figure(figsize=(12, 6))


err = e_sol - taupy_sol
ax = fig.add_subplot(121, projection="3d")
ax.set_facecolor("w")
u.plot(ax=ax, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.set_title("$u=P(x,y)$")
ax.locator_params(nbins=5)
# ax.set_title("Approximate")

ax = fig.add_subplot(122, projection="3d")

ax.plot_surface(xx, yy, err, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")
ax.locator_params(nbins=5)
ax.set_facecolor("w")
ax.set_title("$u=P(x,y) -f(x,y)$")
plt.show()
