from collections.abc import Callable, Generator
from typing import Any, Union

import pytest
from click.testing import Result
from ixmp import Platform

from message_ix import Scenario
from message_ix.tools.add_year import add_year


@pytest.fixture
def base_scen_mp(
    test_mp: Platform, request: pytest.FixtureRequest
) -> Generator[tuple[Scenario, Platform], Any, None]:
    scen = Scenario(
        test_mp, "model", scenario=request.node.name + "_standard", version="new"
    )

    data = {2020: 1, 2030: 2, 2040: 3}

    years = sorted(list(set(data.keys())))
    with scen.transact(message="initialize test model"):
        scen.add_set("node", "node")
        scen.add_set("commodity", "comm")
        scen.add_set("level", "level")
        scen.add_set("year", years)
        scen.add_set("technology", "tec")
        scen.add_set("mode", "mode")
        output_specs: list[Union[int, str]] = ["node", "comm", "level", "year", "year"]

        for yr, value in data.items():
            scen.add_par("demand", ["node", "comm", "level", yr, "year"], 1, "GWa")
            scen.add_par("technical_lifetime", ["node", "tec", yr], 10, "y")
            tec_specs: list[Union[int, str]] = ["node", "tec", yr, yr, "mode"]
            scen.add_par("output", tec_specs + output_specs, 1, "-")
            scen.add_par("var_cost", tec_specs + ["year"], value, "USD/GWa")

    scen.solve(case=f"{request.node.name}_original_years", quiet=True)

    yield scen, test_mp


def adding_years(
    test_mp: Platform, scen_ref: Scenario, years_new: list[int]
) -> Scenario:
    scen_new = Scenario(
        test_mp, model="add_year", scenario="standard", version="new", annotation=" "
    )
    add_year(scen_ref, scen_new, years_new)
    return scen_new


def assert_function(
    scen_ref: Scenario, scen_new: Scenario, years_new: list[int], yr_test: int
) -> None:
    # 1. Testing the set "year" for the new years
    horizon_old = sorted([int(x) for x in scen_ref.set("year")])
    horizon_test = sorted(horizon_old + years_new)
    horizon_new = sorted([int(x) for x in scen_new.set("year")])
    assert horizon_test == horizon_new

    # 2. Testing parameter "technical_lifetime" (function interpolate_1d)
    yr_next = min([x for x in horizon_old if x > yr_test])
    yr_pre = max([x for x in horizon_old if x < yr_test])
    parname = "technical_lifetime"
    ref = scen_ref.par(parname, {"technology": "tec", "year_vtg": [yr_pre, yr_next]})
    value_ref = ref["value"].mean()
    value_new = scen_new.par(parname, {"technology": "tec", "year_vtg": yr_test}).at[
        0, "value"
    ]
    assert value_new == pytest.approx(value_ref, rel=1e-04)

    # 3. Testing parameter "var_cost" (function interpolate_2d)
    ref = scen_ref.par(
        "var_cost",
        {
            "technology": "tec",
            "year_act": [yr_pre, yr_next],
            "year_vtg": [yr_pre, yr_next],
        },
    )

    value_ref = ref["value"].mean()

    value_new = scen_new.par(
        "var_cost", {"technology": "tec", "year_act": yr_test, "year_vtg": yr_test}
    ).at[0, "value"]

    # Asserting if the missing data is generated accurately by interpolation
    assert value_new == pytest.approx(value_ref, rel=1e-04)


YEARS_NEW = [2025, 2035]


# NOTE This should work on IXMP4Backend already, but somehow, add_year() does not seem
# to add years to scen_new. In assert_function(), this means that the filtered
# `var_cost` is empty and .at[] fails.
# TODO Experiment in a notebook why add_year() doesn't work.
@pytest.mark.jdbc
def test_add_year(base_scen_mp: tuple[Scenario, Platform]) -> None:
    scen_ref, test_mp = base_scen_mp

    # Adding new years
    scen_new = Scenario(
        test_mp, model="add_year", scenario="standard", version="new", annotation=" "
    )
    add_year(scen_ref, scen_new, YEARS_NEW)
    scen_new.solve(case="new_years", quiet=True)

    # Running the tests
    assert_function(scen_ref, scen_new, YEARS_NEW, yr_test=2025)


# NOTE This should work on IXMP4Backend already, but with version=None, we can't find a
# default Run for scen_ref. Not sure if JDBC sets this as default before deletion
# (if so, how?) or if it doesn't need a default to load a scen (in contrast to ixmp4).
@pytest.mark.jdbc
def test_add_year_cli(
    message_ix_cli: Callable[..., Result], base_scen_mp: tuple[Scenario, Platform]
) -> None:
    scen_ref, test_mp = base_scen_mp

    # Information about the base Scenario
    platform_name = test_mp.name
    model = scen_ref.model
    scenario = scen_ref.scenario

    cmd = [
        "--platform",
        platform_name,
        "--model",
        model,
        "--scenario",
        scenario,
        "add-years",
        "--years_new",
        repr(YEARS_NEW),
        "--model_new",
        "add_year",
        "--scen_new",
        "standard",
    ]

    # Delete the objects so that the database connection is closed
    del test_mp, scen_ref

    r = message_ix_cli(*cmd)
    assert r.exit_code == 0, (r.output, r.exception)

    # Re-load the base Scenario
    mp = Platform(name=platform_name)
    scen_ref = Scenario(mp, model=model, scenario=scenario)

    # Load the created Scenario
    scen_new = Scenario(mp, model="add_year", scenario="standard")

    assert_function(scen_ref, scen_new, YEARS_NEW, yr_test=2025)

    # Same, except with --dry-run
    r = message_ix_cli(*cmd, "--dry-run")
    assert r.exit_code == 0

    # Bad usage: not giving the base scenario info
    r = message_ix_cli(*cmd[6:], "--dry-run")
    assert r.exit_code == 2
