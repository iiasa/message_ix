import pytest
from ixmp import Platform

from message_ix import Scenario, make_df
from message_ix.tools.add_year import add_year, interpolate_1d, i1d_genno


@pytest.fixture
def base_scen_mp(test_mp):
    scen = Scenario(test_mp, "model", "standard", version="new")

    data = {2020: 1, 2030: 2, 2040: 3}

    years = sorted(list(set(data.keys())))
    scen.add_set("node", "node")
    scen.add_set("commodity", "comm")
    scen.add_set("level", "level")
    scen.add_set("year", years)
    scen.add_set("technology", "tec")
    scen.add_set("mode", "mode")
    output_specs = ["node", "comm", "level", "year", "year"]

    for (yr, value) in data.items():
        scen.add_par("demand", ["node", "comm", "level", yr, "year"], 1, "GWa")
        scen.add_par("technical_lifetime", ["node", "tec", yr], 10, "y")
        tec_specs = ["node", "tec", yr, yr, "mode"]
        scen.add_par("output", tec_specs + output_specs, 1, "-")
        scen.add_par("var_cost", tec_specs + ["year"], value, "USD/GWa")

    scen.commit("initialize test model")
    scen.solve(case="original_years", quiet=True)

    yield scen, test_mp


def adding_years(test_mp, scen_ref, years_new):
    scen_new = Scenario(
        test_mp, model="add_year", scenario="standard", version="new", annotation=" "
    )
    add_year(scen_ref, scen_new, years_new)
    return scen_new


def assert_function(scen_ref, scen_new, years_new, yr_test):
    # 1. Testing the set "year" for the new years
    horizon_old = sorted([int(x) for x in scen_ref.set("year")])
    horizon_test = sorted(horizon_old + years_new)
    horizon_new = sorted([int(x) for x in scen_new.set("year")])
    assert horizon_test == horizon_new

    # 2. Testing parameter "technical_lifetime" (function interpolate_1d)
    yr_next = min([x for x in horizon_old if x > yr_test])
    yr_pre = max([x for x in horizon_old if x < yr_test])
    parname = "technical_lifetime"
    ref = scen_ref.par(parname, {"technology": "tec", "year_vtg": [yr_pre, yr_next]})
    value_ref = ref["value"].mean()
    new = scen_new.par(parname, {"technology": "tec", "year_vtg": yr_test})
    value_new = float(new["value"])
    assert value_new == pytest.approx(value_ref, rel=1e-04)

    # 3. Testing parameter "var_cost" (function interpolate_2d)
    ref = scen_ref.par(
        "var_cost",
        {
            "technology": "tec",
            "year_act": [yr_pre, yr_next],
            "year_vtg": [yr_pre, yr_next],
        },
    )

    value_ref = ref["value"].mean()

    new = scen_new.par(
        "var_cost", {"technology": "tec", "year_act": yr_test, "year_vtg": yr_test}
    )

    # Asserting if the missing data is generated accurately by interpolation
    value_new = float(new["value"])
    assert value_new == pytest.approx(value_ref, rel=1e-04)


YEARS_NEW = [2025, 2035]


def test_add_year(base_scen_mp):
    scen_ref, test_mp = base_scen_mp

    # Adding new years
    scen_new = Scenario(
        test_mp, model="add_year", scenario="standard", version="new", annotation=" "
    )
    add_year(scen_ref, scen_new, YEARS_NEW)
    scen_new.solve(case="new_years", quiet=True)

    # Running the tests
    assert_function(scen_ref, scen_new, YEARS_NEW, yr_test=2025)


def test_add_year_cli(message_ix_cli, base_scen_mp):
    scen_ref, test_mp = base_scen_mp

    # Information about the base Scenario
    platform_name = test_mp.name
    model = scen_ref.model
    scenario = scen_ref.scenario

    cmd = [
        "--platform",
        platform_name,
        "--model",
        model,
        "--scenario",
        scenario,
        "add-years",
        "--years_new",
        repr(YEARS_NEW),
        "--model_new",
        "add_year",
        "--scen_new",
        "standard",
    ]

    # Delete the objects so that the database connection is closed
    del test_mp, scen_ref

    r = message_ix_cli(*cmd)
    print(r.output, r.exception)
    assert r.exit_code == 0

    # Re-load the base Scenario
    mp = Platform(name=platform_name)
    scen_ref = Scenario(mp, model=model, scenario=scenario)

    # Load the created Scenario
    scen_new = Scenario(mp, model="add_year", scenario="standard")

    assert_function(scen_ref, scen_new, YEARS_NEW, yr_test=2025)

    # Same, except with --dry-run
    r = message_ix_cli(*cmd, "--dry-run")
    assert r.exit_code == 0

    # Bad usage: not giving the base scenario info
    r = message_ix_cli(*cmd[6:], "--dry-run")
    assert r.exit_code == 2


@pytest.mark.parametrize("func", [interpolate_1d, i1d_genno])
def test_interpolate_1d(func):
    # Input data
    years_base = [2020, 2030, 2040]
    df = make_df(
        "technical_lifetime",
        node_loc="n",
        technology="t",
        value=[10.0, 20, 30],
        unit="year",
        year_vtg=years_base,
    )

    years_new = [2015, 2025, 2035, 2045]

    # With default extrapolate=False, extrapol_neg=None
    args = dict(
        df=df,
        yrs_new=years_new,
        horizon=years_base,
        year_col="year_vtg",
        extrapolate=False,
        extrapol_neg=None,
        bound_extend=True,
    )
    result = func(**args)
    print("1", result)

    # Result has all the expected years
    assert set(years_base + years_new) - {2015} == set(result["year_vtg"])

    # With extrapolate=True
    args["extrapolate"] = True
    result = func(**args)
    print("2", result)

    # Result has all the expected years
    assert set(years_base + years_new) == set(result["year_vtg"])

    # With extrapolation that produces negative values before `horizon`, extrapol_neg
    # has no effect
    years_new = [2000, 2015, 2025, 2035, 2045, 2050]
    args["yrs_new"] = years_new
    args["extrapol_neg"] = 1.1

    result = func(**args)
    print("3", result)

    # Result has all the expected years
    assert set(years_base + years_new) == set(result["year_vtg"])

    # Extrapolation that produces negative values after `horizon`
    df.loc[:, "value"] = [30.0, 20.0, 1.5]
    args["extrapol_neg"] = 1.1

    result = func(**args)
    print("4", result)

    # Result has all the expected years
    assert set(years_base + years_new) == set(result["year_vtg"])

    # With bound_extend=False
    args["bound_extend"] = False
    result = func(**args)
    print("5", result)
