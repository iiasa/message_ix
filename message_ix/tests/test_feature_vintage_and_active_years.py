from collections.abc import Sequence
from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd
import pytest
from ixmp import Platform
from pandas.testing import assert_frame_equal

from message_ix import Scenario, make_df
from message_ix.testing import SCENARIO

# NOTE If we really need to save runtime, these tests might not need to be parametrized.
# vintage_and_active_years() seems composite, but not sure if individual parts are
# tested here (and not just in ixmp).


@lru_cache()
def _generate_yv_ya(periods: tuple[int, ...]) -> pd.DataFrame:
    """All meaningful combinations of (vintage year, active year) given `periods`."""
    # commented: currently unused, this does the same as the line below, using (start
    # period, final period, uniform ``duration_period). The intermediate periods are
    # inferred
    # _s = slice(periods_or_start, end + 1, dp)
    # data = np.mgrid[_s, _s]

    # - Create a mesh grid using numpy built-ins
    # - Take the upper-triangular portion (setting the rest to 0)
    # - Reshape
    data = np.triu(np.meshgrid(periods, periods, indexing="ij")).reshape((2, -1))
    # Filter only non-zero pairs
    return pd.DataFrame(
        filter(sum, zip(data[0, :], data[1, :])),
        columns=["year_vtg", "year_act"],
        dtype=np.int64,
    )


def _setup(
    mp: Platform,
    years: Sequence[int],
    firstmodelyear: int,
    tl_years: Optional[filter] = None,
) -> tuple[Scenario, pd.DataFrame]:
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


def test_vintage_and_active_years1(test_mp: Platform) -> None:
    """Basic functionality of :meth:`.vintage_and_active_years`."""
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

    with pytest.warns(DeprecationWarning, match="'in_horizon' argument to"):
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

    # Empty data frame: only 2000 and 2010 valid year_act for this node/tec; but both
    # are before the first model year
    with pytest.warns(DeprecationWarning, match="'in_horizon' argument to"):
        obs = scen.vintage_and_active_years(
            ya_args=("foo", "bar", years[0]), in_horizon=True
        )
    assert_frame_equal(
        pd.DataFrame(columns=["year_vtg", "year_act"], dtype=np.int64), obs
    )

    # Exception is raised for incorrect arguments
    with pytest.raises(ValueError, match=r"got \('foo',\) of length 1"):
        scen.vintage_and_active_years(ya_args=("foo",))  # type: ignore[arg-type]


def test_vintage_and_active_years2(test_mp: Platform) -> None:
    """:meth:`.vintage_and_active_years` with periods of uneven duration."""
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]

    scen, yvya_all = _setup(test_mp, years, fmy)

    extra = pd.Series(dict(year_vtg=2010, year_act=2030)).to_frame().T

    # No arguments
    obs = scen.vintage_and_active_years()
    exp = _q(yvya_all, f"{fmy} <= year_act")
    assert_frame_equal(exp, obs)

    # ya_args with 3 elements
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = _q(yvya_all, f"year_vtg == 2010 and {fmy} <= year_act")
    assert_frame_equal(exp, obs)

    # ya_args with 2 elements (no year_vtg)
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = _q(yvya_all, f"{fmy} <= year_act and year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs)

    # in_horizon = False
    with pytest.warns(DeprecationWarning, match="'in_horizon' argument to"):
        obs = scen.vintage_and_active_years(ya_args=("foo", "bar"), in_horizon=False)
    exp = _q(yvya_all, "year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs)

    # Limiting year_vtg
    obs = scen.vintage_and_active_years(("foo", "bar")).query("2010 <= year_vtg")
    exp = _q(yvya_all, f"{fmy} <= year_vtg")
    assert_frame_equal(exp, obs.reset_index(drop=True))

    # Limiting year_act
    obs = scen.vintage_and_active_years(("foo", "bar")).query("2020 <= year_act")
    exp = _q(yvya_all, "2020 <= year_act and year_act - year_vtg < 20", extra)
    assert_frame_equal(exp, obs.reset_index(drop=True))


def test_vintage_and_active_years3(test_mp: Platform) -> None:
    """Technology with ``technical_lifetime`` not defined to the end of the horizon."""
    years = (2000, 2005, 2010, 2015, 2020, 2030)
    fmy = years[2]

    # Last year for which the technical_lifetime of "bar" will be defined
    y_max = years[-2]

    scen, yvya_all = _setup(test_mp, years, fmy, filter(lambda y: y <= y_max, years))

    # With default tl_only=True
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"))
    exp = pd.DataFrame({"year_vtg": (2010, 2010, 2010), "year_act": (2010, 2015, 2020)})
    assert_frame_equal(exp, obs)

    # tl_only=False
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar", "2010"), tl_only=False)
    exp = _q(yvya_all, "year_vtg == 2010")
    assert_frame_equal(exp, obs)

    # ya_args with 2 elements (no year_vtg)
    obs = scen.vintage_and_active_years(ya_args=("foo", "bar"))
    exp = _q(yvya_all, f"{fmy} <= year_act <= {y_max} and year_act - year_vtg < 20")
    assert_frame_equal(exp, obs)


def test_vintage_and_active_years4(test_mp: Platform) -> None:
    """Technology with 'gaps'.

    In this test, no ``technical_lifetime`` is designated for the 2020 and 2030
    vintages. The technology thus cannot be vintaged in these periods, or active in the
    2030 period, so these should not appear in the results.
    """
    years = (2000, 2010, 2020, 2030, 2040, 2050, 2060)
    fmy = years[1]

    # Set up scenario, tech, and retrieve valid (yv, ya) pairs
    scen, yvya_all = _setup(test_mp, years, fmy)

    # Change the technical_lifetime of the technology
    tl = "technical_lifetime"
    data = scen.par(tl)
    scen.remove_par(tl, data.query("year_vtg == 2020 or year_vtg == 2030"))

    obs = scen.vintage_and_active_years(("foo", "bar"))
    assert 2030 not in obs["year_act"]
    assert not any(y in obs["year_vtg"] for y in (2020, 2030))
