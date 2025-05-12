import logging
import re
import sys
from functools import partial
from pathlib import Path

import genno
import pandas as pd
import pyam
import pytest
from genno.testing import assert_qty_equal
from ixmp import Platform
from ixmp.backend.jdbc import JDBCBackend
from ixmp.report import Reporter as ixmp_Reporter
from ixmp.testing import assert_logs
from numpy.testing import assert_allclose
from pandas.testing import assert_frame_equal, assert_series_equal

from message_ix import Scenario
from message_ix.report import Reporter, configure
from message_ix.testing import SCENARIO, make_dantzig, make_westeros

# NOTE These tests maybe don't need to be parametrized.
# Does `Reporter.from_scenario()` depend on otherwise untested Scenario functions?


class TestReporter:
    def test_add_sankey(
        self, test_mp: Platform, request: pytest.FixtureRequest
    ) -> None:
        scen = make_westeros(test_mp, solve=True, quiet=True, request=request)
        rep = Reporter.from_scenario(scen, units={"replace": {"-": ""}})

        # Method runs
        key = rep.add_sankey(year=700, node="Westeros")

        # Returns an existing key of the expected form
        assert key.startswith("sankey figure ")

        assert rep.check_keys(key)


def test_reporter_no_solution(
    caplog: pytest.LogCaptureFixture, message_test_mp: Platform
) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    with assert_logs(
        caplog,
        [
            'Scenario "Canning problem (MESSAGE scheme)/standard" has no solution',
            "Some reporting may not function as expected",
        ],
    ):
        rep = Reporter.from_scenario(scen)

    # Input parameters are still available
    demand = rep.full_key("demand")
    result = rep.get(demand)
    assert 3 == len(result)


# IXMP4Backend is currently not storing the MACRO variables 'C' and 'I' for MESSAGE
# models.
MISSING_IXMP4 = {"C:", "C:n", "C:n-y", "C:y", "I:", "I:n", "I:n-y", "I:y"}


def test_reporter_from_scenario(
    message_test_mp: Platform, test_data_path: Path
) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    # Varies between local & CI contexts
    # DEBUG may be due to reuse of test_mp in a non-deterministic order
    if not scen.has_solution():
        scen.solve(quiet=True)

    # IXMPReporter can be initialized on a MESSAGE Scenario
    rep_ix = ixmp_Reporter.from_scenario(scen)

    # message_ix.Reporter can also be initialized
    rep = Reporter.from_scenario(scen)

    # NOTE Used to write out the expected data
    # Path(test_data_path / "reportergraph.txt").write_text(
    #     "\n".join(list(map(str, sorted(rep.graph))))
    # )

    # Quantities have short dimension names
    assert "demand:n-c-l-y-h" in rep, sorted(rep.graph)

    # Aggregates are available
    assert "demand:n-l-h" in rep, sorted(rep.graph)

    # Quantities contain expected data
    coords = dict(n="chicago new-york topeka".split())
    demand = genno.Quantity([300, 325, 275], coords=coords, name="demand")

    # NB the call to squeeze() drops the length-1 dimensions c-l-y-h
    obs = rep.get("demand:n-c-l-y-h").squeeze(drop=True)
    # check_attrs False because we don't get the unit addition in bare xarray
    assert_qty_equal(obs, demand, check_attrs=False)

    # Prepare the expected items in the graphs
    expected_rep_ix_graph_keys = set(
        Path(test_data_path / "reporterixgraph.txt").read_text().split("\n")
    )
    expected_rep_graph_keys = set(
        Path(test_data_path / "reportergraph.txt").read_text().split("\n")
    )
    if not isinstance(message_test_mp._backend, JDBCBackend):
        expected_rep_ix_graph_keys -= MISSING_IXMP4
        expected_rep_graph_keys -= MISSING_IXMP4

    # ixmp.Reporter pre-populated with only model quantities and aggregates
    assert set(map(str, sorted(rep_ix.graph))) == expected_rep_ix_graph_keys

    # message_ix.Reporter pre-populated with additional, derived quantities
    assert set(map(str, sorted(rep.graph))) == expected_rep_graph_keys

    # Derived quantities have expected dimensions
    vom_key = rep.full_key("vom")
    assert vom_key not in rep_ix
    assert vom_key == "vom:nl-t-yv-ya-m-h"

    # …and expected values
    var_cost = rep.get(rep.full_key("var_cost"))
    ACT = rep.get(rep.full_key("ACT"))
    vom = var_cost * ACT
    # check_attrs false because `vom` multiply above does not add units
    assert_qty_equal(vom, rep.get(vom_key))


def test_reporter_from_dantzig(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    scen = make_dantzig(test_mp, solve=True, quiet=True, request=request)

    # Reporter.from_scenario can handle Dantzig example model
    rep = Reporter.from_scenario(scen)

    # Default target can be calculated
    rep.get("all")


def test_reporter_from_westeros(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    scen = make_westeros(test_mp, emissions=True, solve=True, request=request)

    # Reporter.from_scenario can handle Westeros example model
    rep = Reporter.from_scenario(scen)

    # Westeros-specific configuration: '-' is a reserved character in pint
    configure(units={"replace": {"-": ""}})

    # Default target can be calculated
    rep.get("all")

    # message default target can be calculated
    # TODO if df is empty, year is cast to float
    obs = rep.get("message::default")

    # all expected reporting exists
    assert len(obs.data) == 78

    # custom values are correct
    obs = obs.filter(variable="total om*").as_pandas()

    # Produce a merged data frame; this also implies that the same labels exist in `obs`
    df = pd.DataFrame(
        [
            ["total om cost|coal_ppl", 700, 2801.242],
            ["total om cost|coal_ppl", 710, 5321.242],
            ["total om cost|coal_ppl", 720, 6933.333],
            ["total om cost|grid", 700, 880.0],
            ["total om cost|grid", 710, 1312.0],
            ["total om cost|grid", 720, 1664.0],
            ["total om cost|wind_ppl", 700, 400.6596],
            ["total om cost|wind_ppl", 710, 67.32630],
            ["total om cost|wind_ppl", 720, 0.0],
        ],
        columns=["variable", "year", "value"],
    ).merge(obs, on=["variable", "year"], how="outer")

    assert_allclose(df["value_y"], df["value_x"], err_msg=df.to_string())


def test_reporter_as_pyam(
    caplog: pytest.LogCaptureFixture, tmp_path: Path, dantzig_reporter: Reporter
) -> None:
    caplog.set_level(logging.INFO)

    rep = dantzig_reporter
    as_pyam = rep.get_operator("as_pyam")

    # Key for 'ACT' variable at full resolution
    ACT = rep.full_key("ACT")

    # Mapping from dimension IDs to column names
    rename = dict(nl="region", ya="year")

    # Add a task that converts ACT to a pyam.IamDataFrame
    assert as_pyam
    rep.add("ACT IAMC", (partial(as_pyam, rename=rename, drop=["yv"]), "scenario", ACT))

    # Result is an IamDataFrame
    idf1 = rep.get("ACT IAMC")
    assert isinstance(idf1, pyam.IamDataFrame)

    # …of expected length
    assert len(idf1) == 8

    # …in which variables are not renamed
    assert idf1["variable"].unique() == "ACT"

    # Warning was logged because of extra columns
    w = "Extra columns ['h', 'm', 't'] when converting to IAMC format"
    assert ("genno.compat.pyam.util", logging.INFO, w) in caplog.record_tuples

    # Repeat, using the message_ix.Reporter convenience function
    def add_tm(df, name="Activity"):
        """Callback for collapsing ACT columns."""
        df["variable"] = f"{name}|" + df["t"] + "|" + df["m"]
        return df.drop(["t", "m"], axis=1)

    # Use the convenience function to add the node
    with pytest.warns(DeprecationWarning):
        key2 = rep.convert_pyam(ACT, "iamc", rename=rename, collapse=add_tm)
    key2 = rep.add("as_pyam", ACT, "iamc", rename=rename, collapse=add_tm)

    # Keys of added node(s) are returned
    assert isinstance(ACT, genno.Key)
    assert ACT.name + "::iamc" == key2

    caplog.clear()

    # Result
    idf2 = rep.get(key2)
    df2 = idf2.as_pandas()

    # Extra columns have been removed:
    # - m and t by the collapse callback.
    # - h automatically, because 'ya' was used for the year index.
    assert not any(c in df2.columns for c in ["h", "m", "t"])

    # Variable names were formatted by the callback
    reg_var = (
        pd.DataFrame(
            [
                ["seattle", "Activity|canning_plant|production"],
                ["seattle", "Activity|transport_from_seattle|to_new-york"],
                ["seattle", "Activity|transport_from_seattle|to_chicago"],
                ["seattle", "Activity|transport_from_seattle|to_topeka"],
                ["san-diego", "Activity|canning_plant|production"],
                ["san-diego", "Activity|transport_from_san-diego|to_new-york"],
                ["san-diego", "Activity|transport_from_san-diego|to_chicago"],
                ["san-diego", "Activity|transport_from_san-diego|to_topeka"],
            ],
            columns=["region", "variable"],
        )
        if sys.version_info >= (3, 10)
        else pd.DataFrame(
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
    )
    assert_frame_equal(df2[["region", "variable"]], reg_var)

    # message_ix.Reporter uses pyam.IamDataFrame.to_csv() to write to file
    path = tmp_path / "activity.csv"
    rep.write(key2, path)

    # File contents are as expected
    # - With a parametrized `test_mp`, the `dantig_reporter` fixture has scenario name
    #   like "test_reporter_as_pyam[jdbc]" with the backend module name. Truncate this
    #   to compare with the expected data.
    expected = Path(__file__).parent / "data" / "report-pyam-write.csv"
    assert expected.read_text() == re.sub(
        r"(test_reporter_as_pyam)\[(jdbc|ixmp4)\]", r"\1", path.read_text()
    )

    # Use a name map to replace variable names
    replacements = {re.escape("Activity|canning_plant|production"): "Foo"}
    with pytest.warns(DeprecationWarning):
        key3 = rep.convert_pyam(
            ACT, rename=rename, replace=dict(variable=replacements), collapse=add_tm
        )
    key3 = rep.add(
        "as_pyam",
        ACT,
        rename=rename,
        replace=dict(variable=replacements),
        collapse=add_tm,
    )
    df3 = rep.get(key3).as_pandas()

    # Values are the same; different names
    exp = df2[df2.variable == "Activity|canning_plant|production"][
        "value"
    ].reset_index()
    assert all(exp == df3[df3.variable == "Foo"]["value"].reset_index())

    # Now convert variable cost
    cb = partial(add_tm, name="Variable cost")
    with pytest.warns(DeprecationWarning):
        key4 = rep.convert_pyam("var_cost", rename=rename, collapse=cb)
    key4 = rep.add("as_pyam", "var_cost", rename=rename, collapse=cb)

    df4 = rep.get(key4).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df4["unit"] == "USD / case")

    # Also change units
    with pytest.warns(DeprecationWarning):
        key5 = rep.convert_pyam(
            "var_cost", rename=rename, collapse=cb, unit="centiUSD / case"
        )
    key5 = rep.add(
        "as_pyam", "var_cost", rename=rename, collapse=cb, unit="centiUSD / case"
    )

    df5 = rep.get(key5).as_pandas().drop(["model", "scenario"], axis=1)

    # Results have the expected units
    assert all(df5["unit"] == "centiUSD / case")
    assert_series_equal(df4["value"], df5["value"] / 100.0)
