import matplotlib.pyplot as plt

from tautoolbox import tau
from tautoolbox.functions import diff, exp, fred, linspace, log

ode = [
    lambda x, y: diff(y) - y - fred(y, lambda x, t: 1 / (x + exp(t))),
    lambda x: -log((x + exp(1)) / (x + 1)),
]
condition = [lambda y: y(0) - 1]
options = tau.settings(basis="ChebyshevU", degree=20)
domain = [0, 1]
problem = tau.problem(ode, domain, condition, options)
yn = tau.solve(problem)[0]

x = linspace(yn)
print(f"Maximum absolute deviation: {max(abs(exp(x) - yn(x)))}")

plt.semilogy(x, abs(exp(x) - yn(x)))
plt.show()
