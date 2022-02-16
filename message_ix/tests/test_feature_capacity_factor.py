"""
This test is designed to check if parameter "capacity_factor" works for models
with sub-annual time slices (index of "time" in MESSAGEix) as expected or not.

"""

from itertools import product

from message_ix import Scenario


def add_cap_par(scen, years, tec, data={"inv_cost": 0.1, "technical_lifetime": 5}):
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

    for year, (parname, val) in product(years, data.items()):
        scen.add_par(parname, ["node", tec, year], val, "-")


def model_generator(
    test_mp,
    comment,
    tec_dict,
    time_steps,
    demand,
    com_dict={"gas_ppl": {"input": "fuel", "output": "electr"}},
    yr=2020,
    capacity=True,
    capacity_factor={},
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
    capacity_factor : dict
        "capacity_factor" with technology as key and "time"/"value" pairs as value.
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
        add_cap_par(scen, [2020], "gas_ppl")

    # Adding capacity factor (optional)
    for tec, data in capacity_factor.items():
        for h, val in data.items():
            scen.add_par("capacity_factor", ["node", tec, yr, yr, h], val, "-")

    # Committing and solving
    scen.commit("scenario was set up.")
    scen.solve(case=comment)

    # Reading "ACT" and "CAP" from the solution
    act = scen.var("ACT", {"technology": "gas_ppl"}).set_index(["technology", "time"])
    cap = scen.var("CAP")

    # 1) Test "ACT" is zero when capacity factor is zero
    cf = scen.par("capacity_factor").set_index(["technology", "time"])
    cf_zero = cf.loc[cf["value"] == 0]
    for i in cf_zero.index:
        assert act.loc[i, "lvl"] == 0

    # 2) Test if "CAP" is correctly calculated based on "ACT" and "capacity_factor"
    if capacity:
        for i in act.index:
            # Correcting ACT based on duration of each time slice
            duration = float(scen.par("duration_time", {"time": i[1]})["value"])
            act.loc[i, "duration-corrected"] = act.loc[i, "lvl"] / duration
            # Dividing by (non-zero) capacity factor
            cf = cf.loc[cf["value"] > 0]
            act.loc[i, "cf-corrected"] = act.loc[i, "duration-corrected"] / float(
                cf.loc[i, "value"]
            )
        # CAP = max("ACT" / "duration_time" / "capcity_factor")
        assert max(act["cf-corrected"]) == float(cap["lvl"])


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
    )


def test_capacity_factor_zero(test_mp):
    """
    Testing zero capacity factor (CF) in a time slice.

    "gas_ppl" is active in "summer" and NOT active in "winter" (CF = 0).
    It is expected that the model output shows no activity (ACT = 0) in "winter".

    Parameters
    ----------
    test_mp : ixmp.Platform()
    """
    comment = "capacity-factor-zero"
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
            ("summer", 0.5, "season", "year"),
            ("winter", 0.5, "season", "year"),
        ],
        demand={"summer": 2, "winter": 1},
        capacity_factor={"gas_ppl": {"summer": 0.8, "winter": 0}},
    )
