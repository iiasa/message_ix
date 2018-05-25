import os
import pandas as pd
from numpy import testing as npt
import pandas.util.testing as pdt
import ixmp
import pytest
import numpy as np

from testing_utils import test_mp
from message_ix import views, default_paths

msg_args = ('canning problem (MESSAGE scheme)', 'standard')


@pytest.fixture(scope="session")
def view_df():
    df = pd.read_csv("{}\\tec_view_data.csv".format(default_paths.MSG_TEST_DIR), dtype={
                     '2010': np.float32}).fillna('')
    df = df.rename(columns={'2010': int('2010')})
    df.loc[:, 'year_vtg/year_rel'] = df.loc[:,
                                            'year_vtg/year_rel'].apply(lambda x: int(x) if x != '' else x)
    yield df


def test_tec_view_canning_all_tecs(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    exp = view_df.set_index(['technology', 'node', 'par', 'unit', 'commodity/emission',
                             'level', 'mode', 'node I/O', 'year_vtg/year_rel']).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen)
    obs.sort_index(inplace=True)
    # , check_index_type=False)#, check_column_type=False)
    pdt.assert_frame_equal(exp, obs)


def test_tec_view_canning_all_tecs_sort_by_par(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    idx = ['par', 'node', 'technology', 'unit', 'commodity/emission',
           'level', 'mode', 'node I/O', 'year_vtg/year_rel']
    exp = view_df.sort_values(idx).set_index(idx).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, sort_by='par')
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs)


def test_tec_view_canning_single_tec(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    tec = 'transport_from_san-diego'
    exp = view_df[view_df['technology'] == tec].set_index(
        ['technology', 'node', 'par', 'unit', 'commodity/emission', 'level', 'mode', 'node I/O', 'year_vtg/year_rel'])  # .astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, tec=tec)
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs)


def test_tec_view_canning_single_par(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    par = 'input'
    exp = view_df[view_df['par'] == par].set_index(['technology', 'node', 'par', 'unit', 'commodity/emission',
                                                    'level', 'mode', 'node I/O', 'year_vtg/year_rel']).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, par=par)
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs)


def test_tec_view_canning_xlsx_idx(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    exp = view_df.rename(columns={
        'technology': 'Technology',
        'node': 'Region',
        'par': 'Parameter',
        'unit': 'Unit',
        'commodity/emission': 'Commodity/Species',
        'level': 'Level',
        'mode': 'Mode',
        'node I/O': 'Region I/O',
        'year_vtg/year_rel': 'Vintage/Year Relation',
    })
    exp = exp.set_index(['Technology', 'Region', 'Parameter', 'Unit', 'Commodity/Species',
                         'Level', 'Mode', 'Region I/O', 'Vintage/Year Relation']).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, xlsx_mapping=True)
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs)
