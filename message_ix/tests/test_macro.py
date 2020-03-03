import numpy as np

from message_ix import Scenario, macro
from message_ix.testing import SCENARIO


def test_init(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO['dantzig'])

    scen = scen.clone('foo', 'bar')
    scen.check_out()
    macro.init(scen)
    scen.commit('foo')
    scen.solve()

    assert np.isclose(scen.var('OBJ')['lvl'], 153.675)
