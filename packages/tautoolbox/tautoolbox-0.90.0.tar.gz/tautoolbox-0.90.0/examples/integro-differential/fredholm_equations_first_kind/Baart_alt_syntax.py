import matplotlib.pyplot as plt
from numpy import pi

from tautoolbox import tau
from tautoolbox.functions import cos, exp, sin, sinh

# here t is the dependent variable and y is the operator
equation = [
    lambda t, y: y.fred(lambda s, t: exp(s * cos(t)), domain=[0, pi / 2]),
    lambda s: 2 * sinh(s) / s,
]

# define problem
problem = tau.problem(equation, domain=[0, pi])

# solve the problem
p1 = tau.solve(problem, alpha=0.01)  #  solve using the TSVE method (default)
p2 = tau.solve(problem, method="tr", alpha=0.01)  # solve using Tikhonov regularization

# True solution
f = tau.polynomial(sin, domain=problem.domain)

# Evaluate the relative error for each solution
rel_error_TSVE = (p1 - f).norm() / f.norm()
rel_error_tikhonov = (p2 - f).norm() / f.norm()

print(f"TSVE:                    relative error {rel_error_TSVE:.2%}")
print(f"Tikhonov regularization: relative error {rel_error_tikhonov:.2%}")

# plots
plt.figure()
plt.title("Baart problem")
f.plot(label="exact")
p1.plot(label="TSVE")
p2.plot(label="Tikhonov")
plt.legend()

plt.show()
