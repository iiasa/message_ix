import numpy as np
import pandas as pd

from message_ix import Scenario

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def add_addon(s):
    s.check_out()
    s.add_set('technology', 'canning_addon')
    s.add_set('addon', 'canning_addon')
    s.add_cat('addon', 'better_production', 'canning_addon')
    s.add_set('map_tec_addon', ['canning_plant', 'better_production'])
    s.commit('adding addon technology')


# reduce max activity from one canning plant, has to be compensated by addon
def test_addon_tec(test_mp):
    scen = Scenario(test_mp, *msg_args).clone(scen='addon', keep_sol=False)

    add_addon(scen)

    f = {'technology': 'canning_plant', 'node_loc': 'seattle'}

    scen.check_out()

    var = scen.par('var_cost', {'node_loc': "seattle",
                                'technology': "transport_from_seattle",
                                'mode': "to_new-york"})
    # add negative csostzs to addon to ensure that upper bound works
    var['technology'] = 'canning_addon'
    var['mode'] = 'production'
    var['value'] = -1
    scen.add_par('var_cost', var)

    bda = scen.par('bound_activity_up', f)
    bda['value'] = bda['value'] / 2
    scen.add_par('bound_activity_up', bda)

    outp = scen.par('output', f)
    outp['technology'] = 'canning_addon'
    scen.add_par('output', outp)

    scen.commit('changing output and bounds')
    scen.solve()

    exp = scen.var('ACT', f)['lvl']
    obs = scen.var('ACT', {'technology': 'canning_addon',
                           'node_loc': 'seattle'})['lvl']
    assert np.isclose(exp, obs)


# introduce addon technology with positive costs, add minimum mitigation
def test_addon_tec_minimum(test_mp):
    scen = Scenario(test_mp, *msg_args).clone(scen='addon_min', keep_sol=False)

    add_addon(scen)

    scen.check_out()

    var = scen.par('var_cost', {'node_loc': "seattle",
                                'technology': "transport_from_seattle",
                                'mode': "to_new-york"})
    var['technology'] = 'canning_addon'
    var['mode'] = 'production'
    var['value'] = 1
    scen.add_par('var_cost', var)

    # add zero output explicity to make sure that map_tec is generated
    outp = scen.par('output', {'technology': 'canning_plant',
                               'node_loc': 'seattle'})
    outp['technology'] = 'canning_addon'
    outp['value'] = 0
    scen.add_par('output', outp)

    addon_min = pd.DataFrame({
            'node': 'seattle',
            'technology': 'canning_plant',
            'year': 2010,
            'mode': 'production',
            'time': 'year',
            'type_addon': 'better_production',
            'value': 0.5,
            'unit': '%'},
            index=[0])
    scen.add_par('addon_minimum', addon_min)

    scen.commit('changing output and bounds')
    scen.solve()

    exp = scen.var('ACT', {'technology': 'canning_plant',
                           'node_loc': 'seattle'})['lvl'] * 0.5
    obs = scen.var('ACT', {'technology': 'canning_addon',
                           'node_loc': 'seattle'})['lvl']
    assert np.isclose(exp, obs)
