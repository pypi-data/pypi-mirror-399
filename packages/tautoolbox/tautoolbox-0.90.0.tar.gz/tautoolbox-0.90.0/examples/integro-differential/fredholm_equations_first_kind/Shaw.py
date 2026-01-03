import matplotlib.pyplot as plt
from numpy import pi as π

from tautoolbox import tau
from tautoolbox.functions import cos, exp, sin

# Shawn problem

# set the problem
a1, a2, c1, c2, t1, t2 = 2, 1, 6, 2, 0.8, -0.5

# true solution
f = tau.polynomial(
    lambda t: a1 * exp(-c1 * (t - t1) ** 2) + a2 * exp(-c2 * (t - t2) ** 2),
    domain=[-π / 2, π / 2],
)

u = tau.polynomial(lambda s, t: π * (sin(s) + sin(t)), domain=[-π / 2, π / 2])
q = tau.polynomial(lambda x: (sin(x) / x) ** 2, domain=[-2, 2])
qu = tau.polynomial(lambda s, t: q(u(s, t)), domain=[-π / 2, π / 2])
cs = tau.polynomial(lambda s, t: cos(s) + cos(t), domain=[-π / 2, π / 2])
kernel = cs * qu
g = (kernel.T * f).sum(axis=1)

alpha = 0.0  # no noise on the rhs
p1 = kernel.fredholm1(g, alpha=alpha)  # solve with the TSVE method
p2 = kernel.fredholm1(g, method="tr", alpha=alpha)  # solve using Tikhonov regularization

# Evaluate the relative error
rel_error_TSVE = (p1 - f).norm() / f.norm()
rel_error_tikhonov = (p2 - f).norm() / f.norm()

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plots
plt.figure()
plt.title("Shaw problem")
f.plot(label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
