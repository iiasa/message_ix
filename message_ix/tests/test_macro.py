from pathlib import Path

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from message_ix import Scenario, macro
from message_ix.models import MACRO
from message_ix.report import Quantity
from message_ix.testing import SCENARIO, make_westeros

# Fixtures


def mr_data_path(n):
    """Path to the test data file for multi-region, multi-sector tests."""
    return Path(__file__).parent.joinpath("data", f"multiregion_macro_input-{n}.xlsx")


@pytest.fixture(scope="session")
def w_data_path():
    """Path to the test data file for Westeros tests."""
    yield Path(__file__).parent.joinpath("data", "westeros_macro_input.xlsx")


@pytest.fixture(scope="function")
def w_data(w_data_path):
    """Data from the Westeros test data file."""
    yield pd.read_excel(w_data_path, sheet_name=None, engine="openpyxl")


@pytest.fixture(scope="module")
def _ws(test_mp, request):
    """Reusable fixture with an instance of the Westeros model."""
    scenario = make_westeros(test_mp, quiet=True, request=request).clone(
        scenario=f"{request.node.name}_test_macro"
    )
    scenario.solve()
    yield scenario


@pytest.fixture
def westeros_solved(request, _ws):
    """Fresh clone of the Westeros model."""
    yield _ws.clone(scenario=request.node.name)


@pytest.fixture
def westeros_not_solved(request, _ws):
    """Fresh clone of the Westeros model, without a solution."""
    yield _ws.clone(scenario=request.node.name, keep_solution=False)


# Tests


def test_calc_valid_data_file(westeros_solved, w_data_path):
    c = macro.prepare_computer(westeros_solved, data=w_data_path)
    c.get("check all")


def test_calc_invalid_data(westeros_solved):
    with pytest.raises(TypeError, match="neither a dict nor a valid path"):
        macro.prepare_computer(westeros_solved, data=list())

    with pytest.raises(ValueError, match="not an Excel data file"):
        macro.prepare_computer(
            westeros_solved, data=Path(__file__).joinpath("other.zip")
        )


def test_calc_valid_data_dict(westeros_solved, w_data):
    c = macro.prepare_computer(westeros_solved, data=w_data)
    c.get("check all")


def test_calc_valid_years(westeros_solved, w_data):
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


def test_calc_no_solution(westeros_not_solved, w_data_path):
    s = westeros_not_solved
    with pytest.raises(RuntimeError, match="solution"):
        macro.prepare_computer(s, data=w_data_path)


def test_config(westeros_solved, w_data_path):
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


def test_calc_data_missing_par(westeros_solved, w_data):
    data = w_data

    data.pop("gdp_calibrate")

    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="gdp_calibrate"):
        c.get("check all")


def test_calc_data_missing_ref(westeros_solved: Scenario, w_data):
    """When "price_ref" is missing, the code computes it by extrapolation."""
    data = w_data

    # NB this doesn't work because extrapolating [511, 162, 161] backwards gives 1134, a
    #    very high value; MACRO errors
    # data.pop("cost_ref")

    data.pop("price_ref")

    c = macro.prepare_computer(westeros_solved, data=data)
    c.get("check all")

    westeros_solved.add_macro(data)


def test_calc_data_missing_column(westeros_solved, w_data):
    data = w_data

    # Drop a column
    data["gdp_calibrate"] = data["gdp_calibrate"].drop("year", axis=1)

    c = macro.prepare_computer(westeros_solved, data=data)
    with pytest.raises(Exception, match="Missing expected columns.*year"):
        c.get("check all")


def test_calc_data_missing_datapoint(westeros_solved, w_data):
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
        ("cost_MESSAGE", "allclose", [6.18242, 8.44930447, 11.89512066, 12.84911389]),
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
def test_calc(westeros_solved, w_data_path, key, test, expected):
    c = macro.prepare_computer(westeros_solved, data=w_data_path)

    assertion = getattr(npt, f"assert_{test}")

    assertion(expected, c.get(key).values)


# Testing how macro handles zero values in PRICE_COMMODITY
def test_calc_price_zero(westeros_solved, w_data_path):
    clone = westeros_solved.clone(scenario="low_demand", keep_solution=False)
    clone.check_out()
    # Lowering demand in the first year
    clone.add_par("demand", ["Westeros", "light", "useful", 700, "year"], 10, "GWa")
    # Making investment and var cost zero for delivering light
    # TODO: these units are based on testing.make_westeros: needs improvement
    clone.add_par("inv_cost", ["Westeros", "bulb", 700], 0, "USD/GWa")
    for y in [690, 700]:
        clone.add_par(
            "var_cost", ["Westeros", "grid", y, 700, "standard", "year"], 0, "USD/GWa"
        )

    clone.commit("demand reduced and zero cost for bulb")
    clone.solve()
    price = clone.var("PRICE_COMMODITY")

    # Assert if there is no zero price (to make sure MACRO receives 0 price)
    assert np.isclose(0, price["lvl"]).any()

    c = macro.prepare_computer(clone, data=w_data_path)
    with pytest.raises(Exception, match="0-price found in MESSAGE variable PRICE_"):
        c.get("price_MESSAGE")


def test_init(message_test_mp):
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


def test_add_model_data(westeros_solved, w_data_path):
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


def test_calibrate(westeros_solved, w_data_path):
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

    # calibration should have changed some/all of these values and none should
    # be NaNs
    assert not np.allclose(start_aeei, end_aeei, rtol=1e-2)
    assert not np.allclose(start_grow, end_grow, rtol=1e-2)
    assert not end_aeei.isnull().any()
    assert not end_grow.isnull().any()


def test_calibrate_roundtrip(westeros_solved, w_data_path):
    # this is a regression test with values observed on May 23, 2024
    with_macro = westeros_solved.add_macro(w_data_path, check_convergence=True)
    aeei = with_macro.par("aeei")["value"].values
    npt.assert_allclose(
        aeei,
        1e-3 * np.array([20.0, -7.56480599206068, 43.6577, 21.18243]),
    )
    grow = with_macro.par("grow")["value"].values
    npt.assert_allclose(
        grow,
        1e-3
        * np.array(
            [
                26.583631,
                69.146018,
                79.138644,
                24.522467,
            ]
        ),
    )


@pytest.fixture
def mr_scenario(test_mp, request):
    """Fixture with a multi-region, multi-sector scenario."""
    scenario = make_westeros(test_mp, request=request)
    with scenario.transact():
        scenario.add_set("year", [2020, 2030, 2040])

    scenario.solve()
    yield scenario


def test_multiregion_valid_data(mr_scenario):
    """Multi-region, multi-sector input data can be checked."""
    s = mr_scenario
    c = macro.prepare_computer(s, data=mr_data_path("2"))
    c.get("check all")


def test_multiregion_derive_data(mr_scenario):
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


def test_multiregion_derive_data_2(mr_scenario):
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


def test_sector_map(westeros_solved, w_data):
    """Calibration works when sector and commodity names are mismatched."""
    for table in "aeei", "config", "demand_ref", "price_ref":
        w_data[table] = w_data[table].replace({"sector": {"light": "FOO"}})

    westeros_solved.add_macro(w_data, check_convergence=True)
