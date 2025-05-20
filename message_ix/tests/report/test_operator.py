from collections.abc import Mapping
from functools import partial
from typing import TYPE_CHECKING, Any

import matplotlib
import pandas as pd
import pyam
from dask.core import literal

try:
    from genno.operator import random_qty
except ImportError:  # pragma: no cover — genno v1.27.1 and earlier
    from genno.testing import random_qty  # type: ignore [no-redef]
from ixmp.report import Quantity

from message_ix import Scenario
from message_ix.report import Reporter, operator
from message_ix.testing import SCENARIO

if TYPE_CHECKING:
    from pathlib import Path

    from ixmp import Platform

# NOTE These tests likely don't need to be parametrized


def test_as_message_df(test_mp: "Platform") -> None:
    q = random_qty(dict(c=3, h=2, nl=5))
    q.units = "kg"

    args: tuple[Any, Mapping, Mapping] = (
        literal("demand"),
        dict(commodity="c", node="nl", time="h"),
        dict(level="l", year=2022),
    )

    # Can be called directly
    result0 = operator.as_message_df(q, *args, wrap=False)
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

    # Works together with ixmp.report.operator.update_scenario

    # Prepare a Scenario
    s = Scenario(test_mp, "m", "s", version="new")

    # Minimal structure to accept the data in `q`
    for col, values in result0.items():
        if col in ("value", "unit"):
            continue
        s.add_set(str(col), values.unique().tolist())
    s.add_set("technology", "t")
    s.commit("")

    # Add the Scenario to the Reporter
    r.add("scenario", s)

    # Convert with wrap=False
    r.add("q::ixmp", partial(operator.as_message_df, wrap=False), key, *args)
    # Add a task to update the scenario
    us = r.get_operator("update_scenario")
    assert us is not None
    key = r.add("add q", partial(us, params=["demand"]), "scenario", "q::ixmp")

    # No data in "demand" parameter
    assert 0 == len(s.par("demand"))
    # Computation succeeds
    r.get(key)
    # All data was added
    assert q.size == len(s.par("demand"))


def test_as_pyam(message_test_mp: "Platform") -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])
    if not scen.has_solution():
        scen.solve(quiet=True)
    rep = Reporter.from_scenario(scen)

    # Quantities for 'ACT' variable at full resolution
    qty = rep.get(rep.full_key("ACT"))

    # Call as_pyam() with an empty quantity
    as_pyam = rep.get_operator("as_pyam")
    # For type checkers:
    assert as_pyam
    p = as_pyam(scen, qty[0:0], rename=dict(nl="region", ya="year"))
    assert isinstance(p, pyam.IamDataFrame)


def test_concat(dantzig_reporter: Reporter) -> None:
    """pyam.concat() correctly passes through to ixmp…concat()."""
    rep = dantzig_reporter

    key = rep.add("concat", "test", "fom:nl-t-ya", "vom:nl-t-ya", "tom:nl-t-ya")
    rep.get(key)


def test_plot_cumulative(tmp_path: "Path") -> None:
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

    result = operator.plot_cumulative(
        Quantity(x, units="GW a"),
        Quantity(y, units="mole / kW a"),
        labels=("Fossil supply", "Resource volume", "Cost"),
    )
    assert isinstance(result, matplotlib.axes.Axes)
    matplotlib.pyplot.savefig(tmp_path / "plot_cumulative.svg")


def test_stacked_bar() -> None:
    data = pd.Series(
        {
            ("region", "foo", 2020): 1.0,
            ("region", "bar", 2020): 2.0,
            ("region", "foo", 2021): 3.0,
            ("region", "bar", 2021): 4.0,
        }
    )
    data.index.names = ["r", "t", "year"]

    result = operator.stacked_bar(Quantity(data), dims=("r", "t", "year"))
    assert isinstance(result, matplotlib.axes.Axes)
