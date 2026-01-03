import matplotlib.pyplot as plt
import numpy as np

from tautoolbox import tau
from tautoolbox.functions import exp

# Wing problem

# set the problem
kernel = tau.polynomial(lambda s, t: t * exp(-s * t**2), domain=[0, 1])
t1, t2 = 1 / 3, 2 / 3


def g(s):
    return (exp(-s * t1**2) - exp(-s * t2**2)) / (2 * s)


def f(t):
    return np.logical_and(t1 < t, t < t2) * 1


x = np.linspace(*[0, 1], 100)

alpha = 1e-2  # noise rhs

# solve with TSVE and compute the relative error
p1 = kernel.fredholm1(g, alpha=alpha)
rel_error_TSVE = np.linalg.norm(p1(x) - f(x)) / np.linalg.norm(f(x))

# solve using Tikhonov regularization and compute the relative error
p2 = kernel.fredholm1(g, method="tr", alpha=alpha)
rel_error_tikhonov = np.linalg.norm(p2(x) - f(x)) / np.linalg.norm(f(x))

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plots
plt.figure()
plt.title("Wing problem")
plt.plot(x, f(x), label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
