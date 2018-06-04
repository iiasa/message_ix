import pytest

import ixmp
import message_ix

import pandas as pd
import pandas.util.testing as pdt

from numpy import testing as npt

import message_ix.utils as utils
from testing_utils import test_mp


msg_args = ('canning problem (MESSAGE scheme)', 'standard')


def test_add_spatial_single(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    data = {'country': 'Austria'}
    utils.add_spatial_sets(scen, data)

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
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    data = {'country': ['Austria', 'Germany']}
    utils.add_spatial_sets(scen, data)

    exp = ['World', 'Austria', 'Germany']
    obs = scen.set('node')
    npt.assert_array_equal(obs, exp)

    exp = ['World', 'global', 'country']
    obs = scen.set('lvl_spatial')
    npt.assert_array_equal(obs, exp)

    exp = [['country', 'Austria', 'World'], ['country', 'Germany', 'World']]
    obs = scen.set('map_spatial_hierarchy')
    npt.assert_array_equal(obs, exp)


def test_add_spatial_heirarchy(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    data = {'country': {'Austria': {'state': ['Vienna', 'Lower Austria']}}}
    utils.add_spatial_sets(scen, data)

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


def test_add_spatial(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    data = {'country': 'Austria'}
    utils.add_spatial_sets(scen, data)


def test_add_temporal_raises(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    pytest.raises(ValueError, utils.add_temporal_sets,
                  scen, data={'foo': 'bar'})


def test_add_temporal(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    exp = ['2010', '2020']
    utils.add_temporal_sets(scen, {'year': exp})
    obs = scen.set('year')
    npt.assert_array_equal(obs, exp)

    obs = scen.set('cat_year')
    exp = pd.DataFrame(
        {'type_year': 'firstmodelyear', 'year': int(exp[0])}, index=[0])
    pdt.assert_frame_equal(obs, exp)


def test_vintage_and_active_years(test_mp):
    scen = test_mp.Scenario(*msg_args, version='new', scheme='MESSAGE')
    utils.add_temporal_sets(scen, {'year': ['2010', '2020']})
    exp = (('2010', '2010', '2020'), ('2010', '2020', '2020'))
    obs = utils.vintage_and_active_years(scen)
    assert obs == exp


def test_make_df():
    base = {'foo': 'bar'}
    exp = pd.DataFrame({'foo': 'bar', 'baz': [42, 42]})
    obs = utils.make_df(base, baz=[42, 42])
    pdt.assert_frame_equal(obs, exp)


def test_make_df_raises():
    pytest.raises(ValueError, utils.make_df, 42, baz=[42, 42])
