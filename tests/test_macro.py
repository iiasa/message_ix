import numpy as np

from message_ix import Scenario, macro

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def test_init(test_mp):
    scen = Scenario(test_mp, *msg_args)
    obs = scen.var('OBJ')['lvl']

    scen = scen.clone('foo', 'bar', keep_sol=False)
    scen.check_out()
    macro.init(scen)
    scen.commit('foo')
    scen.solve()
    exp = scen.var('OBJ')['lvl']

    assert np.isclose(obs, exp)
