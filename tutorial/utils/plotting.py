from functools import partial

from message_ix.reporting import Key, Reporter


def stacked_bar(qty, dims=["nl", "t", "ya"], units="", title="", cf=1.):
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
    ).legend(loc="center left", bbox_to_anchor=(1., 0.5))


class Plots:
    """Plots for tutorial energy models."""
    # TODO re-add plot_new_capacity()
    # TODO re-add plot_extraction()
    # TODO re-add plot_fossil_supply_curve()

    def __init__(self, scenario, input_costs='$/GWa'):
        # Conversion factors between input units and plotting units
        # TODO use the correct units in tutorials
        # TODO allow the correct units to pass through reporting
        cost_unit_conv = {
            "$/GWa": 1.,
            "$/MWa": 1e3,
            "$/kWa": 1e6,
        }.get(input_costs)

        # Basic setup of the Reporter
        self.rep = Reporter.from_scenario(scenario)
        self.rep.configure(units={"replace": {"-": ""}})

        # Add one node for each plot
        for title, key_str, units in [
            ("activity", "out:nl-t-ya", "GWa"),
            ("capacity", "CAP:nl-t-ya", "GW"),
            ("prices", "PRICE_COMMODITY:n-c-y", "¢/kW·h"),
        ]:
            # Convert the string to a Key object
            key = Key.from_str_or_key(key_str)

            # Operation for the reporter: generate a stacked bar plot
            comp = partial(
                stacked_bar,
                dims=key.dims,
                units=units,
                title=title,
                cf=1. if title != "Prices" else (cost_unit_conv * 100 / 8760)
            )
            # Add the computation under a key like "plot activity"
            self.rep.add(f"plot {title}", (comp, key))

    def plot_output(self, tecs):
        self.rep.set_filters(t=[tecs] if isinstance(tecs, str) else tecs)
        return self.rep.get("plot activity")

    def plot_capacity(self, tecs):
        self.rep.set_filters(t=[tecs] if isinstance(tecs, str) else tecs)
        return self.rep.get("plot capacity")

    def plot_prices(self, cmdty):
        self.rep.set_filters(c=[cmdty] if isinstance(cmdty, str) else cmdty)
        return self.rep.get("plot prices")
