from functools import partial
from logging import WARNING
try:
    from pathlib import Path
except:
    from pathlib2 import Path

import pandas as pd
from pandas.testing import assert_series_equal
import pyam
import xarray as xr
from xarray.testing import assert_equal as assert_xr_equal

from message_ix import Scenario
from message_ix.reporting import Reporter, as_pyam


def test_reporter(test_mp):
    scen = Scenario(test_mp,
                    'canning problem (MESSAGE scheme)',
                    'standard')

    # Reporter can be initialized
    rep = Reporter.from_scenario(scen)

    # Number of quantities available in a rudimentary MESSAGEix Scenario
    assert len(rep.graph['all']) == 101

    # Quantities have short dimension names
    assert 'demand:n-c-l-y-h' in rep.graph

    # Aggregates are available
    assert len(rep.graph) == 4824
    assert 'demand:n-l-h' in rep.graph

    # Quantities are available
    dims = dict(coords=['chicago new-york topeka'.split()], dims=['n'])
    demand = xr.DataArray([300, 325, 275], **dims)

    # NB the call to squeeze() drops the length-1 dimensions c-l-y-h
    assert_xr_equal(rep.get('demand:n-c-l-y-h').squeeze(drop=True), demand)


def test_report_as_pyam(test_mp, caplog, tmp_path):
    scen = Scenario(test_mp,
                    'canning problem (MESSAGE scheme)',
                    'standard')
    scen.solve()
    rep = Reporter.from_scenario(scen)

    # Key for 'ACT' variable at full resolution
    ACT = rep.full_key('ACT')

    # Add a computation that converts ACT to a pyam.IamDataFrame
    rep.add('ACT IAMC', (partial(as_pyam, drop=['yv']), 'scenario', 'ya', ACT))

    # Result is an IamDataFrame
    idf1 = rep.get('ACT IAMC')
    assert isinstance(idf1, pyam.IamDataFrame)

    # …of expected length
    assert len(idf1) == 8

    # …in which variables are not renamed
    assert idf1['variable'].unique() == 'ACT'

    # Warning was logged because of extra columns
    w = "Extra columns ['h', 'm', 't'] when converting ['ACT'] to IAMC format"
    assert ('message_ix.reporting.pyam', WARNING, w) in caplog.record_tuples

    # Repeat, using the message_ix.Reporter convenience function
    def m_t(row):
        """Callback for collapsing ACT columns."""
        # .pop() removes the named column from the returned row
        row['variable'] = '|'.join(['Activity', row.pop('t'), row.pop('m')])
        return row

    # Use the convenience function to add the node
    keys = rep.as_pyam(ACT, 'ya', collapse=m_t)

    # Keys of added node(s) are returned
    assert len(keys) == 1
    key2, *_ = keys
    assert key2 == str(ACT) + ':iamc'

    caplog.clear()

    # Result
    idf2 = rep.get(key2)
    df2 = idf2.as_pandas()

    # Extra columns have been removed:
    # - m and t by the collapse callback.
    # - h automatically, because 'ya' was used for the year index.
    assert not any(c in df2.columns for c in ['h', 'm', 't'])

    # Variable names were formatted by the callback
    variable = pd.Series([
        'Activity|canning_plant|production',
        'Activity|transport_from_san-diego|to_chicago',
        'Activity|transport_from_san-diego|to_new-york',
        'Activity|transport_from_san-diego|to_topeka',
        'Activity|canning_plant|production',
        'Activity|transport_from_seattle|to_chicago',
        'Activity|transport_from_seattle|to_new-york',
        'Activity|transport_from_seattle|to_topeka',
    ], name='variable')
    assert_series_equal(df2['variable'], variable)

    # message_ix.Reporter uses pyam.IamDataFrame.to_csv() to write to file
    path = tmp_path / 'activity.csv'
    rep.write(key2, path)

    # File contents are as expected
    expected = Path(__file__).parent / 'data' / 'report-pyam-write.csv'
    assert path.read_text() == expected.read_text()
