# -*- coding: utf-8 -*-
"""Find all parameters related to a technology / commodity / year."""
# Sections of the code:
#
#   I. Required python packages are imported
#  II. Generic utilities for data manupulation
# III. The main function, find_tech_description()


# %% I) Importing required packages

import pandas as pd

import message_ix


# %% II) Utility functions for data manupulation
def dict_to_df(filter_dict: dict) -> pd.DataFrame:
    """Transforms the filter (given as a dictionary) into a data frame
    
    Parameter
    ----------
    filter_dict: dictionary 
    """
    if list not in [type(i) for i in filter_dict.values()]:
        filter_dict = pd.DataFrame.from_dict({k: ([v] if type(v) != list else v) for k, v in filter_dict.items()})

    filter_df = pd.DataFrame.from_dict(filter_dict)
    return filter_df


# %% III) The main function
def get_tech_description(base: message_ix.Scenario, key_filter: str, filters: dict, filename: str) -> dict[str:pd.DataFrame]:
    """Find all parameters that relate to a technology / a year/ a commodity / ect. given in the filter

    :meth:`find_tech_description` does the following:

    1. iterates through the parameter list to identify all parameters related to filters given 
    2. outputs the parameter dict to an excel file

     Parameters
    -----------
    base : message_ix.Scenario
        Reference scenario.
    key_filter : str
        filter key to look for in the database - if this key is not in the idx_names the parameter will be ignored
    filters : dict
        Filters to filter the identified parameters by
    filename : str
        path and name of technology output file
    """

    par_list = [par_name for par_name in base.par_list() if key_filter in base.idx_names(par_name)]
    par_dict = {}

    for par_name in par_list:
        _filters = {k: v for k, v in filters.items() if k in base.idx_names(par_name)}
        if len(_filters) > 0:
            _par = base.par(par_name, {**_filters})
            if not _par.empty:
                par_dict[par_name] = _par

    if filename:
        writer = pd.ExcelWriter(f'{filename}.xlsx')
        dict_to_df(filters).to_excel(writer, sheet_name='applied filters', index=False)
        for par_name, df in par_dict.items():
            df.to_excel(writer, par_name, index=False)
        writer.save()

    return par_dict
