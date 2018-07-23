import numpy as np
import pandas as pd

from message_ix import Scenario

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def calculate_activity(scen, city='seattle'):
    return (
        scen
        .var('ACT')
        .groupby(['technology', 'mode'])['lvl']
        .sum()
        .loc['transport_from_' + city]
    )


def test_add_bound_activity_up(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for act bound
    exp = 0.5 * calculate_activity(scen).sum()
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
    obs = calculate_activity(clone).loc['to_chicago']
    assert np.isclose(obs, exp)


def test_add_bound_activity_up_all_modes(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for act bound
    exp = 0.95 * calculate_activity(scen).sum()
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
    obs = calculate_activity(clone).sum()
    assert np.isclose(obs, exp)


def test_add_share_output(test_mp):
    msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')
    scen = Scenario(test_mp, *msg_multiyear_args)
    scen.solve()
    print(scen.par('output'))
    print(scen.var('ACT'))
    print(scen.set('type_tec'))

    # data for share bound
    print(calculate_activity(scen, city='seattle'))
    print(calculate_activity(scen, city='san-diego'))

    def calc_share(scen):
        a = calculate_activity(scen, city='seattle').loc['to_new-york']
        b = calculate_activity(scen, city='san-diego').loc['to_new-york']
        return a / (a + b)

    exp = 0.95 * calc_share(scen)
    print(exp)
    data = pd.DataFrame({
        'node_loc': 'new-york',
        'type_tec_numerator': 'transport_from_seattle',
        'type_tec_denominator': ['transport_from_seattle', 'transport_from_san-diego'],
        'level': 'consumption',
        'year_act': 2010,
        'time': 'year',
        'unit': 'cases',
        'value': exp,
    })  # , index=[0])

    print(data)

    # # test limiting all modes
    clone = scen.clone('foo', 'baz', keep_sol=False)
    clone.check_out()
    # clone.add_par('bound_activity_up', data)
    # clone.commit('foo')
    # clone.solve()
    # obs = calculate_activity(clone).sum()
    # assert np.isclose(obs, exp)
