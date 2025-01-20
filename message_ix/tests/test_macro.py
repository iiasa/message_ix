from collections.abc import Generator
from pathlib import Path
from typing import Any, Literal, Union

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from ixmp import Platform

from message_ix import Scenario, macro
from message_ix.models import MACRO
from message_ix.report import Quantity
from message_ix.testing import SCENARIO, make_westeros

# NOTE These tests maybe don't need to be parametrized
# Do the following depend on otherwise untested Scenario functions?
# Scenario.add_macro()
# macro.prepare_computer()
# macro.add_model_data()
# macro.calibrate()
# MACRO.initialize()


# Fixtures


def mr_data_path(n: str) -> Path:
    """Path to the test data file for multi-region, multi-sector tests."""
    return Path(__file__).parent.joinpath("data", f"multiregion_macro_input-{n}.xlsx")


@pytest.fixture(scope="session")
def w_data_path() -> Generator[Path, Any, None]:
    """Path to the test data file for Westeros tests."""
    yield Path(__file__).parent.joinpath("data", "westeros_macro_input.xlsx")


@pytest.fixture(scope="function")
def w_data(w_data_path: Path) -> Generator[dict[str, pd.DataFrame], Any, None]:
    """Data from the Westeros test data file."""
    yield pd.read_excel(w_data_path, sheet_name=None, engine="openpyxl")


@pytest.fixture(scope="module")
def _ws(
    test_mp: Platform, request: pytest.FixtureRequest
) -> Generator[Scenario, Any, None]:
    """Module-scoped fixture with a solved instance of the Westeros model."""
    yield make_westeros(test_mp, solve=True, request=request)


@pytest.fixture
def westeros_solved(
    request: pytest.FixtureRequest, _ws: Scenario
) -> Generator[Scenario, Any, None]:
    """Fresh clone of the Westeros model."""
    yield _ws.clone(scenario=request.node.name)


@pytest.fixture
def westeros_not_solved(
    request: pytest.FixtureRequest, _ws: Scenario
) -> Generator[Scenario, Any, None]:
    """Fresh clone of the Westeros model, without a solution."""
    yield _ws.clone(scenario=request.node.name, keep_solution=False)


# Tests


def test_calc_valid_data_file(westeros_solved: Scenario, w_data_path: Path) -> None:
    c = macro.prepare_computer(westeros_solved, data=w_data_path)
    c.get("check all")


def test_calc_invalid_data(westeros_solved: Scenario) -> None:
    #  TypeError is raised with invalid input data type
    with pytest.raises(TypeError, match="neither a dict nor a valid path"):
        macro.prepare_computer(westeros_solved, data=list())  # type: ignore [arg-type]

    with pytest.raises(ValueError, match="not an Excel data file"):
        macro.prepare_computer(
            westeros_solved, data=Path(__file__).joinpath("other.zip")
        )


def test_calc_valid_data_dict(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    c = macro.prepare_computer(westeros_solved, data=w_data)
    c.get("check all")


def test_calc_valid_years(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    """Select desirable years from a config file in Excel format."""
    data = w_data

    # Add an arbitrary year
    arbitrary_yr = 2021
    data["gdp_calibrate"] = pd.concat(
        [data["gdp_calibrate"], data["gdp_calibrate"].assign(year=arbitrary_yr)]
    )

    # Check the arbitrary year is not in config
    assert arbitrary_yr not in data["config"]["year"]

    # But it is in gdp_calibrate
    assert arbitrary_yr in set(data["gdp_calibrate"]["year"])

    # And macro does calibration without error
    westeros_solved.add_macro(data=data)


def test_calc_no_solution(westeros_not_solved: Scenario, w_data_path: Path) -> None:
    s = westeros_not_solved
    with pytest.raises(RuntimeError, match="solution"):
        macro.prepare_computer(s, data=w_data_path)


def test_config(westeros_solved: Scenario, w_data_path: Path) -> None:
    c = macro.prepare_computer(westeros_solved, data=w_data_path)
    assert "config::macro" in c.graph
    assert "sector" in c.get("config::macro")
    assert {"Westeros"} == c.get("node::macro")
    assert {"light"} == c.get("sector::macro")

    # Missing columns in config raises an exception
    data = c.get("data")
    data["config"] = data["config"][["node", "sector", "commodity", "year"]]
    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="level"):
        c.get("check all")

    # Entirely missing config raises an exception
    data.pop("config")
    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="config"):
        c.get("check all")


def test_calc_data_missing_par(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    data = w_data

    data.pop("gdp_calibrate")

    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="gdp_calibrate"):
        c.get("check all")


def test_calc_data_missing_ref(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    """When "price_ref" is missing, the code computes it by extrapolation."""
    data = w_data

    # NB this doesn't work because extrapolating [511, 162, 161] backwards gives 1134, a
    #    very high value; MACRO errors
    # data.pop("cost_ref")

    data.pop("price_ref")

    c = macro.prepare_computer(westeros_solved, data=data)
    c.get("check all")

    westeros_solved.add_macro(data)


def test_calc_data_missing_column(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    data = w_data

    # Drop a column
    data["gdp_calibrate"] = data["gdp_calibrate"].drop("year", axis=1)

    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="Missing expected columns.*year"):
        c.get("check all")


def test_calc_data_missing_datapoint(
    westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]
) -> None:
    data = w_data

    # Skip first data point
    data["gdp_calibrate"] = data["gdp_calibrate"][1:]

    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="Must provide two gdp_calibrate data points"):
        c.get("check all")


#
# Regression tests: these tests were compiled upon moving from R to Python,
# values were confirmed correct at the time and thus are tested explicitly here
#


@pytest.mark.parametrize(
    "key, test, expected",
    (
        ("grow", "allclose", [0.02658363, 0.04137974, 0.04137974, 0.02918601]),
        ("rho", "equal", [-4.0]),
        ("historical_gdp", "equal", [500.0]),
        ("k0", "equal", [1500.0]),
        # These values updated to align with changes in
        # https://github.com/iiasa/message_ix/pull/924
        ("cost_MESSAGE", "allclose", [6.18242, 8.801164, 11.845227, 12.845227]),
        (
            "price_MESSAGE",
            "allclose",
            [211.0, 512.03088025, 162.65962971, 160.65616805],
        ),
        ("demand_MESSAGE", "allclose", [27, 55, 82, 104]),
        ("prfconst", "allclose", [9.68838201e-08]),
        ("lakl", "allclose", [26.027323]),
    ),
)
def test_calc(
    westeros_solved: Scenario,
    w_data_path: Path,
    key: str,
    test: Literal["allclose", "equal"],
    expected: Union[list[float], list[int]],
) -> None:
    """Test calculation of intermediate values on a solved Westeros scenario."""
    c = macro.prepare_computer(westeros_solved, data=w_data_path)

    assertion = getattr(npt, f"assert_{test}")

    assertion(c.get(key).values, expected)


def test_calc_price_zero(westeros_not_solved: Scenario, w_data_path: Path) -> None:
    """MACRO raises an exception for zero values in PRICE_COMMODITY."""
    # Prepare a Scenario
    s = westeros_not_solved
    y = list(s.set("year"))
    yv = y[: y.index(720)]

    # Set costs to zero for technologies possibly active in the first period
    filters = dict(technology=["bulb", "coal_ppl", "grid", "wind_ppl"], year_vtg=yv)
    with s.transact("test_calc_price_zero"):
        for name in "fix_cost", "inv_cost", "var_cost":
            s.add_par(name, s.par(name, filters=filters).assign(value=0))

    s.solve()

    # Confirm that there are zeroes in PRICE_COMMODITY to trigger the exception
    pc = s.var("PRICE_COMMODITY")
    assert np.isclose(0, pc["lvl"]).any(), f"No zero values in:\n{pc.to_string()}"

    c = macro.prepare_computer(s, data=w_data_path)
    with pytest.raises(Exception, match="0-price found in MESSAGE variable PRICE_"):
        c.get("price_MESSAGE")


def test_init(message_test_mp: Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    scen = scen.clone("foo", "bar")
    scen.check_out()
    MACRO.initialize(scen)
    scen.commit("foo")
    scen.solve(quiet=True)

    assert np.isclose(scen.var("OBJ")["lvl"], 153.675)
    assert "mapping_macro_sector" in scen.set_list()
    assert "aeei" in scen.par_list()
    assert "DEMAND" in scen.var_list()
    assert "COST_ACCOUNTING_NODAL" in scen.equ_list()


def test_add_model_data(westeros_solved: Scenario, w_data_path: Path) -> None:
    base = westeros_solved
    clone = base.clone(scenario=f"{base.scenario} cloned", keep_solution=False)
    clone.check_out()
    MACRO.initialize(clone)
    macro.add_model_data(base, clone, w_data_path)
    clone.commit("finished adding macro")
    clone.solve(quiet=True)
    obs = clone.var("OBJ")["lvl"]
    exp = base.var("OBJ")["lvl"]
    assert np.isclose(obs, exp)


def test_calibrate(westeros_solved: Scenario, w_data_path: Path) -> None:
    """Test that :func:`.add_model_data` updates ``aeei`` and ``grow``."""
    base = westeros_solved
    clone = base.clone(base.model, "test macro calibration", keep_solution=False)
    clone.check_out()
    MACRO.initialize(clone)
    macro.add_model_data(base, clone, w_data_path)
    clone.commit("finished adding macro")

    start_aeei = clone.par("aeei")["value"]
    start_grow = clone.par("grow")["value"]

    macro.calibrate(clone, check_convergence=True)

    end_aeei = clone.par("aeei")["value"]
    end_grow = clone.par("grow")["value"]

    # calibration should have changed some/all of these values and none should be NaNs
    assert not np.allclose(start_aeei, end_aeei, rtol=1e-2)
    assert not np.allclose(start_grow, end_grow, rtol=1e-2)
    assert not end_aeei.isnull().any()
    assert not end_grow.isnull().any()


@pytest.mark.parametrize(
    "kwargs",
    (
        {},  # Default concurrent=0
        dict(concurrent=0),  # Explicit value, same as default
        dict(concurrent=1),
        pytest.param(
            dict(concurrent=2),
            marks=pytest.mark.xfail(raises=ValueError, reason="Invalid value"),
        ),
    ),
)
def test_calibrate_roundtrip(
    westeros_solved: Scenario, w_data_path: Path, kwargs
) -> None:
    """Ensure certain values occur after checking convergence.

    The specific values used here were re-checked in :pull:`924`.
    """
    # this is a regression test with values observed on May 23, 2024
    with_macro = westeros_solved.add_macro(
        w_data_path, check_convergence=True, **kwargs
    )
    npt.assert_allclose(
        with_macro.par("aeei")["value"].values,
        1e-3 * np.array([20.0, -7.5674349, 43.659505, 21.182828]),
    )
    npt.assert_allclose(
        with_macro.par("grow")["value"].values,
        1e-3 * np.array([26.58363, 69.14695, 79.13789, 24.52248]),
    )


@pytest.fixture
def mr_scenario(
    test_mp: Platform, request: pytest.FixtureRequest
) -> Generator[Scenario, Any, None]:
    """Fixture with a multi-region, multi-sector scenario."""
    scenario = make_westeros(test_mp, request=request)
    with scenario.transact():
        scenario.add_set("year", [2020, 2030, 2040])

    scenario.solve()
    yield scenario


def test_multiregion_valid_data(mr_scenario: Scenario) -> None:
    """Multi-region, multi-sector input data can be checked."""
    s = mr_scenario
    c = macro.prepare_computer(s, data=mr_data_path("2"))
    c.get("check all")


def test_multiregion_derive_data(mr_scenario: Scenario) -> None:
    s = mr_scenario
    path = mr_data_path("1")
    c = macro.prepare_computer(s, data=path)

    # Fake some data; this emulates the behaviour of the MockScenario class formerly
    # used in this file
    tmp = (
        pd.read_excel(path, sheet_name="aeei")
        .rename(columns={"node": "n", "sector": "c", "year": "y"})
        .set_index(["n", "c", "y"])
    )
    c.add("DEMAND:n-y-c", Quantity(tmp["value"]), sums=True)
    c.add("COST_NODAL_NET:n-y-c", Quantity(tmp.assign(value=1e3)["value"]), sums=True)
    c.add("PRICE_COMMODITY:n-y-c", Quantity(tmp.assign(value=1e3)["value"]), sums=True)
    c.add("ym1", 2020)

    c.get("check all")

    nodes = ["R11_AFR", "R11_CPA"]
    sectors = ["i_therm", "rc_spec"]

    # make sure no extraneous data is there
    check = c.get("demand_MESSAGE").reset_index()
    assert set(check["node"].unique()) == set(nodes)
    assert set(check["sector"].unique()) == set(sectors)

    obs = c.get("lakl")
    exp = pd.Series(
        [3.74767687, 0.00285472], name="value", index=pd.Index(nodes, name="node")
    )
    pd.testing.assert_series_equal(obs, exp)

    obs = c.get("prfconst")
    idx = pd.MultiIndex.from_product([nodes, sectors], names=["node", "sector"])
    exp = pd.Series(
        [1.071971e-08, 1.487598e-11, 9.637483e-09, 6.955715e-13],
        name="value",
        index=idx,
    )
    pd.testing.assert_series_equal(obs, exp)


def test_multiregion_derive_data_2(mr_scenario: Scenario) -> None:
    """Multi-region multi-sector data can be computed."""
    s = mr_scenario
    c = macro.prepare_computer(s, data=mr_data_path("2"))

    c.get("check all")

    nodes = ["Westeros", "Essos"]
    sectors = ["light"]

    # make sure no extraneous data is there
    check = c.get("demand_MESSAGE").reset_index()
    assert set(check["node"].unique()) == set(nodes)
    assert set(check["sector"].unique()) == set(sectors)


def test_sector_map(westeros_solved: Scenario, w_data: dict[str, pd.DataFrame]) -> None:
    """Calibration works when sector and commodity names are mismatched."""
    for table in "aeei", "config", "demand_ref", "price_ref":
        w_data[table] = w_data[table].replace({"sector": {"light": "FOO"}})

    westeros_solved.add_macro(w_data, check_convergence=True)
