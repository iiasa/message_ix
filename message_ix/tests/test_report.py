import logging
import re
from collections import defaultdict
from collections.abc import Generator
from functools import partial
from pathlib import Path

import genno
import numpy as np
import numpy.testing as npt
import pandas as pd
import pyam
import pytest
from genno.testing import assert_qty_equal
from ixmp import Platform
from ixmp.backend import ItemType
from ixmp.backend.jdbc import JDBCBackend
from ixmp.report import Reporter as ixmp_Reporter
from ixmp.testing import assert_logs
from ixmp.util.ixmp4 import is_ixmp4backend
from numpy.testing import assert_allclose
from pandas.testing import assert_frame_equal, assert_series_equal

from message_ix import Scenario, make_df
from message_ix.message import MESSAGE
from message_ix.report import ComputationError, Key, Reporter, configure
from message_ix.testing import SCENARIO, make_dantzig, make_westeros

pytestmark = pytest.mark.ixmp4_209

# NOTE These tests maybe don't need to be parametrized.
# Does `Reporter.from_scenario()` depend on otherwise untested Scenario functions?

#: Expected number of data points for items in the make_dantzig() scenario.
EXP_LEN_DANTZIG = defaultdict(
    lambda: 0,
    ACT=8,
    COMMODITY_BALANCE_GT=5,
    COST_NODAL=6,
    DEMAND=3,
    OBJ=1,
    OBJECTIVE=1,
    PRICE_COMMODITY=5,
    bound_activity_up=2,
    demand=3,
    duration_period=2,
    duration_time=1,
    input=6,
    output=8,
    ref_activity=2,
    var_cost=6,
)
EXP_LEN_DANTZIG.update({"COMMODITY_BALANCE_GT-margin": 5, "OBJECTIVE-margin": 1})

#: Expected number of data points for items in the make_westeros() scenario.
EXP_LEN_WESTEROS = defaultdict(
    lambda: 0,
    ACT=23,
    CAP=23,
    CAP_NEW=12,
    COST_NODAL=6,
    COST_NODAL_NET=3,
    DEMAND=3,
    EMISS=6,
    OBJ=1,
    OBJECTIVE=1,
    PRICE_COMMODITY=9,
    capacity_factor=48,
    demand=5,
    duration_period=5,
    duration_time=1,
    emission_factor=12,
    fix_cost=36,
    growth_activity_up=6,
    historical_activity=3,
    historical_new_capacity=3,
    input=24,
    interestrate=5,
    inv_cost=12,
    output=48,
    technical_lifetime=20,
    var_cost=12,
)
EXP_LEN_WESTEROS.update({"OBJECTIVE-margin": 1})

# IXMP4Backend is currently not storing the MACRO variables 'C' and 'I' for MESSAGE
# models.
MISSING_IXMP4 = {"C:", "C:n", "C:n-y", "C:y", "I:", "I:n", "I:n-y", "I:y"}

# Fixtures


@pytest.fixture(scope="module")
def exp_len_all(test_mp: Platform) -> int:
    """Expected items collected under the "all" reporting key."""

    # - Sets not included in "all".
    # - 1 item each for PAR and VAR.
    # - 2 items (values and marginals) for EQU.
    count = {ItemType.SET: 0, ItemType.PAR: 1, ItemType.EQU: 2, ItemType.VAR: 1}
    N = sum(count[i.type] for i in MESSAGE.items.values())

    # With IXMP4Backend, scenarios do not include variables 'C' and 'I'
    N += 0 if is_ixmp4backend(test_mp._backend) else 2

    return N


@pytest.fixture
def keys(test_data_path: Path) -> Generator[set[str]]:
    """Read two files with lists of keys expected in a :class:`.Reporter` graph.

    Returns
    -------
    list
        with 2 sets including the contents of:

        1. :file:`reporter-keys-ixmp.txt`.
        1. :file:`reporter-keys-message-ix.txt`.
    """
    fn = "reporter-keys-{}.txt"
    return (
        set(test_data_path.joinpath(fn.format(p)).read_text().split("\n")) - {""}
        for p in ("ixmp", "message-ix")
    )


# Tests


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

    def test_gh_988(
        self,
        caplog: pytest.LogCaptureFixture,
        request: pytest.FixtureRequest,
        test_mp: Platform,
    ) -> None:
        """Test of https://github.com/iiasa/message_ix#988."""
        scen = make_dantzig(test_mp, quiet=True, request=request)

        # Remove parameters that were added in iiasa/message_ix#451
        # Not removed: equ COMMODDITY_BALANCE_[GL]T, var COMMODITY_BALANCE
        with scen.transact():
            for name in (
                "input_cap",
                "input_cap_new",
                "input_cap_ret",
                "output_cap",
                "output_cap_new",
                "output_cap_ret",
            ):
                scen.remove_par(name)

        # Reporter.from_scenario() works, despite the missing parameters
        # iiasa/message_ix#988: this raises MissingKeyError
        rep = Reporter.from_scenario(scen, fail_action="raise")

        # Warnings are logged
        pattern = re.compile("is missing 6 parameter.*input_cap_new", re.DOTALL)
        assert any(map(pattern.search, caplog.messages))

        # A full key is available for the task that depends on input_cap_new
        k_full = rep.full_key("in_cap_new")
        # The key has expected dimensions
        assert Key("in_cap_new:nl-t-yv-no-c-l-h") == k_full

        # The key can be computed; the result is an empty Quantity
        result = rep.get(k_full)
        assert 0 == len(result)

    def test_from_scenario(
        self, message_test_mp: Platform, keys: Generator[set[str]]
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
        # Path("reporter-keys-ixmp.txt").write_text(
        #     "\n".join(map(str, sorted(rep_ix.graph)))
        # )
        # Path("reporter-keys-message-ix.txt").write_text(
        #     "\n".join(sorted(map(str, set(rep.graph) - set(rep_ix.graph))))
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
        expected_rep_ix_graph_keys = next(keys)
        expected_rep_graph_keys = expected_rep_ix_graph_keys | next(keys)
        if not isinstance(message_test_mp._backend, JDBCBackend):
            expected_rep_ix_graph_keys -= MISSING_IXMP4
            expected_rep_graph_keys -= MISSING_IXMP4

        # ixmp.Reporter pre-populated with only model quantities and aggregates
        assert expected_rep_ix_graph_keys == set(map(str, rep_ix.graph))

        # message_ix.Reporter pre-populated with additional, derived quantities
        assert expected_rep_graph_keys == set(map(str, rep.graph))

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

    def test_from_scenario_no_solution(
        self, caplog: pytest.LogCaptureFixture, message_test_mp: Platform
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

    def test_from_dantzig(
        self, request: pytest.FixtureRequest, test_mp: Platform, exp_len_all: int
    ) -> None:
        scen = make_dantzig(test_mp, solve=True, quiet=True, request=request)

        # Reporter.from_scenario can handle Dantzig example model
        rep = Reporter.from_scenario(scen)

        # Default target can be calculated
        result = rep.get("all")

        # Result contains data for expected number of model data items
        assert exp_len_all == len(result)

        # Items have expected length
        for qty in result:
            assert EXP_LEN_DANTZIG[qty.name] == len(qty), (
                f"{qty.name}: {qty.to_string()}"
            )

    def test_from_westeros(
        self, request: pytest.FixtureRequest, test_mp: Platform, exp_len_all: int
    ) -> None:
        scen = make_westeros(test_mp, emissions=True, solve=True, request=request)

        # Reporter.from_scenario can handle Westeros example model
        rep = Reporter.from_scenario(scen)

        # Westeros-specific configuration: '-' is a reserved character in pint
        configure(units={"replace": {"-": ""}})

        # Default target can be calculated
        result = rep.get("all")

        # Result contains data for expected number of model data items. On IXMP4Backend,
        # `scen` and thus `result` does not include variables 'C' and 'I'.
        assert exp_len_all == len(result)

        # Items have expected length
        for qty in result:
            assert EXP_LEN_WESTEROS[qty.name] == len(qty)

        # message default target can be calculated
        # FIXME if df is empty, year is cast to float
        obs = rep.get("message::default")

        # all expected reporting exists
        assert len(obs.data) == 78

        # custom values are correct
        obs = obs.filter(variable="total om*").as_pandas()

        # Produce a merged data frame. This also implies that the same labels exist in
        # `obs`.
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


def test_hist(tmp_scenario: Scenario) -> None:
    """Test of https://github.com/iiasa/message_ix#989."""
    s = tmp_scenario

    Y = [-3, -2, -1, 0, 1]
    common = dict(
        commodity="c",
        level="l",
        mode="m",
        node="n",
        node_dest="n",
        node_loc="n",
        technology="t",
        time="h",
        time_dest="h",
        unit="-",
    )
    with s.transact():
        s.add_horizon(Y, 0)
        for name in "commodity", "level", "mode", "node", "technology", "time":
            s.add_set(name, common[name])

        # Add different values for {historical,ref}_activity in each ya:
        # - ya = -3 → historical_activity 1.0, ref_activity 1.1
        # - ya = -2 → historical_activity 2.0, ref_activity 2.2
        # - ya = -1 → historical_activity 3.0, ref_activity 3.3
        ACT = np.array([1.0, 2, 3])
        for k, name in (1.0, "historical_activity"), (1.1, "ref_activity"):
            s.add_par(
                name, make_df(name, year_act=[-3, -2, -1], value=k * ACT, **common)
            )

        # Add output values, distinct for every (yv, ya):
        # - yv = -3 → output = 1.0 in ya==yv, increasing by 0.1 every period
        # - yv = -2 → output = 2.0 in ya==yv, increasing by 0.1 every period
        # - etc.
        name = "output"
        data = common | s.vintage_and_active_years().to_dict() | dict(unit="GWa")
        output = make_df(name, **data).assign(  # type: ignore
            value=lambda df: df.year_vtg + 4 + 0.1 * (df.year_act - df.year_vtg)
        )
        s.add_par(name, output)

    rep = Reporter.from_scenario(s, units=dict(replace={"-": ""}))

    # Full products can be computed without error
    q_hist_full = rep.get("out:*:historical+full")
    q_ref_full = rep.get("out:*:ref+full")

    # Particular values are computed correctly. For (yv, ya) = (-3, -1):
    # - output = 1.2
    # - historical_activity = 3.0
    # - ref_activity = 3.3
    npt.assert_allclose(q_hist_full.sel(yv=-3, ya=-1).item(), 1.2 * 3.0)
    npt.assert_allclose(q_ref_full.sel(yv=-3, ya=-1).item(), 1.2 * 3.3)

    # Values assuming current-year I/O intensitites
    q_hist_current = rep.get("out:*:historical+current")
    q_ref_current = rep.get("out:*:ref+current")

    for q in q_hist_current, q_ref_current:
        assert 3 == len(q)
        # Only values for ya == yv are included
        assert q.to_frame().reset_index().eval("ya == yv").all()

    # Particular values are computed correctly
    npt.assert_allclose(q_hist_full.sel(yv=-2, ya=-2).item(), 2.0 * 2.0)
    npt.assert_allclose(q_ref_full.sel(yv=-2, ya=-2).item(), 2.0 * 2.2)

    # Tasks with +weighted give errors without explicitly supplied weights
    for act in "historical", "ref":
        with pytest.raises(ComputationError, match="Must supply data"):
            rep.get(f"out:*:{act}+weighted")

    # Now add some weights
    df = pd.DataFrame(
        [
            [-3, -3, 1.0],  # Active in ya = -3
            [-3, -2, 0.6],  # Active in ya = -2
            [-2, -2, 0.4],
            [-3, -1, 0.5],  # Active in ya = -1
            [-2, -1, 0.3],
            [-1, -1, 0.2],
        ],
        columns=["yv", "ya", "value"],
    )
    q = genno.Quantity(df.set_index(["yv", "ya"])["value"])

    for act in "historical", "ref":
        # Retrieve full key for shares
        k_share = rep.full_key(f"share:*:out+{act}")
        # Replace the existing key with a task that returns the shares
        rep.add(k_share, q)

    # Full keys, partial sum on "yv" dimension
    k_hist_weighted = rep.full_key("out:*:historical+weighted")
    k_ref_weighted = rep.full_key("out:*:ref+weighted")
    assert "yv" not in Key(k_hist_weighted).dims
    assert "yv" not in Key(k_ref_weighted).dims

    q_hist_weighted = rep.get(k_hist_weighted)
    q_ref_weighted = rep.get(k_ref_weighted)

    # Particular values are computed correctly
    # - historical_activity (ya=-1) = 3.0 multiplied by
    # - output (yv=-3, ya=-1) = 1.2 × share
    #          (yv=-2, ya=-1) = 2.1 × share
    #          (yv=-1, ya=-1) = 3.0 × share
    npt.assert_allclose(
        q_hist_weighted.sel(ya=-1).item(), 3.0 * (0.5 * 1.2 + 0.3 * 2.1 + 0.2 * 3.0)
    )
    # Same shares, different ref_activity
    npt.assert_allclose(
        q_ref_weighted.sel(ya=-1).item(), 3.3 * (0.5 * 1.2 + 0.3 * 2.1 + 0.2 * 3.0)
    )


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
    reg_var = pd.DataFrame(
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
