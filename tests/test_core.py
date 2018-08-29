import os
import ixmp
import message_ix
import pytest

import pandas as pd
import pandas.util.testing as pdt

from message_ix import Scenario
from numpy import testing as npt

msg_args = ('canning problem (MESSAGE scheme)', 'standard')
msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')


def test_add_spatial_single(test_mp):
    scen = Scenario(test_mp, *msg_args, version='new')
    data = {'country': 'Austria'}
    scen.add_spatial_sets(data)

    exp = ['World', 'Austria']
    obs = scen.set('node')
    npt.assert_array_equal(obs, exp)

    exp = ['World', 'global', 'country']
    obs = scen.set('lvl_spatial')
    npt.assert_array_equal(obs, exp)

    exp = [['country', 'Austria', 'World']]
    obs = scen.set('map_spatial_hierarchy')
    npt.assert_array_equal(obs, exp)


def test_add_spatial_multiple(test_mp):
    scen = Scenario(test_mp, *msg_args, version='new')
    data = {'country': ['Austria', 'Germany']}
    scen.add_spatial_sets(data)

    exp = ['World', 'Austria', 'Germany']
    obs = scen.set('node')
    npt.assert_array_equal(obs, exp)

    exp = ['World', 'global', 'country']
    obs = scen.set('lvl_spatial')
    npt.assert_array_equal(obs, exp)

    exp = [['country', 'Austria', 'World'], ['country', 'Germany', 'World']]
    obs = scen.set('map_spatial_hierarchy')
    npt.assert_array_equal(obs, exp)


def test_add_spatial_hierarchy(test_mp):
    scen = Scenario(test_mp, *msg_args, version='new')
    data = {'country': {'Austria': {'state': ['Vienna', 'Lower Austria']}}}
    scen.add_spatial_sets(data)

    exp = ['World', 'Vienna', 'Lower Austria', 'Austria']
    obs = scen.set('node')
    npt.assert_array_equal(obs, exp)

    exp = ['World', 'global', 'state', 'country']
    obs = scen.set('lvl_spatial')
    npt.assert_array_equal(obs, exp)

    exp = [
        ['state', 'Vienna', 'Austria'],
        ['state', 'Lower Austria', 'Austria'],
        ['country', 'Austria', 'World'],
    ]
    obs = scen.set('map_spatial_hierarchy')
    npt.assert_array_equal(obs, exp)


def test_vintage_and_active_years(test_mp):
    scen = Scenario(test_mp, *msg_args, version='new')
    scen.add_horizon({'year': ['2010', '2020']})
    exp = (('2010', '2010', '2020'), ('2010', '2020', '2020'))
    obs = scen.vintage_and_active_years()
    assert obs == exp


def test_cat_all(test_mp):
    scen = test_mp.Scenario(*msg_args)
    df = scen.cat('technology', 'all')
    npt.assert_array_equal(df, ['canning_plant', 'transport_from_seattle',
                                'transport_from_san-diego'])


def test_add_cat(test_mp):
    scen = test_mp.Scenario(*msg_args)
    scen2 = scen.clone(keep_sol=False)
    scen2.check_out()
    scen2.add_cat('technology', 'trade',
                  ['transport_from_san-diego', 'transport_from_seattle'])
    df = scen2.cat('technology', 'trade')
    npt.assert_array_equal(
        df, ['transport_from_san-diego', 'transport_from_seattle'])
    scen2.discard_changes()


def test_add_cat_unique(test_mp):
    scen = test_mp.Scenario(*msg_multiyear_args)
    scen2 = scen.clone(keep_sol=False)
    scen2.check_out()
    scen2.add_cat('year', 'firstmodelyear', 2020, True)
    df = scen2.cat('year', 'firstmodelyear')
    npt.assert_array_equal(
        df, ['2020'])
    scen2.discard_changes()


def test_years_active(test_mp):
    scen = test_mp.Scenario(*msg_multiyear_args)
    df = scen.years_active('seattle', 'canning_plant', '2020')
    npt.assert_array_equal(df, [2020, 2030])


def test_years_active_extend(test_mp):
    scen = test_mp.Scenario(*msg_multiyear_args)
    scen = scen.clone(keep_sol=False)
    scen.check_out()
    scen.add_set('year', ['2040', '2050'])
    scen.add_par('duration_period', '2040', 10, 'y')
    scen.add_par('duration_period', '2050', 10, 'y')
    df = scen.years_active('seattle', 'canning_plant', '2020')
    npt.assert_array_equal(df, [2020, 2030, 2040])
    scen.discard_changes()


def test_new_timeseries_long_name64(test_mp):
    scen = test_mp.Scenario(*msg_multiyear_args)
    scen = scen.clone(keep_sol=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame({
        'region': ['India', ],
        'variable': ['Emissions|CO2|Energy|Demand|Transportation|Aviation|Domestic|Fre', ],
        'unit': ['Mt CO2/yr', ],
        '2012': [0.257009, ]
    })
    scen.add_timeseries(df)
    scen.commit('importing a testing timeseries')


def test_new_timeseries_long_name64plus(test_mp):
    scen = test_mp.Scenario(*msg_multiyear_args)
    scen = scen.clone(keep_sol=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame({
        'region': ['India', ],
        'variable': ['Emissions|CO2|Energy|Demand|Transportation|Aviation|Domestic|Freight|Oil', ],
        'unit': ['Mt CO2/yr', ],
        '2012': [0.257009, ]
    })
    scen.add_timeseries(df)
    scen.commit('importing a testing timeseries')


def test_rename_technology(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()
    assert scen.par('output')['technology'].isin(['canning_plant']).any()
    exp_obj = scen.var('OBJ')['lvl']

    clone = scen.clone('foo', 'bar', keep_sol=False)
    clone.rename('technology', {'canning_plant': 'foo_bar'})
    assert not clone.par('output')['technology'].isin(['canning_plant']).any()
    assert clone.par('output')['technology'].isin(['foo_bar']).any()
    clone.solve()
    obs_obj = clone.var('OBJ')['lvl']
    assert obs_obj == exp_obj


def test_rename_technology_no_rm(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen.solve()
    assert scen.par('output')['technology'].isin(['canning_plant']).any()

    clone = scen.clone('foo', 'bar', keep_sol=False)
    # also test if already checked out
    clone.check_out()

    clone.rename('technology', {'canning_plant': 'foo_bar'}, keep=True)
    assert clone.par('output')['technology'].isin(['canning_plant']).any()
    assert clone.par('output')['technology'].isin(['foo_bar']).any()


def test_excel_read_write(test_mp):
    fname = 'test_excel_read_write.xlsx'

    scen1 = Scenario(test_mp, *msg_args)
    scen1.to_excel(fname)

    scen2 = Scenario(test_mp, model='foo', scen='bar', version='new')
    scen2.read_excel(fname)

    exp = scen1.par('input')
    obs = scen2.par('input')
    pdt.assert_frame_equal(exp, obs)

    scen1.solve()
    scen2.commit('foo')  # must be checked in
    scen2.solve()
    exp = scen1.var('OBJ')['lvl']
    obs = scen2.var('OBJ')['lvl']
    assert exp == obs

    os.remove(fname)
