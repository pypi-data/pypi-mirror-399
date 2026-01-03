import numpy as np
from matplotlib import pyplot as plt

from tautoolbox.polynomial import Polynomial2

plt.style.use("ggplot")

# f(x,y) = cos(10*x*(1+y**2))
f_str = r"f(x,y) = \cos(10x(1+y^2))"


def f(x, y):
    return np.cos(10 * x * (1 + y**2))


domain = [[0, 1]] * 2
p = Polynomial2(f, domain=domain[0])
x = np.linspace(*domain[0], 100)
y = np.linspace(*domain[1], 100)
xx, yy = np.meshgrid(x, y)
ex = f(xx, yy)  # Exact values evaluated on the grid
ap = p.evalm(x, y)  # Approx. Pol. evaluated  at the grid
err = np.abs(ex - ap)  # Accuracy of the approximation
max_err = np.max(err)  # the maximum of the

# Plot of the aproximation and accuracy

# Approximation
plt.close()
fig = plt.figure(figsize=(12, 6))
fig.suptitle(
    f"Approximation of ${f_str}$ by the $P(x,y)$ polynomial, "
    rf"$\max |P(x,y) -f(x,y)|$={max_err:.3e}",
    size=13,
)

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
print(max_err)
