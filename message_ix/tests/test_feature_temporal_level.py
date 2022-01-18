"""
This test ensures that COMMODITY_BALANCE works for (sub-annual) time slices
(index of "time" in MESSAGEix) at different temporal levels, i.e., year, seasons,
months, etc., and with different duration times.

"""

from itertools import product

import pytest

from message_ix import ModelError, Scenario


def add_cap_par(scen, years, tec, data={"inv_cost": 0.1, "technical_lifetime": 5}):
    """
    Adding required parameters for representing "capacity" in a model.

    Parameters
    ----------
    scen : Class
        message_ix.Scenario.
    years : list of integers
        Years for adding data.
    tec : string
        Technology name for adding capacity parameters.
    data : Dict, optional
        Dictionary of parameters and their values.
        The default is {"inv_cost": 0.1, "technical_lifetime": 5}.

    """

    for year, (parname, val) in product(years, data.items()):
        scen.add_par(parname, ["node", tec, year], val, "-")


def model_generator(
    test_mp,
    comment,
    tec_dict,
    time_steps,
    demand,
    relative_time=[],
    com_dict={
        "gas_ppl": {"input": "fuel", "output": "electr"},
        "gas_supply": {"input": [], "output": "fuel"},
    },
    yr=2020,
    capacity=True,
    unit="GWa",
):
    """
    Generates a simple model with two technologies, and a number of time slices.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    comment : string
        Annotation for saving different scenarios and comparing their results.
    tec_dict : dict
        A dictionary for a technology and required info for time-related parameters.
        (e.g., tec_dict = {"gas_ppl": {"time_origin": ["summer"],
                                       "time": ["summer"], "time_dest": ["summer"]})
    time_steps : list of tuples
        Information about each time slice, packed in a tuple with four elements,
        including: time slice name, duration relative to "year", "temporal_lvl",
        and parent time slice. (e.g., time_steps = [("summer", 1, "season", "year")])
    relative_time: list of strings
        List of parent "time" slices, for which a relative duration time is maintained.
        This will be used to specify parameter "duration_time_rel" for these "time"s.
    demand : dict
        A dictionary for information of "demand" in each time slice.
        (e.g., demand = {"summer": 2.5})
    com_dict : dict
        A dictionary for specifying "input" and "output" commodities.
        (e.g., com_dict = {"gas_ppl": {"input": "fuel", "output": "electr"}})
    yr : int, optional
        Model year. The default is 2020.
    capacity : bool, optional
        Parameterization of capacity. The default is True.
    unit :  string
        Unit of "demand"


    """

    # Building an empty scenario
    scen = Scenario(test_mp, "test_time", comment, version="new")

    # Adding required sets
    scen.add_set("node", "node")
    for c in com_dict.values():
        scen.add_set("commodity", [x for x in list(c.values()) if x])

    scen.add_set("level", "level")
    scen.add_set("year", yr)
    scen.add_set("type_year", yr)
    scen.add_set("technology", list(tec_dict.keys()))
    scen.add_set("mode", "mode")
    scen.add_set("lvl_temporal", [x[2] for x in time_steps])
    scen.add_set("time", [x[0] for x in time_steps])
    scen.add_set("time", [x[3] for x in time_steps])
    for x in relative_time:
        scen.add_set("time_relative", x)

    # Adding "time" and "duration_time" to the model
    for (h, dur, tmp_lvl, parent) in time_steps:
        scen.add_set("map_temporal_hierarchy", [tmp_lvl, h, parent])
        scen.add_par("duration_time", [h], dur, "-")

    # Defining demand
    for h, value in demand.items():
        scen.add_par("demand", ["node", "electr", "level", yr, h], value, unit)

    # Adding "input" and "output" parameters of technologies
    for tec, times in tec_dict.items():
        if times["time_dest"]:
            for h1, h2 in zip(times["time"], times["time_dest"]):
                out_spec = [
                    yr,
                    yr,
                    "mode",
                    "node",
                    com_dict[tec]["output"],
                    "level",
                    h1,
                    h2,
                ]
                scen.add_par("output", ["node", tec] + out_spec, 1, "-")
        if times["time_origin"]:
            for h1, h2 in zip(times["time"], times["time_origin"]):
                inp_spec = [
                    yr,
                    yr,
                    "mode",
                    "node",
                    com_dict[tec]["input"],
                    "level",
                    h1,
                    h2,
                ]
                scen.add_par("input", ["node", tec] + inp_spec, 1, "-")

    # Adding capacity related parameters
    if capacity:
        add_cap_par(scen, [2020], "gas_ppl")

    # Committing and solving
    scen.commit("scenario was set up.")
    scen.solve(case=comment)

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
    if capacity:
        for h in act.loc[act["technology"] == "gas_ppl"]["time"]:
            act.loc[
                (act["time"] == h) & (act["technology"] == "gas_ppl"),
                "capacity-corrected",
            ] = act["lvl"] / float(scen.par("duration_time", {"time": h})["value"])
        assert max(
            act.loc[act["technology"] == "gas_ppl", "capacity-corrected"]
        ) == float(scen.var("CAP", {"technology": "gas_ppl"})["lvl"])


# Main tests for commodity balance over various temporal levels (and "time" index)
# In these tests, "demand" is defined in different time slices
# with different "duration_time", there is one power plant ("gas_ppl") to meet "demand",
# which receives fuel from a supply technology ("gas_supply").
# Different temporal level hierarchies are tested, by linkages of "ACT" with
# "demand" and "CAP".


def test_temporal_levels_not_linked(test_mp):
    """
    Testing two unlinked temporal levels.

    "gas_ppl" is active in "summer" and NOT linked to "gas_supply" in "year"
    This setup should not solve.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "1.not-linked"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["summer"],
            "time": ["summer"],
            "time_dest": ["summer"],
        },
        "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
    }

    # Check the model not solve if there is no link between fuel supply and power plant
    with pytest.raises(ModelError):
        model_generator(
            test_mp,
            comment,
            tec_dict,
            time_steps=[("summer", 1, "season", "year")],
            demand={"summer": 2},
        )


def test_season_to_year(test_mp):
    """
    Testing two linked temporal levels.

    Linking "gas_ppl" and "gas_supply" at one temporal level (e.g., "year")
    Only one "season" (duration = 1) and "demand" is defined only at "summer"
    Model solves and "gas_supply" is active.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "2.linked-one-season-with-year"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year"],
            "time": ["summer"],
            "time_dest": ["summer"],
        },
        "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
    }
    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[("summer", 1, "season", "year")],
        demand={"summer": 2},
    )


def test_two_seasons_to_year(test_mp):
    """
    Testing two linked temporal levels with two seasons.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5)
    Model solves and "gas_supply" is active.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "3a.linked-two-seasons-with-year"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
        "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
    }

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 1, "winter": 1},
    )


def test_two_seasons_to_year_relative(test_mp):
    """
    Testing two linked temporal levels with two seasons and a relative time.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5)
    Model should not solve.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "3a.linked-two-seasons-with-year-relative"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
        "gas_supply": {"time_origin": [], "time": ["year"], "time_dest": ["year"]},
    }
    # Shouldn't pass the test, if adding relative duration time
    try:
        model_generator(
            test_mp,
            comment,
            tec_dict,
            time_steps=[
                ("summer", 0.5, "season", "year"),
                ("winter", 0.5, "season", "year"),
            ],
            relative_time=["year"],
            demand={"summer": 1, "winter": 1},
        )
    except AssertionError:
        pass


def test_seasons_to_seasons(test_mp):
    """
    Testing two seasons at one temporal level.

    "demand" in two time slices: "summer" and "winter" (duration = 0.5)
    Model solves and "gas_supply" is active.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "3b.linked-two-seasons-with-two-seasons"
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

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 1, "winter": 1},
    )


def test_unlinked_three_temporal_levels(test_mp):
    """
    Testing three unlinked temporal levels.

    "month" is defined under "season" BUT "season" not linked to "year".
    Model should not solve.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4a.unlinked-temporal-levels"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["Jan", "Feb"],
            "time_dest": ["Jan", "Feb"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["year"],
            "time_dest": ["year"],
        },
    }

    # Check the model shouldn't solve
    with pytest.raises(ModelError):
        model_generator(
            test_mp,
            comment,
            tec_dict,
            time_steps=[
                ("Jan", 0.25, "month", "winter"),
                ("Feb", 0.25, "month", "winter"),
                ("Jun", 0.25, "month", "summer"),
                ("Jul", 0.25, "month", "summer"),
            ],
            demand={"Jan": 1, "Feb": 1},
        )


def test_linked_three_temporal_levels(test_mp):
    """
    Testing three linked temporal levels.

    "month" is defined under "season", and "season" is linked to "year".
    Model solves.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4b.linked-temporal-levels"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["Jan", "Feb"],
            "time_dest": ["Jan", "Feb"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["year"],
            "time_dest": ["year"],
        },
    }
    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
            ("Jan", 0.25, "month", "winter"),
            ("Feb", 0.25, "month", "winter"),
            ("Jun", 0.25, "month", "summer"),
            ("Jul", 0.25, "month", "summer"),
        ],
        demand={"Jan": 1, "Feb": 1},
    )


def test_linked_three_temporal_levels_relative(test_mp):
    """
    Testing three linked temporal levels with a relative time.

    "month" is defined under "season", and "season" is linked to "year".
    Model solves.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4b.linked-temporal-levels-relative"
    # Dictionary of technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": ["year", "year"],
            "time": ["Jan", "Feb"],
            "time_dest": ["Jan", "Feb"],
        },
        "gas_supply": {
            "time_origin": [],
            "time": ["year"],
            "time_dest": ["year"],
        },
    }

    # Shouldn't pass with a relative time duration
    try:
        model_generator(
            test_mp,
            comment,
            tec_dict,
            time_steps=[
                ("summer", 0.5, "season", "year"),
                ("winter", 0.5, "season", "year"),
                ("Jan", 0.25, "month", "winter"),
                ("Feb", 0.25, "month", "winter"),
                ("Jun", 0.25, "month", "summer"),
                ("Jul", 0.25, "month", "summer"),
            ],
            relative_time=["year", "summer"],
            demand={"Jan": 1, "Feb": 1},
        )
    except AssertionError:
        pass


def test_linked_three_temporal_levels_month_to_year(test_mp):
    """
    Testing three linked temporal levels from month to season and year.

    "month" is linked to "season", and "season" is linked to "year".
    Model solves.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4c.linked-temporal-levels-month-to-year"
    # Dictionary of technology input/output
    tec_dict = {
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

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
            ("Jan", 0.25, "month", "winter"),
            ("Feb", 0.25, "month", "winter"),
            ("Jun", 0.25, "month", "summer"),
            ("Jul", 0.25, "month", "summer"),
        ],
        demand={"year": 2},
    )


def test_linked_three_temporal_levels_season_to_year(test_mp):
    """
    Testing three linked temporal levels from season to year.

    season" is linked to "year". Model solves.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4d.linked-temporal-levels-season-to-year"
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

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
            ("Jan", 0.25, "month", "winter"),
            ("Feb", 0.25, "month", "winter"),
            ("Jun", 0.25, "month", "summer"),
            ("Jul", 0.25, "month", "summer"),
        ],
        demand={"year": 2},
    )


def test_linked_three_temporal_levels_time_act(test_mp):
    """
    Testing three linked temporal levels, with activity only at "time".
    Model solves.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4e.time-divider-aggregator"
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

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"year": 2},
    )


def test_linked_three_temporal_levels_different_duration(test_mp):
    """
    Testing three linked temporal levels with different duration times.
    Model solves, linking "month" through "season" to "year".

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "4f.linked-temporal-levels-different-duration"
    # Dictionary of technology input/output
    tec_dict = {
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

    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
            ("Jan", 0.4, "month", "winter"),
            ("Feb", 0.1, "month", "winter"),
            ("Jun", 0.3, "month", "summer"),
            ("Jul", 0.2, "month", "summer"),
        ],
        demand={"year": 2},
    )
