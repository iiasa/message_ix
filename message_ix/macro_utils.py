import pandas as pd
import numpy as np


def calibrate_macro(original, level, sector_commodity_mapping,
                    econ_pars, gdp_calibrate, base_year_demand,
                    aeei, macro_regions):
    def calc_growth(row):
        val = float(row.values[0] + 1) ** (
                1 / period_length.loc[int(row.name)].values[0]) - 1
        return val

    def find_aeei(row):
        val = aeei[row.loc['node']][row.loc['year']][row.loc['commodity']]
        return val

    data = {}

    data['commodity_list'] = list(sector_commodity_mapping.values())
    data['sector_list'] = list(sector_commodity_mapping.keys())

    # temporal structure
    year = [int(i) for i in original.set("year").tolist()]
    firstmodelyear = int(
        original.set("cat_year", {'type_year': "firstmodelyear"})[
            ["year"]].values)
    data['firstmodelyear'] = firstmodelyear
    year_message = [i for i in year if i >= firstmodelyear]
    data['year_message'] = year_message

    try:
        baseyearmacro = [i for i in year if i < firstmodelyear][-1]
    except ValueError:
        print('Scenario has no MACRO base year - '
              'add at least one year before first model year')
    data['baseyearmacro'] = baseyearmacro
    year_macro = [i for i in year if i >= baseyearmacro]
    data['year_macro'] = year_macro

    # periods
    data['period_list'] = year_message

    # period length
    period_length = pd.DataFrame(index=year_macro[1:],
                                 data=np.diff(year_macro))

    # list of regions in the model
    data['region_list'] = macro_regions

    # Economic Parameters
    # lower bound parameters by region (used to avoid divergences in
    # MACRO solution)
    data['lotol'] = econ_pars.loc['lotol']
    # initial capital to GDP ration in 1990 (by region)
    data['kgdp'] = econ_pars.loc['kgdp']
    # depreciation rate (by region)
    data['depr'] = econ_pars.loc['depr']
    # capital value share (by region)
    data['kpvs'] = econ_pars.loc['kpvs']
    # VK, 10 April 2008: DRATE (social discount rate from MESSAGE)
    # introduced as a new parameter as in MERGE 5
    data['drate'] = econ_pars.loc['drate']
    # subsitution elasticity between x and y  (by region)
    data['esub'] = econ_pars.loc['esub']

    # reference price of energy service demands in [US$2005/kWyr]
    # ?: hier PRICE_COMMODITY aus 2020 ok?
    p_ref = original.var("PRICE_COMMODITY", {'year': firstmodelyear,
                                             'commodity': data[
                                                 'commodity_list']})
    # Todo: write more explicit error message
    if len(p_ref) < len(data['commodity_list']):
        raise ValueError
        print('The Scenario has one or more PRICE_COMMODITY = 0. '
              'MACRO cannot handle Prices equal to zero. '
              'Your model mightbe overconstraint')

    p_ref['year'] = baseyearmacro
    data['p_ref'] = p_ref

    # reference demand in base year [GWyr]
    demand_ref = pd.DataFrame(columns=original.var("DEMAND").columns)
    for node in base_year_demand.columns:
        _demand_ref = pd.DataFrame(columns=['node', 'commodity', 'level',
                                            'year', 'lvl'],
                                   index=base_year_demand.index)
        _demand_ref['node'] = node
        _demand_ref['commodity'] = _demand_ref.index
        _demand_ref['level'] = level
        _demand_ref['year'] = baseyearmacro
        _demand_ref['lvl'] = base_year_demand
        demand_ref = demand_ref.append(_demand_ref)

    data['demand_ref'] = demand_ref

    # reference energy system costs in base year [billion US$2005]
    # ?: here COST_NODAL from 2020 ok?
    cost_ref = original.var("COST_NODAL_NET")
    cost_ref = cost_ref[cost_ref.year == firstmodelyear]
    cost_ref['year'] = baseyearmacro
    data['cost_ref'] = cost_ref

    # calculate growth rates based on calibrated GDP
    # Todo: Check for compatibility with multiple nodes
    change = gdp_calibrate.pct_change().dropna()
    growth = change.apply(calc_growth, axis=1)
    data['growth'] = growth

    # uncalibrated AEEI (autonomous energy efficiency improvement)
    reform = {(l1_k, l2_k, l3_k): values for l1_k, l2_d in aeei.items() for
              l2_k, l3_d in l2_d.items() for l3_k, values in l3_d.items()}
    df = pd.DataFrame(index=reform.keys(),
                      columns=['value']).reset_index().rename(
        columns={'level_0': 'node', 'level_1': 'year', 'level_2': 'commodity'})

    df['value'] = df.apply(find_aeei, axis=1)
    aeei = df.copy()
    data['aeei'] = aeei

    return data
