import numpy as np
import pandas as pd

from ixmp import IAMC_IDX

from message_ix import Scenario
from message_ix.utils import make_df


SCENARIO = {
    'dantzig': {
        'model': 'Canning problem (MESSAGE scheme)',
        'scenario': 'standard',
    },
    'dantzig multi-year': {
        'model': 'Canning problem (MESSAGE scheme)',
        'scenario': 'multi-year',
    },
    'westeros': {
        'model': 'Westeros Electrified',
        'scenario': 'baseline',
    },
}


# Create and populate ixmp databases

_ms = [SCENARIO['dantzig']['model'], SCENARIO['dantzig']['scenario']]
HIST_DF = pd.DataFrame(
    [_ms + ['DantzigLand', 'GDP', 'USD', 850., 900., 950.], ],
    columns=IAMC_IDX + [1962, 1963, 1964],
)
INP_DF = pd.DataFrame(
    [_ms + ['DantzigLand', 'Demand', 'cases', 850., 900., 950.], ],
    columns=IAMC_IDX + [1962, 1963, 1964],
)
TS_DF = pd.concat([HIST_DF, INP_DF], sort=False)
TS_DF.sort_values(by='variable', inplace=True)
TS_DF.index = range(len(TS_DF.index))

TS_DF_CLEARED = TS_DF.copy()
TS_DF_CLEARED.loc[0, 1963] = np.nan
TS_DF_CLEARED.loc[0, 1964] = np.nan


def make_dantzig(mp, solve=False, multi_year=False, **solve_opts):
    """Return an :class:`message_ix.Scenario` for Dantzig's canning problem.

    Parameters
    ----------
    mp : ixmp.Platform
        Platform on which to create the scenario.
    solve : bool, optional
        If True, the scenario is solved.
    multi_year : bool, optional
        If True, the scenario has years 1963--1965 inclusive. Otherwise, the
        scenario has the single year 1963.
    """
    # add custom units and region for timeseries data
    mp.add_unit('USD/case')
    mp.add_unit('case')
    mp.add_region('DantzigLand', 'country')

    # initialize a new (empty) instance of an `ixmp.Scenario`
    scen = Scenario(
        mp,
        model=SCENARIO['dantzig']['model'],
        scenario='multi-year' if multi_year else 'standard',
        annotation="Dantzig's canning problem as a MESSAGE-scheme Scenario",
        version='new')

    # Sets
    # NB commit() is refused if technology and year are not given
    t = ['canning_plant', 'transport_from_seattle', 'transport_from_san-diego']
    sets = {
        'technology': t,
        'node': 'seattle san-diego new-york chicago topeka'.split(),
        'mode': 'production to_new-york to_chicago to_topeka'.split(),
        'level': 'supply consumption'.split(),
        'commodity': ['cases'],
    }

    for name, values in sets.items():
        scen.add_set(name, values)

    scen.add_horizon({'year': [1962, 1963], 'firstmodelyear': 1963})

    # Parameters
    par = {}

    demand = {'node': 'new-york chicago topeka'.split(),
              'value': [325, 300, 275]}
    par['demand'] = make_df(
        pd.DataFrame.from_dict(demand), commodity='cases', level='consumption',
        time='year', unit='case', year=1963)

    b_a_u = {'node_loc': ['seattle', 'san-diego'],
             'value': [350, 600]}
    par['bound_activity_up'] = make_df(
        pd.DataFrame.from_dict(b_a_u), mode='production',
        technology='canning_plant', time='year', unit='case', year_act=1963)
    par['ref_activity'] = par['bound_activity_up'].copy()

    input = pd.DataFrame([
        ['to_new-york', 'seattle', 'seattle', t[1]],
        ['to_chicago', 'seattle', 'seattle', t[1]],
        ['to_topeka', 'seattle', 'seattle', t[1]],
        ['to_new-york', 'san-diego', 'san-diego', t[2]],
        ['to_chicago', 'san-diego', 'san-diego', t[2]],
        ['to_topeka', 'san-diego', 'san-diego', t[2]],
    ], columns=['mode', 'node_loc', 'node_origin', 'technology'])
    par['input'] = make_df(
        input, commodity='cases', level='supply', time='year',
        time_origin='year', unit='case', value=1, year_act=1963,
        year_vtg=1963)

    output = pd.DataFrame([
        ['supply', 'production', 'seattle', 'seattle', t[0]],
        ['supply', 'production', 'san-diego', 'san-diego', t[0]],
        ['consumption', 'to_new-york', 'new-york', 'seattle', t[1]],
        ['consumption', 'to_chicago', 'chicago', 'seattle', t[1]],
        ['consumption', 'to_topeka', 'topeka', 'seattle', t[1]],
        ['consumption', 'to_new-york', 'new-york', 'san-diego', t[2]],
        ['consumption', 'to_chicago', 'chicago', 'san-diego', t[2]],
        ['consumption', 'to_topeka', 'topeka', 'san-diego', t[2]],
    ], columns=['level', 'mode', 'node_dest', 'node_loc', 'technology'])
    par['output'] = make_df(
        output, commodity='cases', time='year', time_dest='year', unit='case',
        value=1, year_act=1963, year_vtg=1963)

    # Variable cost: cost per kilometre × distance (neither parametrized
    # explicitly)
    var_cost = pd.DataFrame([
        ['to_new-york', 'seattle', 'transport_from_seattle', 0.225],
        ['to_chicago', 'seattle', 'transport_from_seattle', 0.153],
        ['to_topeka', 'seattle', 'transport_from_seattle', 0.162],
        ['to_new-york', 'san-diego', 'transport_from_san-diego', 0.225],
        ['to_chicago', 'san-diego', 'transport_from_san-diego', 0.162],
        ['to_topeka', 'san-diego', 'transport_from_san-diego', 0.126],
    ], columns=['mode', 'node_loc', 'technology', 'value'])
    par['var_cost'] = make_df(
        var_cost, time='year', unit='USD/case', year_act=1963, year_vtg=1963)

    for name, value in par.items():
        scen.add_par(name, value)

    if multi_year:
        scen.add_set('year', [1964, 1965])
        scen.add_par('technical_lifetime', ['seattle', 'canning_plant', 1964],
                     3, 'y')

    if solve:
        # Always read one equation. Used by test_core.test_year_int.
        scen.init_equ('COMMODITY_BALANCE_GT',
                      ['node', 'commodity', 'level', 'year', 'time'])
        solve_opts['equ_list'] = solve_opts.get('equ_list', []) \
            + ['COMMODITY_BALANCE_GT']

    scen.commit('Created a MESSAGE-scheme version of the transport problem.')
    scen.set_as_default()

    if solve:
        scen.solve(**solve_opts)

    scen.check_out(timeseries_only=True)
    scen.add_timeseries(HIST_DF, meta=True)
    scen.add_timeseries(INP_DF)
    scen.commit("Import Dantzig's transport problem for testing.")

    return scen


def make_westeros(mp, emissions=False, solve=False):
    """Return an :class:`message_ix.Scenario` for the Westeros model.

    This is the same model used in the ``westeros_baseline.ipynb`` tutorial.

    Parameters
    ----------
    mp : ixmp.Platform
        Platform on which to create the scenario.
    emissions : bool, optional
        If True, the ``emissions_factor`` parameter is also populated for CO2.
    solve : bool, optional
        If True, the scenario is solved.
    """
    scen = Scenario(mp, version='new', **SCENARIO['westeros'])

    # Sets

    history = [690]
    model_horizon = [700, 710, 720]
    scen.add_horizon({'year': history + model_horizon,
                      'firstmodelyear': model_horizon[0]})

    country = 'Westeros'
    scen.add_spatial_sets({'country': country})

    sets = {
        'technology': 'coal_ppl wind_ppl grid bulb'.split(),
        'mode': ['standard'],
        'level': 'secondary final useful'.split(),
        'commodity': 'electricity light'.split(),
    }

    for name, values in sets.items():
        scen.add_set(name, values)

    # Parameters — copy & paste from the tutorial notebook

    gdp_profile = pd.Series([1., 1.5, 1.9],
                            index=pd.Index(model_horizon, name='Time'))
    demand_per_year = 40 * 12 * 1000 / 8760
    light_demand = pd.DataFrame({
        'node': country,
        'commodity': 'light',
        'level': 'useful',
        'year': model_horizon,
        'time': 'year',
        'value': (100 * gdp_profile).round(),
        'unit': 'GWa',
    })
    scen.add_par("demand", light_demand)

    year_df = scen.vintage_and_active_years()
    vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

    base = {
        'node_loc': country,
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'standard',
        'time': 'year',
        'unit': '-',
    }

    base_input = make_df(base, node_origin=country, time_origin='year')
    base_output = make_df(base, node_dest=country, time_dest='year')

    bulb_out = make_df(base_output, technology='bulb', commodity='light',
                       level='useful', value=1.0)
    scen.add_par('output', bulb_out)

    bulb_in = make_df(base_input, technology='bulb', commodity='electricity',
                      level='final', value=1.0)
    scen.add_par('input', bulb_in)

    grid_efficiency = 0.9
    grid_out = make_df(base_output, technology='grid', commodity='electricity',
                       level='final', value=grid_efficiency)
    scen.add_par('output', grid_out)

    grid_in = make_df(base_input, technology='grid', commodity='electricity',
                      level='secondary', value=1.0)
    scen.add_par('input', grid_in)

    coal_out = make_df(base_output, technology='coal_ppl',
                       commodity='electricity', level='secondary', value=1.)
    scen.add_par('output', coal_out)

    wind_out = make_df(base_output, technology='wind_ppl',
                       commodity='electricity', level='secondary', value=1.)
    scen.add_par('output', wind_out)

    base_capacity_factor = {
        'node_loc': country,
        'year_vtg': vintage_years,
        'year_act': act_years,
        'time': 'year',
        'unit': '-',
    }

    capacity_factor = {
        'coal_ppl': 1,
        'wind_ppl': 1,
        'bulb': 1,
    }

    for tec, val in capacity_factor.items():
        df = make_df(base_capacity_factor, technology=tec, value=val)
        scen.add_par('capacity_factor', df)

    base_technical_lifetime = {
        'node_loc': country,
        'year_vtg': model_horizon,
        'unit': 'y',
    }

    lifetime = {
        'coal_ppl': 20,
        'wind_ppl': 20,
        'bulb': 1,
    }

    for tec, val in lifetime.items():
        df = make_df(base_technical_lifetime, technology=tec, value=val)
        scen.add_par('technical_lifetime', df)

    base_growth = {
        'node_loc': country,
        'year_act': model_horizon,
        'time': 'year',
        'unit': '-',
    }

    growth_technologies = [
        "coal_ppl",
        "wind_ppl",
    ]

    for tec in growth_technologies:
        df = make_df(base_growth, technology=tec, value=0.1)
        scen.add_par('growth_activity_up', df)

    historic_demand = 0.85 * demand_per_year
    historic_generation = historic_demand / grid_efficiency
    coal_fraction = 0.6

    base_capacity = {
        'node_loc': country,
        'year_vtg': history,
        'unit': 'GWa',
    }

    base_activity = {
        'node_loc': country,
        'year_act': history,
        'mode': 'standard',
        'time': 'year',
        'unit': 'GWa',
    }

    old_activity = {
        'coal_ppl': coal_fraction * historic_generation,
        'wind_ppl': (1 - coal_fraction) * historic_generation,
    }

    for tec, val in old_activity.items():
        df = make_df(base_activity, technology=tec, value=val)
        scen.add_par('historical_activity', df)

    act_to_cap = {
        # 20 year lifetime
        'coal_ppl': 1 / 10 / capacity_factor['coal_ppl'] / 2,
        'wind_ppl': 1 / 10 / capacity_factor['wind_ppl'] / 2,
    }

    for tec in act_to_cap:
        value = old_activity[tec] * act_to_cap[tec]
        df = make_df(base_capacity, technology=tec, value=value)
        scen.add_par('historical_new_capacity', df)

    rate = [0.05] * len(model_horizon)
    unit = ['-'] * len(model_horizon)
    scen.add_par("interestrate", model_horizon, rate, unit)

    base_inv_cost = {
        'node_loc': country,
        'year_vtg': model_horizon,
        'unit': 'USD/GWa',
    }

    # in $ / kW
    costs = {
        'coal_ppl': 500,
        'wind_ppl': 1500,
        'bulb': 5,
    }

    for tec, val in costs.items():
        df = make_df(base_inv_cost, technology=tec, value=val)
        scen.add_par('inv_cost', df)

    base_fix_cost = {
        'node_loc': country,
        'year_vtg': vintage_years,
        'year_act': act_years,
        'unit': 'USD/GWa',
    }

    # in $ / kW
    costs = {
        'coal_ppl': 30,
        'wind_ppl': 10,
    }

    for tec, val in costs.items():
        df = make_df(base_fix_cost, technology=tec, value=val)
        scen.add_par('fix_cost', df)

    base_var_cost = {
        'node_loc': country,
        'year_vtg': vintage_years,
        'year_act': act_years,
        'mode': 'standard',
        'time': 'year',
        'unit': 'USD/GWa',
    }

    # in $ / MWh
    costs = {
        'coal_ppl': 30,
        'grid': 50,
    }

    for tec, val in costs.items():
        df = make_df(base_var_cost, technology=tec, value=val)
        scen.add_par('var_cost', df)

    scen.commit('basic model of Westerosi electrification')
    scen.set_as_default()

    if emissions:
        scen.check_out()

        # Introduce the emission species CO2 and the emission category GHG
        scen.add_set('emission', 'CO2')
        scen.add_cat('emission', 'GHG', 'CO2')

        # we now add CO2 emissions to the coal powerplant
        base_emission_factor = {
            'node_loc': country,
            'year_vtg': vintage_years,
            'year_act': act_years,
            'mode': 'standard',
            'unit': 'USD/GWa',
        }

        emission_factor = make_df(
            base_emission_factor, technology='coal_ppl', emission='CO2',
            value=100.
        )
        scen.add_par('emission_factor', emission_factor)

        scen.commit('Added emissions sets/params to Westeros model.')

    if solve:
        scen.solve()

    return scen
