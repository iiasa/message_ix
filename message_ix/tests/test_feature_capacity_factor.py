"""
This test is designed to check if parameter "capacity_factor" works for models
with sub-annual time slices (index of "time" in MESSAGEix) as expected or not.

"""

from itertools import product

import pytest

from message_ix import ModelError, Scenario


def add_cap_par(scen, years, capacity):
    """
    Adding required parameters for representing "capacity" in a MESSAGEix model.

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

    for year, tec in product(years, capacity.keys()):
        for parname, val in capacity[tec].items():
            scen.add_par(parname, ["node", tec, year], val, "-")


def model_generator(
    test_mp,
    comment,
    tec_dict,
    time_steps,
    demand,
    com_dict={"gas_ppl": {"input": "fuel", "output": "electr"}},
    yr=2020,
    capacity={"gas_ppl": {"inv_cost": 0.1, "technical_lifetime": 5}},
    capacity_factor={},
    var_cost={},
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
    capacity : dict
        Data for "inv_cost" and "technical_lifetime" per technology.
    capacity_factor : dict, optional
        "capacity_factor" with technology as key and "time"/"value" pairs as value.
    var_cost : dict, optional
        "var_cost" with technology as key and "time"/"value" pairs as value.
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
        add_cap_par(scen, [2020], capacity)

    # Adding capacity factor (optional)
    for tec, data in capacity_factor.items():
        for h, val in data.items():
            scen.add_par("capacity_factor", ["node", tec, yr, yr, h], val, "-")

    # Adding variable cost (optional)
    for tec, data in var_cost.items():
        for h, val in data.items():
            scen.add_par("var_cost", ["node", tec, yr, yr, "mode", h], val, "-")

    # Committing and solving
    scen.commit("scenario was set up.")
    scen.solve(case=comment)

    # Reading "ACT" and "CAP" from the solution
    act = scen.var("ACT").set_index(["technology", "time"])
    cap = scen.var("CAP").set_index(["technology"])

    # 1) Test "ACT" is zero when capacity factor is zero
    cf = scen.par("capacity_factor").set_index(["technology", "time"])
    cf_zero = cf.loc[cf["value"] == 0]
    for i in cf_zero.index:
        assert act.loc[i, "lvl"] == 0

    # 2) Test if "CAP" is correctly calculated based on "ACT" and "capacity_factor"
    if capacity:
        for i in act.loc[act["lvl"] > 0].index:
            # Correcting ACT based on duration of each time slice
            duration = float(scen.par("duration_time", {"time": i[1]})["value"])
            act.loc[i, "duration-corrected"] = act.loc[i, "lvl"] / duration
            # Dividing by (non-zero) capacity factor
            act.loc[i, "cf-corrected"] = act.loc[i, "duration-corrected"] / float(
                cf.loc[i, "value"]
            )
        act = act.fillna(0).reset_index().set_index(["technology"])
        # CAP = max("ACT" / "duration_time" / "capcity_factor")
        for i in cap.index:
            assert max(act.loc[i, "cf-corrected"]) == float(cap.loc[i, "lvl"])


# Main tests for checking the behaviour of "capacity_factor"
def test_capacity_factor_time(test_mp):
    """
    Testing capacity factor (CF) is calculated correctly in a model with
    different CF per time slice.


    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "capacity-factor-time"
    # Technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": [],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
    }

    # Build model and solve
    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0.6}},
        var_cost={"gas_ppl": {"summer": 0.2, "winter": 0.2}},
    )


def test_capacity_factor_unequal_time(test_mp):
    """
    Testing capacity factor (CF) is calculated correctly in a model with
    different duration per time slice.


    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "capacity-factor-unequal-time"
    # Technology input/output
    tec_dict = {
        "gas_ppl": {
            "time_origin": [],
            "time": ["summer", "winter"],
            "time_dest": ["summer", "winter"],
        },
    }

    # # Build model and solve
    model_generator(
        test_mp,
        comment,
        tec_dict,
        time_steps=[
            ("summer", 0.3, "season", "year"),
            ("winter", 0.7, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0.8}},
        var_cost={"gas_ppl": {"summer": 0.2, "winter": 0.2}},
    )


def test_capacity_factor_zero(test_mp):
    """
    Testing zero capacity factor (CF) in a time slice.

    "solar_pv_ppl" is active in "day" and NOT at "night" (CF = 0).
    It is expected that the model will be infeasible, because "demand" at night
    cannot be met.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "capacity-factor-zero"
    # Technology input/output
    tec_dict = {
        "solar_pv_ppl": {
            "time_origin": [],
            "time": ["day", "night"],
            "time_dest": ["day", "night"],
        },
    }

    # Build model and solve (should raise GAMS error)
    with pytest.raises(ModelError):
        model_generator(
            test_mp,
            comment,
            tec_dict,
            com_dict={"solar_pv_ppl": {"input": "fuel", "output": "electr"}},
            time_steps=[
                ("day", 0.5, "subannual", "year"),
                ("night", 0.5, "subannual", "year"),
            ],
            demand={"day": 2, "night": 1},
            capacity={"solar_pv_ppl": {"inv_cost": 0.2, "technical_lifetime": 5}},
            capacity_factor={"solar_pv_ppl": {"day": 0.8, "night": 0}},
        )


def test_capacity_factor_zero_two(test_mp):
    """
    Testing zero capacity factor (CF) in a time slice.

    "solar_pv_ppl" is active in "day" and NOT at "night" (CF = 0).
    The model output should show no activity of "solar_pv_ppl" at "night".
    So, "gas_ppl" is active at "night", even though a more expensive technology.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "capacity-factor-zero-two"
    # Technology input/output
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
    model_generator(
        test_mp,
        comment,
        tec_dict,
        com_dict={
            "solar_pv_ppl": {"input": "fuel", "output": "electr"},
            "gas_ppl": {"input": "fuel", "output": "electr"},
        },
        time_steps=[
            ("day", 0.5, "season", "year"),
            ("night", 0.5, "season", "year"),
        ],
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
    )
