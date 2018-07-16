# -*- coding: utf-8 -*-

import numpy as np


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


def is_iter_not_string(x):
    return x if hasattr(x, '__iter__') and not is_str(x) else [x]
    #return hasattr(x, '__iter__') and not is_str(x)


def is_str(x):
    """Returns True if x is a string"""
    try:
        return isinstance(x, (str, unicode))
    except NameError:
        return isinstance(x, str)


def is_num(s):
    """Returns True if s is a number"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def numcols(df):
    dtypes = df.dtypes
    return [i for i in dtypes.index
            if dtypes.loc[i].name.startswith(('float', 'int'))]
