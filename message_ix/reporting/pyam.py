from logging import getLogger

import pandas as pd
from pyam import IAMC_IDX, IamDataFrame


log = getLogger(__name__)


def as_pyam(scenario, year_time_dim, *quantities, drop=[], collapse=None):
    """Return a :class:`pyam.IamDataFrame` containing *quantities*."""

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
