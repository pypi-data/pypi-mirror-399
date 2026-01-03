import matplotlib.pyplot as plt
from numpy import pi

from tautoolbox import tau
from tautoolbox.functions import cos, exp, sin, sinh

# baart problem

# set the problem
kernel = tau.polynomial(
    lambda s, t: exp(s * cos(t)),
    domain=[[0, pi / 2], [0, pi]],
)
g = tau.polynomial(lambda s: 2 * sinh(s) / s, domain=kernel.domain[0])

p1 = kernel.fredholm1(g, alpha=0.01)  # solve using with TSVE method
p2 = kernel.fredholm1(g, method="tr", alpha=0.01)  # solve using Tikhonov regularization

# true solution
f = tau.polynomial(sin, domain=kernel.domain[1])

# Evaluate the relative error for each solution
rel_error_TSVE = (p1 - f).norm() / f.norm()
rel_error_tikhonov = (p2 - f).norm() / f.norm()

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plot
plt.figure()
plt.title("Baart problem")
f.plot(label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
