import collections
import copy
import itertools
import logging
import six

import numpy as np
import pandas as pd

# globally accessible logger
_LOGGER = None


def logger():
    """Access global logger"""
    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig()
        _LOGGER = logging.getLogger()
        _LOGGER.setLevel('INFO')
    return _LOGGER


def isstr(x):
    """Returns True if x is a string"""
    return isinstance(x, six.string_types)


def isscalar(x):
    """Returns True if x is a scalar"""
    return not isinstance(x, collections.Iterable) or isstr(x)


def add_spatial_sets(scenario, data):
    """Add sets related to spatial dimensions of the model

    Parameters
    ----------
    scenario : ixmp.Scenario
    data : dict or other

    Examples
    --------
    data = {'country': 'Austria'}
    data = {'country': ['Austria', 'Germany']}
    data = {'country': {'Austria': {'state': ['Vienna', 'Lower Austria']}}}
    """
    nodes = []
    levels = []
    hierarchy = []

    def recurse(k, v, parent='World'):
        if isinstance(v, collections.Mapping):
            for _parent, _data in v.items():
                for _k, _v in _data.items():
                    recurse(_k, _v, parent=_parent)

        level = k
        children = [v] if isscalar(v) else v
        for child in children:
            hierarchy.append([level, child, parent])
            nodes.append(child)
        levels.append(level)

    for k, v in data.items():
        recurse(k, v)

    scenario.add_set("node", nodes)
    scenario.add_set("lvl_spatial", levels)
    scenario.add_set("map_spatial_hierarchy", hierarchy)


def add_temporal_sets(scenario, data):
    """Add sets related to temporal dimensions of the model

    Parameters
    ----------
    scenario : ixmp.Scenario
    data : dict or other

    Examples
    --------
    data = {'year': [2010, 2020]}
    data = {'year': [2010, 2020], 'firstmodelyear': 2020}
    """
    if 'year' not in data:
        raise ValueError('"year" must be in temporal sets')
    horizon = data['year']
    scenario.add_set("year", horizon)

    first = data['firstmodelyear'] if 'firstmodelyear' in data else horizon[0]
    scenario.add_set("cat_year", ["firstmodelyear", first])


def vintage_and_active_years(scenario):
    """Return a 2-tuple of valid pairs of vintage years and active years for
    use with data input.
    """
    horizon = scenario.set('year')
    combinations = itertools.product(horizon, horizon)
    year_pairs = [(y_v, y_a) for y_v, y_a in combinations if y_v <= y_a]
    v_years, a_years = zip(*year_pairs)
    return v_years, a_years


def make_df(base, **kwargs):
    """Combine existing data with a series of new data defined in kwargs.

    Parameters
    ----------
    base : dict, pd.Series, or pd.DataFrame
        existing dataset to append to
    """
    if not isinstance(base, (collections.Mapping, pd.Series, pd.DataFrame)):
        raise ValueError('base argument must be a dictionary or Pandas object')
    base = copy.deepcopy(base)
    if not isinstance(base, collections.Mapping):
        base = base.to_dict()
    base.update(**kwargs)
    return pd.DataFrame(base)


def multiply_df(df1, column1, df2, column2):
    '''The function merges dataframe df1 with df2 and multiplies column1 with
    column2. The function returns the new merged dataframe with the result
    of the muliplication in the column 'product'.
    '''
    cols = ['mode', 'node_loc', 'technology', 'time', 'year_act', 'year_vtg']
    cols = list(set(cols) & set(df1.columns) & set(df2.columns))
    df = df1.merge(df2, how='left', on=cols)
    df['product'] = df.loc[:, column1] * df.loc[:, column2]
    df = df.dropna(axis='index', subset=['product'])
    return df


def make_ts(df, time_col, value_col, metadata={}):
    '''The function groups the dataframe by the year specified in year_col_name
    (year_act Vs. year_vtg). It then reshapes the dataframe df to reseble the
    timeseries requirements: sets the unit, the variable name, and the
    value column to the one specified in value_col_name. it further drops all
    all additional columns.
    '''
    df = df.groupby(['node_loc', time_col], as_index=False).sum()
    for col, values in metadata.items():
        df[col] = values
    cols = ['node_loc', time_col, value_col] + list(metadata.keys())
    df = df[cols]
    rename = {
        'node_loc': 'region',
        time_col: 'year',
        value_col: 'value'
    }
    df = df.rename(columns=rename)
    df = df.dropna(axis='index', subset=['value'])
    return df


def matching_rows(df, row, match_columns=[]):
    '''The function finds all the columns in a dataframe that are specified
    in the match columns list.
    '''
    rows = np.array([True] * len(df))
    for col in match_columns:
        rows = rows & (df[col] == row[col])
    return df[rows]
