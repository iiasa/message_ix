from pathlib import Path

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from message_ix import Scenario, macro
from message_ix.models import MACRO
from message_ix.testing import SCENARIO, make_westeros

W_DATA_PATH = Path(__file__).parent / "data" / "westeros_macro_input.xlsx"
MR_DATA_PATH = Path(__file__).parent / "data" / "multiregion_macro_input.xlsx"


class MockScenario:
    def __init__(self):
        self.data = pd.read_excel(MR_DATA_PATH, sheet_name=None, engine="openpyxl")
        for name, df in self.data.items():
            if "year" in df:
                df = df[df.year >= 2030]
                self.data[name] = df

    def has_solution(self):
        return True

    def var(self, name, **kwargs):
        df = self.data["aeei"]
        # add extra commodity to be removed
        extra_commod = df[df.sector == "i_therm"].copy()
        extra_commod["sector"] = self.data["config"]["ignore_sectors"][0]
        # add extra region to be removed
        extra_region = df[df.node == "R11_AFR"].copy()
        extra_region["node"] = self.data["config"]["ignore_nodes"][0]
        df = pd.concat([df, extra_commod, extra_region])

        if name == "DEMAND":
            df = df.rename(columns={"sector": "commodity"})
        elif name in ["COST_NODAL_NET", "PRICE_COMMODITY"]:
            df = df.rename(columns={"sector": "commodity", "value": "lvl"})
            df["lvl"] = 1e3
        return df


@pytest.fixture(scope="class")
def westeros_solved(test_mp):
    yield make_westeros(test_mp, solve=True)


@pytest.fixture(scope="class")
def westeros_not_solved(westeros_solved):
    yield westeros_solved.clone(keep_solution=False)


def test_calc_valid_data_file(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, W_DATA_PATH)
    c.read_data()


def test_calc_invalid_data(westeros_solved):
    with pytest.raises(TypeError, match="neither a dict nor a valid path"):
        macro.Calculate(westeros_solved, list())

    with pytest.raises(ValueError, match="not an Excel data file"):
        macro.Calculate(westeros_solved, Path(__file__).joinpath("other.zip"))


def test_calc_valid_data_dict(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(W_DATA_PATH, sheet_name=None, engine="openpyxl")
    c = macro.Calculate(s, data)
    c.read_data()


def test_calc_no_solution(westeros_not_solved):
    s = westeros_not_solved
    pytest.raises(RuntimeError, macro.Calculate, s, W_DATA_PATH)


def test_config(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, W_DATA_PATH)
    c.nodes = set(list(c.nodes) + ["foo"])
    c.sectors = set(list(c.sectors) + ["bar"])

    assert c.nodes == set(["Westeros", "foo"])
    assert c.sectors == set(["light", "bar"])
    c.read_data()
    assert c.nodes == set(["Westeros"])
    assert c.sectors == set(["light"])


def test_calc_data_missing_par(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(W_DATA_PATH, sheet_name=None, engine="openpyxl")
    data.pop("gdp_calibrate")
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_column(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(W_DATA_PATH, sheet_name=None, engine="openpyxl")
    # skip first data point
    data["gdp_calibrate"] = data["gdp_calibrate"].drop("year", axis=1)
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_datapoint(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(W_DATA_PATH, sheet_name=None, engine="openpyxl")
    # skip first data point
    data["gdp_calibrate"] = data["gdp_calibrate"][1:]
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


#
# Regression tests: these tests were compiled upon moving from R to Python,
# values were confirmed correct at the time and thus are tested explicitly here
#


@pytest.mark.parametrize(
    "method, test, expected",
    (
        ("_growth", "allclose", [0.02658363, 0.04137974, 0.04137974, 0.02918601]),
        ("_rho", "equal", [-4.0]),
        ("_gdp0", "equal", [500.0]),
        ("_k0", "equal", [1500.0]),
        (
            "_total_cost",
            "allclose",
            1e-3 * np.array([15, 17.477751, 22.143634, 28.114812]),
        ),
        ("_price", "allclose", [195, 182.852229, 162.039539, 161.002627]),
        ("_demand", "allclose", [90, 100, 150, 190]),
        ("_bconst", "allclose", [3.6846576e-05]),
        ("_aconst", "allclose", [26.027323]),
    ),
)
def test_calc(westeros_solved, method, test, expected):
    calc = macro.Calculate(westeros_solved, W_DATA_PATH)
    calc.read_data()

    function = getattr(calc, method)
    assertion = getattr(npt, f"assert_{test}")

    assertion(function().values, expected)


def test_init(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"])

    scen = scen.clone("foo", "bar")
    scen.check_out()
    MACRO.initialize(scen)
    scen.commit("foo")
    scen.solve()

    assert np.isclose(scen.var("OBJ")["lvl"], 153.675)
    assert "mapping_macro_sector" in scen.set_list()
    assert "aeei" in scen.par_list()
    assert "DEMAND" in scen.var_list()
    assert "COST_ACCOUNTING_NODAL" in scen.equ_list()


def test_add_model_data(westeros_solved):
    base = westeros_solved
    clone = base.clone("foo", "bar", keep_solution=False)
    clone.check_out()
    MACRO.initialize(clone)
    macro.add_model_data(base, clone, W_DATA_PATH)
    clone.commit("finished adding macro")
    clone.solve()
    obs = clone.var("OBJ")["lvl"]
    exp = base.var("OBJ")["lvl"]
    assert np.isclose(obs, exp)


def test_calibrate(westeros_solved):
    base = westeros_solved
    clone = base.clone(base.model, "test macro calibration", keep_solution=False)
    clone.check_out()
    MACRO.initialize(clone)
    macro.add_model_data(base, clone, W_DATA_PATH)
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


def test_calibrate_roundtrip(westeros_solved):
    # this is a regression test with values observed on Aug 9, 2019
    with_macro = westeros_solved.add_macro(W_DATA_PATH, check_convergence=True)
    aeei = with_macro.par("aeei")["value"].values
    npt.assert_allclose(aeei, 1e-3 * np.array([20, 71.759022, 37.424904, 19.936694]))
    grow = with_macro.par("grow")["value"].values
    npt.assert_allclose(
        grow, 1e-3 * np.array([26.583631, 69.101286, 79.520269, 24.529274])
    )


#
# These are a series of tests to guarantee multiregion/multisector
# behavior is as expected.
#


def test_multiregion_valid_data():
    s = MockScenario()
    c = macro.Calculate(s, MR_DATA_PATH)
    c.read_data()


def test_multiregion_derive_data():
    s = MockScenario()
    c = macro.Calculate(s, MR_DATA_PATH)
    c.read_data()
    c.derive_data()

    nodes = ["R11_AFR", "R11_CPA"]
    sectors = ["i_therm", "rc_spec"]

    # make sure no extraneous data is there
    check = c.data["demand"].reset_index()
    assert (check["node"].unique() == nodes).all()
    assert (check["sector"].unique() == sectors).all()

    obs = c.data["aconst"]
    exp = pd.Series(
        [3.74767687, 0.00285472], name="value", index=pd.Index(nodes, name="node")
    )
    pd.testing.assert_series_equal(obs, exp)

    obs = c.data["bconst"]
    idx = pd.MultiIndex.from_product([nodes, sectors], names=["node", "sector"])
    exp = pd.Series(
        [1.071971e-08, 1.487598e-11, 9.637483e-09, 6.955715e-13],
        name="value",
        index=idx,
    )
    pd.testing.assert_series_equal(obs, exp)
