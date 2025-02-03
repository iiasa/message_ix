from typing import List

import numpy.testing as npt
import pytest

# from message_ix.testing import make_westeros
from message_ix import Scenario, make_df

MODEL = "test_emissions_price"

solve_args = {
    "equ_list": ["EMISSION_EQUIVALENCE"],
    # "par_list": ["df_period", "df_year", "levelized_cost"],
    # At the moment, it is not possible to retrieve auxilliary parameters that
    # are created in GAMS back to ixmp. The default "par_list" is coded in Java
    # backened, and specifying a list here does not add/modify the default list.
}

interest_rate = 0.05


def model_setup(scen: Scenario, years: List[int], simple_tecs=True) -> None:
    """generate a minimal model to test the behaviour of the emission prices"""
    scen.add_spatial_sets({"country": "node"})
    scen.add_set("commodity", "comm")
    scen.add_set("level", "level")
    scen.add_horizon(years)
    scen.add_set("mode", "mode")
    scen.add_set("emission", "CO2")
    scen.add_cat("emission", "GHG", "CO2")

    for y in years:
        scen.add_par("interestrate", y, interest_rate, "-")
        scen.add_par(
            "demand",
            make_df(
                "demand",
                node="node",
                commodity="comm",
                level="level",
                time="year",
                year=y,
                value=60 + 2 * (y - years[0]),
                unit="GWa",
            ),
        )

    add_two_tecs(scen, years) if simple_tecs else add_many_tecs(scen, years)


def add_two_tecs(scen: Scenario, years: List[int]) -> None:
    """add two technologies to the scenario"""
    scen.add_set("technology", ["dirty_tec", "clean_tec"])

    common_base = dict(
        node_loc="node", year_vtg=years, year_act=years, mode="mode", value=1
    )
    common_output = dict(
        node_dest="node",
        commodity="comm",
        level="level",
        time="year",
        time_dest="year",
        unit="GWa",
    )

    # the dirty technology is free (no costs) but has emissions
    scen.add_par(
        "output",
        make_df("output", technology="dirty_tec", **common_base, **common_output),
    )
    scen.add_par(
        "emission_factor",
        make_df(
            "emission_factor",
            technology="dirty_tec",
            emission="CO2",
            unit="tCO2",
            **common_base,
        ),
    )

    # the clean technology has variable costs but no emissions
    scen.add_par(
        "output",
        make_df("output", technology="clean_tec", **common_base, **common_output),
    )
    scen.add_par(
        "var_cost",
        make_df(
            "var_cost",
            technology="clean_tec",
            time="year",
            unit="USD/GWa",
            **common_base,
        ),
    )


def add_many_tecs(scen: Scenario, years: List[int], n=50) -> None:
    """add a range of dirty-to-clean technologies to the scenario"""
    # Add some hardcoded tecs for temporary testing
    tecs: dict[str, dict] = {
        "tec1": {
            "emission_factor": 7.4,
            "inv_cost": 500,
            "fix_cost": 30,
            "var_cost": 30,
            "bound_activity_up": 100,
            "lifetime": 20,
        },
        "tec2": {
            "emission_factor": 0,
            "inv_cost": 1500,
            "fix_cost": 10,
            "var_cost": 0,
            "bound_activity_up": 100,
            "lifetime": 20,
        },
        "tec3": {
            "emission_factor": 2.5,
            "inv_cost": 700,
            "fix_cost": 30,
            "var_cost": 30,
            "bound_activity_up": 1000,
            "lifetime": 20,
        },
        "tec4": {
            "emission_factor": 0,
            "inv_cost": 2000,
            "fix_cost": 5,
            "var_cost": 0,
            "bound_activity_up": 10,
            "lifetime": 40,
        },
        "tec5": {
            "emission_factor": 10,
            "inv_cost": 400,
            "fix_cost": 30,
            "var_cost": 30,
            "bound_activity_up": 100,
            "lifetime": 20,
        },
    }
    year_df = scen.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
    mp = scen.platform
    mp.add_unit("USD/kW")
    mp.add_unit("tCO2/kWa")

    for t in tecs:
        scen.add_set("technology", t)
        scen.add_par(
            "output",
            make_df(
                "output",
                node_loc="node",
                node_dest="node",
                technology=t,
                year_vtg=vintage_years,
                year_act=act_years,
                mode="mode",
                commodity="comm",
                level="level",
                time="year",
                time_dest="year",
                value=1,
                unit="GWa",
            ),
        )
        scen.add_par(
            "technical_lifetime",
            make_df(
                "technical_lifetime",
                node_loc="node",
                year_vtg=vintage_years,
                unit="y",
                technology=t,
                value=tecs[t]["lifetime"],
            ),
        )
        scen.add_par(
            "var_cost",
            make_df(
                "var_cost",
                node_loc="node",
                year_vtg=vintage_years,
                year_act=act_years,
                mode="mode",
                time="year",
                unit="USD/kWa",
                technology=t,
                value=tecs[t]["var_cost"],
            ),
        )
        scen.add_par(
            "inv_cost",
            make_df(
                "inv_cost",
                node_loc="node",
                year_vtg=vintage_years,
                unit="USD/kW",
                technology=t,
                value=tecs[t]["inv_cost"],
            ),
        )
        scen.add_par(
            "fix_cost",
            make_df(
                "fix_cost",
                node_loc="node",
                year_vtg=vintage_years,
                year_act=act_years,
                unit="USD/kWa",
                technology=t,
                value=tecs[t]["fix_cost"],
            ),
        )
        scen.add_par(
            "emission_factor",
            make_df(
                "emission_factor",
                node_loc="node",
                year_vtg=vintage_years,
                year_act=act_years,
                unit="tCO2/kWa",
                technology=t,
                mode="mode",
                value=tecs[t]["emission_factor"],
                emission="CO2",
            ),
        )
        scen.add_par(
            "bound_activity_up",
            make_df(
                "bound_activity_up",
                node_loc="node",
                technology=t,
                year_act=act_years,
                mode="mode",
                time="year",
                value=tecs[t]["bound_activity_up"],
                unit="GWa",
            ),
        )


def test_no_constraint(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    model_setup(scen, [2020, 2030])
    scen.commit("initialize test scenario")
    scen.solve(quiet=True)

    # without emissions constraint, the zero-cost technology satisfies demand
    assert scen.var("OBJ")["lvl"] == 0
    # without emissions constraint, there are no emission prices
    assert scen.var("PRICE_EMISSION").empty


def test_cumulative_equidistant(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    years = [2020, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat("year", "cumulative", years)
    scen.add_par("bound_emission", ["World", "GHG", "all", "cumulative"], 0, "tCO2")
    scen.commit("initialize test scenario")
    scen.solve(quiet=True)

    # with emissions constraint, the technology with costs satisfies demand
    assert scen.var("OBJ")["lvl"] > 0
    # under a cumulative constraint, the price must increase with the discount
    # rate starting from the marginal relaxation in the first year
    obs = scen.var("PRICE_EMISSION")["lvl"].values
    npt.assert_allclose(obs, [(1 + interest_rate) ** (y - years[0]) for y in years])


def test_per_period_equidistant(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    years = [2020, 2030, 2040]

    model_setup(scen, years)
    for y in years:
        scen.add_cat("year", y, y)
        scen.add_par("bound_emission", ["World", "GHG", "all", y], 0, "tCO2")
    scen.commit("initialize test scenario")
    scen.solve(quiet=True)

    # with emissions constraint, the technology with costs satisfies demand
    assert scen.var("OBJ")["lvl"] > 0
    # under per-year emissions constraints, the emission price must be equal to
    # the marginal relaxation, ie. the difference in costs between technologies
    npt.assert_allclose(scen.var("PRICE_EMISSION")["lvl"], [1] * 3)


def test_cumulative_variable_periodlength(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    years = [2020, 2025, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat("year", "cumulative", years)
    scen.add_par("bound_emission", ["World", "GHG", "all", "cumulative"], 0, "tCO2")
    scen.commit("initialize test scenario")
    scen.solve(quiet=True, **solve_args)

    # with an emissions constraint, the technology with costs satisfies demand
    assert scen.var("OBJ")["lvl"] > 0
    # under a cumulative constraint, the price must increase with the discount
    # rate starting from the marginal relaxation in the first year
    obs = scen.var("PRICE_EMISSION")["lvl"].values

    # Retrieve `EMISSION_EQUIVALENCE` and divide by `df_period`
    emi_equ = scen.equ("EMISSION_EQUIVALENCE", {"node": "World"}).mrg.tolist()
    # Excluded until parameter can be loaded directly from scenario-object.
    # df_period = scen.par("df_period").value.tolist()
    df_period = [5.52563125, 4.329476671, 3.392258259, 4.740475413]
    exp = [i / j for i, j in zip(emi_equ, df_period)]

    npt.assert_allclose(obs, exp)


def test_per_period_variable_periodlength(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    years = [2020, 2025, 2030, 2040]

    model_setup(scen, years)
    for y in years:
        scen.add_cat("year", y, y)
        scen.add_par("bound_emission", ["World", "GHG", "all", y], 0, "tCO2")
    scen.commit("initialize test scenario")
    scen.solve(quiet=True)

    # with an emissions constraint, the technology with costs satisfies demand
    assert scen.var("OBJ")["lvl"] > 0
    # under per-year emissions constraints, the emission price must be equal to
    # the marginal relaxation, ie. the difference in costs between technologies
    npt.assert_allclose(scen.var("PRICE_EMISSION")["lvl"].values, [1] * 4)


def test_custom_type_variable_periodlength(test_mp, request):
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    years = [2020, 2025, 2030, 2040, 2050]
    custom = [2025, 2030, 2040]

    model_setup(scen, years)
    scen.add_cat("year", "custom", custom)
    scen.add_par("bound_emission", ["World", "GHG", "all", "custom"], 0, "tCO2")

    scen.commit("initialize test scenario")
    scen.solve(quiet=True, **solve_args)

    # with an emissions constraint, the technology with costs satisfies demand
    assert scen.var("OBJ")["lvl"] > 0
    # under a cumulative constraint, the price must increase with the discount
    # rate starting from the marginal relaxation in the first year
    obs = scen.var("PRICE_EMISSION")["lvl"].values

    # Retrieve `EMISSION_EQUIVALENCE` and divide by `df_period`
    emi_equ = scen.equ(
        "EMISSION_EQUIVALENCE", {"node": "World", "year": custom}
    ).mrg.tolist()
    # Excluded until parameter can be loaded directly from scenario-object.
    # df_period = scen.par("df_period").value.tolist()
    df_period = [4.329476671, 3.392258259, 4.740475413]
    exp = [i / j for i, j in zip(emi_equ, df_period)]

    npt.assert_allclose(obs, exp)


# TODO as per Oliver's description:
# - Only need cumulative (no need to parametrize)
@pytest.mark.parametrize(
    "bound, years",
    [
        (10, [2010, 2020, 2025, 2030, 2035, 2040, 2050]),
        (10, [2010, 2015, 2020, 2030, 2040, 2045, 2050]),
        (40, [2010, 2020, 2025, 2030, 2035, 2040, 2050]),
        (40, [2010, 2015, 2020, 2030, 2040, 2045, 2050]),
        (75, [2010, 2020, 2025, 2030, 2035, 2040, 2050]),
        (75, [2010, 2015, 2020, 2030, 2040, 2045, 2050]),
    ],
)
def test_price_duality(test_mp, request, bound, years):
    # set up a scenario for cumulative constraints
    scen = Scenario(
        test_mp,
        MODEL,
        scenario=f"{request.node.name}_cum_many_tecs",
        version="new",
    )
    model_setup(scen, years, simple_tecs=False)
    bound_emission_base = dict(
        node="World", type_emission="GHG", type_tec="all", value=bound, unit="tCO2"
    )
    # We use a `cumulative` base
    scen.add_cat("year", "cumulative", years)
    scen.add_par(
        "bound_emission",
        make_df(
            "bound_emission",
            type_year="cumulative",
            **bound_emission_base,
        ),
    )
    scen.commit("initialize test scenario")
    scen.solve(quiet=True, **solve_args)

    # ----------------------------------------------------------
    # Run scenario with `tax_emission` based on `PRICE_EMISSION`
    # from cumulative constraint scenario.
    # ----------------------------------------------------------
    scen_tax = Scenario(
        test_mp,
        MODEL,
        scenario=f"{request.node.name}_tax_many_tecs",
        version="new",
    )
    model_setup(scen_tax, years, simple_tecs=False)
    # TODO Why do we do this? We applied the bound as cumulative before, but the tax
    # should be per-period?
    for year in years:
        scen_tax.add_cat("year", year, year)

    # use emission prices from cumulative-constraint scenario as taxes
    taxes = scen.var("PRICE_EMISSION").rename(
        columns={"year": "type_year", "lvl": "value"}
    )
    taxes["unit"] = "USD/tCO2"
    # TODO Check: bound is on "World", taxes are on "node"
    taxes["node"] = "node"
    scen_tax.add_par("tax_emission", taxes)
    scen_tax.commit("initialize test scenario for taxes")
    scen_tax.solve(quiet=True, **solve_args)
    # scen_tax.solve(**solve_args)

    print(scen.var("PRICE_EMISSION"))
    print(scen_tax.var("PRICE_EMISSION"))
    print(scen_tax.par("tax_emission"))
    print(scen.var("EMISS"))
    print(scen_tax.var("EMISS"))

    # check emissions are close between cumulative and tax scenarios
    filters = {"node": "World"}
    emiss = scen.var("EMISS", filters).set_index("year").lvl
    emiss_tax = scen_tax.var("EMISS", filters).set_index("year").lvl
    npt.assert_allclose(emiss, emiss_tax, rtol=0.05)

    # check "PRICE_EMISSION" is close between cumulative and tax scenarios
    filters = {"node": "World"}
    price_emission = scen.var("PRICE_EMISSION", filters).set_index("year").lvl
    price_emission_tax = scen_tax.var("PRICE_EMISSION", filters).set_index("year").lvl
    npt.assert_allclose(price_emission, price_emission_tax)

    # check "tax_emission" and "PRICE_EMISSION" are equal in tax-scenario
    filters = {"node": "World"}
    tax_emission = scen_tax.par("tax_emission", filters).set_index("type_year").value
    price_emission_tax = scen_tax.var("PRICE_EMISSION", filters).set_index("year").lvl
    npt.assert_allclose(tax_emission, price_emission_tax)

    # --------------------------------------------------------
    # Run scenario with annual-emission bound based on `EMISS`
    # from cumulative constraint scenario.
    # --------------------------------------------------------

    scenario_period_bound = Scenario(
        test_mp,
        MODEL,
        f"{request.node.name}_period_bound_many_tecs",
        version="new",
    )
    model_setup(scenario_period_bound, years, simple_tecs=False)
    for year in years:
        scenario_period_bound.add_cat("year", year, year)

    # use emissions from cumulative-constraint scenario as period-emission bounds
    emiss_period_bound = (
        scen.var("EMISS", {"node": "World"})
        .rename(columns={"year": "type_year", "lvl": "value"})
        .drop("emission", axis=1)
    )
    emiss_period_bound["type_emission"] = "GHG"
    emiss_period_bound["unit"] = "tCO2"
    # TODO: see above, _per_period_: bound_emission added for every single year. Does
    # it work like this (for all at once), too?
    scenario_period_bound.add_par("bound_emission", emiss_period_bound)
    scenario_period_bound.commit("initialize test scenario for periodic emission bound")
    scenario_period_bound.solve(quiet=True, **solve_args)

    # check -emissions are close between cumulative and yearly-bound scenarios
    emiss_period_bound = (
        scenario_period_bound.var("EMISS", filters).set_index("year").lvl
    )
    npt.assert_allclose(emiss, emiss_period_bound)

    # check "PRICE_EMISSION" is close between cumulative- and yearly-bound scenarios
    price_emission_period_bound = (
        scenario_period_bound.var("PRICE_EMISSION", filters).set_index("year").lvl
    )
    npt.assert_allclose(price_emission, price_emission_period_bound)
