import numpy as np
from matplotlib import pyplot as plt

from tautoolbox.polynomial import ChebyshevT, Polynomial2

plt.style.use("ggplot")

f_str = "g(x,y) = (1+10(x+2y)^2)^{-1}"

basis_x = ChebyshevT(domain=[0, 1])
basis_y = ChebyshevT(domain=[0, 1])


def f(x, y):
    return (1 + 10 * (x + 2 * y) ** 2) ** -1


p = Polynomial2(f, bases=(basis_x, basis_y))
x = np.linspace(*basis_x.domain, 100)
y = np.linspace(*basis_y.domain, 100)
xx, yy = np.meshgrid(x, y)
ex = f(xx, yy)  # Exact values evaluated on the grid
ap = p.evalm(x, y)  # Approx. Pol. evaluated  at the grid
err = np.abs(ex - ap)  # Accuracy of the approximation

# Plot aproximation and accuracy

# Approximation
plt.close()
fig = plt.figure(figsize=(12, 6))
fig.suptitle(f"Approximation of ${f_str}$ by the $P(x,y)$ polynomial", size=14)

ax = fig.add_subplot(121, projection="3d")
p.plot(ax=ax, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$z$")
ax.set_title("$z=P(x,y)$")
ax.locator_params(nbins=5)
ax.set_title("Approximation")

# Plot of exact solution
ax = fig.add_subplot(122, projection="3d")

ax.plot_surface(xx, yy, err, cmap="ocean")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.set_zlabel("$z$")
ax.set_title("$z=|P(x,y) -f(x,y)|$")
ax.locator_params(nbins=5)
ax.set_facecolor("w")
ax.set_title("Error")

plt.show()
