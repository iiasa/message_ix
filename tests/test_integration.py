import pytest
import numpy as np
import pandas.util.testing as pdt

from ixmp import Platform

from message_ix.testing import make_dantzig, TS_DF, TS_DF_CLEARED


def test_run_clone(tmpdir, test_data_path):
    # this test is designed to cover the full functionality of the GAMS API
    # - creates a new scenario and exports a gdx file
    # - runs the tutorial transport model
    # - reads back the solution from the output
    # - performs the test on the objective value
    mp = Platform(tmpdir, dbtype='HSQLDB')
    scen = make_dantzig(mp, solve=True)
    assert np.isclose(scen.var('OBJ')['lvl'], 153.675)
    pdt.assert_frame_equal(scen.timeseries(iamc=True), TS_DF)

    # cloning with `keep_solution=True` keeps all timeseries and the solution
    # (same behaviour as `ixmp.Scenario`)
    scen2 = scen.clone(keep_solution=True)
    assert np.isclose(scen2.var('OBJ')['lvl'], 153.675)
    pdt.assert_frame_equal(scen2.timeseries(iamc=True), TS_DF)

    # cloning with `keep_solution=False` drops the solution and only keeps
    # timeseries set as `meta=True` or prior to the first model year
    # (DIFFERENT behaviour from `ixmp.Scenario`)
    scen3 = scen.clone(keep_solution=False)
    assert np.isnan(scen3.var('OBJ')['lvl'])
    pdt.assert_frame_equal(scen3.timeseries(iamc=True), TS_DF_CLEARED)

    # cloning with `keep_solution=True` and `shift_first_model_year` raises
    pytest.raises(ValueError, scen.clone, shift_first_model_year=2005)
