"""Slow-running tests for nightly continuous integration."""
from functools import partial  # noqa: F401
import os

import ixmp
import message_ix
from message_ix.testing.nightly import (
    DBPATH,
    download_db,
    download_license,
)
import numpy as np  # noqa: F401
import pytest
import yaml

with open('scenarios.yaml', 'r') as f:
    scenarios = yaml.load(f)

ids = []
args = []

for ids, data in scenarios.items():
    ids.append(id)
    args.append((
        data['model'],
        data['scenario'],
        data['solve'],
        data.get('solve_options', {}),
        data['cases']
    ))


def scenarios_mp():
    download_db()
    download_license()


@pytest.mark.skipif(os.environ.get('TRAVIS_EVENT_TYPE', '') != 'cron')
@pytest.mark.parametrize('model,scenario,solve,solve_opts,cases',
                         args, ids=ids)
def test_scenario(scenarios_mp, model, scenario, solve, solve_opts, cases):
    mp = ixmp.Platform(DBPATH, dbtype='HSQLDB')
    scen = message_ix.Scenario(mp, model, scenario)
    scen.solve(model=solve, solve_options=solve_opts)

    for case in cases:
        exp = eval(case['exp'])
        obs = eval(case['obs'])
        assert eval(case['test'])(exp, obs)
