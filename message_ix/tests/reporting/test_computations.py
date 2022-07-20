from functools import partial

import matplotlib
import pandas as pd
import pyam
from dask.core import literal
from genno.testing import random_qty
from ixmp.reporting import Quantity

from message_ix import Scenario
from message_ix.reporting import Reporter, computations
from message_ix.testing import SCENARIO


def test_as_message_df(test_mp):
    q = random_qty(dict(c=3, h=2, nl=5))
    q.units = "kg"

    args = (
        literal("demand"),
        dict(commodity="c", node="nl", time="h"),
        dict(level="l", year=2022),
    )

    # Can be called directly
    result0 = computations.as_message_df(q, *args, wrap=False)
    assert not result0.isna().any().any()
    # Values appear with the correct indices
    assert (
        q.sel(c="c2", h="h1", nl="nl4").item()
        == result0.query("commodity == 'c2' and time == 'h1' and node == 'nl4'")[
            "value"
        ].iloc[0]
    )

    # Through a Reporter, with default wrap=True
    r = Reporter()
    key = r.add("q:nl-c", q)
    r.add("as_message_df", "q::ixmp", key, *args)
    result1 = r.get("q::ixmp")
    assert not result1["demand"].isna().any().any()

    # Works together with ixmp.reporting.computations.update_scenario

    # Prepare a Scenario
    s = Scenario(test_mp, "m", "s", version="new")

    # Minimal structure to accept the data in `q`
    for col, values in result0.items():
        if col in ("value", "unit"):
            continue
        s.add_set(col, values.unique().tolist())
    s.add_set("technology", "t")
    s.commit("")

    # Add the Scenario to the Reporter
    r.add("scenario", s)

    # Convert with wrap=False
    r.add("q::ixmp", partial(computations.as_message_df, wrap=False), key, *args)
    # Add a task to update the scenario
    us = r.get_comp("update_scenario")
    key = r.add("add q", partial(us, params=["demand"]), "scenario", "q::ixmp")

    # No data in "demand" parameter
    assert 0 == len(s.par("demand"))
    # Computation succeeds
    r.get(key)
    # All data was added
    assert q.size == len(s.par("demand"))


def test_as_pyam(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])
    if not scen.has_solution():
        scen.solve(quiet=True)
    rep = Reporter.from_scenario(scen)

    # Quantities for 'ACT' variable at full resolution
    qty = rep.get(rep.full_key("ACT"))

    # Call as_pyam() with an empty quantity
    as_pyam = rep.get_comp("as_pyam")
    p = as_pyam(scen, qty[0:0], rename=dict(nl="region", ya="year"))
    assert isinstance(p, pyam.IamDataFrame)


def test_concat(dantzig_reporter):
    """pyam.concat() correctly passes through to ixmp…concat()."""
    rep = dantzig_reporter

    key = rep.add("concat", "test", "fom:nl-t-ya", "vom:nl-t-ya", "tom:nl-t-ya")
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
