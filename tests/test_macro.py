import numpy as np

from message_ix import Scenario, macro

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def test_init(test_mp):
    scen = Scenario(test_mp, *msg_args)

    scen = scen.clone('foo', 'bar')
    scen.check_out()
    macro.init(scen)
    scen.commit('foo')
    scen.solve()

    assert np.isclose(scen.var('OBJ')['lvl'], 153.675)
