import copy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from ixmp import Platform
from numpy import testing as npt
from pandas.testing import assert_frame_equal

from message_ix import Scenario
from message_ix.testing import SCENARIO, TS_DF, TS_DF_CLEARED, make_dantzig


def test_run_clone(tmpdir: Path, request: pytest.FixtureRequest) -> None:
    # this test is designed to cover the full functionality of the GAMS API
    # - initialize a new ixmp platform instance
    # - create a new scenario based on Dantzigs tutorial transport model
    # - solve the model and read back the solution from the output
    # - perform tests on the objective value and the timeseries data
    mp = Platform(driver="hsqldb", path=tmpdir / "db")
    scen = make_dantzig(mp, solve=True, request=request)
    assert np.isclose(scen.var("OBJ")["lvl"], 153.675)
    assert scen.firstmodelyear == 1963
    expected = TS_DF.copy()
    assert_frame_equal(
        scen.timeseries(iamc=True), expected.assign(scenario=request.node.name)
    )

    # cloning with `keep_solution=True` keeps all timeseries and the solution
    # (same behaviour as `ixmp.Scenario`)
    scen2 = scen.clone(scenario=request.node.name + "_clone", keep_solution=True)
    assert np.isclose(scen2.var("OBJ")["lvl"], 153.675)
    assert scen2.firstmodelyear == 1963
    expected = TS_DF.copy()
    assert_frame_equal(
        scen2.timeseries(iamc=True),
        expected.assign(scenario=request.node.name + "_clone"),
    )

    # cloning with `keep_solution=False` drops the solution and only keeps
    # timeseries set as `meta=True` or prior to the first model year
    # (DIFFERENT behaviour from `ixmp.Scenario`)
    scen3 = scen.clone(scenario=request.node.name + "_clone_2", keep_solution=False)
    assert np.isnan(scen3.var("OBJ")["lvl"])
    assert scen3.firstmodelyear == 1963
    expected = TS_DF_CLEARED.copy()
    assert_frame_equal(
        scen3.timeseries(iamc=True),
        expected.assign(scenario=request.node.name + "_clone_2"),
    )


# TODO ixmp4-remove_solution() doesn't seem to remove the timeseries values for
# 1963 and 1964 yet
@pytest.mark.jdbc
def test_run_remove_solution(test_mp: Platform, request: pytest.FixtureRequest) -> None:
    # create a new instance of the transport problem and solve it
    scen = make_dantzig(test_mp, solve=True, quiet=True, request=request)
    assert np.isclose(scen.var("OBJ")["lvl"], 153.675)

    # check that re-solving the model will raise an error if a solution exists
    pytest.raises(ValueError, scen.solve)

    # check that removing solution with a first-model-year arg raises an error
    # (DIFFERENT behaviour from `ixmp.Scenario`)
    pytest.raises(TypeError, scen.remove_solution, first_model_year=1964)

    # check that removing solution does not delete timeseries data
    # before first model year (DIFFERENT behaviour from `ixmp.Scenario`)
    scen.remove_solution()
    assert scen.firstmodelyear == 1963
    assert_frame_equal(
        scen.timeseries(iamc=True), TS_DF_CLEARED.assign(scenario=scen.scenario)
    )


# TODO IXMP4Backend doesn't support clone(shift_first_model_year=...) yet
@pytest.mark.jdbc
def test_shift_first_model_year(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
    scen = make_dantzig(
        test_mp, solve=True, multi_year=True, quiet=True, request=request
    )

    # assert that `historical_activity` is empty in the source scenario
    assert scen.par("historical_activity").empty

    # clone and shift first model year
    clone = scen.clone(
        scenario=request.node.name + "_multi-year", shift_first_model_year=1964
    )

    exp = TS_DF.copy()
    exp.loc[0, 1964] = np.nan
    exp["scenario"] = request.node.name + "_multi-year"

    # check that solution and timeseries in new model horizon have been removed
    assert np.isnan(clone.var("OBJ")["lvl"])
    assert_frame_equal(exp, clone.timeseries(iamc=True))
    assert clone.firstmodelyear == 1964
    # check that the variable `ACT` is now the parameter `historical_activity`
    assert not clone.par("historical_activity").empty


def scenario_list(mp: Platform) -> pd.DataFrame:
    return mp.scenario_list(default=False)[["model", "scenario"]]


def assert_multi_db(mp1: Platform, mp2: Platform) -> None:
    assert_frame_equal(scenario_list(mp1), scenario_list(mp2))


# NOTE This is not parametrized, but likely should be
def test_multi_db_run(tmpdir: Path, request: pytest.FixtureRequest) -> None:
    # create a new instance of the transport problem and solve it
    mp1 = Platform(driver="hsqldb", path=tmpdir / "mp1")
    scen1 = make_dantzig(mp1, solve=True, quiet=True, request=request)

    mp2 = Platform(driver="hsqldb", path=tmpdir / "mp2")
    # add other unit to make sure that the mapping is correct during clone
    mp2.add_unit("wrong_unit")
    mp2.add_region("wrong_region", "country")

    # check that cloning across platforms must copy the full solution
    dest = dict(platform=mp2)
    pytest.raises(NotImplementedError, scen1.clone, keep_solution=False, **dest)
    pytest.raises(NotImplementedError, scen1.clone, shift_first_model_year=1964, **dest)

    # clone solved model across platforms (with default settings)
    scen1.clone(platform=mp2, scenario=request.node.name, keep_solution=True)

    # close the db to ensure that data and solution of the clone are saved
    mp2.close_db()
    del mp2

    # reopen the connection to the second platform and reload scenario
    _mp2 = Platform(driver="hsqldb", path=tmpdir / "mp2")
    to_be_loaded = copy.deepcopy(SCENARIO["dantzig"])
    to_be_loaded["scenario"] = request.node.name
    scen2 = Scenario(_mp2, **to_be_loaded)
    assert_multi_db(mp1, _mp2)

    # check that sets, variables and parameter were copied correctly
    npt.assert_array_equal(scen1.set("node"), scen2.set("node"))
    scen2.firstmodelyear == 1963
    assert_frame_equal(scen1.par("var_cost"), scen2.par("var_cost"))
    assert np.isclose(scen2.var("OBJ")["lvl"], 153.675)
    assert_frame_equal(scen1.var("ACT"), scen2.var("ACT"))

    expected = TS_DF.copy()
    # check that custom unit, region and timeseries are migrated correctly
    assert_frame_equal(
        scen2.timeseries(iamc=True), expected.assign(scenario=request.node.name)
    )
