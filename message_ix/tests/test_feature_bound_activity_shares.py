from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import pytest
from ixmp import Platform
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal

from message_ix import ModelError, Scenario, make_df
from message_ix.testing import make_dantzig

#: First model year of the :func:`.make_dantzig` scenario.
Y0 = 1963

#: Name of a members of the ``shares`` set.
SHARES = "test-shares"

#: Fixed key-values for subsets and parameters in the :func:`.make_dantzig` scenario.
COMMON = dict(commodity="cases", shares=SHARES, time="year", unit="cases")


def assert_dantzig_solution(s: Scenario, lp_method: int) -> None:
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


def calculate_activity(scen: Scenario, tec="transport_from_seattle") -> pd.Series:
    """Sum ``ACT`` levels for `technology` and `mode` groups; return sums for `tec`."""
    return scen.var("ACT").groupby(["technology", "mode"])["lvl"].sum().loc[tec]


def test_b_a_u_1_mode(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test effect of ``bound_activity_up`` on 1 mode of a tech with multiple modes."""
    s0 = make_dantzig(test_mp, solve=True, request=request)

    # Constraint value
    exp = 0.5 * calculate_activity(s0).sum()

    # Add constraint parameter data to a clone
    s1 = s0.clone(keep_solution=False)

    name = "bound_activity_up"
    mode = "to_chicago"  # Only constrain this mode
    data = make_df(
        name,
        **COMMON,
        node_loc="seattle",
        technology="transport_from_seattle",
        year_act=Y0,
        mode=mode,
        value=exp,
    )

    with s1.transact():
        s1.add_par(name, data)
    s1.solve(quiet=True)

    # Observed result matches the constrained value
    assert np.isclose(calculate_activity(s1).loc[mode], exp)

    # Meeting the constraint has increased the objective function value
    assert s1.var("OBJ")["lvl"] >= s0.var("OBJ")["lvl"]


@pytest.mark.parametrize("lp_method", [1, 2, 3, 4, 5])
@pytest.mark.parametrize(
    "constraint_value",
    [pytest.param(299, marks=pytest.mark.xfail(raises=ModelError)), 301, 325],
)
def test_b_a_u_all_modes(
    request: pytest.FixtureRequest,
    test_mp: Platform,
    tmp_model_dir: Path,
    lp_method: int,
    constraint_value: int,
) -> None:
    """Test ``bound_activity_up`` values applied to mode="all".

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
    # FIXME Resolve this by using TypedDict for make_dantzig kwargs
    s0 = make_dantzig(test_mp, solve=True, request=request, **so)  # type: ignore[arg-type]

    # Ensure the solution is as expected given the LP method
    assert_dantzig_solution(s0, lp_method)

    # Add constraint parameter data to a clone
    s1 = s0.clone(keep_solution=False)
    name = "bound_activity_up"
    data = make_df(
        name,
        **COMMON,
        node_loc="seattle",
        technology="transport_from_seattle",
        year_act=Y0,
        mode="all",
        value=constraint_value,
    )

    with s1.transact():
        s1.add_par(name, data)

    # Scenario solves (not with constraint_value = 299)
    s1.solve(quiet=True, **so)

    # Objective function value is equal to the unconstrained value
    assert_equal(s0.var("OBJ")["lvl"], s1.var("OBJ")["lvl"])

    # Constraint is effective
    assert constraint_value >= calculate_activity(s1).sum()

    if lp_method in {1, 2, 3}:
        # Constraint reduced the total ACT of t=transport_from_seattle
        assert calculate_activity(s0).sum() > calculate_activity(s1).sum()
    else:
        # Constraint had no effect on total ACT of t=transport_from_seattle
        assert_equal(calculate_activity(s0).sum(), calculate_activity(s1).sum())


def test_commodity_share_lo(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test effect of ``share_commodity_lo``."""
    n = "new-york"
    common = COMMON | dict(mode="all", level="consumption", node_share=n, node=n)

    s0 = make_dantzig(test_mp, solve=True, request=request)

    # data for share bound
    def calc_share(s: Scenario) -> float:
        """Compute the share achieved on scenario `s`."""
        a = calculate_activity(s, tec="transport_from_seattle").loc["to_new-york"]
        b = calculate_activity(s, tec="transport_from_san-diego").loc["to_new-york"]
        return a / (a + b)

    # Constraint value
    exp = 1.0 * calc_share(s0)

    # Add constraint parameter data to a clone
    s1 = s0.clone(keep_solution=False)

    with s1.transact("Add share constraints"):
        s1.add_set("shares", SHARES)

        # Add category and mapping set elements
        for tt, members in (
            ("share", ["transport_from_seattle"]),
            ("total", ["transport_from_seattle", "transport_from_san-diego"]),
        ):
            s1.add_cat("technology", tt, members)
            name = f"map_shares_commodity_{tt}"
            s1.add_set(name, make_df(name, **common, type_tec=tt))

        # Add the value of the constraint
        name = "share_commodity_lo"
        s1.add_par(name, make_df(name, **common, value=exp, year_act=Y0))

    s1.solve(quiet=True)

    # The solution has the expected share
    assert np.isclose(exp, calc_share(s1))

    # Objective function value is larger in the clone (with constraints) than the
    # original scenario (unconstrained)
    assert s1.var("OBJ")["lvl"] >= s0.var("OBJ")["lvl"]


def test_commodity_share_up(request: pytest.FixtureRequest, test_mp: Platform) -> None:
    """Test effect of ``share_commodity_up``.

    ``ACT`` variable values from the original solution::

        technology                node_loc   mode         lvl    mrg
        canning_plant             seattle    production   350.0  0.000
        transport_from_seattle    seattle    to_new-york   50.0  0.000
        transport_from_seattle    seattle    to_chicago   300.0  0.000
        transport_from_seattle    seattle    to_topeka      0.0  0.036
        canning_plant             san-diego  production   600.0  0.000
        transport_from_san-diego  san-diego  to_new-york  275.0  0.000
        transport_from_san-diego  san-diego  to_chicago     0.0  0.009
        transport_from_san-diego  san-diego  to_topeka    275.0  0.000

    Seattle canning_plant production (original: 350) is limited to 50% of all
    transport_from_san-diego (original: 550). Expected outcome: some increase of
    transport_from_san-diego with some decrease of production in seattle.
    """

    # data for share bound
    def calc_share(s):
        a = s.var(
            "ACT", filters={"technology": ["canning_plant"], "node_loc": ["seattle"]}
        )["lvl"][0]
        b = calculate_activity(s, tec="transport_from_san-diego").sum()
        return a / b

    common = COMMON | dict(level="supply", node_share="seattle")

    # type_tec members
    tt_share = "share"
    tt_total = "total"

    # common operations for both subtests
    def add_data(s: Scenario, modes: Union[str, list[str]]) -> None:
        with s.transact("Add share_commodity_up"):
            s.add_set("shares", SHARES)
            s.add_cat("technology", tt_share, "canning_plant")
            s.add_cat("technology", tt_total, "transport_from_san-diego")

            name = "map_shares_commodity_share"
            kw = common | dict(node="seattle", type_tec=tt_share, mode="production")
            s.add_set(name, make_df(name, **kw))

            name = "map_shares_commodity_total"
            _kw = common | dict(node="san-diego", type_tec=tt_total, mode=modes)
            s.add_set(name, make_df(name, **_kw))

            name = "share_commodity_up"
            kw = common | dict(unit="%")
            s.add_par(name, make_df(name, **kw, year_act=Y0, value=0.5))

        s.solve(quiet=True)

    # initial data
    s0 = make_dantzig(test_mp, solve=True, request=request)

    exp = 0.5

    # In the unmodified Dantzig scenario, the share is larger than the value to be used
    assert calc_share(s0) > exp

    # Add share constraints for each mode explicitly
    s1 = s0.clone(keep_solution=False)
    add_data(s1, modes=["to_new-york", "to_chicago", "to_topeka"])

    # Resulting shares are within the bound
    obs1 = calc_share(s1)
    assert obs1 <= exp

    # Meeting the constraint has increased the objective function value
    assert s1.var("OBJ")["lvl"] >= s0.var("OBJ")["lvl"]

    # Add share constraints with mode='all'
    s2 = s0.clone(keep_solution=False)
    add_data(s2, modes="all")

    # Shares are the same as constraining each mode individually, and within the bound
    assert obs1 == calc_share(s2) <= exp

    # Meeting the constraint has increased the objective function value
    assert s2.var("OBJ")["lvl"] >= s0.var("OBJ")["lvl"]

    # Test of https://github.com/iiasa/message_ix/pull/930

    # Add emissions factor and check the emissions equivalence function
    s3 = s1.clone(keep_solution=False)
    name, e = "emission_factor", "emiss"
    data = make_df(
        name,
        emission=e,
        mode="production",
        node_loc="seattle",
        technology="canning_plant",
        year_vtg=Y0,
        year_act=Y0,
        value=1.5,
        unit="kg/kWa",
    )
    with s3.transact("Add emission factor"):
        s3.add_set("emission", e)
        s3.add_cat("emission", "emiss_type", e)
        s3.add_par(name, data)

    s3.solve(quiet=True)

    # EMISSION_EQUIVALENCE does not have the type_tec == "share"
    obs = s3.var("EMISS")
    assert not (set(obs["type_tec"].unique()) & {"share", "total"}), (
        f"EMISSION_EQUIVALENCE contains type_tec='share' or 'total':\n{obs}"
    )


@pytest.mark.parametrize(
    "dir, node, mode, exp_value",
    (
        ("lo", "san-diego", "to_new-york", 1.05),
        ("up", "seattle", "to_chicago", 0.95),
    ),
)
def test_share_mode(
    request: pytest.FixtureRequest,
    test_mp: Platform,
    dir: str,
    node: str,
    mode: str,
    exp_value: float,
) -> None:
    """Test effect of parameters ``share_mode_{lo,up}``."""
    s0 = make_dantzig(test_mp, solve=True, request=request)

    tec = f"transport_from_{node}"

    def calc_share(s: Scenario) -> float:
        """Shorthand for calculating share of `mode` in total activity."""
        tmp = calculate_activity(s, tec=tec)
        return tmp.loc[mode] / tmp.sum()

    # Constraint value
    exp = exp_value * calc_share(s0)

    # Add constraint parameter data to a clone
    s1 = s0.clone(keep_solution=False)

    name = f"share_mode_{dir}"
    data = make_df(
        name,
        **COMMON,
        node_share=node,
        technology=tec,
        mode=mode,
        year_act=Y0,
        value=exp,
    )

    with s1.transact():
        s1.add_set("shares", SHARES)
        s1.add_par(name, data)
    s1.solve(quiet=True)

    # Observed result matches the constrained value
    assert np.isclose(calc_share(s1), exp)

    # Meeting the constraint has increased the objective function value
    assert s1.var("OBJ")["lvl"] >= s0.var("OBJ")["lvl"]
