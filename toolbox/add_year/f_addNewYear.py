# -*- coding: utf-8 -*-
"""
Description:
    This functionality adds new time steps to an existing MESSAGE scenario
    (hereafter "reference scenario"). This is done by creating a new empty
    scenario (hereafter "new scenario") and:
    - Copying all sets from reference scenario and adding new time steps to
    relevant sets (e.g., adding 2025 between 2020 and 2030 in the set "year")
    - Copying all parameters from reference scenario, adding new time steps to
    relevant parameters, calculating missing values for the added time steps.

Sections of this code:
    I. Required python packages are imported and ixmp platform loaded.
    II. Generic utilities for dataframe manipulation
    III. The main class called "addNewYear"
    IV. Submodule "addSets" for adding and modifying the sets
    V. Submodule "addPar" for copying and modifying each parameter
    VI. The submodule "addPar" calls two utility functions ("df_interpolate"
    and "df_interpolate_2D") for calculating missing values.
    VII. Code for running the script as "main"


Usage:
    This script can be used either:
    A) By running directly from the command line, example:
    ---------------------------------------------------------------------------
    python f_addNewYear.py --model_ref "MESSAGE_Model" --scen_ref "baseline"
    --years_new "[2015,2025,2035,2045]"
    ---------------------------------------------------------------------------
    (Other input arguments are optional. For more info see Section V below.)

    B) By calling the class "addNewYear" from other python scripts
"""
# %% I) Importing required packages and loading ixmp platform

import numpy as np
import pandas as pd
from timeit import default_timer as timer
import argparse
import ixmp as ix
import message_ix

mp = ix.Platform(dbtype='HSQLDB')      # Loading ixmp Platform

# %% II) Required utility functions for dataframe manupulation
# II.A) Utility function for interpolation/extrapolation of two numbers,
# lists or series (x: time steps, y: data points)


def intpol(y1, y2, x1, x2, x):
    if x2 == x1 and y2 != y1:
        print('>>> Warning <<<: No difference between x1 and x2,' +
              'returned empty!!!')
        return []
    elif x2 == x1 and y2 == y1:
        return y1
    else:
        y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
        return y

# II.B) Utility function for slicing a MultiIndex dataframe and
# setting a value to a specific level
# df: dataframe, idx: list of indexes, level: string, locator: list,
# value: integer/string


def f_slice(df, idx, level, locator, value):
    if locator:
        df = df.reset_index().loc[df.reset_index()[level].isin(locator)].copy()
    else:
        df = df.reset_index().copy()
    if value:
        df[level] = value
    return df.set_index(idx)

# II.C) A function for creating a mask for removing extra values from a
# dataframe


def f_mask(df, index, count, value):
    df.loc[index, df.columns > (df.loc[[index]].notnull().cumsum(
        axis=1) == count).idxmax(axis=1).values[0]] = value

# II.D) Function for unifroming the "unit" in different years to prevent
# mistakes in indexing and grouping


def unit_uniform(df):
    column = [x for x in df.columns if x in ['commodity', 'emission']]
    if column:
        com_list = set(df[column[0]])
        for com in com_list:
            df.loc[df[column[0]] == com, 'unit'] = df.loc[
                df[column[0]] == com, 'unit'].mode()[0]
    else:
        df['unit'] = df['unit'].mode()[0]
    return df

# %% III) The main class


class addNewYear(object):
    ''' This class does the following:
    A. calls function "addSets" to add and modify required sets.
    B. calls function "addPar" to add new years and modifications
    to each parameter if needed.

    Parameters:
    -----------
        sc_ref : string
            reference scenario (MESSAGE model/scenario instance)
        sc_new : string
            new scenario for adding new years and required modifications
            (MESSAGE model/scenario instance)
        yrs_new : list of integers
            new years to be added
        firstyear_new : integer, default None
            a new first model year for new scenario (optional)
        macro : boolean, default False
            a flag to add new years to macro parameters (True) or not (False)
        baseyear_macro : integer, default None
            a new base year for macro
        parameter: list of strings, default all
            parameters for adding new years
        rewrite: boolean, default True
            a flag to permit rewriting a parameter in new scenario when adding
            new years (True) or not (False)
        check_unit: boolean, default False
            a flag to uniform the units under each commodity (if there is
            inconsistency between units in two model years)
                extrapol_neg: float, default None
            a number to multiply by the data of the previous timestep,
            when extrapolation is negative
        bound_extend: boolean, default True
            a flag to permit the duplication of the data from the previous
            timestep, when there is only one data point for interpolation
            (e.g., permitting the extension of a bound to 2025, when there
            is only one value in 2020)
    '''

    def __init__(self, sc_ref, sc_new, years_new, firstyear_new=None,
                 lastyear_new=None, macro=False, baseyear_macro=None,
                 parameter=all, region=all, rewrite=True, unit_check=True,
                 extrapol_neg=None, bound_extend=True):

        # III.A) Adding sets and required modifications
        years_new = sorted([x for x in years_new if str(x)
                            not in set(sc_ref.set('year'))])
        self.addSets(
            sc_ref,
            sc_new,
            years_new,
            firstyear_new,
            lastyear_new,
            baseyear_macro)
        # --------------------------------------------------------------------------
        # III.B)  Adding parameters and calculating the missing values for the
        # additonal years
        if parameter == all:
            par_list = sorted(sc_ref.par_list())
        elif isinstance(parameter, list):
            par_list = parameter
        elif isinstance(parameter, str):
            par_list = [parameter]
        else:
            print(
                'Parameters should be defined in a list of strings or as' +
                'a single string!')

        if 'technical_lifetime' in par_list:
            par_list.insert(
                0, par_list.pop(
                    par_list.index('technical_lifetime')))

        if region == all:
            reg_list = sc_ref.set('node').tolist()
        elif isinstance(region, list):
            reg_list = region
        elif isinstance(region, str):
            reg_list = [region]
        else:
            print('Regions should be defined in a list of strings or as' +
                  'a single string!')

        # List of parameters to be ignored (even not copied to the new
        # scenario)
        par_ignore = ['duration_period']
        par_list = [x for x in par_list if x not in par_ignore]

        if not macro:
            par_macro = [
                'demand_MESSAGE',
                'price_MESSAGE',
                'cost_MESSAGE',
                'gdp_calibrate',
                'historical_gdp',
                'MERtoPPP',
                'kgdp',
                'kpvs',
                'depr',
                'drate',
                'esub',
                'lotol',
                'p_ref',
                'lakl',
                'prfconst',
                'grow',
                'aeei',
                'aeei_factor',
                'gdp_rate']
            par_list = [x for x in par_list if x not in par_macro]

        for parname in par_list:
            # For historical parameters extrapolation permitted (e.g., from
            # 2010 to 2015)
            if 'historical' in parname:
                extrapol = True
                yrs_new = [
                    x for x in years_new if x < int(
                        sc_new.set(
                            'cat_year', {
                                'type_year': 'firstmodelyear'})['year'])]
            else:
                extrapol = False
                yrs_new = years_new

            if 'bound' in parname:
                bound_ext = bound_extend
            else:
                bound_ext = True

            year_list = [x for x in sc_ref.idx_sets(parname) if 'year' in x]

            if len(year_list) == 2 or parname in ['land_output']:
                # The loop over "node" is only for reducing the size of tables
                for node in reg_list:
                    self.addPar(
                        sc_ref,
                        sc_new,
                        yrs_new,
                        parname,
                        [node],
                        extrapolate=extrapol,
                        rewrite=rewrite,
                        unit_check=unit_check,
                        extrapol_neg=extrapol_neg,
                        bound_extend=bound_ext)
            else:
                self.addPar(
                    sc_ref,
                    sc_new,
                    yrs_new,
                    parname,
                    reg_list,
                    extrapolate=extrapol,
                    rewrite=rewrite,
                    unit_check=unit_check,
                    extrapol_neg=extrapol_neg,
                    bound_extend=bound_ext)

        sc_new.set_as_default()
        print('> All required parameters were successfully ' +
              'added to the new scenario.')

    # %% Submodules needed for running the main function
    #   IV) Adding new years to sets
    def addSets(
            self,
            sc_ref,
            sc_new,
            years_new,
            firstyear_new=None,
            lastyear_new=None,
            baseyear_macro=None):
        '''
        Description:
            Adding required sets and relevant modifications:
            This function adds additional years to an existing scenario,
            by starting to make a new scenario from scratch.
            After modification of the year-related sets, this function copeis
            all other sets from the "reference" scenario
            to the "new" scenario.

        Input arguments:
            Please see the description for the input arguments under the main
            function "addNewYear"

        Usage:
            This module is called by function "addNewYear"
        '''
    #   IV.A) Treatment of the additional years in the year-related sets

        # A.1. Set - year
        yrs_old = list(map(int, sc_ref.set('year')))
        horizon_new = sorted(yrs_old + years_new)
        sc_new.add_set('year', [str(yr) for yr in horizon_new])

        # A.2. Set _ type_year
        yr_typ = sc_ref.set('type_year').tolist()
        sc_new.add_set('type_year', sorted(
            yr_typ + [str(yr) for yr in years_new]))

        # A.3. Set _ cat_year
        yr_cat = sc_ref.set('cat_year')

        # A.4. Changing the first year if needed
        if firstyear_new:
            yr_cat.loc[yr_cat['type_year'] ==
                       'firstmodelyear', 'year'] = firstyear_new
        if lastyear_new:
            yr_cat.loc[yr_cat['type_year'] ==
                       'lastmodelyear', 'year'] = lastyear_new

        # A.5. Changing the base year and initialization year of macro if a new
        # year specified
        if not yr_cat.loc[yr_cat['type_year'] ==
                          'baseyear_macro', 'year'].empty and baseyear_macro:
            yr_cat.loc[yr_cat['type_year'] ==
                       'baseyear_macro', 'year'] = baseyear_macro
        if not yr_cat.loc[yr_cat['type_year'] ==
                          'initializeyear_macro', 'year'
                          ].empty and baseyear_macro:
            yr_cat.loc[yr_cat['type_year'] ==
                       'initializeyear_macro', 'year'] = baseyear_macro

        yr_pair = []
        for yr in years_new:
            yr_pair.append([yr, yr])
            yr_pair.append(['cumulative', yr])

        yr_cat = yr_cat.append(
            pd.DataFrame(
                yr_pair,
                columns=[
                    'type_year',
                    'year']),
            ignore_index=True).sort_values('year').reset_index(
                drop=True)

        # A.6. Changing the cumulative years based on the new first model year
        firstyear_new = int(
            yr_cat.loc[yr_cat['type_year'] == 'firstmodelyear', 'year'])
        yr_cat = yr_cat.drop(yr_cat.loc[
                (yr_cat['type_year'] == 'cumulative') & (
                 yr_cat['year'] < firstyear_new)].index)
        sc_new.add_set('cat_year', yr_cat)

        # IV.B) Copying all other sets
        set_list = [s for s in sc_ref.set_list() if 'year' not in s]
        # Sets with one index set
        index_list = [
            x for x in set_list if not isinstance(
                sc_ref.set(x), pd.DataFrame)]
        for set_name in index_list:
            if set_name not in sc_new.set_list():
                sc_new.init_set(set_name, idx_sets=None, idx_names=None)
            sc_new.add_set(set_name, sc_ref.set(set_name).tolist())

            # The rest of the sets
        for set_name in [x for x in set_list if x not in index_list]:
            if set_name not in sc_new.set_list() and not [
                    x for x in sc_ref.idx_sets(
                            set_name) if x not in sc_ref.set_list()]:
                sc_new.init_set(set_name,
                                idx_sets=sc_ref.idx_sets(set_name).tolist(),
                                idx_names=sc_ref.idx_names(set_name).tolist())
            sc_new.add_set(set_name, sc_ref.set(set_name))

        sc_new.commit('sets added!')
        print('> All the sets updated and added to the new scenario.')

    # %% V) Adding new years to parameters

    def addPar(
            self,
            sc_ref,
            sc_new,
            yrs_new,
            parname,
            region_list,
            extrapolate=False,
            rewrite=True,
            unit_check=True,
            extrapol_neg=None,
            bound_extend=True):
        ''' Adding required parameters and relevant modifications:
        Description:
            This function adds additional years to a parameter.
            The value of the parameter for additional years is calculated
            mainly by interpolating and extrapolating of data from existing
            years.

        Input arguments:
            Please see the description for the input arguments under the
            main function "addNewYear"

        Usage:
            This module is called by function "addNewYear"
        '''

    #  V.A) Initialization and checks

        par_list_new = sc_new.par_list().tolist()
        idx_names = sc_ref.idx_names(parname)
        horizon = sorted([int(x) for x in list(set(sc_ref.set('year')))])
        node_col = [
            x for x in idx_names if x in [
                'node',
                'node_loc',
                'node_rel']]

        if parname not in par_list_new:
            sc_new.check_out()
            sc_new.init_par(
                parname,
                idx_sets=sc_ref.idx_sets(parname).tolist(),
                idx_names=sc_ref.idx_names(parname).tolist())
            sc_new.commit('New parameter initiated!')

        if node_col:
            par_old = sc_ref.par(parname, {node_col[0]: region_list})
            par_new = sc_new.par(parname, {node_col[0]: region_list})
            sort_order = [
                node_col[0],
                'technology',
                'commodity',
                'year_vtg',
                'year_act']
            nodes = par_old[node_col[0]].unique().tolist()
        else:
            par_old = sc_ref.par(parname)
            par_new = sc_new.par(parname)
            sort_order = ['technology', 'commodity', 'year_vtg', 'year_act']
            nodes = ['N/A']

        if not par_new.empty and not rewrite:
            print(
                  '> Parameter "' + parname + '" already has data '
                  'in new scenario and left unchanged for node/s: {}.'.format(
                    region_list))
            return
        if par_old.empty:
            print(
                '> Parameter "' + parname + '" is empty in reference scenario '
                'for node/s: {}!'.format(region_list))
            return

        # Sorting the data to make it ready for dataframe manupulation
        sort_order = [x for x in sort_order if x in idx_names]
        if sort_order:
            par_old = par_old.sort_values(sort_order).reset_index(drop=True)

        sc_new.check_out()
        if not par_new.empty and rewrite:
            print(
                '> Parameter "' + parname + '" is being removed from new '
                'scenario to be updated for node/s in {}...'.format(nodes))
            sc_new.remove_par(parname, par_new)

        col_list = sc_ref.idx_names(parname).tolist()
        year_list = [
            c for c in col_list if c in [
                'year',
                'year_vtg',
                'year_act',
                'year_rel']]

        # A uniform "unit" for values in different years to prevent mistakes in
        # indexing and grouping
        if 'unit' in col_list and unit_check:
            par_old = unit_uniform(par_old)
    # --------------------------------------------------------------------------------------------------------
    #  V.B) Treatment of the new years in the specified parameter based on
    # the time-related dimension of that parameter
    #  V.B.1) Parameters with no time component
        if len(year_list) == 0:
            sc_new.add_par(parname, par_old)
            sc_new.commit(parname)
            print(
                '> Parameter "' + parname + '" just copied to new scenario '
                'since has no time-related entries.')

    #  V.B.2) Parameters with one dimension related to time
        elif len(year_list) == 1:
            year_col = year_list[0]
            df = par_old.copy()
            df_y = self.df_interpolate(
                df,
                yrs_new,
                horizon,
                year_col,
                'value',
                extrapolate=extrapolate,
                extrapol_neg=extrapol_neg,
                bound_extend=bound_extend)
            sc_new.add_par(parname, df_y)
            sc_new.commit(' ')
            print(
                '> Parameter "' + parname + '" copied and new years '
                'added for node/s: "{}".'.format(nodes))

    # V.B.3) Parameters with two dimensions related to time (such as
    # 'input','output', etc.)
        elif len(year_list) == 2:
            year_col = 'year_act'
            node_col = 'node_loc'
            year_ref = [x for x in year_list if x != year_col][0]

            year_diff = [x for x in horizon[1:-
                                            1] if horizon[
                                                    horizon.index(x) + 1] -
                         horizon[horizon.index(x)] > horizon[
                                 horizon.index(x)] - horizon[
                                         horizon.index(x) - 1]]
            print(
                '> Parameter "{}" is being added for node/s "{}"...'.format(
                        parname,
                        nodes))

            # Flagging technologies that have lifetime for adding new timesteps
            firstyear_new = int(
                sc_new.set(
                    'cat_year', {
                        'type_year': 'firstmodelyear'})['year'])
            min_step = min(np.diff(
                sorted([int(x) for x in set(sc_new.set('year')) if int(
                        x) > firstyear_new])))
            par_tec = sc_new.par(
                'technical_lifetime', {
                    'node_loc': nodes})
            # Technologies with lifetime bigger than minimum time interval
            par_tec = par_tec.loc[par_tec['value'] > min_step]
            df = par_old.copy()

            if parname == 'relation_activity':
                tec_list = []
            else:
                tec_list = [t for t in list(set(df[
                        'technology'])) if t in list(set(par_tec[
                                'technology']))]

            df_y = self.df_interpolate_2d(
                df,
                yrs_new,
                horizon,
                year_ref,
                year_col,
                tec_list,
                par_tec,
                value_col='value',
                extrapolate=extrapolate,
                extrapol_neg=extrapol_neg,
                year_diff=year_diff)
            sc_new.add_par(parname, df_y)
            sc_new.commit(parname)
            print(
                '> Parameter "' + parname + '" copied and new years added '
                'for node/s: "{}".'.format(nodes))

    # %% VI) Required functions
    # VI.A) A function to add new years to a datafarme by interpolation and
    # (extrapolation if needed)

    def df_interpolate(
            self,
            df,
            yrs_new,
            horizon,
            year_col,
            value_col='value',
            extrapolate=False,
            extrapol_neg=None,
            bound_extend=True):
        '''
        Description:
            This function receives a parameter data as a dataframe, and adds
            new data for the additonal years by interpolation and
            extrapolation.

        Input arguments:
            df_par (dataframe): the dataframe of the parameter to which new
                years to be added
            yrs_new (list of integers): new years to be added
            horizon (list of integers): the horizon of the reference scenario
            year_col (string): the header of the column to which the new years
                should be added, for example, "year_act"
            value_col (string): the header of the column containing values
            extrapolate: if True, the extrapolation is allowed when a new year
                is outside the parameter years
            extrapol_neg: if True, negative values obtained by extrapolation
                are allowed.

        Usage:
            This function is called by function "addPar"
        '''
        horizon_new = sorted(horizon + yrs_new)
        idx = [x for x in df.columns if x not in [year_col, value_col]]
        if not df.empty:
            df2 = df.pivot_table(index=idx, columns=year_col, values=value_col)

            # To sort the new years smaller than the first year for
            # extrapolation (e.g. 2025 values are calculated first; then
            # values of 2015 based on 2020 and 2025)
            year_before = sorted(
                [x for x in yrs_new if x < min(df2.columns)], reverse=True)
            if year_before and extrapolate:
                for y in year_before:
                    yrs_new.insert(len(yrs_new), yrs_new.pop(yrs_new.index(y)))

            for yr in yrs_new:
                if yr > max(horizon):
                    extrapol = True
                else:
                    extrapol = extrapolate

                # a) If this new year is after the current range of modeled
                # years, do extrapolation
                if extrapol:
                    if yr == horizon_new[horizon_new.index(
                            max(df2.columns)) + 1]:
                        year_pre = max([x for x in df2.columns if x < yr])

                        if len([x for x in df2.columns if x < yr]) >= 2:
                            year_pp = max(
                                [x for x in df2.columns if x < year_pre])

                            df2[yr] = intpol(df2[year_pre], df2[year_pp],
                                             year_pre, year_pp, yr)

                            if bound_extend:
                                df2[yr] = df2[yr].fillna(df2[year_pre])

                            df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]
                            if extrapol_neg and not df2[yr].loc[(
                                    df2[yr] < 0) & (df2[year_pre] >= 0)].empty:
                                df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0),
                                        yr] = df2.loc[(df2[yr] < 0) & (df2[
                                                year_pre] >= 0),
                                                year_pre] * extrapol_neg
                        else:
                            df2[yr] = df2[year_pre]

                # b) If this new year is before the current range of modeled
                # years, do extrapolation
                elif yr < min(df2.columns) and extrapol:
                    year_next = min([x for x in df2.columns if x > yr])

                    if len([x for x in df2.columns if x > yr]) >= 2:
                        year_nn = horizon[horizon.index(yr) + 2]
                        df2[yr] = intpol(
                            df2[year_next], df2[year_nn],
                            year_next, year_nn, yr)
                        df2[yr][np.isinf(df2[year_next])] = df2[year_next]
                        if extrapol_neg and not df2[yr].loc[(
                                df2[yr] < 0) & (df2[year_next] >= 0)].empty:
                            df2.loc[(df2[yr] < 0) &
                                    (df2[year_next] >= 0),
                                    yr] = df2.loc[(df2[yr] < 0) & (
                                            df2[year_next] >= 0),
                                            year_next] * extrapol_neg

                    elif bound_extend:
                        df2[yr] = df2[year_next]

                # c) Otherise, do intrapolation
                elif yr > min(df2.columns) and yr < max(df2.columns):
                    year_pre = max([x for x in df2.columns if x < yr])
                    year_next = min([x for x in df2.columns if x > yr])
                    df2[yr] = intpol(
                        df2[year_pre], df2[year_next], year_pre, year_next, yr)

                    # Extrapolate for new years if the value exists for the
                    # previous year but not for the next years
                    # TODO: here is the place that should be changed if the 
                    # new year should go the time step before the existing one
                    if [x for x in df2.columns if x < year_pre]:
                        year_pp = max([x for x in df2.columns if x < year_pre])
                        df2[yr] = df2[yr].fillna(
                            intpol(
                                df2[year_pre],
                                df2[year_pp],
                                year_pre,
                                year_pp,
                                yr))
                        if extrapol_neg and not df2[yr].loc[(
                                df2[yr] < 0) & (df2[year_pre] >= 0)].empty:
                            df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0),
                                    yr] = df2.loc[(df2[yr] < 0) & (
                                            df2[year_pre] >= 0),
                                            year_pre] * extrapol_neg

                    if bound_extend:
                        df2[yr] = df2[yr].fillna(df2[year_pre])
                    df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]

            df2 = pd.melt(
                df2.reset_index(),
                id_vars=idx,
                value_vars=[
                    x for x in df2.columns if x not in idx],
                var_name=year_col,
                value_name=value_col).dropna(
                subset=[value_col]).reset_index(
                drop=True)
            df2 = df2.sort_values(idx).reset_index(drop=True)
        else:
            print(
                '+++ WARNING: The submitted dataframe is empty, so returned' +
                'empty results!!! +++')
            df2 = df
        return df2

    # %% VI.B) A function to interpolate the data for new time steps in
    # parameters with two dimensions related to time

    def df_interpolate_2d(
            self,
            df,
            yrs_new,
            horizon,
            year_ref,
            year_col,
            tec_list,
            par_tec,
            value_col='value',
            extrapolate=False,
            extrapol_neg=None,
            year_diff=None):
        '''
        Description:
            This function receives a dataframe that has 2 time-related columns
            (e.g., "input" or "relation_activity"), and adds new data for the
            additonal years in both time-related columns by interpolation
            and extrapolation.

        Input arguments:
            df (dataframe): the parameter to which new years to be added
            yrs_new (list of integers): new years to be added
            horizon (list of integers): the horizon of the reference scenario
            year_ref (string): the header of the first column to which the new
                years should be added, for example, "year_vtg"
            year_col (string): the header of the second column to which the
                new years should be added, for example, "year_act"
            value_col (string): the header of the column containing values
            extrapolate: if True, the extrapolation is allowed when a new year
                is outside the parameter years
            extrapol_neg: if True, negative values obtained by extrapolation
                are allowed.

        Usage:
            This utility is called by function "addPar"
        '''
        def f_index(df1, df2): return df1.loc[df1.index.isin(
            df2.index)]     # For checking the index of two dataframes

        idx = [x for x in df.columns if x not in [year_col, value_col]]
        if df.empty:
            return df
            print(
                '+++ WARNING: The submitted dataframe is empty, so' +
                'returned empty results!!! +++')

        df_tec = df.loc[df['technology'].isin(tec_list)]
        df2 = df.pivot_table(index=idx, columns=year_col, values='value')
        df2_tec = df_tec.pivot_table(
            index=idx, columns=year_col, values='value')

        # ------------------------------------------------------------------------------
        # First, changing the time interval for the transition period
        # (e.g., year 2010 in old R11 model transits from 5 year to 10 year)
        horizon_new = sorted(horizon +
                             [x for x in yrs_new if x not in horizon])
        yr_diff_new = [x for x in horizon_new[1:-
                                              1] if horizon_new[
                                                      horizon_new.index(x) +
                                                      1] -
                       horizon_new[horizon_new.index(x)] > horizon_new[
                               horizon_new.index(x)] - horizon_new[
                                       horizon_new.index(x) - 1]]

        if year_diff and tec_list:
            if isinstance(year_diff, list):
                year_diff = year_diff[0]

            # Removing data from old transition year
            if not yr_diff_new or year_diff not in yr_diff_new:
                year_next = [x for x in df2.columns if x > year_diff][0]

                df_pre = f_slice(
                    df2_tec, idx, year_ref, [year_diff], year_diff)
                df_next = f_slice(
                    df2_tec, idx, year_ref, [year_next], year_diff)
                df_count = pd.DataFrame({
                        'c_pre': df_pre.count(axis=1),
                        'c_next': df_next.loc[df_next.index.isin(
                                  df_pre.index)].count(axis=1)},
                                                index=df_pre.index)
                df_y = df_count.loc[df_count['c_pre'] == df_count[
                                             'c_next'] + 1]

                for i in df_y.index:
                    df2.loc[i, df2.columns > (df2.loc[[i]].notnull().cumsum(
                        axis=1) == df_count[
                             'c_next'][i]).idxmax(axis=1).values[0]] = np.nan

        # Generating duration_period_sum matrix for masking
        df_dur = pd.DataFrame(index=horizon_new[:-1], columns=horizon_new[1:])
        for i in df_dur.index:
            for j in [x for x in df_dur.columns if x > i]:
                df_dur.loc[i, j] = j - i

        # Adding data for new transition year
        if yr_diff_new and tec_list and year_diff not in yr_diff_new:
            yrs = [x for x in horizon if x <= yr_diff_new[0]]
            year_next = min([x for x in df2.columns if x > yr_diff_new[0]])
            df_yrs = f_slice(df2_tec, idx, year_ref, yrs, [])
            if yr_diff_new[0] in df2.columns:
                df_yrs = df_yrs.loc[~pd.isna(df_yrs[yr_diff_new[0]]), :]
                df_yrs = df_yrs.append(
                                f_slice(
                                    df2_tec,
                                    idx,
                                    year_ref,
                                    [year_next],
                                    []),
                                ignore_index=False).reset_index(
                                    ).sort_values(idx).set_index(idx)

            for yr in sorted(
                    [x for x in list(set(df_yrs.reset_index(
                            )[year_ref])) if x < year_next]):
                yr_next = min([x for x in horizon_new if x > yr])
                d = f_slice(df_yrs, idx, year_ref, [yr], [])
                d_n = f_slice(df_yrs, idx, year_ref, [yr_next], yr)

                if d_n[year_next].loc[~pd.isna(d_n[year_next])].empty:
                    if [x for x in horizon_new if x > yr_next]:
                        yr_nn = min([x for x in horizon_new if x > yr_next])
                    else:
                        yr_nn = yr_next
                    d_n = f_slice(df_yrs, idx, year_ref, [yr_nn], yr)
                d_n = d_n.loc[d_n.index.isin(d.index), :]
                d = d.loc[d.index.isin(d_n.index), :]
                d[d.isnull() & d_n.notnull()] = d_n
                df2.loc[df2.index.isin(d.index), :] = d

            df_dur.loc[df_dur.index <= yr_diff_new[0],
                       df_dur.columns >= year_next] = df_dur.loc[
                df_dur.index <= yr_diff_new[0],
                df_dur.columns >= year_next] - (
                yr_diff_new[0] - horizon_new[horizon_new.index(
                                                         yr_diff_new[0]) - 1])
        # --------------------------------------------------------------------------
        # Second, adding year_act of new years when year_vtg is in the existing
        # years
        for yr in yrs_new:
            if yr > max(horizon):
                extrapol = True
            else:
                extrapol = extrapolate

            # a) If this new year is greater than the current range of modeled
            # years, do extrapolation
            if yr > horizon_new[horizon_new.index(
                    max(df2.columns))] and extrapol:
                year_pre = max([x for x in df2.columns if x < yr])
                year_pp = max([x for x in df2.columns if x < year_pre])

                df2[yr] = intpol(
                    df2[year_pre],
                    df2[year_pp],
                    year_pre,
                    year_pp,
                    yr)
                df2[yr][np.isinf(df2[year_pre].shift(+1))
                        ] = df2[year_pre].shift(+1)
                df2[yr] = df2[yr].fillna(df2[year_pre])

                if yr - horizon_new[horizon_new.index(yr) - 1] >= horizon_new[
                        horizon_new.index(yr) - 1] - horizon_new[
                                horizon_new.index(yr) - 2]:

                    df2[yr].loc[pd.isna(df2[year_pre].shift(+1))
                                & ~pd.isna(df2[year_pp].shift(+1))] = np.nan
                if extrapol_neg and not df2[yr].loc[(df2[yr] < 0) & (
                        df2[year_pre].shift(+1) >= 0)].empty:
                    df2.loc[(df2[yr] < 0) & (df2[year_pre].shift(+1) >= 0),
                            yr] = df2.loc[(df2[yr] < 0) & (
                                    df2[year_pre].shift(+1) >= 0),
                                          year_pre] * extrapol_neg

            # b) Otherise, do intrapolation
            elif yr > min(df2.columns) and yr < max(df2.columns):
                year_pre = max([x for x in df2.columns if x < yr])
                year_next = min([x for x in df2.columns if x > yr])

                df2[yr] = intpol(
                    df2[year_pre],
                    df2[year_next],
                    year_pre,
                    year_next,
                    yr)
                df2_t = df2.loc[df2_tec.index, :].copy()

                # This part calculates the missing value if only the previous
                # timestep has a value (and not the next)
                if tec_list:
                    df2_t[yr].loc[(pd.isna(df2_t[yr])) & (~pd.isna(df2_t[
                            year_pre]))] = intpol(
                        df2_t[year_pre],
                        df2_t[year_next].shift(-1),
                        year_pre, year_next, yr)

                    # Treating technologies with phase-out in model years
                    if [x for x in df2.columns if x < year_pre]:
                        year_pp = max([x for x in df2.columns if x < year_pre])
                        df2_t[yr].loc[(pd.isna(df2_t[yr])) & (
                                       pd.isna(df2_t[year_pre].shift(-1))) & (
                                       ~pd.isna(df2_t[year_pre]))] = intpol(
                                            df2_t[year_pre],
                                            df2_t[year_pp],
                                            year_pre, year_pp, yr)

                        if extrapol_neg and not df2_t[yr].loc[(
                                df2_t[yr] < 0) & (df2_t[year_pre] >= 0)].empty:
                            df2_t.loc[(df2_t[yr] < 0) & (df2_t[year_pre] >= 0),
                                      yr] = df2_t.loc[(df2_t[yr] < 0) & (
                                                      df2_t[year_pre] >= 0),
                                                      year_pre] * extrapol_neg
                    df2.loc[df2_tec.index, :] = df2_t
                df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]
            df2 = df2.reindex(sorted(df2.columns), axis=1)
        # --------------------------------------------------------------------------
        # Third, adding year_vtg of new years and their respective year_act for
        # both existing and new years
        for yr in yrs_new:
            # a) If this new year is after the current range of modeled years,
            # do extrapolation
            if yr > max(horizon):
                year_pre = horizon_new[horizon_new.index(yr) - 1]
                year_pp = horizon_new[horizon_new.index(yr) - 2]
                df_pre = f_slice(df2, idx, year_ref, [year_pre], yr)
                df_pp = f_slice(df2, idx, year_ref, [year_pp], yr)
                df_yr = intpol(
                    df_pre,
                    f_index(
                        df_pp,
                        df_pre),
                    year_pre,
                    year_pp,
                    yr)
                df_yr[np.isinf(df_pre)] = df_pre

                # For those technolofies with one value for each year
                df_yr.loc[pd.isna(df_yr[yr])] = intpol(
                    df_pre, df_pp.shift(+1, axis=1),
                    year_pre, year_pp, yr).shift(+1, axis=1)
                df_yr[pd.isna(df_yr)] = df_pre

                if extrapol_neg:
                    df_yr[(df_yr < 0) & (df_pre >= 0)] = df_pre * extrapol_neg
                df_yr.loc[:, df_yr.columns < yr] = np.nan

            # c) Otherise, do intrapolation
            elif yr > min(df2.columns) and yr < max(horizon):
                year_pre = horizon_new[horizon_new.index(yr) - 1]
                year_next = min([x for x in horizon if x > yr])

                df_pre = f_slice(df2, idx, year_ref, [year_pre], yr)
                df_next = f_slice(df2, idx, year_ref, [year_next], yr)
                df_yr = pd.concat((
                        df_pre,
                        df_next.loc[df_next.index.isin(df_pre.index)]),
                                  axis=0).groupby(level=idx).mean()
                df_yr[yr] = df_yr[yr].fillna(
                    df_yr[[year_pre, year_next]].mean(axis=1))
                df_yr[np.isinf(df_pre)] = df_pre

                # Creating a mask to remove extra values
                df_count = pd.DataFrame({'c_pre': df_pre.count(axis=1),
                                         'c_next': df_next.loc[
                    df_next.index.isin(df_pre.index)].count(axis=1)},
                    index=df_yr.index)

                for i in df_yr.index:
                    # Mainly for cases of two new consecutive years (like 2022
                    # and 2024)
                    if ~np.isnan(
                            df_count['c_next'][i]) and df_count[
                            'c_pre'][i] >= df_count['c_next'][i] + 2:
                                            df_yr[year_pre] = np.nan

                    # For technologies phasing out before the end of horizon
                    # (like nuc_lc)
                    elif np.isnan(df_count['c_next'][i]):
                        df_yr.loc[i, :] = df_pre.loc[i, :].shift(+1)
                        if tec_list:
                            f_mask(df_yr, i, df_count['c_pre'][i] + 1, np.nan)
                        else:
                            f_mask(df_yr, i, df_count['c_pre'][i], np.nan)

                    # For the rest
                    else:
                        df_yr[year_pre] = np.nan
                        f_mask(df_yr, i, df_count['c_pre'][i], np.nan)

            else:
                continue

            df2 = df2.append(df_yr)
            df2 = df2.reindex(sorted(df2.columns), axis=1).sort_index()
        # ---------------------------------------------------------------------------
        # Forth: final masking based on technical lifetime
        if tec_list:

            df3 = df2.copy()
            for y in sorted([x for x in list(
                    set(df2.index.get_level_values(year_ref))
                    ) if x in df_dur.index]):
                df3.loc[df3.index.get_level_values(year_ref).isin([y]),
                        df3.columns.isin(df_dur.columns)] = df_dur.loc[
                                y, df_dur.columns.isin(df3.columns)].values

            df3 = df3.reset_index().set_index(
                ['node_loc', 'technology', year_ref]).sort_index(level=1)
            par_tec = par_tec.set_index(
                ['node_loc', 'technology', year_ref]).sort_index(level=1)

            for i in [x for x in par_tec.index if x in df3.index]:
                df3.loc[i, 'lifetime'] = par_tec.loc[i, 'value'].copy()

            df3 = df3.reset_index().set_index(idx).dropna(
                subset=['lifetime']).sort_index()
            for i in df3.index:
                df2.loc[i, df3.loc[i, :] >= int(
                    df3.loc[i, 'lifetime'])] = np.nan

            # Removing extra values from non-lifetime technologies
            for i in [x for x in df2.index if x not in df3.index]:
                df2.loc[i, df2.columns > df2.loc[[i]].index.get_level_values(
                        year_ref)[0]] = np.nan

        df_par = pd.melt(
            df2.reset_index(),
            id_vars=idx,
            value_vars=[
                x for x in df2.columns if x not in idx],
            var_name=year_col,
            value_name='value').dropna(
            subset=['value'])
        df_par = df_par.sort_values(idx).reset_index(drop=True)
        return df_par


# %% VII) Input arguments related to running the script from command line
# Text formatting for long help texts
class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('B|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)


def read_args():

    annon = """
    Adding additional years to a MESSAGE model/scenario instance

    Example:
    python f_addYear.py --model_ref "Austria_tutorial" --scen_ref "test_core"
    --scen_new "test_5y" --years_new "[2015,2025,2035,2045]"

    """
    parser = argparse.ArgumentParser(
        description=annon,
        formatter_class=SmartFormatter)

    parser.add_argument('--model_ref',
                        help="B| --model_ref: string\n"
                        "reference model name")
    parser.add_argument('--scen_ref',
                        help="B| --scen_ref: string\n"
                        "reference scenario name")
    parser.add_argument('--version_ref',
                        help="B| --version_ref: integer (standard=None)\n"
                        "version number of reference scenario")
    parser.add_argument('--model_new',
                        help='B| --model_new: string (standard=None)\n'
                        'new model name')
    parser.add_argument('--scen_new',
                        help='B| --scen_new: string (optional)\n'
                        'new scenario name')
    parser.add_argument('--create_new',
                        help='B| --create_new: string (standard=True)\n'
                        'True, for creating a new scenario\n'
                        'False, for using an existing scenario')
    parser.add_argument('--years_new',
                        help='--years_new : list\n    new years to be added')
    parser.add_argument('--firstyear_new',
                        help='B| --firstyear_new: integer (standard=None)\n'
                        'new first model year')
    parser.add_argument('--lastyear_new',
                        help='B| --lastyear_new: integer (standard=None)\n'
                        'new last model year')
    parser.add_argument('--macro',
                        help='B| --macro: string (standard=False)\n'
                        'True, for adding new years to macro parameters\n'
                        'False, for ignoring new years for macro parameters')
    parser.add_argument('--baseyear_macro',
                        help='B| --baseyear_macro : integer (standard=None)\n'
                        'new base year for macro\n')
    parser.add_argument('--parameter',
                        help='B| --parameter: list (standard=all)\n'
                        'list of parameters for adding new years to them\n'
                        'all, for all the parameters')
    parser.add_argument('--region',
                        help='B| --region: list (standard=all)\n'
                        'list of regions for adding new years to them\n'
                        'all, for all the regions')
    parser.add_argument('--rewrite',
                        help='B| --rewrite: string (standard=True)\n'
                        'rewriting parameters in the new scenario')
    parser.add_argument('--unit_check',
                        help='B|--unit_check: string (standard=False)\n'
                        'checking units before adding new years')
    parser.add_argument('--extrapol_neg',
                        help='B| --extrapol_neg: string (standard=None)\n'
                        'treating negative values from extrapolation of\n'
                        'two positive values:\n'
                        'None: does nothing\n'
                        'integer: multiplier to adjacent value'
                        'replacing negative one')
    parser.add_argument('--bound_extend',
                        help='B| --bound_extend : string (standard=True)\n'
                        'copying data from previous timestep if only one data'
                        'available for interpolation:\n')

    args = parser.parse_args()
    return args


# %% If run as main script
if __name__ == '__main__':
    start = timer()
    print('>> Running the script f_addYears.py...')
    args = read_args()
    model_ref = args.model_ref
    scen_ref = args.scen_ref
    version_ref = int(args.version_ref) if args.version_ref else None

    model_new = args.model_new if args.model_new else args.model_ref
    scen_new = args.scen_new if args.scen_new else str(args.scen_ref + '_5y')
    create_new = args.create_new if args.create_new else True
    print(args.years_new)
    years_new = list(map(int, args.years_new.strip('[]').split(',')))
    firstyear_new = int(args.firstyear_new) if args.firstyear_new else None
    lastyear_new = int(args.lastyear_new) if args.lastyear_new else None
    macro = args.macro if args.macro else False
    baseyear_macro = int(args.baseyear_macro) if args.baseyear_macro else None

    parameter = list(map(str, args.parameter.strip(
        '[]').split(','))) if args.parameter else all
    region = list(map(str, args.region.strip('[]').split(','))
                  ) if args.region else all
    rewrite = args.rewrite if args.rewrite else True
    unit_check = args.unit_check if args.unit_check else True
    extrapol_neg = args.extrapol_neg if args.extrapol_neg else 0.5
    bound_extend = args.bound_extend if args.bound_extend else True

    # Loading the reference scenario and creating a new scenario to add the
    # additional years
    if version_ref:
        sc_ref = message_ix.Scenario(
            mp,
            model=model_ref,
            scen=scen_ref,
            version=version_ref)
    else:
        sc_ref = message_ix.Scenario(mp, model=model_ref, scen=scen_ref)

    if create_new:
        sc_new = message_ix.Scenario(
            mp,
            model=model_new,
            scen=scen_new,
            version='new',
            scheme='MESSAGE',
            annotation='5 year modelling')
    else:
        sc_new = message_ix.Scenario(mp, model=model_new, scen=scen_new)
        if sc_new.has_solution():
            sc_new.remove_solution()
        sc_new.check_out()

    # Calling the main function
    addNewYear(
        sc_ref,
        sc_new,
        years_new,
        firstyear_new,
        lastyear_new,
        macro,
        baseyear_macro,
        parameter,
        region,
        rewrite,
        unit_check,
        extrapol_neg,
        bound_extend)
    end = timer()
    mp.close_db()
    print('> Elapsed time for adding new years:', round((end - start) / 60),
          'min and', round((end - start) % 60, 1), 'sec.')
    print('> New scenario with additional years is: "{}"|"{}"|{}'.format(
        sc_new.model, sc_new.scenario, str(sc_new.version)))

# Sample input arguments from commandline
# python f_addNewYear.py --model_ref "CD_Links_SSP2" --scen_ref "baseline"
# --years_new "[2015,2025,2035,2045,2055,2120]"
