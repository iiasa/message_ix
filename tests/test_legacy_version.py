import numpy as np
from message_ix import Scenario

msg_args = ('canning problem (MESSAGE scheme)', 'standard')
msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')


def test_solve_legacy_scenario(test_legacy_mp):
    scen = Scenario(test_legacy_mp, *msg_args)
    exp = scen.var('OBJ')['lvl']

    # solve scenario, assert that the new objective value is close to previous
    scen.remove_solution()
    scen.solve()
    assert np.isclose(exp, scen.var('OBJ')['lvl'])
