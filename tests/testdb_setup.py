import os
import pandas as pd
import ixmp as ix

import message_ix

from conftest import here

db_dir = os.path.join(here, 'testdb')
test_db = os.path.join(db_dir, 'ixmptest')

# remove existing database files

for fname in [
        os.path.join(db_dir, 'ixmptest.lobs'),
        os.path.join(db_dir, 'ixmptest.properties'),
        os.path.join(db_dir, 'ixmptest.script')
]:
    if os.path.isfile(fname):
        os.remove(fname)

# launch the modeling platform instance, creating a new test database file
mp = ix.Platform(dbprops=test_db, dbtype='HSQLDB')
model = "canning problem (MESSAGE scheme)"
scenario = "standard"
annot = "Dantzig's canning problem as a MESSAGE-scheme ixmp.Scenario"
scen = message_ix.Scenario(mp, model, scenario, version='new',
                           annotation=annot)
input_file = os.path.join(db_dir, 'input.xlsx')
scen.read_excel(input_file)
comment = "importing a MESSAGE-scheme version of the transport problem"
scen.commit(comment)
scen.set_as_default()

# duplicate the MESSAGE-scheme transport scenario for additional unit tests
scen = message_ix.Scenario(mp, model, scenario)
scen = scen.clone(scen='multi-year',
                  annotation='adding additional years for unit-testing')
scen.check_out()
scen.add_set('year', [2020, 2030])
scen.add_par('technical_lifetime', ['seattle', 'canning_plant', '2020'],
             30, 'y')
scen.commit('adding years and technical lifetime to one technology')


# close the test database, remove the test database properties file
mp.close_db()
