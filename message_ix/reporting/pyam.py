from logging import getLogger
from functools import partial

import pandas as pd
from pyam import IAMC_IDX, IamDataFrame


log = getLogger(__name__)


def as_pyam(scenario, year_time_dim, quantities, drop=[], collapse=None):
    """Return a :class:`pyam.IamDataFrame` containing *quantities*."""

    # TODO, this should check for any viable container
    if not isinstance(quantities, list):
        quantities = [quantities]
        
    # Renamed automatically
    IAMC_columns = {
        'n': 'region',
        'nl': 'region',
    }

    # Convert each of *quantities* individually
    dfs = []
    for qty in quantities:
        df = qty.to_series() \
                .rename('value') \
                .reset_index() \
                .rename(columns=IAMC_columns)
        df['variable'] = qty.name
        df['unit'] = qty.attrs.get('unit', '')

        dfs.append(df)

    # Combine DataFrames
    df = pd.concat(dfs)
    # Set model and scenario columns
    df['model'] = scenario.model
    df['scenario'] = scenario.scenario

    # Set one column as 'year' or 'time' (long IAMC format); drop any other
    # columns
    year_or_time = 'year' if year_time_dim.startswith('y') else 'time'
    df = df.rename(columns={year_time_dim: year_or_time}) \
           .drop(drop, axis=1)
    if collapse:
        df = collapse(df)

    # Warn about extra columns
    extra = sorted(set(df.columns) - set(IAMC_IDX + ['year', 'time', 'value']))
    if extra:
        log.warning('Extra columns {!r} when converting {} to IAMC format'
                    .format(extra, [q.name for q in quantities]))

    return IamDataFrame(df)


# TODO: this should be a generalized function instead of many different collapse
# functions using pandas' eval
def collapse_ene_cols(df, kind):
    df['variable'] = kind + '|' + df['l'] + \
        '|' + df['c'] + '|' + df['t'] + '|' + df['m']
    rcol = 'nd' if kind == 'out' else 'no'
    df['region'] = df['region'] + '|' + df[rcol]
    df.drop(['l', 'c', 't', 'm'] + [rcol], axis=1, inplace=True)
    return df


def collapse_capacity_cols(df, kind):
    df['variable'] = kind + '|' + df['t']
    df.drop(['t'], axis=1, inplace=True)
    return df


def collapse_cost_cols(df, kind):
    df['variable'] = kind + '|' + df['t']
    df.drop(['t'], axis=1, inplace=True)
    return df


def collapse_emi_cols(df):
    df['variable'] = 'emis|' + df['e'] + '|' + df['t'] + '|' + df['m']
    df.drop(['e', 't', 'm'], axis=1, inplace=True)
    return df

AS_PYAM_ARGS = {
    'pyam:out': ('out:nl-t-ya-m-nd-c-l', 'ya', partial(collapse_ene_cols, kind='out')),
    'pyam:in': ('in:nl-t-ya-m-no-c-l', 'ya', partial(collapse_ene_cols, kind='in')),
    'pyam:cap': ('CAP:nl-t-ya', 'ya', partial(collapse_capacity_cols, kind='capacity')),
    'pyam:new_cap': ('CAP_NEW:nl-t-yv', 'yv', partial(collapse_capacity_cols, kind='new capacity')),
    'pyam:inv': ('inv:nl-t-yv', 'yv', partial(collapse_cost_cols, kind='inv cost')),
    'pyam:fom': ('fom:nl-t-ya', 'ya', partial(collapse_cost_cols, kind='fom cost')),
    'pyam:vom': ('vom:nl-t-ya', 'ya', partial(collapse_cost_cols, kind='vom cost')),
    'pyam:tom': ('tom:nl-t-ya', 'ya', partial(collapse_cost_cols, kind='total om cost')),
    'pyam:emis': ('emi:nl-t-ya-m-e', 'ya', collapse_emi_cols),
}


