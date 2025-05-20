"""Test storage representation.

This is a unit test for representing storage in the MESSAGEix model, and testing the
functionality of storage equations. The workflow is as follows:

- Build a stylized MESSAGEix model.
- Add seasonality and modify parameters for timesteps accordingly.
- Add storage implementation (dam: storage device, pump: charger, turbine: discharger).
- Test storage functionality and equations.
"""

import logging
from itertools import product
from typing import Union

import pandas as pd
import pandas.testing as pdt
import pytest
from ixmp import Platform
from ixmp.testing import assert_logs

from message_ix import Scenario
from message_ix.models import MESSAGE
from message_ix.testing import make_dantzig
from message_ix.util import expand_dims


# A function for generating a simple MESSAGEix model with two technologies
def model_setup(scen: Scenario, years: list[int]) -> None:
    scen.add_set("node", "node")
    scen.add_set("commodity", "electr")
    scen.add_set("level", "level")
    scen.add_set("year", years)
    scen.add_set("type_year", years)
    scen.add_set("technology", ["wind_ppl", "gas_ppl"])
    scen.add_set("mode", "M1")
    output_specs: list[Union[int, str]] = ["node", "electr", "level", "year", "year"]
    # Two technologies, one cheaper than the other
    var_cost = {"wind_ppl": 0, "gas_ppl": 2}
    for year, (tec, cost) in product(years, var_cost.items()):
        scen.add_par("demand", ["node", "electr", "level", year, "year"], 1, "GWa")
        tec_specs: list[Union[int, str]] = ["node", tec, year, year, "M1"]
        scen.add_par("output", tec_specs + output_specs, 1, "GWa")
        scen.add_par("var_cost", tec_specs + ["year"], cost, "USD/GWa")


# A function for adding sub-annual time steps to a MESSAGEix model
def add_seasonality(scen: Scenario, time_duration: dict[str, float]) -> None:
    scen.add_set("time", sorted(list(set(time_duration.keys()))))
    scen.add_set("lvl_temporal", "season")
    for h, duration in time_duration.items():
        scen.add_set("map_temporal_hierarchy", ["season", h, "year"])
        scen.add_par("duration_time", [h], duration, "-")


# A function for modifying model parameters after adding sub-annual time steps
def year_to_time(
    scen: Scenario, parname: str, time_share: Union[dict[str, float], dict[str, int]]
) -> None:
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
def add_storage_data(scen: Scenario, time_order: dict[str, int]) -> None:
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
        scen.add_set(
            "map_tec_storage",
            ["node", tec, "M1", "dam", "M1", "storage", "water", "season"],
        )

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
        tec_sp = ["node", tec, year, year, "M1"]
        scen.add_par("output", tec_sp + output_spec[tec] + [h, h], 1, "GWa")
        scen.add_par("input", tec_sp + input_spec[tec] + [h, h], 1, "GWa")
        scen.add_par("var_cost", tec_sp + [h], var_cost[tec], "USD/GWa")

    # Adding storage self-discharge (as %) and initial content
    for year, h in product(set(scen.set("year")), time_order.keys()):
        storage_spec = ["node", "dam", "M1", "storage", "water", year, h]
        scen.add_par("storage_self_discharge", storage_spec, 0.05, "%")

        # Adding initial content of storage (optional)
        storage_spec = ["node", "dam", "M1", "storage", "water", year, "a"]
        scen.add_par("storage_initial", storage_spec, 0.5, "%")


# Main function for building a model with storage and testing the functionality
def storage_setup(
    test_mp: Platform, time_duration: dict[str, float], comment: str
) -> None:
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
    scen.solve(case="no_storage" + comment, quiet=True)

    # Second, adding upper bound on activity of the cheap technology (wind_ppl)
    scen.remove_solution()
    scen.check_out()
    for h in time_duration.keys():
        scen.add_par(
            "bound_activity_up", ["node", "wind_ppl", 2020, "M1", h], 0.25, "GWa"
        )
    scen.commit("activity bounded")
    scen.solve(case="no_storage_bounded" + comment, quiet=True)
    cost_no_stor = scen.var("OBJ")["lvl"]
    act_no_stor = scen.var("ACT", {"technology": "gas_ppl"})["lvl"].sum()

    # Third, adding storage technologies but with no input to storage device
    scen.remove_solution()
    scen.check_out()
    # Chronological order of timesteps in the year
    time_order = {"a": 1, "b": 2, "c": 3, "d": 4}
    add_storage_data(scen, time_order)
    scen.commit("storage data added")
    scen.solve(case="with_storage_no_input" + comment, quiet=True)
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
    scen.solve(
        case="with_storage_and_input" + comment,
        quiet=True,
        var_list=["STORAGE", "STORAGE_CHARGE"],
    )
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

    # 3. Activity of discharger <= activity of charger
    act_pump = scen.var("ACT", {"technology": "pump"})["lvl"]
    act_turb = scen.var("ACT", {"technology": "turbine"})["lvl"]
    assert act_turb.sum() <= act_pump.sum()

    # 4. Activity of input provider to storage = act of storage * storage input
    act_cooler = scen.var("ACT", {"technology": "cooler"})["lvl"]
    inp = scen.par("input", {"technology": "dam"})["value"]
    act_stor = scen.var("ACT", {"technology": "dam"})["lvl"]
    pdt.assert_series_equal(inp * act_stor, act_cooler, check_names=False)

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
    if scen.has_var("STORAGE") and not scen.var("STORAGE").empty:
        # 1. Equality: storage content at the end is equal to the beginning
        # (i.e., the difference is what is pumped in the first time slice)
        storage_first = scen.var("STORAGE", {"time": "a"})["lvl"].item()
        storage_last = scen.var("STORAGE", {"time": "d"})["lvl"].item()
        pump_first = scen.var("ACT", {"technology": "pump", "time": "a"}).at[0, "lvl"]
        assert storage_last == storage_first - pump_first

        # 2. Storage content should never exceed storage activity
        assert max(scen.var("STORAGE")["lvl"]) <= max_stor

        # 3. Commodity balance: charge - discharge - losses = 0
        change = scen.var("STORAGE_CHARGE").set_index(["year", "time"])["lvl"]
        loss = scen.par("storage_self_discharge").set_index(["year", "time"])["value"]
        assert (change[change > 0] * (1 - loss)).sum() >= -(change[change < 0]).sum()

        # 4. Energy balance: storage change + losses = storage content
        storage = scen.var("STORAGE").set_index(["year", "time"])["lvl"]
        assert storage[(2020, "b")] * (1 - loss[(2020, "b")]) == -change[(2020, "c")]


# Storage test for different duration times
def test_storage(test_mp: Platform) -> None:
    """
    Testing storage setup with equal and unequal duration of seasons"

    """
    time_duration = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
    storage_setup(test_mp, time_duration, "_equal_time")

    time_duration = {"a": 0.3, "b": 0.25, "c": 0.25, "d": 0.2}
    storage_setup(test_mp, time_duration, "_unequal_time")


def test_structure(
    caplog: pytest.LogCaptureFixture, test_mp: Platform, request: pytest.FixtureRequest
) -> None:
    """:meth:`MESSAGE.initialize` and :meth:`MESSAGE.enforce` handle old structure."""
    scen = make_dantzig(test_mp, request=request)

    # Item name to use for the tests, a parameter, and its dimensions
    name = "storage_initial"
    dims = ["node", "technology", "level", "commodity", "year", "time"]
    # NB here we cannot use make_df, since that refers to the current dimensionality of
    #    storage_initial via MESSAGE.items
    data = pd.Series(
        ["topeka", "canning_plant", "supply", "cases", 1963, "year", 1.0, "kg"],
        index=dims + ["value", "unit"],
    )

    def prepare(scen: Scenario, with_data: bool = False) -> None:
        """Re-initialize to the former definition, i.e. omitting mode."""
        with scen.transact():
            scen.remove_par(name)
            scen.init_par(name, idx_sets=dims)
            if with_data:
                scen.add_par(name, data.to_frame().transpose())

    # Test by calling the MESSAGE model class methods directory. This is not the typical
    # user behaviour; we just want to avoid a more complex way of doing so.

    # Calling initialize() with no data automatically expands the dimensions
    prepare(scen)
    assert "mode" not in scen.idx_sets(name)

    with scen.transact():
        MESSAGE.initialize(scen)

    assert "mode" in scen.idx_sets(name)
    # …and enforce() completes without raising an exception
    MESSAGE.enforce(scen)

    # Now with data in storage_initial, a warning is raised
    prepare(scen, with_data=True)

    # Two context managers for the with: block
    c1 = pytest.warns(UserWarning, match="'storage_initial' has data with dimensions")
    c2 = assert_logs(caplog, "Existing index sets of 'stora", at_level=logging.WARNING)
    with c1, c2:
        with scen.transact():
            MESSAGE.initialize(scen)

    # …the dimensions are *not* expanded automatically
    assert "mode" not in scen.idx_sets(name)

    # …and the scenario would not solve
    with pytest.raises(ValueError, match="'storage_initial' has data with dimensions"):
        MESSAGE.enforce(scen)

    # expand_dims() results in the correct dimensionality and complete data
    expand_dims(scen, name, mode="production")
    assert "mode" in scen.idx_sets(name)

    # …and enforce() completes without raising an exception
    MESSAGE.enforce(scen)
