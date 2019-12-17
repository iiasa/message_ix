import pytest

from functools import partial
from logging import WARNING
from pathlib import Path

from ixmp.reporting import Reporter as ixmp_Reporter
from ixmp.testing import assert_qty_equal
from numpy.testing import assert_allclose
import pandas as pd
from pandas.testing import assert_frame_equal
import pyam
import xarray as xr

from message_ix import Scenario
from message_ix.reporting import Reporter, configure, computations
from message_ix.testing import make_dantzig, make_westeros


def test_reporter_no_solution(test_mp):
    scen = Scenario(test_mp,
                    'canning problem (MESSAGE scheme)',
                    'standard')

    pytest.raises(RuntimeError, Reporter.from_scenario, scen)


def test_reporter(test_mp):
    scen = Scenario(test_mp,
                    'canning problem (MESSAGE scheme)',
                    'standard')

    # Varies between local & CI contexts
    # DEBUG may be due to reuse of test_mp in a non-deterministic order
    if not scen.has_solution():
        scen.solve()

    # IXMPReporter can be initialized on a MESSAGE Scenario
    rep_ix = ixmp_Reporter.from_scenario(scen)

    # message_ix.Reporter can also be initialized
    rep = Reporter.from_scenario(scen)

    # Number of quantities available in a rudimentary MESSAGEix Scenario
    assert len(rep.graph['all']) == 120

    # Quantities have short dimension names
    assert 'demand:n-c-l-y-h' in rep.graph

    # Aggregates are available
    assert 'demand:n-l-h' in rep.graph

    # Quantities contain expected data
    dims = dict(coords=['chicago new-york topeka'.split()], dims=['n'])
    demand = xr.DataArray([300, 325, 275], **dims)

    # NB the call to squeeze() drops the length-1 dimensions c-l-y-h
    obs = rep.get('demand:n-c-l-y-h').squeeze(drop=True)
    # TODO: Squeeze on AttrSeries still returns full index, whereas xarray
    # drops everything except node
    obs = obs.reset_index(['c', 'l', 'y', 'h'], drop=True)
    # check_attrs False because we don't get the unit addition in bare xarray
    assert_qty_equal(obs.sort_index(), demand, check_attrs=False)

    # ixmp.Reporter pre-populated with only model quantities and aggregates
    assert len(rep_ix.graph) == 5088

    # message_ix.Reporter pre-populated with additional, derived quantities
    # This is the same value as in test_tutorials.py
    assert len(rep.graph) == 16569

    # Derived quantities have expected dimensions
    vom_key = rep.full_key('vom')
    assert vom_key not in rep_ix
    assert vom_key == 'vom:nl-t-yv-ya-m-h'

    # …and expected values
    vom = (
        rep.get(rep.full_key('ACT')) * rep.get(rep.full_key('var_cost'))
    ).dropna()
    # check_attrs false because `vom` multiply above does not add units
    assert_qty_equal(vom, rep.get(vom_key), check_attrs=False)


def test_reporter_from_dantzig(test_mp):
    scen = make_dantzig(test_mp, solve=True)

    # Reporter.from_scenario can handle Dantzig example model
    rep = Reporter.from_scenario(scen)

    # Default target can be calculated
    rep.get('all')


def test_reporter_from_westeros(test_mp):
    scen = make_westeros(test_mp, emissions=True, solve=True)

    # Reporter.from_scenario can handle Westeros example model
    rep = Reporter.from_scenario(scen)

    # Westeros-specific configuration: '-' is a reserved character in pint
    configure(units={'replace': {'-': ''}})

    # Default target can be calculated
    rep.get('all')

    # message default target can be calculated
    # TODO if df is empty, year is cast to float
    obs = rep.get('message:default')

    # all expected reporting exists
    assert len(obs.data) == 69

    # custom values are correct
    obs = obs.filter(variable='total om*')
    assert len(obs.data) == 9
    assert all(
        obs['variable'] ==  # noqa: W504
        ['total om cost|coal_ppl'] * 3 +  # noqa: W504
        ['total om cost|grid'] * 3 +  # noqa: W504
        ['total om cost|wind_ppl'] * 3
    )
    assert all(obs['year'] == [700, 710, 720] * 3)

    obs = obs['value'].values
    exp = [4832.177734, 8786.515625, 12666.666016, 5555.555664, 8333.333984,
           10555.555664, 305.748138, 202.247391, 0.]
    assert len(obs) == len(exp)
    assert_allclose(obs, exp)


def test_reporter_convert_pyam(test_mp, caplog, tmp_path):
    scen = Scenario(test_mp,
                    'canning problem (MESSAGE scheme)',
                    'standard')
    if not scen.has_solution():
        scen.solve()
    rep = Reporter.from_scenario(scen)

    # Key for 'ACT' variable at full resolution
    ACT = rep.full_key('ACT')

    # Add a computation that converts ACT to a pyam.IamDataFrame
    rep.add('ACT IAMC', (partial(computations.as_pyam, drop=['yv'],
                                 year_time_dim='ya'),
                         'scenario', ACT))

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
    def m_t(df):
        """Callback for collapsing ACT columns."""
        # .pop() removes the named column from the returned row
        df['variable'] = 'Activity|' + df['t'] + '|' + df['m']
        df.drop(['t', 'm'], axis=1, inplace=True)
        return df

    # Use the convenience function to add the node
    keys = rep.convert_pyam(ACT, 'ya', collapse=m_t)

    # Keys of added node(s) are returned
    assert len(keys) == 1
    key2, *_ = keys
    assert key2 == ACT.name + ':iamc'

    caplog.clear()

    # Result
    idf2 = rep.get(key2)
    df2 = idf2.as_pandas()

    # Extra columns have been removed:
    # - m and t by the collapse callback.
    # - h automatically, because 'ya' was used for the year index.
    assert not any(c in df2.columns for c in ['h', 'm', 't'])

    # Variable names were formatted by the callback
    reg_var = pd.DataFrame([
        ['san-diego', 'Activity|canning_plant|production'],
        ['san-diego', 'Activity|transport_from_san-diego|to_chicago'],
        ['san-diego', 'Activity|transport_from_san-diego|to_new-york'],
        ['san-diego', 'Activity|transport_from_san-diego|to_topeka'],
        ['seattle', 'Activity|canning_plant|production'],
        ['seattle', 'Activity|transport_from_seattle|to_chicago'],
        ['seattle', 'Activity|transport_from_seattle|to_new-york'],
        ['seattle', 'Activity|transport_from_seattle|to_topeka'],
    ], columns=['region', 'variable'])
    assert_frame_equal(df2[['region', 'variable']], reg_var)

    # message_ix.Reporter uses pyam.IamDataFrame.to_csv() to write to file
    path = tmp_path / 'activity.csv'
    rep.write(key2, path)

    # File contents are as expected
    expected = Path(__file__).parent / 'data' / 'report-pyam-write.csv'
    assert path.read_text() == expected.read_text()
