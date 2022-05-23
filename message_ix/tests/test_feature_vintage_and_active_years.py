from functools import lru_cache
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import Scenario
from message_ix.testing import SCENARIO


@lru_cache()
def _generate_yv_ya(
    start_or_periods: Union[Tuple[int, ...], int],
    end: Optional[int] = None,
    dp: Optional[int] = None,
) -> pd.DataFrame:
    """All meaningful combinations of (vintage year, active year).

    Can be called one of two ways:

    1. (start, end, dp): the values are the start period, final period, and (single)
       value for ``duration_period``. The intermediate periods are inferred.
    2. A sequence (tuple) of periods: the values are used directly as the periods.
    """
    # Create a mesh grid using numpy built-ins
    if isinstance(start_or_periods, int):
        assert end is not None
        _s = slice(start_or_periods, end + 1, dp)
        data = np.mgrid[_s, _s]
    else:
        assert end is None and dp is None
        data = np.meshgrid(start_or_periods, start_or_periods, indexing="ij")
    # Take the upper-triangular portion (setting the rest to 0), reshape
    data = np.triu(data).reshape((2, -1))
    # Filter only non-zero pairs
    return pd.DataFrame(
        filter(sum, zip(data[0, :], data[1, :])), columns=["year_vtg", "year_act"]
    )


def _setup(scenario, years, firstmodelyear, tl_years=None):
    """Common setup for test of :meth:`.vintage_and_active_years`.

    Adds:

    - the model time horizon, using `years` and `firstmodelyear`.
    - a node 'foo'
    - a technology 'bar', with a ``technical_lifetime`` of 20 years; either for all
      `years`, or for a subset of `tl_years`.
    """
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


def _q(
    df: pd.DataFrame, query: str, append: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Shorthand to query the results of :func:`_generate_yv_ya`."""
    result = df.query(query).reset_index(drop=True)
    if append is not None:
        result = pd.concat([result, append]).sort_values(
            ["year_vtg", "year_act"], ignore_index=True
        )
    return result


def test_vintage_and_active_years1(test_mp):
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    obs = scen.vintage_and_active_years()
    exp = pd.DataFrame(
        {
            "year_vtg": (2000, 2000, 2010, 2010, 2020),
            "year_act": (2010, 2020, 2010, 2020, 2020),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order
    years = (2000, 2010, 2020)
    fmy = years[1]

    _setup(scen, years, fmy)


    # part is before horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2000"))
    exp = pd.DataFrame({"year_vtg": (2000,), "year_act": (2010,)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    obs = scen.vintage_and_active_years(
        ya_args=("foo", "bar", "2000"), in_horizon=False
    )
    exp = pd.DataFrame({"year_vtg": (2000, 2000), "year_act": (2000, 2010)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # fully in horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame({"year_vtg": (2010, 2010), "year_act": (2010, 2020)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # part after horizon
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2020"))
    exp = pd.DataFrame({"year_vtg": (2020,), "year_act": (2020,)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Advance the first model year
    scen.add_cat("year", "firstmodelyear", years[-1], is_unique=True)

    # Empty data frame: only 2000 and 2010 valid year_act for this node/tec;
    # but both are before the first model year
    obs = scen.vintage_and_active_years(
        ya_args=("foo", "bar", years[0]), in_horizon=True
    )
    pdt.assert_frame_equal(
        pd.DataFrame(columns=["year_vtg", "year_act"]), obs, check_dtype=False
    )

    # Exception is raised for incorrect arguments
    with pytest.raises(
        ValueError, match="At least 2 arguments are required if using `ya_args`"
    ):
        scen.vintage_and_active_years(ya_args=("foo"))


def test_vintage_and_active_years2(test_mp):
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    # Add years of differing time length
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]

    _setup(scen, years, fmy)

    # Check if default function call is valid
    obs = scen.vintage_and_active_years()
    exp = pd.DataFrame(
        {
            "year_vtg": (
                2000,
                2000,
                2000,
                2000,
                2005,
                2005,
                2005,
                2005,
                2010,
                2010,
                2010,
                2010,
                2015,
                2015,
                2015,
                2020,
                2020,
                2030,
            ),
            "year_act": (
                2010,
                2015,
                2020,
                2030,
                2010,
                2015,
                2020,
                2030,
                2010,
                2015,
                2020,
                2030,
                2015,
                2020,
                2030,
                2020,
                2030,
                2030,
            ),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order


    # Check standard functionality with different period duration lengths
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame(
        {"year_vtg": (2010, 2010, 2010, 2010), "year_act": (2010, 2015, 2020, 2030)}
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = pd.DataFrame(
        {
            "year_vtg": (
                2000,
                2000,
                2005,
                2005,
                2005,
                2010,
                2010,
                2010,
                2010,
                2015,
                2015,
                2015,
                2020,
                2020,
                2030,
            ),
            "year_act": (
                2010,
                2015,
                2010,
                2015,
                2020,
                2010,
                2015,
                2020,
                2030,
                2015,
                2020,
                2030,
                2020,
                2030,
                2030,
            ),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), in_horizon=False)
    exp = pd.DataFrame(
        {
            "year_vtg": (
                2000,
                2000,
                2000,
                2000,
                2005,
                2005,
                2005,
                2005,
                2010,
                2010,
                2010,
                2010,
                2015,
                2015,
                2015,
                2020,
                2020,
                2030,
            ),
            "year_act": (
                2000,
                2005,
                2010,
                2015,
                2005,
                2010,
                2015,
                2020,
                2010,
                2015,
                2020,
                2030,
                2015,
                2020,
                2030,
                2020,
                2030,
                2030,
            ),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the vintage years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), vtg_lower=2010)
    exp = pd.DataFrame(
        {
            "year_vtg": (2010, 2010, 2010, 2010, 2015, 2015, 2015, 2020, 2020, 2030),
            "year_act": (2010, 2015, 2020, 2030, 2015, 2020, 2030, 2020, 2030, 2030),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2020
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), act_lower=2020)
    exp = pd.DataFrame(
        {
            "year_vtg": (2005, 2010, 2010, 2015, 2015, 2020, 2020, 2030),
            "year_act": (2020, 2020, 2030, 2020, 2030, 2020, 2030, 2030),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order


def test_vintage_and_active_years3(test_mp):
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    # Add years of differing time length
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]
    y_max = years[-2]

    _setup(scen, years, fmy, filter(lambda y: y <= y_max, years))


    # Check standard functionality with different period duration lengths
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame({"year_vtg": (2010, 2010, 2010), "year_act": (2010, 2015, 2020)})
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Check if no vintge-year is passed, that all values corresponding
    # to technical lifetime are passed if the active years >= 2010
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = pd.DataFrame(
        {
            "year_vtg": (
                2000,
                2000,
                2005,
                2005,
                2005,
                2010,
                2010,
                2010,
                2015,
                2015,
                2020,
            ),
            "year_act": (
                2010,
                2015,
                2010,
                2015,
                2020,
                2010,
                2015,
                2020,
                2015,
                2020,
                2020,
            ),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order
