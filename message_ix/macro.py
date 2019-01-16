import ixmp
import message_ix
import os
import pandas as pd
from macro_utils import prepare_calibration_data

##############################################################################
# direct input of parameters from kwargs
##############################################################################
mp = ixmp.Platform(dbprops='localdb/message_zaf', dbtype='HSQLDB')
model = 'MESSAGE South Africa'
scenario = 'baseline_MACRO_calibrated_new'
original = message_ix.Scenario(mp, model=model, scenario=scenario)

# names of energy sectors
sector_commodity_mapping = {"i_spec": "i_spec", "i_therm": "i_therm",
                            "i_feed": "i_feed", "rc_spec": "rc_spec",
                            "rc_therm": "rc_therm", "transport": "transport"}
level = "useful"

econ_pars = {
    'South Africa': {'lotol': 0.05, 'kgdp': 3, 'depr': 0.05, 'kpvs': 0.3,
                     'drate': 0.5, 'esub': 0.2}}
gdp_calibrate = {
    'South Africa': {2010: 372, 2020: 543, 2030: 764, 2040: 1074,
                     2050: 1412}}

base_year_demand = {'South Africa': {"i_spec": 9.8, "i_therm": 8.7, "i_feed": 5.3,
                    "rc_spec": 3.8, "rc_therm": 4.2, "transport": 19.46}}
base_year_demand = pd.DataFrame(base_year_demand)

gdp_calibrate = pd.DataFrame(gdp_calibrate)

aeei = {'South Africa': {
    '2020': {"i_spec": 2e-2, "i_therm": 2e-2, "i_feed": 2e-2, "rc_spec": 2e-2,
             "rc_therm": 2e-2, "transport": 2e-2},
    '2030': {"i_spec": 2e-2, "i_therm": 2e-2, "i_feed": 2e-2, "rc_spec": 2e-2,
             "rc_therm": 2e-2, "transport": 2e-2},
    '2040': {"i_spec": 2e-2, "i_therm": 2e-2, "i_feed": 2e-2, "rc_spec": 2e-2,
             "rc_therm": 2e-2, "transport": 2e-2},
    '2050': {"i_spec": 2e-2, "i_therm": 2e-2, "i_feed": 2e-2, "rc_spec": 2e-2,
             "rc_therm": 2e-2, "transport": 2e-2}}}

MERtoPPP = {'South Africa': {'2010': 1.761, '2020': 1.584, '2030': 1.438,
                             '2040': 1.319, '2050': 1.239}}
MERtoPPP = pd.DataFrame(MERtoPPP)


def init_macro(original, level, sector_commodity_mapping, econ_pars,gdp_calibrate,
               base_year_demand, aeei, MERtoPPP):
    data = prepare_calibration_data(original, level, sector_commodity_mapping,
                                    econ_pars, gdp_calibrate, base_year_demand,
                                    aeei, MERtoPPP)

    modelpath = 'C:\\Users\\ga46gup\\Modelle\\message_ix\\message_ix\\model'
    newscenario = scenario + '_MACRO'
    comment = "Adding MACRO structure and data to existing MESSAGE run"
    new = original.clone(model=model, scenario=scenario, annotation=comment,
                         keep_solution=False)
    new.check_out()

    path = 'C:\\Users\\ga46gup\\Modelle\\message_ix\\message_ix\\MACRO_py\MACRO_py'
    os.chdir(path)

    # useful demand levels by region and year
    demand_new = original.var("DEMAND", {'node': data['region_list'],
                                         'year': data['year_message'],
                                         'commodity': data['commodity_list']})
    demand = data['demand_ref'].append(demand_new)

    # useful energy demand prices by region and year
    price_new = original.var("PRICE_COMMODITY",
                             {'node': data['region_list'],
                              'year': data['year_message'],
                              'commodity': data['commodity_list']})
    price = data['p_ref'].append(price_new)

    # regional energy system costs
    total_cost_new = original.var("COST_NODAL_NET",
                                  {'node': data['region_list'],
                                   'year': data['year_message']})
    # reference energy system costs (convert from US. million to US. billion)
    total_cost = data['cost_ref'].append(total_cost_new)
    total_cost = total_cost.pivot_table(columns='node', index='year',
                                        values='lvl')
    total_cost = total_cost / 1e3

    # ------------------------------------------------------------------------
    # calculate derive MACRO variables (see Manne & Richels
    # "Buying GHG Insurance", Chapter 7, pp. 129-132 for details)
    # ------------------------------------------------------------------------
    # production function
    # exponent rho (esub is elasticity of substitution  between energy and the
    # value added aggregates, i.e. capital and labor)
    rho = (data['esub'] - 1) / data['esub']
    # production Y in base year
    gdp0 = gdp_calibrate.loc[data['baseyearmacro']]
    # capital K in base year
    k0 = data['kgdp'] * gdp0
    # investments I in base year
    i0 = k0 * (data['growth'].loc[data['firstmodelyear']] + data['depr'])
    # consumption C in base year
    c0 = gdp0 - i0 - total_cost.loc[data['baseyearmacro']]

    # production function coefficients for capital, labor (aconst) and
    # energy (bconst) are calibrated from the first-order optimality
    # condition, i.e. bconst from dY/d"ELEC" = peref or dY/d"NELE" = pnref
    # (equivalent as shown numerically below) and aconst by inserting bconst
    # back into the production function, setting the labor force index in the
    # base year to 1 (numeraire) and solving for aconst

    # production function coefficients of the different energy sectors
    # (factor of 1000 needed for billion US. to trillion US. conversion)
    data['demand_ref'] = data['demand_ref'].pivot_table(columns='commodity',
                                                        index='node',
                                                        values='lvl')
    data['p_ref'] = data['p_ref'].pivot_table(columns='commodity',
                                              index='node',
                                              values='lvl')

    def calc_bconst(row):
        val = (data['p_ref'].loc[row.name] / 1e3 * (
                float(1 / gdp0.loc[row.name]) * row) ** float(
            rho.loc[row.name] - 1))
        return val

    bconst = data['demand_ref'].apply(calc_bconst, axis=1)

    # production function coefficient of capital and labor
    # (factor of 1000 needed for billion US. to trillion US. conversion)
    def calc_partmp(row):
        val = bconst.loc[row.name] * row ** rho.loc[row.name]
        return val

    partmp = data['demand_ref'].apply(calc_partmp, axis=1)

    def calc_aconst(row):
        val = ((gdp_calibrate.loc[data['baseyearmacro'], row.name] / 1000) **
               rho.loc[
                   row.name] - partmp.sum(axis=0) / (
                           (k0.loc[row.name] / 1000) ** (
                           rho.loc[row.name] * data['kgdp'].loc[row.name])))
        return val

    aconst = partmp.apply(calc_aconst, axis=1)

    # ------------------------------------------------------------------------
    # add sets needed for MACRO (if they don't exist)
    # ------------------------------------------------------------------------
    # sets that are standard part of a MESSAGE scenario, but needed for
    # running MACRO standalone
    if not new.has_set("node"):
        new.init_set("node")
    for node in data['region_list']:
        new.add_set("node", node)

    if not new.has_set("type_node"):
        new.init_set("type_node")
    new.add_set("type_node", "economy")

    if not new.has_set("cat_node"):
        new.init_set("cat_node", ["type_node", "node"])
    for node in data['region_list']:
        new.add_set("cat_node", f"economy.{node}")

    if not new.has_set("year"):
        new.init_set("year")
    for year in data['period_list']:
        new.add_set("year", str(year))

    if not new.has_set("commodity"):
        new.init_set("commodity")
    for commodity in data['commodity_list']:
        new.add_set("commodity", commodity)

    if not new.has_set("level"):
        new.init_set("level")
    new.add_set("level", level)

    # set of MACRO base year
    if not new.has_set("type_year"):
        new.init_set("type_year")
    new.add_set("type_year", "baseyear_macro")
    new.add_set("type_year", "initializeyear_macro")

    if not new.has_set("cat_year"):
        new.init_set("cat_year", ["type_year", "year"])
    new.add_set("cat_year", f"baseyear_macro.{data['baseyearmacro']}")
    new.add_set("cat_year", f"initializeyear_macro.{data['baseyearmacro']}")

    # set of MACRO sectors
    if not new.has_set("sector"):
        new.init_set("sector")
    for sector in data['sector_list']:
        new.add_set("sector", sector)

    # mapping of MACRO sectors to MESSAGE commodity/level combinations
    if not new.has_set("mapping_macro_sector"):
        new.init_set("mapping_macro_sector", ["sector", "commodity", "level"])
    for k, v in sector_commodity_mapping.items():
        new.add_set("mapping_macro_sector", [k, v, level])

    # only needed for setting up a standalone MACRO model in a MESSAGE scheme
    # new.add_set("technology","dummy")

    # ------------------------------------------------------------------------
    # add parameters needed for MACRO

    # storage of MESSAGE results in GDX for standalone use of MACRO
    # (including calibration process)

    for unit in ['GWa', "USD/kWa","G.", "T.", '-']:
        if not unit in mp.units().tolist():
            mp.add_unit(unit)

    # demand
    if not new.has_par("demand_MESSAGE"):
        new.init_par("demand_MESSAGE", ["node", "sector", "year"])
    for node in data['region_list']:
        for sector in data['sector_list']:
            for year in data['period_list']:
                new.add_par("demand_MESSAGE", f"{node}.{sector}.{year}",
                            float(demand.loc[(demand.node == node) &
                                       (demand.year == year) &
                                       (demand.commodity ==
                                        sector_commodity_mapping[sector])]['lvl']),
                            "GWa")

    # prices
    if not new.has_par("price_MESSAGE"):
        new.init_par("price_MESSAGE", ["node", "sector", "year"])
    for node in data['region_list']:
        for sector in data['sector_list']:
            for year in data['period_list']:
                new.add_par("price_MESSAGE", f"{node}.{sector}.{year}",
                            price.loc[(price.node == node) &
                                      (price.year == year) &
                                      (price.commodity == sector_commodity_mapping[sector])]['lvl'],
                            "USD/kWa")

    # system costs
    if not new.has_par("cost_MESSAGE"):
        new.init_par("cost_MESSAGE", ["node", "year"])
    for node in data['region_list']:
        for year in data['period_list']:
            new.add_par("cost_MESSAGE", f"{node}.{year}",
                        total_cost.loc[year, node], "G.")

    # GDP values to calibrate to (incl. base year data)
    if not new.has_par("gdp_calibrate"):
        new.init_par("gdp_calibrate", ["node", "year"])
    for node in data['region_list']:
        for year in data['period_list']:
            new.add_par("gdp_calibrate", f"{node}.{year}",
                        gdp_calibrate.loc[year, node], "T.")

    # historical GDP values (base year data or data for model slicing)
    # ? passt hier baseyearmacro?
    if not new.has_par("historical_gdp"):
        new.init_par("historical_gdp", ["node", "year"])
    for node in data['region_list']:
        new.add_par("historical_gdp", f"{node}.{data['baseyearmacro']}",
                    gdp_calibrate.loc[data['baseyearmacro'], node], "T.")

    # MER to PPP conversion factor
    if not new.has_par("MERtoPPP"):
        new.init_par("MERtoPPP", ["node", "year"])
    for node in data['region_list']:
        for year in data['period_list']:
            new.add_par("MERtoPPP", f"{node}.{year}", MERtoPPP.loc[str(year), node],
                        "-")

    # capital to GDP ratio
    if not new.has_par("kgdp"):
        new.init_par("kgdp", ["node"])
    for node in data['region_list']:
        new.add_par("kgdp", node, data["kgdp"].loc[node], "-")

    # capital value share
    if not new.has_par("kpvs"):
        new.init_par("kpvs", ["node"])
    for node in data['region_list']:
        new.add_par("kpvs", node, data["kpvs"].loc[node], "-")

    # capital depreciation rate
    if not new.has_par("depr"):
        new.init_par("depr", ["node"])
    for node in data['region_list']:
        new.add_par("depr", node, data["depr"].loc[node], "-")

    # discount rate
    if not new.has_par("drate"):
        new.init_par("drate", ["node"])
    for node in data['region_list']:
        new.add_par("drate", node, data["drate"].loc[node], "-")

    # elasticity of substitution between capital-labor and total energy
    if not new.has_par("esub"):
        new.init_par("esub", ["node"])
    for node in data['region_list']:
        new.add_par("esub", node, data["esub"].loc[node], "-")

    # tolerance parameter
    if not new.has_par("lotol"):
        new.init_par("lotol", ["node"])
    for node in data['region_list']:
        new.add_par("lotol", node, data["lotol"].loc[node], "-")

    # base year reference prices
    if not new.has_par("p_ref"):
        new.init_par("p_ref", ["node", "sector"])
    for node in data['region_list']:
        for sector in data['sector_list']:
            new.add_par("p_ref", f"{node}.{sector}",
                        data['p_ref'].loc[node, sector], "USD/kWa")

    # production function coefficient of capital and labor - ??? welches vormat soll ads haben???
    # if not new.has_par("lakl"):
    #     new.init_par("lakl", ["node"])
    # for node in data['region_list']:
    #     new.add_par("lakl", node, aconst.loc[node], "-")

    # production function coefficients of the different energy sectors
    if not new.has_par("prfconst"):
        new.init_par("prfconst", ["node", "sector"])
    for node in data['region_list']:
        for sector in data['sector_list']:
            new.add_par("prfconst", f"{node}.{sector}",
                        bconst.loc[node, sector], "-")

    # labor supply growth rate
    if not new.has_par("grow"):
        new.init_par("grow", ["node", "year"])
    for node in data['region_list']:
        for year in data['period_list']:
            new.add_par("grow", f"{node}.{year}",
                        data['growth'].loc[year],
                        "-")

    # autonomous energy efficiency improvement (aeei) coefficients
    if not new.has_par("aeei"):
        new.init_par("aeei", ["node", "sector", "year"])
    for node in data['region_list']:
        for sector in data['sector_list']:
            for year in data['period_list']:
                new.add_par("aeei", f"{node}.{sector}.{year}",
                            data['aeei'].loc[(data['aeei'].node==node) &
                                             (data['aeei'].year == str(year)) &
                                             (data['aeei'].commodity == sector_commodity_mapping[sector])]['value'], "-")

    # ------------------------------------------------------------------------
    # initialize cost accounting variables/equations if they don't exist
    # MESSAGE variables relvant for MACRO
    if not new.has_var("DEMAND"):
        new.init_var("DEMAND", ["node", "commodity", "level", "year", "time"])
    if not new.has_var("PRICE_COMMODITY"):
        new.init_var("PRICE", ["node", "commodity", "level", "year", "time"])
    if not new.has_var("COST_NODAL"):
        new.init_var("COST_NODAL", ["node", "year"])
    if not new.has_var("COST_NODAL_NET"):
        new.init_var("COST_NODAL_NET", ["node", "year"])
    if not new.has_equ("COST_ACCOUNTING_NODAL"):
        new.init_equ("COST_ACCOUNTING_NODAL", ["node", "year"])
    # MACRO variables
    if not new.has_var("GDP"):
        new.init_var("GDP", ["node", "year"])
    if not new.has_var("I"):
        new.init_var("I", ["node", "year"])
    if not new.has_var("C"):
        new.init_var("C", ["node", "year"])
    if not new.has_var("K"):
        new.init_var("K", ["node", "year"])
    if not new.has_var("KN"):
        new.init_var("KN", ["node", "year"])
    if not new.has_var("Y"):
        new.init_var("Y", ["node", "year"])
    if not new.has_var("YN"):
        new.init_var("YN", ["node", "year"])
    if not new.has_var("EC"):
        new.init_var("EC", ["node", "year"])
    if not new.has_var("UTILITY"):
        new.init_var("UTILITY")
    if not new.has_var("PHYSENE"):
        new.init_var("PHYSENE", ["node", "sector", "year"])
    if not new.has_var("PRODENE"):
        new.init_var("PRODENE", ["node", "sector", "year"])
    if not new.has_var("NEWENE"):
        new.init_var("NEWENE", ["node", "sector", "year"])
    if not new.has_var("EC"):
        new.init_var("EC", ["node", "year"])
    # calibration variables
    if not new.has_var("grow_calibrate"):
        new.init_var("grow_calibrate", ["node", "year"])
    if not new.has_var("aeei_calibrate"):
        new.init_var("aeei_calibrate", ["node", "sector", "year"])

    # ------------------------------------------------------------------------
    # save the ixDataStructure to the database

    new.commit(comment)

    # assign the just-uploaded datastructure as the "default version"
    new.set_as_default()

    # ------------------------------------------------------------------------
    # export the ixDataStructure to GAMS gdx, solve and import solution
    os.chdir(modelpath)
    new.solve(model="MESSAGE", case=newscenario)
