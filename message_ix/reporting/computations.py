# Import other comps so they can be imported from this module
from ixmp.reporting.computations import *        # noqa: F401, F403
from ixmp.reporting.computations import product
from ixmp.reporting.utils import RENAME_DIMS, as_quantity

from .pyam import as_pyam, concat, write_report  # noqa: F401


def add(a, b, fill_value=0.0):
    """Sum of *a* and *b*."""
    return a.add(b, fill_value=fill_value).dropna()


def map_as_qty(set_df):
    """Convert *set_df* to a Quantity."""
    set_from, set_to = set_df.columns
    names = [RENAME_DIMS.get(c, c) for c in set_df.columns]

    # Add a value column
    set_df['value'] = 1

    return set_df.set_index([set_from, set_to])['value'] \
                 .rename_axis(index=names) \
                 .pipe(as_quantity)


def broadcast_map(quantity, map, rename={}):
    """Broadcast *quantity* using a *map* dictionary."""
    return product(quantity, map).drop(map.dims[0]) \
                                 .rename(rename)
