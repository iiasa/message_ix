import pytest

import numpy as np
import pandas as pd

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from message_ix import Scenario, macro
from message_ix.testing import make_westeros


@pytest.fixture(scope='module')
def westeros_solved(test_mp):
    return make_westeros(test_mp, solve=True)


@pytest.fixture(scope='module')
def westeros_not_solved(test_mp):
    return make_westeros(test_mp, solve=False)


def test_init(test_mp):
    scen = Scenario(test_mp, *msg_args)

    scen = scen.clone('foo', 'bar')
    scen.check_out()
    macro.init(scen)
    scen.commit('foo')
    scen.solve()

    assert np.isclose(scen.var('OBJ')['lvl'], 153.675)
    assert 'mapping_macro_sector' in scen.set_list()
    assert 'aeei' in scen.par_list()
    assert 'DEMAND' in scen.var_list()
    assert 'COST_ACCOUNTING_NODAL' in scen.equ_list()


def test_calc_valid_data_file(westeros_solved):
    s = westeros_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    c = macro.Calculate(s, path)
    c.read_data()


def test_calc_valid_data_dict(westeros_solved):
    s = westeros_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    c = macro.Calculate(s, data)
    c.read_data()


def test_calc_no_solution(westeros_not_solved):
    s = westeros_not_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    pytest.raises(RuntimeError, macro.Calculate, s, path)


def test_calc_data_missing_par(westeros_solved):
    s = westeros_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    data.pop('gdp_calibrate')
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_column(westeros_solved):
    s = westeros_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'].drop('year', axis=1)
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_datapoint(westeros_solved):
    s = westeros_solved
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'][1:]
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)
