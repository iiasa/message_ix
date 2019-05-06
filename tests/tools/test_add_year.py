# -*- coding: utf-8 -*-
# Importing required packages
import os
import math
import ixmp as ix
import message_ix
from conftest import here

from message_ix.tools.add_year import add_year

db_dir = os.path.join(here, 'testdb')
test_db = os.path.join(db_dir, 'ixmptest')
test_mp = ix.Platform(dbprops=test_db, dbtype='HSQLDB')


def test_addNewYear(test_mp):
    msg_multiyear_args = ('canning problem (MESSAGE scheme)', 'multi-year')
    sc_ref = message_ix.Scenario(test_mp, *msg_multiyear_args)
    assert sc_ref.par('technical_lifetime')['technology'
                                            ].isin(['canning_plant']).any()
    sc_ref.solve()

    # Building a new scenario and adding new years
    sc_new = message_ix.Scenario(test_mp, model='foo', scenario='bar',
                                 version='new', annonation=' ')

    # Using the function addNewYear
    years_new = [2015, 2025]

    add_year(sc_ref, sc_new, years_new)

    # 1. Testing the set "year" for the new years
    horizon_old = sorted([int(x) for x in sc_ref.set('year')])
    horizon_test = sorted(horizon_old + years_new)
    horizon_new = sorted([int(x) for x in sc_new.set('year')])

    # Asserting if the lists are equal
    assert (horizon_test == horizon_new)

    # 2. Testing parameter "technical_lifetime"
    df_tec = sc_ref.par('technical_lifetime', {'node_loc': 'seattle',
                                               'technology': 'canning_plant',
                                               'year_vtg': [2020, 2030]})
    value_ref = df_tec['value'].mean()
    df_tec_new = sc_new.par('technical_lifetime',
                            {'node_loc': 'seattle',
                             'technology': 'canning_plant',
                             'year_vtg': 2025}
                            )

    value_new = float(df_tec_new['value'])

    # Asserting if the missing data is generated accurately by interpolation
    # of adjacent data points
    assert math.isclose(value_ref, value_new, rel_tol=1e-04)

    # 3. Testing parameter "output"
    df_tec = sc_ref.par('output', {'node_loc': 'seattle',
                                   'technology': 'canning_plant',
                                   'year_act': 2030,
                                   'year_vtg': [2020, 2030]})

    value_ref = df_tec['value'].mean()

    df_tec_new = sc_new.par('output', {'node_loc': 'seattle',
                                       'technology': 'canning_plant',
                                       'year_act': 2025,
                                       'year_vtg': 2025})

    # Asserting if the missing data is generated or not
    assert df_tec_new['value'].tolist()

    # Asserting if the missing data is generated accurately by interpolation
    value_new = float(df_tec_new['value'])
    assert math.isclose(value_ref, value_new, rel_tol=1e-04)
