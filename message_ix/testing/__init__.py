import io
import os
from collections.abc import Callable, Generator
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import ixmp
import numpy as np
import pandas as pd
import pytest
from click.testing import CliRunner, Result
from ixmp import IAMC_IDX

from message_ix import Scenario, cli, make_df
from message_ix.report import Reporter

if TYPE_CHECKING:
    from ixmp import Platform
    from pint import UnitRegistry


GHA = "GITHUB_ACTIONS" in os.environ

# Pytest hooks


def pytest_report_header(config: pytest.Config, start_path: Path) -> str:
    """Add the message_ix import path to the pytest report header."""
    import message_ix

    return f"message_ix location: {Path(message_ix.__file__).parent}"


def pytest_sessionstart() -> None:
    """Use only 2 threads for CPLEX on GitHub Actions runners with 2 CPU cores."""
    import message_ix.models

    if "GITHUB_ACTIONS" in os.environ:
        message_ix.models.DEFAULT_CPLEX_OPTIONS["threads"] = 2


# Data for testing

SCENARIO = {
    "austria": dict(
        model="Austrian energy model", scenario="baseline", scheme="MESSAGE"
    ),
    "dantzig": {
        "model": "Canning problem (MESSAGE scheme)",
        "scenario": "standard",
        "scheme": "MESSAGE",
    },
    "dantzig multi-year": {
        "model": "Canning problem (MESSAGE scheme)",
        "scenario": "multi-year",
        "scheme": "MESSAGE",
    },
    "westeros": {
        "model": "Westeros Electrified",
        "scenario": "baseline",
        "scheme": "MESSAGE",
    },
}

#: Model names, scenario names, and file hashes for 'snapshots' of scenarios used in
#: :mod:`.tests.test_snapshots`. These correspond to files in the Zenodo record at
#: doi:`10.5281/zenodo.15277570 <https://doi.org/10.5281/zenodo.15277570>`_.
SNAPSHOTS = (
    (
        dict(model="CD_Links_SSP2", scenario="baseline"),
        "md5:ff57ee38defe2b983b22f26f696a6746",
    ),
    (
        dict(model="CD_Links_SSP2_v2", scenario="NPi2020_1000-con-prim-dir-ncr"),
        "md5:ae17c294c9479a2af14a9d3157f49257",
    ),
)


# Create and populate ixmp databases

_ms: list[Union[str, float]] = [
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
TS_DF = (
    pd.concat([HIST_DF, INP_DF], sort=False)
    .sort_values(by="variable")
    .reset_index(drop=True)
)

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


# FIXME reduce complexity 19 → ≤13
def make_austria(  # noqa: C901
    mp,
    solve: bool = False,
    quiet: bool = True,
    *,
    request: Optional["pytest.FixtureRequest"] = None,
) -> Scenario:
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

    args = SCENARIO["austria"] | dict(
        version="new",
        annotation="A stylized energy system model for illustration and testing",
    )
    if request:
        args.update(scenario=request.node.name)

    scen = Scenario(mp, **args)

    # Structure

    year: dict[str, Any] = dict(all=list(range(2010, 2041, 10)))
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

    common: dict[str, Any] = dict(
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
    demand_profile = gdp_profile**beta

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

    data = AUSTRIA_PAR.copy()
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
        scen.solve(quiet=quiet, solve_options=dict(iis=1))

    return scen


def make_dantzig(
    mp,
    solve: bool = False,
    multi_year: bool = False,
    *,
    request: Optional["pytest.FixtureRequest"] = None,
    **solve_opts,
) -> Scenario:
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

    # Scenario identifiers
    args = dict(
        model=SCENARIO["dantzig"]["model"],
        version="new",
        annotation="Dantzig's canning problem as a MESSAGE-scheme Scenario",
    )
    if request:
        # Use a distinct scenario name for a particular test
        args.update(scenario=request.node.name)
    else:
        args.update(scenario="multi-year" if multi_year else "standard")

    # Initialize a new (empty) instance of an `ixmp.Scenario`
    scen = Scenario(mp, **args)

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
        solve_opts.setdefault("quiet", True)
        scen.solve(**solve_opts)

    scen.check_out(timeseries_only=True)
    scen.add_timeseries(HIST_DF, meta=True)
    scen.add_timeseries(INP_DF)
    scen.commit("Import Dantzig's transport problem for testing.")

    return scen


def make_westeros(
    mp: "Platform",
    emissions: bool = False,
    solve: bool = False,
    quiet: bool = True,
    model_horizon: list[int] = [700, 710, 720],
    *,
    request: Optional["pytest.FixtureRequest"] = None,
) -> Scenario:
    """Return a new :class:`message_ix.Scenario` containing the ‘Westeros’ model.

    This is the same model used in the :file:`westeros_baseline.ipynb` tutorial. In
    particular:

    - There is always one historical period :py:`year = 690` with
      :py:`duration_period = 10`, and one historical period :py:`year = 680` with a
      duration that is undefined.

    Parameters
    ----------
    mp :
        Platform on which to create the scenario.
    emissions :
        If :any:`True`, the ``emissions_factor`` parameter is also populated for CO2.
    solve :
        If :any:`True`, the scenario is solved.
    quiet :
        Passed to :meth:`Scenario.solve` if :py:`solve is True`.
    model_horizon :
        List of periods within the model horizon. The historical periods
        :py:`year = [680, 690]` are always prepended.

    Other parameters
    ----------------
    request :
        For use with :mod:`pytest`. If given, the returned Scenario has a scenario name
        constructed from the Pytest node name, which should be unique within a test
        session.
    """
    mp.add_unit("USD/kW")
    mp.add_unit("tCO2/kWa")

    # Scenario identifiers
    args = SCENARIO["westeros"] | dict(version="new")
    if request:
        # Use a distinct scenario name for a particular test
        args.update(scenario=request.node.name)

    scen = Scenario(mp, **args)

    # Common keyword arguments to make_df()
    t = "year"
    common: dict[str, Any] = dict(mode="standard", time=t, time_dest=t, time_origin=t)

    # Periods
    assert len(model_horizon) and 690 < min(model_horizon)
    y = [680, 690] + model_horizon
    ym1_index, y0_index = 1, 2
    scen.add_horizon(year=y, firstmodelyear=y[y0_index])
    dp0 = scen.par("duration_period").query("year == 690")["value"].item()
    assert 10.0 == dp0

    # Retrieve valid (yV, yA) combinations
    yv_ya = scen.vintage_and_active_years()
    yV, yA = yv_ya["year_vtg"].tolist(), yv_ya["year_act"].tolist()
    common |= dict(year=y[y0_index:], year_act=yA, year_vtg=yV)

    # Nodes
    n = "Westeros"
    common |= dict(node=n, node_dest=n, node_loc=n, node_origin=n)
    scen.add_spatial_sets({"country": n})

    # Other sets
    for name, values in (
        ("technology", ["coal_ppl", "wind_ppl", "grid", "bulb"]),
        ("mode", ["standard"]),
        ("level", ["secondary", "final", "useful"]),
        ("commodity", ["electricity", "light"]),
    ):
        scen.add_set(name, values)

    # Free parameters
    demand_per_year = 40 * 12 * 1000 / 8760  # Base period demand value
    gdp_index = {680: 0.5, 690: 0.5, 700: 1.0, 710: 1.5, 720: 1.9}
    grid_efficiency = 0.9
    coal_fraction = 0.6

    # Parameter data
    name = "demand"
    kw = common | dict(commodity="light", level="useful", year=y, unit="GWa")
    # - Create a Series from some GDP indices and NaN for other `model_horizon` periods.
    # - Multiply by base-period demand.
    # - Interpolate.
    # - Select only the indices from `model_horizon`.
    demand = (
        pd.Series({y_: None for y_ in y[y0_index:]} | gdp_index)
        .mul(demand_per_year)
        .sort_index()
        .interpolate(method="index")
        .round()
        .loc[y]
    )
    scen.add_par(name, make_df(name, **kw, value=demand.values))

    for name, t, c, L, value in [
        ("input", "bulb", "electricity", "final", 1.0),
        ("output", "bulb", "light", "useful", 1.0),
        ("input", "grid", "electricity", "secondary", 1.0 / grid_efficiency),
        ("output", "grid", "electricity", "final", 1.0),
        ("output", "coal_ppl", "electricity", "secondary", 1.0),
        ("output", "wind_ppl", "electricity", "secondary", 1.0),
    ]:
        kw = common | dict(technology=t, commodity=c, level=L, value=value, unit="-")
        scen.add_par(name, make_df(name, **kw))

    name = "capacity_factor"
    capacity_factor = dict(coal_ppl=1.0, wind_ppl=0.36, bulb=1.0, grid=1.0)
    for t, value in capacity_factor.items():
        kw = common | dict(technology=t, value=value, unit="-")
        scen.add_par(name, make_df(name, **kw))

    name = "technical_lifetime"
    for t, value in dict(coal_ppl=20, wind_ppl=20, bulb=1, grid=30).items():
        kw = common | dict(technology=t, year_vtg=y, value=value, unit="y")
        scen.add_par(name, make_df(name, **kw))

    name = "growth_activity_up"
    for t in "coal_ppl", "wind_ppl":
        kw = common | dict(year_act=y[y0_index:], technology=t, value=0.1, unit="-")
        scen.add_par(name, make_df(name, **kw))

    historic_generation = demand.loc[y[ym1_index]] / grid_efficiency
    for t, value in (
        ("coal_ppl", coal_fraction * historic_generation),
        ("wind_ppl", (1 - coal_fraction) * historic_generation),
        ("grid", historic_generation),
    ):
        kw = common | dict(
            year_vtg=y[ym1_index], year_act=y[ym1_index], technology=t, unit="GWa"
        )
        name = "historical_activity"
        scen.add_par(name, make_df(name, **kw, value=value))
        name = "historical_new_capacity"
        scen.add_par(name, make_df(name, **kw, value=value / capacity_factor[t] / dp0))

    name = "interestrate"
    scen.add_par(name, make_df(name, year=y, value=0.05, unit="-"))

    for name, tec, value in [
        ("inv_cost", "coal_ppl", 500),
        ("inv_cost", "wind_ppl", 1500),
        ("inv_cost", "bulb", 5),
        ("inv_cost", "grid", 800),
        ("fix_cost", "coal_ppl", 30),
        ("fix_cost", "wind_ppl", 10),
        ("fix_cost", "grid", 16),
        ("var_cost", "coal_ppl", 30),
    ]:
        kw = common | (
            dict(year_vtg=y[y0_index:], unit="USD/kW")
            if name == "inv_cost"
            else dict(year_vtg=yV, year_act=yA, unit="USD/kWa")
        )
        scen.add_par(name, make_df(name, **kw, technology=tec, value=value))

    scen.commit("basic model of Westerosi electrification")
    scen.set_as_default()

    if emissions:
        scen.check_out()

        # Introduce the emission species CO2 and the emission category GHG
        e = "CO2"
        scen.add_set("emission", e)
        scen.add_cat("emission", "GHG", e)

        # we now add CO2 emissions to the coal powerplant
        name = "emission_factor"
        kw = common | dict(emission=e, technology="coal_ppl")
        scen.add_par(name, make_df(name, **kw, value=100.0, unit="tCO2/kWa"))

        scen.commit("Added emissions sets/params to Westeros model.")

    if solve:
        scen.solve(quiet=quiet)

    return scen


def make_subannual(
    mp: "Platform",
    tec_dict,
    time_steps,
    demand,
    time_relative=[],
    com_dict={"gas_ppl": {"input": "fuel", "output": "electr"}},
    capacity={"gas_ppl": {"inv_cost": 0.1, "technical_lifetime": 5}},
    capacity_factor={},
    var_cost={},
    operation_factor={},
    *,
    request: Optional["pytest.FixtureRequest"] = None,
) -> Scenario:
    """Return an :class:`message_ix.Scenario` with subannual time resolution.

    The scenario contains a simple model with two technologies, and a number of time
    slices.

    Parameters
    ----------
    request :
        The pytest ``request`` fixture.
    tec_dict : dict
        A dictionary for a technology and required info for time-related parameters.
        (e.g., ``tec_dict = {"gas_ppl": {"time_origin": ["summer"], "time": ["summer"],
        "time_dest": ["summer"]}``)
    time_steps : list of tuples
        Information about each time slice, packed in a tuple with four elements,
        including: time slice name, duration relative to "year", "temporal_lvl",
        and parent time slice (e.g., ``time_steps = [("summer", 1, "season", "year")]``)
    demand : dict
        A dictionary for information of "demand" in each time slice.
        (e.g., 11demand = {"summer": 2.5}``)
    time_relative: list of str, optional
        List of parent "time" slices, for which a relative duration time is maintained.
        This will be used to specify parameter "duration_time_rel" for these "time"s.
    com_dict : dict, optional
        A dictionary for specifying "input" and "output" commodities.
        (e.g., ``com_dict = {"gas_ppl": {"input": "fuel", "output": "electr"}}``)
    capacity : dict, optional
        Data for "inv_cost" and "technical_lifetime" per technology.
    capacity_factor : dict, optional
        "capacity_factor" with technology as key and "time"/"value" pairs as value.
    var_cost : dict, optional
        "var_cost" with technology as key and "time"/"value" pairs as value.
    operation_factor : dict, optional
        "operation_factor" with technology as key and "value" as value.
    """
    # Build an empty scenario
    args = dict(model="Test subannual time steps", scenario="baseline", version="new")
    if request:
        # Use a distinct scenario name for a particular test
        args.update(scenario=request.node.name)

    scen = Scenario(mp, **args)

    # Add required sets
    scen.add_set("node", "node")
    for c in com_dict.values():
        scen.add_set("commodity", [x for x in list(c.values()) if x])

    # Fixed values
    y = 2020
    unit = "GWa"

    scen.add_set("level", "level")
    scen.add_set("year", y)
    scen.add_set("type_year", y)
    scen.add_set("mode", "mode")

    scen.add_set("technology", list(tec_dict.keys()))

    # Add "time" and "duration_time" to the model
    for h, dur, tmp_lvl, parent in time_steps:
        scen.add_set("time", h)
        scen.add_set("time", parent)
        scen.add_set("lvl_temporal", tmp_lvl)
        scen.add_set("map_temporal_hierarchy", [tmp_lvl, h, parent])
        scen.add_par("duration_time", [h], dur, "-")

    scen.add_set("time_relative", time_relative)

    # Common dimensions for parameter data
    common = dict(
        node="node",
        node_loc="node",
        node_rel="node",
        mode="mode",
        level="level",
        year=y,
        year_vtg=y,
        year_act=y,
        year_rel=y,
    )

    # Define demand; unpack (key, value) pairs into individual pd.DataFrame rows
    df = make_df(
        "demand",
        **common,
        commodity="electr",
        time=demand.keys(),
        value=demand.values(),
        unit=unit,
    )
    scen.add_par("demand", df)

    # Add "input" and "output" parameters of technologies
    common.update(value=1.0, unit="-")
    base_output = make_df("output", **common, node_dest="node")
    base_input = make_df("input", **common, node_origin="node")
    for tec, times in tec_dict.items():
        c = com_dict[tec]
        for h1, h2 in zip(times["time"], times.get("time_dest", [])):
            scen.add_par(
                "output",
                base_output.assign(
                    technology=tec, commodity=c["output"], time=h1, time_dest=h2
                ),
            )
        for h1, h2 in zip(times["time"], times.get("time_origin", [])):
            scen.add_par(
                "input",
                base_input.assign(
                    technology=tec, commodity=c["input"], time=h1, time_origin=h2
                ),
            )

    # Add capacity related parameters
    for year, tec in product([y], capacity.keys()):
        for parname, val in capacity[tec].items():
            scen.add_par(parname, ["node", tec, year], val, "-")

    common.pop("value")

    # Add capacity factor and variable cost data, both optional
    for name, arg in [("capacity_factor", capacity_factor), ("var_cost", var_cost)]:
        for tec, data in arg.items():
            df = make_df(
                name, **common, technology=tec, time=data.keys(), value=data.values()
            )
            scen.add_par(name, df)

    # Add operation factor and an arbitrary relation (optional)
    for name, arg in [("operation_factor", operation_factor)]:
        for tec, data in arg.items():
            df = make_df(name, **common, technology=tec, value=data)
            scen.add_par(name, df)
            # Arbitray relation to create "map_tec_relation". This is for testing
            # average capacity factor, used for calculating "operation_factor"
            scen.add_set("relation", "yearly_activity")
            common.update(relation="yearly_activity", technology=tec, value=1)
            scen.add_par("relation_activity", make_df("relation_activity", **common))

    scen.commit("Scenario with subannual time resolution")
    scen.solve()

    return scen


# Fixtures


@pytest.fixture
def dantzig_reporter(
    request: pytest.FixtureRequest, message_test_mp: "Platform", ureg: "UnitRegistry"
) -> Generator[Reporter, Any, None]:
    """A :class:`.Reporter` with a solved :func:`.make_dantzig` scenario."""
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone(
        scenario=request.node.name
    )

    if not scen.has_solution():
        scen.solve(quiet=True)

    rep = Reporter.from_scenario(scen)

    # The Dantzig model has no data in fix_cost, which creates an error adding the
    # derived keys <fom:nl-t-yv-ya> and <vom:nl-t-yv-ya> because the former has no
    # units. Force application of units to this empty quantity.
    rep.configure(units=dict(apply=dict(fix_cost="USD/case")))

    yield rep


@pytest.fixture(scope="session")
def message_ix_cli(
    tmp_env: os._Environ[str],
) -> Generator[Callable[..., Result], Any, None]:
    """A CliRunner object that invokes the message_ix command-line interface.

    :obj:`None` in *args* is automatically discarded.
    """

    class Runner(CliRunner):
        def invoke(self, *args, **kwargs) -> Result:
            return super().invoke(
                cli.main,
                list(filter(None, args)),
                env=tmp_env,
                catch_exceptions=False,
                color=True,
                **kwargs,
            )

    yield Runner().invoke


@pytest.fixture(scope="class")
def message_test_mp(test_mp: "Platform") -> Generator["Platform", Any, None]:
    """A test platform with two versions of the :func:`.make_dantzig` scenario.

    One version has :py:`multi_year=False`, and the other :py:`multi_year=True`.
    """
    make_dantzig(test_mp)
    make_dantzig(test_mp, multi_year=True)
    yield test_mp


@pytest.fixture(scope="session")
def snapshots_from_zenodo(
    pytestconfig: pytest.Config,
) -> "Platform":  # pragma: no cover
    """Platform with Scenarios from :data:`.SNAPSHOTS`.

    This fixture:

    1. Downloads the files from the Zenodo record to the pytest cache directory. If the
       files are already present, this step is not repeated. The file hashes are
       verified.
    2. Creates a :class:`.Platform`, also in the pytest cache directory.
    3. Adds the downloaded scenarios to the platform.
    """
    from pooch import HTTPDownloader, Pooch

    from message_ix.models import MACRO

    # Create a pooch 'registry' from `SCENARIOS`
    assert pytestconfig.cache, "Pytest config does not have `.cache` set!"
    cache_dir = pytestconfig.cache.mkdir("snapshots")
    filename = "{0[model]}_{0[scenario]}_v1.xlsx"
    p = Pooch(
        base_url="https://zenodo.org/api/records/15277571/files/",
        path=cache_dir,
        registry={filename.format(si): h for si, h in SNAPSHOTS},
    )

    def zenodo_token_download(url, output_file, pooch):
        token = os.environ["MESSAGE_IX_ZENODO_TOKEN"]
        HTTPDownloader(params={"token": token})(f"{url}/content", output_file, pooch)

    # Download (if needed) each file and store its full path
    paths = [p.fetch(fn, downloader=zenodo_token_download) for fn in p.registry.keys()]

    # Create a new Platform, also in the pytest cache directory
    mp = ixmp.Platform(backend="jdbc", driver="hsqldb", path=cache_dir.joinpath("db"))

    # Populate `mp` from the data files
    for path, (scenario_info, _) in zip(paths, SNAPSHOTS):
        try:
            # Load an existing scenario
            s = Scenario(mp, **scenario_info)
        except ValueError:
            s = Scenario(mp, **scenario_info, version="new")
            MACRO.initialize(s)
            s.read_excel(path, add_units=True, init_items=True)
        else:
            pass  # Already read from file → do not repeat

    assert len(SNAPSHOTS) == len(mp.scenario_list(default=False))

    return mp


@pytest.fixture(scope="session")
def test_data_path(request: pytest.FixtureRequest) -> Path:
    """Path to the directory containing test data."""
    return Path(__file__).parents[1] / "tests" / "data"


@pytest.fixture(scope="function")
def tmp_model_dir(tmp_path: Path) -> Generator[Path, Any, None]:
    """Temporary directory containing a copy of the MESSAGE model files.

    This may be used, among other purposes, to isolate the writing/reading of
    :file:`cplex.opt` from other tests.

    See also
    --------
    :func:`.copy_model`
    """
    from message_ix.util import copy_model

    copy_model(tmp_path, overwrite=False, set_default=False, quiet=True)

    yield tmp_path


@pytest.fixture(scope="session")
def tutorial_path(request: pytest.FixtureRequest) -> Path:
    """Path to the directory containing the tutorials."""
    return Path(__file__).parents[2] / "tutorial"


@pytest.fixture(scope="session")
def ureg() -> Generator["UnitRegistry", Any, None]:
    """Session-scoped :class:`pint.UnitRegistry` with units needed by tests."""
    import pint

    registry = pint.get_application_registry()

    for unit in "USD", "case":
        try:
            registry.define(f"{unit} = [{unit}]")
        except (pint.RedefinitionError, pint.DefinitionSyntaxError):
            # Already defined
            pass

    yield registry
