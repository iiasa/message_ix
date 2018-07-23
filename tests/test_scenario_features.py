import numpy as np
import pandas as pd

from message_ix import Scenario

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def calculate_seattle_activity(scen):
    return (
        scen
        .var('ACT')
        .groupby(['technology', 'mode'])['lvl']
        .sum()
        .loc['transport_from_seattle']
    )


def test_add_bound_activity_up(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for act bound
    exp = 0.5 * calculate_seattle_activity(scen).sum()
    data = pd.DataFrame({
        'node_loc': 'seattle',
        'technology': 'transport_from_seattle',
        'year_act': 2010,
        'time': 'year',
        'unit': 'cases',
        'mode': 'to_chicago',
        'value': exp,
    }, index=[0])

    # test limiting one mode
    clone = scen.clone('foo', 'bar', keep_sol=False)
    clone.check_out()
    clone.add_par('bound_activity_up', data)
    clone.commit('foo')
    clone.solve()
    obs = calculate_seattle_activity(clone).loc['to_chicago']
    assert np.isclose(obs, exp)


def test_add_bound_activity_up_all_modes(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for act bound
    exp = 0.95 * calculate_seattle_activity(scen).sum()
    data = pd.DataFrame({
        'node_loc': 'seattle',
        'technology': 'transport_from_seattle',
        'year_act': 2010,
        'time': 'year',
        'unit': 'cases',
        'mode': 'all',
        'value': exp,
    }, index=[0])

    # test limiting all modes
    clone = scen.clone('foo', 'baz', keep_sol=False)
    clone.check_out()
    clone.add_par('bound_activity_up', data)
    clone.commit('foo')
    clone.solve()
    obs = calculate_seattle_activity(clone).sum()
    assert np.isclose(obs, exp)
