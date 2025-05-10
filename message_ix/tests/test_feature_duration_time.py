"""
This test ensures that the parameter "duration_time" is specified correctly,
and that the GAMS formulation checks pass.
Several possible combinations of temporal levels, e.g., year, seasons,
months; and different number of time slices at each level are tested.

"""

from itertools import product
from typing import Union

from ixmp import Platform

from message_ix import Scenario


# A function for generating a simple model with sub-annual time slices
def model_generator(
    test_mp: Platform,
    comment: str,
    tec_time: dict[str, list[str]],
    demand_time: dict[str, int],
    time_steps: list[tuple[str, int, str]],
    com_dict: dict[str, dict[str, str]],
    yr: int = 2020,
) -> None:
    """

    Generates a simple model with a few technologies, and a flexible number of
    time slices.

    Parameters
    ----------
    comment : string
        Annotation for saving different scenarios and comparing their results.
    tec_time : dict
        A dictionary for mapping a technology to its input/output temporal levels.
    demand_time : dict
        A dictionary for mapping the total "demand" specified at a temporal level.
    time_steps : list of tuples
        Information about each time slice, packed in a tuple with three elements,
        including: "temporal_lvl", number of time slices, and the parent time slice.
    com_dict : dict
        A dictionary for specifying "input" and "output" commodities.
    yr : int, optional
        Model year. The default is 2020.


    """

    # Building an empty scenario
    scen = Scenario(test_mp, "test_duration_time", comment, version="new")

    # Adding required sets
    scen.add_set("node", "fairyland")
    for c in com_dict.values():
        scen.add_set("commodity", [x for x in list(c.values()) if x])

    scen.add_set("level", "final")
    scen.add_set("year", yr)
    scen.add_set("type_year", yr)
    scen.add_set("technology", list(tec_time.keys()))
    scen.add_set("mode", "standard")

    # Adding "time" related info to the model: "lvl_temporal", "time",
    # "map_temporal_hierarchy", and "duration_time"
    map_time: dict[str, list[str]] = {}
    for [tmp_lvl, number, parent] in time_steps:
        scen.add_set("lvl_temporal", tmp_lvl)
        times = (
            [tmp_lvl[0] + "-" + str(x + 1) for x in range(number)]
            if parent == "year"
            else [
                p + "_" + tmp_lvl[0] + "-" + str(x + 1)
                for (p, x) in product(map_time[parent], range(number))
            ]
        )

        map_time[tmp_lvl] = times
        scen.add_set("time", times)

        # Adding "map_temporal_hierarchy" and "duration_time"
        for h in times:
            p = "year" if parent == "year" else h.split("_" + tmp_lvl[0])[0]
            # Temporal hierarchy (order: temporal level, time, parent time)
            scen.add_set("map_temporal_hierarchy", [tmp_lvl, h, p])

            # Duration time is relative to the duration of the parent temporal level
            dur_parent = scen.par("duration_time", {"time": p}).at[0, "value"]
            scen.add_par("duration_time", [h], dur_parent / number, "-")

    # Adding "demand" at a temporal level (total demand divided by the number of
    # time slices in that temporal level)
    for tmp_lvl, value in demand_time.items():
        times = scen.set("map_temporal_hierarchy", {"lvl_temporal": tmp_lvl})["time"]
        for h in times:
            scen.add_par(
                "demand",
                ["fairyland", "electr", "final", yr, h],
                value / len(times),
                "GWa",
            )

    # Adding "input" and "output" parameters of technologies
    for tec, [tmp_lvl_in, tmp_lvl_out] in tec_time.items():
        times_in = scen.set("map_temporal_hierarchy", {"lvl_temporal": tmp_lvl_in})[
            "time"
        ]
        times_out = scen.set("map_temporal_hierarchy", {"lvl_temporal": tmp_lvl_out})[
            "time"
        ]
        # If technology is linking two different temporal levels
        time_pairs = (
            product(times_in, times_out)
            if tmp_lvl_in != tmp_lvl_out
            else zip(times_in, times_out)
        )

        # Configuring data for "time_origin" and "time" in "input"
        for h_in, h_act in time_pairs:
            # "input"
            inp = com_dict[tec]["input"]
            if inp:
                inp_spec = [yr, yr, "standard", "fairyland", inp, "final", h_act, h_in]
                scen.add_par("input", ["fairyland", tec] + inp_spec, 1, "-")
        # "output"
        for h in times_out:
            out = com_dict[tec]["output"]
            out_spec: list[Union[int, str]] = [
                yr,
                yr,
                "standard",
                "fairyland",
                out,
                "final",
                h,
                h,
            ]
            scen.add_par("output", ["fairyland", tec] + out_spec, 1, "-")

    # Committing
    scen.commit("scenario was set up.")

    # Testing if the model solves in GAMS
    scen.solve(case=comment)

    # Testing if sum of "duration_time" is almost 1
    for tmp_lvl in scen.set("lvl_temporal"):
        times = scen.set("map_temporal_hierarchy", {"lvl_temporal": tmp_lvl})[
            "time"
        ].to_list()
        assert (
            abs(sum(scen.par("duration_time", {"time": times})["value"]) - 1.0) < 1e-12
        )


# Tests for "duration_time" of different numbers of time slices, at different
# temporal levels ("lvl_temporal")
# In these tests "demand" is defined in different time slices and one power plant
# to meet demand, which receives fuel from a supply technology.


# Testing one temporal level ("season") and different number of time slices
def test_season(test_mp: Platform, n_time: list[int] = [4, 12, 50]) -> None:
    comment = "season"
    com_dict = {"power-plant": {"input": "", "output": "electr"}}
    tec_time = {"power-plant": ["season", "season"]}
    demand_time = {"season": 100}

    for t in n_time:
        time_steps = [("season", t, "year")]
        # Check the model solves without error and sum of "duration_time" = 1
        model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)


# Testing one temporal level ("season") linked to "year" with a technology
def test_year_season(test_mp: Platform, n_time: list[int] = [5, 15, 27]) -> None:
    comment = "year_season"
    com_dict = {
        "power-plant": {"input": "fuel", "output": "electr"},
        "fuel-supply": {"input": "", "output": "fuel"},
    }
    tec_time = {"power-plant": ["year", "season"], "fuel-supply": ["year", "year"]}
    demand_time = {"season": 100}
    for t in n_time:
        time_steps = [("season", t, "year")]
        # Check the model solves without error and sum of "duration_time" = 1
        model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)


# Testing two temporal levels with one technology
def test_season_day(test_mp: Platform) -> None:
    comment = "4-season_24-days"
    com_dict = {"power-plant": {"input": "", "output": "electr"}}
    tec_time = {"power-plant": ["day", "day"]}
    demand_time = {"day": 100}
    time_steps = [("season", 4, "year"), ("day", 24, "season")]

    # Check the model solves without error and sum of "duration_time" = 1
    model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)


# Testing 24 days linked to four seasons, with two technologies
def test_season_day_2tech(test_mp: Platform) -> None:
    comment = "4-season_24-days_2-tech"
    com_dict = {
        "power-plant": {"input": "fuel", "output": "electr"},
        "fuel-supply": {"input": "", "output": "fuel"},
    }
    tec_time = {"power-plant": ["season", "day"], "fuel-supply": ["season", "season"]}
    demand_time = {"day": 100}
    time_steps = [("season", 4, "year"), ("day", 24, "season")]

    # Check the model solves without error and sum of "duration_time" = 1
    model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)


# Testing 60 days linked to 4 seasons linked to year, with three technology
def test_year_season_day(test_mp: Platform) -> None:
    comment = "year_4-season_30-days_3-tech"
    com_dict = {
        "power-plant": {"input": "fuel", "output": "electr"},
        "fuel-transport": {"input": "fuel", "output": "fuel"},
        "fuel-supply": {"input": "", "output": "fuel"},
    }
    tec_time = {
        "power-plant": ["season", "day"],
        "fuel-transport": ["year", "season"],
        "fuel-supply": ["year", "year"],
    }
    demand_time = {"day": 100}
    time_steps = [("season", 4, "year"), ("day", 30, "season")]

    # Check the model solves without error and sum of "duration_time" = 1
    model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)


# Testing four temporal levels (year, season, day, hour) with four technologies
def test_year_season_day_hour(test_mp: Platform) -> None:
    n_season = 4
    n_day = 2
    n_hour = 6
    comment = "y_4s_2d_6h"
    com_dict = {
        "power-plant": {"input": "fuel", "output": "electr"},
        "fuel-transport": {"input": "fuel", "output": "fuel"},
        "fuel-processing": {"input": "raw fuel", "output": "fuel"},
        "fuel-supply": {"input": "", "output": "raw fuel"},
    }
    tec_time = {
        "power-plant": ["day", "hour"],
        "fuel-transport": ["season", "day"],
        "fuel-processing": ["year", "season"],
        "fuel-supply": ["year", "year"],
    }
    demand_time = {"hour": 100}
    time_steps = [
        ("season", n_season, "year"),
        ("day", n_day, "season"),
        ("hour", n_hour, "day"),
    ]

    # Check the model solves without error and sum of "duration_time" = 1
    model_generator(test_mp, comment, tec_time, demand_time, time_steps, com_dict)
