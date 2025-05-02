from typing import Union

import numpy as np
import pandas as pd
from ixmp import Platform

from message_ix import Scenario
from message_ix.testing import SCENARIO

# First model year of the Dantzig scenario
_year = 1963

addon_share = pd.DataFrame(
    {
        "node": "seattle",
        "technology": "canning_plant",
        "year_act": _year,
        "mode": "production",
        "time": "year",
        "type_addon": "better_production",
        "value": 0.5,
        "unit": "%",
    },
    index=[0],
)

f = {"technology": "canning_plant", "node_loc": "seattle"}
g = {"technology": "canning_addon", "node_loc": "seattle"}


def add_addon(
    s: Scenario, costs: Union[bool, int] = False, zero_output: bool = False
) -> None:
    s.check_out()
    s.add_set("technology", "canning_addon")
    s.add_set("addon", "canning_addon")
    s.add_cat("addon", "better_production", "canning_addon")
    s.add_set("map_tec_addon", ["canning_plant", "better_production"])
    conversion_df = pd.DataFrame(
        {
            "node": "seattle",
            "technology": "canning_plant",
            "year_vtg": _year,
            "year_act": _year,
            "mode": "production",
            "time": "year",
            "type_addon": "better_production",
            "unit": "cases",
            "value": 1.0,
        },
        index=[0],
    )

    s.add_par("addon_conversion", conversion_df)

    # optionally add negative costs to addon to ensure that upper bound works
    if costs:
        var = s.par(
            "var_cost",
            {
                "node_loc": "seattle",
                "technology": "transport_from_seattle",
                "mode": "to_new-york",
            },
        )
        var["technology"] = "canning_addon"
        var["mode"] = "production"
        var["value"] = costs
        s.add_par("var_cost", var)

    # add output (zero explicity to make sure that `map_tec_*` is generated)
    outp = s.par("output", {"technology": "canning_plant", "node_loc": "seattle"})
    outp["technology"] = "canning_addon"
    if zero_output:
        outp["value"] = 0
    s.add_par("output", outp)

    s.commit("adding addon technology")


# reduce max activity from one canning plant, has to be compensated by addon
def test_addon_tec(message_test_mp: Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone(
        scenario="addon", keep_solution=False
    )

    add_addon(scen, costs=-1)

    scen.check_out()
    bda = scen.par("bound_activity_up", f)
    bda["value"] = bda["value"] / 2
    scen.add_par("bound_activity_up", bda)
    scen.commit("changing output and bounds")

    scen.solve(quiet=True)

    exp = scen.var("ACT", f)["lvl"]
    obs = scen.var("ACT", g)["lvl"]
    assert np.isclose(exp, obs)


# introduce addon technology with negatove costs, add maximum mitigation
def test_addon_up(message_test_mp: Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone(
        scenario="addon_up", keep_solution=False
    )
    add_addon(scen, costs=-1, zero_output=True)

    scen.check_out()
    scen.add_par("addon_up", addon_share)
    scen.commit("adding upper bound on addon technology")

    scen.solve(quiet=True)

    exp = scen.var("ACT", f)["lvl"] * 0.5
    obs = scen.var("ACT", g)["lvl"]
    assert np.isclose(exp, obs)


# introduce addon technology with positive costs, add minimum mitigation
def test_addon_lo(message_test_mp: Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone(
        scenario="addon_lo", keep_solution=False
    )
    add_addon(scen, costs=1, zero_output=True)

    scen.check_out()

    scen.add_par("addon_lo", addon_share)

    scen.commit("adding lower bound on addon technology")
    scen.solve(quiet=True)

    exp = scen.var("ACT", f)["lvl"] * 0.5
    obs = scen.var("ACT", g)["lvl"]
    assert np.isclose(exp, obs)
