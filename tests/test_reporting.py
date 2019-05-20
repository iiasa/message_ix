import xarray as xr
from xarray.testing import assert_equal as assert_xr_equal

from message_ix import Scenario
from message_ix.reporting import Reporter


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
