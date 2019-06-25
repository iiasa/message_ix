from logging import getLogger

import pandas as pd
from pyam import IAMC_IDX, IamDataFrame


log = getLogger(__name__)


def as_pyam(scenario, year_time_dim, quantities, drop=[], collapse=None):
    """Return a :class:`pyam.IamDataFrame` containing *quantities*.

    See also
    --------
    Reporter.as_pyam for documentation of the arguments.
    """
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


def collapse_message_cols(df, var, kind=None):
    """:meth:`as_pyam` `collapse=...` callback for MESSAGE quantities.

    Parameters
    ----------
    var : str
        Name for 'variable' column.
    kind : None or 'ene' or 'emi', optional
        Determines which other columns are combined into the 'region' and
        'variable' columns:

        - 'ene': 'variable' is
          ``'<var>|<level>|<commodity>|<technology>|<mode>'`` and 'region' is
          ``'<region>|<node_dest>'`` (if `var='out'`) or
          ``'<region>|<node_origin>'`` (if `'var='in'`).
        - 'emi': 'variable' is ``'<var>|<emission>|<technology>|<mode>'``.
        - Otherwise: 'variable' is ``'<var>|<technology>'``.

        The referenced columns are also dropped, so it is not necessary to
        provide the `drop` argument of :meth:`as_pyam`.
    """
    if kind == 'ene':
        # Region column
        rcol = 'nd' if var == 'out' else 'no'
        df['region'] = df['region'].str.cat(df[rcol], sep='|')
        df.drop(rcol, axis=1, inplace=True)

        var_cols = ['l', 'c', 't', 'm']
    elif kind == 'emi':
        var_cols = ['e', 't', 'm']
    else:
        var_cols = ['t']

    # Assemble variable column
    df['variable'] = var
    df['variable'] = df['variable'].str.cat([df[c] for c in var_cols], sep='|')

    # Drop same columns
    return df.drop(var_cols, axis=1)
