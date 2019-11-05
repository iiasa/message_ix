"""Slow-running tests for nightly continuous integration."""
from functools import partial  # noqa: F401
import os

import ixmp
import message_ix
from message_ix.testing.nightly import (
    download,
    iter_scenarios,
)
import numpy as np  # noqa: F401
import pytest


# commented: temporarily disabled to develop the current PR
# pytestmark = pytest.mark.skipif(
#     os.environ.get('TRAVIS_EVENT_TYPE', '') != 'cron',
#     reason="Nightly scenario tests only run on Travis 'cron' events.")

# For development/debugging, uncomment the following
pytestmark = pytest.mark.skipif(
    'TRAVIS_EVENT_TYPE' not in os.environ,
    reason='Run on all Travis jobs, for debugging.')


# Information about nightly scenarios to run
ids, args = zip(*iter_scenarios())


@pytest.fixture(scope='module')
def downloaded_scenarios(tmp_path_factory):
    path = tmp_path_factory.mktemp('nightly')

    # Download scenarios database into the temporary path; install GAMS license
    download(path)

    yield dict(
        # TODO repack the archive without a 'db' directory, and remove from the
        #      path here
        dbprops=path / 'db' / 'scenarios',
        dbtype='HSQLDB',
    )


@pytest.fixture(scope='function')
def mp(downloaded_scenarios):
    """Modeling platform."""
    # NB this must be a *function*-scoped fixture (rather than the *module*-
    #    scoped fixture above) because JDBCBackend doesn't free up enough
    #    memory after the first usage.
    yield ixmp.Platform(**downloaded_scenarios)


@pytest.mark.parametrize('model,scenario,solve,solve_opts,cases',
                         args, ids=ids)
def test_scenario(mp, model, scenario, solve, solve_opts, cases):
    scen = message_ix.Scenario(mp, model, scenario)
    scen.solve(model=solve, solve_options=solve_opts)

    for case in cases:
        exp = eval(case['exp'])
        obs = eval(case['obs'])
        assert eval(case['test'])(exp, obs)
