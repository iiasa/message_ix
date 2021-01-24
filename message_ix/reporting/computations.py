# Import other comps so they can be imported from this module
import pandas as pd
from ixmp.reporting import RENAME_DIMS, Quantity
from ixmp.reporting.computations import *  # noqa: F401, F403
from ixmp.reporting.computations import add, product

from .pyam import as_pyam, concat, write_report  # noqa: F401

__all__ = [
    # Defined here
    "broadcast_map",
    "map_as_qty",
    "stacked_bar",
    # In .pyam
    "as_pyam",
    "concat",
    "write_report",
    # in ixmp
    "add",
    "product",
]


def map_as_qty(set_df, full_set):
    """Convert *set_df* to a :class:`.Quantity`.

    For the MESSAGE sets named ``cat_*`` (see :ref:`mapping-sets`)
    :meth:`ixmp.Scenario.set` returns a :class:`~pandas.DataFrame` with two
    columns: the *category* set (S1) elements and the *category member* set
    (S2, also required as the argument `full_set`) elements.

    map_as_qty converts such a DataFrame (*set_df*) into a Quantity with two
    dimensions. At the coordinates *(s₁, s₂)*, the value is 1 if *s₂* is a
    mapped from *s₁*; otherwise 0.

    An category named 'all', containing all elements of `full_set`, is added
    automatically.

    See also
    --------
    broadcast_map
    """
    set_from, set_to = set_df.columns
    names = [RENAME_DIMS.get(c, c) for c in set_df.columns]

    # Add an 'all' mapping
    set_df = pd.concat(
        [
            set_df,
            pd.DataFrame([("all", e) for e in full_set], columns=set_df.columns),
        ]
    )

    # Add a value column
    set_df["value"] = 1

    return (
        set_df.set_index([set_from, set_to])["value"]
        .rename_axis(index=names)
        .pipe(Quantity)
    )


def broadcast_map(quantity, map, rename={}):
    """Broadcast *quantity* using a *map*.

    The *map* must be a 2-dimensional quantity, such as returned by
    :meth:`map_as_qty`.

    *quantity* is 'broadcast' by multiplying it with the 2-dimensional *map*,
    and then dropping the common dimension. The result has the second dimension
    of *map* instead of the first.

    Parameters
    ----------
    rename : dict (str -> str), optional
        Dimensions to rename on the result.
    """
    return product(quantity, map).drop(map.dims[0]).rename(rename)


def plot_cumulative(x, y, labels):
    """Plot a supply curve.

    - `x` and `y` must share the first two dimensions.
    - The first dimension must contain unique values.
    - One rectangle is plotted for each unique value in the second dimension.

    Parameters
    ----------
    x : Quantity
        e.g. ``<resource_volume:n-g>``.
    y : Quantity
        e.g. ``<resource_cost:n-g-y>``. The ``mean()`` is taken across the third
        dimension.
    """
    from matplotlib import pyplot
    from matplotlib.patches import Rectangle

    # Unpack the dimensions of `y`, typically "n" (node), "g" (grade), "y" (year)
    d0, d1, d2 = y.dims

    assert (
        d0,
        d1,
    ) == x.dims, (
        f"dimensions of x {repr(x.dims)} != first dimensions of y {repr((d0, d1))}"
    )

    # Check that all data have the same value in the first dimension
    d0_labels = set(x.coords[d0].values) | set(y.coords[d0].values)
    assert (
        len(d0_labels) == 1
    ), "non-unique values {repr(d0_labels)} for dimension {repr(d0)}"

    axes_properties = dict(
        title=f"{d0_labels.pop()} {labels[0].title()}",
        xlabel=f"{labels[1]} [{x.attrs['_unit']:~}]",
        ylabel=f"{labels[2]} [{y.attrs['_unit']:~}]",
    )

    # Reshape data
    x_series = x.drop(d0).to_series()
    # NB groupby().mean() here will compute a mean price across d2, e.g. year
    y_series = y.drop(d0).to_series().groupby(d1).mean()

    fig, ax = pyplot.subplots()

    # Markers
    ax.scatter(x_series, y_series, color="white")

    # Add one rectangular patch to the axes per element
    x_total = 0
    for i, (x_value, y_value) in enumerate(zip(x_series, y_series)):
        ax.add_patch(Rectangle((x_total, 0), x_value, y_value, edgecolor="black"))
        # Bottom-left x position for next patch
        x_total += x_value

    # Set figure attributes
    ax.set(xlim=[0, x_total], **axes_properties)

    return ax


def stacked_bar(qty, dims=["nl", "t", "ya"], units="", title="", cf=1.0, stacked=True):
    """Plot `qty` as a stacked bar chart.

    Parameters
    ----------
    qty : ixmp.reporting.Quantity
        Data to plot.
    dims : 3-tuple of str
        Dimensions for, respectively:

        1. The node/region.
        2. Dimension to stack.
        3. The ordinate (x-axis).
    units : str
        Units to display on the plot.
    title : str
        Title fragment; the plot title is "{node} {title}".
    cf : float, optional
        Conversion factor to apply to data.
    """
    # - Multiply by the conversion factor
    # - Convert to a pd.Series
    # - Unstack one dimension
    # - Convert to pd.DataFrame
    df = (cf * qty).to_series().unstack(dims[1]).reset_index()

    # Plot using matplotlib via pandas
    ax = df.plot(
        x=dims[2],
        kind="bar",
        stacked=stacked,
        xlabel="Year",
        ylabel=units,
        title=f"{df.loc[0, dims[0]]} {title}",
        width=5.0,
    )
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    return ax
