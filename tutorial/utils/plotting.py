from functools import partial

from message_ix.reporting import Key, Reporter


def stacked_bar(qty, dims=["nl", "t", "ya"], units="", title="", cf=1.0):
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
        Title fragment; the plot title is "{Node} Energy System {Title}".
    cf : float, optional
        Conversion factor to apply to data.
    """
    # Multiply by the conversion factor; convert to a pd.Series;
    # unstack one dimension, then to pd.DataFrame
    df = (cf * qty).to_series().unstack(dims[1]).reset_index()

    # Plot using matplotlib via pandas
    return df.plot(
        x=dims[2],
        kind="bar",
        stacked=True,
        xlabel="Year",
        ylabel=units,
        title=f"{df.loc[0, dims[0]]} Energy System {title.title()}",
    ).legend(loc="center left", bbox_to_anchor=(1.0, 0.5))


PLOTS = [
    ("activity", stacked_bar, "out:nl-t-ya", "GWa"),
    ("capacity", stacked_bar, "CAP:nl-t-ya", "GW"),
    ("prices", stacked_bar, "PRICE_COMMODITY:n-c-y", "¢/kW·h"),
]


def prepare_tutorial_plots(rep: Reporter, input_costs="$/GWa") -> None:
    """Prepare `rep` to Plots for tutorial energy models.

    Makes available several keys:

    - `plot activity`
    - `plot capacity`
    - `plot prices`

    To control the contents of each plot, use :meth:`.set_filters` on `rep`.
    """
    # TODO re-add plot_new_capacity()
    # TODO re-add plot_extraction()
    # TODO re-add plot_fossil_supply_curve()

    # Conversion factors between input units and plotting units
    # TODO use exact units in all tutorials
    # TODO allow the correct units to pass through reporting
    cost_unit_conv = {
        "$/GWa": 1.0,
        "$/MWa": 1e3,
        "$/kWa": 1e6,
    }.get(input_costs)

    # Basic setup of the reporter
    rep.configure(units={"replace": {"-": ""}})

    # Add one node to the reporter for each plot
    for title, func, key_str, units in PLOTS:
        # Convert the string to a Key object so as to reference its .dims
        key = Key.from_str_or_key(key_str)

        # Operation for the reporter
        comp = partial(
            # The function to use, e.g. stacked_bar()
            func,
            # Other keyword arguments to the plotting function
            dims=key.dims,
            units=units,
            title=title,
            cf=1.0 if title != "Prices" else (cost_unit_conv * 100 / 8760),
        )

        # Add the computation under a key like "plot activity"
        rep.add(f"plot {title}", (comp, key))
