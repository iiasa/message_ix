from ixmp.reporting.computations import (  # noqa: F401
    product,
    write_report as ixmp_write_report
)
import pyam


def add(a, b, fill_value=0.0):
    """Sum of *a* and *b*."""
    return a.add(b, fill_value=fill_value).dropna()


def concat(*args):
    """Concatenate *args*, which must be :class:`pyam.IamDataFrame`."""
    return pyam.concat(args)


def write_report(quantity, path):
    """Write the report identified by *key* to the file at *path*.

    If *quantity* is a :class:`pyam.IamDataFrame` and *path* ends with '.csv'
    or '.xlsx', use :mod:`pyam` methods to write the file to CSV or Excel
    format, respectively. Otherwise, equivalent to
    :meth:`ixmp.reporting.computations.write_report`.
    """
    if not isinstance(quantity, pyam.IamDataFrame):
        return ixmp_write_report(quantity, path)

    if path.suffix == '.csv':
        quantity.to_csv(path)
    elif path.suffix == '.xlsx':
        quantity.to_excel(path, merge_cells=False)
    else:
        raise ValueError('pyam.IamDataFrame can be written to .csv or .xlsx, '
                         'not {}'.format(path.suffix))
