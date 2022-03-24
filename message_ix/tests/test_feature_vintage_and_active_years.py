import pandas as pd
import pandas.testing as pdt

from message_ix import Scenario
from message_ix.testing import SCENARIO
import pytest


def test_vintage_and_active_years(test_mp):
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
    scen.add_set("node", "foo")
    scen.add_set("technology", "bar")
    scen.add_par(
        "duration_period", pd.DataFrame({"unit": "???", "value": 10, "year": years})
    )
    scen.add_par(
        "technical_lifetime",
        pd.DataFrame(
            {
                "node_loc": "foo",
                "technology": "bar",
                "unit": "???",
                "value": 20,
                "year_vtg": years,
            }
        ),
    )

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
    pdt.assert_frame_equal(pd.DataFrame(columns=["year_vtg", "year_act"]), obs)

    # Exception is raised for incorrect arguments
    with pytest.raises(ValueError, match="3 arguments are required if using `ya_args`"):
        scen.vintage_and_active_years(ya_args=("foo", "bar"))


def test_vintage_and_active_years_upd(test_mp):
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
    scen.add_set("node", "foo")
    scen.add_set("technology", "bar")
    scen.add_par(
        "duration_period",
        pd.DataFrame({"unit": "???", "value": [5, 5, 5, 5, 5, 10], "year": years}),
    )
    scen.add_par(
        "technical_lifetime",
        pd.DataFrame(
            {
                "node_loc": "foo",
                "technology": "bar",
                "unit": "???",
                "value": 20,
                "year_vtg": years,
            }
        ),
    )

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
