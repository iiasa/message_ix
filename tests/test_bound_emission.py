
from message_ix import Scenario


def model_setup(scen, years):
    scen.add_set('node', 'node')
    scen.add_set('lvl_spatial', 'country')
    scen.add_set('map_spatial_hierarchy', ['country', 'node', 'World'])
    scen.add_set('commodity', 'comm')
    scen.add_set('emission', 'emiss')
    scen.add_set('type_emission', 't_emiss')
    scen.add_set('cat_emission', ['t_emiss', 'emiss'])
    scen.add_set('level', 'level')
    scen.add_set('year', years)
    scen.add_set('type_year', years)

    scen.add_set('technology', ['tec1', 'tec2'])
    scen.add_set('mode', 'mode')
    output_specs = ['node', 'comm', 'level', 'year', 'year']
    dict_var_cost = {'tec1': 1, 'tec2': 2}
    dict_emission_factor = {'tec1': 1.5, 'tec2': 1}

    for yr in years:
        scen.add_par('demand', ['node', 'comm', 'level', yr, 'year'], 1, 'GWa')
        for t in dict_var_cost.keys():
            tec_specs = ['node', t, yr, yr, 'mode']
            scen.add_par('output', tec_specs + output_specs, 1, 'GWa')
            scen.add_par('var_cost',
                         tec_specs + ['year'], dict_var_cost[t], 'USD/GWa')
            scen.add_par('emission_factor',
                         tec_specs + ['emiss'], dict_emission_factor[t], '???')


def add_bound_emission(scen, bound, year='cumulative'):
    if scen.has_solution():
        scen.remove_solution()
    scen.check_out()
    scen.add_par('bound_emission',
                 ['node', 't_emiss', 'all', year], bound, '???')
    scen.commit('Emission bound added')


def test_bound_emission_10y(test_mp):
    scen = Scenario(test_mp, 'test_bound_emission', 'standard', version='new')
    model_setup(scen, [2020, 2030, 2040])
    scen.commit('initialize test model')
    add_bound_emission(scen, bound=1.250)
    scen.solve(case='bound_emission_10y')

    assert scen.var('EMISS')['lvl'].mean() <= float(scen.par('bound_emission'
                                                             )['value'])


def test_bound_emission_5y(test_mp):
    scen = Scenario(test_mp, 'test_bound_emission', 'standard', version='new')
    model_setup(scen, [2020, 2025, 2030, 2040, 2050])
    scen.commit('initialize test model')
    add_bound_emission(scen, bound=1.250)
    scen.solve(case='bound_emission_5y')

    assert scen.var('EMISS')['lvl'].mean() <= float(scen.par('bound_emission'
                                                             )['value'])
