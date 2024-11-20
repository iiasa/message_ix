from collections.abc import Mapping
from typing import TYPE_CHECKING, Literal, overload

import pandas as pd

from message_ix.util import make_df

if TYPE_CHECKING:
    from genno.types import AnyQuantity

__all__ = [
    "as_message_df",
    "model_periods",
    "plot_cumulative",
    "stacked_bar",
]


@overload
def as_message_df(
    qty: "AnyQuantity",
    name: str,
    dims: Mapping,
    common: Mapping,
    wrap: Literal[True] = True,
) -> dict[str, pd.DataFrame]: ...


@overload
def as_message_df(
    qty: "AnyQuantity",
    name: str,
    dims: Mapping,
    common: Mapping,
    wrap: Literal[False],
) -> pd.DataFrame: ...


def as_message_df(qty, name, dims, common, wrap=True):
    """Convert `qty` to an :meth:`.add_par`-ready data frame using :func:`.make_df`.

    The resulting data frame has:

    - A "value" column populated with the values of `qty`.
    - A "unit" column with the string representation of the units of `qty`.
    - Other dimensions/key columns filled with labels of `qty` according to `dims`.
    - Other dimensions/key columns filled with uniform values from `common`.

    Parameters
    ----------
    qty : genno.Quantity
    name : str
        Name of the :ref:`MESSAGEix parameter <parameter_def>` to prepare.
    dims : mapping
        Each key corresponds to a dimension of the target parameter `name`, for instance
        "node_loc"; the label corresponds to a dimension of `qty`, for instance "nl".
    common : mapping
        Each key corresponds to a dimension of the target parameter; values are used
        literally, as if passed to :func:`.make_df`.
    wrap : bool, optional
        See below.

    Returns
    -------
    dict
        if `wrap` is :data:`True` (the default): length 1, mapping from `name` to
        :class:`pandas.DataFrame` containing the converted data.
    pandas.DataFrame
        if `wrap` is :data:`False`.
    """
    name = getattr(name, "data", name)  # Unwrap dask.core.literal
    base = qty.to_series().reset_index(name="value")
    df = make_df(
        name,
        unit=f"{qty.units:~}",
        value=base["value"],
        **{k1: base.get(k2) for k1, k2 in dims.items()},
        **common,
    )
    return {name: df} if wrap else df


def model_periods(y: list[int], cat_year: pd.DataFrame) -> list[int]:
    """Return the elements of `y` beyond the firstmodelyear of `cat_year`."""
    return list(
        filter(
            lambda year: cat_year.query("type_year == 'firstmodelyear'")["year"].item()
            <= year,
            y,
        )
    )


def plot_cumulative(x: "AnyQuantity", y: "AnyQuantity", labels: tuple[str, str, str]):
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
    assert isinstance(d1, str)

    assert (
        d0,
        d1,
    ) == x.dims, f"dimensions of x {x.dims!r} != first dimensions of y {(d0, d1)!r}"

    # Check that all data have the same value in the first dimension
    d0_labels = set(x.coords[d0].values) | set(y.coords[d0].values)
    assert len(d0_labels) == 1, f"non-unique values {d0_labels!r} for dimension {d0!r}"
    d0_label = d0_labels.pop()

    axes_properties = dict(
        title=f"{d0_label} {labels[0].title()}",
        xlabel=f"{labels[1]} [{x.attrs['_unit']:~}]",
        ylabel=f"{labels[2]} [{y.attrs['_unit']:~}]",
    )

    # Reshape data
    x_series = x.sel({d0: d0_label}, drop=True).to_series()
    # NB groupby().mean() here will compute a mean price across d2, e.g. year
    y_series = y.sel({d0: d0_label}, drop=True).to_series().groupby(d1).mean()

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


def stacked_bar(
    qty: "AnyQuantity",
    dims: tuple[str, ...] = ("nl", "t", "ya"),
    units: str = "",
    title: str = "",
    cf: float = 1.0,
    stacked: bool = True,
):
    """Plot `qty` as a stacked bar chart.

    Parameters
    ----------
    qty : Quantity
        Data to plot.
    dims : tuple of str
        3 or more dimensions for, respectively:

        - 1 dimension: The node/region.
        - 1 or more dimensions: to stack in bars of different colour.
        - 1 dimension: The ordinate (x-axis); typically the year.
    units : str
        Units to display on the plot.
    title : str
        Title fragment; the plot title is "{node} {title}".
    cf : float, optional
        Conversion factor to apply to data.
    """
    if len(dims) < 3:  # pragma: no cover
        raise ValueError(f"Must pass >= 3 dimensions; got dims={dims!r}")

    # - Multiply by the conversion factor
    # - Convert to a pd.Series
    # - Unstack one dimension
    # - Convert to pd.DataFrame
    df = (cf * qty).to_series().unstack(dims[1:-1]).reset_index()

    # Plot using matplotlib via pandas
    ax = df.plot(
        x=dims[-1],
        kind="bar",
        stacked=stacked,
        xlabel="Year",
        ylabel=units,
        title=f"{df.loc[0, dims[0]]} {title}",
    )
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    return ax
