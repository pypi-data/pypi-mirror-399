import matplotlib.pyplot as plt
from numpy import pi

from tautoolbox import tau
from tautoolbox.functions import sin

# Gravity problem

# true solution
f = tau.polynomial(lambda t: sin(pi * t) + 0.5 * sin(2 * pi * t), domain=[0, 1])

# set the problem
d = 0.25
kernel = tau.polynomial(lambda s, t: d * (d**2 + (s - t) ** 2) ** (-3 / 2), domain=[0, 1])
g = (kernel * f).sum(axis=1)

alpha = 1e-2  # noise rhs
p1 = kernel.fredholm1(g, alpha=alpha)  # solve with the TSVE method
p2 = kernel.fredholm1(g, method="tr", alpha=alpha)  # using Tikhonov regularization

# Evaluate the relative error
rel_error_TSVE = (p1 - f).norm() / f.norm()
rel_error_tikhonov = (p2 - f).norm() / f.norm()

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plots
plt.figure()
plt.title("Gravity problem")
f.plot(label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
