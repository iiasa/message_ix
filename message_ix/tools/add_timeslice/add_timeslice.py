"""
This script receives a MESSAGEix scenario and an input data (currently only Excel)
file for the input data / config for sub-annual time slices, and does the following:
    1- Configures data of time slices (names, duration, parent, temporal level).
    2- Identifies technolgies that must be represented at the time slice level.
    3- Adds time slices to relevant parameters, e.g., "output", "input",
    "capacity_factor", "var_cost" etc., for relevant technologies.

Notice: for the global/national models with "relation_activity" used for emissions,
shares, etc., this script must be run based on modifications suggested in PR#680 to
allow for the index of "time" being added to relations via new parameters like
"relation_activity_time", etc.
"""

from datetime import datetime
from timeit import default_timer as timer
from typing import Any, Optional, Union

import pandas as pd

from message_ix import Scenario

# Parameters that should get the same value as "year" for time slices
# Notice: this list is applied for all time-slice technologes then the input data for
# some technologies can be updated from the input data file
par_equal = [
    "input",
    "output",
    "capacity_factor",
    "var_cost",
    "growth_activity_up",
    "growth_activity_lo",
    "level_cost_activity_soft_up",
    "level_cost_activity_soft_lo",
    "soft_activity_lo",
    "soft_activity_up",
]

# Parameters with values from "year" to be divided equally between time slices
# Notice: this configuration is added for all time-slice technologes. If it is
# desired to divide the value from "year" non-equally the setup should be added
# through the input data file (see the sheet for "demand", for example)
par_divide = [
    # "demand",  # "demand" is treated in Excel
    "historical_activity",
    "bound_activity_lo",
    "bound_activity_up",
    "initial_activity_up",
    "initial_activity_lo",
    "abs_cost_activity_soft_up",
    "abs_cost_activity_soft_lo",
]

# Parameters that should be removed for time-slice technologies
par_ignore: list[str] = []

interval = 50  # intervals for commiting input data to the database
# (This has no impact on results, just adds data in chunks)

set_update = True  # if True, adds time slices and set adjustments
node_exlude = ["World"]  # nodes to be excluded from the timeslicing

# Adjustments before adding time slices
# Remove entries of zero in "input" and "output" for time-slice commodities
remove_zero_input_output = True
remove_old_time_lvl = True  # if True, removes old temporal mapping


def configure_inputdata(
    data_file: pd.ExcelFile,
    n_time: int,
    nodes: list[str],
    par_list: list[str],
    additional_hierarchy: Optional[bool] = False,
) -> tuple[list[float], pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    Reads input data configuration from a data file (e.g., Excel), formats data, and
    return dataframes. The code can resample the input data to reduce the number of
    time slices, e.g., from 48 to 12.

    Parameters
    ----------
    data_file : ExcelFile
        Input configuration file.
    n_time : int
        Number of time slices.
    nodes : list of str
        Nodes to which time slices should be added.
    par_list : list of str
        message_ix parameters that their configuration data must be read from
        the Excel file to format time slice index.
    additional_hierarchy : bool, optional
        If there are multiple hierarchical temporal levels. The default is False.

    Returns
    -------
    duration : list
        List of duration time for each "time" for parameter "duraiton_time".
    df_time : DataFrame
        Configuration for time slices, their duration, and hirerachical mapping.
    dict_xls : dict
        Dictionary of parameters with time slices and their updated values.
    """
    # Converting time series based on the number of time slices
    df_time = data_file.parse("map_temporal_hierarchy", converters={"time": str})
    df_time = df_time.loc[df_time["lvl_temporal"] != "Sum"]
    n_xls = len(df_time["time"])
    dur = df_time["duration_time"]
    length = int(n_xls / n_time)

    # Parameters to be formatted by data from Excel
    par_list = [x for x in data_file.sheet_names if x in par_list]  # type: ignore

    dict_xls = {}
    # Reading data and updating values either using a "rate" or direct "value"
    for p in par_list:
        df_xls = data_file.parse(p, index_col=0)

        # Creating a new dataframe and converting data if needed. This is done, e.g.,
        # if the Excel data has 48 time slice but the desired number is 16.
        new = pd.DataFrame(index=range(1, n_time + 1), columns=df_xls.columns)

        for col, rate in df_xls.loc["rate", :].to_dict().items():
            assert isinstance(col, str)
            df_xls = df_xls.loc[df_xls.index != "rate"]
            # Looping over each cluster of time slices that must be merged
            for z, i in enumerate(list(range(0, n_xls, length))):
                # If the value in Excel is a rate, then sum them for each cluster
                if rate == "Yes":
                    new.loc[z + 1, col] = float(
                        df_xls.iloc[i : i + length, :][col].sum()
                    )
                # If the value in Excel is not a rate, then average for each cluster
                elif rate == "No":
                    new.loc[z + 1, col] = float(
                        df_xls.iloc[i : i + length, :][col].mean()
                    )
            new.loc["rate", col] = rate

        # Populating data for other nodes, if "all" is passed as node name
        for col in new.columns:
            if col.split(",")[0] == "all":
                for node in nodes:
                    c = node + "," + col.split(",")[1]
                    new[c] = new.loc[:, col]
                new = new.drop(col, axis=1)

        dict_xls[p] = new

    # Calculating duration of each time slice and round it by 8 decimals
    duration = [round(x, 8) for x in dur.groupby(dur.index // length).sum()]

    # Updating "duration_time" in the table of configuration and pick useful columns
    df_time = df_time.loc[0 : n_time - 1, :]
    df_time["duration_time"] = duration
    df_time = df_time[["lvl_temporal", "time_parent", "time", "duration_time"]]

    # Adding additional hierarchy if needed (e.g., if there is day, week, season)
    if additional_hierarchy:
        df = data_file.parse("map_temporal_hierarchy")
        df = df.loc[~df["lvl_temporal"].isin(set(df_time["lvl_temporal"]))].copy()
        new_times = [x for x in set(df["time"]) if x not in set(df_time["time"])]

        # Appending new time slices
        df_time = pd.concat([df_time, df.loc[df["time"].isin(new_times)]])

        # Adding additional temporal hierarchy
        for ti in df_time["time"].to_list():
            d = df.loc[df["time"] == ti].copy()
            d["duration_time"] = float(
                df_time.loc[df_time["time"] == ti, "duration_time"].iloc[0]
            )
            df_time = pd.concat([df_time, d], ignore_index=True)
    return duration, df_time, dict_xls


def setup_timeslice(
    scenario: Scenario, df: pd.DataFrame, remove_old_time_lvl: bool = True
) -> None:
    """
    Update time-reated sets and "duration_time" after adding new time slices

    Parameters
    ----------
    scenario : message_ix.Scenario
    df : DataFrame
        A table including time slice names, and their duration, parent time, and
        temporal level.
    remove_old_time_lvl : bool, optional
        If True, removes existing "map_temporal_hierarchy", before adding a new
        one. The default is False.
    """
    scenario.check_out()

    # Adding sub-annual time slices to the set 'time'
    for t in df["time"].tolist():
        scenario.add_set("time", t)

    # Adding sub-annual time levels to the set 'lvl_temporal'
    for lvl in set(df["lvl_temporal"]):
        scenario.add_set("lvl_temporal", lvl)

    # Removing existing temporal hierarchy, if needed.
    if remove_old_time_lvl:
        df_ref = scenario.set("map_temporal_hierarchy")
        scenario.remove_set("map_temporal_hierarchy", df_ref)

    # Adding new temporal hierarchy
    scenario.add_set("map_temporal_hierarchy", df)
    print("- All time-related sets configured for new time slices.")

    # Removing old duration times
    df_ref = scenario.par("duration_time")
    scenario.remove_par("duration_time", df_ref.loc[~(df_ref["time"] == "year"), :])

    # Adding duration time of each time slice
    df["value"] = df["duration_time"]
    scenario.add_par("duration_time", df)
    scenario.commit("time-slice sets and duration time modified")
    print('- Parameter "duration_time" updated for new time slices.')


def setup_parameters(
    scenario: Scenario, dict_xls: dict[str, pd.DataFrame], par_update: dict[str, dict]
) -> tuple[dict[str, dict], dict[str, str]]:
    """
    Read input data and setup parameters that must be modified for time slices

    Parameters
    ----------
    scenario : message_ix.Scenario
    dict_xls : dict
        A dictionary of data from Excel with keys as parameter names and value
        as DataFrames.
    par_update : dict
        A dictionary, with the key being parameters that must be modified for
        time slices, and values are members of an index (technology/commodity, etc.),
        with their multipliers for each time slice. "all" encompasses all members
        of that index.This dict includes parameters both from Excel and this script.
        (e.g., {"capacity_factor": {"all": [1, 1, 1, 1]}})

    Returns
    -------
    par_update : dict
        Updated version based on the data from Excel.
    index_cols : dict
        A dicationary of time related parameters (keys) and the main index as values
        (e.g., {"capacity_factor": "technology"}.

    """
    scenario.check_out()
    xls_pars = [x for x in dict_xls.keys() if x in scenario.par_list()]

    index_cols = {}
    for parname in set(list(par_update.keys()) + xls_pars):
        if "technology" in scenario.idx_names(parname):
            index_cols[parname] = "technology"
        elif "commodity" in scenario.idx_names(parname):
            index_cols[parname] = "commodity"
        elif "relation" in scenario.idx_names(parname):
            index_cols[parname] = "relation"

        # Treating parameters from Excel file
        if parname not in xls_pars:
            continue
        df_xls = dict_xls[parname]

        # Finding index of "year" and "node" for this parameter
        node_col = [x for x in scenario.idx_names(parname) if "node" in x][0]

        # Modifying data based on if it is a rate e.g. demand) or an absolute value
        # (e.g., capacity factor)
        for item in df_xls.columns:
            # Parameters with input data as absolute values: make existing value = 1
            if df_xls.loc["rate", item] == "No":
                if "," in item:
                    # Loading original data and replacing that with the value of 1
                    df_item = scenario.par(
                        parname,
                        {
                            index_cols[parname]: [item.split(",")[1]],
                            node_col: [item.split(",")[0]],
                        },
                    )

                else:
                    df_item = scenario.par(parname, {index_cols[parname]: [item]})
                # Assigning value of 1 to the original data to be multiplied later
                df_item["value"] = 1
                scenario.add_par(parname, df_item)

            if parname not in par_update.keys():
                par_update[parname] = {}

            # Removing index of "rate" from the dataframe and adding to data
            par_update[parname][item] = df_xls.loc[df_xls.index != "rate"][
                item
            ].tolist()
    scenario.commit("")
    print("- Input data of parameters are set up based on the data from Excel.")
    return par_update, index_cols


def get_node_tec(data_dict: dict[str, Any]) -> list[tuple[str, str]]:
    return [(k.split(",")[0], k.split(",")[1]) for k in data_dict.keys() if "," in k]


def get_node_col(scenario: Scenario, parname: str) -> str:
    return [
        x for x in scenario.idx_names(parname) if x in ["node", "node_loc", "node_rel"]
    ][0]


def get_df_ref(
    scenario_ref: Scenario,
    parname: str,
    index_col: str,
    key: str,
    item_list: Optional[list[str]],
    data_dict: dict[str, Any],
    node_tec: list,
    node_col: str,
) -> pd.DataFrame:
    if key == "all":
        df_ref = (
            scenario_ref.par(parname, {index_col: item_list, "time": "year"})
            if item_list
            else scenario_ref.par(parname, {"time": "year"})
        )

        df_ref = df_ref.loc[~df_ref[index_col].isin(data_dict.keys())]

        for x in node_tec:
            df_ref = df_ref.loc[
                (df_ref[index_col] != x[1]) & (df_ref[node_col] != x[1])
            ]
    elif "," in key:
        df_ref = scenario_ref.par(
            parname,
            {
                index_col: key.split(",")[1],
                node_col: key.split(",")[0],
                "time": "year",
            },
        )
    else:
        df_ref = scenario_ref.par(parname, {index_col: key, "time": "year"})

    return df_ref


def process_df_ref(
    scenario: Scenario,
    df_ref: pd.DataFrame,
    parname: str,
    times: list[str],
    n1: int,
    nn: int,
    tec_inp,
    tec_only_inp,
    ratio,
) -> pd.DataFrame:
    time_cols = [x for x in scenario.idx_names(parname) if "time" in x]
    df_list = []

    for ti in times[n1:nn]:
        df_new = df_ref.copy()
        for col in time_cols:
            if col == "time_origin":
                df_new.loc[df_new["technology"].isin(tec_inp), col] = ti
            elif col == "time_dest":
                df_new.loc[~df_new["technology"].isin(tec_only_inp), col] = ti
            else:
                df_new[col] = ti
        df_new["value"] *= ratio[times.index(ti)]
        df_list.append(df_new)

    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()


def configure_parameter(
    scenario: Scenario,
    parname: str,
    data_dict: dict[str, Any],
    index_col: str,
    item_list: Optional[list[str]],
    tec_inp: list[str],
    tec_only_inp: list[str],
    n1: int,
    nn: int,
    times: list[str],
    sc_ref: Optional[Scenario] = None,
) -> None:
    """
    Main function for reparameterization of the time-related parameters

    Parameters
    ----------
    scenario : message_ix.Scenario
    parname : str
        Time-related parameter being modified.
    data_dict : dict
        A dictionary with members of an index (technology/commodity, etc.) and
        their multipliers for each time slice. "all" is used for all members
        of that index.(e.g., {"all": [1, 1, 1, 1]}, or
        {"CAS,wind_ppl": [0.1, 0.4, 0.6, 0.3]}).
    index_col : str
        Index ove which populating time-related data (e.g., "technology").
    item_list : list of str, optional
        List of members of an index (e.g., list of technologies).
    tec_inp : list of str
        List of technologies with their "input" from time slices ("output" can be
        to time slices or not)
    tec_only_inp : list of str
        List of technologies with their "input" from time slices but their "output"
        does not link to time slices
    n1 : int
        Counting first inerval when using many time slices.
    nn : int
        Last interval for adding data in chunks.
    sc_ref : message_ix.Scenario, optional
        If copying data from a reference scenario. The default is None.
    times : list of str
        Sub-annual time slices.
    """
    scenario.check_out()
    if not sc_ref:
        sc_ref = scenario

    node_tec = get_node_tec(data_dict)
    node_col = get_node_col(scenario, parname)

    for key, ratio in data_dict.items():
        df_ref = get_df_ref(
            sc_ref, parname, index_col, key, item_list, data_dict, node_tec, node_col
        )

        if df_ref.empty:
            continue

        if nn >= n1:
            scenario.remove_par(parname, df_ref)

        df = process_df_ref(
            scenario, df_ref, parname, times, n1, nn, tec_inp, tec_only_inp, ratio
        )

        if not df.empty:
            scenario.add_par(parname, df)

    scenario.commit("")


def remove_data_zero(
    scenario: Scenario,
    parname: str,
    filters: dict[str, Any],
    value: Optional[float] = 0,
) -> pd.DataFrame:
    """
    Remove data from a parameter if value is equal to a certain number (e.g., 0)

    Parameters
    ----------
    scenario : message_ix.Scenario
    parname : str
        Parameter to be modified.
    filters : dict
        Subset of data in a parameter to be modified.
    value : float, optional
        Value that must be removed from filtered data. The default is 0.

    Returns
    -------
    df : DataFrame
        Removed data.
    """
    scenario.check_out()
    df = scenario.par(parname, filters)
    df = df.loc[df["value"] == value]
    scenario.remove_par(parname, df)
    scenario.commit("Spcified data removed")
    return df


def par_remove(
    scenario: Scenario,
    par_dict: dict[str, dict[str, Any]],
    verbose: Optional[bool] = True,
) -> None:
    """
    Remove a subset of some parameters if needed

    Parameters
    ----------
    sc : message_ix.Scenario
    par_dict : dict
        Data of parameters (keys), fromwhich a subset of data (values) to be removed.
    verbose : bool, optional
        Printing information. The default is True.
    """
    for parname, filters in par_dict.items():
        df = scenario.par(parname, filters)
        scenario.remove_par(parname, df)
        if verbose:
            log_message = "All" if not filters else filters
            print(f'> {log_message} data was removed from parmeter "{parname}".')


def identify_technologies(
    scenario: Scenario, commodities_time: list[str], extra_techs: Optional[list[str]]
) -> tuple[list[str], list[str], list[str]]:
    commodities = [x for x in set(scenario.set("commodity")) if x in commodities_time]
    # Technologies with an "output" for time-slice commodities
    # Representaiton model: input= to, ta ... output: ta, td)
    tec_out = list(
        set(scenario.par("output", {"commodity": commodities})["technology"])
    )
    tec_out = (
        sorted([x for x in tec_out if not any([y in x for y in extra_techs])])
        if extra_techs
        else tec_out
    )
    # Technologies with "input" from commodities represented at the time-slice level
    tec_inp = sorted(
        set(scenario.par("input", {"commodity": commodities})["technology"])
    )

    return tec_out, tec_inp, commodities


def remove_zero_tech(
    scenario: Scenario,
    tec_out: list[str],
    tec_inp: list[str],
    remove_zero_input_output: bool,
) -> tuple[list[str], list[str]]:
    if remove_zero_input_output:
        df_rem_out = set(
            remove_data_zero(scenario, "output", {"technology": tec_out})["technology"]
        )
        tec_out = sorted([x for x in tec_out if x not in df_rem_out])

        df_rem_in = set(
            remove_data_zero(scenario, "input", {"technology": tec_inp})["technology"]
        )
        tec_inp = sorted([x for x in tec_inp if x not in df_rem_in])

    return tec_out, tec_inp


def setup_par_update(
    scenario: Scenario,
    par_list: list[str],
    n_time: int,
    duration: list[float],
    tec_list: list[str],
) -> dict[str, dict[str, Any]]:
    par_update: dict[str, dict[str, list[Union[float, int]]]] = {}
    for parname in par_list:
        if parname in par_equal:
            par_update[parname] = {"all": [1] * n_time}
        elif parname in par_divide:
            par_update[parname] = {"all": duration}
        elif parname in par_ignore:
            par_remove(scenario, {parname: {"technology": tec_list}}, verbose=False)
    return par_update


def modify_parameters(
    scenario: Scenario,
    par_update: dict[str, dict],
    index_cols: dict[str, str],
    tec_list: list[str],
    tec_inp: list[str],
    tec_only_inp: list[str],
    times: list[str],
    n_time: int,
    interval: int,
) -> None:
    print("- Parameters are being modified for time slices...")
    for parname, data_dict in par_update.items():
        index_col = index_cols[parname]
        item_list = tec_list if index_col == "technology" else None

        n1 = 0
        while n1 < n_time:
            nn = min([n_time, n1 + interval - 1])
            configure_parameter(
                scenario,
                parname,
                data_dict,
                index_col,
                item_list,
                tec_inp,
                tec_only_inp,
                n1,
                nn,
                times,
            )
            print("    ", end="\r")
            print(str(nn + 1), end="\r")
            n1 += interval
        print('- Time slices added to "{}".'.format(parname))
    print("- All parameters successfully modified for time slices.")


def correct_technology_input_output(
    scenario: Scenario, tec_inp: list[str], tec_out: list[str], commodities: list[str]
) -> None:
    for tec in tec_inp:
        df = scenario.par("input", {"technology": tec})
        df = df.loc[~df["commodity"].isin(commodities)].copy()
        scenario.remove_par("input", df)
        df["time_origin"] = "year"
        scenario.add_par("input", df)
    print("- Input of time-slice technologies corrected for year-related commodities.")

    for tec in tec_out:
        df = scenario.par("output", {"technology": tec})
        df = df.loc[~df["commodity"].isin(commodities)].copy()
        scenario.remove_par("output", df)
        df["time_dest"] = "year"
        scenario.add_par("output", df)
    print("- Output of time-slice technologies corrected for year-related commodities.")


def solve_scenario(scenario: Scenario) -> None:
    print(
        'Solving scenario "{}/{}", started at {}, please wait!'.format(
            scenario.model, scenario.scenario, datetime.now().strftime("%H:%M:%S")
        )
    )
    start = timer()
    scenario.solve(solve_options={"lpmethod": "4"})
    end = timer()
    print(
        "Elapsed time for solving:",
        int((end - start) / 60),
        "min and",
        round((end - start) % 60, 2),
        "sec.",
    )
    scenario.set_as_default()


def add_timeslices(
    scenario: Scenario,
    data_file: pd.ExcelFile,
    n_time: int,
    commodities_time: list[str],
    temporal_lvls: list[str],
    add_hierarchy: Optional[bool] = True,
    extra_techs: Optional[list[str]] = [],
) -> Scenario:
    """
    Main module for adding time slice data, reparamaterization, and solving

    Parameters
    ----------
    scenario : message_ix.Scenario
        Scenario to be edited for adding time slices.
    data_file : pandas.ExcelFile
        Full path to the Excel data file.
    n_time : int
        Number of time slices (must be <= number of time slices in the data file,
        For example, if the input data has 48 time slices, this can be 48, 24, 16, or
        12 time slices)
    commodities_time : list of str
        List of commodities to be represented at the time-slice level.
        (relevant technologies will be found in the script)
    temporal_lvls : list of str
        Temporal levels for which data to be populated from the data file.
    add_hierarchy : bool, optional
        Importing multiple temporal hierarchy from data file. The default is True.
        Notice: if n_time < number of time slices in the data file, this must
        be False, i.e., only one temporal hierarchy level can be configured while
        reducing the number of time slices.
    extra_techs : list of str, optional
        Technologies (partial or full name) to be excluded from time-slice modelling.
        The default is [].

    Returns
    -------
    scenario : message_ix.Scenario
        Scenario with time slices.
    """
    # -------------------------------------------------------------------------------
    # 1) Updating MESSAGEix sets relevant to time slices
    # -------------------------------------------------------------------------------

    # Adding subannual time slices to the relevant sets
    nodes = [x for x in set(scenario.set("node")) if x not in ["World"] + node_exlude]
    duration, df_time, dict_xls = configure_inputdata(
        data_file,
        n_time,
        nodes,
        scenario.par_list(),
        additional_hierarchy=add_hierarchy,
    )
    times = df_time.loc[df_time["lvl_temporal"].isin(temporal_lvls), "time"].to_list()

    if set_update:
        # Updating sets and mappings related to "time", and parameter "duraiton_time"
        setup_timeslice(scenario, df_time)

    # -----------------------------------------------------------------------------
    # 2) Modifying relevant parameters before adding sub-annual time slices
    # -------------------------------------------------------------------------------

    # List of technologies that will have output to time slices
    # sectors/commodities represented at time slice level
    # Representaiton model (input= to, ta ... output: ta, td)
    tec_out, tec_inp, commodities = identify_technologies(
        scenario, commodities_time, extra_techs
    )

    # Excluding technologies with zero output for time-slice commodities
    # This is done because some technologies have output for certain commodities,
    # but the amount is zero.
    if remove_zero_input_output:
        tec_out, tec_inp = remove_zero_tech(
            scenario, tec_out, tec_inp, remove_zero_input_output
        )

    # Technologies with only input needed for time slices (output: 'year'/nothing)
    # Representaiton model (to='1', ta='1' --> ta='1', td='year')
    tec_only_inp = [x for x in tec_inp if x not in tec_out]

    # All technologies relevant to time slices
    tec_list = tec_out + tec_inp

    # Find relevant parameters to be modified for time slices
    par_list = [
        x
        for x in scenario.par_list()
        if "time" in scenario.idx_sets(x) and "technology" in scenario.idx_sets(x)
    ]

    scenario.check_out()
    # A dictionary for updating parameters with an index related to "time"
    # Keys are parameter names, values are members of an index (such as names of
    # technology/commodity/etc.), with a multiplier to their yearly value to convert
    # to time-related values. "all" can be passed to handle all members of the
    # examined index in one go.
    par_update = setup_par_update(scenario, par_list, n_time, duration, tec_list)
    scenario.commit("")

    # Setting up the data and values of parameters from Excel
    par_update, index_cols = setup_parameters(scenario, dict_xls, par_update)
    modify_parameters(
        scenario,
        par_update,
        index_cols,
        tec_list,
        tec_inp,
        tec_only_inp,
        times,
        n_time,
        interval,
    )

    # -------------------------------------------------------------------------
    # 3) Doing some adjustments and solving
    # -------------------------------------------------------------------------------

    scenario.check_out()
    # Finding commodities that must not be at the time slice level
    # (These are for technologies that have multiple input or output commodities
    # from which only a subset of commodities should be at the time slice level)
    # 3.1) Correcting input of tec_inp technologies
    correct_technology_input_output(scenario, tec_inp, tec_out, commodities)
    scenario.commit("Time slice modifications done.")

    # 3.3) Solving
    solve_scenario(scenario)
    return scenario


# %% Example
if __name__ == "__main__":
    import pathlib

    import ixmp as ix

    import message_ix

    mp = ix.Platform()

    # Model/scenario names
    model_ref = "Westeros Electrified"
    scenario_ref = "baseline"

    # Input data file with time slices
    xls_file = "timeslices_for_westeros.xlsx"

    # Getting the path to the data file
    here = pathlib.Path(__file__).resolve()
    path_xls = here.parent.parent.parent / "tutorial" / "westeros"

    # Time-slice related commodities and temporal levels
    commodities_time = ["electricity", "light"]
    temporal_lvls = ["season"]

    # Number of time slices (this can be <= number of time slices in the data file)
    n_time = 4

    # Loading scenario and input data
    scen_ref = message_ix.Scenario(mp, model=model_ref, scenario=scenario_ref)
    scen = scen_ref.clone(model=model_ref + "_t" + str(n_time), keep_solution=False)

    # Loading Excel data (time series)
    data_file = pd.ExcelFile(path_xls / xls_file)

    # Adding time-slice data. modifications, and solving
    add_timeslices(scen, data_file, n_time, commodities_time, temporal_lvls)
