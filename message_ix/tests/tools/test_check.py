import pytest

from message_ix import Scenario, make_df
from message_ix.testing import make_dantzig, make_westeros
from message_ix.tools import check


def test_check_dantzig(test_mp):
    scen = make_dantzig(test_mp)

    # Checks all True
    results = check(scen)
    assert results[0]


@pytest.fixture
def westeros(test_mp):
    yield make_westeros(test_mp)


# Minimal config to make Westeros reportable
WESTEROS_CONFIG = {"units": {"replace": {"-": ""}}}


def test_gaps_input(westeros):
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
    with westeros.transact():
        westeros.remove_par("input", to_delete)

    # Checks fail
    results = check(westeros, config=WESTEROS_CONFIG)
    assert not results[0]


def test_check_tl_integer(westeros):
    # Change one value
    tl = "technical_lifetime"
    with westeros.transact():
        westeros.add_par(
            tl,
            make_df(
                tl,
                node_loc="Westeros",
                technology="bulb",
                year_vtg=700,
                value=1.1,
                unit="y",
            ),
        )

    # Checks fail
    results = check(westeros, config=WESTEROS_CONFIG)
    assert not results[0]

    assert """FAIL Non-integer values for ``technical_lifetime``:
See https://github.com/iiasa/message_ix/issues/503.
- 1.1 at indices: nl=Westeros t=bulb yv=700""" in map(
        str, results
    )


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
