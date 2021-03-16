from pathlib import Path

import pint
import pytest
from click.testing import CliRunner

import message_ix
from message_ix.testing import SCENARIO, make_dantzig

# Fixtures


@pytest.fixture(scope="session")
def test_data_path(request):
    """Path to the directory containing test data."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def tutorial_path(request):
    """Path to the directory containing the tutorials."""
    return Path(__file__).parents[2] / "tutorial"


@pytest.fixture(scope="session")
def message_ix_cli(tmp_env):
    """A CliRunner object that invokes the message_ix command-line interface.

    :obj:`None` in *args* is automatically discarded.
    """
    from message_ix import cli

    class Runner(CliRunner):
        def invoke(self, *args, **kwargs):
            return super().invoke(
                cli.main, list(filter(None, args)), env=tmp_env, **kwargs
            )

    yield Runner().invoke


@pytest.fixture(scope="class")
def message_test_mp(test_mp):
    make_dantzig(test_mp)
    make_dantzig(test_mp, multi_year=True)
    yield test_mp


@pytest.fixture(scope="session")
def ureg():
    """Session-scoped :class:`pint.UnitRegistry` with units needed by tests."""
    registry = pint.get_application_registry()

    for unit in "USD", "case":
        try:
            registry.define(f"{unit} = [{unit}]")
        except pint.DefinitionSyntaxError:
            # Already defined
            pass

    yield registry


@pytest.fixture
def dantzig_reporter(message_test_mp, ureg):
    scen = message_ix.Scenario(message_test_mp, **SCENARIO["dantzig"])

    if not scen.has_solution():
        scen.solve(quiet=True)

    rep = message_ix.Reporter.from_scenario(scen)

    # The Dantzig model has no data in fix_cost, which creates an error adding the
    # derived keys <fom:nl-t-yv-ya> and <vom:nl-t-yv-ya> because the former has no
    # units. Force application of units to this empty quantity.
    rep.configure(units=dict(apply=dict(fix_cost="USD/case")))

    yield rep
