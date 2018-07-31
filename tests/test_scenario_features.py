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


def test_add_share_output_up(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, city='seattle').loc['to_new-york']
        b = calculate_activity(s, city='san-diego').loc['to_new-york']
        return a / (a + b)

    exp = 0.95 * calc_share(scen)

    # add share constraints
    clone = scen.clone('foo', 'baz', keep_sol=False)
    clone.check_out()
    clone.add_set('type_tec', ['share', 'total'])
    cat_tec = [
        ['share', 'transport_from_seattle'],
        ['total', 'transport_from_seattle'],
        ['total', 'transport_from_san-diego'],
    ]
    clone.add_set('cat_tec', cat_tec)
    clone.add_set('shares', 'test-share')
    clone.add_set('map_shares_commodity_level',
                  pd.DataFrame({
                      'shares': 'test-share',
                      'commodity': 'cases',
                      'level': 'consumption',
                      'type_tec_share': 'share',
                      'type_tec_total': 'total',
                  }, index=[0]))
    clone.add_par('share_factor_up',
                  pd.DataFrame({
                      'shares': 'test-share',
                      'node_loc': 'new-york',
                      'year_act': 2010,
                      'time': 'year',
                      'unit': 'cases',
                      'value': exp,
                  }, index=[0]))
    clone.commit('foo')
    clone.solve()
    obs = calc_share(clone)
    assert np.isclose(obs, exp)


def test_add_share_output_lo(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, city='seattle').loc['to_new-york']
        b = calculate_activity(s, city='san-diego').loc['to_new-york']
        return a / (a + b)

    exp = 1.05 * calc_share(scen)

    # add share constraints
    clone = scen.clone('foo', 'baz', keep_sol=False)
    clone.check_out()
    clone.add_set('type_tec', ['share', 'total'])
    cat_tec = [
        ['share', 'transport_from_seattle'],
        ['total', 'transport_from_seattle'],
        ['total', 'transport_from_san-diego'],
    ]
    clone.add_set('cat_tec', cat_tec)
    clone.add_set('shares', 'test-share')
    clone.add_set('map_shares_commodity_level',
                  pd.DataFrame({
                      'shares': 'test-share',
                      'commodity': 'cases',
                      'level': 'consumption',
                      'type_tec_share': 'share',
                      'type_tec_total': 'total',
                  }, index=[0]))
    clone.add_par('share_factor_lo',
                  pd.DataFrame({
                      'shares': 'test-share',
                      'node_loc': 'new-york',
                      'year_act': 2010,
                      'time': 'year',
                      'unit': 'cases',
                      'value': exp,
                  }, index=[0]))
    clone.commit('foo')
    clone.solve()
    obs = calc_share(clone)
    assert np.isclose(obs, exp)
