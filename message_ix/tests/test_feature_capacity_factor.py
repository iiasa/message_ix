"""Test ``capacity_factor`` effects, mainly for models with sub-annual resolution."""

import pytest
from ixmp import Platform

from message_ix import ModelError, Scenario
from message_ix.testing import make_subannual


def check_solution(scen: Scenario) -> None:
    """Perform several assertions about the solution of `scen`."""
    # Reading "ACT" and "CAP" from the solution, plus "operation_factor"
    act = scen.var("ACT").set_index(["technology", "time"])
    cap = scen.var("CAP").set_index(["technology"])
    op_fac = scen.par("operation_factor").set_index(["technology"])

    # 1) ACT is zero when capacity factor (CF) is zero
    cf = scen.par("capacity_factor").set_index(["technology", "time"])
    cf_zero = cf.loc[cf["value"] == 0]
    for i in cf_zero.index:
        assert act.loc[i, "lvl"] == 0

    # 2) CAP is correctly calculated based on "ACT", CF, and "operation_factor"
    for i in act.index:
        # Correct CF based on duration of each time slice
        duration = scen.par("duration_time", {"time": i[1]}).at[0, "value"]
        if i[1] != "year":
            cf.loc[i, "duration-corrected"] = cf.loc[i, "value"] * duration
            if cf.loc[i, "value"] == 0 or duration == 0:
                act.loc[i, "cf-corrected"] = act.loc[i, "lvl"]
            else:
                act.loc[i, "cf-corrected"] = act.loc[i, "lvl"] / float(
                    cf.loc[i, "duration-corrected"]
                )
    act = act.fillna(0).reset_index().set_index(["technology"])
    # CAP = max("ACT" / "duration_time" / "capacity_factor") / "operation_factor"
    for i in cap.index:
        # Considering operation factor (if specified)
        if not op_fac.empty:
            # Weighted average CF for "year" (for calculating "operation_factor")
            cf_year = sum(cf["duration-corrected"])
            # Capacity is related to "operation_factor", when defined, and yearly CF
            assert sum(act.loc[i, "lvl"]) == round(
                float(cap.loc[i, "lvl"]) * float(op_fac.loc[i, "value"]) * cf_year, 6
            )
        else:
            assert max(act.loc[i, "cf-corrected"]) == float(cap.loc[i, "lvl"])


# Dictionary of technology input/output
TD_0 = {
    "gas_ppl": {
        "time_origin": [],
        "time": ["summer", "winter"],
        "time_dest": ["summer", "winter"],
    },
}


def test_capacity_factor_time(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """``capacity_factor`` is calculated correctly when it varies by time slice."""
    # Build model and solve
    scen = make_subannual(
        test_mp,
        TD_0,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0.6}},
        var_cost={"gas_ppl": {"summer": 0.2, "winter": 0.2}},
        request=request,
    )
    check_solution(scen)


def test_capacity_factor_unequal_time(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """``capacity_factor`` is calculated correctly when ``duration_time`` is uneven."""
    # Build model and solve
    scen = make_subannual(
        test_mp,
        TD_0,
        time_steps=[
            ("summer", 0.3, "season", "year"),
            ("winter", 0.7, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0.8}},
        var_cost={"gas_ppl": {"summer": 0.2, "winter": 0.2}},
        request=request,
    )
    check_solution(scen)


# List of time step tuples
TS_0 = [
    ("day", 0.5, "subannual", "year"),
    ("night", 0.5, "subannual", "year"),
]


def test_capacity_factor_zero(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test zero capacity factor (CF) in a time slice.

    "solar_pv_ppl" is active in "day" and NOT at "night" (CF = 0). It is expected that
    the model will be infeasible, because "demand" at night cannot be met.
    """
    # Dictionary of technology input/output
    tec_dict = {
        "solar_pv_ppl": {
            "time_origin": [],
            "time": ["day", "night"],
            "time_dest": ["day", "night"],
        },
    }

    # Build model and solve (should raise GAMS error)
    with pytest.raises(ModelError):
        make_subannual(
            test_mp,
            tec_dict,
            com_dict={"solar_pv_ppl": {"input": "fuel", "output": "electr"}},
            time_steps=TS_0,
            demand={"day": 2, "night": 1},
            capacity={"solar_pv_ppl": {"inv_cost": 0.2, "technical_lifetime": 5}},
            capacity_factor={"solar_pv_ppl": {"day": 0.8, "night": 0}},
            request=request,
        )


def test_capacity_factor_zero_two(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test zero capacity factor (CF) in a time slice.

    "solar_pv_ppl" is active in "day" and NOT at "night" (CF = 0). The model output
    should show no activity of "solar_pv_ppl" at "night". So, "gas_ppl" is active at
    "night", even though a more expensive technology.
    """
    # Dictionary of technology input/output
    tec_dict = {
        "solar_pv_ppl": {
            "time_origin": [],
            "time": ["day", "night"],
            "time_dest": ["day", "night"],
        },
        "gas_ppl": {
            "time_origin": [],
            "time": ["day", "night"],
            "time_dest": ["day", "night"],
        },
    }

    # Build model and solve
    scen = make_subannual(
        test_mp,
        tec_dict,
        com_dict={
            "solar_pv_ppl": {"input": "fuel", "output": "electr"},
            "gas_ppl": {"input": "fuel", "output": "electr"},
        },
        time_steps=TS_0,
        demand={"day": 2, "night": 1},
        capacity={
            "solar_pv_ppl": {"inv_cost": 0.1, "technical_lifetime": 5},
            "gas_ppl": {"inv_cost": 0.1, "technical_lifetime": 5},
        },
        capacity_factor={
            "solar_pv_ppl": {"day": 0.8, "night": 0},
            "gas_ppl": {"day": 0.8, "night": 0.8},
        },
        var_cost={
            "solar_pv_ppl": {"day": 0, "night": 0},
            "gas_ppl": {"day": 0.2, "night": 0.2},
        },
        request=request,
    )
    check_solution(scen)


def test_capacity_factor_average(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Weighted average of ``capacity_factor`` for "year" is calculated correctly,
    based on time slices, when there is no capacity factor defined for "year"."""
    # Build model and solve
    scen = make_subannual(
        test_mp,
        TD_0,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0.6}},
        var_cost={"gas_ppl": {"summer": 0.2, "winter": 0.2}},
        operation_factor={"gas_ppl": 0.8},
        request=request,
    )
    check_solution(scen)
