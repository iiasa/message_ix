import logging

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal

from message_ix import ModelError, Scenario, make_df
from message_ix.testing import make_dantzig

log = logging.getLogger(__name__)

# First model year of the Dantzig scenario
_year = 1963


def calculate_activity(scen, tec="transport_from_seattle") -> pd.Series:
    """Sum ``ACT`` levels for `technology` and `mode` groups; return sums for `tec`."""
    return scen.var("ACT").groupby(["technology", "mode"])["lvl"].sum().loc[tec]


def test_add_bound_activity_up(request, test_mp, testrun_uid):
    scen = make_dantzig(test_mp, request=request, solve=True, quiet=True)

    # data for act bound
    exp = 0.5 * calculate_activity(scen).sum()
    name = "bound_activity_up"
    data = make_df(
        name,
        node_loc="seattle",
        technology="transport_from_seattle",
        year_act=_year,
        time="year",
        unit="cases",
        mode="to_chicago",
        value=exp,
    )

    # test limiting one mode
    clone = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} cloned", keep_solution=False
    )

    with clone.transact():
        clone.add_par("bound_activity_up", data)

    clone.solve(quiet=True)
    obs = calculate_activity(clone).loc["to_chicago"]
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def assert_dantzig_solution(s: "Scenario", lp_method: int) -> None:
    """Assert that the Dantzig model contains the expected solution.

    The model has two solutions with equal objective function values.

    - The simplex algorithms—`lp_method` is 1 (primal simplex), 2 (dual simplex), or 3
      (network simplex) find a solution in which, for instance, ``ACT`` of
      nl=san-diego, t=transport_from_san-diego, m=to_new-york is 275 cases.
    - The barrier (`lp_method` is 4) and sifting (`lp_method` is 5) algorithms find a
      solution in which the same variable is 325 cases.

    This function asserts that `s` contains the expected solution.
    """
    assert np.isclose(153.675, s.var("OBJ")["lvl"])

    cols = ["node_loc", "mode", "lvl"]

    # First lvl column: simplex solution
    # Second lvl column: other methods solution
    exp = (
        pd.DataFrame(
            [
                ["seattle", "production", 350.0, 350.0],
                ["seattle", "to_new-york", 50.0, 0.0],
                ["seattle", "to_chicago", 300.0, 300.0],
                ["seattle", "to_topeka", 0.0, 0.0],
                ["san-diego", "production", 600.0, 600.0],
                ["san-diego", "to_new-york", 275.0, 325.0],
                ["san-diego", "to_chicago", 0.0, 0.0],
                ["san-diego", "to_topeka", 275.0, 275.0],
            ]
        )
        .take([0, 1, 2 if lp_method in {1, 2, 3} else 3], axis=1)
        .set_axis(cols, axis=1)
    )

    assert_frame_equal(exp, s.var("ACT")[cols])


@pytest.mark.parametrize("lp_method", [1, 2, 3, 4, 5])
@pytest.mark.parametrize(
    "constraint_value",
    [pytest.param(299, marks=pytest.mark.xfail(raises=ModelError)), 301, 325],
)
def test_b_a_u_all_modes(request, test_mp, tmp_model_dir, lp_method, constraint_value):
    """Test ``bound_activity_up`` values applied mode="all".

    - In the unconstrained Dantzig problem:

      - Regardless of CPLEX `lp_method`, the ``ACT`` of t=transport_from_seattle,
        m=to_chicago is 300.
      - Depending on `lp_method`:

        - Simplex methods: t=transport_from_seattle, m=to_new-york is 50.0. The sum of
          the values is 300 + 50 = 350, equal to the ``ACT`` of nl=seattle,
          t=canning_plant, m=production.
        - Other methods (barrier, sifting): t=transport_from_seattle, m=to_new-york is
          zero. The sum of values is 300 + 0 = 300. The demand at n=new-york is instead
          supplied by t=transport_from_san-diego.

    - If ``bound_activity_up`` is applied to t=transport_from_seattle, m=all:

      - Any value < 300 is infeasible. This would be the value obtained, for instance,
        by summing ``ACT`` for t=transport_from_seattle across all modes for the
        barrier/sifting solution and then applying a factor < 1.0.
      - Any value >= 300 is feasible.

        - Values in the range (300, 350) alter the simplex solution, but not the barrier
          solution.
        - The objective function value does not change.
    """
    # Solve options: use the model files and read/write cplex.opt in the temporary dir
    so = dict(model_dir=tmp_model_dir, solve_options=dict(lpmethod=lp_method))

    # Create and solve the Dantzig model
    scen = make_dantzig(test_mp, request=request, solve=True, **so)

    # Ensure the solution is as expected given the LP method
    assert_dantzig_solution(scen, lp_method)

    clone = scen.clone(scenario=f"{scen.scenario} cloned", keep_solution=False)
    with clone.transact("Bound all modes of t=transport_from_seattle"):
        name = "bound_activity_up"
        clone.add_par(
            name,
            make_df(
                name,
                node_loc="seattle",
                technology="transport_from_seattle",
                year_act=_year,
                time="year",
                mode="all",
                value=constraint_value,
                unit="cases",
            ),
        )

    # Scenario solves (not with constraint_value = 299)
    clone.solve(quiet=True, **so)

    # Objective function value is equal to the unconstrained value
    assert_equal(scen.var("OBJ")["lvl"], clone.var("OBJ")["lvl"])

    # Constraint is effective
    assert constraint_value >= calculate_activity(clone).sum()

    if lp_method in {1, 2, 3}:
        # Constraint reduced the total ACT of t=transport_from_seattle
        assert calculate_activity(scen).sum() > calculate_activity(clone).sum()
    else:
        # Constraint had no effect on total ACT of t=transport_from_seattle
        assert_equal(calculate_activity(scen).sum(), calculate_activity(clone).sum())


def test_commodity_share_up(test_mp, request, testrun_uid):
    """Original Solution
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

    common = dict(shares="test-share", node_share="seattle")

    # common operations for both subtests
    def add_data(s, map_df):
        with s.transact("Add share_commodity_up"):
            s.add_cat("technology", "share", "canning_plant")
            s.add_cat("technology", "total", "transport_from_san-diego")

            s.add_set("shares", "test-share")

            s.add_set(
                "map_shares_commodity_share",
                make_df(
                    "map_shares_commodity_share",
                    **common,
                    node="seattle",
                    type_tec="share",
                    mode="production",
                    commodity="cases",
                    level="supply",
                ),
            )
            s.add_set("map_shares_commodity_total", map_df)
            s.add_par(
                "share_commodity_up",
                make_df(
                    "share_commodity_up",
                    **common,
                    year_act=_year,
                    time="year",
                    unit="%",
                    value=0.5,
                ),
            )

    # initial data
    scen = make_dantzig(test_mp, solve=True, request=request)

    exp = 0.5

    # check shares orig, should be bigger than expected bound
    orig = calc_share(scen)
    assert orig > exp

    # add share constraints for modes explicitly
    map_df = make_df(
        "map_shares_commodity_total",
        **common,
        node="san-diego",
        type_tec="total",
        mode=["to_new-york", "to_chicago", "to_topeka"],
        commodity="cases",
        level="supply",
    )
    clone = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} share_mode_list", keep_solution=False
    )
    add_data(clone, map_df)
    clone.solve(quiet=True)

    # check shares new, should be lower than expected bound
    obs = calc_share(clone)
    assert obs <= exp

    # check obj
    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj

    # add share constraints with mode == 'all'
    map_df2 = map_df.assign(mode="all")
    clone2 = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} share_all_modes", keep_solution=False
    )
    add_data(clone2, map_df2)
    clone2.solve(quiet=True)

    # check shares new, should be lower than expected bound
    obs2 = calc_share(clone2)
    assert obs2 <= exp

    # it should also be the same as the share with explicit modes
    assert obs == obs2

    # check obj
    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone2.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_commodity_share_lo(test_mp, request, testrun_uid):
    scen = make_dantzig(test_mp, request=request, solve=True, quiet=True)

    # data for share bound
    def calc_share(s: Scenario) -> float:
        """Compute the share achieved on scenario `s`."""
        a = calculate_activity(s, tec="transport_from_seattle").loc["to_new-york"]
        b = calculate_activity(s, tec="transport_from_san-diego").loc["to_new-york"]
        return a / (a + b)

    exp = 1.0 * calc_share(scen)

    # add share constraints
    clone = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} cloned", keep_solution=False
    )

    with clone.transact("Add share constraints"):
        clone.add_set("shares", "test-share")

        common = dict(
            mode="all", node="new-york", node_share="new-york", shares="test-share"
        )

        # Add category and mapping set elements
        for tt, members in (
            ("share", ["transport_from_seattle"]),
            ("total", ["transport_from_seattle", "transport_from_san-diego"]),
        ):
            clone.add_cat("technology", tt, members)
            name = f"map_shares_commodity_{tt}"
            clone.add_set(
                name,
                make_df(
                    name, **common, type_tec=tt, commodity="cases", level="consumption"
                ),
            )

        # Add the value of the constraint
        name = "share_commodity_lo"
        clone.add_par(
            name,
            make_df(
                name, time="year", unit="cases", value=exp, year_act=_year, **common
            ),
        )

    clone.solve(quiet=True)

    # The solution has the expected share
    assert np.isclose(exp, calc_share(clone))

    # Objective function value is larger in the clone (with constraints) than the
    # original scenario (unconstrained)
    assert clone.var("OBJ")["lvl"] >= scen.var("OBJ")["lvl"]


def test_add_share_mode_up(request, test_mp, testrun_uid):
    scen = make_dantzig(test_mp, request=request, solve=True, quiet=True)

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, tec="transport_from_seattle").loc["to_chicago"]
        b = calculate_activity(s, tec="transport_from_seattle").sum()
        return a / b

    exp = 0.95 * calc_share(scen)

    # add share constraints
    clone = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} cloned", keep_solution=False
    )

    with clone.transact("Add share_mode_up"):
        clone.add_set("shares", "test-share")
        clone.add_par(
            "share_mode_up",
            make_df(
                "share_mode_up",
                shares="test-share",
                node_share="seattle",
                technology="transport_from_seattle",
                mode="to_chicago",
                year_act=_year,
                time="year",
                unit="cases",
                value=exp,
            ),
        )

    clone.solve(quiet=True)
    obs = calc_share(clone)
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj


def test_add_share_mode_lo(request, test_mp, testrun_uid):
    scen = make_dantzig(test_mp, solve=True, request=request, quiet=True)

    # data for share bound
    def calc_share(s):
        a = calculate_activity(s, tec="transport_from_san-diego").loc["to_new-york"]
        b = calculate_activity(s, tec="transport_from_san-diego").sum()
        return a / b

    exp = 1.05 * calc_share(scen)

    # add share constraints
    clone = scen.clone(
        scenario=f"{scen.scenario}-{testrun_uid} cloned", keep_solution=False
    )
    with clone.transact():
        clone.add_set("shares", "test-share")
        clone.add_par(
            "share_mode_lo",
            make_df(
                "share_mode_lo",
                shares="test-share",
                node_share="san-diego",
                technology="transport_from_san-diego",
                mode="to_new-york",
                year_act=_year,
                time="year",
                unit="cases",
                value=exp,
            ),
        )

    clone.solve(quiet=True)

    obs = calc_share(clone)
    assert np.isclose(obs, exp)

    orig_obj = scen.var("OBJ")["lvl"]
    new_obj = clone.var("OBJ")["lvl"]
    assert new_obj >= orig_obj
