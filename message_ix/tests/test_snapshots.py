"""Tests of specific :data:`.SNAPSHOTS`."""

import numpy.testing as npt
import pytest

import message_ix
from message_ix.testing import SNAPSHOTS

#: Mapping from scenario URLs and to callables that perform assertions on the solved
#: :class:`.Scenario`.
CHECK = {
    "CD_Links_SSP2/baseline#1": lambda s: npt.assert_allclose(
        s.var("OBJ")["lvl"], 3869529.75, rtol=3e-6
    ),
    "CD_Links_SSP2_v2/NPi2020_1000-con-prim-dir-ncr#1": lambda s: npt.assert_allclose(
        s.var("OBJ")["lvl"], 3359089.0, rtol=3e-6
    ),
}


@pytest.mark.nightly
@pytest.mark.parametrize("scenario_info, hash", SNAPSHOTS)
def test_solve_and_check(
    snapshots_from_zenodo, scenario_info, hash
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

    # Retrieve the check to be applied to this scenario
    check = CHECK[scen.url]

    # Scenario solves
    scen.solve(model="MESSAGE-MACRO", solve_options=dict(lpmethod=4, tilim=300))

    # Check evaluates to True
    check(scen)
