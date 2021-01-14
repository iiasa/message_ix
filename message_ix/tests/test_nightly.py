"""Slow-running tests for nightly continuous integration."""
from functools import partial  # noqa: F401

import ixmp
import numpy as np  # noqa: F401
import pytest

import message_ix
from message_ix.testing.nightly import download, iter_scenarios

# In setup.cfg, the pytest argument -m "not nightly" is given by default.
# To force running these tests only, give -m nightly or comment this line.
pytestmark = pytest.mark.nightly


# Information about nightly scenarios to run
ids, args = zip(*iter_scenarios())


@pytest.fixture(scope="module")
def downloaded_scenarios(tmp_path_factory):
    path = tmp_path_factory.mktemp("nightly")

    # Download scenarios database into the temporary path; install GAMS license
    download(path)

    # NB could `yield ixmp.Platform(...)` here, but Travis/macOS jobs fail due
    #    to excessive memory use in Java/ixmp_source. Instead, create multiple
    #    Platforms so that memory is released after each is destroyed.
    yield dict(
        # TODO repack the archive without a 'db' directory, and remove from the
        #      path here
        backend="jdbc",
        driver="hsqldb",
        path=path / "db" / "scenarios",
    )


@pytest.mark.parametrize("model,scenario,solve,solve_opts,cases", args, ids=ids)
def test_scenario(downloaded_scenarios, model, scenario, solve, solve_opts, cases):
    mp = ixmp.Platform(**downloaded_scenarios)
    scen = message_ix.Scenario(mp, model, scenario)
    scen.solve(model=solve, solve_options=solve_opts)

    for case in cases:
        exp = eval(case["exp"])
        obs = eval(case["obs"])
        assert eval(case["test"])(exp, obs)
