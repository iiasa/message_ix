import pytest
from ixmp import Platform

from message_ix import Scenario
from message_ix.message_macro import MESSAGE_MACRO


class TestMESSAGE_MACRO:
    """Tests of :class:`.MESSAGE_MACRO`."""

    @pytest.mark.parametrize(
        "kwargs, solve_args",
        (
            (dict(), []),
            (
                dict(convergence_criterion=0.02, max_adjustment=0.4, max_iteration=100),
                [
                    "--CONVERGENCE_CRITERION=0.02",
                    "--MAX_ADJUSTMENT=0.4",
                    "--MAX_ITERATION=100",
                ],
            ),
        ),
    )
    def test_init(self, kwargs, solve_args) -> None:
        # A model instance can be constructed with the given `kwargs`
        mm = MESSAGE_MACRO(**kwargs)

        # Command-line options to GAMS have expected form
        assert all(e in mm.solve_args for e in solve_args), mm.solve_args

    def test_init_GAMS_min_version(self) -> None:
        class _MM(MESSAGE_MACRO):
            """Dummy subclass requiring a non-existent GAMS version."""

            GAMS_min_version = "999.9.9"

        # Constructor complains about an insufficient GAMS version
        with pytest.raises(
            RuntimeError, match="MESSAGE-MACRO requires GAMS >= 999.9.9; got "
        ):
            _MM()

    def test_initialize(self, test_mp: Platform) -> None:
        # MESSAGE_MACRO.initialize() runs
        Scenario(
            test_mp,
            "test_message_macro",
            "test_initialize",
            version="new",
            scheme="MESSAGE-MACRO",
        )
