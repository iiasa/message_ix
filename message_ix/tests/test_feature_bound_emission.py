from typing import Union

from ixmp import Platform

from message_ix import Scenario


def model_setup(scen: Scenario, years: list[int]) -> None:
    scen.add_set("node", "node")
    scen.add_set("lvl_spatial", "country")
    scen.add_set("map_spatial_hierarchy", ["country", "node", "World"])
    scen.add_set("commodity", "comm")
    scen.add_set("emission", "emiss")
    scen.add_cat("emission", "emiss_type", "emiss")
    scen.add_set("level", "level")
    scen.add_set("year", years)
    scen.add_set("type_year", years)

    scen.add_set("technology", ["tec1", "tec2"])
    scen.add_set("mode", "mode")
    output_specs: list[Union[int, str]] = ["node", "comm", "level", "year", "year"]
    dict_var_cost = {"tec1": 1, "tec2": 2}
    dict_em_factor = {"tec1": 1.5, "tec2": 1}

    for yr in years:
        scen.add_par("demand", ["node", "comm", "level", yr, "year"], 1, "GWa")
        for t in dict_var_cost.keys():
            tec_specs: list[Union[int, str]] = ["node", t, yr, yr, "mode"]
            scen.add_par("output", tec_specs + output_specs, 1, "GWa")
            scen.add_par("var_cost", tec_specs + ["year"], dict_var_cost[t], "USD/GWa")
            scen.add_par(
                "emission_factor", tec_specs + ["emiss"], dict_em_factor[t], "kg/kWa"
            )


def add_bound_emission(
    scen: Scenario, bound: float, year: Union[int, str] = "cumulative"
) -> None:
    scen.check_out()
    scen.add_par("bound_emission", ["node", "emiss_type", "all", year], bound, "kg")
    scen.commit("Emission bound added")


def assert_function(scen: Scenario, year: Union[int, str]) -> None:
    var_em = scen.var("EMISS", {"node": "node"}).set_index(["year"])["lvl"]
    bound_em = scen.par("bound_emission", {"type_year": year}).at[0, "value"]

    if year == "cumulative":
        duration = scen.par("duration_period").set_index("year")["value"]
        assert sum(var_em * duration) / sum(duration) <= bound_em
    else:
        assert var_em[year] <= bound_em


# Testing emission bound per one year
def test_bound_emission_year(test_mp: Platform) -> None:
    scen = Scenario(test_mp, "test_bound_emission", "standard", version="new")
    model_setup(scen, [2020, 2030])
    scen.commit("initialize test model")
    add_bound_emission(scen, bound=1.250, year=2020)
    scen.solve(case="bound_emission_year", quiet=True)
    assert_function(scen, year=2020)


# Testing cumulative emission bound for model years with equal intervals
def test_bound_emission_10y(test_mp: Platform) -> None:
    scen = Scenario(test_mp, "test_bound_emission", "standard", version="new")
    model_setup(scen, [2020, 2030, 2040, 2050])
    scen.commit("initialize test model")
    add_bound_emission(scen, bound=1.250)
    scen.solve(case="bound_emission_10y", quiet=True)
    assert_function(scen, year="cumulative")


# Testing cumulative emission bound for model years with mixed intervals
def test_bound_emission_5y(test_mp: Platform) -> None:
    scen = Scenario(test_mp, "test_bound_emission", "standard", version="new")
    model_setup(scen, [2020, 2025, 2030, 2040])
    scen.commit("initialize test model")
    add_bound_emission(scen, bound=1.250)
    scen.solve(case="bound_emission_5y", quiet=True)
    assert_function(scen, year="cumulative")
