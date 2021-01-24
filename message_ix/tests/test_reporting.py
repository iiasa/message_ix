from functools import partial
from logging import WARNING
from pathlib import Path

import pandas as pd
import pyam
import pytest
import xarray as xr
from ixmp.reporting import Quantity
from ixmp.reporting import Reporter as ixmp_Reporter
from ixmp.testing import assert_qty_equal
from numpy.testing import assert_allclose
from pandas.testing import assert_frame_equal, assert_series_equal

from message_ix import Scenario
from message_ix.reporting import Reporter, computations, configure
from message_ix.testing import SCENARIO, make_dantzig, make_westeros


def test_reporter_no_solution(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    pytest.raises(RuntimeError, Reporter.from_scenario, scen)


def test_reporter(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    # Varies between local & CI contexts
    # DEBUG may be due to reuse of test_mp in a non-deterministic order
    if not scen.has_solution():
        scen.solve()

    # IXMPReporter can be initialized on a MESSAGE Scenario
    rep_ix = ixmp_Reporter.from_scenario(scen)

    # message_ix.Reporter can also be initialized
    rep = Reporter.from_scenario(scen)

    # Number of quantities available in a rudimentary MESSAGEix Scenario
    assert len(rep.graph["all"]) == 123

    # Quantities have short dimension names
    assert "demand:n-c-l-y-h" in rep.graph

    # Aggregates are available
    assert "demand:n-l-h" in rep.graph

    # Quantities contain expected data
    dims = dict(coords=["chicago new-york topeka".split()], dims=["n"])
    demand = Quantity(xr.DataArray([300, 325, 275], **dims), name="demand")

    # NB the call to squeeze() drops the length-1 dimensions c-l-y-h
    obs = rep.get("demand:n-c-l-y-h").squeeze(drop=True)
    # check_attrs False because we don't get the unit addition in bare xarray
    assert_qty_equal(obs, demand, check_attrs=False)

    # ixmp.Reporter pre-populated with only model quantities and aggregates
    assert len(rep_ix.graph) == 5223

    # message_ix.Reporter pre-populated with additional, derived quantities
    # This is the same value as in test_tutorials.py
    assert len(rep.graph) == 12688

    # Derived quantities have expected dimensions
    vom_key = rep.full_key("vom")
    assert vom_key not in rep_ix
    assert vom_key == "vom:nl-t-yv-ya-m-h"

    # …and expected values
    var_cost = rep.get(rep.full_key("var_cost"))
    ACT = rep.get(rep.full_key("ACT"))
    vom = computations.product(var_cost, ACT)
    # check_attrs false because `vom` multiply above does not add units
    assert_qty_equal(vom, rep.get(vom_key))


def test_reporter_from_dantzig(test_mp):
    scen = make_dantzig(test_mp, solve=True)

    # Reporter.from_scenario can handle Dantzig example model
    rep = Reporter.from_scenario(scen)

    # Default target can be calculated
    rep.get("all")


def test_reporter_from_westeros(test_mp):
    scen = make_westeros(test_mp, emissions=True, solve=True)

    # Reporter.from_scenario can handle Westeros example model
    rep = Reporter.from_scenario(scen)

    # Westeros-specific configuration: '-' is a reserved character in pint
    configure(units={"replace": {"-": ""}})

    # Default target can be calculated
    rep.get("all")

    # message default target can be calculated
    # TODO if df is empty, year is cast to float
    obs = rep.get("message:default")

    # all expected reporting exists
    assert len(obs.data) == 69

    # custom values are correct
    obs = obs.filter(variable="total om*")
    assert len(obs.data) == 9
    assert all(
        obs["variable"]
        == ["total om cost|coal_ppl"] * 3  # noqa: W504
        + ["total om cost|grid"] * 3  # noqa: W504
        + ["total om cost|wind_ppl"] * 3  # noqa: W504
    )
    assert all(obs["year"] == [700, 710, 720] * 3)

    obs = obs["value"].values
    exp = [
        4832.177734,
        8786.515625,
        12666.666016,
        5555.555664,
        8333.333984,
        10555.555664,
        305.748138,
        202.247391,
        0.0,
    ]
    assert len(obs) == len(exp)
    assert_allclose(obs, exp)


def test_reporter_convert_pyam(dantzig_reporter, caplog, tmp_path):
    rep = dantzig_reporter

    # Key for 'ACT' variable at full resolution
    ACT = rep.full_key("ACT")

    # Add a computation that converts ACT to a pyam.IamDataFrame
    rep.add(
        "ACT IAMC",
        (
            partial(computations.as_pyam, drop=["yv"], year_time_dim="ya"),
            "scenario",
            ACT,
        ),
    )

    # Result is an IamDataFrame
    idf1 = rep.get("ACT IAMC")
    assert isinstance(idf1, pyam.IamDataFrame)

    # …of expected length
    assert len(idf1) == 8

    # …in which variables are not renamed
    assert idf1["variable"].unique() == "ACT"

    # Warning was logged because of extra columns
    w = "Extra columns ['h', 'm', 't'] when converting 'ACT' to IAMC format"
    assert ("message_ix.reporting.pyam", WARNING, w) in caplog.record_tuples

    # Repeat, using the message_ix.Reporter convenience function
    def add_tm(df, name="Activity"):
        """Callback for collapsing ACT columns."""
        df["variable"] = f"{name}|" + df["t"] + "|" + df["m"]
        return df.drop(["t", "m"], axis=1)

    # Use the convenience function to add the node
    keys = rep.convert_pyam(ACT, "ya", collapse=add_tm)

    # Keys of added node(s) are returned
    assert len(keys) == 1
    key2, *_ = keys
    assert key2 == ACT.name + ":iamc"

    caplog.clear()

    # Result
    idf2 = rep.get(key2)
    df2 = idf2.as_pandas()

    # Extra columns have been removed:
    # - m and t by the collapse callback.
    # - h automatically, because 'ya' was used for the year index.
    assert not any(c in df2.columns for c in ["h", "m", "t"])

    # Variable names were formatted by the callback
    reg_var = pd.DataFrame(
        [
            ["san-diego", "Activity|canning_plant|production"],
            ["san-diego", "Activity|transport_from_san-diego|to_chicago"],
            ["san-diego", "Activity|transport_from_san-diego|to_new-york"],
            ["san-diego", "Activity|transport_from_san-diego|to_topeka"],
            ["seattle", "Activity|canning_plant|production"],
            ["seattle", "Activity|transport_from_seattle|to_chicago"],
            ["seattle", "Activity|transport_from_seattle|to_new-york"],
            ["seattle", "Activity|transport_from_seattle|to_topeka"],
        ],
        columns=["region", "variable"],
    )
    assert_frame_equal(df2[["region", "variable"]], reg_var)

    # message_ix.Reporter uses pyam.IamDataFrame.to_csv() to write to file
    path = tmp_path / "activity.csv"
    rep.write(key2, path)

    # File contents are as expected
    expected = Path(__file__).parent / "data" / "report-pyam-write.csv"
    assert path.read_text() == expected.read_text()

    # Use a name map to replace variable names
    rep.add("activity variables", {"Activity|canning_plant|production": "Foo"})
    key3 = rep.convert_pyam(
        ACT, "ya", replace_vars="activity variables", collapse=add_tm
    ).pop()
    df3 = rep.get(key3).as_pandas()

    # Values are the same; different names
    exp = df2[df2.variable == "Activity|canning_plant|production"][
        "value"
    ].reset_index()
    assert all(exp == df3[df3.variable == "Foo"]["value"].reset_index())

    # Now convert variable cost
    cb = partial(add_tm, name="Variable cost")
    key4 = rep.convert_pyam("var_cost", "ya", collapse=cb).pop()
    df4 = rep.get(key4).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df4["unit"] == "USD / case")

    # Also change units
    key5 = rep.convert_pyam("var_cost", "ya", collapse=cb, unit="centiUSD / case").pop()
    df5 = rep.get(key5).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df5["unit"] == "centiUSD / case")
    assert_series_equal(df4["value"], df5["value"] / 100.0)
