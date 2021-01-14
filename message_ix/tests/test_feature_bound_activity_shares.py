import numpy as np
import pandas as pd

from message_ix import Scenario
from message_ix.testing import SCENARIO

# First model year of the Dantzig scenario
_year = 1963


def calculate_activity(scen, tec="transport_from_seattle"):
    return scen.var("ACT").groupby(["technology", "mode"])["lvl"].sum().loc[tec]


def test_add_bound_activity_up(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()

    # data for act bound
    exp = 0.5 * calculate_activity(scen).sum()
    data = pd.DataFrame(
        {
            "node_loc": "seattle",
            "technology": "transport_from_seattle",
            "year_act": _year,
            "time": "year",
            "unit": "cases",
            "mode": "to_chicago",
            "value": exp,
        },
        index=[0],
    )

    # test limiting one mode
    clone = scen.clone("foo", "bar", keep_solution=False)
    clone.check_out()
    clone.add_par("bound_activity_up", data)
    clone.commit("foo")
    clone.solve()
    obs = calculate_activity(clone).loc["to_chicago"]
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_add_bound_activity_up_all_modes(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()

    # data for act bound
    exp = 0.95 * calculate_activity(scen).sum()
    data = pd.DataFrame(
        {
            "node_loc": "seattle",
            "technology": "transport_from_seattle",
            "year_act": _year,
            "time": "year",
            "unit": "cases",
            "mode": "all",
            "value": exp,
        },
        index=[0],
    )

    # test limiting all modes
    clone = scen.clone("foo", "baz", keep_solution=False)
    clone.check_out()
    clone.add_par("bound_activity_up", data)
    clone.commit("foo")
    clone.solve()
    obs = calculate_activity(clone).sum()
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_commodity_share_up(message_test_mp):
    """Origial Solution
    ----------------

         lvl         mode    mrg   node_loc                technology
    0  350.0   production  0.000    seattle             canning_plant
    1   50.0  to_new-york  0.000    seattle    transport_from_seattle
    2  300.0   to_chicago  0.000    seattle    transport_from_seattle
    3    0.0    to_topeka  0.036    seattle    transport_from_seattle
    4  600.0   production  0.000  san-diego             canning_plant
    5  275.0  to_new-york  0.000  san-diego  transport_from_san-diego
    6    0.0   to_chicago  0.009  san-diego  transport_from_san-diego
    7  275.0    to_topeka  0.000  san-diego  transport_from_san-diego

    Constraint Test
    ---------------

    Seattle canning_plant production (original: 350) is limited to 50% of all
    transport_from_san-diego (original: 550). Expected outcome: some increase
    of transport_from_san-diego with some decrease of production in seattle.
    """
    # data for share bound
    def calc_share(s):
        a = s.var(
            "ACT", filters={"technology": ["canning_plant"], "node_loc": ["seattle"]}
        )["lvl"][0]
        b = calculate_activity(s, tec="transport_from_san-diego").sum()
        return a / b

    # common operations for both subtests
    def add_data(s, map_df):
        s.add_cat("technology", "share", "canning_plant")
        s.add_cat("technology", "total", "transport_from_san-diego")

        s.add_set("shares", "test-share")
        s.add_set(
            "map_shares_commodity_share",
            pd.DataFrame(
                {
                    "shares": "test-share",
                    "node_share": "seattle",
                    "node": "seattle",
                    "type_tec": "share",
                    "mode": "production",
                    "commodity": "cases",
                    "level": "supply",
                },
                index=[0],
            ),
        )
        s.add_set("map_shares_commodity_total", map_df)
        s.add_par(
            "share_commodity_up",
            pd.DataFrame(
                {
                    "shares": "test-share",
                    "node_share": "seattle",
                    "year_act": _year,
                    "time": "year",
                    "unit": "%",
                    "value": 0.5,
                },
                index=[0],
            ),
        )

    # initial data
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()
    exp = 0.5

    # check shares orig, should be bigger than expected bound
    orig = calc_share(scen)
    assert orig > exp

    # add share constraints for modes explicitly
    map_df = pd.DataFrame(
        {
            "shares": "test-share",
            "node_share": "seattle",
            "node": "san-diego",
            "type_tec": "total",
            "mode": ["to_new-york", "to_chicago", "to_topeka"],
            "commodity": "cases",
            "level": "supply",
        }
    )
    clone = scen.clone(scenario="share_mode_list", keep_solution=False)
    clone.check_out()
    add_data(clone, map_df)
    clone.commit("foo")
    clone.solve()

    # check shares new, should be lower than expected bound
    obs = calc_share(clone)
    assert obs <= exp

    # check obj
    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj

    # add share constraints with mode == 'all'
    map_df2 = pd.DataFrame(
        {
            "shares": "test-share",
            "node_share": "seattle",
            "node": "san-diego",
            "type_tec": "total",
            "mode": "all",
            "commodity": "cases",
            "level": "supply",
        },
        index=[0],
    )
    clone2 = scen.clone(scenario="share_all_modes", keep_solution=False)
    clone2.check_out()
    add_data(clone2, map_df2)
    clone2.commit("foo")
    clone2.solve()

    # check shares new, should be lower than expected bound
    obs2 = calc_share(clone2)
    assert obs2 <= exp

    # it should also be the same as the share with explicit modes
    assert obs == obs2

    # check obj
    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone2.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_share_commodity_lo(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, tec="transport_from_seattle").loc["to_new-york"]
        b = calculate_activity(s, tec="transport_from_san-diego").loc["to_new-york"]
        return a / (a + b)

    exp = 1.0 * calc_share(scen)

    # add share constraints
    clone = scen.clone(scenario="share_commodity_lo", keep_solution=False)
    clone.check_out()
    clone.add_cat("technology", "share", "transport_from_seattle")
    clone.add_cat(
        "technology", "total", ["transport_from_seattle", "transport_from_san-diego"]
    )
    clone.add_set("shares", "test-share")
    clone.add_set(
        "map_shares_commodity_share",
        pd.DataFrame(
            {
                "shares": "test-share",
                "node_share": "new-york",
                "node": "new-york",
                "type_tec": "share",
                "mode": "all",
                "commodity": "cases",
                "level": "consumption",
            },
            index=[0],
        ),
    )
    clone.add_set(
        "map_shares_commodity_total",
        pd.DataFrame(
            {
                "shares": "test-share",
                "node_share": "new-york",
                "node": "new-york",
                "type_tec": "total",
                "mode": "all",
                "commodity": "cases",
                "level": "consumption",
            },
            index=[0],
        ),
    )
    clone.add_par(
        "share_commodity_lo",
        pd.DataFrame(
            {
                "shares": "test-share",
                "node_share": "new-york",
                "year_act": _year,
                "time": "year",
                "unit": "cases",
                "value": exp,
            },
            index=[0],
        ),
    )
    clone.commit("foo")
    clone.solve()
    obs = calc_share(clone)
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_add_share_mode_up(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, tec="transport_from_seattle").loc["to_chicago"]
        b = calculate_activity(s, tec="transport_from_seattle").sum()
        return a / b

    exp = 0.95 * calc_share(scen)

    # add share constraints
    clone = scen.clone(scenario="share_mode_up", keep_solution=False)
    clone.check_out()
    clone.add_set("shares", "test-share")
    clone.add_par(
        "share_mode_up",
        pd.DataFrame(
            {
                "shares": "test-share",
                "node_share": "seattle",
                "technology": "transport_from_seattle",
                "mode": "to_chicago",
                "year_act": _year,
                "time": "year",
                "unit": "cases",
                "value": exp,
            },
            index=[0],
        ),
    )
    clone.commit("foo")
    clone.solve()
    obs = calc_share(clone)
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_add_share_mode_lo(message_test_mp):
    scen = Scenario(message_test_mp, **SCENARIO["dantzig"]).clone()
    scen.solve()

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, tec="transport_from_san-diego").loc["to_new-york"]
        b = calculate_activity(s, tec="transport_from_san-diego").sum()
        return a / b

    exp = 1.05 * calc_share(scen)

    # add share constraints
    clone = scen.clone("foo", "baz", keep_solution=False)
    clone.check_out()
    clone.add_set("shares", "test-share")
    clone.add_par(
        "share_mode_lo",
        pd.DataFrame(
            {
                "shares": "test-share",
                "node_share": "san-diego",
                "technology": "transport_from_san-diego",
                "mode": "to_new-york",
                "year_act": _year,
                "time": "year",
                "unit": "cases",
                "value": exp,
            },
            index=[0],
        ),
    )
    clone.commit("foo")
    clone.solve()

    obs = calc_share(clone)
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj
