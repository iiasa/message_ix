import os
import pandas as pd
from numpy import testing as npt
import pandas.util.testing as pdt
import pytest
import numpy as np

from testing_utils import test_mp
from message_ix import views
from message_ix import xlsx_importer

here = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(scope="session")
def init_model(test_mp):
    im = xlsx_importer.init_model(test_mp, os.path.join(
        here, 'xlsx_input.xlsx'), False, False)
    yield im


@pytest.fixture(scope="session")
def read_input(init_model):
    meta, tecs, dems, resources, mpa_data = init_model.read_input()
    yield meta, tecs, dems, resources, mpa_data


@pytest.fixture(scope="session")
def read_test_data():
    df = pd.read_csv('xlsx_test_data.csv').set_index('Unnamed: 0')
    df.index.name = None
    yield df


def test_read_input_meta(read_input):
    exp = pd.DataFrame({'Variable': ['Model Name', 'Scenario Name', 'Annotation', 'Discount rate', 'First model year'],
                        'Units': [np.nan, np.nan, np.nan, '%', 'year'],
                        'Value': ['xlsx_test_model', 'xlsx_test_scenario', 'test', 5, 2010]}).set_index('Variable')
    obs = read_input[0]
    pdt.assert_frame_equal(exp, obs)


def test_read_input_tecs(read_input, read_test_data):
    exp = read_test_data
    obs = read_input[1]
    pdt.assert_frame_equal(exp, obs)


def test_read_input_dems(read_input):
    exp = pd.DataFrame({'Variable': ['electricity'],
                        'Parameter': ['demand'],
                        'Region': ['test_reg'],
                        'Level': ['useful'],
                        'Sector': ['electricity'],
                        'Units': ['GWa'],
                        '2010': [5],
                        '2020': [6],
                        '2030': [7],
                        '2040': [8],
                        'Comment': [np.nan], })
    exp = exp[['Variable', 'Parameter', 'Region', 'Level', 'Sector',
               'Units', '2010', '2020', '2030', '2040', 'Comment']]
    obs = read_input[2]
    pdt.assert_frame_equal(exp, obs)


def test_read_input_resources(read_input):
    exp = pd.DataFrame({'Resource': ['coal', 'coal'],
                        'Parameter': ['resource_volume', 'resource_remaining'],
                        'Region': ['test_reg', 'test_reg'],
                        'Commodity': ['coal', 'coal'],
                        'Level': ['resource', 'resource'],
                        'Grade': ['a', 'a'],
                        'Units': ['GWa', '%'],
                        '2010': [1000, 0.9],
                        '2020': [np.nan, 0.9],
                        '2030': [np.nan, 0.9],
                        '2040': [np.nan, 0.9],
                        'Comment': [np.nan, np.nan]})
    exp = exp[['Resource', 'Parameter', 'Region', 'Commodity', 'Level',
               'Grade', 'Units', '2010', '2020', '2030', '2040', 'Comment']]
    obs = read_input[3]
    pdt.assert_frame_equal(exp, obs)


def test_read_input_mpa_data(read_input):
    exp = pd.DataFrame({'Technology': ['test_ppl'],
                        'startup_lo': [0.05],
                        'mpa_lo': [-0.05],
                        'startup_up': [0.05],
                        'mpa_up': [0.075]})
    exp = exp[['Technology', 'startup_lo', 'mpa_lo', 'startup_up', 'mpa_up']]
    obs = read_input[4]
    pdt.assert_frame_equal(exp, obs)


@pytest.fixture(scope="session")
def create_scen(init_model):
    scenario, model_nm, scen_nm = init_model.create_scen()
    yield scenario, model_nm, scen_nm


def test_create_scen_model_name(create_scen):
    exp = 'xlsx_test_model'
    obs = create_scen[1]
    assert exp == obs


def test_create_scen_scenario_name(create_scen):
    exp = 'xlsx_test_scenario'
    obs = create_scen[2]
    assert exp == obs


@pytest.fixture(scope="session")
def add_meta(init_model):
    horizon, vintage_years, firstyear = init_model.add_metadata()
    yield horizon, vintage_years, firstyear


def test_add_meta_horizon(add_meta):
    exp = ['2000', '2005', '2010', '2020', '2030', '2040']
    obs = add_meta[0]
    assert exp == obs


def test_add_meta_first_year(add_meta):
    exp = 2010
    obs = add_meta[2]
    assert exp == obs


@pytest.fixture(scope="session")
def add_par(create_scen, add_meta):
    ap = xlsx_importer.add_par(
        create_scen[0], add_meta[0], add_meta[1], add_meta[2], False)
    yield ap


@pytest.fixture(scope="session")
def add_par_resource(init_model, add_par):
    init_model.fossil_resource_input_data(add_par)


def test_add_par_fossil_resource_volume(add_par_resource, create_scen):
    exp = pd.DataFrame({'commodity': ['coal'],
                        'grade': ['a'],
                        'node': ['test_reg'],
                        'unit': ['GWa'],
                        'value': 1000.0})
    obs = create_scen[0].par('resource_volume')
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_fossil_resource_remaining(add_par_resource, create_scen):
    exp = pd.DataFrame({'commodity': 'coal',
                        'grade': 'a',
                        'node': 'test_reg',
                        'unit': '%',
                        'value': 0.9,
                        'year': [2010, 2020, 2030, 2040]})
    obs = create_scen[0].par('resource_remaining')
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


@pytest.fixture(scope="session")
def add_par_demand(init_model, add_par):
    init_model.demand_input_data(add_par)


def test_add_par_demand(add_par_demand, create_scen):
    exp = pd.DataFrame({'commodity': 'electricity',
                        'level': 'useful',
                        'node': 'test_reg',
                        'time': 'year',
                        'unit': 'GWa',
                        'value': [5, 6, 7, 8],
                        'year': [2010, 2020, 2030, 2040]})
    obs = create_scen[0].par('demand')
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


@pytest.fixture(scope="session")
def add_par_tec(init_model, add_par):
    init_model.technology_parameters(add_par)


def test_add_par_tec_input(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'input',
                'unit': '%',
                'commodity': 'coal',
                'level': 'resource',
                'mode': 'standard',
                'node_origin': 'test_reg',
                'time': 'year',
                'time_origin': 'year',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [2.5,	np.nan,	np.nan,	np.nan],
                2020: [2.5,	2.5,	np.nan,	np.nan],
                2030: [2.5,	2.5,	2.5,	np.nan],
                2040: [2.5,	2.5,	2.5,	2.5]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='input').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_output(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'output',
                'unit': '%',
                'commodity': 'electricity',
                'level': 'useful',
                'mode': 'standard',
                'node_dest': 'test_reg',
                'time': 'year',
                'time_dest': 'year',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [1.0,	np.nan,	np.nan,	np.nan],
                2020: [1.0,	1.0,	np.nan,	np.nan],
                2030: [1.0,	1.0,	1.0,	np.nan],
                2040: [1.0,	1.0,	1.0,	1.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp_dict.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='output').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_inv_cost(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'inv_cost',
                'unit': 'USD/GW',
                'year_vtg': '',
                2010: [1600000000],
                2020: [1600000000],
                2030: [1600000000],
                2040: [1600000000]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='inv_cost').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_fix_cost(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'fix_cost',
                'unit': 'USD/GW',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [30000000.0,	np.nan,	np.nan,	np.nan],
                2020: [30000000.0,	30000000.0,	np.nan,	np.nan],
                2030: [30000000.0,	30000000.0,	30000000.0,	np.nan],
                2040: [30000000.0,	30000000.0,	30000000.0,	30000000.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='fix_cost').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_var_cost(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'var_cost',
                'unit': 'USD/GWa',
                'mode': 'standard',
                'time': 'year',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [422232000.0,	np.nan,	np.nan,	np.nan],
                2020: [422232000.0,	422232000.0,	np.nan,	np.nan],
                2030: [422232000.0,	422232000.0,	422232000.0,	np.nan],
                2040: [422232000.0,	422232000.0,	422232000.0,	422232000.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='var_cost').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_lifetime(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'technical_lifetime',
                'unit': 'y',
                'year_vtg': '',
                2010: [10.0],
                2020: [10.0],
                2030: [10.0],
                2040: [10.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='technical_lifetime').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_bound_activity_lo(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'bound_activity_lo',
                'unit': 'GWa',
                'mode': 'standard',
                'time': 'year',
                'year_vtg': '',
                2010: [4.0],
                2020: [4.0],
                2030: [4.0],
                2040: [4.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='bound_activity_lo').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_bound_activity_up(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'bound_activity_up',
                'unit': 'GWa',
                'mode': 'standard',
                'time': 'year',
                'year_vtg': '',
                2010: [6.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='bound_activity_up').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_bound_new_capacity_lo(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'bound_new_capacity_lo',
                'unit': 'GW',
                'year_vtg': '',
                2020: [5.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='bound_new_capacity_lo').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_bound_new_capacity_up(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'bound_new_capacity_up',
                'unit': 'GW',
                'year_vtg': '',
                2010: [1.5]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='bound_new_capacity_up').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_capacity_factor(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'capacity_factor',
                'unit': '%',
                'time': 'year',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [0.75,	np.nan,	np.nan,	np.nan],
                2020: [0.75,	0.75,	np.nan,	np.nan],
                2030: [0.75,	0.75,	0.75,	np.nan],
                2040: [0.75,	0.75,	0.75,	0.75]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='capacity_factor').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_emission_factor(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'emission_factor',
                'unit': 'Mt CO2/GWa',
                'emission': 'CO2',
                'mode': 'standard',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [0.814,	np.nan,	np.nan,	np.nan],
                2020: [0.814,	0.814,	np.nan,	np.nan],
                2030: [0.814,	0.814,	0.814,	np.nan],
                2040: [0.814,	0.814,	0.814,	0.814]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='emission_factor').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_growth_activity_lo(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'growth_activity_lo',
                'unit': '%',
                'time': 'year',
                'year_vtg': '',
                2020: [0.03],
                2030: [0.03],
                2040: [0.03]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='growth_activity_lo').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_growth_activity_up(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'growth_activity_up',
                'unit': '%',
                'time': 'year',
                'year_vtg': '',
                2020: [0.05],
                2030: [0.05],
                2040: [0.05]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='growth_activity_up').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_reliability_factor(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node': 'test_reg',
                'par': 'reliability_factor',
                'unit': '%',
                'commodity': 'electricity',
                'level': 'useful',
                'rating': 'full_rel',
                'time': 'year',
                'year_vtg': '',
                2010: [1.0],
                2020: [1.0],
                2030: [1.0],
                2040: [1.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='reliability_factor').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_flexibility_factor(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node_loc': 'test_reg',
                'par': 'flexibility_factor',
                'unit': '%',
                'commodity': 'electricity',
                'level': 'useful',
                'mode': 'standard',
                'rating': 'full_rel',
                'time': 'year',
                'year_vtg': [2010, 2020, 2030, 2040],
                2010: [0.15,	np.nan,	np.nan,	np.nan],
                2020: [0.15,	0.15,	np.nan,	np.nan],
                2030: [0.15,	0.15,	0.15,	np.nan],
                2040: [0.15,	0.15,	0.15,	0.15]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='flexibility_factor').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_add_par_tec_rating_bin(create_scen, add_par_tec):
    exp_dict = {'technology': 'test_ppl',
                'node': 'test_reg',
                'par': 'rating_bin',
                'unit': '%',
                'commodity': 'electricity',
                'level': 'useful',
                'rating': 'full_rel',
                'time': 'year',
                'year_vtg': '',
                2010: [1.0],
                2020: [1.0],
                2030: [1.0],
                2040: [1.0]}
    exp = pd.DataFrame(exp_dict)
    exp = exp[list(exp.keys())]
    obs = views.tec_view(
        create_scen[0], tec='test_ppl', par='rating_bin').reset_index()
    pdt.assert_frame_equal(exp, obs, check_dtype=False)
