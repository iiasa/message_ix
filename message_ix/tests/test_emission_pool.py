import pandas as pd
import pandas.testing as pdt

from message_ix.testing import make_westeros


def prep_scenario(s, test_mp):
    s.check_out()

    # Initialize parameters
    new_par = {
        "historical_emission_pool": ["node", "emission", "type_tec", "year"],
        "emission_sink_rate": ["node", "emission", "type_tec", "year"],
        "bound_emission_pool": ["node", "type_emission", "type_tec", "year"],
        "tax_emission_pool": ["node", "type_emission", "type_tec", "year"],
    }
    for par, idx in new_par.items():
        if par not in s.par_list():
            s.init_par(par, idx)

    # Initialize sets
    new_set = {
        "is_bound_emission_pool": ["node", "type_emission", "type_tec", "year"],
        "is_emission_sink_rate": ["node", "emission", "type_tec", "year"],
    }
    for sets, idx in new_set.items():
        if sets not in s.set_list():
            s.init_set(sets, idx)

    # Initialize variables
    new_var = {
        "EMISS_POOL": ["node", "emission", "type_tec", "year"],
        "PRICE_EMISSION_POOL": ["node", "type_emission", "type_tec", "year"],
    }
    for var, idx in new_var.items():
        if var not in s.var_list():
            s.init_var(var, idx)

    # Add emission parameters
    s.add_set("emission", "CO2")
    s.add_cat("emission", "GHG", "CO2")
    test_mp.add_unit("tCO2/kWa")
    test_mp.add_unit("MtCO2")

    # Add emission factor
    year_df = s.vintage_and_active_years()
    emission_factor = {
        "node_loc": "Westeros",
        "technology": "coal_ppl",
        "year_vtg": year_df["year_vtg"],
        "year_act": year_df["year_act"],
        "mode": "standard",
        "unit": "tCO2/kWa",
        "emission": "CO2",
        "value": 7.4,
    }
    s.add_par("emission_factor", emission_factor)

    # Add historic emission pool
    s.add_set("type_year", 690)
    s.add_set("cat_year", pd.DataFrame({"type_year": [690], "year": 690}))
    df = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": 690,
            "value": [100000],
            "unit": "MtCO2",
        }
    )
    s.add_par("historical_emission_pool", df)

    df = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720],
            "value": [0.02, 0.01, 0.005],
            "unit": "???",
        }
    )
    s.add_par("emission_sink_rate", df)
    s.add_set("is_emission_sink_rate", df.drop(["value", "unit"], axis=1))

    s.commit("prep test sceanrios")


def test_add_setup(test_mp):
    s = make_westeros(test_mp, quiet=True)
    prep_scenario(s, test_mp)
    s.solve(var_list=["EMISS_POOL", "PRICE_EMISSION_POOL"])

    # Ensure that parameter historical_emission_pool
    # has been added.
    exp = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": 690,
            "value": [100000],
            "unit": "MtCO2",
        }
    )

    obs = s.par("historical_emission_pool")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)

    # Ensure that parameter emission_sink_rate
    # has been added.
    exp = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720],
            "value": [0.02, 0.01, 0.005],
            "unit": "???",
        }
    )

    obs = s.par("emission_sink_rate")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)

    # Ensure that set is_emission_sink_rate
    # has been added.
    exp = exp.drop(["value", "unit"], axis=1)

    obs = s.set("is_emission_sink_rate")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_tax_emission_pool(test_mp):
    s = make_westeros(test_mp, quiet=True)
    prep_scenario(s, test_mp)

    s.check_out()
    df = pd.DataFrame(
        {
            "node": "Westeros",
            "type_emission": "GHG",
            "type_tec": "all",
            "year": [700, 710, 720],
            "value": [500, 500, 500],
            "unit": "???",
        }
    )
    s.add_par("tax_emission_pool", df)
    s.commit("tax_emission_pool added")

    s.solve(var_list=["EMISS_POOL", "PRICE_EMISSION_POOL"])

    exp = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720],
            "lvl": [86874.248590, 80820.292479, 76971.707123],
            "mrg": 0.0,
        }
    )

    obs = s.var("EMISS_POOL")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_tax_emission_pool_world(test_mp):
    s = make_westeros(test_mp, quiet=True)
    prep_scenario(s, test_mp)

    s.check_out()
    s.add_set("type_emission", "CO2")
    s.add_cat("emission", "CO2", "CO2")

    for par in ["emission_sink_rate", "historical_emission_pool"]:
        df = s.par(par)
        df["node"] = "World"
        s.add_par(par, df)

    for set in ["is_emission_sink_rate"]:
        df = s.set(set)
        df["node"] = "World"
        s.add_set(set, df)

    df = pd.DataFrame(
        {
            "node": "World",
            "type_emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720],
            "value": [500, 500, 500],
            "unit": "???",
        }
    )
    s.add_par("tax_emission_pool", df)
    s.commit("tax_emission_pool added")

    s.solve(var_list=["EMISS_POOL", "PRICE_EMISSION_POOL"])

    exp = pd.DataFrame(
        {
            "node": 3 * ["World"] + 3 * ["Westeros"],
            "emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720, 700, 710, 720],
            "lvl": [
                86874.248590,
                80820.292479,
                76971.707123,
                86874.248590,
                80820.292479,
                76971.707123,
            ],
            "mrg": 0.0,
        }
    )

    obs = s.var("EMISS_POOL")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)


def test_bound_emission_pool(test_mp):
    s = make_westeros(test_mp, quiet=True)
    prep_scenario(s, test_mp)

    s.check_out()
    df = pd.DataFrame(
        {
            "node": "Westeros",
            "type_emission": "GHG",
            "type_tec": "all",
            "year": [700, 710, 720],
            "value": [87000, 86000, 85000],
            "unit": "???",
        }
    )
    s.add_par("bound_emission_pool", df)
    s.add_set("is_bound_emission_pool", df.drop(["value", "unit"], axis=1))
    s.commit("bound_emission_pool added")

    s.solve(var_list=["EMISS_POOL", "PRICE_EMISSION_POOL"])

    exp = pd.DataFrame(
        {
            "node": "Westeros",
            "emission": "CO2",
            "type_tec": "all",
            "year": [700, 710, 720],
            "lvl": [87000, 85476.734072, 85000],
            # When changing the capacity factor of wind to 0.36,
            # comment in the line below.
            # "lvl": [87000, 85975.299326, 85000],
            "mrg": 0.0,
        }
    )

    obs = s.var("EMISS_POOL")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)

    exp = pd.DataFrame(
        {
            "node": "Westeros",
            "type_emission": "GHG",
            "type_tec": "all",
            "year": [700, 720],
            "lvl": [1.8271384, 2.939589],
            # When changing the capacity factor of wind to 0.36,
            # comment in the line below.
            # "lvl": [27.397316, 44.070817],
            "mrg": 0.0,
        }
    )

    obs = s.var("PRICE_EMISSION_POOL")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)
