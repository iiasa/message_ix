from ixmp.reporting.computations import (  # noqa: F401
    product,
    write_report as ixmp_write_report
)
import pyam


def write_report(quantity, path):
    if not isinstance(quantity, pyam.IamDataFrame):
        return ixmp_write_report(quantity, path)

    if path.suffix == '.csv':
        quantity.to_csv(path)
    elif path.suffix == '.xlsx':
        quantity.to_excel(path, merge_cells=False)
    else:
        raise ValueError('pyam.IamDataFrame can be written to .csv or .xlsx, '
                         'not {}'.format(path.suffix))
