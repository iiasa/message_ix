import pytest

import numpy as np
import pandas as pd

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from message_ix import Scenario, macro
from message_ix.testing import make_westeros

# tons of deprecation warnings come from reading excel (xlrd library), ignore
# them for now
pytestmark = pytest.mark.filterwarnings("ignore")

MSG_ARGS = ('canning problem (MESSAGE scheme)', 'standard')

DATA_PATH = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'


@pytest.fixture(scope='module')
def westeros_solved(test_mp):
    return make_westeros(test_mp, solve=True)


@pytest.fixture(scope='module')
def westeros_not_solved(test_mp):
    return make_westeros(test_mp, solve=False)


def test_calc_valid_data_file(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()


def test_calc_valid_data_dict(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(DATA_PATH, sheet_name=None)
    c = macro.Calculate(s, data)
    c.read_data()


def test_calc_no_solution(westeros_not_solved):
    s = westeros_not_solved
    pytest.raises(RuntimeError, macro.Calculate, s, DATA_PATH)


def test_calc_data_missing_par(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(DATA_PATH, sheet_name=None)
    data.pop('gdp_calibrate')
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_column(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(DATA_PATH, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'].drop('year', axis=1)
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)


def test_calc_data_missing_datapoint(westeros_solved):
    s = westeros_solved
    data = pd.read_excel(DATA_PATH, sheet_name=None)
    # skip first data point
    data['gdp_calibrate'] = data['gdp_calibrate'][1:]
    c = macro.Calculate(s, data)
    pytest.raises(ValueError, c.read_data)

#
# Regression tests: these tests were compiled upon moving from R to Python,
# values were confirmed correct at the time and thus are tested explicitly here
#


def test_calc_growth(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._growth()
    assert len(obs) == 3
    obs = obs.values
    exp = np.array([0.041380, 0.041380, 0.029186])
    assert np.isclose(obs, exp).all()


def test_calc_rho(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._rho()
    assert len(obs) == 1
    obs = obs[0]
    exp = -4
    assert obs == exp


def test_calc_gdp0(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._gdp0()
    assert len(obs) == 1
    obs = obs[0]
    exp = 500
    assert obs == exp


def test_calc_k0(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._k0()
    assert len(obs) == 1
    obs = obs[0]
    exp = 1500
    assert obs == exp


def test_calc_total_cost(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._total_cost()
    # 4 values, 3 in model period, one in history
    assert len(obs) == 4
    obs = obs.values
    exp = np.array([15, 17.477751, 22.143633, 28.189798])
    assert np.isclose(obs, exp).all()


def test_calc_price(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._price()
    # 4 values, 3 in model period, one in history
    assert len(obs) == 4
    obs = obs.values
    exp = np.array([195, 183.094376, 161.645111, 161.645111])
    assert np.isclose(obs, exp).all()


def test_calc_demand(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._demand()
    # 4 values, 3 in model period, one in history
    assert len(obs) == 4
    obs = obs.values
    exp = np.array([90, 100, 150, 190])
    assert np.isclose(obs, exp).all()


def test_calc_bconst(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._bconst()
    assert len(obs) == 1
    obs = obs[0]
    exp = 3.6846576e-05
    assert np.isclose(obs, exp)


def test_calc_aconst(westeros_solved):
    s = westeros_solved
    c = macro.Calculate(s, DATA_PATH)
    c.read_data()
    obs = c._aconst()

    assert len(obs) == 1
    obs = obs[0]
    exp = 26.027323
    assert np.isclose(obs, exp)


def test_init(test_mp):
    scen = Scenario(test_mp, *MSG_ARGS)

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


def test_add_macro_data(westeros_solved):
    base = westeros_solved
    clone = base.clone('foo', 'bar', keep_solution=False)
    clone.check_out()
    macro.init(clone)
    macro.add_macro_data(base, clone, DATA_PATH)
    clone.commit('finished adding macro')
    clone.solve()
    obs = clone.var('OBJ')['lvl']
    exp = base.var('OBJ')['lvl']
    assert np.isclose(obs, exp)
