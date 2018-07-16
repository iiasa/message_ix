import os
import pandas as pd
from numpy import testing as npt
import pandas.util.testing as pdt
import ixmp
import pytest
import numpy as np

from message_ix import views

msg_args = ('canning problem (MESSAGE scheme)', 'standard')
here = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope="session")
def view_df():
    df = pd.read_csv(os.path.join(here, 'tec_view_data.csv'), dtype={
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
    obs = views.tec_view(scen, column_style='model_mapping')
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs, check_index_type=False)


def test_tec_view_canning_all_tecs_sort_by_par(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    idx = ['par', 'node', 'technology', 'unit', 'commodity/emission',
           'level', 'mode', 'node I/O', 'year_vtg/year_rel']
    exp = view_df.sort_values(idx).set_index(idx).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, sort_by='par', column_style='model_mapping')
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs, check_index_type=False)


def test_tec_view_canning_single_tec(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    tec = 'transport_from_san-diego'
    exp = view_df[view_df['technology'] == tec].set_index(
        ['technology', 'node', 'par', 'unit', 'commodity/emission', 'level', 'mode', 'node I/O', 'year_vtg/year_rel'])
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, tec=tec, column_style='model_mapping')
    obs.sort_index(inplace=True)
    #assert 0
    pdt.assert_frame_equal(exp, obs, check_index_type=False)


def test_tec_view_canning_single_par(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    par = 'input'
    exp = view_df[view_df['par'] == par].set_index(['technology', 'node', 'par', 'unit', 'commodity/emission',
                                                    'level', 'mode', 'node I/O', 'year_vtg/year_rel']).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, par=par, column_style='model_mapping')
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs, check_index_type=False)


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
    exp = exp.set_index(['Technology', 'Region', 'Parameter', 'Unit',
                         'Commodity/Species', 'Level', 'Mode', 'Region I/O',
                         'Vintage/Year Relation']).astype('float32')
    exp.sort_index(inplace=True)
    obs = views.tec_view(scen, column_style='file_mapping')
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs, check_index_type=False)


def test_tec_view_canning_raw_idx(test_mp, view_df):
    scen = test_mp.Scenario(*msg_args)
    exp = view_df
    exp1 = exp[~exp['par'].isin(['input', 'output'])].drop('node I/O', axis=1)

    exp2 = exp[exp['par'] == 'output'].rename(
        columns={'node I/O': 'node_dest'})
    exp2['time_dest'] = 'year'

    exp3 = exp[exp['par'] == 'input'].rename(
        columns={'node I/O': 'node_origin'})
    exp3['time_origin'] = 'year'

    exp = pd.concat([exp1, exp2, exp3])
    exp = exp.rename(columns={'commodity/emission': 'commodity',
                              'year_vtg/year_rel': 'year_vtg',
                              'node': 'node_loc'}).fillna(' ')
    exp['time'] = 'year'
    idx = ['technology', 'node_loc', 'par', 'unit', 'commodity',
           'level', 'mode', 'node_dest', 'node_origin', 'time',
           'time_dest', 'time_origin', 'year_vtg']
    exp = exp.sort_values(by=idx).set_index(idx).astype('float32')
    obs = views.tec_view(scen)
    obs.sort_index(inplace=True)
    pdt.assert_frame_equal(exp, obs, check_index_type=False)
