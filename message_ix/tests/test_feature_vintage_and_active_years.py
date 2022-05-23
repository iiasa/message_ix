import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import Scenario
from message_ix.testing import SCENARIO


def _add_tl(scenario, years):
    """Add a technology, its lifetime, and period durations."""
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
            year_vtg=years,
        ),
    )


def test_vintage_and_active_years1(test_mp):
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    years = [2000, 2010, 2020]
    scen.add_horizon(year=years, firstmodelyear=2010)
    obs = scen.vintage_and_active_years()
    exp = pd.DataFrame(
        {
            "year_vtg": (2000, 2000, 2010, 2010, 2020),
            "year_act": (2010, 2020, 2010, 2020, 2020),
        }
    )
    pdt.assert_frame_equal(exp, obs, check_like=True)  # ignore col order

    # Add a technology, its lifetime, and period durations
    _add_tl(scen, years)
    assert all((10, 10, 10) == scen.par("duration_period")["value"])

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
    years = [2000, 2005, 2010, 2015, 2020, 2030]
    scen.add_horizon(year=years, firstmodelyear=2010)

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

    # Add a technology, its lifetime, and period durations
    _add_tl(scen, years)
    assert all((5, 5, 5, 5, 5, 10) == scen.par("duration_period")["value"])

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
    years = [2000, 2005, 2010, 2015, 2020, 2030]
    scen.add_horizon(year=years, firstmodelyear=2010)

    # Add a technology, its lifetime, and period durations
    _add_tl(scen, filter(lambda y: y <= 2020, years))
    assert all((5, 5, 5, 5, 5, 10) == scen.par("duration_period")["value"].values)

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
