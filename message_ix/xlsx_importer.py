import pandas as pd
import numpy as np
import itertools
from itertools import product


def apply_filters(df, filters={}):
    """ Function that filters dataframe on specified values for given columns

    Parameters
    ----------
    df : dataframe
    filters : dictionary
        dictionary containing the column and then the respective entry for which the column should be filtered
        multiple columns can be added
        {'column_1': 'value_1', 'column_2': 'value_2'}


    Returns
    -------
    df : dataframe

    """
    rows = np.array([True] * len(df))
    for col, val in filters.items():
        if type(val) == str:
            rows = rows & (df[col] == val)
        else:
            rows = rows & (df[col].isin(val))
    return df[rows]


class init_model(object):
    """ Class 'init_model' contains all functions required to create a model.
    Includes functions to:
    1. Read input data
    2. Create scenario in the local database
    3. Add scenario metadata as well as basic set definitions
    4. Add demand data
    5. Add fossil resource data
    6. Add renewable resource data
    7. Add technology parameters
    8. Add relative soft constraints
    9. Add incovenience costs as generic relations
    10. Add final energy market penetrations while taking into account demand trajectories
    """

    def __init__(self, mp, filin, verbose, disp_error):
        """Initialize a new Python-class init_model

        Parameters
        ----------
        mp : Python-class 
            ixmp.Platform
        filin : string
            the name of the xlsx file (<file name>.xlsx) containg the model.scenario data
        verbose : boolean
            shows input data upon model creation 
        disp-error : boolean
            displays extended error reporting
        """
        self.mp = mp
        self.filin = filin
        self.verbose = verbose
        self.disp_error = disp_error

    def read_input(self):
        """ Read xlsx input file
        """
        xlsx = pd.ExcelFile(self.filin)
        self.meta = xlsx.parse('metadata', index_col=0)
        self.tecs = xlsx.parse('technologies')
        self.dems = xlsx.parse('demands')
        self.resources = xlsx.parse('resource')
        self.mpa_data = xlsx.parse('final_mpa')

        return(self.meta, self.tecs, self.dems, self.resources, self.mpa_data)

    def create_scen(self):
        """ Creates scenario
        """
        # Creates a new data structure based on model and scenario name
        model_nm = self.meta.loc['Model Name', 'Value']
        scen_nm = self.meta.loc['Scenario Name', 'Value']
        annot = self.meta.loc['Annotation', 'Value']
        self.scenario = self.mp.Scenario(
            model_nm, scen_nm, version='new', annotation=annot, scheme="MESSAGE")

        return(self.scenario, model_nm, scen_nm)

    def add_metadata(self):
        """ Adds scenario metadata and introduces model structure (levels, commodities grades etc.)
        1. Adds 'year'
        2. Adds 'firstmodelyear'
        3. Adds 'interestrate' 
        4. Adds regions and spatial mapping
        5. Adds 'mode'
        6. Adds 'units'
        7. Adds 'level'
        8. Adds all relevant sets for intermittent renewables using renewable resources
        9. Adds 'grade'
        10. Adds 'commodity'
        11. Adds 'technology'
        12. Adds 'emission'       
        """
        # Define the time periods included in the model
        self.horizon = [
            d for d in self.tecs.columns[self.tecs.columns.str.startswith(('1', '2'))]]
        self.scenario.add_set("year", self.horizon)
        print('Scenario years are\n', self.scenario.set(
            "year"), '\n') if self.verbose == True else 0

        # Define the first model year (this defines in which year the model starts the optimization)
        self.firstyear = self.meta.loc['First model year', 'Value']
        self.scenario.add_set("cat_year", ["firstmodelyear", self.firstyear])
        print('Scenario firstyear is\n', self.scenario.set(
            "cat_year"), '\n') if self.verbose == True else 0

        # Define the discount rate
        dr = [self.meta.loc['Discount rate', 'Value'] / 100.] * \
            len(self.horizon)
        dr_unit = [self.meta.loc['Discount rate', 'Units']] * len(self.horizon)
        self.scenario.add_par(
            "interestrate", key=self.horizon, val=dr, unit=dr_unit)
        print('Scenario discountrate is\n', self.scenario.par(
            "interestrate"), '\n') if self.verbose == True else 0

        # Defines the vintage years and corresponding activty years.
        # This is a preliminary solution as this doesnt take into account the technologies lifetime.
        # Despite having values, in the model, the activity per vintage is limited by its lifetime.
        self.vintage_years = pd.Series()
        for y_v in self.horizon:
            self.vintage_years[y_v] = [
                y_a for y_a in self.horizon if y_v <= y_a]

        # Define Regions
        regs = self.dems['Region'].unique().tolist()
        for reg in regs:
            self.scenario.add_set("node", reg)
            self.scenario.add_set("lvl_spatial", "country")
            self.scenario.add_set("map_spatial_hierarchy", [
                                  "country", reg, "World"])

        # Define Modes
        [self.scenario.add_set("mode", mode)
         for mode in self.tecs['Mode'].dropna().unique().tolist()]
        print('Scenario modes are\n', self.scenario.set(
            "mode"), '\n') if self.verbose == True else 0

        # Add unknown units
        for unit in [u for u in self.tecs['Units'].dropna().unique().tolist() + self.dems['Units'].dropna().unique().tolist() if u not in self.mp.units()]:
            self.mp.add_unit(
                unit, comment="Adding new unit required for India Model")

        # Define Levels
        all_levels = self.tecs['Level'].dropna().unique().tolist() \
            + self.dems['Level'].dropna().unique().tolist() \
            + self.resources['Level'].dropna().unique().tolist()
        self.scenario.add_set("level", all_levels)

        if 'resource' in self.scenario.set("level").tolist():
            # Assign resource level (all non-renewable levels)
            self.scenario.add_set("level_resource", ["resource"])
            print('Scenario levels are:\n', self.scenario.set(
                'level'), '\n') if self.verbose == True else 0

        if 'renewable' in self.scenario.set("level").tolist():
            # Assign renewable level
            self.scenario.add_set("level_renewable", ["renewable"])

        # Add penetration bins (ratings)
        ratings = self.scenario.add_set(
            'rating', self.tecs['Rating'].dropna().unique().tolist())
        print('Scenario penetration bins are:\n', self.scenario.set(
            "rating"), '\n') if self.verbose == True else 0

        # Adds resource grades
        self.scenario.add_set(
            "grade", self.resources['Grade'].dropna().unique().tolist())
        print('Scenario grades are:\n', self.scenario.set(
            "grade"), '\n') if self.verbose == True else 0

        # Define Commodities
        self.scenario.add_set("commodity", self.tecs['Commodity'].dropna().append(
            self.dems['Sector'].dropna()).append(self.resources['Commodity'].dropna()).unique().tolist())
        print('Scenario commodities are:\n', self.scenario.set(
            "commodity"), '\n') if self.verbose == True else 0

        # Define Technologies
        self.scenario.add_set(
            'technology', self.tecs['Technology'].dropna().unique().tolist())
        print('Sceanrio technologies are:\n', self.scenario.set(
            'technology'), '\n') if self.verbose == True else 0

        # Add emission species
        self.scenario.add_set(
            'emission', self.tecs['Species'].dropna().unique().tolist())
        print('Scenario emission species are:\n', self.scenario.set(
            "emission"), '\n') if self.verbose == True else 0

        return(self.horizon, self.vintage_years, self.firstyear)

    def demand_input_data(self, ap):
        """ Adds data for demands to scenario

        Parameter
        ---------

        ap: add_par class 
            contains all functions necessary to add data
        """
        ap.add_dem(self.dems)
        print('Scenario demands are:\n', self.scenario.par(
            "demand"), '\n') if self.verbose == True else 0

    def fossil_resource_input_data(self, ap):
        """ Adds data for fossil resources to scenario

        Parameter
        ---------

        ap: add_par class 
            contains all functions necessary to add data
        """
        rvol = apply_filters(self.resources, filters={
                             'Parameter': 'resource_volume'}).dropna(axis=1, how='all')
        rvol = rvol.rename(columns={rvol.columns[-1]: 'value'})
        ap.add_res_volume(rvol)
        print('Scenario resource volumes are:\n', self.scenario.par(
            "resource_volume"), '\n') if self.verbose == True else 0

        # Adds remaining resource constraint
        ap.add_rem_resources(apply_filters(self.resources, filters={
                             'Parameter': 'resource_remaining'}))
        print('Scenario remaining resources are:\n', self.scenario.par(
            "resource_remaining"), '\n') if self.verbose == True else 0

    def renewable_resource_input_data(self, ap):
        """ Function covers all necessary steps to add renewable resources

        Parameter
        ---------

        ap: add_par class 
            contains all functions necessary to add data

        Steps as follows:
        1. Updates 'type_tec' to include all intermittent renewable technologies.
#        2. Adds 'flexibility_factor'
#        3. Adds 'rating_bin' size
#        4. Adds 'reliability_factor' for different bins
#        5. Adds 'peak_load_factor'
        6. Adds 'renewable_potential'
        7. Adds 'renewable_capacity_factor' for the various potentials
        """

        # Define which technologies are "intermittent renewables"
        self.scenario.add_set('type_tec', ["renewable"])
        ren_tec = apply_filters(self.tecs, filters={'Level': 'renewable'})[
            'Technology'].unique().tolist()
        cat_tec = {"renewable": ren_tec}
        cat_tec = pd.DataFrame.from_dict(cat_tec).stack().reset_index(drop=False).rename(
            columns={'level_1': 'type_tec', 0: 'technology'})[['technology', 'type_tec']]
        self.scenario.add_set('cat_tec', cat_tec)

        # Adds potentials for renewables for every timestep in the model
        ren_pot = apply_filters(self.resources, filters={
                                'Parameter': 'renewable_potential'}).dropna(axis=1, how='all')
        ren_pot = ren_pot.rename(columns={ren_pot.columns[-1]: 'value'})
        ap.add_ren_pot(ren_pot)
        print(self.scenario.par('renewable_potential')
              ) if self.verbose == True else 0

        # Adds capacity factor for renewables for every timestep in the model
        ren_cpf = apply_filters(self.resources, filters={
                                'Parameter': 'renewable_capacity_factor'})
        ren_cpf = ren_cpf.dropna(axis=1, how='all')
        ren_cpf = ren_cpf.rename(columns={ren_cpf.columns[-1]: 'value'})
        ap.add_ren_cpf(ren_cpf)
        print(self.scenario.par('renewable_capacity_factor')
              ) if self.verbose == True else 0

    def technology_parameters(self, ap):
        """ Function covers all necessary steps to add renewable resources

        Parameter
        ---------

        ap: add_par class 
            contains all functions necessary to add data

        Steps as follows, adding:
        1. input (AT)
        2. output (AT)
        3. inv_cost (AT)
        4. var_cost (AT)
        5. fix_cost (AT)
        6. capacity factor (AT)
        7. technical_lifetime (AT)
        8. initial_new_capacity_up (currently excluded)
        9. growth_new_capacity_up (currently excluded)
        10. bound_new_capacity_up (AT)
        11. bound_new_capacity_lo (currently excluded)
        12. bound_total_capacity_up (currently excluded)
        13. bound_total_capacity_lo (currently excluded)
        14. initial_activity_up (AT)
        15. growth_activity_up (AT)
        16. initial_activity_lo (currently excluded)
        17. growth_activity_lo (currently excluded)
        18. bound_activity_lo (AT)   
        19. bound_activity_up (AT)
        20. historic_capacity (currently excluded)
        21. emission_factor (AT)

        """

        # Adds input level, commodity and efficiency for all technologies
        ap.add_tec_input(apply_filters(
            self.tecs, filters={'Parameter': 'input'}))
        print('Scenario inputs for technologies are:\n', self.scenario.par(
            "input"), '\n') if self.verbose == True else 0

        # Adds output level, commodity and efficiency for all technologies
        ap.add_tec_output(apply_filters(
            self.tecs, filters={'Parameter': 'output'}))
        print('Scenario outputs for technologies are:\n', self.scenario.par(
            "output"), '\n') if self.verbose == True else 0

        # Adds investment costs for all technologies
        ap.add_tec_inv(apply_filters(
            self.tecs, filters={'Parameter': 'inv_cost'}))
        print('Scenario investment costs for technologies are:\n',
              self.scenario.par("inv_cost"), '\n') if self.verbose == True else 0

        # Adds all variable costs for technologies
        ap.add_tec_varcost(apply_filters(
            self.tecs, filters={'Parameter': 'var_cost'}))
        print('Scenario variable O&M costs for technologies are:\n',
              self.scenario.par("var_cost"), '\n') if self.verbose == True else 0

        # Adds all fixed costs for technologies
        ap.add_tec_fixcost(apply_filters(
            self.tecs, filters={'Parameter': 'fix_cost'}))
        print('Scenario fixed costs for technologies are:\n', self.scenario.par(
            "fix_cost"), '\n') if self.verbose == True else 0

        # Adds capacity factors for all technologies
        ap.add_tec_plf(apply_filters(self.tecs, filters={
                       'Parameter': 'capacity_factor'}))
        print('Scenario capacity factors for technologies are:\n', self.scenario.par(
            "capacity_factor"), '\n') if self.verbose == True else 0

        # Adds lifetime for all technologies
        ap.add_tec_pll(apply_filters(self.tecs, filters={
                       'Parameter': 'technical_lifetime'}))
        print('Scenario lifetimes for technologies are:\n', self.scenario.par(
            "technical_lifetime"), '\n') if self.verbose == True else 0

        # Adds initial (start-up) value (capacity) for upper market penetration on capacity
        ap.add_tec_mpc_up_init(apply_filters(self.tecs, filters={
                               'Parameter': 'initial_new_capacity_up'}))
        print('Scenario initial new capacties up for technologies are:\n', self.scenario.par(
            "initial_new_capacity_up"), '\n') if self.verbose == True else 0

        # Adds annual growth rate (%) for upper market penetration on capacity
        ap.add_tec_mpc_up_gr(apply_filters(self.tecs, filters={
                             'Parameter': 'growth_new_capacity_up'}))
        print('Scenario capacity growth rates up for new technologies are:\n', self.scenario.par(
            "growth_new_capacity_up"), '\n') if self.verbose == True else 0

        # Adds upper bound on new installed capacity
        ap.add_tec_bdc_up(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_new_capacity_up'}))
        print('Scenario initial new capacity low for technologies are:\n', self.scenario.par(
            'bound_new_capacity_up'), '\n') if self.verbose == True else 0

        # Adds lower bound on new installed capacity
        ap.add_tec_bdc_lo(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_new_capacity_lo'}))
        print('Scenario capacity growth rates low for new technologies are:\n', self.scenario.par(
            'bound_new_capacity_lo'), '\n') if self.verbose == True else 0

        # Adds upper bound on new installed capacity
        ap.add_tec_bdi_up(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_total_capacity_up'}))
        print('Scenario bounds on total capacity up for new technologies are:\n', self.scenario.par(
            'bound_total_capacity_up'), '\n') if self.verbose == True else 0

        # Adds lower bound on new installed capacity
        ap.add_tec_bdi_lo(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_total_capacity_lo'}))
        print('Scenario bounds on total cpapcity low for new technologies are:\n', self.scenario.par(
            'bound_total_capacity_lo'), '\n') if self.verbose == True else 0

        # Adds initial (start-up) value (activty) for upper market penetration on activity
        ap.add_tec_mpa_up_init(apply_filters(self.tecs, filters={
                               'Parameter': 'initial_activity_up'}))
        print('Scenario initial activity up for new technologies are:\n', self.scenario.par(
            "initial_activity_up"), '\n') if self.verbose == True else 0

        # Adds annual growth rate (%) for upper market penetration on activity
        ap.add_tec_mpa_up_gr(apply_filters(self.tecs, filters={
                             'Parameter': 'growth_activity_up'}))
        print('Scenario activity growth rates up for new technologies are:\n',
              self.scenario.par("growth_activity_up"), '\n') if self.verbose == True else 0

        # Adds initial (start-up) value (activty) for upper market penetration on activity
        ap.add_tec_mpa_lo_init(apply_filters(self.tecs, filters={
                               'Parameter': 'initial_activity_lo'}))
        print('Scenario initial activity up for new technologies are:\n', self.scenario.par(
            "initial_activity_lo"), '\n') if self.verbose == True else 0

        # Adds annual growth rate (%) for upper market penetration on activity
        ap.add_tec_mpa_lo_gr(apply_filters(self.tecs, filters={
                             'Parameter': 'growth_activity_lo'}))
        print('Scenario activity growth rates up for new technologies are:\n',
              self.scenario.par("growth_activity_lo"), '\n') if self.verbose == True else 0

        # Adds lower bound on technology activity
        ap.add_tec_bda_lo(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_activity_lo'}))
        print('Scenario bounds on activity low for technologies are:\n', self.scenario.par(
            'bound_activity_lo'), '\n') if self.verbose == True else 0

        # Adds upper bound on technology activity
        ap.add_tec_bda_up(apply_filters(self.tecs, filters={
                          'Parameter': 'bound_activity_up'}))
        print('Scenario bouns on activity up for technologies are:\n', self.scenario.par(
            'bound_activity_up'), '\n') if self.verbose == True else 0

        # Adds historic installed capacity for technologies
        ap.add_tec_hisc(apply_filters(self.tecs, filters={
                        'Parameter': 'historic_capacity'}))
        print('Scenario historical new capacities for technologoies are:\n', self.scenario.par(
            'historical_new_capacity'), '\n') if self.verbose == True else 0

        # Adds emission factors for technologies
        ap.add_tec_emi_fac(apply_filters(self.tecs, filters={
                           'Parameter': 'emission_factor'}))
        print('Scenario emission factors for technologies are:\n', self.scenario.par(
            'emission_factor'), '\n') if self.verbose == True else 0

        # Define the flexibility for various powerplants
        ap.add_tec_flex(apply_filters(self.tecs, filters={
                        'Parameter': 'flexibility_factor'}))
        print(self.scenario.par("flexibility_factor")
              ) if self.verbose == True else 0

        # Adds the "bin" size for technologies
        ap.add_bin_size(apply_filters(
            self.tecs, filters={'Parameter': 'rating_bin'}))
        print(self.scenario.par("rating_bin")) if self.verbose == True else 0

        # Adds the "bin" reliability factor
        ap.add_bin_reliability(apply_filters(self.tecs, filters={
                               'Parameter': 'reliability_factor'}))
        print(self.scenario.par("reliability_factor")
              ) if self.verbose == True else 0

        # Adds peak load factor
        ap.add_peak_load(apply_filters(self.tecs, filters={
                         'Parameter': 'peak_load_factor'}))
        print(self.scenario.par('peak_load_factor')
              ) if self.verbose == True else 0

    def rel_soft_constraints(self, mpalo=None, mpaup=None, mpclo=None, mpcup=None):
        """ Adds relative soft constraints"

        Parameter
        ---------

        mpalo : list
            parameters for adding soft_growth_activity_lo to all technologies with growth_activity_lo
            [<% relaxation>,<% of LCOE>]
        mpaup : list
            parameters for adding soft_growth_activity_up to all technologies with growth_activity_up
            [<% relaxation>,<% of LCOE>]
        mpclo : list
            parameters for adding soft_growth_new_capacity_lo to all technologies with growth_new_capacity_lo
            [<% relaxation>,<% of LCOE>]
        mpcup : list
            parameters for adding soft_growth_new_capacity_up to all technologies with growth_new_capacity_up
            [<% relaxation>,<% of LCOE>]
        """

        # Add soft_growth_activity_lo
        if mpalo:
            for n in mpalo:
                assert type(n) is float, 'Value is not a float'
            assert mpalo[0] <= 0.0, 'Value is greater/equal 0'
            assert mpalo[1] >= 0.0, 'Relative costs is smaller/equal 0'

            # Step 1. - Retrieve all growthrates (mpa) on activity lo
            relcostsoftmpalo = softmpalo = self.scenario.par(
                'growth_activity_lo')
            # Step 2. - Add generic 5% +/-
            softmpalo.loc[:, 'value'] = mpalo[0]
            self.scenario.add_par('soft_activity_lo', softmpalo)
            # Step 3. - Set costs relative to lev. costs 50%
            relcostsoftmpalo.loc[:, 'value'] = mpalo[1]
            self.scenario.add_par(
                'level_cost_activity_soft_lo', relcostsoftmpalo)

        # Add soft_growth_activity_up
        if mpaup:
            for n in mpaup:
                assert type(n) is float, 'Value is not a float'
            assert mpaup[0] >= 0.0, 'Value is smaller/equal 0'
            assert mpaup[1] >= 0.0, 'Relative costs is smaller/equal 0'

            relcostsoftmpaup = softmpaup = self.scenario.par(
                'growth_activity_up')
            softmpaup.loc[:, 'value'] = mpaup[0]
            self.scenario.add_par('soft_activity_up', softmpaup)
            relcostsoftmpaup.loc[:, 'value'] = mpaup[1]
            self.scenario.add_par(
                'level_cost_activity_soft_up', relcostsoftmpaup)

        # Add soft_growth_new_capacity_lo
        if mpclo:
            for n in mpclo:
                assert type(n) is float, 'Value is not a float'
            assert mpclo[0] <= 0.0, 'Value is greater/equal 0'
            assert mpclo[1] >= 0.0, 'Relative costs is smaller/equal 0'

            relcostsoftmpclo = softmpclo = self.scenario.par(
                'growth_new_capacity_lo')
            softmpclo.loc[:, 'value'] = mpclo[0]
            self.scenario.add_par('soft_new_capacity_lo', softmpclo)
            relcostsoftmpclo.loc[:, 'value'] = mpclo[1]
            self.scenario.add_par('level_cost_new_capacity_soft_lo',
                                  relcostsoftmpclo)

        # Add soft_growth_new_capacity_up
        if mpcup:
            for n in mpcup:
                assert type(n) is float, 'Value is not a float'
            assert mpcup[0] >= 0.0, 'Value is smaller/equal 0'
            assert mpcup[1] >= 0.0, 'Relative costs is smaller/equal 0'

            relcostsoftmpcup = softmpcup = self.scenario.par(
                'growth_new_capacity_up')
            softmpcup.loc[:, 'value'] = mpcup[0]
            self.scenario.add_par('soft_new_capacity_up', softmpcup)
            relcostsoftmpcup.loc[:, 'value'] = mpcup[1]
            self.scenario.add_par('level_cost_new_capacity_soft_up',
                                  relcostsoftmpcup)

    def inconvenience_costs(self):
        """ Adds invonvenience costs in the form of a generic relation
        """
        acty = [y for y in self.horizon if int(y) >= self.firstyear]
        inconvc = apply_filters(
            self.tecs, filters={'Parameter': 'inconv_cost'})
        for (idx, row), yr in itertools.product(inconvc.iterrows(), self.horizon):
            # Defines name of relation
            rel = 'inconv_{}'.format(row['Technology'])

            # Adds new relation to scenario
            if rel not in self.scenario.set('relation'):
                self.scenario.add_set("relation", rel)

            # Add costs for relation
            par = pd.DataFrame({
                'node_rel': row['Region'],
                'relation': rel,
                'year_rel': [yr],
                'value': row[yr],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("relation_cost", par)

            # Adds technology entry into relation
            par = pd.DataFrame({
                'relation': rel,
                'node_rel': row['Region'],
                'year_rel': [yr],
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_act': [yr],
                'mode': row['Mode'],
                'unit': '%',
                        'value': [1.0]
            })
            self.scenario.add_par("relation_activity", par)

    def final_energy_mpa(self, mpa_gen):
        """ Adds lower/upper market pentrations constraints

        Parameters
        ----------

        mpa_gen : boolean/integer
            if set to False, no market pentration constraints will be added, otherwise
            the integer provided specifies the year as of which the constraints are added.
        """
        # Checks whether the year defined for the generation of the mpas is defined
        assert str(mpa_gen) in self.scenario.set(
            'year').values, 'Year as of which mpas should be generated is not defined as a year in the model'

        # Checks whether all technologies contained in the mpalo parameterization are also contained within the model
        tec_excl = self.mpa_data[~self.mpa_data['Technology'].isin(
            self.scenario.set('technology'))]['Technology'].values
        mpa_data = self.mpa_data[~self.mpa_data['Technology'].isin(tec_excl)]
        print(tec_excl, 'have been omitted') if not tec_excl else None

        # Retrieves demands
        demands = self.scenario.par('demand').pivot(
            index='commodity', columns='year', values='value')

        # Part 1: Ensure that all technologies use the correct demands

        # Add routine to distinguish between technologies which do not deliver directly onto demands
        # Step 1 - filter all technologies that deliver onto demands
        useful_tec = self.scenario.par('output', filters={'level': ['useful']})[
            'technology'].unique().tolist()
        # Step 2 - retrieve the inputs of these technologies
        useful_src = self.scenario.par(
            'input', filters={'technology': useful_tec})
        # Step 3 - filter out any technologies which do not deliver onto level: final
        # For all technologies that deliver onto useful energy, but that do not source their energy from the final level,
        # the demands recalculated for each source using the input efficiency.
        # e.g. p_transport_road demand is in bpkm.
        #      large_vehicle_road and small_vehicle_road both deliver onto this demand but have a conversion factor
        #      to convert from bvkm to bpkm. The demands are therefore recalculated and assigned to large_vehicle_road
        #      and small_vehicle_road. These are used to generate the mpa_lo/up for the technologies delivering on these
        #      two technologies.
        #      If there is a bda_lo for all years, then this is used to calculate the mpa_lo/up
        alt_final_tec = useful_src[useful_src['level'] != 'final']
        if not alt_final_tec.empty:
            # Map technolgoies with intermediate final outputs to the relevant input commodities
            mapping_comm2ut = alt_final_tec[[
                'commodity', 'technology']].drop_duplicates().set_index('commodity')
            # Filter out unique entries per technology and vintage
            alt_final_tec = alt_final_tec.groupby(
                ['technology', 'year_vtg']).first().reset_index()
            # Arrange so these can be used to recalculate the demands
            alt_final_tec = alt_final_tec.pivot(
                index='commodity', columns='year_act', values='value')

            for ut in alt_final_tec.index:
                check = 0
                # Retrieves technology bda_lo
                ut_bda_lo = self.scenario.par('bound_activity_lo', filters={
                    'technology': mapping_comm2ut.loc[ut]['technology']})

                # Checks to see if bda_lo is defined for entire time horizon
                if not ut_bda_lo.empty:
                    yrs_bda_lo = [y for y in [int(h) for h in self.horizon if int(h) >= int(self.firstyear)] if y not in
                                  [y for y in ut_bda_lo.loc[:, 'year_act']]]
                    if yrs_bda_lo:
                        check = 1
                        print('re-calculating demands, but not applying bda_lo as not defined for all yrs. Missing for:',
                              yrs_bda_lo)

                if not ut_bda_lo.empty and not check:
                    print('re-calcualting demands based on bda_lo for sector',
                          mapping_comm2ut.loc[ut]['technology'])
                    ut_bda_lo = ut_bda_lo.pivot(
                        index='technology', columns='year_act', values='value').reset_index()
                    ut_bda_lo['technology'] = ut
                    # mutliplies demand (bda_lo) by efficiency
                    ut_new_dem = ut_bda_lo.set_index(
                        'technology').multiply(alt_final_tec).dropna()
                    for col in ut_new_dem.columns:
                        ut_new_dem = ut_new_dem.rename(columns={col: int(col)})
                    demands = pd.concat([demands, ut_new_dem])
                else:
                    # Filter demand to be multiplied by input coefficient
                    tmp = demands.reset_index()
                    tmp = tmp[tmp['index'] == ut].set_index('index')
                    tmp = tmp.multiply(alt_final_tec).dropna()
                    for col in tmp.columns:
                        tmp = tmp.rename(columns={col: int(col)})
                    demands = tmp.combine_first(demands)

        # Part 2: Calculate the annual growth rates for different demands

        def CAGR(first, last, periods):
            vals = (last / first)**(1 / periods)
            vals = vals.rename(last.name)
            return vals

        # Calculates annual growth rate
        dem_gr = demands.copy()
        dem_gr = dem_gr.apply(lambda x: x if int(x.name) < mpa_gen else CAGR(
            demands[demands.reset_index().columns[int(demands.reset_index().columns.get_loc(x.name)) - 1]], x, 5))

        # Part 3: Calcualte mpa_lo/up

        # Routine passes over individual demands
        for tec in mpa_data['Technology'].tolist():
            # Filter for correct mpa generation input parameters
            tec_mpa = apply_filters(mpa_data, filters={'Technology': tec})
            # Retrieve the output parameters
            tec_out = self.scenario.par('output', filters={'technology': tec})
            # Retrieve the level name onto which the technology delivers
            tec_lvl = tec_out['level'].unique()[0]
            # Retrieve the name of the demand
            tec_com = tec_out['commodity'].unique()[0]
            # Selects correct demand
            tec_dem_gr = dem_gr.loc[tec_com]
            # Selects correct demand growth rate
            tec_dem = demands.loc[tec_com]
            yr = tec_dem_gr.index
            for i in range(len(yr)):
                if yr[i] < mpa_gen:
                    continue
                # The mpa_lo is the lower of either:
                #    a. the predefined growth rate (1+mpa_lo)
                #    b. the agr of the demand + the predefined growth rate
                # This ensures that with a steep decline of demand, that the technology can phase out fast enough
                # The same applies for the mpa_up, but in the opposite direction
                mpa_lo = min(
                    1 + tec_mpa.iloc[0]['mpa_lo'], tec_dem_gr[yr[i]] + tec_mpa.iloc[0]['mpa_lo'])
                mpa_up = max(min(1 + tec_mpa.iloc[0]['mpa_up'], tec_dem_gr[yr[i]] + tec_mpa.iloc[0]
                                 ['mpa_up']), (tec_dem_gr[yr[i]] + tec_mpa.iloc[0]['mpa_up']) / 2)
                startup_lo = ((mpa_lo - 1) * tec_mpa.iloc[0]['startup_lo'] * tec_dem[yr[i]]) / (
                    mpa_lo**(yr[i] - yr[i - 1]) - 1)
                startup_up = ((mpa_up - 1) * tec_mpa.iloc[0]['startup_up'] * tec_dem[yr[i]]) / (
                    mpa_up**(yr[i] - yr[i - 1]) - 1)
                # mpa_lo and mpa_up need to have 1 subtracted for entry into messageix
                mpa_lo = mpa_lo - 1
                mpa_up = mpa_up - 1
                par_mpa_lo = pd.DataFrame({
                    'node_loc': tec_out['node_loc'].unique()[0],
                    'time': 'year',
                    'unit': '%',
                    'year_act': yr[i],
                    'technology': tec,
                    'mode': tec_out['mode'].unique()[0],
                    'value': [mpa_lo]})
                self.scenario.add_par('growth_activity_lo', par_mpa_lo)
                par_mpa_up = pd.DataFrame({
                    'node_loc': tec_out['node_loc'].unique()[0],
                    'time': 'year',
                    'unit': '%',
                    'year_act': yr[i],
                    'technology': tec,
                    'mode': tec_out['mode'].unique()[0],
                    'value': [mpa_up]})
                self.scenario.add_par('growth_activity_up', par_mpa_up)
                par_startup_lo = pd.DataFrame({
                    'node_loc': tec_out['node_loc'].unique()[0],
                    'time': 'year',
                    'unit': 'GWa',
                    'year_act': yr[i],
                    'technology': tec,
                    'value': [startup_lo]})
                self.scenario.add_par('initial_activity_lo', par_startup_lo)
                par_startup_up = pd.DataFrame({
                    'node_loc': tec_out['node_loc'].unique()[0],
                    'time': 'year',
                    'unit': 'GWa',
                    'year_act': yr[i],
                    'technology': tec,
                    'value': [startup_up]})
                self.scenario.add_par('initial_activity_up', par_startup_up)


class add_par(object):

    def __init__(self, scenario, horizon, vintage_years, firstyear, disp_error):
        """ Initialize Python-class add_par

        Parameters
        ----------
        scenario : ixmp.Sceanrio
        horizon : list
            model years
        vintage_years : list
            vintage years and corresponding activity years 
        firstyear : integer
            first model year
        disp-error : boolean
            displays extended error reporting
        """
        self.scenario = scenario
        self.horizon = horizon
        self.vintage_years = vintage_years
        self.firstyear = firstyear
        self.disp_error = disp_error

    def add_dem(self, df):
        """ Adds parameter demand to the datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing demands

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            if yr in df.columns:
                par = pd.DataFrame({
                    'node': row['Region'],
                    'commodity': row['Sector'],
                    'level': row['Level'],
                    'year': [yr],
                    'time': 'year',
                    'value': row[yr],
                    'unit': row['Units']
                })
                if par.isnull().values.any():
                    print("Cannot add parameter containing 'NaN'\n",
                          par) if self.disp_error == True else 0
                else:
                    self.scenario.add_par("demand", par)

    def add_res_volume(self, df):
        """ Adds resource parameter resource volume to the datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing resource volume

        """
        for (idx, row) in df.iterrows():
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'grade': row['Grade'],
                'value': [row['value']],
                'unit': row['Units']
            })
            self.scenario.add_par("resource_volume", par)

    def add_rem_resources(self, df):
        """ Adds resource parameter remaining resource to the datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing remaining resource data over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            if yr in df.columns:
                par = pd.DataFrame({
                    'node': row['Region'],
                    'commodity': row['Commodity'],
                    'grade': row['Grade'],
                    'value': row[yr],
                    'unit': row['Units'],
                    'year': [yr]
                })
                self.scenario.add_par("resource_remaining", par)

    def add_tec_input(self, df):
        """ Adds technology parameter input to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology inputs over time and vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            if not np.isnan(row['Region_IO']) and row['Region_IO'] != row['Region']:
                par = pd.DataFrame({
                    'node_loc': row['Region'],
                    'node_origin': row['Region_IO'],
                    'level': row['Level'],
                    'commodity': row['Commodity'],
                    'year_vtg': yr,
                    'year_act': self.vintage_years[yr],
                    'time': 'year',
                    'time_origin': 'year',
                    'technology': row['Technology'],
                    'value': row[yr],
                    'mode': row['Mode'],
                    'unit': row['Units']
                })
            else:
                par = pd.DataFrame({
                    'node_loc': row['Region'],
                    'node_origin': row['Region'],
                    'level': row['Level'],
                    'commodity': row['Commodity'],
                    'year_vtg': yr,
                    'year_act': self.vintage_years[yr],
                    'time': 'year',
                    'time_origin': 'year',
                    'technology': row['Technology'],
                    'value': row[yr],
                    'mode': row['Mode'],
                    'unit': row['Units']
                })
            if par.isnull().values.any():
                print("Cannot add parameter input containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("input", par)

    def add_tec_output(self, df):
        """ Adds technology parameter output to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology outputs over time and vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            if not np.isnan(row['Region_IO']) and row['Region_IO'] != row['Region']:
                par = pd.DataFrame({
                    'node_loc': row['Region'],
                    'node_dest': row['Region_IO'],
                    'level': row['Level'],
                    'commodity': row['Commodity'],
                    'year_vtg': yr,
                    'year_act': self.vintage_years[yr],
                    'time': 'year',
                    'time_dest': 'year',
                    'technology': row['Technology'],
                    'value': row[yr],
                    'mode': row['Mode'],
                    'unit': row['Units']
                })
            else:
                par = pd.DataFrame({
                    'node_loc': row['Region'],
                    'node_dest': row['Region'],
                    'level': row['Level'],
                    'commodity': row['Commodity'],
                    'year_vtg': yr,
                    'year_act': self.vintage_years[yr],
                    'time': 'year',
                    'time_dest': 'year',
                    'technology': row['Technology'],
                    'value': row[yr],
                    'mode': row['Mode'],
                    'unit': row['Units']
                })
            if par.isnull().values.any():
                print("Cannot add parameter output containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("output", par)

    def add_tec_inv(self, df):
        """ Adds technology parameter investment costs to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology investment costs per vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': [yr],
                'value': row[yr],
                'technology': row['Technology'],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter inv_cost containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("inv_cost", par)

    def add_tec_varcost(self, df):
        """ Adds technology parameter variable costs to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology variable costs over time and vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': yr,
                'year_act': self.vintage_years[yr],
                'mode': row['Mode'],
                'time': 'year',
                'value': row[yr],
                'technology': row['Technology'],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter var_cost containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("var_cost", par)

    def add_tec_fixcost(self, df):
        """ Adds technology parameter fixed costs to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology variable costs over time and vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': yr,
                'year_act': self.vintage_years[yr],
                'value': row[yr],
                'technology': row['Technology'],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter fix_cost containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par("fix_cost", par)

    def add_tec_plf(self, df):
        """ Adds technology parameter capacity/plant factor to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology capacity/plant factor

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': yr,
                'year_act': self.vintage_years[yr],
                'time': 'year',
                'value': row[yr],
                'technology': row['Technology'],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter capacity_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('capacity_factor', par)

    def add_tec_pll(self, df):
        """ Adds technology parameter lifetime to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing technology lifetime per vintage

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': [yr],
                'technology': row['Technology'],
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter technical_lifetime containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('technical_lifetime', par)

    def add_tec_mpc_up_init(self, df):
        """ Adds technology parameter initial/start-up value for dynamic upper bound on capacity (mpc up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing initial/start-up value for dynamic upper bound on capacity (mpc up) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_vtg': [yr],
                'value': row[yr],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter initial_new_capacity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('initial_new_capacity_up', par)

    def add_tec_mpc_up_gr(self, df):
        """ Adds technology parameter growth rate for dynamic upper bound on capacity (mpc up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing growth rate for dynamic upper bound on capacity (mpc up) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_vtg': [yr],
                'value': row[yr],
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter growth_new_capacity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('growth_new_capacity_up', par)

    def add_tec_bdc_up(self, df):
        """ Adds technology parameter upper bound on new capacity (bdc up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing upper bound on new capacity (bdc up) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'unit': row['Units'],
                'year_vtg': [yr],
                'technology': row['Technology'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_new_capacity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_new_capacity_up', par)

    def add_tec_bdc_lo(self, df):
        """ Adds technology parameter lower bound on new capacity (bdc lo) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing lower bound on new capacity (bdc lo) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'unit': row['Units'],
                'year_vtg': [yr],
                'technology': row['Technology'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_new_capacity_lo containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_new_capacity_lo', par)

    def add_tec_bdi_up(self, df):
        """ Adds technology parameter upper bound on total capacity (bdi up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing upper bound on total capacity (bdi up) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'unit': row['Units'],
                'year_act': [yr],
                'technology': row['Technology'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_total_capacity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_total_capacity_up', par)

    def add_tec_bdi_lo(self, df):
        """ Adds technology parameter lower bound on total capacity (bdi lo) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing lower bound on total capacity (bdi lo) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'unit': row['Units'],
                'year_act': [yr],
                'technology': row['Technology'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_total_capacity_lo containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_total_capacity_lo', par)

    def add_tec_bda_up(self, df):
        """ Adds technology parameter upper bound on new activity (bda up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing upper bound on new activity (bda up) over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'time': 'year',
                'unit': row['Units'],
                'year_act': [yr],
                'technology': row['Technology'],
                'mode': row['Mode'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_activity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_activity_up', par)

    def add_tec_bda_lo(self, df):
        """ Adds technology parameter lower bound on new activity (bda lo) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing lower bound on new activity (bda lo)

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'time': 'year',
                'unit': row['Units'],
                'year_act': [yr],
                'technology': row['Technology'],
                'mode': row['Mode'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter bound_activity_lo containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('bound_activity_lo', par)

    def add_tec_mpa_up_init(self, df):
        """ Adds technology parameter initial/start-up value for dynamic upper bound on activity (mpa up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing initial/start-up value for dynamic upper bound on activity (mpa up)

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_act': [yr],
                'value': row[yr],
                'time': 'year',
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter initial_activity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('initial_activity_up', par)

    def add_tec_mpa_up_gr(self, df):
        """ Adds technology parameter growth rate for dynamic upper bound on activity (mpa up) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing growth rate for dynamic upper bound on activity (mpa up)

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_act': [yr],
                'value': row[yr],
                'time': 'year',
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter growth_activity_up containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('growth_activity_up', par)

    def add_tec_mpa_lo_init(self, df):
        """ Adds technology parameter initial/start-up value for dynamic lower bound on activity (mpa lo) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing initial/start-up value for dynamic lower bound on activity (mpa lo)

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_act': [yr],
                'value': row[yr],
                'time': 'year',
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter initial_activity_lo containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('initial_activity_lo', par)

    def add_tec_mpa_lo_gr(self, df):
        """ Adds technology parameter growth rate for dynamic lower bound on activity (mpa lo) to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing growth rate for dynamic lower bound on activity (mpa lo)

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_act': [yr],
                'value': row[yr],
                'time': 'year',
                'unit': row['Units']
            })
            if par.isnull().values.any():
                print("Cannot add parameter growth_activity_lo containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('growth_activity_lo', par)

    def add_tec_hisc(self, df):
        """ Adds technology parameter historic new installed capacity to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing historic new installed capacity over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'year_vtg': [yr],
                'technology': row['Technology'],
                'unit': row['Units'],
                'value': [row[yr]]
            })
            if par.isnull().values.any():
                print("Cannot add parameter historical_new_capacity containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('historical_new_capacity', par)

    def add_tec_flex(self, df):
        """ Adds technology parameter flexibility to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing flexibility over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'commodity': row['Commodity'],
                'level': row['Level'],
                'mode': row['Mode'],
                'rating': row['Rating'],
                'year_act': self.vintage_years[yr],
                'year_vtg': yr,
                'technology': row['Technology'],
                'time': 'year',
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter flexibility_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('flexibility_factor', par)

    def add_bin_size(self, df):
        """ Adds bin parameter potential/size to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing bin parameter potential/size over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'level': row['Level'],
                'rating': row['Rating'],
                'year_act': [yr],
                'technology': row['Technology'],
                'time': 'year',
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter rating_bin containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('rating_bin', par)

    def add_bin_reliability(self, df):
        """ Adds bin parameter reliability to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing bin reliability factors over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'level': row['Level'],
                'rating': row['Rating'],
                'year_act': [yr],
                'technology': row['Technology'],
                'time': 'year',
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter reliability_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('reliability_factor', par)

    def add_peak_load(self, df):
        """ Adds technology parameter peak_load_factor to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing peak_load_factor over time

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'level': row['Level'],
                'year': [yr],
                'time': 'year',
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter peak_load_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('peak_load_factor', par)

    def add_ren_pot(self, df):
        """ Adds potential of different renewable resources to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing potential of different renewable resources

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'grade': row['Grade'],
                'level': row['Level'],
                'year': [yr],
                'unit': row['Units'],
                'value': row['value']
            })
            if par.isnull().values.any():
                print("Cannot add parameter renewable_potential containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('renewable_potential', par)

    def add_ren_cpf(self, df):
        """ Adds capacitiy factor for different renewable resources to datastructure

        Parameters
        ----------
        df : dataframe
            dataframe containing capacitiy factor for different renewable resources

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node': row['Region'],
                'commodity': row['Commodity'],
                'grade': row['Grade'],
                'level': row['Level'],
                'year': [yr],
                'unit': row['Units'],
                'value': row['value']
            })
            if par.isnull().values.any():
                print("Cannot add parameter renewable_capacity_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('renewable_capacity_factor', par)

    def add_upper_share(self, df):
        """ Adds a set of relations and technologies to the datastructure required to make share constraints

        Parameters
        ----------
        df : dataframe
            dataframe containing all shares which should be added to the model

        """
        for share in df['Parameter'].dropna().unique().tolist():
            for reg in df['Region'].dropna().unique().tolist():
                # Adds share useful energy cooking, which limits the contribution of a certain source to a maximum share.
                sub_df = apply_filters(
                    df, filters={'Parameter': share, 'Region': reg})

                # Adds relations for each of the technologies which are part of the share constraint
                self.scenario.add_set("relation", ['{}_{}'.format(r, share) for r in sub_df['Technology'].dropna().unique().tolist()]
                                      + [share])
                self.scenario.add_set("technology", share)

                for (idx, row), yr in itertools.product(sub_df.iterrows(), self.horizon):
                    if np.isnan(row[yr]):
                        continue
                    # Sets the relation_upper to 0 for all technology specific relations
                    par = pd.DataFrame({
                        'relation': '{}_{}'.format(row['Technology'], share),
                        'node_rel': row['Region'],
                        'year_rel': [yr],
                        'unit': '%',
                        'value': [0.0]
                    })
                    if par.isnull().values.any():
                        print("Cannot add parameter relation_upper containing 'NaN'\n",
                              par) if self.disp_error == True else 0
                    else:
                        self.scenario.add_par("relation_upper", par)

                    # Sets the technology entry into the technology specific relation to 1
                    par = pd.DataFrame({
                        'relation': '{}_{}'.format(row['Technology'], share),
                        'node_rel': row['Region'],
                        'year_rel': [yr],
                        'node_loc': row['Region'],
                        'technology': row['Technology'],
                        'year_act': [yr],
                        'mode': row['Mode'],
                        'unit': '%',
                        'value': [1.0]
                    })
                    if par.isnull().values.any():
                        print("Cannot add parameter relation_activity containing 'NaN'\n",
                              par) if self.disp_error == True else 0
                    else:
                        self.scenario.add_par("relation_activity", par)

                   # Sets the entry into the technology specific relation to 1
                    par = pd.DataFrame({
                        'relation': share,
                        'node_rel': row['Region'],
                        'year_rel': [yr],
                        'node_loc': row['Region'],
                        'technology': row['Technology'],
                        'year_act': [yr],
                        'mode': row['Mode'],
                        'unit': '%',
                        'value': [1.0]
                    })
                    if par.isnull().values.any():
                        print("Cannot add parameter relation_activity containing 'NaN'\n",
                              par) if self.disp_error == True else 0
                    else:
                        self.scenario.add_par("relation_activity", par)

                   # Sets the entry into the technology specific relation to 1
                    par = pd.DataFrame({
                        'relation': '{}_{}'.format(row['Technology'], share),
                        'node_rel': row['Region'],
                        'year_rel': [yr],
                        'node_loc': row['Region'],
                        'technology': share,
                        'year_act': [yr],
                        'mode': 'standard',
                        'unit': '%',
                        'value': row[yr] * -1
                    })
                    if par.isnull().values.any():
                        print("Cannot add parameter relation_activity containing 'NaN'\n",
                              par) if self.disp_error == True else 0
                    else:
                        self.scenario.add_par("relation_activity", par)

                # Sets relation_upper and relation_lower for overarching constraint
                par = pd.DataFrame({
                    'relation': share,
                    'node_rel': reg,
                    'year_rel': self.horizon,
                    'unit': '%',
                    'value': 0.0
                })
                self.scenario.add_par("relation_upper", par)
                self.scenario.add_par("relation_lower", par)

                par = pd.DataFrame({
                    'relation': share,
                    'node_rel': reg,
                    'year_rel': self.horizon,
                    'node_loc': reg,
                    'technology': share,
                    'year_act': self.horizon,
                    'mode': row['Mode'],
                    'unit': '%',
                    'value': -1
                })
                self.scenario.add_par("relation_activity", par)

    def add_tec_emi_fac(self, df):
        """ Adds emission factors for technologies over time

        Parameters
        ----------
        df : dataframe
            dataframe containing emission factors for different technologies

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'technology': row['Technology'],
                'year_vtg': yr,
                'year_act': self.vintage_years[yr],
                'mode': row['Mode'],
                'emission': row['Species'],
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter emission_factor containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('emission_factor', par)

    def add_addon_conversion(self, df):
        """ Adss conversion factor for addon technologies over time

        Parameters
        ----------
        df : dataframe
            dataframe containing conversion factors for the linking parent and addon technologies

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'addon': row['Technology'],
                'technology': row['Parent_technology'],
                'year_vtg': yr,
                'year_act': self.vintage_years[yr],
                'mode': row['Mode'],
                'time': 'year',
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter addon_conversion containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('addon_conversion', par)

    def add_addon_minimum(self, df):
        """ Adss conversion factor for addon technologies over time

        Parameters
        ----------
        df : dataframe
            dataframe containing conversion factors for the linking parent and addon technologies

        """
        for (idx, row), yr in itertools.product(df.iterrows(), self.horizon):
            par = pd.DataFrame({
                'node_loc': row['Region'],
                'tec': row['Technology'],
                #'year_vtg': yr,
                #'year_act': self.vintage_years[yr],
                'year_act': [yr],
                'mode': row['Mode'],
                'time': 'year',
                'type_addon': row['Type_addon'],
                'unit': row['Units'],
                'value': row[yr]
            })
            if par.isnull().values.any():
                print("Cannot add parameter addon_minimum containing 'NaN'\n",
                      par) if self.disp_error == True else 0
            else:
                self.scenario.add_par('addon_minimum', par)
