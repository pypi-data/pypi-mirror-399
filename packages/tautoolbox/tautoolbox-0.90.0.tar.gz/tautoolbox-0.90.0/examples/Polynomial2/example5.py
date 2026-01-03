import numpy as np
from matplotlib import pyplot as plt
from scipy.special import airy

from tautoolbox.polynomial import Polynomial2

plt.style.use("ggplot")

f_str = "real(airy(5 * (x + y^2)) * airy(-5 * (x^2 + y^2)))"

optx = {"basis": "LegendreP"}


def f(x, y):
    return np.real(airy(5 * (x + y**2))[0] * airy(-5 * (x**2 + y**2))[0])


p = Polynomial2(f)

# Plot of the Polynomial2 approximation
fig = plt.figure(figsize=(12, 6))
fig.suptitle(
    f"Approximation of ${f_str}$ by the $P(x,y)$ polynomial",
    size=14,
)

ax1 = fig.add_subplot(121, projection="3d")
p.plot(ax=ax1, cmap="ocean")
ax1.locator_params(axis="z", nbins=3)
ax1.locator_params(axis="x", nbins=3)
ax1.locator_params(axis="y", nbins=3)
ax1.set_title("Approximation")

# Contour plot of the aproximation
ax2 = fig.add_subplot(122)
p.contour(ax=ax2, pivots=True)
ax2.locator_params(axis="x", nbins=5)
ax2.locator_params(axis="y", nbins=5)
ax2.set_aspect("equal", adjustable="box")
ax2.set_title("Contour plot and pivots")

plt.show()
