import pytest

import numpy as np
import pandas as pd

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from message_ix import Scenario, macro
from message_ix.testing import make_westeros


def test_init(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO['dantzig'])

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


def test_calc_valid_data_file(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    c = macro.Calculate(s, path)
    c.read_data()


def test_calc_valid_data_dict(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    c = macro.Calculate(s, data)
    c.read_data()


def test_calc_no_solution(test_mp):
    s = make_westeros(test_mp)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    pytest.raises(RuntimeError, macro.Calculate, s, path)


def test_calc_data_missing_par(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    data.pop('gdp_calibrate')
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_column(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'].drop('year', axis=1)
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_datapoint(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    data = pd.read_excel(path, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'][1:]
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)
