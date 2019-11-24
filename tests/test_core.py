import os

import ixmp
import numpy as np
from numpy import testing as npt
import pandas as pd
import pandas.util.testing as pdt

from message_ix import Scenario
from message_ix.testing import make_dantzig


msg_args = ('canning problem (MESSAGE scheme)', 'standard')
msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')


def test_year_int(test_mp):
    scen = make_dantzig(test_mp, solve=True, multi_year=True)

    # Dimensions indexed by 'year' are returned as integers for all item types
    assert scen.set('cat_year').dtypes['year'] == 'int'
    assert scen.par('demand').dtypes['year'] == 'int'
    assert scen.par('bound_activity_up').dtypes['year_act'] == 'int'
    assert scen.var('ACT').dtypes['year_vtg'] == 'int'
    assert scen.equ('COMMODITY_BALANCE_GT').dtypes['year'] == 'int'


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
    scen.add_horizon({'year': ['2000', '2010', '2020'],
                      'firstmodelyear': '2010'})
    obs = scen.vintage_and_active_years()
    exp = pd.DataFrame({'year_vtg': (2000, 2000, 2010, 2010, 2020),
                        'year_act': (2010, 2020, 2010, 2020, 2020)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order


def test_vintage_and_active_years_with_lifetime(test_mp):
    scen = Scenario(test_mp, *msg_args, version='new')
    years = ['2000', '2010', '2020']
    scen.add_horizon({'year': years,
                      'firstmodelyear': '2010'})
    scen.add_set('node', 'foo')
    scen.add_set('technology', 'bar')
    scen.add_par('duration_period', pd.DataFrame({
        'unit': '???',
        'value': 10,
        'year': years
    }))
    scen.add_par('technical_lifetime', pd.DataFrame({
        'node_loc': 'foo',
        'technology': 'bar',
        'unit': '???',
        'value': 20,
        'year_vtg': years,
    }))

    # part is before horizon
    obs = scen.vintage_and_active_years(ya_args=('foo', 'bar', '2000'))
    exp = pd.DataFrame({'year_vtg': (2000,),
                        'year_act': (2010,)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    obs = scen.vintage_and_active_years(ya_args=('foo', 'bar', '2000'),
                                        in_horizon=False)
    exp = pd.DataFrame({'year_vtg': (2000, 2000),
                        'year_act': (2000, 2010)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # fully in horizon
    obs = scen.vintage_and_active_years(ya_args=('foo', 'bar', '2010'))
    exp = pd.DataFrame({'year_vtg': (2010, 2010),
                        'year_act': (2010, 2020)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # part after horizon
    obs = scen.vintage_and_active_years(ya_args=('foo', 'bar', '2020'))
    exp = pd.DataFrame({'year_vtg': (2020,),
                        'year_act': (2020,)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order


def test_cat_all(test_mp):
    scen = Scenario(test_mp, *msg_args)
    df = scen.cat('technology', 'all')
    npt.assert_array_equal(df, ['canning_plant', 'transport_from_seattle',
                                'transport_from_san-diego'])


def test_add_cat(test_mp):
    scen = Scenario(test_mp, *msg_args)
    scen2 = scen.clone(keep_solution=False)
    scen2.check_out()
    scen2.add_cat('technology', 'trade',
                  ['transport_from_san-diego', 'transport_from_seattle'])
    df = scen2.cat('technology', 'trade')
    npt.assert_array_equal(
        df, ['transport_from_san-diego', 'transport_from_seattle'])
    scen2.discard_changes()


def test_add_cat_unique(test_mp):
    scen = Scenario(test_mp, *msg_multiyear_args)
    scen2 = scen.clone(keep_solution=False)
    scen2.check_out()
    scen2.add_cat('year', 'firstmodelyear', 2020, True)
    df = scen2.cat('year', 'firstmodelyear')
    npt.assert_array_equal(
        df, ['2020'])
    scen2.discard_changes()


def test_years_active(test_mp):
    scen = Scenario(test_mp, *msg_multiyear_args)
    years = scen.years_active('seattle', 'canning_plant', '2020')
    assert isinstance(years, list)
    assert isinstance(years[0], int)
    npt.assert_array_equal(years, [2020, 2030])


def test_years_active_extend(test_mp):
    scen = Scenario(test_mp, *msg_multiyear_args)
    scen = scen.clone(keep_solution=False)
    scen.check_out()
    scen.add_set('year', ['2040', '2050'])
    scen.add_par('duration_period', '2040', 10, 'y')
    scen.add_par('duration_period', '2050', 10, 'y')
    years = scen.years_active('seattle', 'canning_plant', '2020')
    npt.assert_array_equal(years, [2020, 2030, 2040])
    scen.discard_changes()


def test_new_timeseries_long_name64(test_mp):
    scen = Scenario(test_mp, *msg_multiyear_args)
    scen = scen.clone(keep_solution=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame({
        'region': ['India', ],
        'variable': [('Emissions|CO2|Energy|Demand|Transportation|Aviation|'
                      'Domestic|Fre'), ],
        'unit': ['Mt CO2/yr', ],
        '2012': [0.257009, ]
    })
    scen.add_timeseries(df)
    scen.commit('importing a testing timeseries')


def test_new_timeseries_long_name64plus(test_mp):
    scen = Scenario(test_mp, *msg_multiyear_args)
    scen = scen.clone(keep_solution=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame({
        'region': ['India', ],
        'variable': [('Emissions|CO2|Energy|Demand|Transportation|Aviation|'
                      'Domestic|Freight|Oil'), ],
        'unit': ['Mt CO2/yr', ],
        '2012': [0.257009, ]
    })
    scen.add_timeseries(df)
    scen.commit('importing a testing timeseries')


def test_rename_technology(test_mp):
    scen = Scenario(test_mp, *msg_args)
    assert scen.par('output')['technology'].isin(['canning_plant']).any()

    clone = scen.clone('foo', 'bar')
    clone.rename('technology', {'canning_plant': 'foo_bar'})
    assert not clone.par('output')['technology'].isin(['canning_plant']).any()
    assert clone.par('output')['technology'].isin(['foo_bar']).any()
    clone.solve()
    assert np.isclose(clone.var('OBJ')['lvl'], 153.675)


def test_rename_technology_no_rm(test_mp):
    scen = Scenario(test_mp, *msg_args)
    assert scen.par('output')['technology'].isin(['canning_plant']).any()

    clone = scen.clone('foo', 'bar')
    # also test if already checked out
    clone.check_out()

    clone.rename('technology', {'canning_plant': 'foo_bar'}, keep=True)
    assert clone.par('output')['technology'].isin(['canning_plant']).any()
    assert clone.par('output')['technology'].isin(['foo_bar']).any()


def test_excel_read_write(test_mp):
    fname = 'test_excel_read_write.xlsx'

    scen1 = Scenario(test_mp, *msg_args)
    scen1.to_excel(fname)

    scen2 = Scenario(test_mp, model='foo', scenario='bar', version='new')
    scen2.read_excel(fname)

    exp = scen1.par('input')
    obs = scen2.par('input')
    pdt.assert_frame_equal(exp, obs)

    scen2.commit('foo')  # must be checked in
    scen2.solve()
    assert np.isclose(scen2.var('OBJ')['lvl'], 153.675)

    os.remove(fname)


def test_clone(tmpdir):
    # Two local platforms
    mp1 = ixmp.Platform(driver='hsqldb', path=tmpdir / 'mp1')
    mp2 = ixmp.Platform(driver='hsqldb', path=tmpdir / 'mp2')

    # A minimal scenario
    scen1 = Scenario(mp1, model='model', scenario='scenario', version='new')
    scen1.add_spatial_sets({'country': 'Austria'})
    scen1.add_set('technology', 'bar')
    scen1.add_horizon({'year': [2010, 2020]})
    scen1.commit('add minimal sets for testing')

    assert len(mp1.scenario_list(default=False)) == 1

    # Clone
    scen2 = scen1.clone(platform=mp2)

    # Return type of ixmp.Scenario.clone is message_ix.Scenario
    assert isinstance(scen2, Scenario)

    # Close and re-open both databases
    mp1.close_db()  # TODO this should be done automatically on del
    mp2.close_db()  # TODO this should be done automatically on del
    del mp1, mp2
    mp1 = ixmp.Platform(driver='hsqldb', path=tmpdir / 'mp1')
    mp2 = ixmp.Platform(driver='hsqldb', path=tmpdir / 'mp2')

    # Same scenarios present in each database
    assert all(mp1.scenario_list(default=False) ==
               mp2.scenario_list(default=False))

    # Load both scenarios
    scen1 = Scenario(mp1, 'model', 'scenario')
    scen2 = Scenario(mp2, 'model', 'scenario')

    # Contents are identical
    assert all(scen1.set('node') == scen2.set('node'))
    assert all(scen1.set('year') == scen2.set('year'))
