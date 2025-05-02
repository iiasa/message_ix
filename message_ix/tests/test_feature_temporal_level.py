"""Ensure that COMMODITY_BALANCE works for models with sub-annual time resolution.

The tests check at different temporal levels, i.e., year, seasons, months, etc., and
with different duration_time values.

In these tests, "demand" is defined in different time slices with different
"duration_time", there is one power plant ("gas_ppl") to meet "demand", which receives
fuel from a supply technology ("gas_supply"). Different temporal level hierarchies are
tested, by linkages of "ACT" with "demand" and "CAP".
"""

import pytest
from ixmp import Platform

from message_ix import ModelError, Scenario
from message_ix.testing import make_subannual

# Values for the com_dict argument to make_subannual
COM_DICT = {
    "gas_ppl": {"input": "fuel", "output": "electr"},
    "gas_supply": {"input": [], "output": "fuel"},
}


def check_solution(scen: Scenario) -> None:
    # Reading "ACT" greater than zero from the solution
    act = scen.var("ACT")[scen.var("ACT")["lvl"] > 0]

    # 1) Testing if linkage between "gas_ppl" with "gas_supply" technology is made
    assert "gas_supply" in set(act["technology"])

    # 2) Testing if "ACT" of "gas_ppl" is correct (with respect to "duration_time_rel")
    # i.e., sum("ACT" of "gas_ppl") = sum("ACT" of "gas_supply") = sum("demand")
    assert (
        sum(act.loc[act["technology"] == "gas_ppl"]["lvl"])
        == sum(act.loc[act["technology"] == "gas_supply"]["lvl"])
        == sum(scen.par("demand")["value"])
    )

    # 3) Test if "CAP" of "gas_ppl" is correctly calculated based on "ACT"
    # i.e., "CAP" = max("ACT" / "duration_time")
    for h in act.loc[act["technology"] == "gas_ppl"]["time"]:
        act.loc[
            (act["time"] == h) & (act["technology"] == "gas_ppl"),
            "capacity-corrected",
        ] = act["lvl"] / scen.par("duration_time", {"time": h}).at[0, "value"]
    assert (
        max(act.loc[act["technology"] == "gas_ppl", "capacity-corrected"])
        == scen.var("CAP", {"technology": "gas_ppl"}).at[0, "lvl"]
    )


# Dictionary of technology input/output
TD_0 = {
    "gas_ppl": {
        "time_origin": [],
        "time": ["summer"],
        "time_dest": ["summer"],
    },
    "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
}


def test_temporal_levels_not_linked(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test two unlinked temporal levels.

    "gas_ppl" is active in "summer" and NOT linked to "gas_supply" in "year". This
    setup should not solve.
    """
    tec_dict = TD_0.copy()
    tec_dict["gas_ppl"]["time_origin"] = ["summer"]

    # Check the model not solve if there is no link between fuel supply and power plant
    with pytest.raises(ModelError):
        make_subannual(
            test_mp,
            tec_dict,
            time_steps=[("summer", 1, "season", "year")],
            demand={"summer": 2},
            com_dict=COM_DICT,
            request=request,
        )


def test_season_to_year(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test two linked temporal levels.

    Linking "gas_ppl" and "gas_supply" at one temporal level (e.g., "year")
    Only one "season" (duration = 1) and "demand" is defined only at "summer"
    Model solves and "gas_supply" is active.
    """
    tec_dict = TD_0.copy()
    tec_dict["gas_ppl"]["time_origin"] = ["year"]

    scen = make_subannual(
        test_mp,
        tec_dict,
        time_steps=[("summer", 1, "season", "year")],
        demand={"summer": 2},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


# Dictionary of technology input/output
TD_1 = {
    "gas_ppl": {
        "time_origin": ["year", "year"],
        "time": ["summer", "winter"],
        "time_dest": ["summer", "winter"],
    },
    "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
}
# List of time step tuples
TS_0 = [
    ("summer", 0.5, "season", "year"),
    ("winter", 0.5, "season", "year"),
]


def test_two_seasons_to_year(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test two linked temporal levels with two seasons.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5). Model solves
    and "gas_supply" is active.
    """
    scen = make_subannual(
        test_mp,
        TD_1,
        time_steps=TS_0,
        demand={"summer": 1, "winter": 1},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


def test_two_seasons_to_year_relative(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test two linked temporal levels with two seasons and a relative time.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5). Model solves,
    but assertions fail.
    """
    scen = make_subannual(
        test_mp,
        TD_1,
        time_steps=TS_0,
        time_relative=["year"],
        demand={"summer": 1, "winter": 1},
        com_dict=COM_DICT,
        request=request,
    )
    # Shouldn't pass the test, if adding relative duration time
    with pytest.raises(AssertionError):
        check_solution(scen)


def test_seasons_to_seasons(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test two seasons at one temporal level.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5). Model solves
    and "gas_supply" is active.
    """
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["summer", "winter"],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
    }

    scen = make_subannual(
        test_mp,
        tec_dict,
        time_steps=TS_0,
        demand={"summer": 1, "winter": 1},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


# Dictionary of technology input/output
TD_2 = {
    "gas_ppl": {
        "time_origin": ["year", "year"],
        "time": ["Jan", "Feb"],
        "time_dest": ["Jan", "Feb"],
    },
    "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
}
# List of time step tuples
TS_1 = [
    ("summer", 0.5, "season", "year"),
    ("winter", 0.5, "season", "year"),
    ("Jan", 0.25, "month", "winter"),
    ("Feb", 0.25, "month", "winter"),
    ("Jun", 0.25, "month", "summer"),
    ("Jul", 0.25, "month", "summer"),
]


def test_unlinked_three_temporal_levels(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three unlinked temporal levels.

    "month" is defined under "season" BUT "season" not linked to "year". Model should
    not solve.
    """

    # Check the model shouldn't solve
    with pytest.raises(ModelError):
        make_subannual(
            test_mp,
            TD_2,
            time_steps=TS_1[2:],  # Exclude the definitions of "summer" and "winter"
            demand={"Jan": 1, "Feb": 1},
            com_dict=COM_DICT,
            request=request,
        )


def test_linked_three_temporal_levels(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels.

    "month" is defined under "season", and "season" is linked to "year". Model solves.
    """
    scen = make_subannual(
        test_mp,
        TD_2,
        time_steps=TS_1,
        demand={"Jan": 1, "Feb": 1},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


def test_linked_three_temporal_levels_relative(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels with a relative time.

    "month" is defined under "season", and "season" is linked to "year". Model solves,
    but assertions fail.
    """
    scen = make_subannual(
        test_mp,
        TD_2,
        time_steps=TS_1,
        time_relative=["year", "summer"],
        demand={"Jan": 1, "Feb": 1},
        com_dict=COM_DICT,
        request=request,
    )
    # Shouldn't pass with a relative time duration
    with pytest.raises(AssertionError):
        check_solution(scen)


# Dictionary of technology input/output
TD_3 = {
    "gas_ppl": {
        "time_origin": ["Jan", "Feb"],
        "time": ["Jan", "Feb"],
        "time_dest": ["year"],
    },
    "gas_supply": {
        "time_origin": [],
        "time": ["Jan", "Feb"],
        "time_dest": ["Jan", "Feb"],
    },
}


def test_linked_three_temporal_levels_month_to_year(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels from month to season and year.

    "month" is linked to "season", and "season" is linked to "year". Model solves.
    """

    scen = make_subannual(
        test_mp,
        TD_3,
        time_steps=TS_1,
        demand={"year": 2},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


def test_linked_three_temporal_levels_season_to_year(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels from season to year.

    "season" is linked to "year". Model solves.
    """
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["winter", "winter"],
            "time": ["Jan", "Feb"],
            "time_dest": ["year", "year"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["winter", "summer"],
            "time_dest": ["winter", "summer"],
        },
    }
    scen = make_subannual(
        test_mp,
        tec_dict,
        time_steps=TS_1,
        demand={"year": 2},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


def test_linked_three_temporal_levels_time_act(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels, with activity only at "time".

    Model solves.
    """
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["summer", "winter"],
            "time_dest": ["year", "year"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["year"],
            "time_dest": ["year"],
        },
    }

    scen = make_subannual(
        test_mp,
        tec_dict,
        time_steps=TS_0,
        demand={"year": 2},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)


def test_linked_three_temporal_levels_different_duration(
    request: pytest.FixtureRequest, test_mp: Platform
) -> None:
    """Test three linked temporal levels with different duration times.

    Model solves, linking "month" through "season" to "year".
    """
    scen = make_subannual(
        test_mp,
        TD_3,
        time_steps=TS_1,
        demand={"year": 2},
        com_dict=COM_DICT,
        request=request,
    )
    check_solution(scen)
