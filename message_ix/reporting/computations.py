from typing import Mapping, Union

import pandas as pd
from ixmp.reporting import Quantity

from message_ix.util import make_df

__all__ = [
    "as_message_df",
    "plot_cumulative",
    "stacked_bar",
]


def as_message_df(
    qty: Quantity, name: str, dims: Mapping, common: Mapping, wrap: bool = True
) -> Union[pd.DataFrame, dict]:
    """Convert `qty` to an :mod:`ixmp.add_par`-ready data frame using :func:`make_df`.

    The resulting data frame has:

    - A "value" column populated with the values of `qty`.
    - A "unit" column with the string representation of the units of `qty`.
    - Other dimensions/key columns filled with labels of `qty` according to `dims`.
    - Other dimensions/key columns filled with uniform values from `common`.

    Parameters
    ----------
    qty : :class:`.genno.Quantity`
    name : str
        Name of the :ref:`MESSAGEix parameter <parameter_def>` to prepare.
    dims : mapping (str → str)
        Each key corresponds to a dimension of the target parameter `name`, e.g.
        "node_loc"; the label corresponds to a dimension of `qty`, e.g. "nl".
    common : mapping (str → Any)
        Each key corresponds to a dimension of the target parameter; values are used
        literally, as if passed to :func:`.make_df`.
    wrap : bool, optional
        See below.

    Returns
    -------
    length-1 :class:`dict` of `name` → pandas.DataFrame
        if `wrap` is :data:`True`, the default; or
    pandas.DataFrame
        if `wrap` is :data:`False`.
    """
    name = getattr(name, "data", name)  # Unwrap dask.core.literal
    base = qty.to_series().reset_index(name="value")
    df = make_df(
        name,
        unit=f"{qty.units:~}",
        value=base["value"],
        **{k1: base[k2] for k1, k2 in dims.items()},
        **common,
    )
    return {name: df} if wrap else df


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
    ), f"non-unique values {repr(d0_labels)} for dimension {repr(d0)}"

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
    )
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    return ax
