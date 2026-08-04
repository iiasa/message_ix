"""Tests for subannual generic relations (``relation_*_time``).

|MESSAGEix| supports subannual generic relations via parameters
``relation_upper_time``, ``relation_lower_time`` and
``relation_activity_time``, and flag sets ``is_relation_upper_time`` /
``is_relation_lower_time``. The equations ``RELATION_EQUIVALENCE_TIME``,
``RELATION_CONSTRAINT_UP_TIME`` and ``RELATION_CONSTRAINT_LO_TIME`` bind the
auxiliary variable ``REL_TIME(r, n, y, h)`` per time slice.
"""

import pandas as pd
import pytest
from ixmp import Platform

from message_ix import Scenario, make_df

pytestmark = pytest.mark.ixmp4_209

NODE = "node"
YEAR = 2020
MODE = "mode"
TIMES = ["h1", "h2"]
DURATION = 0.5  # equal halves of the year
SLICE = "h1"  # slice at which the per-slice bounds in these tests apply

CHEAP_VAR_COST = 10.0
EXPENSIVE_VAR_COST = 50.0
DEMAND_PER_SLICE = 5.0

CAP_VALUE = 2.0  # below DEMAND_PER_SLICE so the expensive tech must help at h1
FLOOR_VALUE = 2.0  # expensive_ppl must run at least this much at h1
ANNUAL_CAP = 6.0  # below the 10 GWa cheap_ppl would supply unconstrained
COEXIST_SLICE_CAP = 3.0  # tighter cheap_ppl bound at h1
# cheap_ppl is dearer at h2 (still below EXPENSIVE_VAR_COST) so the solution
# prefers cheap at h1 and the per-slice cap binds rather than sitting slack
# under solver degeneracy.
COEXIST_H2_VAR_COST = 20.0


def _act_at(act: pd.DataFrame, technology: str, time: str) -> float:
    """Total solved ``ACT`` for ``technology`` at ``time``."""
    rows = act[(act["technology"] == technology) & (act["time"] == time)]
    return float(rows["lvl"].sum())


def _act_total(act: pd.DataFrame, technology: str) -> float:
    """Total solved ``ACT`` for ``technology`` summed over time slices."""
    return float(act[act["technology"] == technology]["lvl"].sum())


def _build_subannual_baseline(mp: Platform, scenario_name: str) -> Scenario:
    """Minimal 2-slice RES with a cheap and expensive supply technology.

    Each slice has ``DEMAND_PER_SLICE`` GWa electricity demand at
    ``level=useful``. Both technologies have subannual ACT at every time
    slice. With no additional constraint the solution uses the cheap
    technology exclusively.
    """
    scen = Scenario(
        mp, model="test_relation_time", scenario=scenario_name, version="new"
    )
    scen.add_horizon(year=[YEAR], firstmodelyear=YEAR)
    scen.add_spatial_sets({"country": NODE})

    with scen.transact("structure"):
        scen.add_set("mode", MODE)
        scen.add_set("level", "useful")
        scen.add_set("commodity", "electr")
        scen.add_set("technology", ["cheap_ppl", "expensive_ppl"])
        scen.add_set("lvl_temporal", "subannual")
        for t in TIMES:
            scen.add_set("time", t)
            scen.add_set("map_temporal_hierarchy", ["subannual", t, "year"])

    with scen.transact("temporal structure and demand"):
        scen.remove_par("duration_time", scen.par("duration_time"))
        # the "year" slice must remain in duration_time at value 1.0
        scen.add_par(
            "duration_time",
            make_df(
                "duration_time",
                time=TIMES + ["year"],
                value=[DURATION] * len(TIMES) + [1.0],
                unit="%",
            ),
        )
        scen.add_par(
            "demand",
            make_df(
                "demand",
                node=NODE,
                commodity="electr",
                level="useful",
                year=YEAR,
                time=TIMES,
                value=DEMAND_PER_SLICE,
                unit="GWa",
            ),
        )

    common = dict(node_loc=NODE, year_vtg=YEAR, year_act=YEAR, time=TIMES)
    with scen.transact("technology data"):
        for tech, var_cost in (
            ("cheap_ppl", CHEAP_VAR_COST),
            ("expensive_ppl", EXPENSIVE_VAR_COST),
        ):
            scen.add_par(
                "output",
                make_df(
                    "output",
                    **common,
                    technology=tech,
                    mode=MODE,
                    commodity="electr",
                    level="useful",
                    node_dest=NODE,
                    time_dest=TIMES,
                    value=1.0,
                    unit="GWa",
                ),
            )
            scen.add_par(
                "var_cost",
                make_df(
                    "var_cost",
                    **common,
                    technology=tech,
                    mode=MODE,
                    value=var_cost,
                    unit="USD/GWa",
                ),
            )
            scen.add_par(
                "capacity_factor",
                make_df(
                    "capacity_factor", **common, technology=tech, value=1.0, unit="-"
                ),
            )

    return scen


def _add_time_relation(
    scen: Scenario,
    bound_par: str,
    bound_value: float,
    *,
    relation: str = "slice_bound",
    technology: str = "cheap_ppl",
    times: tuple[str, ...] = (SLICE,),
    set_flag: bool = False,
) -> None:
    """Bound ``technology`` activity at each slice in ``times``.

    ``bound_par`` is ``relation_upper_time`` or ``relation_lower_time``. The
    ``relation_*_time`` parameters and ``is_relation_*_time`` flag sets are
    initialized by :meth:`.MESSAGE.initialize` (see :attr:`.MESSAGE.items`).
    With ``set_flag=False`` the flag set is composed from parameter keys by
    :meth:`.MESSAGE.enforce`.
    """
    with scen.transact("subannual relation bound"):
        scen.add_set("relation", relation)
        scen.add_par(
            "relation_activity_time",
            make_df(
                "relation_activity_time",
                relation=relation,
                node_rel=NODE,
                year_rel=YEAR,
                node_loc=NODE,
                technology=technology,
                year_act=YEAR,
                mode=MODE,
                time=list(times),
                value=1.0,
                unit="-",
            ),
        )
        scen.add_par(
            bound_par,
            make_df(
                bound_par,
                relation=relation,
                node_rel=NODE,
                year_rel=YEAR,
                time=list(times),
                value=bound_value,
                unit="GWa",
            ),
        )
        if set_flag:
            for t in times:
                scen.add_set(f"is_{bound_par}", [relation, NODE, str(YEAR), t])


def _add_annual_cap(
    scen: Scenario, relation: str, cap_value: float, *, technology: str = "cheap_ppl"
) -> None:
    """Cap ``technology`` activity summed over the year via annual ``relation_*``.

    ``is_relation_upper`` is composed from ``relation_upper`` by the backend
    at solve time, so it is not set here.
    """
    with scen.transact("annual relation bound"):
        scen.add_set("relation", relation)
        scen.add_par(
            "relation_activity",
            make_df(
                "relation_activity",
                relation=relation,
                node_rel=NODE,
                year_rel=YEAR,
                node_loc=NODE,
                technology=technology,
                year_act=YEAR,
                mode=MODE,
                value=1.0,
                unit="-",
            ),
        )
        scen.add_par(
            "relation_upper",
            make_df(
                "relation_upper",
                relation=relation,
                node_rel=NODE,
                year_rel=YEAR,
                value=cap_value,
                unit="GWa",
            ),
        )


def test_subannual_relation_not_populated(test_mp: Platform) -> None:
    """Baseline without ``relation_*_time`` populated must solve cleanly.

    Regression guard for scenarios that never use the feature:
    ``data_load.gms`` must handle the case where the new ``relation_*_time``
    symbols are absent from the scenario GDX, and the new
    ``RELATION_*_TIME`` equations must not introduce infeasibility or solve
    errors.
    """
    scen = _build_subannual_baseline(test_mp, "baseline_no_cap")
    scen.solve(quiet=True)
    expected = len(TIMES) * DEMAND_PER_SLICE * CHEAP_VAR_COST
    assert float(scen.var("OBJ")["lvl"]) == pytest.approx(expected, rel=1e-3)


def test_subannual_relation_upper_binds(test_mp: Platform) -> None:
    """A subannual upper bound on ``cheap_ppl`` at ``h1`` binds.

    ``cheap_ppl.ACT`` at ``h1`` rides the cap and ``expensive_ppl`` picks up
    the slack; ``h2`` is unchanged.
    """
    scen = _build_subannual_baseline(test_mp, "baseline_for_upper_cap")
    capped = scen.clone(scenario="upper_cap", keep_solution=False)
    _add_time_relation(capped, "relation_upper_time", CAP_VALUE, set_flag=True)
    capped.solve(quiet=True)

    act = capped.var("ACT")
    assert _act_at(act, "cheap_ppl", SLICE) == pytest.approx(CAP_VALUE, rel=1e-3)
    assert _act_at(act, "expensive_ppl", SLICE) == pytest.approx(
        DEMAND_PER_SLICE - CAP_VALUE, rel=1e-3
    )
    # the cap at h1 leaves h2 unconstrained
    assert _act_at(act, "cheap_ppl", "h2") == pytest.approx(DEMAND_PER_SLICE, rel=1e-3)

    expected = (CAP_VALUE + DEMAND_PER_SLICE) * CHEAP_VAR_COST + (
        DEMAND_PER_SLICE - CAP_VALUE
    ) * EXPENSIVE_VAR_COST
    assert float(capped.var("OBJ")["lvl"]) == pytest.approx(expected, rel=1e-3)


def test_subannual_relation_flag_composed_without_explicit_flag(
    test_mp: Platform,
) -> None:
    """``is_relation_upper_time`` composes from parameter keys on solve.

    The caller populates only ``relation_activity_time`` /
    ``relation_upper_time`` without adding entries to
    ``is_relation_upper_time``. :meth:`.MESSAGE.enforce` composes the flag
    set from parameter keys at solve time. The constraint must still bind.
    """
    scen = _build_subannual_baseline(test_mp, "baseline_for_composed_flag")
    capped = scen.clone(scenario="composed_flag_cap", keep_solution=False)
    _add_time_relation(capped, "relation_upper_time", CAP_VALUE)
    capped.solve(quiet=True)

    act = capped.var("ACT")
    assert _act_at(act, "cheap_ppl", SLICE) == pytest.approx(CAP_VALUE, rel=1e-3)


def test_subannual_relation_upper_zero_bound_binds(test_mp: Platform) -> None:
    """A zero-valued ``relation_upper_time`` is a valid binding constraint.

    ``relation_upper_time = 0`` expresses "REL_TIME <= 0", forcing
    ``cheap_ppl`` activity at ``SLICE`` to zero. The flag set composition
    must preserve the key regardless of value (key-based, not value-based),
    so the constraint still fires.
    """
    scen = _build_subannual_baseline(test_mp, "baseline_for_zero_cap")
    capped = scen.clone(scenario="zero_cap", keep_solution=False)
    _add_time_relation(capped, "relation_upper_time", 0.0)
    capped.solve(quiet=True)

    act = capped.var("ACT")
    assert _act_at(act, "cheap_ppl", SLICE) == pytest.approx(0.0, abs=1e-6)
    assert _act_at(act, "expensive_ppl", SLICE) == pytest.approx(
        DEMAND_PER_SLICE, rel=1e-3
    )


def test_subannual_relation_lower_binds(test_mp: Platform) -> None:
    """A subannual lower bound forces ``expensive_ppl`` activity at ``h1``.

    Exercises ``RELATION_CONSTRAINT_LO_TIME`` and the lower branch of the
    :meth:`.MESSAGE.enforce` flag composition (``is_relation_lower_time`` is
    not set explicitly). ``expensive_ppl`` runs the floor at ``h1`` and
    ``cheap_ppl`` covers the remaining demand.
    """
    scen = _build_subannual_baseline(test_mp, "baseline_for_lower")
    floored = scen.clone(scenario="lower_floor", keep_solution=False)
    _add_time_relation(
        floored,
        "relation_lower_time",
        FLOOR_VALUE,
        relation="slice_floor",
        technology="expensive_ppl",
    )
    floored.solve(quiet=True)

    act = floored.var("ACT")
    assert _act_at(act, "expensive_ppl", SLICE) == pytest.approx(FLOOR_VALUE, rel=1e-3)
    assert _act_at(act, "cheap_ppl", SLICE) == pytest.approx(
        DEMAND_PER_SLICE - FLOOR_VALUE, rel=1e-3
    )


def test_subannual_relation_matches_annual(test_mp: Platform) -> None:
    """Even per-slice ``_time`` caps reproduce the annual relation.

    An annual ``relation_upper = C`` on ``cheap_ppl`` and a
    ``relation_upper_time = C / 2`` at each of two equal slices give the same
    objective and the same total ``cheap_ppl`` activity.
    """
    base = _build_subannual_baseline(test_mp, "baseline_for_equivalence")

    annual = base.clone(scenario="annual_cap", keep_solution=False)
    _add_annual_cap(annual, "annual_cap", ANNUAL_CAP)
    annual.solve(quiet=True)

    subannual = base.clone(scenario="subannual_cap", keep_solution=False)
    _add_time_relation(
        subannual,
        "relation_upper_time",
        ANNUAL_CAP / len(TIMES),
        relation="uniform_cap",
        times=tuple(TIMES),
    )
    subannual.solve(quiet=True)

    assert float(annual.var("OBJ")["lvl"]) == pytest.approx(
        float(subannual.var("OBJ")["lvl"]), rel=1e-3
    )
    cheap_annual = _act_total(annual.var("ACT"), "cheap_ppl")
    cheap_subannual = _act_total(subannual.var("ACT"), "cheap_ppl")
    assert cheap_annual == pytest.approx(cheap_subannual, rel=1e-3)
    assert cheap_subannual == pytest.approx(ANNUAL_CAP, rel=1e-3)


def test_subannual_and_annual_relation_coexist(test_mp: Platform) -> None:
    """Annual and subannual bounds on one relation both bind.

    An annual ``relation_upper`` caps total ``cheap_ppl`` activity; a tighter
    ``relation_upper_time`` caps it further at ``h1``. The solution rides both
    the annual total and the per-slice cap.
    """
    base = _build_subannual_baseline(test_mp, "baseline_for_coexist")
    scen = base.clone(scenario="coexist", keep_solution=False)
    with scen.transact("dearer cheap_ppl at h2"):
        h2_cost = scen.par(
            "var_cost", filters={"technology": "cheap_ppl", "time": "h2"}
        )
        scen.remove_par("var_cost", h2_cost)
        scen.add_par("var_cost", h2_cost.assign(value=COEXIST_H2_VAR_COST))
    _add_annual_cap(scen, "coexist_cap", ANNUAL_CAP)
    _add_time_relation(
        scen, "relation_upper_time", COEXIST_SLICE_CAP, relation="coexist_cap"
    )
    scen.solve(quiet=True)

    act = scen.var("ACT")
    assert _act_at(act, "cheap_ppl", SLICE) == pytest.approx(
        COEXIST_SLICE_CAP, rel=1e-3
    )
    assert _act_total(act, "cheap_ppl") == pytest.approx(ANNUAL_CAP, rel=1e-3)
