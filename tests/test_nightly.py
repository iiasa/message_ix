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


pytestmark = pytest.mark.skipif()

# commented: temporarily disabled to develop the current PR
# pytestmark = pytest.mark.skipif(
#     os.environ.get('TRAVIS_EVENT_TYPE', '') != 'cron'
#     or os.environ.get('TRAVIS_OS_NAME', '') == 'osx',
#     reason="Nightly scenario tests only run on Travis 'cron' events.")
pytestmark = pytest.mark.skipif(
    'TRAVIS_EVENT_TYPE' not in os.environ
    or os.environ.get('TRAVIS_OS_NAME', '') == 'osx',
    reason='Run on all Travis jobs, for debugging.')


ids, args = zip(*iter_scenarios())


@pytest.fixture(scope='module')
def scenarios_mp(tmp_path_factory):
    path = tmp_path_factory.mktemp('nightly')
    download(path)

    platform_args = dict(
        # TODO remove the 'db' directory
        dbprops=path / 'db' / 'scenarios',
        dbtype='HSQLDB',
    )

    yield ixmp.Platform(**platform_args)


@pytest.mark.parametrize('model,scenario,solve,solve_opts,cases',
                         args, ids=ids)
def test_scenario(scenarios_mp, model, scenario, solve, solve_opts, cases):
    scen = message_ix.Scenario(scenarios_mp, model, scenario)
    scen.solve(model=solve, solve_options=solve_opts)

    for case in cases:
        exp = eval(case['exp'])
        obs = eval(case['obs'])
        assert eval(case['test'])(exp, obs)
