import pandas as pd
import numpy as np

def prepare_calibration_data(original, sector_commodity_mapping, econ_pars,
                             gdp_calibrate, aeei, MERtoPPP):
    def calc_growth(row):
        val = float(row.values[0] + 1) ** (
                1 / period_length.loc[int(row.name)].values[0]) - 1
        return val

    def find_aeei(row):
        val = aeei[row.loc['node']][row.loc['year']][row.loc['commodity']]
        return val

    dict={}

    commodity_list = list(sector_commodity_mapping.values())
    dict['commodity_list'] = commodity_list
    sector_list = list(sector_commodity_mapping.keys())
    dict['sector_list'] = sector_list

    # temporal structure
    year = [int(i) for i in original.set("year").tolist()]
    firstmodelyear = int(
        original.set("cat_year", {'type_year': "firstmodelyear"})[
            ["year"]].values)
    dict['firstmodelyear'] = firstmodelyear
    year_message = [i for i in year if i >= firstmodelyear]
    dict['year_message'] = year_message

    try:
        baseyearmacro = [i for i in year if i < firstmodelyear][-1]
    except ValueError:
        print('Scenario has no MACRO base year - '
              'add at least one year before first model year')
    dict['baseyearmacro'] = baseyearmacro
    year_macro = [i for i in year if i >= baseyearmacro]
    dict['year_macro'] = year_macro

    # periods
    period_list = year_message
    dict['period_list'] = period_list

    # period length
    period_length = pd.DataFrame(index=year_macro[1:],
                                 data=np.diff(year_macro))

    # list of regions in the model
    region_list = [i for i in original.set("node").tolist() if i != 'World']
    dict['region_list'] = region_list

    # Economic Parameters
    econ_pars = pd.DataFrame.from_dict(econ_pars)
    # lower bound parameters by region (used to avoid divergences in MACRO solution)
    dict['lotol'] = econ_pars.loc['lotol']
    # initial capital to GDP ration in 1990 (by region)
    dict['kgdp'] = econ_pars.loc['kgdp']
    # depreciation rate (by region)
    dict['depr'] = econ_pars.loc['depr']
    # capital value share (by region)
    dict['kpvs'] = econ_pars.loc['kpvs']
    # VK, 10 April 2008: DRATE (social discount rate from MESSAGE) introduced as a new parameter as in MERGE 5
    dict['drate'] = econ_pars.loc['drate']
    # subsitution elasticity between x and y  (by region)
    dict['esub'] = econ_pars.loc['esub']

    # reference price of energy service demands in [US$2005/kWyr]
    # ?: hier PRICE_COMMODITY aus 2020 ok?
    p_ref = original.var("PRICE_COMMODITY", {'year': firstmodelyear,
                                                 'commodity': commodity_list})
    p_ref['year'] = baseyearmacro
    dict['p_ref'] = p_ref

    # reference demand in base year [GWyr]
    demand_ref = original.var("DEMAND", {'year': firstmodelyear,
                                             'commodity': commodity_list})
    demand_ref['year'] = baseyearmacro
    dict['demand_ref'] = demand_ref

    # reference energy system costs in base year [billion US$2005]
    # ?: hier COST_NODAL aus 2020 ok?
    cost_ref = original.var("COST_NODAL_NET")
    cost_ref = cost_ref[cost_ref.year==firstmodelyear]
    cost_ref['year'] = baseyearmacro
    dict['cost_ref'] = cost_ref

    # calculate growth rates based on calibrated GDP
    change = gdp_calibrate.pct_change().dropna()
    growth = change.apply(calc_growth, axis=1)
    dict['growth'] = growth

    # uncalibrated AEEI (autonomous energy efficiency improvement)
    reform = {(l1_k, l2_k, l3_k): values for l1_k, l2_d in aeei.items() for
              l2_k, l3_d in l2_d.items() for l3_k, values in l3_d.items()}
    df = pd.DataFrame(index=reform.keys(),
                      columns=['value']).reset_index().rename(
        columns={'level_0': 'node', 'level_1': 'year', 'level_2': 'commodity'})

    df['value'] = df.apply(find_aeei, axis=1)
    aeei = df.copy()

    # MER to PPP conversion ratio
    # ?: hier LAM werte  ok?
    MERtoPPP = pd.DataFrame.from_dict(MERtoPPP)

    #########################################################################
    # NEVER USED PARAMETERS - was sollen wir mit denen machen?
    #########################################################################
    # read correction coefficients (MESSAGE vs MACRO energy units)
    correction = [1e-3] * 6
    # read scaling factors for production function
    scaling = [1] * 6

    return dict
