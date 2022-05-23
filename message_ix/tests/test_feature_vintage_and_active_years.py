from functools import lru_cache
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from message_ix import Scenario, make_df
from message_ix.testing import SCENARIO


@lru_cache()
def _generate_yv_ya(periods: Tuple[int, ...]) -> pd.DataFrame:
    """All meaningful combinations of (vintage year, active year) given `periods`."""
    # commented: currently unused, this does the same as the line below, using (start
    # period, final period, uniform ``duration_period). The intermediate periods are
    # inferred
    # _s = slice(periods_or_start, end + 1, dp)
    # data = np.mgrid[_s, _s]

    # Create a mesh grid using numpy built-ins
    data = np.meshgrid(periods, periods, indexing="ij")
    # Take the upper-triangular portion (setting the rest to 0), reshape
    data = np.triu(data).reshape((2, -1))
    # Filter only non-zero pairs
    return pd.DataFrame(
        filter(sum, zip(data[0, :], data[1, :])), columns=["year_vtg", "year_act"]
    )


def _setup(
    mp: Platform, years: Sequence[int], firstmodelyear: int, tl_years=None
) -> Tuple[Scenario, pd.DataFrame]:
    """Common setup for test of :meth:`.vintage_and_active_years`.

    Adds:

    - the model time horizon, using `years` and `firstmodelyear`.
    - a node 'foo'
    - a technology 'bar', with a ``technical_lifetime`` of 20 years; either for all
      `years`, or for a subset of `tl_years`.

    Returns the Scenario and a data frame from :func:`_generate_yv_ya`.
    """
    scenario = Scenario(mp, **SCENARIO["dantzig"], version="new")

    scenario.add_horizon(year=years, firstmodelyear=firstmodelyear)
    scenario.add_set("node", "foo")
    scenario.add_set("technology", "bar")
    scenario.add_par(
        "technical_lifetime",
        make_df(
            "technical_lifetime",
            node_loc="foo",
            technology="bar",
            unit="y",
            value=20,
            year_vtg=tl_years or years,
        ),
    )

    return scenario, _generate_yv_ya(years)


def _q(
    df: pd.DataFrame, query: str, append: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Shorthand to query the results of :func:`_generate_yv_ya`.

    1. :meth:`pandas.DataFrame.query` is called with the `query` argument.
    2. Any additional rows in `append` are appended.
    3. The index is reset.
    """
    result = df.query(query).reset_index(drop=True)

    if append is not None:
        result = pd.concat([result, append]).sort_values(
            ["year_vtg", "year_act"], ignore_index=True
        )

    return result


def test_vintage_and_active_years1(test_mp):
    years = (2000, 2010, 2020)
    fmy = years[1]

    # Set up scenario, tech, and retrieve valid (yv, ya) pairs
    scen, yvya_all = _setup(test_mp, years, fmy)

    # Default / no arguments
    assert_frame_equal(
        _q(yvya_all, f"year_act >= {fmy}"),
        scen.vintage_and_active_years(),
    )

    # part is before horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2000"))
    exp = pd.DataFrame({"year_vtg": (2000,), "year_act": (2010,)})
    assert_frame_equal(exp, obs)

    obs = scen.vintage_and_active_years(
        ya_args=("foo", "bar", "2000"), in_horizon=False
    )
    exp = pd.DataFrame({"year_vtg": (2000, 2000), "year_act": (2000, 2010)})
    assert_frame_equal(exp, obs)

    # fully in horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame({"year_vtg": (2010, 2010), "year_act": (2010, 2020)})
    assert_frame_equal(exp, obs)

    # part after horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2020"))
    exp = pd.DataFrame({"year_vtg": (2020,), "year_act": (2020,)})
    assert_frame_equal(exp, obs)

    # Advance the first model year
    scen.add_cat("year", "firstmodelyear", years[-1], is_unique=True)

    # Empty data frame: only 2000 and 2010 valid year_act for this node/tec;
    # but both are before the first model year
    obs = scen.vintage_and_active_years(
        ya_args=("foo", "bar", years[0]), in_horizon=True
    )
    assert_frame_equal(
        pd.DataFrame(columns=["year_vtg", "year_act"]), obs, check_dtype=False
    )

    # Exception is raised for incorrect arguments
    with pytest.raises(
        ValueError, match="At least 2 arguments are required if using `ya_args`"
    ):
        scen.vintage_and_active_years(ya_args=("foo"))


def test_vintage_and_active_years2(test_mp):
    # Add years of differing time length
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]

    scen, yvya_all = _setup(test_mp, years, fmy)

    extra = pd.Series(dict(year_vtg=2010, year_act=2030)).to_frame().T

    # Check if default function call is valid
    obs = scen.vintage_and_active_years()
    exp = _q(yvya_all, f"year_act >= {fmy}")
    assert_frame_equal(exp, obs)

    # Check standard functionality with different period duration lengths
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = _q(yvya_all, f"year_vtg == 2010 and year_act >= {fmy}")
    assert_frame_equal(exp, obs)

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = _q(yvya_all, f"year_act >= {fmy} and year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs)

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), in_horizon=False)
    exp = _q(yvya_all, "year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs)

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the vintage years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), vtg_lower=2010)
    exp = _q(yvya_all, f"year_vtg >= {fmy}")
    assert_frame_equal(exp, obs)

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2020
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), act_lower=2020)
    exp = _q(yvya_all, "2020 <= year_act and year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs)


def test_vintage_and_active_years3(test_mp):
    # Add years of differing time length
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]
    y_max = years[-2]


    scen, yvya_all = _setup(test_mp, years, fmy, filter(lambda y: y <= y_max, years))

    # Check standard functionality with different period duration lengths
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame({"year_vtg": (2010, 2010, 2010), "year_act": (2010, 2015, 2020)})
    assert_frame_equal(exp, obs)

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = _q(yvya_all, f"{fmy} <= year_act <= {y_max} and year_act - year_vtg < 20")
    assert_frame_equal(exp, obs)
