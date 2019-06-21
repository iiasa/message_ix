# -*- coding: utf-8 -*-
from message_ix import Scenario
from message_ix.tools.add_year import add_year
import pytest


def model_setup(scen, data):
    years = sorted(list(set(data.keys())))
    scen.add_set('node', 'node')
    scen.add_set('commodity', 'comm')
    scen.add_set('level', 'level')
    scen.add_set('year', years)
    scen.add_set('technology', 'tec')
    scen.add_set('mode', 'mode')
    output_specs = ['node', 'comm', 'level', 'year', 'year']

    for (yr, value) in data.items():
        scen.add_par('demand', ['node', 'comm', 'level', yr, 'year'], 1, 'GWa')
        scen.add_par('technical_lifetime', ['node', 'tec', yr], 10, 'y')
        tec_specs = ['node', 'tec', yr, yr, 'mode']
        scen.add_par('output', tec_specs + output_specs, 1, '-')
        scen.add_par('var_cost', tec_specs + ['year'], value, 'USD/GWa')


def adding_years(test_mp, scen_ref, years_new):
    scen_new = Scenario(test_mp, model='add_year', scenario='standard',
                        version='new', annotation=' ')
    add_year(scen_ref, scen_new, years_new)
    return scen_new


def assert_function(scen_ref, scen_new, years_new, yr_test):
    # 1. Testing the set "year" for the new years
    horizon_old = sorted([int(x) for x in scen_ref.set('year')])
    horizon_test = sorted(horizon_old + years_new)
    horizon_new = sorted([int(x) for x in scen_new.set('year')])
    assert (horizon_test == horizon_new)

    # 2. Testing parameter "technical_lifetime" (function interpolate_1d)
    yr_next = min([x for x in horizon_old if x > yr_test])
    yr_pre = max([x for x in horizon_old if x < yr_test])
    parname = 'technical_lifetime'
    ref = scen_ref.par(parname, {'technology': 'tec',
                                 'year_vtg': [yr_pre, yr_next]})
    value_ref = ref['value'].mean()
    new = scen_new.par(parname, {'technology': 'tec', 'year_vtg': yr_test})
    value_new = float(new['value'])
    assert value_new == pytest.approx(value_ref, rel=1e-04)

    # 3. Testing parameter "var_cost" (function interpolate_2d)
    ref = scen_ref.par('var_cost', {'technology': 'tec',
                                    'year_act': [yr_pre, yr_next],
                                    'year_vtg': [yr_pre, yr_next]})

    value_ref = ref['value'].mean()

    new = scen_new.par('var_cost', {'technology': 'tec',
                                    'year_act': yr_test,
                                    'year_vtg': yr_test})

    # Asserting if the missing data is generated accurately by interpolation
    value_new = float(new['value'])
    assert value_new == pytest.approx(value_ref, rel=1e-04)


def test_add_year(test_mp):
    scen_ref = Scenario(test_mp, 'model', 'standard', version='new')
    model_setup(scen_ref, {2020: 1, 2030: 2, 2040: 3})
    scen_ref.commit('initialize test model')
    scen_ref.solve(case='original_years')

    # Adding new years
    years_new = [2025, 2035]
    scen_new = adding_years(test_mp, scen_ref, years_new)
    scen_new.solve(case='new_years')

    # Running the tests
    assert_function(scen_ref, scen_new, years_new, yr_test=2025)
