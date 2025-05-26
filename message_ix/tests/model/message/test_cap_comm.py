from typing import TYPE_CHECKING, Union

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import ModelError, Scenario, make_df
from message_ix.testing import make_westeros

if TYPE_CHECKING:
    from ixmp import Platform


COMMON: dict[str, Union[int, str]] = dict(
    commodity="coal",
    level="end_of_life",
    node_dest="World",
    node_loc="World",
    node_origin="World",
    technology="coal_ppl",
    time_dest="year",
    time_origin="year",
    time="year",
    unit="t",
    value=1,
    year_act=2020,
    year_vtg=2020,
    year=2020,
)


@pytest.mark.parametrize(
    "name, dims",
    (
        ("input_cap", 10),
        ("input_cap_new", 9),
        ("input_cap_ret", 9),
        ("output_cap", 10),
        ("output_cap_new", 9),
        ("output_cap_ret", 9),
    ),
)
def test_parameters(test_mp: "Platform", name: str, dims: int) -> None:
    """Check that data for material parameters be created, stored, and retrieved."""

    s = Scenario(test_mp, "m", f"{__name__}.test_parameters", version="new")
    with s.transact(f"Add data for {name!r}"):
        for set_name in "commodity", "level", "technology", "year":
            s.add_set(set_name, COMMON[set_name])
        s.add_par(name, make_df(name, **COMMON))

    df_out = s.par(name)

    # Parameters have the correct number of dims
    assert (1, dims) == df_out.shape

    if name in ("input_cap_ret", "output_cap_ret"):
        # Parameters have certain values
        cols = ["year_vtg", "commodity"]
        exp = pd.DataFrame([[2020, "coal"]], columns=cols)
        pdt.assert_frame_equal(df_out[cols], exp)


NEEDS_CAP_COM = pytest.mark.xfail(
    raises=ModelError,
    reason="Infeasible without cap_comm=1",
)


@pytest.mark.parametrize(
    "kwargs",
    (
        pytest.param(dict(), marks=NEEDS_CAP_COM),
        pytest.param(dict(cap_comm=0), marks=NEEDS_CAP_COM),
        dict(cap_comm=1),
    ),
)
def test_new_params_working(test_mp: "Platform", kwargs: dict) -> None:
    """Check the model creation functions in message_ix.testing."""

    scen = make_westeros(test_mp, solve=False)

    common = dict(
        commodity="steel", level="material", node="Westeros", time="year", unit="t"
    )

    # Fake conversion of electricity into steel at coal_ppl
    output = dict(
        node_loc=common["node"],
        node_dest=common["node"],
        technology="coal_ppl",
        year_vtg=[690, 700, 710, 720],
        time_dest="year",
        value=1,
    )
    df_output = make_df("output_cap_new", **common, **output)

    # Add steel demand
    demand = dict(year=[700, 710, 720], value=[100, 150, 170])
    df_demand = make_df("demand", **common, **demand)

    with scen.transact("Prepare scenario for test_new_params_working()"):
        # Add new commodity and level
        scen.add_set("commodity", "steel")
        scen.add_set("level", "material")

        # Add new parameters
        scen.add_par("output_cap_ret", df_output)
        scen.add_par("output_cap_new", df_output)

        # Add demand data
        scen.add_par("demand", df_demand)

    scen.solve(**kwargs)

    price_steel = scen.var("PRICE_COMMODITY", {"commodity": "steel"}).set_index("year")

    assert np.isclose(price_steel.loc[700, "lvl"], 536.519)
