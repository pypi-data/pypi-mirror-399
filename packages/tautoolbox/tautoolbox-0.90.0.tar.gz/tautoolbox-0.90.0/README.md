# Tau Toolbox

   AUTHORS:

       Paulo B. Vasconcelos
       Centro de Matemática - Universidade do Porto
       Email: pjv@fep.up.pt

       José M. A. Matos
       Centro de Matemática - Universidade do Porto
       Email: jma@isep.ipp.pt

       José A. O. Matos
       Centro de Matemática - Universidade do Porto
       Email: jamatos@fep.up.pt

       Nilson Lima

   REFERENCE:

       Solving differential eigenproblems via the spectral Tau method
       NUMERICAL ALGORITHMS
       DOI: https://doi.org/10.1007/s11075-022-01366-z

   SOFTWARE REVISION DATE:

       Version 0.90 : 2025-12-31

   SOFTWARE LANGUAGE:

       MATLAB 9.12.0 (R2022a)
       Octave 8.1.0


Tau Toolbox is a Python library for the solution of integro-differential
problems based on the Lanczos' Tau method.

Tau Toolbox is free software released under the GNU Lesser General Public
License version 3 (LGPLv3). A copy of the License is enclosed in the project.

## Installation

Just clone the Tau Toolbox repository following
`git clone https://bitbucket.org/tautoolbox/taupy.git`.

Tau Toolbox can also be obtained at https://cmup.fc.up.pt/tautoolbox/.

`Tautoolbox` requires Python 3.10 together with the following modules:

 * `numpy`
 * `matplotlib`

### Help

A Tau Toolbox User Guide will be made available soon, along with a set of
Technical Reports.

### Support

The project is very recent. Nevertheless it has been thoroughly tested.
The project supports the tool in the sense that reports of errors or
poor performance will gain immediate attention from the developers.

## Getting started

The best way to get started is by using the many
[examples](https://bitbucket.org/tautoolbox/taupy/src/main/examples/)
provided.

Tackle your problems with ease:

* To solve the ordinary differential problem
$y''(x)+y(x)= 0$ in $[0,2\pi]$ with $y(0)=1$ and $y'(2\pi)=0$,
just type:

```python
import tautoolbox as tau
import numpy as np
from tautoolbox.functions import diff, linspace
import matplotlib.pyplot as plt

equation = lambda x, y: diff(y, 2) + y
domain = [0, 2 * np.pi]
conditions = lambda y: [y(0) - 1, y.diff(1, 2 * np.pi)]
problem = tau.problem(equation, domain, conditions)
yn = tau.solve(problem)[0]

x = linspace(yn)
plt.plot(x, yn(x))
```

You can find more examples in the `examples` folder.

**Notice** that we refer sometimes to `taupy`, this is not to be confused with the [`taupy` package](https://pypi.org/project/taupy/).
This reference, that we have used internally since 2021, refers to the Python implementation of the [Matlab/Octave Tautoolbox](https://bitbucket.org/tautoolbox/tautoolbox/src/main/).
There are some small differences between both implementations but the general structure is the same, and as long as possible, the syntax is also the same adapted to the syntax of the languages.
