"""Tests for recursive-dynamic (myopic / rolling-horizon) solve mode.

The mode is selected with the ``foresight`` keyword: ``0`` is perfect foresight,
``1`` is myopic, and a value ``> 1`` is a rolling horizon with that many years of
look-ahead.
"""

import numpy as np
import pytest
from ixmp import Platform

from message_ix.testing import make_westeros

pytestmark = pytest.mark.ixmp4_209


@pytest.mark.parametrize("foresight", [1, 15, 30])
def test_objective_vs_perfect_foresight(
    request: pytest.FixtureRequest, test_mp: Platform, foresight: int
) -> None:
    """RD objective is bounded by perfect foresight; equal at full lookahead.

    Because the active ``year`` set accumulates across iterations and ``OBJECTIVE``
    sums over ``year``, the final ``OBJ`` is the full-horizon cost with earlier
    periods at their fixed values. Limited foresight can never beat perfect
    foresight, and when ``foresight`` spans the model horizon (> 20 years for
    :func:`.make_westeros`) the first iteration solves the full intertemporal problem
    so the two objectives match.
    """
    pf = make_westeros(test_mp, solve=True, request=request)

    rolling = pf.clone(keep_solution=False)
    rolling.solve(foresight=foresight, quiet=True)

    obj_pf = pf.var("OBJ")["lvl"]
    obj_rd = rolling.var("OBJ")["lvl"]

    # Limited foresight cannot beat perfect foresight (prior decisions are pinned
    # within the tolerance band).
    assert obj_rd + 1e-6 * abs(obj_pf) >= obj_pf

    # Foresight spanning the horizon reproduces perfect foresight exactly.
    if foresight > 20:  # horizon span of make_westeros (firstmodelyear 700 .. 720)
        assert np.isclose(obj_pf, obj_rd)


def test_foresight_keyword_matches_gams_args(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """``solve(foresight=N)`` matches ``gams_args=["--foresight=N"]``."""
    base = make_westeros(test_mp, request=request)

    via_keyword = base.clone(keep_solution=False)
    via_keyword.solve(foresight=20, quiet=True)

    via_gams_args = base.clone(keep_solution=False)
    via_gams_args.solve(gams_args=["--foresight=20"], quiet=True)

    assert np.isclose(via_keyword.var("OBJ")["lvl"], via_gams_args.var("OBJ")["lvl"])
