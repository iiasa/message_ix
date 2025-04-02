from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from message_ix import Scenario, make_df

if TYPE_CHECKING:
    from ixmp import Platform

#: Periods: one historical, two in the time horizon
Y = [0, 10, 20]


@pytest.fixture(scope="module")
def gh_923_scenario(test_mp: "Platform") -> Generator[Scenario, None, None]:
    """Minimal test scenario for :func:`test_gh_923`."""
    s = Scenario(test_mp, __name__, "gh_923", "new")

    # Set elements

    # Other sets
    common = dict(commodity="c", level="l", mode="m", technology="t", unit="GWa")
    common["node_dest"] = common["node_loc"] = common["node"] = "n"
    common["time_dest"] = common["time"] = "h"

    # Shorthand
    def _add(name: str, **kw) -> str:
        s.add_par(name, make_df(name, **(common | kw)))
        return name

    # Build the scenario
    with s.transact("Build scenario for issue #923"):
        s.add_horizon(Y, Y[1])

        # Extract (yv, ya) pairs, only for periods where ya is within the time horizon
        yv_ya = s.vintage_and_active_years(in_horizon=False).query("year_act >= @Y[1]")
        yv = yv_ya["year_vtg"].values
        ya = yv_ya["year_act"].values

        # Add single elements to other sets
        for name in filter(s.set_list().__contains__, common):
            s.add_set(name, common[name])

        # Populate other parameters
        bncu = _add("bound_new_capacity_up", year_vtg=Y[1], value=0.0)
        cf = _add("capacity_factor", year_vtg=yv, year_act=ya, value=1.0, unit="-")
        # NB Required because only the value time="year" → 1.0 is auto-populated
        dt = _add("duration_time", value=1.0, unit="-")
        d = _add("demand", year=Y[1:], value=1.0)
        hnc = _add("historical_new_capacity", year_vtg=Y[0], value=1.0)
        o = _add("output", year_vtg=yv, year_act=ya, value=0.1)
        tl = _add("technical_lifetime", year_vtg=Y, value=20, unit="y")

    # for name in ("duration_period", bncu, cf, d, dt, hnc, o, tl):  # DEBUG
    #     print(name, s.par(name).to_string(), sep="\n", end="\n\n")
    del bncu, cf, dt, d, hnc, o, tl

    yield s


@pytest.mark.parametrize(
    "tl_value",
    (
        [20, 20, 20],  # Passes without a fix for #923
        [20, 10, 10],  # Fails without a fix for #923
    ),
)
def test_gh_923(request, gh_923_scenario: Scenario, tl_value: list[int]) -> None:
    """Minimum reproducible test for :issue:`923`."""
    s = gh_923_scenario.clone(scenario=request.node.name)

    # Set technical_lifetime
    tl = "technical_lifetime"
    with s.transact("Reproduce issue #923"):
        s.add_par(tl, s.par(tl).sort_values("year_vtg").assign(value=tl_value))

    # print(tl, s.par(tl).to_string(), sep="\n", end="\n\n")  # DEBUG

    s.solve(solve_options=dict(iis=1))

    # for name in "ACT", "CAP", "CAP_NEW":  # DEBUG
    #     print(name, s.var(name).to_string(), sep="\n", end="\n\n")
