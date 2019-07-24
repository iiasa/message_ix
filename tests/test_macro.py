import numpy as np

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from message_ix import Scenario, macro
from message_ix.testing import make_westeros

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


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


def test_calc_valid_data(test_mp):
    s = make_westeros(test_mp, solve=True)
    path = Path(__file__).parent / 'data' / 'westeros_macro_input.xlsx'
    c = macro.Calculate(s, path)
    c.read_data()
