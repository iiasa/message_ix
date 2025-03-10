# -*- coding: utf-8 -*-
"""Add model years to an existing Scenario."""
# Sections of the code:
#
#   I. Required python packages are imported
#  II. Generic utilities for dataframe manipulation
# III. The main function, add_year()
#  IV. Function add_year_set() for adding and modifying the sets
#   V. Function add_year_par() for copying and modifying each parameter
#  VI. Two utility functions, interpolate_1d() and interpolate_2d(), for
#      calculating missing values

# %% I) Importing required packages
import logging
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd

from message_ix import Scenario

log = logging.getLogger(__name__)


# %% II) Utility functions for dataframe manupulation
def intpol(
    y1: Union[float, pd.Series, pd.DataFrame],
    y2: Union[float, pd.Series, pd.DataFrame],
    x1: int,
    x2: int,
    x: int,
) -> Union[float, pd.Series, pd.DataFrame]:
    """Interpolate between (*x1*, *y1*) and (*x2*, *y2*) at *x*.

    Parameters
    ----------
    y1, y2 : float or pandas.Series
    x1, x2, x : int
    """
    if x2 == x1 and y2 != y1:
        log.warning("No difference between x1 and x2, returned empty")
        return pd.Series([])
    elif x2 == x1 and y2 == y1:
        return y1
    else:
        y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
        return y


def slice_df(
    df: pd.DataFrame,
    idx: list[str],
    level: str,
    locator: list,
    value: Union[int, str, None],
) -> pd.DataFrame:
    """Slice a MultiIndex DataFrame and set a value to a specific level.

    Parameters
    ----------
    df : pandas.DataFrame
    idx : list of str
       Columns to set as index.
    level: str
    locator : list
    value : int or str

    """
    df = (
        df.reset_index().loc[df.reset_index()[level].isin(locator)].copy()
        if locator
        else df.reset_index().copy()
    )
    if value:
        df[level] = value
    return df.set_index(idx)


def mask_df(
    df: pd.DataFrame, index: tuple[Union[int, str], ...], count: int, value
) -> None:
    """Create a mask for removing extra values from *df*."""
    df.loc[
        index,
        df.columns
        > (df.loc[[index], :].notnull().cumsum(axis=1) == count)
        .idxmax(axis=1)
        .values[0],
    ] = value


def unit_uniform(df: pd.DataFrame) -> pd.DataFrame:
    """Make units in *df* uniform."""
    column = [x for x in df.columns if x in ["commodity", "emission"]]
    if column:
        com_list = set(df[column[0]])
        for com in com_list:
            df.loc[df[column[0]] == com, "unit"] = df.loc[
                df[column[0]] == com, "unit"
            ].mode()[0]
    else:
        df["unit"] = df["unit"].mode()[0]
    return df


# %% III) The main function


def add_year(
    sc_ref: Scenario,
    sc_new: Scenario,
    years_new: list[int],
    firstyear_new: Optional[int] = None,
    lastyear_new: Optional[int] = None,
    macro: bool = False,
    baseyear_macro: Optional[int] = None,
    parameter: Union[list[str], Literal["all"]] = "all",
    region: Union[list[str], Literal["all"]] = "all",
    rewrite: bool = True,
    unit_check: bool = True,
    extrapol_neg: Optional[float] = None,
    bound_extend: bool = True,
) -> None:
    """Add years to *sc_ref* to produce *sc_new*.

    :meth:`add_year` does the following:

    1. calls :meth:`add_year_set` to add and modify required sets.
    2. calls :meth:`add_year_par` to add new years and modifications to each
       parameter if needed.

    Parameters
    -----------
    sc_ref : ixmp.Scenario
        Reference scenario.
    sc_new : ixmp.Scenario
        New scenario.
    yrs_new : list of int
        New years to be added.
    firstyear_new : int, optional
        New first model year for new scenario.
    macro : bool
        Add new years to parameters of the MACRO model.
    baseyear_macro : int
        New base year for the MACRO model.
    parameter: list of str or 'all'
        Parameters for adding new years.
    rewrite: bool
        Permit rewriting a parameter in new scenario when adding new years.
    check_unit: bool
        Harmonize the units for each commodity, if there is inconsistency
        across model years.
    extrapol_neg: float
        When extrapolation produces negative values, replace with a multiple of
        the value for the previous timestep.
    bound_extend: bool
        Duplicate data from the previous timestep when there is only one data
        point for interpolation (e.g., permitting the extension of a bound to
        2025, when there is only one value in 2020).
    """
    # III.A) Adding sets and required modifications
    years_new = sorted([x for x in years_new if str(x) not in set(sc_ref.set("year"))])
    add_year_set(sc_ref, sc_new, years_new, firstyear_new, lastyear_new, baseyear_macro)
    # -------------------------------------------------------------------------
    # III.B)  Adding parameters and calculating the missing values for the
    # additonal years
    par_list: list[str]
    if parameter in ("all", ["all"]):
        par_list = sorted(sc_ref.par_list())
    elif isinstance(parameter, list):
        par_list = parameter
    else:
        log.warning(
            "Parameters should be defined in a list of strings or as a single string"
        )
        par_list = []

    if "technical_lifetime" in par_list:
        par_list.insert(0, par_list.pop(par_list.index("technical_lifetime")))

    reg_list: list[str]
    if region in ("all", ["all"]):
        nodes: pd.Series = sc_ref.set("node")  # type: ignore
        reg_list = nodes.tolist()
    elif isinstance(region, list):
        reg_list = region
    else:
        log.warning(
            "Regions should be defined in a list of strings or as a single string"
        )
        reg_list = []

    # List of parameters to be ignored (even not copied to the new
    # scenario)
    par_ignore = ["duration_period"]
    par_list = [x for x in par_list if x not in par_ignore]

    if not macro:
        par_macro = [
            "demand_MESSAGE",
            "price_MESSAGE",
            "cost_MESSAGE",
            "gdp_calibrate",
            "historical_gdp",
            "MERtoPPP",
            "kgdp",
            "kpvs",
            "depr",
            "drate",
            "esub",
            "lotol",
            "p_ref",
            "lakl",
            "prfconst",
            "grow",
            "aeei",
            "aeei_factor",
            "gdp_rate",
        ]
        par_list = [x for x in par_list if x not in par_macro]

    cat_year_new: pd.DataFrame = sc_new.set("cat_year")
    firstmodelyear_new = cat_year_new.query("type_year == 'firstmodelyear'")
    firstyr_new: int = (
        int(min(cat_year_new["year"]))
        if firstmodelyear_new.empty
        else int(firstmodelyear_new["year"].item())
    )  # type: ignore
    # assert isinstance(firstyear_new, int)

    cat_year_ref: pd.DataFrame = sc_new.set("cat_year")
    firstmodelyear_ref = cat_year_ref.query("type_year == 'firstmodelyear'")
    firstyr_ref: int = (
        min(cat_year_ref["year"]) if firstmodelyear_ref.empty else firstyr_new
    )

    for parname in par_list:
        # For historical parameters extrapolation permitted (e.g., from
        # 2010 to 2015)
        extrapol = (
            True if "historical" in parname or firstyr_ref > firstyr_new else False
        )
        yrs_new = (
            [x for x in years_new if x < firstyr_new]
            if "historical" in parname
            else years_new
        )

        bound_ext = bound_extend if "bound" in parname else True

        year_list = [x for x in sc_ref.idx_sets(parname) if "year" in x]

        if len(year_list) == 2 or parname in ["land_output"]:
            # The loop over "node" is only for reducing the size of tables
            for node in reg_list:
                add_year_par(
                    sc_ref,
                    sc_new,
                    yrs_new,
                    parname,
                    [node],
                    firstyr_new,
                    extrapol,
                    rewrite,
                    unit_check,
                    extrapol_neg,
                    bound_ext,
                )
        else:
            add_year_par(
                sc_ref,
                sc_new,
                yrs_new,
                parname,
                reg_list,
                firstyr_new,
                extrapol,
                rewrite,
                unit_check,
                extrapol_neg,
                bound_ext,
            )

    sc_new.set_as_default()
    log.info("All required parameters were successfully added to the new scenario")


# %% Submodules needed for running the main function
#   IV) Adding new years to sets
# FIXME reduce complexity 14 → ≤13
def add_year_set(  # noqa: C901
    sc_ref: Scenario,
    sc_new: Scenario,
    years_new: list[int],
    firstyear_new: Optional[int] = None,
    lastyear_new: Optional[int] = None,
    baseyear_macro: Optional[int] = None,
) -> None:
    """Add new years to sets.

    :meth:`add_year_set` adds additional years to an existing scenario, by
    starting to make a new scenario from scratch. After modification of the
    year-related sets, all other sets are copied from *sc_ref* to *sc_new*.

    See :meth:`add_year` for parameter descriptions.

    """
    #   IV.A) Treatment of the additional years in the year-related sets
    # A.1. Set - year
    yrs_old = list(map(int, sc_ref.set("year")))
    horizon_new = sorted(yrs_old + years_new)
    sc_new.add_set("year", [str(yr) for yr in horizon_new])

    # A.2. Set _ type_year
    yr_typ = sc_ref.set("type_year").tolist()
    sc_new.add_set("type_year", sorted(yr_typ + [str(yr) for yr in years_new]))

    # A.3. Set _ cat_year
    yr_cat = sc_ref.set("cat_year")

    # A.4. Changing the first year if needed
    if firstyear_new:
        if not yr_cat.loc[yr_cat["type_year"] == "firstmodelyear"].empty:
            yr_cat.loc[yr_cat["type_year"] == "firstmodelyear", "year"] = firstyear_new
        else:
            yr_cat.loc[len(yr_cat.index)] = ["firstmodelyear", firstyear_new]
    if lastyear_new:
        if not yr_cat.loc[yr_cat["type_year"] == "lastmodelyear"].empty:
            yr_cat.loc[yr_cat["type_year"] == "lastmodelyear", "year"] = lastyear_new
        else:
            yr_cat.loc[len(yr_cat.index)] = ["lastmodelyear", lastyear_new]

    # A.5. Changing the base year and initialization year of macro if a new
    # year specified
    if baseyear_macro:
        if not yr_cat.loc[yr_cat["type_year"] == "baseyear_macro", "year"].empty:
            yr_cat.loc[yr_cat["type_year"] == "baseyear_macro", "year"] = baseyear_macro
        if not yr_cat.loc[yr_cat["type_year"] == "initializeyear_macro", "year"].empty:
            yr_cat.loc[yr_cat["type_year"] == "initializeyear_macro", "year"] = (
                baseyear_macro
            )

    yr_pair: list[list[Union[int, str]]] = []
    for yr in years_new:
        yr_pair.append([yr, yr])
        yr_pair.append(["cumulative", yr])

    yr_cat = (
        pd.concat(
            [yr_cat, pd.DataFrame(yr_pair, columns=["type_year", "year"])],
            ignore_index=True,
        )
        .sort_values("year")
        .reset_index(drop=True)
    )

    # A.6. Changing the cumulative years based on the new first model year
    if "firstmodelyear" in set(yr_cat["type_year"]):
        firstyear_new = int(yr_cat.loc[yr_cat["type_year"] == "firstmodelyear", "year"])
        yr_cat = yr_cat.drop(
            yr_cat.loc[
                (yr_cat["type_year"] == "cumulative") & (yr_cat["year"] < firstyear_new)
            ].index
        )
    sc_new.add_set("cat_year", yr_cat)

    # IV.B) Copying all other sets
    set_list = [s for s in sc_ref.set_list() if "year" not in s]
    # Sets with one index set
    index_list = [x for x in set_list if not isinstance(sc_ref.set(x), pd.DataFrame)]
    for set_name in index_list:
        if set_name not in sc_new.set_list():
            sc_new.init_set(set_name, idx_sets=None, idx_names=None)
        sc_new.add_set(set_name, sc_ref.set(set_name).tolist())

    # The rest of the sets

    for set_name in [x for x in set_list if x not in index_list]:
        new_set = [x for x in sc_ref.idx_sets(set_name) if x not in sc_ref.set_list()]
        if set_name not in sc_new.set_list() and not new_set:
            sc_new.init_set(
                set_name,
                idx_sets=sc_ref.idx_sets(set_name),
                idx_names=sc_ref.idx_names(set_name),
            )
        sc_new.add_set(set_name, sc_ref.set(set_name))

    sc_new.commit("sets added!")
    log.info("All the sets updated and added to the new scenario")


def next_step_bigger_than_previous(x: list[int], i: int) -> bool:
    return x[i + 1] - x[i] > x[i] - x[i - 1]


# %% V) Adding new years to parameters
def add_year_par(
    sc_ref: Scenario,
    sc_new: Scenario,
    yrs_new: list[int],
    parname: str,
    reg_list: list[str],
    firstyear_new: int,
    extrapolate: bool = False,
    rewrite: bool = True,
    unit_check: bool = True,
    extrapol_neg: Optional[float] = None,
    bound_extend: bool = True,
) -> None:
    """Add new years to parameters.

    This function adds additional years to a parameter. The value of the
    parameter for additional years is calculated mainly by interpolating and
    extrapolating data from existing years.

    See :meth:`add_year` for parameter descriptions.

    """
    #  V.A) Initialization and checks
    par_list_new = sc_new.par_list()
    idx_names = sc_ref.idx_names(parname)
    horizon = sorted([int(x) for x in list(set(sc_ref.set("year")))])
    node_col = [x for x in idx_names if x in ["node", "node_loc", "node_rel"]]
    year_list = [
        x for x in idx_names if x in ["year", "year_vtg", "year_act", "year_rel"]
    ]

    if parname not in par_list_new:
        sc_new.check_out()
        sc_new.init_par(
            parname,
            idx_sets=sc_ref.idx_sets(parname),
            idx_names=sc_ref.idx_names(parname),
        )
        sc_new.commit("New parameter initiated!")

    par_old = sc_ref.par(parname, filters={node_col[0]: reg_list} if node_col else None)
    par_new = sc_new.par(parname, filters={node_col[0]: reg_list} if node_col else None)
    sort_order = (
        [
            node_col[0],
            "technology",
            "commodity",
            "mode",
            "emission",
        ]
        + year_list
        if node_col
        else ["technology", "commodity"] + year_list
    )
    nodes = par_old[node_col[0]].unique().tolist() if node_col else ["N/A"]

    if not par_new.empty and not rewrite:
        log.info(
            f"Parameter {parname} already has data in new scenario and left "
            f"unchanged for node(s): {reg_list}"
        )
        return
    if par_old.empty:
        log.info(
            f"Parameter {parname} is empty in reference scenario for node(s): "
            + repr(reg_list)
        )
        return

    # Sorting the data to make it ready for dataframe manipulation
    sort_order = [x for x in sort_order if x in idx_names]
    if sort_order:
        par_old = par_old.sort_values(sort_order).reset_index(drop=True)
        rem_idx = [x for x in par_old.columns if x not in sort_order]
        par_old = par_old.reindex(columns=sort_order + rem_idx)

    sc_new.check_out()
    if not par_new.empty and rewrite:
        log.info(
            f"Parameter {parname} is being removed from new scenario to be updated for "
            f"node(s) in {nodes}"
        )
        sc_new.remove_par(parname, par_new)

    # A uniform "unit" for values in different years
    if "unit" in par_old.columns and unit_check:
        par_old = unit_uniform(par_old)
    #   ---------------------------------------------------------------------------
    #   V.B) Adding new years to a parameter based on time-related indexes
    #   V.B.1) Parameters with no time index
    if len(year_list) == 0:
        sc_new.add_par(parname, par_old)
        sc_new.commit(parname)
        log.info(
            f"Parameter {parname} just copied to new scenario since has no time-related"
            "entries"
        )

    #   V.B.2) Parameters with one index related to time
    elif len(year_list) == 1:
        year_col = year_list[0]
        df = par_old.copy()
        df_y = interpolate_1d(
            df,
            yrs_new,
            horizon,
            year_col,
            "value",
            extrapolate,
            extrapol_neg,
            bound_extend,
        )
        sc_new.add_par(parname, df_y)
        sc_new.commit(" ")
        log.info(f"Parameter {parname} copied and new years added for node(s): {nodes}")

    #   V.B.3) Parameters with two indexes related to time (such as 'input')
    elif len(year_list) == 2:
        year_col = "year_act"
        year_ref = [x for x in year_list if x != year_col][0]

        year_diff = [
            x
            for x in horizon[1:-1]
            if next_step_bigger_than_previous(horizon, horizon.index(x))
        ]
        log.info(f"Parameter {parname} is being added for node(s): {nodes}")

        # Flagging technologies that have lifetime for adding new timesteps
        yr_list = [int(x) for x in set(sc_new.set("year")) if int(x) > firstyear_new]
        min_step = min(np.diff(sorted(yr_list)))
        par_tec = sc_new.par("technical_lifetime", {"node_loc": nodes})
        # Technologies with lifetime bigger than minimum time interval
        par_tec = par_tec.loc[par_tec["value"] > min_step]
        df = par_old.copy()

        tec_list = (
            []
            if parname == "relation_activity"
            else [
                t
                for t in (set(df["technology"]))
                if t in list(set(par_tec["technology"]))
            ]
        )

        df_y = interpolate_2d(
            df,
            yrs_new,
            horizon,
            year_ref,
            year_col,
            tec_list,
            par_tec,
            "value",
            extrapolate,
            extrapol_neg,
            year_diff,
            bound_extend,
        )
        sc_new.add_par(parname, df_y)
        sc_new.commit(parname)
        log.info(f"Parameter {parname} copied and new years added for node(s): {nodes}")


# %% VI) Required functions


# FIXME reduce complexity 18 → ≤13
def interpolate_1d(  # noqa: C901
    df: pd.DataFrame,
    yrs_new: list[int],
    horizon: list[int],
    year_col: str,
    value_col: str = "value",
    extrapolate: bool = False,
    extrapol_neg: Optional[float] = None,
    bound_extend: bool = True,
):
    """Interpolate data with one year dimension.

    This function receives a parameter data as a dataframe, and adds new data
    for the additonal years by interpolation and extrapolation.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe of the parameter to which new years to be added.
    yrs_new : list of int
        New years to be added.
    horizon: list of int
        The horizon of the reference scenario.
    year_col : str
        The header of the column to which the new years should be added, e.g.
        `'year_act'`.
    value_col : str
        The header of the column containing values.
    extrapolate : bool
        Allow extrapolation when a new year is outside the parameter years.
    extrapol_neg : bool
        Allow negative values obtained by extrapolation.
    bound_extend : bool
        Allow extrapolation of bounds for new years
    """
    horizon_new = sorted(horizon + yrs_new)
    idx = [x for x in df.columns if x not in [year_col, value_col]]
    if not df.empty:
        df2 = df.pivot_table(index=idx, columns=year_col, values=value_col)
        df2_int_column_list = [int(column) for column in df2.columns]

        # To sort the new years smaller than the first year for
        # extrapolation (e.g. 2025 values are calculated first; then
        # values of 2015 based on 2020 and 2025)
        year_before = sorted(
            [x for x in yrs_new if x < min(df2_int_column_list)], reverse=True
        )
        if year_before and extrapolate:
            for y in year_before:
                yrs_new.insert(len(yrs_new), yrs_new.pop(yrs_new.index(y)))

        for yr in yrs_new:
            extrapol = True if yr > max(horizon) else extrapolate

            # a) If this new year greater than modeled years, do extrapolation
            if yr > max(df2_int_column_list) and extrapol:
                if yr == horizon_new[horizon_new.index(max(df2_int_column_list)) + 1]:
                    year_pre = max([x for x in df2_int_column_list if x < yr])

                    if len([x for x in df2_int_column_list if x < yr]) >= 2:
                        year_pp = max([x for x in df2_int_column_list if x < year_pre])
                        df2[yr] = intpol(
                            df2[year_pre], df2[year_pp], year_pre, year_pp, yr
                        )

                        if bound_extend:
                            df2[yr] = df2[yr].fillna(df2[year_pre])

                        df2[yr][np.isinf(df2[year_pre])] = df2[year_pre]
                        if (
                            not df2[yr].loc[(df2[yr] < 0) & (df2[year_pre] >= 0)].empty
                            and extrapol_neg
                        ):
                            df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0), yr] = (
                                df2.loc[(df2[yr] < 0) & (df2[year_pre] >= 0), year_pre]
                                * extrapol_neg
                            )
                    else:
                        df2[yr] = df2[year_pre]

            # b) If the new year is smaller than modeled years, extrapolate
            elif yr < min(df2_int_column_list) and extrapol:
                year_next = min([x for x in df2_int_column_list if x > yr])

                # To make sure the new year is not two steps smaller
                cond = year_next == horizon_new[horizon_new.index(yr) + 1]

                if len([x for x in df2_int_column_list if x > yr]) >= 2 and cond:
                    year_nn = min([x for x in df2_int_column_list if x > year_next])
                    df2[yr] = intpol(
                        df2[year_next], df2[year_nn], year_next, year_nn, yr
                    )
                    df2[yr][np.isinf(df2[year_next])] = df2[year_next]
                    if (
                        not df2[yr].loc[(df2[yr] < 0) & (df2[year_next] >= 0)].empty
                        and extrapol_neg
                    ):
                        df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0), yr] = (
                            df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0), year_next]
                            * extrapol_neg
                        )

                elif bound_extend and cond:
                    df2[yr] = df2[year_next]

            # c) Otherise, do intrapolation
            elif yr > min(df2_int_column_list) and yr < max(df2_int_column_list):
                year_pre = max([x for x in df2_int_column_list if x < yr])
                year_next = min([x for x in df2_int_column_list if x > yr])
                df2[yr] = intpol(df2[year_pre], df2[year_next], year_pre, year_next, yr)

                # Extrapolate for new years if the value exists for the
                # previous year but not for the next years
                # TODO: here is the place that should be changed if the
                # new year should go to the time step before the existing one
                if [x for x in df2_int_column_list if x > year_next]:
                    year_nn = min([x for x in df2_int_column_list if x > year_next])
                    df2[yr] = df2[yr].fillna(
                        intpol(df2[year_next], df2[year_nn], year_next, year_nn, yr)
                    )
                    if (
                        not df2[yr].loc[(df2[yr] < 0) & (df2[year_next] >= 0)].empty
                        and extrapol_neg
                    ):
                        df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0), yr] = (
                            df2.loc[(df2[yr] < 0) & (df2[year_next] >= 0), year_next]
                            * extrapol_neg
                        )

                if bound_extend:
                    df2[yr] = df2[yr].fillna(df2[year_pre])
                mask = np.isinf(df2[year_pre])
                df2.loc[mask, str(yr)] = df2[year_pre]

        df2 = (
            pd.melt(
                df2.reset_index(),
                id_vars=idx,
                value_vars=[x for x in df2.columns if x not in idx],
                var_name=year_col,
                value_name=value_col,
            )
            .dropna(subset=[value_col])
            .reset_index(drop=True)
        )
        df2 = df2.sort_values(idx).reset_index(drop=True)
    else:
        log.warning("The submitted dataframe is empty, so returned empty results")
        df2 = df
    return df2


# %% VI.B) Interpolating parameters with two dimensions related to time


# FIXME reduce complexity 38 → ≤13
def interpolate_2d(  # noqa: C901
    df: pd.DataFrame,
    yrs_new: list[int],
    horizon: list[int],
    year_ref: str,
    year_col: str,
    tec_list: list[str],
    par_tec: pd.DataFrame,
    value_col: str = "value",
    extrapolate: bool = False,
    extrapol_neg: Optional[float] = None,
    year_diff: Optional[list[int]] = None,
    bound_extend: bool = True,
):
    """Interpolate parameters with two dimensions related year.

    This function receives a dataframe that has 2 time-related columns (e.g.,
    "input" or "relation_activity"), and adds new data for the additonal years
    in both time-related columns by interpolation and extrapolation.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe of the parameter to which new years to be added.
    yrs_new : list of int
        New years to be added.
    horizon: list of int
        The horizon of the reference scenario.
    year_ref : str
        The header of the first column to which the new years should be added,
        e.g. `'year_vtg'`.
    year_col : str
        The header of the column to which the new years should be added, e.g.
        `'year_act'`.
    tec_list : list of str
        List of technologies in the parameter ``technical_lifetime``.
    par_tec : pandas.DataFrame
        Parameter ``technical_lifetime``.
    value_col : str
        The header of the column containing values.
    extrapolate : bool
        Allow extrapolation when a new year is outside the parameter years.
    extrapol_neg : bool
        Allow negative values obtained by extrapolation.
    year_diff : list of int
        List of model years with different time intervals before and after them
    bound_extend : bool
        Allow extrapolation of bounds for new years based on one data point
    """

    def idx_check(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        return df1.loc[df1.index.isin(df2.index)]

    if df.empty:
        log.warning("The submitted dataframe is empty, so returned empty results")
        return df

    df_tec = df.loc[df["technology"].isin(tec_list)]
    idx = [x for x in df.columns if x not in [year_col, value_col]]
    df2 = df.pivot_table(index=idx, columns=year_col, values="value")
    df2_tec = df_tec.pivot_table(index=idx, columns=year_col, values="value")
    df2_int_column_list = [int(column) for column in df2.columns]

    # -------------------------------------------------------------------------
    # First, changing the time interval for the transition period
    # (e.g., year 2010 in old R11 model transits from 5 year to 10 year)
    horizon_new = sorted(horizon + [x for x in yrs_new if x not in horizon])
    yr_diff_new = [
        x
        for x in horizon_new[1:-1]
        if next_step_bigger_than_previous(horizon_new, horizon_new.index(x))
    ]

    # Generating duration_period_sum matrix for masking
    df_dur = pd.DataFrame(
        index=horizon_new[:-1], columns=[str(year) for year in horizon_new[1:]]
    )
    for i in df_dur.index.astype(str):
        for j in [x for x in df_dur.columns if x > i]:
            df_dur.loc[i, j] = int(j) - int(i)

    # Adding data for new transition year
    if yr_diff_new and tec_list and year_diff not in yr_diff_new:
        yrs = [x for x in horizon if x <= yr_diff_new[0]]
        year_next = min([x for x in df2_int_column_list if x > yr_diff_new[0]])
        df_yrs = slice_df(df2_tec, idx, year_ref, yrs, None)
        if yr_diff_new[0] in df2_int_column_list:
            df_yrs = df_yrs.loc[~pd.isna(df_yrs[yr_diff_new[0]]), :]
            df_yrs = pd.concat(
                [df_yrs, slice_df(df2_tec, idx, year_ref, [year_next], None)]
            ).reset_index()
            df_yrs = df_yrs.sort_values(idx).set_index(idx)

        for yr in sorted(
            [
                int(x)
                for x in list(set(df_yrs.reset_index()[year_ref]))
                if int(x) < year_next
            ]
        ):
            yr_next = min([x for x in horizon_new if x > yr])
            d = slice_df(df_yrs, idx, year_ref, [yr], None)
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

        cond1 = df_dur.index <= yr_diff_new[0]
        cond2 = df_dur.columns.astype(int) >= year_next
        subt = yr_diff_new[0] - horizon_new[horizon_new.index(yr_diff_new[0]) - 1]
        df_dur.loc[cond1, cond2] = df_dur.loc[cond1, cond2] - subt
    # -------------------------------------------------------------------------
    # Second, adding year_act of new years if year_vtg is in existing years
    for yr in yrs_new:
        extrapol = True if yr > max(horizon) else extrapolate

        # a) If this new year is greater than modeled years, do extrapolation
        if yr > horizon_new[horizon_new.index(max(df2_int_column_list))] and extrapol:
            year_pre = max([x for x in df2_int_column_list if x < yr])
            year_pp = max([x for x in df2_int_column_list if x < year_pre])

            df2[yr] = intpol(df2[year_pre], df2[year_pp], year_pre, year_pp, yr)
            df2[yr][np.isinf(df2[year_pre].shift(+1))] = df2[year_pre].shift(+1)
            df2[yr] = df2[yr].fillna(df2[year_pre])

            k = horizon_new.index(yr)
            if yr - horizon_new[k - 1] >= horizon_new[k - 1] - horizon_new[k - 2]:
                df2[yr].loc[
                    (pd.isna(df2[year_pre].shift(+1)))
                    & (~pd.isna(df2[year_pp].shift(+1)))
                ] = np.nan
            cond = (df2[yr] < 0) & (df2[year_pre].shift(+1) >= 0)
            if not df2[yr].loc[cond].empty and extrapol_neg:
                df2.loc[cond, yr] = df2.loc[cond, year_pre] * extrapol_neg

        # b) Otherwise, do intrapolation
        elif yr > min(df2_int_column_list) and yr < max(df2_int_column_list):
            year_pre = max([x for x in df2_int_column_list if x < yr])
            year_next = min([x for x in df2_int_column_list if x > yr])

            df2[yr] = intpol(df2[year_pre], df2[year_next], year_pre, year_next, yr)
            df2_t = df2.loc[df2_tec.index, :].copy()

            # This part calculates the missing value if only the previous
            # timestep has a value (and not the next)
            if tec_list:
                cond = (pd.isna(df2_t[yr])) & (~pd.isna(df2_t[year_pre]))
                df2_t.loc[cond, yr] = intpol(
                    df2_t[year_pre],
                    df2_t[year_next].shift(-1),
                    year_pre,
                    year_next,
                    yr,
                )

                # Treating technologies with phase-out in model years
                if [x for x in df2_int_column_list if x < year_pre]:
                    year_pp = max([x for x in df2_int_column_list if x < year_pre])
                    cond3 = (pd.isna(df2_t[yr])) & (~pd.isna(df2_t[year_pre]))
                    cond4 = pd.isna(df2_t[year_pre].shift(-1))

                    df2_t.loc[cond3 & cond4, yr] = intpol(
                        df2_t[year_pre], df2_t[year_pp], year_pre, year_pp, yr
                    )
                    cond = (df2_t[yr] < 0) & (df2_t[year_pre] >= 0)
                    if not df2_t[yr].loc[cond].empty and extrapol_neg:
                        df2_t.loc[cond, yr] = df2_t.loc[cond, year_pre] * extrapol_neg
                df2.loc[df2_tec.index, :] = df2_t
            df2.loc[np.isinf(df2[year_pre]), yr] = df2[year_pre]
        df2 = df2.reindex(sorted([column for column in df2.columns]), axis=1)

    # -------------------------------------------------------------------------
    # Third, adding year_vtg of new years
    for yr in yrs_new:
        # a) If this new year is greater than modeled years, do extrapolation
        if yr > max(horizon):
            year_pre = horizon_new[horizon_new.index(yr) - 1]
            year_pp = horizon_new[horizon_new.index(yr) - 2]
            df_pre = slice_df(df2, idx, year_ref, [year_pre], yr)
            df_pp = slice_df(df2, idx, year_ref, [year_pp], yr)
            df_yr: pd.DataFrame = intpol(
                df_pre, idx_check(df_pp, df_pre), year_pre, year_pp, yr
            )  # type: ignore
            df_yr[np.isinf(df_pre)] = df_pre

            # For those technolofies with one value for each year
            df_to_fill_nans: pd.DataFrame = intpol(
                df_pre, df_pp.shift(+1, axis=1), year_pre, year_pp, yr
            )  # type: ignore
            df_yr.loc[pd.isna(df_yr[yr])] = df_to_fill_nans.shift(+1, axis=1)
            df_yr[pd.isna(df_yr)] = df_pre

            if extrapol_neg:
                df_yr[(df_yr < 0) & (df_pre >= 0)] = df_pre * extrapol_neg
            df_yr.loc[:, df_yr.columns < str(yr)] = np.nan

        # c) Otherwise, do intrapolation
        elif yr > min(df2_int_column_list) and yr < max(horizon):
            year_pre = horizon_new[horizon_new.index(yr) - 1]
            year_next = min([x for x in horizon if x > yr])

            df_pre = slice_df(df2, idx, year_ref, [year_pre], yr)
            df_next = slice_df(df2, idx, year_ref, [year_next], yr)
            df_yr = (
                pd.concat((df_pre, idx_check(df_next, df_pre)), axis=0)
                .groupby(level=idx)
                .mean()
            )
            if df_yr.empty:
                continue
            if not df_yr.empty and yr not in df_yr.columns:
                df_yr[yr] = np.nan
                # TODO: here is the place that should be changed if the
                # new year should go to the time step before the existing one
                if bound_extend and not df_next.empty:
                    df_yr[yr] = df_yr[year_next]
                elif bound_extend and not df_pre.empty:
                    df_yr[yr] = df_yr[year_pre]

            else:
                df_yr[yr] = df_yr[yr].fillna(df_yr[[year_pre, year_next]].mean(axis=1))
            df_yr[np.isinf(df_pre)] = df_pre

            # Creating a mask to remove extra values
            df_count = pd.DataFrame(
                {
                    "c_pre": df_pre.count(axis=1),
                    "c_next": idx_check(df_next, df_pre).count(axis=1),
                },
                index=df_yr.index,
            )

            for i in df_yr.index:
                # Mainly for cases of two new consecutive new years
                if ~np.isnan(df_count["c_next"][i]):
                    df_yr[year_pre] = np.nan
                    # For the rest
                    if df_count["c_pre"][i] < df_count["c_next"][i] + 2:
                        mask_df(df_yr, i, df_count["c_pre"][i], np.nan)

                # For technologies phasing out before the end of horizon
                elif np.isnan(df_count["c_next"][i]):
                    df_yr.loc[i, :] = df_pre.loc[i, :].shift(+1)
                    if tec_list:
                        mask_df(df_yr, i, df_count["c_pre"][i] + 1, np.nan)
                    else:
                        mask_df(df_yr, i, df_count["c_pre"][i], np.nan)

        else:
            continue

        df2 = pd.concat([df2, df_yr])
        df2 = df2.reindex(sorted(df2.columns), axis=1).sort_index()
    # -------------------------------------------------------------------------
    # Forth: final masking based on technical lifetime
    if tec_list and not df_dur.empty:
        df3 = (
            df2.loc[df2.index.get_level_values("technology").isin(tec_list), :]
            .copy()
            .dropna(how="all")
        )
        idx_list = list(set(df3.index.get_level_values(year_ref)))
        for y in sorted([x for x in idx_list if x in df_dur.index]):
            df3.loc[
                df3.index.get_level_values(year_ref).isin([y]),
                df3.columns.isin(df_dur.columns),
            ] = df_dur.loc[y, df_dur.columns.isin(df3.columns)].values
        node_column = [x for x in idx if any(y in x for y in ["node", "node_loc"])][0]
        df3 = (
            df3.reset_index()
            .set_index([node_column, "technology", year_ref])
            .sort_index(level=1)
        )
        par_t = par_tec.set_index(["node_loc", "technology", year_ref]).sort_index(
            level=1
        )

        for i in [x for x in par_t.index if x in df3.index]:
            df3.loc[i, "lifetime"] = par_t.loc[i, "value"].copy()

        df3 = df3.reset_index().set_index(idx).dropna(subset=["lifetime"]).sort_index()
        for i in df3.index:
            df2.loc[i, df3.loc[i, :] >= int(df3.loc[i, "lifetime"])] = np.nan

        # Removing extra values from non-lifetime technologies
        for i in [x for x in df2.index if x not in df3.index]:
            condition = df2.loc[[i]].index.get_level_values(year_ref)[0]
            df2.loc[i, df2.columns > condition] = np.nan

    df_par = pd.melt(
        df2.reset_index(),
        id_vars=idx,
        value_vars=[x for x in df2.columns if x not in idx],
        var_name=year_col,
        value_name="value",
    ).dropna(subset=["value"])
    df_par = df_par.sort_values(idx).reset_index(drop=True)
    return df_par
