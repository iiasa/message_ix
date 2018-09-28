# -*- coding: utf-8 -*-
"""
This function extends or shortens the lifetime of an existing technology in an ixmp scenario
Straightforward version: 'straight' is the linear inter/extrapolation of the two adjacent data points straight from the available model data
@author: zakeri
"""
import pandas as pd
import numpy as np
import ixmp as ix
from colorama import Fore
mp = ix.Platform()


def change_lifetime(
        sc,
        tec,
        lifetime=None,
        year_start=None,
        year_end=None,
        nodes=all,
        par_exclude=None,
        remove_old=False,
        test_run=False,
        extrapol_neg=0.5):
    '''
    sc: object
        ixmp scenario
    tec: string
        Technology name
    lifetime: integer
        New technical lifetime
    year_start: integer
        The first vintage year for this lifetime
    year_end: integer
        The last vintage year for this lifetime
    nodes: string or a list/series of strings, default all
        Model regions in where the lifetime of technology should be updated
    par_exclude: string or a list of strings, default None
        Parameters with no need for being updated for new activity or vintage years (e.g., some bounds may not be needed)
    remove_old: boolean, default False
        A flag for permitting the removal of old vintage years (i.e., those not included in new specified vintage years) from scenario
    test_run: boolean, default False
        If true, the script is run only for test, and no changes will be commited to MESSAGE scenario
    extrapol_neg: integer or None
        Treatment of negative values from extrapolation of two positive values: None does nothing (negative accepted),
        and integer acts as a multiplier of the adjacent value (e.g., 0, 0.5 or 1) for replacing the negative value
    '''
# ------------------------------------------------------------------------------
    # I) Required utility functions for dataframe manupulation
    # I.1) Utility function for interpolation/extrapolation of two numbers,
    # lists or series (x: time steps, y: data points)
    def intpol(y1, y2, x1, x2, x):
        if x2 == x1 and y2 != y1:
            print(
                Fore.RESET +
                '>>> Warning <<<: No difference between x1 and x2, returned empty!!!')
            return []
        elif x2 == x1 and y2 == y1:
            return y1
        else:
            y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
            return y

    # I.2) Utility function for slicing a MultiIndex dataframe and setting a
    # value to a specific level
    # df: dataframe, idx: list, level: string, locator: list, value:
    # integer/string
    def f3(df, idx, level, locator, value):
        df = df.reset_index().loc[df.reset_index()[level].isin(locator)].copy()
        df[level] = value
        return df.set_index(idx)

    # I.3) Function for unifroming the "unit" in different years to prevent
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
# ______________________________________________________________________________
    # II) Initialization and making required year sets
    if nodes == all:
        nodes = sc.set('node')
    elif isinstance(nodes, str):
        nodes = [nodes]

    if par_exclude is None:
        par_exclude = []
    elif isinstance(par_exclude, str):
        par_exclude = [par_exclude]

    first_modelYear = int(
        sc.set(
            'cat_year', {
                'type_year': 'firstmodelyear'})['year'])
    horizon = sorted([int(i) for i in sc.set('year')])

    # Finding MESSAGE parameters with time-related index sets
    parlist_1d = [x for x in set(sc.par_list()) if len([y for y in sc.idx_names(
        x) if 'year' in y]) == 1 and 'technology' in sc.idx_names(x)]  # Parameters with one time-related index
    parlist_2d = [x for x in set(sc.par_list()) if len([y for y in sc.idx_names(
        x) if 'year' in y]) == 2]  # Parameters with two time-related indexes

    if not test_run:
        sc.remove_sol()
        sc.check_out()
# __________________________________________________________________________________
# % III) Modification of parameters
    for node in nodes:
        par_empty = []
        results = {}

        # III.1) First, changing parameter "technical_lifetime"
        parname = 'technical_lifetime'
        df_old = sc.par(parname, {'node_loc': node, 'technology': tec})

        if df_old.empty:
            print('There is no technical lifetime for technology "' +
                  tec + '" in node "' + node + '", no change applied!')
            continue

        year_start = min(df_old['year_vtg']) if not year_start else year_start
        year_end = max(df_old['year_vtg']) if not year_end else year_end
        lifetime = min(df_old['value']) if not lifetime else lifetime

        vtg_years = [x for x in horizon if x >= year_start and x <=
                     year_end]            # New vintage years
        act_years = [max([x for x in vtg_years if x < lifetime + y])
                     for y in vtg_years]   # New last activity years

        df_new = df_old.copy()
        df_new = df_new.loc[df_new['year_vtg'].isin(vtg_years)]
        # For estimating required loop numbers later
        lifetime_old = min(df_new['value'])

        for yr in vtg_years:
            if yr in set(df_new['year_vtg']):
                df_new.loc[df_new['year_vtg'] == yr, 'value'] = lifetime
            else:
                d = df_new.iloc[0, :].copy()
                d['year_vtg'] = yr
                d['value'] = lifetime
                df_new = df_new.append(d, ignore_index=True)

        df_new = df_new.sort_values('year_vtg').reset_index(drop=True)

        if remove_old:
            # Removing extra vintage years if desired
            sc.remove_par(parname, df_old)
        if not test_run:
            sc.add_par(parname, df_new)
        results[parname] = df_new
        par_exclude.append(parname)
        print(
            Fore.RESET +
            '> Parameter "' +
            parname +
            '" updated for new lifetime of "' +
            tec +
            '" in "' +
            node +
            '".')

        # Estimating how many time steps will possibly have missing data (for
        # using in Part III.3)
        n = 1 if lifetime <= lifetime_old else int(
            (lifetime - lifetime_old) / min(np.diff(vtg_years)))

# ------------------------------------------------------------------------------
        # III.2) Parameters with one index related to time (e.g., "inv_cost")
        for parname in set(parlist_1d) - set(par_exclude):
            # Node-related index
            node_col = [y for y in sc.idx_names(parname) if 'node' in y][0]
            df_old = sc.par(parname, {node_col: node, 'technology': tec})
            # Year-related index
            year_ref = [y for y in df_old.columns if 'year' in y][0]

            if df_old.empty:
                par_empty.append(parname)
                continue
            # No update of missing data for historical years (for 1d
            # parameters)
            elif max(df_old[year_ref]) < first_modelYear:
                par_empty.append(parname)
                continue

            if 'unit' in df_old.columns:
                df_old = unit_uniform(df_old)

            idx = [x for x in df_old.columns if x not in [year_ref, 'value']]
            # Converting data to pivot table for extrapolation using numeric
            # columns
            df2 = df_old.copy().pivot_table(index=idx, columns=year_ref, values='value')

            # Preparing for backward extrapolation if more than one new years
            # to be added before existing ones
            year_list = sorted([x for x in vtg_years if x <
                                min(df_old[year_ref])], reverse=True)
            year_list = year_list + \
                sorted([x for x in vtg_years if x > max(df_old[year_ref])])

            for yr in [x for x in year_list if yr >= first_modelYear]:
                if yr < max(df2.columns):
                   # Finding two adjacent years for extrapolation
                    year_next = horizon[horizon.index(yr) + 1]
                    year_nn = horizon[horizon.index(
                        yr) + 2] if len([x for x in df2.columns if x > yr]) >= 2 else year_next

                elif yr > max(df2.columns) and horizon[horizon.index(yr) - 1] in df2.columns:
                    year_next = horizon[horizon.index(yr) - 1]
                    year_nn = horizon[horizon.index(
                        yr) - 2] if len([x for x in df2.columns if x < yr]) >= 2 else year_next

                else:
                    continue

                df2.loc[:, yr] = intpol(float(df2[year_next]), float(
                    df2[year_nn]), year_next, year_nn, yr)

                if not df2.loc[np.isinf(df2[year_next])].empty:
                    # If adjacent value(s) are infinity, the missing value is
                    # set to the same inf
                    df2.loc[np.isinf(df2[year_next]),
                            yr] = df2.loc[:, year_next]

                if extrapol_neg and not df2[yr].loc[(
                        df2[yr] < 0) & (df2[year_next] >= 0)].empty:
                    # Negative values after extrapolation are ignored, if
                    # adjacent value is positive a multiplier is applied.
                    df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0),
                            yr] = df2.loc[:, year_next] * extrapol_neg

            df_new = pd.melt(df2.reset_index(), id_vars=idx, value_vars=[x for x in df2.columns if x not in idx],     # Reformatting to ixmp parameter table format
                             var_name=year_ref, value_name='value').dropna(subset=['value']).reset_index(drop=True)
            df_new = df_new.sort_values(
                idx +
                [year_ref]).reset_index(
                drop=True)
            df_new = df_new.loc[df_new[year_ref].isin(vtg_years)]

            if remove_old:
                # Removing extra vintage/activity years if desired
                sc.remove_par(parname, df_old)
            if not test_run:
                sc.add_par(parname, df_new)
            results[parname] = df_new
            print(
                Fore.RESET +
                '> Parameter "' +
                parname +
                '" updated for new lifetime of "' +
                tec +
                '" in "' +
                node +
                '".')
# ------------------------------------------------------------------------------
        # III.3) Parameters with two indexes related to time (e.g., 'input')
        for parname in set(parlist_2d) - set(par_exclude):
            # Existing data
            df_old = sc.par(parname, {'node_loc': node, 'technology': tec})

            if df_old.empty:
                par_empty.append(parname)
                continue

            if 'unit' in df_old.columns:
                df_old = unit_uniform(df_old)

            idx = [x for x in df_old.columns if x not in ['year_act', 'value']]
            # Making pivot table for extrapolation
            df2 = df_old.copy().pivot_table(index=idx, columns='year_act', values='value')
            # The second index related to time, to be paired with year_act
            year_ref = [
                y for y in df_old.columns if y in [
                    'year', 'year_vtg', 'year_rel']][0]

            # Checking inconsistency in vintage years for
            # commodities/emissions/relations for one specific technology
            col_nontec = [
                x for x in sc.idx_names(parname) if not any(
                    y in x for y in [
                        'time',
                        'node',
                        'tec',
                        'mode',
                        'year',
                        'level',
                        'rating'])]
            if col_nontec:
                df_count = df2.reset_index().loc[df2.reset_index()[year_ref].isin(
                    vtg_years), col_nontec].apply(pd.value_counts).fillna(0)
                df_count = df_count.loc[df_count[col_nontec[0]] < int(
                    df_count.mean())]

                if not df_count.empty:    # NOTICE: this is not solved here and it should be decided by the user
                    print(Fore.RED +
                          '>>> WARNING <<<: In parameter "' +
                          parname +
                          '" the vintage years of "' +
                          str({col_nontec[0]: df_count.index.tolist()}) +
                          ', "' +
                          tec +
                          '" in "' +
                          node +
                          '" are different from other input entries; Please check the results!!!')

            # III.3.1) Adding extra active years to existing vintage years, if
            # lifetime extended
            # For checking the index of two dataframes
            def f2(df1, df2): return df1.loc[df1.index.isin(df2.index)]
            count = 0
            while count <= n:
                # The counter of loop (no explicit use of k)
                count = count + 1
                for yr in sorted(
                        [x for x in set(df_old[year_ref]) if x in vtg_years]):
                    # The last active year of this vintage year
                    yr_end = act_years[vtg_years.index(yr)]

                    if yr < max(df_old['year_act']):
                        year_next = horizon[horizon.index(yr) + 1]

                        if yr < horizon[horizon.index(
                                max(df_old['year_act'])) - 1]:
                            year_nn = horizon[horizon.index(yr) + 2]
                        else:
                            year_nn = yr   # This is for the year one but last in the horizon

                        df_yr = df2[df2.index.get_level_values(year_ref).isin(
                            [yr])].reindex(sorted(df2.columns), axis=1)

                        # Finding the first active year with a missing value
                        yr_act = sorted([x for x in df_yr.columns if pd.isna(
                            df_yr[x][0]) and x <= yr_end and x > yr])[:1]
                        if yr_act:
                            yr_act = yr_act[0]
                            # Extrapolation across the activity years of the
                            # following two vintage years (column-wise)
                            df_yr[yr_act] = intpol(f3(df2,
                                                      idx,
                                                      year_ref,
                                                      [year_next],
                                                      yr)[yr_act],
                                                   f2(f3(df2,
                                                         idx,
                                                         year_ref,
                                                         [year_nn],
                                                         yr)[yr_act],
                                                      f3(df2,
                                                         idx,
                                                         year_ref,
                                                         [year_next],
                                                         yr)),
                                                   year_next,
                                                   year_nn,
                                                   yr)

                        # To make sure no data in active years bigger than the
                        # end year
                        df_yr.loc[:, df_yr.columns > yr_end] = np.nan
                        df2.loc[df_yr.index, :] = df_yr
                        df2 = df2.reindex(sorted(df2.columns), axis=1)

            # III.3.2) Adding missing values for extended vintage and active years (before and fater existing vintage years)
            # New vintage years before the first existing vintage year
            # (reversing to extrapolate backwards)
            yr_list = sorted([x for x in vtg_years if x <
                              min(df_old['year_act'])], reverse=True)

            # Plus new vintage years after the last existing vintage year
            yr_list = yr_list + \
                sorted([x for x in vtg_years if x > max(df_old[year_ref])])

            if yr_list:
                for yr in yr_list:
                    # Finding the two adjacent vintage years
                    if yr < min(df_old['year_act']):
                        year_next = horizon[horizon.index(yr) + 1]
                        year_nn = horizon[horizon.index(yr) + 2]
                        df2[yr] = np.nan

                    else:
                        year_next = horizon[horizon.index(yr) - 1]
                        year_nn = horizon[horizon.index(yr) - 2]

                        if yr not in df2.columns:     # Adding missing active years for this new vintage year
                            df2[yr] = intpol(
                                df2[year_next], df2[year_nn], year_next, year_nn, yr)
                            df2[yr].loc[pd.isna(df2[yr]) & ~pd.isna(
                                df2[year_next])] = df2.loc[:, year_next].copy()
                            # Removing extra values from previous vintage year
                            df2[yr].loc[pd.isna(df2[yr].shift(+1))] = np.nan

                            if extrapol_neg:
                                df2[yr].loc[(df2[yr] < 0) & (
                                    df2[year_next] >= 0)] = df2.loc[:, year_next].copy() * extrapol_neg

                    df_yr = intpol(f3(df2, idx, year_ref, [year_next], yr), f2(f3(df2, idx, year_ref, [year_nn], yr), f3(df2, idx, year_ref, [
                                   year_next], yr)), year_next, year_nn, yr)  # Configuring the new vintage year to be added to vintage years

                    # Excluding parameters with two time index, but not across
                    # all active years
                    if parname not in ['relation_activity']:
                        df_yr[year_next].loc[pd.isna(df_yr[year_next])] = f3(
                            df2, idx, year_ref, [year_next], yr).loc[:, year_next].copy()
                        df_yr[yr].loc[pd.isna(df_yr[yr])] = intpol(
                            df_yr[year_next], df_yr[year_nn], year_next, year_nn, yr)

                    if not df_yr.loc[pd.isna(df_yr[yr])].empty:
                        df_yr.loc[:, yr] = intpol(f3(df2, idx, year_ref, [year_next], yr).loc[:, year_next], f3(
                            df2, idx, year_ref, [year_nn], yr).loc[:, year_nn], year_next, year_nn, yr)

                    yr_end = act_years[vtg_years.index(yr)]
                    # To make sure no extra active years for new vintage years
                    # in the loop
                    df_yr.loc[:, (df_yr.columns > yr_end) |
                              (df_yr.columns < yr)] = np.nan

                    if yr in set(df_old[year_ref]):
                        df2.loc[df2.index.isin(df_yr.index), :] = df_yr
                    else:
                        df2 = df2.append(df_yr)
                    df2 = df2.reindex(sorted(df2.columns), axis=1)
                    df2 = df2.reset_index().sort_values(idx).set_index(idx)

            for yr in vtg_years:           # The final check in case the liftime is being reduced
                df2.loc[df2.index.get_level_values(year_ref).isin(
                    [yr]), df2.columns > act_years[vtg_years.index(yr)]] = np.nan

            df_new = pd.melt(
                df2.reset_index(),
                id_vars=idx,
                value_vars=[
                    x for x in df2.columns if x not in idx],
                var_name='year_act',
                value_name='value').dropna(
                subset=['value'])
            df_new = df_new.sort_values(idx).reset_index(drop=True)
            df_new = df_new.loc[df_new[year_ref].isin(vtg_years)]

            if remove_old:
                # Removing extra (old) vintage/activity years if desired
                sc.remove_par(parname, df_old)
            if not test_run:
                sc.add_par(parname, df_new)

            results[parname] = df_new.pivot_table(
                index=idx, columns='year_act', values='value').reset_index()
            print(
                Fore.RESET +
                '> Parameter "' +
                parname +
                '" updated for new lifetime of "' +
                tec +
                '" in "' +
                node +
                '".')

        #print(Fore.RESET +'> Parameters "' + str(par_empty) + '" have no data in node "' + node + '", no update needed!')
    if not test_run:
        sc.commit('Scenario updated for new lifetime.')
    return results
