from message_ix import Scenario
import pandas as pd
import numpy.testing as npt

MODEL = 'test_emissions_price'


def model_setup(scen, years):
    scen.add_spatial_sets({'country': 'node'})
    scen.add_set('commodity', 'comm')
    scen.add_set('level', 'level')
    scen.add_set('year', years)

    scen.add_set('technology', ['dirty_tec', 'clean_tec'])
    scen.add_set('mode', 'mode')

    scen.add_set('emission', 'co2')
    scen.add_cat('emission', 'ghg', 'co2')

    for y in years:
        scen.add_par('interestrate', y, 0.05, '-')
        scen.add_par('demand', ['node', 'comm', 'level', y, 'year'], 1, 'GWa')

        # the dirty technology is free (no costs) but has emissions
        output_specs = ['node', 'comm', 'level', 'year', 'year']
        tec_specs = ['node', 'dirty_tec', y, y, 'mode']
        scen.add_par('output', tec_specs + output_specs, 1, 'GWa')
        scen.add_par('emission_factor', tec_specs + ['co2'], 1, 'tCO2')

        # the clean technology has variable costs but no emissions
        tec_specs = ['node', 'clean_tec', y, y, 'mode']
        scen.add_par('output', tec_specs + output_specs, 1, 'GWa')
        scen.add_par('var_cost', tec_specs + ['year'], 1, 'USD/GWa')


def test_no_constraint(test_mp):
    scen = Scenario(test_mp, MODEL, 'no_constraint', version='new')
    model_setup(scen, [2020, 2030])
    scen.commit('initialize test scenario')
    scen.solve()

    assert scen.var('OBJ')['lvl'] == 0
    assert scen.var('PRICE_EMISSION').empty


def test_cumulative_equidistant(test_mp):
    scen = Scenario(test_mp, MODEL, 'cum_equidistant', version='new')
    years = [2020, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat('year', 'cumulative', years)
    scen.add_par('bound_emission',
                 ['World', 'ghg', 'all', 'cumulative'], 0, 'tCO2')
    scen.commit('initialize test scenario')
    scen.solve()

    assert scen.var('OBJ')['lvl'] > 0
    obs = scen.var('PRICE_EMISSION')['lvl'].values
    npt.assert_allclose(obs, [1.05**(y - years[0]) for y in years])


def test_per_period_equidistant(test_mp):
    scen = Scenario(test_mp, MODEL, 'per_period_equidistant', version='new')
    years = [2020, 2030, 2040]

    model_setup(scen, years)
    for y in years:
        scen.add_cat('year', y, y)
        scen.add_par('bound_emission',
                     ['World', 'ghg', 'all', y], 0, 'tCO2')
    scen.commit('initialize test scenario')
    scen.solve()

    assert scen.var('OBJ')['lvl'] > 0
    obs = scen.var('PRICE_EMISSION')['lvl']
    npt.assert_allclose(obs, [1] * 3)


def test_cumulative_variable_periodlength(test_mp):
    scen = Scenario(test_mp, MODEL, 'cum_equidistant', version='new')
    years = [2020, 2025, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat('year', 'cumulative', years)
    scen.add_par('bound_emission',
                 ['World', 'ghg', 'all', 'cumulative'], 0, 'tCO2')
    scen.commit('initialize test scenario')
    scen.solve()

    assert scen.var('OBJ')['lvl'] > 0
    obs = scen.var('PRICE_EMISSION')['lvl'].values
    npt.assert_allclose(obs, [1.05**(y - years[0]) for y in years])


def test_per_period_variable_periodlength(test_mp):
    scen = Scenario(test_mp, MODEL, 'cum_equidistant', version='new')
    years = [2020, 2025, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat('year', 'cumulative', years)
    scen.add_par('bound_emission',
                 ['World', 'ghg', 'all', 'cumulative'], 0, 'tCO2')
    scen.commit('initialize test scenario')
    scen.solve()

    assert scen.var('OBJ')['lvl'] > 0
    obs = scen.var('PRICE_EMISSION')['lvl'].values
    npt.assert_allclose(obs, [1] * 4)
