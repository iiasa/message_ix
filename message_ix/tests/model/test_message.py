from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import ModelError, Scenario, make_df
from message_ix.testing import make_westeros

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
def test_gh_923(
    request: pytest.FixtureRequest, gh_923_scenario: Scenario, tl_value: list[int]
) -> None:
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


@pytest.mark.parametrize(
    "model_horizon",
    [
        [720],  # Simplest possible case: 1 model period
        [691, 720],  # 2 periods of various durations
        [700, 720],
        [719, 720],
        # Transition from duration_period=5 to duration_period=10
        [695, 700, 710, 720],
        # Transition from duration_period=10 to duration_period=5
        [700, 710, 715, 720],
    ],
)
def test_growth_new_capacity_up(
    request: pytest.FixtureRequest, test_mp: "Platform", model_horizon: list[int]
) -> None:
    """``CAP_NEW`` is correctly constrained according to ``growth_new_capacity_up``.

    This test adds ``tax_emission`` values and removes all constraints except
    ``growth_new_capacity_up`` on the technology "wind_ppl", such that the model chooses
    ``CAP_NEW`` for this technology equal to the upper bound given by
    ``NEW_CAPACITY_CONSTRAINT_UP``. Because the total model duration and constraint
    value are the same in all cases, ``CAP`` added within the model horizon (the
    discrete integral of ``CAP_NEW``) is also the same.

    The final two cases for `model_horizon` check for transitions from 5- to 10-year
    periods and vice versa, as occur in MESSAGEix-GLOBIOM (:mod:`message_ix_models`).
    The `exp_lvl` values for these cases were set in :pull:`654` by applying the
    parameters of `wind_ppl` directly to the ``NEW_CAPACITY_BOUND_UP`` [sic] equation.
    """

    # Create a Westeros baseline scenario including emissions; clone to a unique URL
    s = make_westeros(
        test_mp, emissions=True, model_horizon=model_horizon, request=request
    )

    # Retrieve historical_new_capacity for the constrained technology
    hnc = (
        s.par("historical_new_capacity")
        .query("technology == 'wind_ppl' and year_vtg == 690")["value"]
        .item()
    )

    # Modify the scenario
    n = "Westeros"
    common = dict(node=n, node_loc=n, technology="wind_ppl", year_vtg=model_horizon)
    with s.transact("prepare for test"):
        # Remove Westeros default dynamic constraint on ACT
        s.remove_par("growth_activity_up", s.par("growth_activity_up"))

        # Increase technical_lifetime of t="*_ppl". This is to cover cases where
        # duration_period is up to 29 years; but we do it in all cases for parity.
        name = "technical_lifetime"
        filters: dict[str, Any] = dict(technology=["coal_ppl", "wind_ppl"])
        s.add_par(name, s.par(name, filters=filters).assign(value=30.0))

        # Add emission tax
        name = "tax_emission"
        kw = common | dict(type_emission="GHG", type_tec="all", type_year=model_horizon)
        s.add_par(name, make_df(name, **kw, value=100.0, unit="???"))

        # Add `growth_new_capacity_up` for `wind_ppl`
        # NB no value is set for the historical period y=690; this means that additions
        #    to capacity must be flat/constant until 0690-12-31, with growth only
        #    possible after that point, i.e. from the start of the first model period.
        name = "growth_new_capacity_up"
        gncu = 0.01
        s.add_par(name, make_df(name, **common, value=gncu, unit="-"))

    # Scenario is feasible
    s.solve(quiet=True, solve_options=dict(iis=1))

    # Retrieve total capacity constructed during the model horizon = CAP for all 1+
    # vintages within the model horizon. This is the product of CAP_NEW and the
    # respective duration_period, i.e. its discrete integral over the period.
    filters = dict(technology="wind_ppl", year_vtg=model_horizon, year_act=720)
    obs = s.var("CAP", filters=filters)["lvl"].sum()

    # Expected value: integral of f(t) = a^t with a = gncu, on the interval from t = 0
    # (start of the first model period, so 0691-01-01) to t = 30 (end of the period
    # y=720 = 0720-12-31).
    # This value is the same regardless of time discretization.
    exp = hnc * ((1 + gncu) ** 30 - (1 + gncu) ** 0) / np.log(1 + gncu)

    npt.assert_allclose(obs, exp)


@pytest.mark.parametrize(
    "year_vtg, active_historical_techs",
    (
        pytest.param([690], {"coal_ppl", "wind_ppl", "grid"}, id="A"),
        pytest.param([690, 700], set(), id="B"),
    ),
)
def test_historical_new_capacity(
    test_mp: "Platform",
    request: pytest.FixtureRequest,
    year_vtg: list[int],
    active_historical_techs: set[str],
) -> None:
    """Test MESSAGE choice between ``historical_new_capacity`` and ``CAP_NEW``.

    This test exists to confirm behaviour prior to :pull:`924` is not altered by the
    change to ``map_tec_lifetime`` in that pull request.

    In particular, when both historical (y=690) and in-model (y=700) vintages of a
    technology have zero costs (case ‘B’), the model chooses to use the later vintage
    and *not* to use existing historical capacity. This is because constructing a larger
    amount of year_vtg=700 allows it to be used in year_act=710, which reduces overall
    system cost.
    """
    s = make_westeros(test_mp, model_horizon=[700, 710, 720], request=request)

    with s.transact(""):
        # Reduce demand to a low magnitude that can be supplied with historical capacity
        s.add_par("demand", s.par("demand").assign(value=1.0))

        # Reduce all costs to zero for periods `year_vtg`
        filters = dict(year_vtg=year_vtg)
        for name in "fix_cost", "inv_cost", "var_cost":
            s.add_par(name, s.par(name, filters=filters).assign(value=0.0))

    s.solve()

    # Identify technologies from the historical period that are active (i.e. within the
    # model horizon); compare these to the expected set
    assert active_historical_techs == set(
        s.var("ACT").query("year_vtg == 690 and lvl > 1e-7").technology
    )


def test_soft_activity_up(request: pytest.FixtureRequest, test_mp: "Platform") -> None:
    """Test function of parameter ``soft_activity_up``.

    This test was rewritten as part of :pull:`924` to confirm that behaviour was not
    altered by the change to ``map_tec_lifetime`` in that pull request.
    """
    s = make_westeros(test_mp, solve=True, request=request)

    # Record variable values prior to changes
    OBJ_pre = s.var("OBJ")["lvl"]
    ACT_pre = s.var("ACT")

    n = "Westeros"
    common = dict(node=n, technology="coal_ppl", time="year")

    # Reduce dynamic constraint from 10% to 5% → scenario is infeasible
    s.remove_solution()
    with s.transact(""):
        gau = "growth_activity_up"
        s.add_par(gau, s.par(gau).eval("value = value / 2"))
    with pytest.raises(ModelError):
        s.solve()

    # Add values to soft_activity_up → scenario is again feasible
    with s.transact(""):
        sau = "soft_activity_up"
        data = make_df(sau, **common, node_loc=n, year_act=700, value=0.7, unit="-")
        s.add_par(sau, data)
    s.solve(var_list=["ACT_UP"])

    # Equation ACTIVITY_SOFT_CONSTRAINT_UP is active, thus the ACT_UP variable used on
    # its LHS is populated and has values equal to the historical activity of coal_ppl
    ha = s.par("historical_activity", filters=dict(technology="coal_ppl"))
    exp = pd.DataFrame(common | dict(year=[700], lvl=ha.at[0, "value"], mrg=[0.0]))
    pdt.assert_frame_equal(exp, s.var("ACT_UP"), check_like=True, check_dtype=False)

    # The objective function value is reduced by a specific amount
    npt.assert_allclose(s.var("OBJ")["lvl"] - OBJ_pre, -1578.125, rtol=1e-5)

    # - Merge resulting ACT with data prior to changes.
    # - Compute differences in lvl.
    # - Select rows with non-zero differences.
    dims = ["node_loc", "technology", "year_vtg", "year_act", "mode", "time"]
    df = (
        ACT_pre.merge(s.var("ACT"), on=dims)
        .eval("change = lvl_y - lvl_x")
        .query("abs(change) > 1e-7")
    )

    # No net change in ACT
    npt.assert_allclose(df["change"].sum(), 0.0, atol=1e-7, rtol=0)
    # Activity of wind_ppl decreases in every period (coal_ppl increases)
    assert (df.query("technology == 'wind_ppl'")["change"] < 0.0).all()
