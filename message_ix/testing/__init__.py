import io
from itertools import product
from typing import List, Union

import numpy as np
import pandas as pd
from ixmp import IAMC_IDX

from message_ix import Scenario, make_df

SCENARIO = {
    "austria": dict(model="Austrian energy model", scenario="baseline"),
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


def _to_df(columns, table):
    """Return a pd.DataFrame for a fixed-width text `table`."""
    return pd.read_fwf(io.StringIO(table), index_col=0, header=None).set_axis(
        columns.split(), axis=1
    )


AUSTRIA_TECH = _to_df(
    "input_commodity input_level input_value output_commodity output_level "
    "output_value",
    """
bio_ppl                                        electricity        secondary  1.0
coal_ppl                                       electricity        secondary  1.0
gas_ppl                                        electricity        secondary  1.0
hydro_ppl                                      electricity        secondary  1.0
oil_ppl                                        electricity        secondary  1.0
solar_pv_ppl                                   electricity        final      1.0
wind_ppl                                       electricity        secondary  1.0
import                                         electricity        secondary  1.0
electricity_grid  electricity  secondary  1.0  electricity        final      0.873
appliances        electricity  final      1.0  other_electricity  useful     1.0
bulb              electricity  final      1.0  light              useful     1.0
cfl               electricity  final      0.3  light              useful     1.0
""",
)

AUSTRIA_PAR = _to_df(
    "activity capacity_factor technical_lifetime inv_cost fix_cost var_cost "
    "emission_factor",
    """
bio_ppl             4554  0.75  30  1600  30  48.2
coal_ppl            7184  0.85  40  1500  40  24.4  0.854
gas_ppl            14346  0.75  30   870  25  42.4  0.339
hydro_ppl          38406  0.5   60  3000  60
oil_ppl             1275  0.75  30   950  25  77.8  0.5
solar_pv_ppl          89  0.15  20  4000  25
wind_ppl            2064  0.2   20  1100  40
import              2340
electricity_grid                              47.8
appliances
bulb                      0.1    1     5
cfl                  0.0  0.1   10   900
""",
)


def make_austria(mp, solve=False):
    """Return an :class:`message_ix.Scenario` for the Austrian energy system.

    This is the same model used in the ``austria.ipynb`` tutorial.

    Parameters
    ----------
    mp : ixmp.Platform
        Platform on which to create the scenario.
    solve : bool, optional
        If True, the scenario is solved.
    """
    mp.add_unit("USD/kW")
    mp.add_unit("MtCO2")
    mp.add_unit("tCO2/kWa")

    scen = Scenario(
        mp,
        version="new",
        **SCENARIO["austria"],
        annotation="A stylized energy system model for illustration and testing",
    )

    # Structure

    year = dict(all=list(range(2010, 2041, 10)))
    scen.add_horizon(year=year["all"])
    year_df = scen.vintage_and_active_years()
    year["vtg"] = year_df["year_vtg"]
    year["act"] = year_df["year_act"]

    country = "Austria"
    scen.add_spatial_sets({"country": country})

    sets = dict(
        commodity=["electricity", "light", "other_electricity"],
        emission=["CO2"],
        level=["secondary", "final", "useful"],
        mode=["standard"],
    )

    sets["technology"] = AUSTRIA_TECH.index.to_list()
    plants = sets["technology"][:7]
    lights = sets["technology"][10:]

    for name, values in sets.items():
        scen.add_set(name, values)

    scen.add_cat("emission", "GHGs", "CO2")

    # Parameters

    name = "interestrate"
    scen.add_par(name, make_df(name, year=year["all"], value=0.05, unit="-"))

    common = dict(
        mode="standard",
        node_dest=country,
        node_loc=country,
        node_origin=country,
        node=country,
        time_dest="year",
        time_origin="year",
        time="year",
        year_act=year["act"],
        year_vtg=year["vtg"],
        year=year["all"],
    )

    gdp_profile = np.array([1.0, 1.21631, 1.4108, 1.63746])
    beta = 0.7
    demand_profile = gdp_profile ** beta

    # From IEA statistics, in GW·h, converted to GW·a
    base_annual_demand = dict(other_electricity=55209.0 / 8760, light=6134.0 / 8760)

    name = "demand"
    common.update(level="useful", unit="GWa")
    for c, base in base_annual_demand.items():
        scen.add_par(
            name, make_df(name, **common, commodity=c, value=base * demand_profile)
        )
    common.pop("level")

    # input, output
    common.update(unit="-")
    for name, (tec, info) in product(("input", "output"), AUSTRIA_TECH.iterrows()):
        value = info[f"{name}_value"]
        if np.isnan(value):
            continue
        scen.add_par(
            name,
            make_df(
                name,
                **common,
                technology=tec,
                commodity=info[f"{name}_commodity"],
                level=info[f"{name}_level"],
                value=value,
            ),
        )

    data = AUSTRIA_PAR
    # Convert GW·h to GW·a
    data["activity"] = data["activity"] / 8760.0
    # Convert USD / MW·h to USD / GW·a
    data["var_cost"] = data["var_cost"] * 8760.0 / 1e3
    # Convert t / MW·h to t / kw·a
    data["emission_factor"] = data["emission_factor"] * 8760.0 / 1e3

    def _add():
        """Add using values from the calling scope."""
        scen.add_par(name, make_df(name, **common, technology=tec, value=value))

    name = "capacity_factor"
    for tec, value in data[name].dropna().items():
        _add()

    name = "technical_lifetime"
    common.update(year_vtg=year["all"], unit="y")
    for tec, value in data[name].dropna().items():
        _add()

    name = "growth_activity_up"
    common.update(year_act=year["all"][1:], unit="%")
    value = 0.05
    for tec in plants + lights:
        _add()

    name = "initial_activity_up"
    common.update(year_act=year["all"][1:], unit="%")
    value = 0.01 * base_annual_demand["light"] * demand_profile[1:]
    for tec in lights:
        _add()

    # bound_activity_lo, bound_activity_up
    common.update(year_act=year["all"][0], unit="GWa")
    for (tec, value), kind in product(data["activity"].dropna().items(), ("up", "lo")):
        name = f"bound_activity_{kind}"
        _add()

    name = "bound_activity_up"
    common.update(year_act=year["all"][1:])
    for tec in ("bio_ppl", "hydro_ppl", "import"):
        value = data.loc[tec, "activity"]
        _add()

    name = "bound_new_capacity_up"
    common.update(year_vtg=year["all"][0], unit="GW")
    for tec, value in (data["activity"] / data["capacity_factor"]).dropna().items():
        _add()

    name = "inv_cost"
    common.update(dict(year_vtg=year["all"], unit="USD/kW"))
    for tec, value in data[name].dropna().items():
        _add()

    # fix_cost, var_cost
    common.update(dict(year_vtg=year["vtg"], year_act=year["act"], unit="USD/kWa"))
    for name in ("fix_cost", "var_cost"):
        for tec, value in data[name].dropna().items():
            _add()

    name = "emission_factor"
    common.update(
        year_vtg=year["vtg"], year_act=year["act"], unit="tCO2/kWa", emission="CO2"
    )
    for tec, value in data[name].dropna().items():
        _add()

    scen.commit("Initial commit for Austria model")
    scen.set_as_default()

    if solve:
        scen.solve()

    return scen


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

    for name, values in (
        ("technology", ["coal_ppl", "wind_ppl", "grid", "bulb"]),
        ("mode", ["standard"]),
        ("level", ["secondary", "final", "useful"]),
        ("commodity", ["electricity", "light"]),
    ):
        scen.add_set(name, values)

    # Parameters — copy & paste from the tutorial notebook

    common = dict(
        mode="standard",
        node_dest=country,
        node_loc=country,
        node_origin=country,
        node=country,
        time_dest="year",
        time_origin="year",
        time="year",
        year_act=act_years,
        year_vtg=vintage_years,
        year=model_horizon,
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
            # FIXME should use demand_per_year; requires adjustments elsewhere.
            value=(100 * gdp_profile).round(),
            unit="GWa",
        ),
    )

    grid_efficiency = 0.9
    common.update(unit="-")

    for name, tec, c, l, value in [
        ("input", "bulb", "electricity", "final", 1.0),
        ("output", "bulb", "light", "useful", 1.0),
        ("input", "grid", "electricity", "secondary", 1.0),
        ("output", "grid", "electricity", "final", grid_efficiency),
        ("output", "coal_ppl", "electricity", "secondary", 1.0),
        ("output", "wind_ppl", "electricity", "secondary", 1.0),
    ]:
        scen.add_par(
            name,
            make_df(name, **common, technology=tec, commodity=c, level=l, value=value),
        )

    # FIXME the value for wind_ppl should be 0.36; requires adjusting other tests.
    name = "capacity_factor"
    capacity_factor = dict(coal_ppl=1.0, wind_ppl=1.0, bulb=1.0)
    for tec, value in capacity_factor.items():
        scen.add_par(name, make_df(name, **common, technology=tec, value=value))

    name = "technical_lifetime"
    common.update(year_vtg=model_horizon, unit="y")
    for tec, value in dict(coal_ppl=20, wind_ppl=20, bulb=1).items():
        scen.add_par(name, make_df(name, **common, technology=tec, value=value))

    name = "growth_activity_up"
    common.update(year_act=model_horizon, unit="-")
    for tec in "coal_ppl", "wind_ppl":
        scen.add_par(name, make_df(name, **common, technology=tec, value=0.1))

    historic_demand = 0.85 * demand_per_year
    historic_generation = historic_demand / grid_efficiency
    coal_fraction = 0.6

    common.update(year_act=history, year_vtg=history, unit="GWa")
    for tec, value in (
        ("coal_ppl", coal_fraction * historic_generation),
        ("wind_ppl", (1 - coal_fraction) * historic_generation),
    ):
        name = "historical_activity"
        scen.add_par(name, make_df(name, **common, technology=tec, value=value))
        # 20 year lifetime
        name = "historical_new_capacity"
        scen.add_par(
            name,
            make_df(
                name,
                **common,
                technology=tec,
                value=value / (2 * 10 * capacity_factor[tec]),
            ),
        )

    name = "interestrate"
    scen.add_par(name, make_df(name, year=model_horizon, value=0.05, unit="-"))

    for name, tec, value in [
        ("inv_cost", "coal_ppl", 500),
        ("inv_cost", "wind_ppl", 1500),
        ("inv_cost", "bulb", 5),
        ("fix_cost", "coal_ppl", 30),
        ("fix_cost", "wind_ppl", 10),
        ("var_cost", "coal_ppl", 30),
        ("var_cost", "grid", 50),
    ]:
        common.update(
            dict(year_vtg=model_horizon, unit="USD/kW")
            if name == "inv_cost"
            else dict(year_vtg=vintage_years, year_act=act_years, unit="USD/kWa")
        )
        scen.add_par(name, make_df(name, **common, technology=tec, value=value))

    scen.commit("basic model of Westerosi electrification")
    scen.set_as_default()

    if emissions:
        scen.check_out()

        # Introduce the emission species CO2 and the emission category GHG
        scen.add_set("emission", "CO2")
        scen.add_cat("emission", "GHG", "CO2")

        # we now add CO2 emissions to the coal powerplant
        name = "emission_factor"
        common.update(year_vtg=vintage_years, year_act=act_years, unit="tCO2/kWa")
        scen.add_par(
            name,
            make_df(name, **common, technology="coal_ppl", emission="CO2", value=100.0),
        )

        scen.commit("Added emissions sets/params to Westeros model.")

    if solve:
        scen.solve()

    return scen
