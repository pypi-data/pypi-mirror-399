from matplotlib import pyplot as plt

from tautoolbox import tau

plt.style.use("ggplot")

# 2*d^2u/dx^2+d^2u/dy^2 - 10*x**2*u =0, in [[-1,1],[-3,0]]
# u(+-1,y)=u(x,-3)=u(x,0)=1

optx = tau.settings(basis="ChebyshevT")
opty = tau.settings(basis="ChebyshevT")
problem = tau.problem(
    lambda x, y, u: 2 * u.diff((2, 0)) + u.diff((0, 2)) - 10 * x**2 * u,
    domain=[[-1, 1], [-3, 0]],
    options=(optx, opty),
)
problem.bc = 1

u = tau.solve(problem)

# Plots
plt.figure()
ax = u.plot(cmap="ocean")
plt.locator_params(nbins=5)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$u$")

plt.show()
