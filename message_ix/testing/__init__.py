from typing import List, Union

import numpy as np
import pandas as pd
from ixmp import IAMC_IDX

from message_ix import Scenario, make_df

SCENARIO = {
    "dantzig": {"model": "Canning problem (MESSAGE scheme)", "scenario": "standard"},
    "dantzig multi-year": {
        "model": "Canning problem (MESSAGE scheme)",
        "scenario": "multi-year",
    },
    "westeros": {"model": "Westeros Electrified", "scenario": "baseline"},
}


# Create and populate ixmp databases

_ms: List[Union[str, float]] = [
    SCENARIO["dantzig"]["model"],
    SCENARIO["dantzig"]["scenario"],
]
HIST_DF = pd.DataFrame(
    [_ms + ["DantzigLand", "GDP", "USD", 850.0, 900.0, 950.0]],
    columns=IAMC_IDX + [1962, 1963, 1964],
)
INP_DF = pd.DataFrame(
    [_ms + ["DantzigLand", "Demand", "cases", 850.0, 900.0, 950.0]],
    columns=IAMC_IDX + [1962, 1963, 1964],
)
TS_DF = pd.concat([HIST_DF, INP_DF], sort=False)
TS_DF.sort_values(by="variable", inplace=True)
TS_DF.index = range(len(TS_DF.index))

TS_DF_CLEARED = TS_DF.copy()
TS_DF_CLEARED.loc[0, 1963] = np.nan
TS_DF_CLEARED.loc[0, 1964] = np.nan


def make_dantzig(mp, solve=False, multi_year=False, **solve_opts):
    """Return an :class:`message_ix.Scenario` for Dantzig's canning problem.

    Parameters
    ----------
    mp : ixmp.Platform
        Platform on which to create the scenario.
    solve : bool, optional
        If True, the scenario is solved.
    multi_year : bool, optional
        If True, the scenario has years 1963--1965 inclusive. Otherwise, the
        scenario has the single year 1963.
    """
    # add custom units and region for timeseries data
    mp.add_unit("USD/case")
    mp.add_unit("case")
    mp.add_region("DantzigLand", "country")

    # initialize a new (empty) instance of an `ixmp.Scenario`
    scen = Scenario(
        mp,
        model=SCENARIO["dantzig"]["model"],
        scenario="multi-year" if multi_year else "standard",
        annotation="Dantzig's canning problem as a MESSAGE-scheme Scenario",
        version="new",
    )

    # Sets
    # NB commit() is refused if technology and year are not given
    t = ["canning_plant", "transport_from_seattle", "transport_from_san-diego"]
    sets = {
        "technology": t,
        "node": "seattle san-diego new-york chicago topeka".split(),
        "mode": "production to_new-york to_chicago to_topeka".split(),
        "level": "supply consumption".split(),
        "commodity": ["cases"],
    }

    for name, values in sets.items():
        scen.add_set(name, values)

    scen.add_horizon(year=[1962, 1963], firstmodelyear=1963)

    # Parameters
    par = {}

    # Common values
    common = dict(
        commodity="cases",
        year=1963,
        year_vtg=1963,
        year_act=1963,
        time="year",
        time_dest="year",
        time_origin="year",
    )

    par["demand"] = make_df(
        "demand",
        **common,
        node=["new-york", "chicago", "topeka"],
        level="consumption",
        value=[325, 300, 275],
        unit="case",
    )
    par["bound_activity_up"] = make_df(
        "bound_activity_up",
        **common,
        node_loc=["seattle", "san-diego"],
        mode="production",
        technology="canning_plant",
        value=[350, 600],
        unit="case",
    )
    par["ref_activity"] = par["bound_activity_up"].copy()

    input = pd.DataFrame(
        [
            ["to_new-york", "seattle", "seattle", t[1]],
            ["to_chicago", "seattle", "seattle", t[1]],
            ["to_topeka", "seattle", "seattle", t[1]],
            ["to_new-york", "san-diego", "san-diego", t[2]],
            ["to_chicago", "san-diego", "san-diego", t[2]],
            ["to_topeka", "san-diego", "san-diego", t[2]],
        ],
        columns=["mode", "node_loc", "node_origin", "technology"],
    )
    par["input"] = make_df(
        "input",
        **input,
        **common,
        level="supply",
        value=1,
        unit="case",
    )

    output = pd.DataFrame(
        [
            ["supply", "production", "seattle", "seattle", t[0]],
            ["supply", "production", "san-diego", "san-diego", t[0]],
            ["consumption", "to_new-york", "new-york", "seattle", t[1]],
            ["consumption", "to_chicago", "chicago", "seattle", t[1]],
            ["consumption", "to_topeka", "topeka", "seattle", t[1]],
            ["consumption", "to_new-york", "new-york", "san-diego", t[2]],
            ["consumption", "to_chicago", "chicago", "san-diego", t[2]],
            ["consumption", "to_topeka", "topeka", "san-diego", t[2]],
        ],
        columns=["level", "mode", "node_dest", "node_loc", "technology"],
    )
    par["output"] = make_df("output", **output, **common, value=1, unit="case")

    # Variable cost: cost per kilometre × distance (neither parametrized
    # explicitly)
    var_cost = pd.DataFrame(
        [
            ["to_new-york", "seattle", "transport_from_seattle", 0.225],
            ["to_chicago", "seattle", "transport_from_seattle", 0.153],
            ["to_topeka", "seattle", "transport_from_seattle", 0.162],
            ["to_new-york", "san-diego", "transport_from_san-diego", 0.225],
            ["to_chicago", "san-diego", "transport_from_san-diego", 0.162],
            ["to_topeka", "san-diego", "transport_from_san-diego", 0.126],
        ],
        columns=["mode", "node_loc", "technology", "value"],
    )
    par["var_cost"] = make_df("var_cost", **var_cost, **common, unit="USD/case")

    for name, value in par.items():
        scen.add_par(name, value)

    if multi_year:
        scen.add_set("year", [1964, 1965])
        scen.add_par("technical_lifetime", ["seattle", "canning_plant", 1964], 3, "y")

    if solve:
        # Always read one equation. Used by test_core.test_year_int.
        scen.init_equ(
            "COMMODITY_BALANCE_GT", ["node", "commodity", "level", "year", "time"]
        )
        solve_opts["equ_list"] = solve_opts.get("equ_list", []) + [
            "COMMODITY_BALANCE_GT"
        ]

    scen.commit("Created a MESSAGE-scheme version of the transport problem.")
    scen.set_as_default()

    if solve:
        scen.solve(**solve_opts)

    scen.check_out(timeseries_only=True)
    scen.add_timeseries(HIST_DF, meta=True)
    scen.add_timeseries(INP_DF)
    scen.commit("Import Dantzig's transport problem for testing.")

    return scen


def make_westeros(mp, emissions=False, solve=False):
    """Return an :class:`message_ix.Scenario` for the Westeros model.

    This is the same model used in the ``westeros_baseline.ipynb`` tutorial.

    Parameters
    ----------
    mp : ixmp.Platform
        Platform on which to create the scenario.
    emissions : bool, optional
        If True, the ``emissions_factor`` parameter is also populated for CO2.
    solve : bool, optional
        If True, the scenario is solved.
    """
    mp.add_unit("USD/kW")
    mp.add_unit("tCO2/kWa")
    scen = Scenario(mp, version="new", **SCENARIO["westeros"])

    # Sets
    history = [690]
    model_horizon = [700, 710, 720]
    scen.add_horizon(year=history + model_horizon, firstmodelyear=model_horizon[0])
    year_df = scen.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    country = "Westeros"
    scen.add_spatial_sets({"country": country})

    sets = dict(
        technology="coal_ppl wind_ppl grid bulb".split(),
        mode=["standard"],
        level="secondary final useful".split(),
        commodity="electricity light".split(),
    )
    for name, values in sets.items():
        scen.add_set(name, values)

    # Parameters — copy & paste from the tutorial notebook

    common = dict(
        node=country,
        node_loc=country,
        node_dest=country,
        node_origin=country,
        year=model_horizon,
        year_vtg=vintage_years,
        year_act=act_years,
        mode="standard",
        time="year",
        time_dest="year",
        time_origin="year",
    )

    gdp_profile = np.array([1.0, 1.5, 1.9])
    demand_per_year = 40 * 12 * 1000 / 8760
    scen.add_par(
        "demand",
        make_df(
            "demand",
            **common,
            commodity="light",
            level="useful",
            value=(100 * gdp_profile).round(),
            unit="GWa",
        ),
    )

    grid_efficiency = 0.9
    common.update(unit="-")

    for par, t, c, l, value in [
        ("input", "bulb", "electricity", "final", 1.0),
        ("output", "bulb", "light", "useful", 1.0),
        ("input", "grid", "electricity", "secondary", 1.0),
        ("output", "grid", "electricity", "final", grid_efficiency),
        ("output", "coal_ppl", "electricity", "secondary", 1.0),
        ("output", "wind_ppl", "electricity", "secondary", 1.0),
    ]:
        scen.add_par(
            par, make_df(par, **common, technology=t, commodity=c, level=l, value=value)
        )

    capacity_factor = {t: 1.0 for t in ("coal_ppl", "wind_ppl", "bulb")}
    for tec, val in capacity_factor.items():
        scen.add_par(
            "capacity_factor",
            make_df("capacity_factor", **common, technology=tec, value=val),
        )

    common.update(year_vtg=model_horizon, unit="y")
    for tec, val in dict(coal_ppl=20, wind_ppl=20, bulb=1).items():
        scen.add_par(
            "technical_lifetime",
            make_df("technical_lifetime", **common, technology=tec, value=val),
        )

    common.update(year_act=model_horizon, unit="-")
    for tec in "coal_ppl", "wind_ppl":
        scen.add_par(
            "growth_activity_up",
            make_df("growth_activity_up", **common, technology=tec, value=0.1),
        )

    historic_demand = 0.85 * demand_per_year
    historic_generation = historic_demand / grid_efficiency
    coal_fraction = 0.6

    common.update(year_act=history, year_vtg=history, unit="GWa")
    for tec, val in dict(
        coal_ppl=coal_fraction * historic_generation,
        wind_ppl=(1 - coal_fraction) * historic_generation,
    ).items():
        scen.add_par(
            "historical_activity",
            make_df("historical_activity", **common, technology=tec, value=val),
        )
        # 20 year lifetime
        val *= 1 / 10 / capacity_factor[t] / 2
        scen.add_par(
            "historical_new_capacity",
            make_df("historical_new_capacity", **common, technology=t, value=val),
        )

    scen.add_par(
        "interestrate",
        make_df("interestrate", year=model_horizon, value=0.05, unit="-"),
    )

    common.update(year_vtg=model_horizon, year_act=model_horizon)
    del common["unit"]

    for t, par, value in [
        ("coal_ppl", "inv_cost", 500),
        ("wind_ppl", "inv_cost", 1500),
        ("bulb", "inv_cost", 5),
        ("coal_ppl", "fix_cost", 30),
        ("wind_ppl", "fix_cost", 10),
        ("coal_ppl", "var_cost", 30),
        ("grid", "var_cost", 50),
    ]:
        scen.add_par(
            par,
            make_df(
                par,
                **common,
                technology=tec,
                value=value,
                unit="USD/kW" if par == "inv_cost" else "USD/kWa",
            ),
        )

    scen.commit("basic model of Westerosi electrification")
    scen.set_as_default()

    if emissions:
        scen.check_out()

        # Introduce the emission species CO2 and the emission category GHG
        scen.add_set("emission", "CO2")
        scen.add_cat("emission", "GHG", "CO2")

        # we now add CO2 emissions to the coal powerplant
        scen.add_par(
            "emission_factor",
            make_df(
                "emission_factor",
                **common,
                technology="coal_ppl",
                emission="CO2",
                value=100.0,
                unit="tCO2/kWa",
            ),
        )

        scen.commit("Added emissions sets/params to Westeros model.")

    if solve:
        scen.solve()

    return scen
