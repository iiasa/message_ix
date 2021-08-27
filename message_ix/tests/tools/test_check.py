import pytest

from message_ix import Scenario, make_df
from message_ix.testing import make_dantzig, make_westeros
from message_ix.tools import check


def test_check_dantzig(test_mp):
    scen = make_dantzig(test_mp)

    # Checks all True
    results = check(scen)
    assert results[0]


def test_check_westeros(test_mp):
    scen = make_westeros(test_mp)

    # Minimal config to make Westeros reportable
    config = {"units": {"replace": {"-": ""}}}

    # Checks all pass
    results = check(scen, config=config)
    assert results[0]

    # Delete one value
    to_delete = make_df(
        "input",
        node_loc="Westeros",
        technology="bulb",
        year_vtg=690,
        year_act=710,
        mode="standard",
        node_origin="Westeros",
        commodity="electricity",
        level="final",
        time="year",
        time_origin="year",
    ).dropna(axis=1)
    with scen.transact():
        scen.remove_par("input", to_delete)

    # Checks fail
    results = check(scen, config=config)
    assert not results[0]


@pytest.mark.parametrize(
    "url, config",
    [
        # ("ixmp://platform/model/scenario#version", dict()),
    ],
)
def test_check_existing(url, config):
    """Check existing scenarios.

    For local use only: extend the list of parameters, above, but do not commit
    additions to ``main``.
    """
    # import pint
    # from iam_units import registry
    #
    # pint.set_application_registry(registry)

    scen, mp = Scenario.from_url(url)
    results = check(scen, config=config)

    # Checks all pass
    assert results[0], "\n".join(map(str, results))
