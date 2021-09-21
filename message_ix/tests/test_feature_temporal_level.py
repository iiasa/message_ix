# -*- coding: utf-8 -*-
"""
This test ensures that COMMODITY_BALANCE works for (sub-annual) time slices (index of "time" in MESSAGEix)
at different temporal levels, like seasons, months, etc., and with different duration times.

"""

import pytest
from itertools import product
from message_ix import Scenario


# A function for adding required parameters for representing "capacity"
def add_cap_par(scen, years, tec, data={"inv_cost": 0.1, "technical_lifetime": 5}):

    for year, (parname, val) in product(years, data.items()):
        scen.add_par(parname, ["node", tec, year], val, "-")


# A function for generating a simple model with sub-annual time slices
def model_generator(
    test_mp,
    comment,
    tec_dict,
    com_dict,
    time_steps,
    demand,
    yr=2020,
    capacity=True,
    unit="GWa",
):
    """

    Generates a simple model with two technologies, and a flexible number of time slices.

    Parameters
    ----------
    test_mp : ixmp.Platform()
    comment : string
        Annotation for saving different scenarios and comparing their results.
    tec_dict : dict
        A dictionary for a technology and required information for time-related parameters.
        (e.g., tec_dict = {"gas_ppl": {"time_origin": ["summer"], "time": ["summer"], "time_dest": ["summer"]})
    com_dict : dict
        A dictionary for specifying "input" and "output" commodities.
        (e.g., com_dict = {"gas_ppl": {"input": "fuel", "output": "electr"}})
    time_steps : list of tuples
        Information about each time slice, packed in a tuple with four elements,
        including: time slice name, duration relative to "year", "temporal_lvl", and parent time slice.
        (e.g., time_steps = [("summer", 1, "season", "year")])
    demand : dict
        A dictionary for information of "demand" in each time slice.
        (e.g., demand = {"summer": 2.5})
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
