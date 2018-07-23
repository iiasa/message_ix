import os
import pandas as pd
import ixmp as ix

import message_ix

from conftest import here

db_dir = os.path.join(here, 'testdb')
test_db = os.path.join(db_dir, 'ixmptest')

# %% remove existing database files

for fname in [
        os.path.join(db_dir, 'ixmptest.lobs'),
        os.path.join(db_dir, 'ixmptest.properties'),
        os.path.join(db_dir, 'ixmptest.script')
]:
    if os.path.isfile(fname):
        os.remove(fname)

# %% launch the modeling platform instance, creating a new test database file

mp = ix.Platform(dbprops=test_db, dbtype='HSQLDB')

model = "canning problem (MESSAGE scheme)"
scenario = "standard"
annot = "Dantzig's canning problem as a MESSAGE-scheme ixmp.Scenario"

scen = message_ix.Scenario(
    mp, model, scenario, version='new', annotation=annot)

# year set and (sub-annual) time set
year = [2010]
scen.add_set("year", year)
scen.add_set("cat_year", ["firstmodelyear", 2010])

city = ["seattle", "san-diego", "new-york", "chicago", "topeka"]
scen.add_set("node", city)
scen.add_set("lvl_spatial", "location")

for item in city:
    scen.add_set("map_spatial_hierarchy", ["location", item, "World"])

scen.add_set("commodity", "cases")
scen.add_set("level", ["supply", "consumption"])

scen.add_set("technology", "canning_plant")

scen.add_set(
    "technology", ["transport_from_seattle", "transport_from_san-diego"])

scen.add_set(
    "mode", ["production", "to_new-york", "to_chicago", "to_topeka"])

scen.add_par("demand", ['new-york', 'cases', 'consumption', '2010', 'year'],
             325.0, "cases")
scen.add_par("demand", ['chicago', 'cases', 'consumption', '2010', 'year'],
             300.0, "cases")
scen.add_par("demand", ['topeka', 'cases', 'consumption', '2010', 'year'],
             275.0, "cases")
bda_data = [
    {'node_loc': "seattle", 'value': 350.0},
    {'node_loc': "san-diego", 'value': 600}
]
bda = pd.DataFrame(bda_data)

bda['technology'] = 'canning_plant'
bda['year_act'] = '2010'
bda['mode'] = 'production'
bda['time'] = 'year'
bda['unit'] = 'cases'

scen.add_par("bound_activity_up", bda)

outp_data = [
    {'node_loc': "seattle"},
    {'node_loc': "san-diego"}
]
outp = pd.DataFrame(outp_data)

outp['technology'] = 'canning_plant'
outp['year_vtg'] = '2010'
outp['year_act'] = '2010'
outp['mode'] = 'production'
outp['node_dest'] = outp['node_loc']
outp['commodity'] = 'cases'
outp['level'] = 'supply'
outp['time'] = 'year'
outp['time_dest'] = 'year'
outp['value'] = 1
outp['unit'] = '%'

scen.add_par("output", outp)

inp_data = [
    {'mode': "to_new-york"},
    {'mode': "to_chicago"},
    {'mode': "to_topeka"},
]
inp = pd.DataFrame(inp_data)

inp['node_loc'] = 'seattle'
inp['technology'] = 'transport_from_seattle'
inp['year_vtg'] = '2010'
inp['year_act'] = '2010'
inp['node_origin'] = 'seattle'
inp['commodity'] = 'cases'
inp['level'] = 'supply'
inp['time'] = 'year'
inp['time_origin'] = 'year'
inp['value'] = 1
inp['unit'] = '%'

scen.add_par("input", inp)

inp['node_loc'] = 'san-diego'
inp['technology'] = 'transport_from_san-diego'
inp['node_origin'] = 'san-diego'

scen.add_par("input", inp)

outp_data = [
    {'mode': "to_new-york", 'node_dest': "new-york"},
    {'mode': "to_chicago", 'node_dest': "chicago"},
    {'mode': "to_topeka", 'node_dest': "topeka"},
]
outp = pd.DataFrame(outp_data)

outp['node_loc'] = 'seattle'
outp['technology'] = 'transport_from_seattle'
outp['year_vtg'] = '2010'
outp['year_act'] = '2010'
outp['commodity'] = 'cases'
outp['level'] = 'consumption'
outp['time'] = 'year'
outp['time_dest'] = 'year'
outp['value'] = 1
outp['unit'] = '%'

scen.add_par("output", outp)

outp['node_loc'] = 'san-diego'
outp['technology'] = 'transport_from_san-diego'

scen.add_par("output", outp)

var_cost_data = [
    {'node_loc': "seattle", 'technology': "transport_from_seattle",
     'mode': "to_new-york", 'value': 0.225},
    {'node_loc': "seattle", 'technology': "transport_from_seattle",
     'mode': "to_chicago", 'value': 0.153},
    {'node_loc': "seattle", 'technology': "transport_from_seattle",
     'mode': "to_topeka", 'value': 0.162},
    {'node_loc': "san-diego", 'technology': "transport_from_san-diego",
     'mode': "to_new-york", 'value': 0.225},
    {'node_loc': "san-diego", 'technology': "transport_from_san-diego",
     'mode': "to_chicago", 'value': 0.162},
    {'node_loc': "san-diego", 'technology': "transport_from_san-diego",
     'mode': "to_topeka", 'value': 0.126},
]
var_cost = pd.DataFrame(var_cost_data)

var_cost['year_vtg'] = '2010'
var_cost['year_act'] = '2010'
var_cost['time'] = 'year'
var_cost['unit'] = 'USD'

scen.add_par("var_cost", var_cost)

scen.add_par("ref_activity",
             "seattle.canning_plant.2010.production.year", 350, "cases")
scen.add_par("ref_activity",
             "san-diego.canning_plant.2010.production.year", 600, "cases")

comment = "importing a MESSAGE-scheme version of the transport problem"
scen.commit(comment)
scen.set_as_default()


# %%  duplicate the MESSAGE-scheme transport scenario for additional unit tests

scen = mp.Scenario(model, scenario)
scen = scen.clone(scen='multi-year',
                  annotation='adding additional years for unit-testing')

scen.check_out()
scen.add_set('year', [2020, 2030])
scen.add_par('technical_lifetime', ['seattle', 'canning_plant', '2020'],
             30, 'y')
scen.commit('adding years and technical lifetime to one technology')


# %% close the test database, remove the test database properties file

mp.close_db()
