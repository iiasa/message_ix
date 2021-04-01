import numpy.testing as npt
import pandas as pd
import numpy as np
import pandas.testing as pdt
import pytest

from message_ix import Scenario, make_df
from message_ix.testing import make_dantzig, make_westeros


def test_new_params_defined(test_mp):
    # Check whether the new material-related message_ix Parameters are initiated
    # and have the correct shapes
    result = make_df("input_cap")
    assert result.shape == (1, 10)

    result = make_df("input_cap_new")
    assert result.shape == (1, 9)

    result = make_df("input_cap_ret")
    assert result.shape == (1, 9)

    result = make_df("output_cap")
    assert result.shape == (1, 10)

    result = make_df("output_cap_new")
    assert result.shape == (1, 9)

    result = make_df("output_cap_ret")
    assert result.shape == (1, 9)

    # Check correct behaviour when adding key-worded args:
    defaults = dict(
        node_loc="World",
        node_dest="World",
        technology="coal_ppl",
        node_origin="World",
        commodity="coal",
        level="end_of_life",
        year_vtg=2020,
        time="year",
        time_origin="year",
        time_dest="year",
        value=1,
        unit="t",
    )

    result_i = make_df("input_cap_ret", **defaults)
    pdt.assert_series_equal(result_i["commodity"], pd.Series("coal", name="commodity"))
    pdt.assert_series_equal(result_i["year_vtg"], pd.Series(2020, name="year_vtg"))

    result_o = make_df("output_cap_ret", **defaults)
    pdt.assert_series_equal(result_o["commodity"], pd.Series("coal", name="commodity"))
    pdt.assert_series_equal(result_o["year_vtg"], pd.Series(2020, name="year_vtg"))


def test_new_params_working(test_mp):
    """Check the model creation functions in message_ix.testing."""

    scen = make_westeros(test_mp, solve=False)

    # Fake conversion of electricity into steel at coal_ppl
    df_output = dict(
        node_loc="Westeros",
        node_dest="Westeros",
        technology="coal_ppl",
        node_origin="Westeros",
        commodity="steel",
        level="material",
        year_vtg=[690, 700, 710, 720],
        time="year",
        time_origin="year",
        time_dest="year",
        value=1,
        unit="t",
    )

    result_o = make_df("output_cap_new", **df_output)

    # Add steel demand
    df_demand = dict(
        node="Westeros",
        commodity="steel",
        level="material",
        year=[700, 710, 720],
        time="year",
        value=[100, 150, 170],
        unit="t",
    )

    result_d = make_df("demand", **df_demand)

    # Add new commodity and level
    scen.check_out()
    scen.add_set("commodity", "steel")
    scen.add_set("level", "material")
    scen.commit("add steel as a commodity")

    # Add new parameters
    scen.check_out()
    scen.add_par("output_cap_ret", result_o)
    scen.add_par("output_cap_new", result_o)
    scen.commit("add output_cap_ret & output_cap_new")

    scen.check_out()
    scen.add_par("demand", result_d)
    scen.commit("add demand")

    scen.solve()

    price_steel = scen.var("PRICE_COMMODITY", {"commodity": "steel"})

    assert np.isclose(price_steel.lvl[0], 536.519)
