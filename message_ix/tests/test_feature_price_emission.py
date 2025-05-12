from typing import Union

import numpy.testing as npt
import pytest
from ixmp import Platform

from message_ix import Scenario, make_df

MODEL = "test_emissions_price"

solve_args = {"equ_list": ["EMISSION_EQUIVALENCE"]}


def model_setup(scen: Scenario, years: list[int], simple_tecs: bool = True) -> None:
    """generate a minimal model to test the behaviour of the emission prices"""
    scen.add_spatial_sets({"country": "node"})
    scen.add_set("commodity", "comm")
    scen.add_set("level", "level")
    scen.add_set("year", years)

    scen.add_set("mode", "mode")

    scen.add_set("emission", "CO2")
    scen.add_cat("emission", "GHG", "CO2")

    for y in years:
        scen.add_par("interestrate", y, 0.05, "-")
        scen.add_par("demand", ["node", "comm", "level", y, "year"], 1, "GWa")

    if simple_tecs:
        add_two_tecs(scen, years)
    else:
        add_many_tecs(scen, years)


def add_two_tecs(scen: Scenario, years: list[int]) -> None:
    """add two technologies to the scenario"""
    scen.add_set("technology", ["dirty_tec", "clean_tec"])

    common = dict(node_loc="node", year_vtg=years, year_act=years, value=1, mode="mode")

    # the dirty technology is free (no costs) but has emissions
    scen.add_par(
        "output",
        make_df(
            "output",
            node_dest="node",
            technology="dirty_tec",
            commodity="comm",
            level="level",
            time="year",
            time_dest="year",
            unit="GWa",
            **common,
        ),
    )
    scen.add_par(
        "emission_factor",
        make_df(
            "emission_factor",
            unit="tCO2",
            technology="dirty_tec",
            emission="CO2",
            **common,
        ),
    )

    # the clean technology has variable costs but no emissions
    scen.add_par(
        "output",
        make_df(
            "output",
            node_dest="node",
            technology="clean_tec",
            commodity="comm",
            level="level",
            time="year",
            time_dest="year",
            unit="GWa",
            **common,
        ),
    )
    scen.add_par(
        "var_cost",
        make_df(
            "var_cost",
            time="year",
            unit="USD/GWa",
            technology="clean_tec",
            **common,
        ),
    )


def add_many_tecs(scen: Scenario, years: list[int], n: int = 50) -> None:
    """add a range of dirty-to-clean technologies to the scenario"""
    output_specs: list[Union[int, str]] = ["node", "comm", "level", "year", "year"]

    for i in range(n + 1):
        t = "tec{}".format(i)
        scen.add_set("technology", t)
        for y in years:
            tec_specs: list[Union[int, str]] = ["node", t, y, y, "mode"]
            # variable costs grow quadratically over technologies
            # to get rid of the curse of linearity
            c = (10 * i / n) ** 2 * (1.045) ** (y - years[0])
            e = 1 - i / n
            scen.add_par("output", tec_specs + output_specs, 1, "GWa")
            scen.add_par("var_cost", tec_specs + ["year"], c, "USD/GWa")
            scen.add_par("emission_factor", tec_specs + ["CO2"], e, "tCO2")


def test_no_constraint(test_mp: Platform, request: pytest.FixtureRequest) -> None:
    scen = Scenario(test_mp, MODEL, scenario=request.node.name, version="new")
    model_setup(scen, [2020, 2030])
    scen.commit("initialize test scenario")
    scen.solve(quiet=True)

    # without emissions constraint, the zero-cost technology satisfies demand
    assert scen.var("OBJ")["lvl"] == 0
    # without emissions constraint, there are no emission prices
    assert scen.var("PRICE_EMISSION").empty


def test_cumulative_equidistant(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
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
    npt.assert_allclose(obs, [1.05 ** (y - years[0]) for y in years])


def test_per_period_equidistant(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
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


def test_cumulative_variable_periodlength(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
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
    # npt.assert_allclose(obs, [1.05 ** (y - years[0]) for y in years])

    # Retrieve `EMISSION_EQUIVALENCE` and divide by `df_period`
    emi_equ = scen.equ("EMISSION_EQUIVALENCE", {"node": "World"}).mrg.tolist()
    # Excluded until parameter can be loaded directly from scenario-object.
    # df_period = scen.par("df_period").value.tolist()
    df_period = [5.52563125, 4.329476671, 3.392258259, 4.740475413]
    exp = [i / j for i, j in zip(emi_equ, df_period)]

    npt.assert_allclose(obs, exp)


def test_per_period_variable_periodlength(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
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


def test_custom_type_variable_periodlength(
    test_mp: Platform, request: pytest.FixtureRequest
) -> None:
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
    # npt.assert_allclose(obs, [1.05 ** (y - custom[0]) for y in custom])

    # Retrieve `EMISSION_EQUIVALENCE` and divide by `df_period`
    emi_equ = scen.equ(
        "EMISSION_EQUIVALENCE", {"node": "World", "year": custom}
    ).mrg.tolist()
    # Excluded until parameter can be loaded directly from scenario-object.
    # df_period = scen.par("df_period").value.tolist()
    df_period = [4.329476671, 3.392258259, 4.740475413]
    exp = [i / j for i, j in zip(emi_equ, df_period)]

    npt.assert_allclose(obs, exp)


def test_price_duality(test_mp: Platform, request: pytest.FixtureRequest) -> None:
    years = [2020, 2025, 2030, 2040, 2050]
    for c in [0.25, 0.5, 0.75]:
        # set up a scenario for cumulative constraints
        scen = Scenario(
            test_mp,
            MODEL,
            scenario=request.node.name + "_cum_many_tecs",
            version="new",
        )
        model_setup(scen, years, simple_tecs=False)
        scen.add_cat("year", "cumulative", years)
        scen.add_par(
            "bound_emission", ["World", "GHG", "all", "cumulative"], 0.5, "tCO2"
        )
        scen.commit("initialize test scenario")
        scen.solve(quiet=True)

        # set up a new scenario with emissions taxes
        tax_scen = Scenario(
            test_mp,
            MODEL,
            scenario=request.node.name + "_tax_many_tecs",
            version="new",
        )
        model_setup(tax_scen, years, simple_tecs=False)
        for y in years:
            tax_scen.add_cat("year", y, y)

        # use emission prices from cumulative-constraint scenario as taxes
        taxes = scen.var("PRICE_EMISSION").rename(
            columns={"year": "type_year", "lvl": "value"}
        )
        taxes["unit"] = "USD/tCO2"
        tax_scen.add_par("tax_emission", taxes)
        tax_scen.commit("initialize test scenario for taxes")
        tax_scen.solve(quiet=True)

        # check that emissions are close between cumulative and tax scenario
        filters = {"node": "World"}
        emiss = scen.var("EMISS", filters).set_index("year").lvl
        emiss_tax = tax_scen.var("EMISS", filters).set_index("year").lvl
        npt.assert_allclose(emiss, emiss_tax, rtol=0.20)
