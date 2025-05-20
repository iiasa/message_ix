import sys
from collections.abc import Generator
from copy import deepcopy
from pathlib import Path
from subprocess import run
from typing import Any, Optional

import ixmp
import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import pytest
from ixmp.backend.jdbc import JDBCBackend

import message_ix
from message_ix import Scenario
from message_ix.testing import GHA, SCENARIO, make_dantzig, make_westeros


@pytest.fixture
def dantzig_message_scenario(
    message_test_mp: ixmp.Platform,
) -> Generator[Scenario, Any, None]:
    yield Scenario(message_test_mp, **SCENARIO["dantzig"])


class TestScenario:
    @pytest.mark.parametrize(
        "set_name, old, new, keep",
        (
            ("technology", "coal_ppl", "coal_powerplant", False),
            ("node", "Westeros", "Essos", False),
            ("node", "Westeros", "Essos", True),
            # "year" dimensions: integer instead of string values; model is infeasible
            # (GAMS error)
            pytest.param("year", 700, 701, False, marks=pytest.mark.xfail),
            # Indexed set, doesn't work
            pytest.param("cat_year", "foo", "bar", False, marks=pytest.mark.xfail),
            # Name of a parameter, not a set
            pytest.param(
                "bound_activity_up",
                "",
                "",
                False,
                marks=pytest.mark.xfail(raises=KeyError),
            ),
            # Not a name of any item
            pytest.param(
                "foo", "", "", False, marks=pytest.mark.xfail(raises=KeyError)
            ),
        ),
    )
    def test_rename0(
        self,
        test_mp: ixmp.Platform,
        set_name: str,
        old: str,
        new: str,
        keep: bool,
        request: pytest.FixtureRequest,
    ) -> None:
        # Create a Westeros scenario instance and solve it
        scen_ref = make_westeros(test_mp, quiet=True, solve=True, request=request)

        # Clone the scenario to do renaming and tests
        scen = scen_ref.clone(keep_solution=False)

        # Rename members of a message_ix.set from an "old" name to a "new" name
        scen.check_out()
        scen.rename(set_name, {old: new}, keep)

        # Check if the new member has been added to that set
        assert new in set(scen.set(set_name))

        # Check if the scenario solves and the objective function remains the same
        scen.solve(quiet=True)

        # Check if "old" is removed (keep=False)
        assert keep == (old in set(scen.set(set_name)))

        # Check if OBJ value remains unchanged when "old" is removed (keep=False); or
        # twice as high when "old" note is kept (keep=True)
        exp = scen_ref.var("OBJ")["lvl"] * (1 + int(keep and set_name == "node"))
        assert np.isclose(exp, scen.var("OBJ")["lvl"])

    @pytest.mark.parametrize("check_out", (True, False))
    @pytest.mark.parametrize("keep", (True, False))
    def test_rename1(
        self,
        request: pytest.FixtureRequest,
        dantzig_message_scenario: Scenario,
        check_out: bool,
        keep: bool,
    ) -> None:
        scen = dantzig_message_scenario
        assert scen.par("output")["technology"].isin(["canning_plant"]).any()

        clone = scen.clone(scenario=request.node.name)

        if check_out:
            clone.check_out()

        clone.rename("technology", {"canning_plant": "foo_bar"}, keep=keep)

        assert keep == clone.par("output")["technology"].isin(["canning_plant"]).any()
        assert clone.par("output")["technology"].isin(["foo_bar"]).any()

        clone.solve(quiet=True)
        assert np.isclose(clone.var("OBJ")["lvl"], 153.675)

    def test_rename2(self, dantzig_message_scenario: Scenario) -> None:
        """Test :meth:`.rename` for parameters with 2+ indexes for the same set."""
        scen = dantzig_message_scenario

        # Counts of unique combinations of (node_loc, node_dest)
        vc_pre = scen.par("output")[["node_loc", "node_dest"]].value_counts()
        assert 1 == vc_pre[("seattle", "new-york")]

        # Rename
        scen.rename("node", {"seattle": "redmond", "new-york": "brooklyn"})

        # Same number of unique combinations
        vc_post = scen.par("output")[["node_loc", "node_dest"]].value_counts()
        assert len(vc_pre) == len(vc_post)

        # Values are renamed when appearing in either of the sets indexed by `node`
        assert 1 == vc_post[("redmond", "brooklyn")]

    def test_solve(self, dantzig_message_scenario: Scenario) -> None:
        s = dantzig_message_scenario

        # Scenario solves correctly
        s.solve()

        base_path = Path(message_ix.__file__).parent.joinpath("model")
        name = "Canning_problem_(MESSAGE_scheme)_standard.gdx"

        # Check both the GDX input and output files
        for parts in ("data", f"MsgData_{name}"), ("output", f"MsgOutput_{name}"):
            path = str(base_path.joinpath(*parts))

            # ixmp_version is present in the GDX file
            result = run(["gdxdump", path, "Symb=ixmp_version"], capture_output=True)

            # ixmp_version contains the expected contents
            assert "'message_ix'.'3-" in result.stdout.decode()
            assert "'ixmp'.'3-" in result.stdout.decode()


@pytest.mark.skipif(not GHA, reason="Check for GitHub Actions workflows only")
def test_backends_available() -> None:
    """Check that the expected set of backends are available within GHA workflows."""
    from ixmp.backend import available

    exp = {"ixmp4", "jdbc"} if sys.version_info >= (3, 10) else {"jdbc"}
    assert exp <= set(available())


def test_year_int(test_mp: ixmp.Platform, request: pytest.FixtureRequest) -> None:
    scen = make_dantzig(test_mp, solve=True, multi_year=True, request=request)

    # Dimensions indexed by 'year' are returned as integers for all item types
    assert scen.set("cat_year").dtypes["year"] == "int"
    assert scen.par("demand").dtypes["year"] == "int"
    assert scen.par("bound_activity_up").dtypes["year_act"] == "int"
    assert scen.var("ACT").dtypes["year_vtg"] == "int"
    assert scen.equ("COMMODITY_BALANCE_GT").dtypes["year"] == "int"


def test_add_spatial_single(test_mp: ixmp.Platform) -> None:
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    data = {"country": "Austria"}
    scen.add_spatial_sets(data)

    exp = ["World", "Austria"]
    obs = scen.set("node")
    npt.assert_array_equal(obs, exp)

    exp = ["World", "global", "country"]
    obs = scen.set("lvl_spatial")
    npt.assert_array_equal(obs, exp)

    exp_map = [["country", "Austria", "World"]]
    obs = scen.set("map_spatial_hierarchy")
    npt.assert_array_equal(obs, exp_map)


def test_add_spatial_multiple(test_mp: ixmp.Platform) -> None:
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    data = {"country": ["Austria", "Germany"]}
    scen.add_spatial_sets(data)

    exp = ["World", "Austria", "Germany"]
    obs = scen.set("node")
    npt.assert_array_equal(obs, exp)

    exp = ["World", "global", "country"]
    obs = scen.set("lvl_spatial")
    npt.assert_array_equal(obs, exp)

    exp_map = [["country", "Austria", "World"], ["country", "Germany", "World"]]
    obs = scen.set("map_spatial_hierarchy")
    npt.assert_array_equal(obs, exp_map)


def test_add_spatial_hierarchy(test_mp: ixmp.Platform) -> None:
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    data = {"country": {"Austria": {"state": ["Vienna", "Lower Austria"]}}}
    scen.add_spatial_sets(data)

    exp = ["World", "Vienna", "Lower Austria", "Austria"]
    obs = scen.set("node")
    npt.assert_array_equal(obs, exp)

    exp = ["World", "global", "state", "country"]
    obs = scen.set("lvl_spatial")
    npt.assert_array_equal(obs, exp)

    exp_map = [
        ["state", "Vienna", "Austria"],
        ["state", "Lower Austria", "Austria"],
        ["country", "Austria", "World"],
    ]
    obs = scen.set("map_spatial_hierarchy")
    npt.assert_array_equal(obs, exp_map)


@pytest.mark.parametrize(
    "args, kwargs, exp",
    [
        # Two periods of duration 20, 1 each of duration 10 and 15
        (
            ([2020, 2030, 2050, 2070, 2085],),
            dict(),
            {
                "year": [2020, 2030, 2050, 2070, 2085],
                "fmy": [2020],
                # 20 is chosen for the first period
                "dp": [20, 10, 20, 20, 15],
            },
        ),
        # Mix of positional and keyword arguments; firstmodelyear given
        (
            ([2020, 2030, 2040, 2060],),
            dict(firstmodelyear=2030),
            {
                "year": [2020, 2030, 2040, 2060],
                # firstmodelyear as selected
                "fmy": [2030],
                # 10 is chosen for the first period
                "dp": [10, 10, 10, 20],
            },
        ),
        # Years out of order
        (
            ([2030, 2010, 2020],),
            dict(),
            {
                "year": [2010, 2020, 2030],
                "fmy": [2010],
                "dp": [10, 10, 10],
            },
        ),
        # Deprecated usage with a dict as the first positional argument
        (
            (dict(year=[2010, 2020]),),
            dict(),
            {"year": [2010, 2020], "fmy": [2010], "dp": [10, 10]},
        ),
        (
            (dict(year=[2010, 2020], firstmodelyear=2020),),
            dict(),
            {"year": [2010, 2020], "fmy": [2020], "dp": [10, 10]},
        ),
        # Deprecated usage with user errors
        pytest.param(
            (dict(firstmodelyear=2010),),
            dict(),
            None,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            (dict(year=[2010, 2020], firstmodelyear=2010),),
            dict(firstmodelyear=2020),
            None,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            (dict(year=[2010, 2020], foo="bar"),),
            dict(),
            None,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            (dict(year=[2010, 2020]),),
            dict(data=dict(year=[2010, 2020])),
            None,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ],
)
def test_add_horizon(
    test_mp: ixmp.Platform, args, kwargs, exp: Optional[dict[str, list[int]]]
) -> None:
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    # Running on both backends; add_horizon() manipulates these items
    _args = deepcopy(args)
    _kwargs = deepcopy(kwargs)

    # Call completes successfully
    if isinstance(_args[0], dict) and "data" not in _kwargs:
        with pytest.warns(
            DeprecationWarning,
            match=(
                r"dict\(\) argument to add_horizon\(\); use year= and "
                "firstmodelyear="
            ),
        ):
            scen.add_horizon(*_args, **_kwargs)
    else:
        scen.add_horizon(*_args, **_kwargs)

    # For type checkers
    assert exp

    # Sets and parameters have the expected contents
    npt.assert_array_equal(exp["year"], scen.set("year"))
    npt.assert_array_equal(exp["fmy"], scen.cat("year", "firstmodelyear"))
    npt.assert_array_equal(exp["dp"], scen.par("duration_period")["value"])


def test_add_horizon_repeat(
    test_mp: ixmp.Platform, caplog: pytest.LogCaptureFixture
) -> None:
    """add_horizon() does not handle scenarios with existing years."""
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    # Create a base scenario
    scen.add_horizon([2010, 2020, 2030])
    npt.assert_array_equal([10, 10, 10], scen.par("duration_period")["value"])

    with pytest.raises(
        ValueError,
        match=r"Scenario has year=\[2010, 2020, 2030\] and related values",
    ):
        scen.add_horizon([2015, 2020, 2025], firstmodelyear=2010)


def test_cat_all(dantzig_message_scenario: Scenario) -> None:
    scen = dantzig_message_scenario
    df = scen.cat("technology", "all")
    npt.assert_array_equal(
        df, ["canning_plant", "transport_from_seattle", "transport_from_san-diego"]
    )


def test_cat_list(test_mp: ixmp.Platform) -> None:
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")

    # cat_list() returns default 'year' categories in a new message_ix.Scenario
    # NOTE JDBC sets up default items in the DB backend, including the base expected
    # data and then finds nothing new when calling models.MESSAGE.initialize(). Thus, no
    # `commit()` is issued and ixmp_source doesn't `assignPeriodMaps()`, which would add
    # 'cumulative'.
    # IXMP4Backend only reads in the items here and thus `commit()`s, which adds
    # 'cumulative'. This can't change without adapting the `commit()` logic, which we
    # rely on elsewhere. So we have to adapt the expectation instead.
    exp = ["firstmodelyear", "lastmodelyear", "initializeyear_macro"]
    if not isinstance(test_mp._backend, JDBCBackend):
        exp.insert(0, "cumulative")
    assert exp == scen.cat_list("year")


def test_add_cat(dantzig_message_scenario: Scenario) -> None:
    scen = dantzig_message_scenario
    scen2 = scen.clone(keep_solution=False)
    scen2.check_out()
    scen2.add_cat(
        "technology", "trade", ["transport_from_san-diego", "transport_from_seattle"]
    )
    df = scen2.cat("technology", "trade")
    npt.assert_array_equal(df, ["transport_from_san-diego", "transport_from_seattle"])
    scen2.discard_changes()


def test_add_cat_unique(message_test_mp: ixmp.Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig multi-year"])
    scen2 = scen.clone(keep_solution=False)
    scen2.check_out()
    scen2.add_cat("year", "firstmodelyear", 1963, True)
    assert [1963] == scen2.cat("year", "firstmodelyear")


def test_years_active(test_mp: ixmp.Platform) -> None:
    test_mp.add_unit("year")
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    scen.add_set("node", "foo")
    scen.add_set("technology", "bar")

    # Periods of uneven length
    years = [1990, 1995, 2000, 2005, 2010, 2020, 2030]

    # First period length is immaterial
    duration = [1900, 5, 5, 5, 5, 10, 10]
    scen.add_horizon(year=years, firstmodelyear=years[-1])
    # Not sure why mypy doesn't like this
    scen.add_par(
        "duration_period",
        pd.DataFrame(zip(years, duration), columns=["year", "value"]),  # type: ignore[arg-type]
    )

    # 'bar' built in period '1995' with 25-year lifetime:
    # - is constructed in 1991-01-01.
    # - by 1995-12-31, has operated 5 years.
    # - operates until 2015-12-31. This is within the period '2020'.
    scen.add_par(
        "technical_lifetime",
        pd.DataFrame(
            dict(
                node_loc="foo",
                technology="bar",
                unit="year",
                value=25,
                year_vtg=years[1],
            ),
            index=[0],
        ),
    )

    result = scen.years_active("foo", "bar", years[1])

    # Correct return type
    assert isinstance(result, list)
    assert isinstance(result[0], int)

    # Years 1995 through 2020
    npt.assert_array_equal(result, years[1:-1])


def test_years_active_extend(message_test_mp: ixmp.Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig multi-year"])

    # Existing time horizon
    years = [1963, 1964, 1965]
    result = scen.years_active("seattle", "canning_plant", years[1])
    npt.assert_array_equal(result, years[1:])

    # Add years to the scenario
    years.extend([1993, 1995])
    scen.check_out()
    scen.add_set("year", years[-2:])
    scen.add_par("duration_period", "1993", 28, "y")
    scen.add_par("duration_period", "1995", 2, "y")

    # technical_lifetime of seattle/canning_plant/1964 is 30 years.
    # - constructed in 1964-01-01.
    # - by 1964-12-31, has operated 1 year.
    # - by 1965-12-31, has operated 2 years.
    # - operates until 1993-12-31.
    # - is NOT active within the period '1995' (1994-01-01 to 1995-12-31)
    result = scen.years_active("seattle", "canning_plant", 1964)
    npt.assert_array_equal(result, years[1:-1])


def test_years_active_extended2(test_mp: ixmp.Platform) -> None:
    test_mp.add_unit("year")
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    scen.add_set("node", "foo")
    scen.add_set("technology", "bar")

    # Periods of uneven length
    years = [1990, 1995, 2000, 2005, 2010, 2020, 2030]

    # First period length is immaterial
    duration = [1900, 5, 5, 5, 5, 10, 10]
    scen.add_horizon(year=years, firstmodelyear=years[-1])
    # Not sure why mypy doesn't like this
    scen.add_par(
        "duration_period",
        pd.DataFrame(zip(years, duration), columns=["year", "value"]),  # type: ignore[arg-type]
    )

    # 'bar' built in period '2020' with 10-year lifetime:
    # - is constructed in 2011-01-01.
    # - by 2020-12-31, has operated 10 years.
    # - operates until 2020-12-31. This is within the period '2020'.
    # The test ensures that the correct lifetime value is retrieved,
    # i.e. the lifetime for the vintage 2020.
    scen.add_par(
        "technical_lifetime",
        pd.DataFrame(
            dict(
                node_loc="foo",
                technology="bar",
                unit="year",
                value=[20, 20, 20, 20, 20, 10, 10],
                year_vtg=years,
            ),
        ),
    )

    result = scen.years_active("foo", "bar", years[-2])

    # Correct return type
    assert isinstance(result, list)
    assert isinstance(result[0], int)

    # Years 2020
    npt.assert_array_equal(result, years[-2])


def test_years_active_extend3(test_mp: ixmp.Platform) -> None:
    test_mp.add_unit("year")
    scen = Scenario(test_mp, **SCENARIO["dantzig"], version="new")
    scen.add_set("node", "foo")
    scen.add_set("technology", "bar")

    # Periods of uneven length
    years = [1990, 1995, 2000, 2005, 2010, 2020, 2030]

    scen.add_horizon(year=years, firstmodelyear=2010)

    scen.add_set("year", [1992])
    scen.add_par("duration_period", "1992", 2, "y")
    scen.add_par("duration_period", "1995", 3, "y")

    scen.add_par(
        "technical_lifetime",
        pd.DataFrame(
            dict(
                node_loc="foo",
                technology="bar",
                unit="year",
                value=[20],
                year_vtg=1990,
            ),
        ),
    )

    obs = scen.years_active("foo", "bar", 1990)

    assert obs == [1990, 1992, 1995, 2000, 2005]


def test_new_timeseries_long_name64(message_test_mp: ixmp.Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig multi-year"])
    scen = scen.clone(keep_solution=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame(
        {
            "region": [
                "India",
            ],
            "variable": [
                ("Emissions|CO2|Energy|Demand|Transportation|Aviation|Domestic|Fre"),
            ],
            "unit": [
                "Mt CO2/yr",
            ],
            "2012": [
                0.257009,
            ],
        }
    )
    scen.add_timeseries(df)
    scen.commit("importing a testing timeseries")


def test_new_timeseries_long_name64plus(message_test_mp: ixmp.Platform) -> None:
    scen = Scenario(message_test_mp, **SCENARIO["dantzig multi-year"])
    scen = scen.clone(keep_solution=False)
    scen.check_out(timeseries_only=True)
    df = pd.DataFrame(
        {
            "region": [
                "India",
            ],
            "variable": [
                (
                    "Emissions|CO2|Energy|Demand|Transportation|Aviation|"
                    "Domestic|Freight|Oil"
                ),
            ],
            "unit": [
                "Mt CO2/yr",
            ],
            "2012": [
                0.257009,
            ],
        }
    )
    scen.add_timeseries(df)
    scen.commit("importing a testing timeseries")


def test_excel_read_write(
    message_test_mp: ixmp.Platform, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    # Path to temporary file
    fname = tmp_path / (request.node.name + "_excel_read_write.xlsx")

    scen1 = Scenario(message_test_mp, **SCENARIO["dantzig"])
    scen1 = make_dantzig(mp=message_test_mp, request=request)
    scen1 = scen1.clone(scenario=request.node.name + "_clone", keep_solution=False)
    with scen1.transact(message="new set and parameter added."):
        scen1.init_set("new_set")
        scen1.add_set("new_set", "member")
        scen1.init_par("new_par", idx_sets=["new_set"])
        scen1.add_par("new_par", "member", 2, "-")

    # Writing to Excel without solving
    scen1.to_excel(fname)

    # Writing to Excel when scenario has a solution
    scen1.solve(quiet=True)
    scen1.to_excel(fname)

    scen2 = Scenario(message_test_mp, model="foo", scenario="bar", version="new")

    # Fails without init_items=True
    with pytest.raises(ValueError, match="no set 'new_set'"):
        scen2.read_excel(fname)

    # Succeeds with init_items=True
    scen2.read_excel(fname, init_items=True, commit_steps=True)

    exp = scen1.par("input")
    obs = scen2.par("input")
    pdt.assert_frame_equal(exp, obs)

    assert scen2.has_par("new_par")
    assert 2 == scen2.par("new_par").at[0, "value"]

    scen2.solve(quiet=True)
    assert np.isclose(scen2.var("OBJ")["lvl"], scen1.var("OBJ")["lvl"])


def test_clone(tmpdir: Path) -> None:
    # Two local platforms
    mp1 = ixmp.Platform(driver="hsqldb", path=tmpdir / "mp1")
    mp2 = ixmp.Platform(driver="hsqldb", path=tmpdir / "mp2")

    # A minimal scenario
    scen1 = Scenario(mp1, model="model", scenario="scenario", version="new")
    scen1.add_spatial_sets({"country": "Austria"})
    scen1.add_set("technology", "bar")
    scen1.add_horizon(year=[2010, 2020])
    scen1.commit("add minimal sets for testing")

    assert len(mp1.scenario_list(default=False)) == 1

    # Clone
    scen2 = scen1.clone(platform=mp2)

    # Return type of ixmp.Scenario.clone is message_ix.Scenario
    assert isinstance(scen2, Scenario)

    # Close and re-open both databases
    mp1.close_db()  # TODO this should be done automatically on del
    mp2.close_db()  # TODO this should be done automatically on del
    del mp1, mp2
    mp1 = ixmp.Platform(driver="hsqldb", path=tmpdir / "mp1")
    mp2 = ixmp.Platform(driver="hsqldb", path=tmpdir / "mp2")

    # Same scenarios present in each database
    assert all(mp1.scenario_list(default=False) == mp2.scenario_list(default=False))

    # Load both scenarios
    scen1 = Scenario(mp1, "model", "scenario")
    scen2 = Scenario(mp2, "model", "scenario")

    # Contents are identical
    assert all(scen1.set("node") == scen2.set("node"))
    assert all(scen1.set("year") == scen2.set("year"))
