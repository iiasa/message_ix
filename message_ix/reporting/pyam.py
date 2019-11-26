from logging import getLogger

from ixmp.reporting.computations import (
    concat as ixmp_concat,
    write_report as ixmp_write_report,
)
import pandas as pd
from pyam import IAMC_IDX, IamDataFrame, concat as pyam_concat


log = getLogger(__name__)


def as_pyam(scenario, quantities, year_time_dim, drop=[], collapse=None):
    """Return a :class:`pyam.IamDataFrame` containing *quantities*.

    Warnings are logged if the arguments result in additional, unhandled
    columns in the
    resulting data frame that are not part of the IAMC spec.

    Raises
    ------
    ValueError
        If the resulting data frame has duplicate values in the standard IAMC
        index columns. :class:`pyam.IamDataFrame` cannot handle this data.

    See also
    --------
    message_ix.reporting.Reporter.convert_pyam
    """
    # TODO, this should check for any viable container
    if not isinstance(quantities, list):
        quantities = [quantities]

    # If collapse is not provided, it is a pass-through
    collapse = collapse or (lambda df: df)

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
           .pipe(collapse) \
           .drop(drop, axis=1)

    # Raise exception for non-unique data
    duplicates = df.duplicated(subset=set(df.columns) - {'value'})
    if duplicates.any():
        raise ValueError('Duplicate IAMC indices cannot be converted:\n'
                         + str(df[duplicates]))

    # Warn about extra columns
    extra = sorted(set(df.columns) - set(IAMC_IDX + ['year', 'time', 'value']))
    if extra:
        log.warning('Extra columns {!r} when converting {} to IAMC format'
                    .format(extra, [q.name for q in quantities]))

    return IamDataFrame(df)


# Computations that operate on pyam.IamDataFrame inputs

def concat(*args):
    """Concatenate *args*, which must be :class:`pyam.IamDataFrame`."""
    if isinstance(args[0], IamDataFrame):
        return pyam_concat(args)
    else:
        return ixmp_concat(args)


def write_report(quantity, path):
    """Write the report identified by *key* to the file at *path*.

    If *quantity* is a :class:`pyam.IamDataFrame` and *path* ends with '.csv'
    or '.xlsx', use :mod:`pyam` methods to write the file to CSV or Excel
    format, respectively. Otherwise, equivalent to
    :meth:`ixmp.reporting.computations.write_report`.
    """
    if not isinstance(quantity, IamDataFrame):
        return ixmp_write_report(quantity, path)

    if path.suffix == '.csv':
        quantity.to_csv(path)
    elif path.suffix == '.xlsx':
        quantity.to_excel(path, merge_cells=False)
    else:
        raise ValueError('pyam.IamDataFrame can be written to .csv or .xlsx, '
                         'not {}'.format(path.suffix))


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
