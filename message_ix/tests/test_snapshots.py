"""Tests of specific :data:`.SNAPSHOTS`."""

from collections.abc import Callable

import numpy.testing as npt
import pytest
from ixmp import Platform

import message_ix
from message_ix.testing import SNAPSHOTS
from message_ix.tools.migrate import v311

#: Mapping from scenario URLs to tuples of:
#:
#: 1. Callable to prep the scenario.
#: 2. Keyword arguments to Scenario.solve()
#: 3. Callable that perform assertions on the solved :class:`.Scenario`.
CHECK: dict[str, tuple[Callable, dict, Callable]] = {
    "CD_Links_SSP2/baseline#1": (
        v311,
        dict(),
        lambda s: npt.assert_allclose(s.var("OBJ")["lvl"], 3871755.5),
    ),
    "CD_Links_SSP2_v2/NPi2020_1000-con-prim-dir-ncr#1": (
        v311,
        dict(max_adjustment=0.1),
        lambda s: npt.assert_allclose(s.var("OBJ")["lvl"], 3366415.25),
    ),
}


@pytest.mark.nightly
@pytest.mark.parametrize("scenario_info, hash", SNAPSHOTS)
def test_solve_and_check(
    snapshots_from_zenodo: Platform, scenario_info: dict[str, str], hash: str
) -> None:  # pragma: no cover
    """Test that snapshots scenario solve and satisfy :data:`CHECK`.

    The pytest argument :program:`-m "not nightly"` is added by default via
    :file:`pyproject.toml`. To explicitly run these tests, give
    :program:`pytest -m nightly …`.

    See also
    --------
    snapshots_from_zenodo
    """
    scen = message_ix.Scenario(snapshots_from_zenodo, **scenario_info)

    # Retrieve the preparation callback and check to be applied to this scenario
    pre, solve_kw, check = CHECK[scen.url]

    # Run the prep callback
    try:
        scen.remove_solution()
    except ValueError:
        pass
    pre(scen)

    # Prepare keyword arguments to solve()
    solve_kw.setdefault("model", "MESSAGE-MACRO")
    solve_kw.setdefault("solve_options", dict())
    solve_kw["solve_options"].setdefault("lpmethod", 4)
    solve_kw["solve_options"].setdefault("tilim", 300)

    # Scenario solves, i.e. is feasible
    scen.solve(**solve_kw)

    # Check evaluates to True
    check(scen)
