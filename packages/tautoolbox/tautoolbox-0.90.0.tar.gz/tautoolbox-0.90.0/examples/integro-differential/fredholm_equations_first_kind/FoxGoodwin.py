import matplotlib.pyplot as plt

from tautoolbox import tau

# Fox-Goodwin problem

# set the problem
kernel = tau.polynomial(lambda s, t: (s**2 + t**2) ** (1 / 2), domain=[0, 1])
g = tau.polynomial(lambda s: 1 / 3 * ((1 + s**2) ** (3 / 2) - s**3), domain=[0, 1])

p1 = kernel.fredholm1(g, alpha=0.01)  # solve with the TSVE method
p2 = kernel.fredholm1(g, method="tr", alpha=0.01)  # using the Tikhonov regularization

# true solution
f = tau.polynomial(domain=[0, 1])

# Evaluate the relative error
rel_error_TSVE = (p1 - f).norm() / f.norm()
rel_error_tikhonov = (p2 - f).norm() / f.norm()

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plots
plt.figure()
plt.title("Fox-Goodwin problem")
f.plot(label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
