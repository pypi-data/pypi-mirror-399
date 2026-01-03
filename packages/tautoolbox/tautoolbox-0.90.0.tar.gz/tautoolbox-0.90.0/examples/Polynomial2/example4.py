import numpy as np
from matplotlib import pyplot as plt

from tautoolbox.polynomial import Polynomial2

plt.style.use("ggplot")

# h(x,y) = f(x,y)*g(x,y)
#   where f(x,y) is example2 and g(x,y) is example3

f_str = r"f(x,y) = \cos(10x(1+y^2)) \cdot (1+10(x+2y)^2)^{-1}"

# Using the default basis i.e. ChebyshevT and domain i.e. [-1,1]
domain = [[-1, 1]] * 2


def f(x, y):
    return np.cos(10 * x * (1 + y**2)) * (1 + 10 * (x + 2 * y) ** 2) ** -1


p = Polynomial2(f)
x = np.linspace(*domain[0], 100)
y = np.linspace(*domain[1], 100)
xx, yy = np.meshgrid(x, y)
ex = f(xx, yy)  # Exact values evaluated on the grid
ap = p.evalm(x, y)  # Approx. Pol. evaluated  at the grid
err = np.abs(ex - ap)  # Accuracy of the approximation

# Plot of the aproximation and accuracy

# Approximation
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
