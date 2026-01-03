# y'(t) = alpha*y(t) + beta*y(t-1) + gamma*y(t + 1);
# beta = 3; gamma = -.2; alpha = m-beta*exp(-m)-gamma*exp(m)
# t \in [0,3]
# exact solution: y(t) = exp(m*t)
import matplotlib.pyplot as plt

from tautoolbox import tau
from tautoolbox.functions import diff, exp

n = 30
m = 1.2
beta = 3
gamma = 0
alpha = m - beta * exp(-m) - gamma * exp(m)


options = tau.settings(degree=n - 1, basis="ChebyshevT")
problem = tau.problem(
    equation=lambda t, y: diff(y) - alpha * y - beta * y(t - 1) - gamma * y(t + 1),
    domain=[0, 3],
    conditions=lambda y: y(0) - 1,
    options=options,
)
yn, *info = tau.solve(problem)

y = tau.polynomial(lambda x: exp(m * x), problem.domain, options=options)

plt.figure(1)
plt.title("Backward-forward linear delay differential equation (IVP)")
(y - yn).plot(linewidth=1.6)
plt.xlabel("$x$")
plt.ylabel("Error: $y-y_n$")
plt.show()
