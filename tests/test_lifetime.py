# -*- coding: utf-8 -*-
# Importing required packages
import os
import ixmp as ix
import pandas as pd
from itertools import product
from pandas.testing import assert_frame_equal
from conftest import here
file_path = os.path.join(here, '..', 'toolbox', 'lifetime_changer')
os.chdir(file_path)
from f_lifetimeChanger import change_lifetime

# Building a new scenario and adding two parameters
mp = ix.Platform()
scen = mp.Scenario(
    'model_test',
    'scenario_test',
    version='new',
    scheme='MESSAGE')

scen.add_set('technology', 'tech_test')
scen.add_set('node', 'node_test')
scen.add_set('commodity', 'com_test')
scen.add_set('mode', 'M_test')
scen.add_set('level', 'level_test')
horizon = list(range(1990, 2081, 10))
lifetime = 30
scen.add_set('year', horizon)
scen.add_set('cat_year', pd.DataFrame(
    {'type_year': 'firstmodelyear', 'year': '2020'}, index=[0]))

first_year_vtg = 2010
df = pd.DataFrame({'node_loc': 'node_test', 'technology': 'tech_test', 'year_vtg': [
                  x for x in horizon if x >= first_year_vtg], 'unit': 'y', 'value': lifetime})

scen.add_par('technical_lifetime', df)
years_pair = [
    x for x in product(
        horizon,
        horizon) if x[1] >= x[0] and x[1] -
    x[0] < lifetime]
df = pd.DataFrame({'node_loc': 'node_test',
                   'node_dest': 'node_test',
                   'technology': 'tech_test',
                   'time': 'year',
                   'time_dest': 'year',
                   'commodity': 'com_test',
                   'level': 'level_test',
                   'mode': 'M_test',
                   'unit': '-',
                   'year_vtg': [x[0] for x in years_pair if x[0] >= first_year_vtg],
                   'year_act': [x[1] for x in years_pair if x[0] >= first_year_vtg],
                   'value': 1})
scen.add_par('output', df)
scen.commit('test built')

# Testing the function change_lifetime
# 1) Testing the case of lifetime extension
lifetime_new = 40
year_start = 1990

dfs = change_lifetime(
    scen,
    'tech_test',
    lifetime_new,
    year_start,
    year_end=None,
    nodes=all,
    par_exclude=None,
    remove_old=False,
    test_run=False,
    extrapol_neg=0.5)

# Testing parameter "technical_lifetime"
df_test = pd.DataFrame({'node_loc': 'node_test',
                        'technology': 'tech_test',
                        'year_vtg': [x for x in horizon if x >= year_start],
                        'unit': 'y',
                        'value': lifetime_new})
assert_frame_equal(df_test, dfs['technical_lifetime'], check_dtype=False)

# Testing parameter "output"
years_pair_test = [
    x for x in product(
        horizon,
        horizon) if x[1] >= x[0] and x[1] -
    x[0] < lifetime_new]
df_test = pd.DataFrame({'node_loc': 'node_test',
                        'node_dest': 'node_test',
                        'technology': 'tech_test',
                        'time': 'year',
                        'time_dest': 'year',
                        'commodity': 'com_test',
                        'level': 'level_test',
                        'mode': 'M_test',
                        'unit': '-',
                        'year_vtg': [x[0] for x in years_pair_test if x[0] >= year_start],
                        'year_act': [x[1] for x in years_pair_test if x[0] >= year_start],
                        'value': 1}).sort_values(['year_vtg',
                                                  'year_act']).reset_index(drop=True)

df_new = scen.par('output').sort_values(
    ['year_vtg', 'year_act']).reset_index(drop=True)
assert_frame_equal(df_test, df_new, check_like=True, check_dtype=False)

# 2) Testing the case of lifetime contraction

lifetime_new = 25
year_start = 2020
year_end = 2070

dfs = change_lifetime(
    scen,
    'tech_test',
    lifetime_new,
    year_start,
    year_end,
    nodes=all,
    par_exclude=None,
    remove_old=True,
    test_run=False,
    extrapol_neg=0.5)

# Testing parameter "technical_lifetime"
df_test = pd.DataFrame({'node_loc': 'node_test', 'technology': 'tech_test',
                        'year_vtg': [x for x in horizon if x >= year_start and x <= year_end],
                        'unit': 'y', 'value': lifetime_new})
assert_frame_equal(df_test, dfs['technical_lifetime'], check_dtype=False)

# Testing parameter "output"
period_test = [x for x in horizon if x >= year_start and x <= year_end]
years_pair_test = [
    x for x in product(
        period_test,
        period_test) if x[1] >= x[0] and x[1] -
    x[0] < lifetime_new]
df_test = pd.DataFrame({'node_loc': 'node_test',
                        'node_dest': 'node_test',
                        'technology': 'tech_test',
                        'time': 'year',
                        'time_dest': 'year',
                        'commodity': 'com_test',
                        'level': 'level_test',
                        'mode': 'M_test',
                        'unit': '-',
                        'year_vtg': [x[0] for x in years_pair_test],
                        'year_act': [x[1] for x in years_pair_test],
                        'value': 1}).sort_values(['year_vtg',
                                                  'year_act']).reset_index(drop=True)

df_new = scen.par('output').sort_values(
    ['year_vtg', 'year_act']).reset_index(drop=True)
assert_frame_equal(df_test, df_new, check_like=True, check_dtype=False)
