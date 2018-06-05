import ixmp
import message_ix
import pytest

import pandas as pd
import pandas.util.testing as pdt

from message_ix import Scenario
from numpy import testing as npt
from testing_utils import test_mp


msg_args = ('canning problem (MESSAGE scheme)', 'standard')


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
