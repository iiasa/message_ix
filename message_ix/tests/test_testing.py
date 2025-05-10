import pytest
from ixmp import Platform

from message_ix import ModelError, Scenario
from message_ix.testing import make_austria, make_dantzig, make_westeros


@pytest.mark.parametrize(
    "kwargs",
    (
        dict(solve=False, quiet=True),
        # Equivalent to austria_load_scenario.ipynb
        dict(solve=True),
    ),
)
def test_make_austria(
    request: pytest.FixtureRequest, test_mp: Platform, kwargs: dict[str, bool]
) -> None:
    """:func:`.make_austria` runs.

    Depending on the `kwargs`, this also tests that the resulting Scenario is feasible.
    """
    s = make_austria(test_mp, **kwargs, request=request)
    assert isinstance(s, Scenario)


@pytest.mark.parametrize(
    "kwargs",
    (
        dict(solve=True),
        dict(solve=True, multi_year=True),
    ),
)
def test_make_dantzig(
    request: pytest.FixtureRequest, test_mp: Platform, kwargs: dict[str, bool]
) -> None:
    """:func:`.make_dantzig` runs.

    Depending on the `kwargs`, this also tests that the resulting Scenario is feasible.
    """
    s = make_dantzig(test_mp, **kwargs, request=request)
    assert isinstance(s, Scenario)


@pytest.mark.parametrize(
    "kwargs",
    (
        dict(),
        pytest.param(
            dict(model_horizon=[691, 720]),
            marks=pytest.mark.xfail(
                raises=ModelError,
                reason="growth_activity_up is too tight in the first period",
            ),
        ),
        # Shortest duration with feasible (demand, growth_activity_up)
        dict(model_horizon=[694, 720]),
    ),
)
def test_make_westeros(
    request: pytest.FixtureRequest, test_mp: Platform, kwargs: dict[str, list[int]]
) -> None:
    """:func:`.make_westeros` runs.

    Depending on the `kwargs`, this also tests that the resulting Scenario is feasible.
    """
    s = make_westeros(test_mp, **kwargs, request=request)  # type: ignore[arg-type]
    assert isinstance(s, Scenario)

    s.solve(quiet=True, solve_options=dict(iis=1))
