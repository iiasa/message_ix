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
    III. The main class called "add_year"
    IV. Submodule "add_year_set" for adding and modifying the sets
    V. Submodule "add_year_par" for copying and modifying each parameter
    VI. Submodule "add_year_par" calls two utility functions ("interpolate_1d"
    and "interpolate_2D") for calculating missing values.
    VII. Code for running the script as "main"


Usage:
    This script can be used either:
    A) By running directly from the command line, example:
    ---------------------------------------------------------------------------
    python f_add_year.py --model_ref "MESSAGE_Model" --scen_ref "baseline"
    --years_new "[2015,2025,2035,2045]"
    ---------------------------------------------------------------------------
    (Other input arguments are optional. For more info see Section V below.)

    B) By calling the class "add_year" from other python scripts
"""
# %% I) Importing required packages and loading ixmp platform

import numpy as np
import pandas as pd

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


def slice_df(df, idx, level, locator, value):
    if locator:
        df = df.reset_index().loc[df.reset_index()[level].isin(locator)].copy()
    else:
        df = df.reset_index().copy()
    if value:
        df[level] = value
    return df.set_index(idx)

# II.C) A function for creating a mask for removing extra values from a
# dataframe


def mask_df(df, index, count, value):
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


# %% III) The main function
def add_year(sc_ref, sc_new, years_new, firstyear_new=None, lastyear_new=None,
             macro=False, baseyear_macro=None, parameter='all', region='all',
             rewrite=True, unit_check=True, extrapol_neg=None,
             bound_extend=True):
    ''' This class does the following:
    A. calls function "add_year_set" to add and modify required sets.
    B. calls function "add_year_par" to add new years and modifications
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
    # III.A) Adding sets and required modifications
    years_new = sorted([x for x in years_new if str(x)
                        not in set(sc_ref.set('year'))])
    add_year_set(sc_ref, sc_new, years_new, firstyear_new, lastyear_new,
                 baseyear_macro)
    # -------------------------------------------------------------------------
    # III.B)  Adding parameters and calculating the missing values for the
    # additonal years
    if parameter == 'all':
        par_list = sorted(sc_ref.par_list())
    elif isinstance(parameter, list):
        par_list = parameter
    elif isinstance(parameter, str):
        par_list = [parameter]
    else:
        print('Parameters should be defined in a list of strings or as'
              ' a single string!')

    if 'technical_lifetime' in par_list:
        par_list.insert(0, par_list.pop(par_list.index('technical_lifetime')))

    if region == 'all':
        reg_list = sc_ref.set('node').tolist()
    elif isinstance(region, list):
        reg_list = region
    elif isinstance(region, str):
        reg_list = [region]
    else:
        print('Regions should be defined in a list of strings or as'
              ' a single string!')

    # List of parameters to be ignored (even not copied to the new
    # scenario)
    par_ignore = ['duration_period']
    par_list = [x for x in par_list if x not in par_ignore]

    if not macro:
        par_macro = ['demand_MESSAGE', 'price_MESSAGE', 'cost_MESSAGE',
                     'gdp_calibrate', 'historical_gdp', 'MERtoPPP', 'kgdp',
                     'kpvs', 'depr', 'drate', 'esub', 'lotol', 'p_ref', 'lakl',
                     'prfconst', 'grow', 'aeei', 'aeei_factor', 'gdp_rate']
        par_list = [x for x in par_list if x not in par_macro]

    firstyear = sc_new.set('cat_year', {'type_year': 'firstmodelyear'})['year']
    for parname in par_list:
        # For historical parameters extrapolation permitted (e.g., from
        # 2010 to 2015)
        if 'historical' in parname:
            extrapol = True
            yrs_new = [x for x in years_new if x < int(firstyear)]
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
                add_year_par(sc_ref, sc_new, yrs_new, parname, [node],
                             extrapol, rewrite, unit_check, extrapol_neg,
                             bound_ext)
        else:
            add_year_par(sc_ref, sc_new, yrs_new, parname, reg_list,
                         extrapol, rewrite, unit_check, extrapol_neg,
                         bound_ext)

    sc_new.set_as_default()
    print('> All required parameters were successfully ' +
          'added to the new scenario.')


# %% Submodules needed for running the main function
#   IV) Adding new years to sets
def add_year_set(sc_ref, sc_new, years_new, firstyear_new=None,
                 lastyear_new=None, baseyear_macro=None):
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
        function "add_year"

    Usage:
        This module is called by function "add_year"
    '''
#   IV.A) Treatment of the additional years in the year-related sets

    # A.1. Set - year
    yrs_old = list(map(int, sc_ref.set('year')))
    horizon_new = sorted(yrs_old + years_new)
    sc_new.add_set('year', [str(yr) for yr in horizon_new])

    # A.2. Set _ type_year
    yr_typ = sc_ref.set('type_year').tolist()
    sc_new.add_set('type_year', sorted(yr_typ + [str(yr) for yr in years_new]))

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
                      'initializeyear_macro', 'year'].empty and baseyear_macro:
        yr_cat.loc[yr_cat['type_year'] ==
                   'initializeyear_macro', 'year'] = baseyear_macro

    yr_pair = []
    for yr in years_new:
        yr_pair.append([yr, yr])
        yr_pair.append(['cumulative', yr])

    yr_cat = yr_cat.append(pd.DataFrame(yr_pair,
                                        columns=['type_year', 'year']),
                           ignore_index=True
                           ).sort_values('year').reset_index(drop=True)

    # A.6. Changing the cumulative years based on the new first model year
    firstyear_new = int(yr_cat.loc[yr_cat['type_year'] == 'firstmodelyear',
                                   'year'])
    yr_cat = yr_cat.drop(yr_cat.loc[(yr_cat['type_year'] == 'cumulative'
                                     ) & (yr_cat['year'] < firstyear_new)
                                    ].index)
    sc_new.add_set('cat_year', yr_cat)

    # IV.B) Copying all other sets
    set_list = [s for s in sc_ref.set_list() if 'year' not in s]
    # Sets with one index set
    index_list = [x for x in set_list if not isinstance(sc_ref.set(x),
                                                        pd.DataFrame)]
    for set_name in index_list:
        if set_name not in sc_new.set_list():
            sc_new.init_set(set_name, idx_sets=None, idx_names=None)
        sc_new.add_set(set_name, sc_ref.set(set_name).tolist())

    # The rest of the sets

    for set_name in [x for x in set_list if x not in index_list]:
        new_set = [x for x in sc_ref.idx_sets(set_name
                                              ) if x not in sc_ref.set_list()]
        if set_name not in sc_new.set_list() and not new_set:
            sc_new.init_set(set_name,
                            idx_sets=sc_ref.idx_sets(set_name).tolist(),
                            idx_names=sc_ref.idx_names(set_name).tolist())
        sc_new.add_set(set_name, sc_ref.set(set_name))

    sc_new.commit('sets added!')
    print('> All the sets updated and added to the new scenario.')


# %% V) Adding new years to parameters
def add_year_par(sc_ref, sc_new, yrs_new, parname, region_list,
                 extrapolate=False, rewrite=True, unit_check=True,
                 extrapol_neg=None, bound_extend=True):
    ''' Adding required parameters and relevant modifications:
    Description:
        This function adds additional years to a parameter.
        The value of the parameter for additional years is calculated
        mainly by interpolating and extrapolating of data from existing
        years.

    Input arguments:
        Please see the description for the input arguments under the
        main function "add_year"

    Usage:
        This module is called by function "add_year"
    '''

#  V.A) Initialization and checks

    par_list_new = sc_new.par_list().tolist()
    idx_names = sc_ref.idx_names(parname)
    horizon = sorted([int(x) for x in list(set(sc_ref.set('year')))])
    node_col = [x for x in idx_names if x in ['node', 'node_loc', 'node_rel']]

    if parname not in par_list_new:
        sc_new.check_out()
        sc_new.init_par(parname, idx_sets=sc_ref.idx_sets(parname).tolist(),
                        idx_names=sc_ref.idx_names(parname).tolist())
        sc_new.commit('New parameter initiated!')

    if node_col:
        par_old = sc_ref.par(parname, {node_col[0]: region_list})
        par_new = sc_new.par(parname, {node_col[0]: region_list})
        sort_order = [node_col[0], 'technology', 'commodity', 'year_vtg',
                      'year_act']
        nodes = par_old[node_col[0]].unique().tolist()
    else:
        par_old = sc_ref.par(parname)
        par_new = sc_new.par(parname)
        sort_order = ['technology', 'commodity', 'year_vtg', 'year_act']
        nodes = ['N/A']

    if not par_new.empty and not rewrite:
        print('> Parameter "' + parname + '" already has data in new scenario'
              ' and left unchanged for node/s: {}.'.format(region_list))
        return
    if par_old.empty:
        print('> Parameter "' + parname + '" is empty in reference scenario'
              ' for node/s: {}!'.format(region_list))
        return

    # Sorting the data to make it ready for dataframe manupulation
    sort_order = [x for x in sort_order if x in idx_names]
    if sort_order:
        par_old = par_old.sort_values(sort_order).reset_index(drop=True)

    sc_new.check_out()
    if not par_new.empty and rewrite:
        print('> Parameter "' + parname + '" is being removed from new'
              ' scenario to be updated for node/s in {}...'.format(nodes))
        sc_new.remove_par(parname, par_new)

    col_list = sc_ref.idx_names(parname).tolist()
    year_list = [c for c in col_list if c in ['year', 'year_vtg', 'year_act',
                                              'year_rel']]

    # A uniform "unit" for values in different years to prevent mistakes in
    # indexing and grouping
    if 'unit' in col_list and unit_check:
        par_old = unit_uniform(par_old)
#   ---------------------------------------------------------------------------
#   V.B) Adding new years to a parameter based on time-related indexes
#   V.B.1) Parameters with no time index
    if len(year_list) == 0:
        sc_new.add_par(parname, par_old)
        sc_new.commit(parname)
        print('> Parameter "' + parname + '" just copied to new scenario '
              'since has no time-related entries.')

#   V.B.2) Parameters with one index related to time
    elif len(year_list) == 1:
        year_col = year_list[0]
        df = par_old.copy()
        df_y = interpolate_1d(df, yrs_new, horizon, year_col, 'value',
                              extrapolate, extrapol_neg, bound_extend)
        sc_new.add_par(parname, df_y)
        sc_new.commit(' ')
        print('> Parameter "{}" copied and new years'
              ' added for node/s: "{}".'.format(parname, nodes))

#   V.B.3) Parameters with two indexes related to time (such as 'input')
    elif len(year_list) == 2:
        year_col = 'year_act'
        node_col = 'node_loc'
        year_ref = [x for x in year_list if x != year_col][0]

        def f(x, i):
            return x[i + 1] - x[i] > x[i] - x[i - 1]

        year_diff = [x for x in horizon[1:-1] if f(horizon, horizon.index(x))]
        print('> Parameter "{}" is being added for node/s'
              ' "{}"...'.format(parname, nodes))

        # Flagging technologies that have lifetime for adding new timesteps
        firstyear_new = sc_new.set('cat_year',
                                   {'type_year': 'firstmodelyear'})['year']
        yr_list = [int(x) for x in set(sc_new.set('year')
                                       ) if int(x) > int(firstyear_new)]
        min_step = min(np.diff(sorted(yr_list)))
        par_tec = sc_new.par('technical_lifetime', {'node_loc': nodes})
        # Technologies with lifetime bigger than minimum time interval
        par_tec = par_tec.loc[par_tec['value'] > min_step]
        df = par_old.copy()

        if parname == 'relation_activity':
            tec_list = []
        else:
            tec_list = [t for t in (set(df['technology'])
                                    ) if t in list(set(par_tec['technology']))]

        df_y = interpolate_2d(df, yrs_new, horizon, year_ref, year_col,
                              tec_list, par_tec, 'value', extrapolate,
                              extrapol_neg, year_diff)
        sc_new.add_par(parname, df_y)
        sc_new.commit(parname)
        print('> Parameter "{}" copied and new years added'
              ' for node/s: "{}".'.format(parname, nodes))


# %% VI) Required functions
def interpolate_1d(df, yrs_new, horizon, year_col, value_col='value',
                   extrapolate=False, extrapol_neg=None, bound_extend=True):
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
        bound_extend: if True, allows extrapolation of bounds for new years
    '''
    horizon_new = sorted(horizon + yrs_new)
    idx = [x for x in df.columns if x not in [year_col, value_col]]
    if not df.empty:
        df2 = df.pivot_table(index=idx, columns=year_col, values=value_col)

        # To sort the new years smaller than the first year for
        # extrapolation (e.g. 2025 values are calculated first; then
        # values of 2015 based on 2020 and 2025)
        year_before = sorted([x for x in yrs_new if x < min(df2.columns
                                                            )], reverse=True)
        if year_before and extrapolate:
            for y in year_before:
                yrs_new.insert(len(yrs_new), yrs_new.pop(yrs_new.index(y)))

        for yr in yrs_new:
            if yr > max(horizon):
                extrapol = True
            else:
                extrapol = extrapolate

            # a) If this new year greater than modeled years, do extrapolation
            if extrapol:
                if yr == horizon_new[horizon_new.index(max(df2.columns)) + 1]:
                    year_pre = max([x for x in df2.columns if x < yr])

                    if len([x for x in df2.columns if x < yr]) >= 2:
                        year_pp = max([x for x in df2.columns if x < year_pre])
                        df2[yr] = intpol(df2[year_pre], df2[year_pp],
                                         year_pre, year_pp, yr)

                        if bound_extend:
                            df2[yr] = df2[yr].fillna(df2[year_pre])

                        df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]
                        if not df2[yr].loc[(df2[yr] < 0) & (df2[year_pre] >= 0)
                                           ].empty and extrapol_neg:
                            df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0),
                                    yr] = df2.loc[(df2[yr] < 0
                                                   ) & (df2[year_pre] >= 0),
                                                  year_pre] * extrapol_neg
                    else:
                        df2[yr] = df2[year_pre]

            # b) If the new year is smaller than modeled years, extrapolate
            elif yr < min(df2.columns) and extrapol:
                year_next = min([x for x in df2.columns if x > yr])

                if len([x for x in df2.columns if x > yr]) >= 2:
                    year_nn = horizon[horizon.index(yr) + 2]
                    df2[yr] = intpol(df2[year_next], df2[year_nn],
                                     year_next, year_nn, yr)
                    df2[yr][np.isinf(df2[year_next])] = df2[year_next]
                    if not df2[yr].loc[(df2[yr] < 0) & (df2[year_next] >= 0)
                                       ].empty and extrapol_neg:
                        df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0), yr
                                ] = df2.loc[(df2[yr] < 0
                                             ) & (df2[year_next] >= 0),
                                            year_next] * extrapol_neg

                elif bound_extend:
                    df2[yr] = df2[year_next]

            # c) Otherise, do intrapolation
            elif yr > min(df2.columns) and yr < max(df2.columns):
                year_pre = max([x for x in df2.columns if x < yr])
                year_next = min([x for x in df2.columns if x > yr])
                df2[yr] = intpol(df2[year_pre], df2[year_next],
                                 year_pre, year_next, yr)

                # Extrapolate for new years if the value exists for the
                # previous year but not for the next years
                # TODO: here is the place that should be changed if the
                # new year should go to the time step before the existing one
                if [x for x in df2.columns if x < year_pre]:
                    year_pp = max([x for x in df2.columns if x < year_pre])
                    df2[yr] = df2[yr].fillna(intpol(df2[year_pre],
                                                    df2[year_pp], year_pre,
                                                    year_pp, yr))
                    if not df2[yr].loc[(df2[yr] < 0) & (df2[year_pre] >= 0)
                                       ].empty and extrapol_neg:
                        df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0), yr
                                ] = df2.loc[(df2[yr] < 0
                                             ) & (df2[year_pre] >= 0),
                                            year_pre] * extrapol_neg

                if bound_extend:
                    df2[yr] = df2[yr].fillna(df2[year_pre])
                df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]

        df2 = pd.melt(df2.reset_index(), id_vars=idx,
                      value_vars=[x for x in df2.columns if x not in idx],
                      var_name=year_col, value_name=value_col
                      ).dropna(subset=[value_col]).reset_index(drop=True)
        df2 = df2.sort_values(idx).reset_index(drop=True)
    else:
        print('+++ WARNING: The submitted dataframe is empty, so returned'
              ' empty results!!! +++')
        df2 = df
    return df2


# %% VI.B) Interpolating parameters with two dimensions related to time
def interpolate_2d(df, yrs_new, horizon, year_ref, year_col, tec_list, par_tec,
                   value_col='value', extrapolate=False, extrapol_neg=None,
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
    '''
    def idx_check(df1, df2):
        return df1.loc[df1.index.isin(df2.index)]

    idx = [x for x in df.columns if x not in [year_col, value_col]]
    if df.empty:
        return df
        print('+++ WARNING: The submitted dataframe is empty, so'
              ' returned empty results!!! +++')

    df_tec = df.loc[df['technology'].isin(tec_list)]
    df2 = df.pivot_table(index=idx, columns=year_col, values='value')
    df2_tec = df_tec.pivot_table(index=idx, columns=year_col, values='value')

    # -------------------------------------------------------------------------
    # First, changing the time interval for the transition period
    # (e.g., year 2010 in old R11 model transits from 5 year to 10 year)
    horizon_new = sorted(horizon + [x for x in yrs_new if x not in horizon])

    def f(x, i):
        return x[i + 1] - x[i] > x[i] - x[i - 1]
    yr_diff_new = [x for x in horizon_new[1:-1] if f(horizon,
                                                     horizon.index(x))]

    if year_diff and tec_list:
        if isinstance(year_diff, list):
            year_diff = year_diff[0]

        # Removing data from old transition year
        if not yr_diff_new or year_diff not in yr_diff_new:
            year_next = [x for x in df2.columns if x > year_diff][0]

            df_pre = slice_df(df2_tec, idx, year_ref, [year_diff], year_diff)
            df_next = slice_df(df2_tec, idx, year_ref, [year_next], year_diff)
            df_count = pd.DataFrame({'c_pre': df_pre.count(axis=1),
                                     'c_next': idx_check(df_next, df_pre
                                                         ).count(axis=1)},
                                    index=df_pre.index)
            df_y = df_count.loc[df_count['c_pre'] == df_count['c_next'] + 1]

            for i in df_y.index:
                condition = ((df2.loc[[i]].notnull().cumsum(axis=1)
                              ) == df_count['c_next'][i])
                df2.loc[i, df2.columns > condition.idxmax(axis=1
                                                          ).values[0]] = np.nan

    # Generating duration_period_sum matrix for masking
    df_dur = pd.DataFrame(index=horizon_new[:-1], columns=horizon_new[1:])
    for i in df_dur.index:
        for j in [x for x in df_dur.columns if x > i]:
            df_dur.loc[i, j] = j - i

    # Adding data for new transition year
    if yr_diff_new and tec_list and year_diff not in yr_diff_new:
        yrs = [x for x in horizon if x <= yr_diff_new[0]]
        year_next = min([x for x in df2.columns if x > yr_diff_new[0]])
        df_yrs = slice_df(df2_tec, idx, year_ref, yrs, [])
        if yr_diff_new[0] in df2.columns:
            df_yrs = df_yrs.loc[~pd.isna(df_yrs[yr_diff_new[0]]), :]
            df_yrs = df_yrs.append(slice_df(df2_tec, idx, year_ref,
                                            [year_next], []),
                                   ignore_index=False).reset_index()
            df_yrs = df_yrs.sort_values(idx).set_index(idx)

        for yr in sorted([x for x in list(set(df_yrs.reset_index()[year_ref])
                                          ) if x < year_next]):
            yr_next = min([x for x in horizon_new if x > yr])
            d = slice_df(df_yrs, idx, year_ref, [yr], [])
            d_n = slice_df(df_yrs, idx, year_ref, [yr_next], yr)

            if d_n[year_next].loc[~pd.isna(d_n[year_next])].empty:
                if [x for x in horizon_new if x > yr_next]:
                    yr_nn = min([x for x in horizon_new if x > yr_next])
                else:
                    yr_nn = yr_next
                d_n = slice_df(df_yrs, idx, year_ref, [yr_nn], yr)
            d_n = d_n.loc[d_n.index.isin(d.index), :]
            d = d.loc[d.index.isin(d_n.index), :]
            d[d.isnull() & d_n.notnull()] = d_n
            df2.loc[df2.index.isin(d.index), :] = d

        cond1 = (df_dur.index <= yr_diff_new[0])
        cond2 = (df_dur.columns >= year_next)
        subt = yr_diff_new[0] - horizon_new[horizon_new.index(yr_diff_new[0]
                                                              ) - 1]
        df_dur.loc[cond1, cond2] = df_dur.loc[cond1, cond2] - subt
    # -------------------------------------------------------------------------
    # Second, adding year_act of new years if year_vtg is in existing years
    for yr in yrs_new:
        if yr > max(horizon):
            extrapol = True
        else:
            extrapol = extrapolate

        # a) If this new year is greater than modeled years, do extrapolation
        if yr > horizon_new[horizon_new.index(max(df2.columns))] and extrapol:
            year_pre = max([x for x in df2.columns if x < yr])
            year_pp = max([x for x in df2.columns if x < year_pre])

            df2[yr] = intpol(df2[year_pre], df2[year_pp],
                             year_pre, year_pp, yr)
            df2[yr][np.isinf(df2[year_pre].shift(+1))
                    ] = df2[year_pre].shift(+1)
            df2[yr] = df2[yr].fillna(df2[year_pre])

            j = horizon_new.index(yr)
            if yr - horizon_new[j - 1] >= horizon_new[j - 1
                                                      ] - horizon_new[j - 2]:

                df2[yr].loc[(pd.isna(df2[year_pre].shift(+1))
                             ) & (~pd.isna(df2[year_pp].shift(+1)))] = np.nan
            cond = (df2[yr] < 0) & (df2[year_pre].shift(+1) >= 0)
            if not df2[yr].loc[cond].empty and extrapol_neg:
                df2.loc[cond, yr] = df2.loc[cond, year_pre] * extrapol_neg

        # b) Otherise, do intrapolation
        elif yr > min(df2.columns) and yr < max(df2.columns):
            year_pre = max([x for x in df2.columns if x < yr])
            year_next = min([x for x in df2.columns if x > yr])

            df2[yr] = intpol(df2[year_pre], df2[year_next],
                             year_pre, year_next, yr)
            df2_t = df2.loc[df2_tec.index, :].copy()

            # This part calculates the missing value if only the previous
            # timestep has a value (and not the next)
            if tec_list:
                df2_t[yr].loc[(pd.isna(df2_t[yr])
                               ) & (~pd.isna(df2_t[year_pre]))
                              ] = intpol(df2_t[year_pre],
                                         df2_t[year_next].shift(-1),
                                         year_pre, year_next, yr)

                # Treating technologies with phase-out in model years
                if [x for x in df2.columns if x < year_pre]:
                    year_pp = max([x for x in df2.columns if x < year_pre])
                    df2_t[yr].loc[(pd.isna(df2_t[yr])
                                   ) & (pd.isna(df2_t[year_pre].shift(-1))
                                        ) & (~pd.isna(df2_t[year_pre]))
                                  ] = intpol(df2_t[year_pre], df2_t[year_pp],
                                             year_pre, year_pp, yr)
                    cond = (df2_t[yr] < 0) & (df2_t[year_pre] >= 0)
                    if not df2_t[yr].loc[cond].empty and extrapol_neg:
                        df2_t.loc[cond, yr] = df2_t.loc[cond, year_pre
                                                        ] * extrapol_neg
                df2.loc[df2_tec.index, :] = df2_t
            df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]
        df2 = df2.reindex(sorted(df2.columns), axis=1)
    # -------------------------------------------------------------------------
    # Third, adding year_vtg of new years
    for yr in yrs_new:
        # a) If this new year is greater than modeled years, do extrapolation
        if yr > max(horizon):
            year_pre = horizon_new[horizon_new.index(yr) - 1]
            year_pp = horizon_new[horizon_new.index(yr) - 2]
            df_pre = slice_df(df2, idx, year_ref, [year_pre], yr)
            df_pp = slice_df(df2, idx, year_ref, [year_pp], yr)
            df_yr = intpol(df_pre, idx_check(df_pp, df_pre),
                           year_pre, year_pp, yr)
            df_yr[np.isinf(df_pre)] = df_pre

            # For those technolofies with one value for each year
            df_yr.loc[pd.isna(df_yr[yr])] = intpol(df_pre,
                                                   df_pp.shift(+1, axis=1),
                                                   year_pre, year_pp,
                                                   yr).shift(+1, axis=1)
            df_yr[pd.isna(df_yr)] = df_pre

            if extrapol_neg:
                df_yr[(df_yr < 0) & (df_pre >= 0)] = df_pre * extrapol_neg
            df_yr.loc[:, df_yr.columns < yr] = np.nan

        # c) Otherise, do intrapolation
        elif yr > min(df2.columns) and yr < max(horizon):
            year_pre = horizon_new[horizon_new.index(yr) - 1]
            year_next = min([x for x in horizon if x > yr])

            df_pre = slice_df(df2, idx, year_ref, [year_pre], yr)
            df_next = slice_df(df2, idx, year_ref, [year_next], yr)
            df_yr = pd.concat((df_pre, idx_check(df_next, df_pre)),
                              axis=0).groupby(level=idx).mean()
            df_yr[yr] = df_yr[yr].fillna(df_yr[[year_pre, year_next]
                                               ].mean(axis=1))
            df_yr[np.isinf(df_pre)] = df_pre

            # Creating a mask to remove extra values
            df_count = pd.DataFrame({'c_pre': df_pre.count(axis=1),
                                     'c_next': idx_check(df_next, df_pre
                                                         ).count(axis=1)},
                                    index=df_yr.index)

            for i in df_yr.index:
                # Mainly for cases of two new consecutive new years
                cond = df_count['c_pre'][i] >= df_count['c_next'][i] + 2
                if ~np.isnan(df_count['c_next'][i]) and cond:
                    df_yr[year_pre] = np.nan

                # For technologies phasing out before the end of horizon
                elif np.isnan(df_count['c_next'][i]):
                    df_yr.loc[i, :] = df_pre.loc[i, :].shift(+1)
                    if tec_list:
                        mask_df(df_yr, i, df_count['c_pre'][i] + 1, np.nan)
                    else:
                        mask_df(df_yr, i, df_count['c_pre'][i], np.nan)

                # For the rest
                else:
                    df_yr[year_pre] = np.nan
                    mask_df(df_yr, i, df_count['c_pre'][i], np.nan)

        else:
            continue

        df2 = df2.append(df_yr)
        df2 = df2.reindex(sorted(df2.columns), axis=1).sort_index()
    # -------------------------------------------------------------------------
    # Forth: final masking based on technical lifetime
    if tec_list:

        df3 = df2.copy()
        idx_list = list(set(df2.index.get_level_values(year_ref)))
        for y in sorted([x for x in idx_list if x in df_dur.index]):
            df3.loc[df3.index.get_level_values(year_ref).isin([y]),
                    df3.columns.isin(df_dur.columns)
                    ] = df_dur.loc[y, df_dur.columns.isin(df3.columns)].values

        df3 = df3.reset_index().set_index(
            ['node_loc', 'technology', year_ref]).sort_index(level=1)
        par_tec = par_tec.set_index(
            ['node_loc', 'technology', year_ref]).sort_index(level=1)

        for i in [x for x in par_tec.index if x in df3.index]:
            df3.loc[i, 'lifetime'] = par_tec.loc[i, 'value'].copy()

        df3 = df3.reset_index().set_index(idx).dropna(subset=['lifetime']
                                                      ).sort_index()
        for i in df3.index:
            df2.loc[i, df3.loc[i, :] >= int(
                df3.loc[i, 'lifetime'])] = np.nan

        # Removing extra values from non-lifetime technologies
        for i in [x for x in df2.index if x not in df3.index]:
            condition = df2.loc[[i]].index.get_level_values(year_ref)[0]
            df2.loc[i, df2.columns > condition] = np.nan

    df_par = pd.melt(df2.reset_index(), id_vars=idx,
                     value_vars=[x for x in df2.columns if x not in idx],
                     var_name=year_col,
                     value_name='value').dropna(subset=['value'])
    df_par = df_par.sort_values(idx).reset_index(drop=True)
    return df_par
