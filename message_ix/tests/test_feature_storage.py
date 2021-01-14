# -*- coding: utf-8 -*-
"""
This is a unit test for representing storage in the MESSAGEix model, and
testing the functionality of storage equations. The workflow is as follows:
    - building a stylized MESSAGEix model
    - adding seasonality and modifying parameters for timesteps accordingly
    - adding storage implementation (dam: storage device, pump: charger,
                                     turbine: discharger)
    - testing storage functionality and equations

"""

from itertools import product

from message_ix import Scenario


# A function for generating a simple MESSAGEix model with two technologies
def model_setup(scen, years):
    scen.add_set("node", "node")
    scen.add_set("commodity", "electr")
    scen.add_set("level", "level")
    scen.add_set("year", years)
    scen.add_set("type_year", years)
    scen.add_set("technology", ["wind_ppl", "gas_ppl"])
    scen.add_set("mode", "mode")
    output_specs = ["node", "electr", "level", "year", "year"]
    # Two technologies, one cheaper than the other
    var_cost = {"wind_ppl": 0, "gas_ppl": 2}
    for year, (tec, cost) in product(years, var_cost.items()):
        scen.add_par("demand", ["node", "electr", "level", year, "year"], 1, "GWa")
        tec_specs = ["node", tec, year, year, "mode"]
        scen.add_par("output", tec_specs + output_specs, 1, "GWa")
        scen.add_par("var_cost", tec_specs + ["year"], cost, "USD/GWa")


# A function for adding sub-annual time steps to a MESSAGEix model
def add_seasonality(scen, time_duration):
    scen.add_set("time", sorted(list(set(time_duration.keys()))))
    scen.add_set("lvl_temporal", "season")
    for h, duration in time_duration.items():
        scen.add_set("map_temporal_hierarchy", ["season", h, "year"])
        scen.add_par("duration_time", [h], duration, "-")


# A function for modifying model parameters after adding sub-annual time steps
def year_to_time(scen, parname, time_share):
    old = scen.par(parname)
    scen.remove_par(parname, old)
    time_idx = [x for x in scen.idx_names(parname) if "time" in x]
    for h, share in time_share.items():
        new = old.copy()
        for index in time_idx:
            new[index] = h
        new["value"] = share * old["value"]
        scen.add_par(parname, new)


# A function for adding storage technologies and parameterization
def add_storage_data(scen, time_order):
    # Adding level of storage
    scen.add_set("level", "storage")

    # Adding storage technologies (reservoir, charger, and discharger)
    scen.add_set("technology", ["dam", "pump", "turbine"])

    # Adding a storage commodity
    scen.add_set("commodity", ["water", "cooling", "dummay"])

    # Specifying storage reservoir technology
    scen.add_set("storage_tec", "dam")

    # Specifying storage level
    scen.add_set("level_storage", "storage")

    # Adding mapping for storage and charger/discharger technologies
    for tec in ["pump", "turbine"]:
        scen.add_set("map_tec_storage", ["node", tec, "dam", "storage", "water"])

    # Adding time sequence
    for h in time_order.keys():
        scen.add_par("time_order", ["season", h], time_order[h], "-")

    # Adding input, output, and capacity factor for storage technologies
    output_spec = {
        "dam": ["node", "dummay", "level"],
        "pump": ["node", "water", "storage"],
        "turbine": ["node", "electr", "level"],
    }

    input_spec = {
        "dam": ["node", "cooling", "level"],
        "pump": ["node", "electr", "level"],
        "turbine": ["node", "water", "storage"],
    }

    var_cost = {"dam": 0, "pump": 0.2, "turbine": 0.3}
    stor_tecs = ["dam", "pump", "turbine"]
    for year, h, tec in product(set(scen.set("year")), time_order.keys(), stor_tecs):
        tec_sp = ["node", tec, year, year, "mode"]
        scen.add_par("output", tec_sp + output_spec[tec] + [h, h], 1, "GWa")
        scen.add_par("input", tec_sp + input_spec[tec] + [h, h], 1, "GWa")
        scen.add_par("var_cost", tec_sp + [h], var_cost[tec], "USD/GWa")

    # Adding storage self-discharge (as %) and initial content
    for year, h in product(set(scen.set("year")), time_order.keys()):
        storage_spec = ["node", "dam", "storage", "water", year, h]
        scen.add_par("storage_self_discharge", storage_spec, 0.05, "%")

        # Adding initial content of storage (optional)
        storage_spec = ["node", "dam", "storage", "water", year, "a"]
        scen.add_par("storage_initial", storage_spec, 0.08, "GWa")


# Main function for building a model with storage and testing the functionality
def storage_setup(test_mp, time_duration, comment):

    # First, building a simple model and adding seasonality
    scen = Scenario(test_mp, "no_storage", "standard", version="new")
    model_setup(scen, [2020])
    add_seasonality(scen, time_duration)
    # Fixed share for parameters that don't change across timesteps
    fixed_share = {"a": 1, "b": 1, "c": 1, "d": 1}
    year_to_time(scen, "output", fixed_share)
    year_to_time(scen, "var_cost", fixed_share)
    # Variable share for parameters that are changing in each timestep
    # share of demand in each season from annual demand
    demand_share = {"a": 0.15, "b": 0.2, "c": 0.4, "d": 0.25}
    year_to_time(scen, "demand", demand_share)
    scen.commit("initialized a model with timesteps")
    scen.solve(case="no_storage" + comment)

    # Second, adding upper bound on activity of the cheap technology (wind_ppl)
    scen.remove_solution()
    scen.check_out()
    for h in time_duration.keys():
        scen.add_par(
            "bound_activity_up", ["node", "wind_ppl", 2020, "mode", h], 0.25, "GWa"
        )
    scen.commit("activity bounded")
    scen.solve(case="no_storage_bounded" + comment)
    cost_no_stor = scen.var("OBJ")["lvl"]
    act_no_stor = scen.var("ACT", {"technology": "gas_ppl"})["lvl"].sum()

    # Third, adding storage technologies but with no input to storage device
    scen.remove_solution()
    scen.check_out()
    # Chronological order of timesteps in the year
    time_order = {"a": 1, "b": 2, "c": 3, "d": 4}
    add_storage_data(scen, time_order)
    scen.commit("storage data added")
    scen.solve(case="with_storage_no_input" + comment)
    act = scen.var("ACT")

    # Forth, adding storage technologies and providing input to storage device
    scen.remove_solution()
    scen.check_out()
    # Adding a new technology "cooler" to provide input of "cooling" to dam
    scen.add_set("technology", "cooler")
    df = scen.par("output", {"technology": "turbine"})
    df["technology"] = "cooler"
    df["commodity"] = "cooling"
    scen.add_par("output", df)
    # Changing input of dam from 1 to 1.2 to test commodity balance
    df = scen.par("input", {"technology": "dam"})
    df["value"] = 1.2
    scen.add_par("input", df)
    scen.commit("storage needs no separate input")
    scen.solve(case="with_storage_and_input" + comment)
    cost_with_stor = scen.var("OBJ")["lvl"]
    act_with_stor = scen.var("ACT", {"technology": "gas_ppl"})["lvl"].sum()

    # Fifth. Tests for the functionality of storage
    # 1. Check that "dam" is not active if no "input" commodity is defined
    assert "dam" not in act[act["lvl"] > 0]["technology"].tolist()

    # 2. Testing functionality of storage
    # Check the contribution of storage to the system cost
    assert cost_with_stor < cost_no_stor
    # Activity of expensive technology should be lower with storage
    assert act_with_stor < act_no_stor

    # 3. Activity of discharger <= activity of charger + initial content
    act_pump = scen.var("ACT", {"technology": "pump"})["lvl"]
    act_turb = scen.var("ACT", {"technology": "turbine"})["lvl"]
    initial_content = float(scen.par("storage_initial")["value"])
    assert act_turb.sum() <= act_pump.sum() + initial_content

    # 4. Activity of input provider to storage = act of storage * storage input
    for ts in time_duration.keys():
        act_cooler = scen.var("ACT", {"technology": "cooler", "time": ts})["lvl"]
        inp = scen.par("input", {"technology": "dam", "time": ts})["value"]
        act_stor = scen.var("ACT", {"technology": "dam", "time": ts})["lvl"]
        assert float(act_cooler) == float(inp) * float(act_stor)

    # 5. Max activity of charger <= max activity of storage
    max_pump = max(act_pump)
    act_storage = scen.var("ACT", {"technology": "dam"})["lvl"]
    max_stor = max(act_storage)
    assert max_pump <= max_stor

    # 6. Max activity of discharger <= max storage act - self discharge losses
    max_turb = max(act_turb)
    loss = scen.par("storage_self_discharge")["value"][0]
    assert max_turb <= max_stor * (1 - loss)

    # Sixth, testing equations of storage (when added to ixmp variables)
    if scen.has_var("STORAGE"):
        # 1. Equality: storage content in the beginning and end is related
        storage_first = scen.var("STORAGE", {"time": "a"})["lvl"]
        storage_last = scen.var("STORAGE", {"time": "d"})["lvl"]
        relation = scen.par("relation_storage", {"time_first": "d", "time_last": "a"})[
            "value"
        ][0]
        assert storage_last >= storage_first * relation

        # 2. Storage content should never exceed storage activity
        assert max(scen.var("STORAGE")["lvl"]) <= max_stor

        # 3. Commodity balance: charge - discharge - losses = 0
        change = scen.var("STORAGE_CHARGE").set_index(["year_act", "time"])["lvl"]
        loss = scen.par("storage_self_discharge").set_index(["year", "time"])["value"]
        assert sum(change[change > 0] * (1 - loss)) == -sum(change[change < 0])

        # 4. Energy balance: storage change + losses = storage content
        storage = scen.var("STORAGE").set_index(["year", "time"])["lvl"]
        assert storage[(2020, "b")] * (1 - loss[(2020, "b")]) == -change[(2020, "c")]


# Storage test for different duration times
def test_storage(test_mp):
    """
    Testing storage setup with equal and unequal duration of seasons"

    """
    time_duration = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
    storage_setup(test_mp, time_duration, "_equal_time")

    time_duration = {"a": 0.3, "b": 0.25, "c": 0.25, "d": 0.2}
    storage_setup(test_mp, time_duration, "_unequal_time")
