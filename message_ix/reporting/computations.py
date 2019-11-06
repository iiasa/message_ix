# Import other comps so they can be imported from this module
from ixmp.reporting.computations import *        # noqa: F401, F403
from ixmp.reporting.computations import product  # noqa: F401

from .pyam import as_pyam, concat, write_report  # noqa: F401


def add(a, b, fill_value=0.0):
    """Sum of *a* and *b*."""
    return a.add(b, fill_value=fill_value).dropna()
