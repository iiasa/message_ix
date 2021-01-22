from ixmp.reporting import Quantity
import matplotlib
import pandas as pd
import pyam

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


def test_stacked_bar():
    data = pd.DataFrame(
        [
            ["region", "foo", 2020, 1.0],
            ["region", "bar", 2020, 2.0],
            ["region", "foo", 2021, 3.0],
            ["region", "bar", 2021, 4.0],
        ],
        columns=["r", "t", "year", "value"],
    ).set_index(["r", "t", "year"])["value"]
    print(data)
    qty = Quantity(data)
    result = computations.stacked_bar(qty, dims=["r", "t", "year"])
    assert isinstance(result, matplotlib.axes.Axes)
