"""Slow-running tests for nightly continuous integration."""
from functools import partial  # noqa: F401
import os

import ixmp
import message_ix
from message_ix.testing.nightly import (
    DBPATH,
    download,
    iter_scenarios,
)
import numpy as np  # noqa: F401
import pytest


ids, args = zip(*iter_scenarios())


def scenarios_mp(tmp_path):
    download(tmp_path)
    yield ixmp.Platform(dbprops=tmp_path / 'scenarios', dbtype='HSQLDB')


@pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE', '') != 'cron')
@pytest.mark.parametrize('model,scenario,solve,solve_opts,cases',
                         args, ids=ids)
def test_scenario(scenarios_mp, model, scenario, solve, solve_opts, cases):
    scen = message_ix.Scenario(scenarios_mp, model, scenario)
    scen.solve(model=solve, solve_options=solve_opts)

    for case in cases:
        exp = eval(case['exp'])
        obs = eval(case['obs'])
        assert eval(case['test'])(exp, obs)
