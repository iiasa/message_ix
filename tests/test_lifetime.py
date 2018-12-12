# -*- coding: utf-8 -*-
# Importing required packages

import os
import ixmp as ix
from message_ix import Scenario
import pandas as pd
from itertools import product
from pandas.testing import assert_frame_equal
from conftest import here

db_dir = os.path.join(here, 'testdb')
test_db = os.path.join(db_dir, 'ixmptest')
test_mp = ix.Platform(dbprops=test_db, dbtype='HSQLDB')

file_path = os.path.join(here, '..', 'toolbox', 'lifetime_changer')
os.chdir(file_path)
from f_lifetimeChanger import change_lifetime


def test_lifetime_changer(test_mp):
    msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')
    scen = Scenario(test_mp, *msg_multiyear_args)
    assert scen.par('technical_lifetime')[
        'technology'].isin(['canning_plant']).any()
    scen.solve()

    df_tec = scen.par(
        'technical_lifetime', {
            'node_loc': 'seattle', 'technology': 'canning_plant'})
    df_par = scen.par(
        'output', {
            'node_loc': 'seattle', 'technology': 'canning_plant'})

    # Building a new scenario and adding two parameters
    clone = scen.clone('foo', 'bar', keep_sol=False)
    clone.check_out()
    # Changing the lifetime based on avaiable input and output
    df_tec.loc[df_tec['technology'] == 'canning_plant', 'value'] = 10
    clone.add_par('technical_lifetime', df_tec)
    clone.commit('')
    # Testing the function change_lifetime
    lifetime_new = 20
    year_vtg_start = 2020
    year_vtg_end = 2030

    dfs = change_lifetime(
        test_mp,
        clone,
        'canning_plant',
        lifetime_new,
        year_vtg_start,
        year_vtg_end,
        year_act_end=None,
        nodes='seattle',
        par_exclude=None,
        remove_old=False,
        test_run=False,
        extrapol_neg=0.5)

    # Testing parameter "technical_lifetime"
    df_test = df_tec.copy()
    horizon = [int(x) for x in clone.set('year')]
    df_test.loc[df_test['technology'] ==
                'canning_plant', 'value'] = lifetime_new
    if year_vtg_end > max(df_tec['year_vtg']):
        df_row = df_test.loc[0, :].copy()
        for yr in [x for x in horizon if x > max(
                df_tec['year_vtg']) and x <= year_vtg_end]:
            df_row['year_vtg'] = yr
            df_test = df_test.append(df_row, ignore_index=True)

    assert_frame_equal(df_test, dfs['technical_lifetime'], check_dtype=False)

    # Testing parameter "output"
    df_test2 = pd.DataFrame(columns=df_par.columns)
    df_test2 = df_par.copy()
    years_pair_test = [
        x for x in product(
            horizon,
            horizon) if x[1] >= x[0] and x[1] -
        x[0] < lifetime_new and x[0] >= min(
            df_test['year_vtg']) and x[0] <= max(
                df_test['year_vtg'])]

    df_row = df_par.loc[0, :].copy()
    for x in years_pair_test:
        df_row['year_vtg'] = x[0]
        df_row['year_act'] = x[1]
        df_test2 = df_test2.append(df_row, ignore_index=True)

    df_new = clone.par('output', {'node_loc': 'seattle',
                                  'technology': 'canning_plant'}) \
                  .sort_values(['year_vtg', 'year_act']) \
                  .reset_index(drop=True)

    assert_frame_equal(df_test2, df_new, check_like=True, check_dtype=False)
    clone.solve()
