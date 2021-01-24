import matplotlib
import pandas as pd
import pyam
from ixmp.reporting import Quantity

from message_ix import Scenario
from message_ix.reporting import Reporter, computations
from message_ix.testing import SCENARIO


def test_as_pyam(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])
    if not scen.has_solution():
        scen.solve()
    rep = Reporter.from_scenario(scen)

    # Quantities for 'ACT' variable at full resolution
    qty = rep.get(rep.full_key("ACT"))

    # Call as_pyam() with an empty quantity
    p = computations.as_pyam(scen, qty[0:0], year_time_dim="ya")
    assert isinstance(p, pyam.IamDataFrame)


def test_concat(dantzig_reporter):
    """pyam.concat() correctly passes through to ixmp…concat()."""
    rep = dantzig_reporter

    key = rep.add(
        "test",
        computations.concat,
        "fom:nl-t-ya",
        "vom:nl-t-ya",
        "tom:nl-t-ya",
    )
    rep.get(key)


def test_plot_cumulative(tmp_path):
    x = pd.Series(
        {
            ("region", "a"): 500,
            ("region", "b"): 1000,
        }
    )
    x.index.names = ["n", "g"]

    y = pd.Series(
        {
            ("region", "a", 2020): 1.1,
            ("region", "b", 2020): 2.2,
            ("region", "a", 2021): 3.3,
            ("region", "b", 2021): 4.4,
        }
    )
    y.index.names = ["n", "g", "y"]

    result = computations.plot_cumulative(
        Quantity(x, units="GW a"),
        Quantity(y, units="mole / kW a"),
        labels=("Fossil supply", "Resource volume", "Cost"),
    )
    assert isinstance(result, matplotlib.axes.Axes)
    matplotlib.pyplot.savefig(tmp_path / "plot_cumulative.svg")


def test_stacked_bar():
    data = pd.Series(
        {
            ("region", "foo", 2020): 1.0,
            ("region", "bar", 2020): 2.0,
            ("region", "foo", 2021): 3.0,
            ("region", "bar", 2021): 4.0,
        }
    )
    data.index.names = ["r", "t", "year"]

    result = computations.stacked_bar(Quantity(data), dims=["r", "t", "year"])
    assert isinstance(result, matplotlib.axes.Axes)
