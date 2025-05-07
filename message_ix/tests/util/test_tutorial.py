from typing import TYPE_CHECKING

from ixmp.report import Key

from message_ix import Reporter, Scenario, make_df
from message_ix.testing import SCENARIO
from message_ix.util.tutorial import prepare_plots, solve_modified

if TYPE_CHECKING:
    import pytest
    from ixmp import Platform


# NOTE This test likely doesn't need to be parametrized
def test_prepare_plots(dantzig_reporter: Reporter) -> None:
    # Function runs without error
    prepare_plots(dantzig_reporter)

    # Plot keys are added; contains a task with 2 elements
    (func, key) = dantzig_reporter.graph["plot new capacity"]

    # First element is a callable partial object with certain keywords
    assert callable(func)
    assert func.keywords == dict(
        dims=("nl", "t", "yv"),
        units="GWa",
        title="Energy System New Capacity",
        cf=1.0,
        stacked=True,
    )

    # Second element is a key
    assert Key("CAP_NEW", ["nl", "t", "yv"]) == key


def test_solve_modified(
    caplog: "pytest.LogCaptureFixture", message_test_mp: "Platform"
) -> None:
    base = Scenario(message_test_mp, **SCENARIO["dantzig"])

    # Base objective value
    base.solve(quiet=True)
    base_obj = base.var("OBJ")["lvl"]

    with solve_modified(base, "new scenario name") as scenario:
        # Scenario is not yet solved
        assert not scenario.has_solution()

        # Scenario has the indicated new name
        assert "new scenario name" == scenario.scenario

        # Change one demand parameter from 325 to 326
        scenario.add_par(
            "demand",
            make_df(
                "demand",
                node=["new-york"],
                commodity=["cases"],
                level="consumption",
                year=1963,
                time="year",
                value=326,
                unit="case",
            ),
        )

    # Scenario is solved at the end of the with: statement
    assert scenario.has_solution()

    assert scenario.var("OBJ")["lvl"] != base_obj
