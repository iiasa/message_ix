"""Tests of :class:`ixmp.model.base.Model` classes in :mod:`message_ix.models`."""

import re
from collections import defaultdict
from typing import TYPE_CHECKING

import ixmp
import pytest
from ixmp.backend.jdbc import JDBCBackend

from message_ix.models import MESSAGE, MESSAGE_MACRO

if TYPE_CHECKING:
    from ixmp import Platform


class TestMESSAGE:
    def test_initialize(self, caplog, test_mp: "Platform") -> None:
        # Expected numbers of items by type
        exp = defaultdict(list)
        for name, spec in MESSAGE.items.items():
            exp[str(spec.type.name).lower()].append(name)

        # balance_equality is removed in initialize() for JDBC
        if isinstance(test_mp._backend, JDBCBackend):
            exp["set"].remove("balance_equality")

        # Use ixmp.Scenario to avoid invoking ixmp_source/Java code that automatically
        # populates empty scenarios
        s = ixmp.Scenario(test_mp, model="m", scenario="s", version="new")

        # Initialization succeeds on a totally empty scenario
        MESSAGE.initialize(s)

        # The expected items exist
        for ix_type, exp_names in exp.items():
            obs_names = getattr(s, f"{ix_type}_list")()
            assert sorted(obs_names) == sorted(exp_names)

    def test_initialize_filter_log(self, caplog, test_mp: "Platform") -> None:
        """Test :meth:`MESSAGE.initialize` logging under some conditions.

        For :class:`.Scenario` created with message_ix v3.10 or earlier, equations and
        variables may be initialized but have zero dimensions, thus empty lists of
        "index sets" and "index names". When :class:`.Scenario` is instantiated,
        :meth:`MESSAGE.initialize` is invoked, and in turn
        :meth:`ixmp.model.base.Model.initialize_items`. This method generates many log
        messages on level :data:`~logging.WARNING`.

        In order to prevent this log noise, :func:`.models._filter_log_initialize_items`
        is used. This test checks that it is effective.
        """
        # Use ixmp.Scenario to avoid invoking ixmp_source/Java code that automatically
        # populates empty scenarios
        s = ixmp.Scenario(test_mp, model="m", scenario="s", version="new")

        # Initialize an equation with no dimensions. This mocks the state of a Scenario
        # created with message_ix v3.10 or earlier.
        s.init_equ("NEW_CAPACITY_BOUND_LO", idx_sets=[], idx_names=[])

        s.commit("")
        s.set_as_default()
        caplog.clear()

        # Initialize items.
        MESSAGE.initialize(s)

        # Messages related to re-initializing items with 0 dimensions are filtered and
        # do not reach `caplog`. This assertion fails with message_ix v3.10.
        message_pattern = re.compile(
            r"Existing index (name|set)s of 'NEW_CAPACITY_BOUND_LO' \[\] do not match "
            r"\('node', '.*', 'year'\)"
        )
        extra = list(filter(message_pattern.match, caplog.messages))
        assert not extra, f"{len(extra)} unwanted log messages: {extra}"


def test_message_macro() -> None:
    # Constructor runs successfully
    MESSAGE_MACRO()

    class _MM(MESSAGE_MACRO):
        """Dummy subclass requiring a non-existent GAMS version."""

        GAMS_min_version = "99.9.9"

    # Constructor complains about an insufficient GAMS version
    with pytest.raises(
        RuntimeError, match="MESSAGE-MACRO requires GAMS >= 99.9.9; found "
    ):
        _MM()

    # Construct with custom model options
    mm = MESSAGE_MACRO(
        convergence_criterion=0.02, max_adjustment=0.4, max_iteration=100
    )

    # Command-line options to GAMS have expected form
    expected = [
        "--CONVERGENCE_CRITERION=0.02",
        "--MAX_ADJUSTMENT=0.4",
        "--MAX_ITERATION=100",
    ]
    assert all(e in mm.solve_args for e in expected)
