"""
Dummy conftest.py for tautoolbox.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
https://pytest.org/latest/plugins.html
"""

import numpy
import pytest

from tautoolbox import polynomial, tau


@pytest.fixture(autouse=True)
def add_ns(doctest_namespace):
    doctest_namespace["np"] = numpy
    doctest_namespace["polynomial"] = polynomial
    doctest_namespace["tau"] = tau
