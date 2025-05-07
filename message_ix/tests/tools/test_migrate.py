"""Tests of :mod:`message_ix.tools.migrate`."""

import sys

import pytest
from ixmp import Platform

from message_ix.testing import make_westeros
from message_ix.tools.migrate import v311


@pytest.mark.jdbc
@pytest.mark.xfail(
    condition=sys.version_info < (3, 10),
    raises=ImportError,
    reason="Uses itertools.pairwise, added in Python 3.10",
)
def test_v311(
    caplog: pytest.LogCaptureFixture, request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Minimal test of :func:`.v311`."""
    s = make_westeros(test_mp, request=request)

    # Function runs
    v311(s)
    assert 0 == len(caplog.messages)

    # Applying a second time generates a log message but no change
    with caplog.at_level("INFO"):
        v311(s)

    assert (
        "Migration 'initial_new_capacity_up_v311' already applied to this scenario"
        in caplog.messages
    )
