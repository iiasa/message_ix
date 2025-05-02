from typing import Optional, Union

import pytest
from ixmp import Platform

from message_ix import ModelError, Scenario


def model_setup(scen: Scenario, var_cost: Optional[int] = 1) -> None:
    scen.add_set("node", "node")
    scen.add_set("commodity", "comm")
    scen.add_set("level", "level")
    scen.add_set("year", 2020)

    scen.add_par("demand", ["node", "comm", "level", 2020, "year"], 1, "GWa")

    scen.add_set("technology", "tec")
    scen.add_set("mode", "mode")
    tec_specs: list[Union[int, str]] = ["node", "tec", 2020, 2020, "mode"]
    output_specs: list[Union[int, str]] = ["node", "comm", "level", "year", "year"]
    scen.add_par("output", tec_specs + output_specs, 1, "GWa")
    scen.add_par("var_cost", tec_specs + ["year"], var_cost, "USD/GWa")


def test_commodity_price(test_mp: Platform) -> None:
    scen = Scenario(test_mp, "test_commodity_price", "standard", version="new")
    model_setup(scen)
    scen.commit("initialize test model")
    scen.solve(case="price_commodity_standard", quiet=True)

    assert scen.var("OBJ")["lvl"] == 1
    assert scen.var("PRICE_COMMODITY")["lvl"][0] == 1


def test_commodity_price_equality(test_mp: Platform) -> None:
    scen = Scenario(test_mp, "test_commodity_price", "equality", version="new")
    model_setup(scen, var_cost=-1)
    scen.commit("initialize test model with negative variable costs")

    # negative variable costs and supply >= demand causes an unbounded ray
    with pytest.raises(ModelError, match="GAMS errored with return code 3"):
        scen.solve(quiet=True)

    # use the commodity-balance equality feature
    scen.check_out()
    scen.add_set("balance_equality", ["comm", "level"])
    scen.commit("set commodity-balance for `[comm, level]` as equality")
    scen.solve(case="price_commodity_equality", quiet=True)

    assert scen.var("OBJ")["lvl"] == -1
    assert scen.var("PRICE_COMMODITY")["lvl"][0] == -1
