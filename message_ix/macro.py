import logging
import os
from collections.abc import Collection, Hashable, Iterable, Mapping, MutableMapping
from dataclasses import dataclass
from functools import partial
from operator import itemgetter, mul
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
import pandas as pd

from message_ix.report import Key, Reporter

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import genno
    import pandas
    from genno import Quantity
    from pandas import DataFrame, Series

    from message_ix.core import Scenario


EXPERIMENTAL = """
======================= WARNING =======================

You are using *experimental*, incomplete features from
`message_ix.macro`—please exercise caution. Read more:
- https://github.com/iiasa/message_ix/issues/317
- https://github.com/iiasa/message_ix/issues/318
- https://github.com/iiasa/message_ix/issues/319
- https://github.com/iiasa/message_ix/issues/320

======================================================
"""

# Pairing MACRO calibration parameters with input data for consistency of units
UNITS = dict(
    cost_MESSAGE="cost_ref",
    demand_MESSAGE="demand_ref",
    historical_gdp="gdp_calibrate",
    price_MESSAGE="price_ref",
)

#: MACRO calibration parameters to be verified when reading the input data.
INPUT_DATA = [
    "aeei",
    "cost_ref",
    "demand_ref",
    "depr",
    "drate",
    "esub",
    "gdp_calibrate",
    "kgdp",
    "kpvs",
    "lotol",
    "MERtoPPP",
    "price_ref",
]


# Utility methods


def _notna(data, where=None):
    """Raise :class:`RuntimeError` if `data` contains any missing values."""
    if data.isna().any(axis=None):
        raise RuntimeError(
            f"NaN values in {__name__}.{where}:\n"
            + data[data.isna().any(axis=1)].to_string()
        )
    return data


# Internal calculations and computations (alphabetical order)


def aconst(
    bconst: "Series",
    demand_ref: "Series",
    gdp0: "Series",
    k0: "Series",
    kpvs: "Series",
    rho: "Series",
) -> "Series":
    """Calculate production function coefficient of capital and labor.

    This is the MACRO GAMS parameter `lakl`.
    """
    partmp = (bconst * demand_ref**rho).groupby(level="node").sum()
    # TODO automatically get the units here!!
    aconst = ((gdp0 / 1e3) ** rho - partmp) / (k0 / 1e3) ** (rho * kpvs)
    # want the series to only have index of node
    return aconst.droplevel("year")


def add_par(
    scenario: "Scenario", data: "pandas.DataFrame", ym1: int, *, name: str
) -> None:
    """Add `data` to the `scenario`."""
    # FIXME look up the correct units
    units: Mapping[str, str] = {}

    # Assign units
    data = data.reset_index().assign(unit=units.get(UNITS.get(name, name), "-"))

    try:
        # Remove data prior to the MACRO initialization year
        data = data.query(f"{ym1} <= year")
    except Exception:
        pass  # No column/dimension "year"

    scenario.add_par(name, data)


@dataclass
class Structures:
    """MACRO structure information."""

    level: set[str]
    node: set[str]
    sector: set[str]
    #: Model years for which MACRO is calibrated.
    year: set[int]


def add_structure(
    scenario: "Scenario",
    mapping_macro_sector: "pandas.DataFrame",
    s: Structures,
    ym1: int,
) -> None:
    """Add MACRO structure information to `scenario`."""
    # Remove old initializeyear_macro before adding new one
    cat = scenario.set("cat_year", {"type_year": "initializeyear_macro"})
    if not cat.empty:
        scenario.remove_set("cat_year", cat)

    # Add temporal set structure
    scenario.add_set("type_year", "initializeyear_macro")
    scenario.add_set("cat_year", ["initializeyear_macro", ym1])

    # Add nodal set structure
    scenario.add_set("type_node", "economy")
    for n in s.node:
        scenario.add_set("cat_node", ["economy", n])

    # Add sectoral set structure
    scenario.add_set("sector", sorted(s.sector))
    scenario.add_set("mapping_macro_sector", mapping_macro_sector)


def bconst(
    demand_ref: "DataFrame", gdp0: "Series", price_ref: "DataFrame", rho: "Series"
) -> "DataFrame":
    """Calculate production function coefficient.

    This is the MACRO GAMS parameter ``prfconst``.
    """
    # TODO automatically get the units here
    # NB(PNK) pandas 1.4.4 automatically drops "year" in the division; pandas 1.5.0
    # does not. Drop here pre-emptively.
    tmp = ((gdp0 / demand_ref) ** (rho - 1)).droplevel("year")
    return price_ref / 1e3 * tmp


def clean_model_data(data: "Quantity", s: Structures) -> "DataFrame":
    """Clean MESSAGE variable data for calibration of MACRO parameters.

    Parameters
    ----------
    data : genno.Quantity
        With short dimension names (c, l, n, y), etc.

    Returns
    -------
    pandas.DataFrame
        With full column names and a "value" column. Only the labels in `s` (levels,
        nodes, sectors, and years) appear in the respective dimensions.
    """
    from genno.operator import rename_dims, select

    names = {"c": "commodity"}

    # Construct selectors for only the values appearing in `s`
    selectors: MutableMapping[Hashable, Iterable[Hashable]] = {}
    for dim, kind in ("l", "level"), ("n", "node"), ("sector", "sector"), ("y", "year"):
        if dim in data.dims:
            selectors[dim] = sorted(getattr(s, kind))
            names[dim] = kind

    return (
        select(data, selectors)  # type: ignore [attr-defined]
        .pipe(rename_dims, names)
        .to_series()
        .rename("value")
        .reset_index()
    )


def demand(
    model_demand: "DataFrame",
    demand_ref: "DataFrame",
    mapping_macro_sector: "DataFrame",
    ym1: int,
) -> "DataFrame":
    """Prepare data for the ``demand_MESSAGE`` MACRO parameter.

    Parameters
    ----------
    model_demand :
        Values from the ``DEMAND`` MESSAGE variable.
    demand_ref :
        Reference values to use for the period `ym1`.
    mapping_macro_sector :
        MACRO set of the same name; see :func:`.mapping_macro_sector`.
    ym1 :
        First pre-model period; see :func:`.ym1`.

    Returns
    -------
    pandas.DataFrame
        With the dimensions (node, sector, year).

    Raises
    ------
    RuntimeError
        If there zero or missing values in the computed data.
    """
    # - Use reference data for the pre-model period
    # - Map `model_demand` from MESSAGE (commodity, level) to MACRO sector
    return (
        pd.concat(
            [
                demand_ref.reset_index().assign(year=ym1),
                model_demand.merge(mapping_macro_sector, on=["commodity", "level"]),
            ],
            sort=True,
        )
        .set_index(["node", "sector", "year"])["value"]
        .pipe(_notna, "demand")
    )


def extrapolate(
    model_data: "DataFrame", mapping_macro_sector: "DataFrame", ym1: int
) -> "Series":
    r"""Extrapolate `model_data` to cover period `ym1`.

    The extrapolation is done by fitting :math:`y = b \times m ^ x`, i.e. with two
    parameters `b` and `m`. This is identical to the GROWTH() function in Microsoft
    Excel (
    https://support.microsoft.com/en-us/office/growth-function-541a91dc-3d5e-437d-b156-21324e68b80d
    ). Data are grouped on all other dimensions, and fitting/extrapolation is performed
    for each group.

    Returns
    -------
    pandas.Series
        The index does *not* have a ``year`` dimension; the data are implicitly for
        `ym1`.
    """
    from sys import version_info

    from scipy.optimize import curve_fit

    def f(x, b, m):
        """Compound growth function to fit."""
        return b * m**x

    def fitted_intercept(df: pd.DataFrame) -> float:
        """Fit `f` to the data, with value → x and year → y."""
        # Shift years so that ym1 = 0
        (b, m), _ = curve_fit(f, df["year"] - ym1, df["value"])
        return b  # The intercept at ym1 == b

    # Apply fitted_intercept to grouped data
    groupby_cols = set(model_data.columns) - {"year", "value"}
    apply_kwargs = {"include_groups": False} if version_info.minor > 8 else {}
    result = (
        model_data.groupby(list(groupby_cols))
        .apply(fitted_intercept, **apply_kwargs)
        .rename("value")
    )

    # Convert "commodity" and "level" to "sector"
    if "commodity" in model_data.columns:
        result = (
            result.reset_index()
            .merge(mapping_macro_sector, on=["commodity", "level"])
            .set_index(list(groupby_cols - {"commodity", "level"} | {"sector"}))[
                "value"
            ]
        )

    return result.pipe(_notna, "extrapolate")


def gdp0(gdp_calibrate, ym1: int) -> "Series":
    """Select GDP reference values from "gdp_calibrate"."""
    return gdp_calibrate.iloc[gdp_calibrate.index.isin([ym1], level="year")]


def growth(gdp_calibrate) -> "DataFrame":
    """Calculate GDP growth rates between model periods (MACRO parameter ``grow``)."""
    diff = gdp_calibrate.groupby(level="node").diff()
    years = sorted(gdp_calibrate.index.get_level_values("year").unique())
    dt = pd.Series(years, index=pd.Index(years, name="year")).diff()
    growth = (diff / gdp_calibrate + 1) ** (1 / dt) - 1
    growth.name = "value"
    return growth.dropna()


def macro_periods(demand: "Quantity", config: "DataFrame") -> set[int]:
    """Periods ("years") for the MACRO model.

    The intersection of those appearing in the `config` data and in the ``DEMAND``
    variable of the base scenario.
    """
    model_periods = set(demand.coords["y"].data)
    config_periods = set(config["year"].unique())
    if not model_periods & config_periods:
        raise RuntimeError(
            f"No intersection of model periods {model_periods} and config periods "
            f"{config_periods}"
        )
    return model_periods & config_periods


def mapping_macro_sector(config: "DataFrame") -> "DataFrame":
    """Data for the MACRO set ``mapping_macro_sector``."""
    return config[["sector", "commodity", "level"]].dropna().drop_duplicates()


def price(
    model_price: "DataFrame",
    price_ref: "DataFrame",
    mapping_macro_sector: "DataFrame",
    s: Structures,
    ym1: int,
) -> "DataFrame":
    """Prepare data for the ``price_MESSAGE`` MACRO parameter.

    Reads PRICE_COMMODITY from MESSAGEix, validates the data, and combines the data with
    a reference price specified for the base year of MACRO.

    Raises
    ------
    RuntimeError
        If there zero or missing values in PRICE_COMMODITY.

    Returns
    -------
    pandas.DataFrame
        Data of price per commodity, region, and level.
    """
    # Map from MESSAGE (commodity, level) to MACRO sector
    data = model_price.merge(mapping_macro_sector, on=["commodity", "level"])

    # Check for completeness of nodes, sectors
    _validate_data(None, data, s)
    # Check for completeness of years within nodes and sectors
    for (node, _), group_df in data.groupby(["node", "sector"]):
        if set(s.year) - set(group_df["year"]):
            error_message = "Missing data for some periods"
        elif np.isclose(group_df["value"], 0).any():
            error_message = "0-price found"
        else:
            continue

        log.info("\n" + data.to_string())
        raise RuntimeError(
            f"{error_message} in MESSAGE variable PRICE_COMMODITY for "
            f"commodity={group_df.commodity.unique()[0]!r}, node={node!r}."
        )

    # - Use row(s) for reference data for the pre-model period
    # - Set desired index columns
    # - Select "value" series, discarding other columns (incl. commodity, level, time)
    return (
        pd.concat([price_ref.reset_index().assign(year=ym1), data], sort=True)
        .set_index(["node", "sector", "year"])["value"]
        .pipe(_notna, "price")
    )


def rho(esub: "Series") -> "Series":
    """Calculate "rho" based on "esub", elasticity of substitution."""
    return (esub - 1) / esub


def total_cost(model_cost: "DataFrame", cost_ref: "DataFrame", ym1: int) -> "DataFrame":
    """Combine `model_cost` and `cost_ref` (reference year) data.

    Raises
    ------
    RuntimeError
        If NaN values in the cost data.

    Returns
    -------
    pandas.DataFrame
        Total cost of the system.

    """
    # - Use row(s) for reference data for the pre-model period.
    # - Divide data by 1000; this mirrors the R code used as a basis for this module
    #   FIXME determine if this is necessary and describe why
    # - Set desired index columns.
    # - Select "value" series, discarding other columns.
    return (
        pd.concat(
            [
                cost_ref.reset_index().assign(year=ym1),
                model_cost.assign(value=model_cost.value / 1e3),
            ],
            sort=True,
        )
        .set_index(["node", "year"])["value"]
        .pipe(_notna, "total_cost")
    )


def unique_set(column: str, df: "DataFrame") -> set:
    """A :class:`set` of the unique elements in `column` of `df`."""
    return set(df[column].dropna().unique())


def validate_transform(
    name: str, data: Mapping[str, "DataFrame"], s: Structures
) -> "Series":
    """Validate `df` as input data for `name`, and transform for further calculation."""
    try:
        df = data[name]
    except KeyError:
        raise KeyError(f"Missing input data table {name!r}")

    if name == "config":
        cols = ["node", "sector", "level", "commodity", "year"]
        missing = set(cols) - set(df.columns)
        if missing:
            raise KeyError(f"Missing config data for {missing!r}")
        for col in cols:
            if df[col].dropna().empty:
                raise ValueError(f"Config data for {col!r} is empty")
        return pd.Series()

    # Validate this parameter and retrieve the index columns/dimensions
    idx = _validate_data(name, df, s)

    # Store units of this parameter
    units = df["unit"].unique()
    assert 1 == len(units), f"Non-unique units for parameter {name}"
    # self.units[name] = units[0] # FIXME reenable

    try:
        # Discard data beyond the last MACRO year
        df = df.query(f"year <= {max(s.year)}")
    except Exception:  # pandas.errors.UndefinedVariableError; no "year" column
        pass

    # Series with multi-index
    return df.set_index(idx)["value"]


def _validate_data(name: Optional[str], df: "DataFrame", s: Structures) -> list:
    """Validate input `df` against `s` for MACRO parameter `name` calibration .

    Parameters
    ----------
    name : string
        MESSAGEix parameter name related to MACRO calibration. When reading
        data from Excel, these names are the Excel sheet names.
    df : Pandas DataFrame
        Data of each MACRO calibration parameter.
    s :
        Instance of :class:`.Structures`.

    Raises
    ------
    ValueError
        Assert if some required set elements missing in MACRO calibration data.

    Returns
    -------
    list of str
        Dimensions/index sets of the validated MESSAGEix parameter.
    """
    from .models import MACRO

    # Check required dimensions
    if name is None:
        dims: list[str] = []
    else:
        item_name = name.replace("_ref", "_MESSAGE")
        item = MACRO.items[item_name]
        dims = list(item.dims or item.coords)

        # For cost_ref, demand_ref, price_ref, only require one year's data, without a
        # "year" dimension
        if name.endswith("_ref"):
            dims.remove("year")

        diff = set(dims) - set(df.columns) - {"unit"}
        if diff:
            raise ValueError(f"Missing expected columns for {name}: {diff}")

    # Check required labels in keys
    for kind in "level", "node", "sector", "year":
        try:
            diff = getattr(s, kind) - set(df[kind])
        except KeyError:
            continue

        if diff:
            raise ValueError(f"Not all {kind}s included in {name} data: {diff}")

    return dims


def ym1(df: "Series", macro_periods: Collection[int]) -> int:
    """Period for MACRO initialization: "year minus-one".

    This is the period before the first period in the model horizon.

    Parameters
    ----------
    df :
        Data with a "year" level on a MultiIndex, usually "gdp_calibrate" in the input
        data.
    macro_periods :
        Computed by :func:`macro_periods`.

    Raises
    ------
    ValueError
        If `df` does not contain at least two periods before the model horizon. This
        much data is the minimum required to compute growth rates in the historical
        periods (MACRO's ``initializeyear``).
    """
    data_years_before_model = sorted(
        filter(lambda y: y < min(macro_periods), set(df.index.get_level_values("year")))
    )

    if len(data_years_before_model) < 2:
        raise ValueError(
            "Must provide two gdp_calibrate data points prior to the model horizon in "
            "order to calculate growth rates"
        )

    # Return the most recent period PRIOR to the model horizon
    return max(data_years_before_model)


# API methods for other code


def add_model_data(
    base: "Scenario", clone: "Scenario", data: Union[Mapping, os.PathLike]
) -> None:
    """Calculate and add MACRO structure and data to `clone`.

    Parameters
    ----------
    base : .Scenario
        Base scenario with a solution.
    clone : .Scenario
        Clone of base scenario for adding calibration parameters.
    data : dict
        Data for calibration.
    """
    c2 = prepare_computer(base, clone, data)
    for k in "add structure", "add data":
        # print(c2.describe(k))  # For debugging
        c2.get(k)


def calibrate(s, check_convergence: bool = True, **kwargs):
    """Calibrate a MESSAGEix scenario to parameters of MACRO.

    Parameters
    ----------
    s : .Scenario
        MESSAGEix scenario with calibration data.
    check_convergence : bool, optional
        Test is MACRO-calibrated scenario converges in one iteration.
    **kwargs :
        Keyword arguments passed to meth:`message_ix.Scenario.solve`.

    Raises
    ------
    RuntimeError
        If calibrated scenario solves in more than one iteration.

    Returns
    -------
    s : message_ix.Scenario()
        MACRO-calibrated scenario.

    """
    # Solve MACRO standalone
    gams_args = ["LogOption=2"]  # pass everything to log file
    s.solve(
        model="MACRO",
        var_list=["N_ITER", "MAX_ITER", "aeei_calibrate", "grow_calibrate"],
        gams_args=gams_args,
    )

    n_iter = s.var("N_ITER")["lvl"]
    max_iter = s.var("MAX_ITER")["lvl"]
    log.info(f"MACRO converged after {n_iter} of a maximum of {max_iter} iterations")

    units = s.par("grow")["unit"].unique()
    assert 1 == len(units), "Non-unique units for 'grow'"

    # Get out calibrated values
    data = {}
    for name in "aeei", "grow":
        data[name] = (
            s.var(f"{name}_calibrate")
            .rename(columns={"lvl": "value"})
            .drop("mrg", axis=1)
            .assign(unit=units[0])
        )

    # Update calibrated value parameters
    s.remove_solution()
    with s.transact("Update MACRO values after calibration"):
        s.add_par("aeei", data["aeei"])
        s.add_par("grow", data["grow"])
    s.set_as_default()

    # Test to make sure number of iterations is 1
    if check_convergence:
        test = s.clone(scenario=f"{s.scenario} test to confirm MACRO converges")
        kwargs.setdefault("gams_args", gams_args)
        test.solve(model="MESSAGE-MACRO", var_list=["N_ITER"], **kwargs)
        test.set_as_default()

        n_iter = test.var("N_ITER")["lvl"]
        if n_iter > 1:
            raise RuntimeError(f"Number of iterations after calibration {n_iter} > 1")

    return s


def prepare_computer(
    base: "Scenario",
    target: Optional["Scenario"] = None,
    data: Union[Mapping, os.PathLike, None] = None,
) -> "genno.Computer":
    """Prepare a :class:`.Reporter` to perform MACRO calibration calculations.

    Parameters
    ----------
    base : message_ix.Scenario
        Must have a stored solution.
    target : message_ix.Scenario
        Scenario to which to add computed data.
    data : dict or os.PathLike
        If :class:`~os.PathLike`, the path to an Excel file containing parameter data,
        one per sheet. If :class:`dict`, a mapping from parameter names to data frames.

    Raises
    ------
    ValueError
        if any of the require parameters for MACRO calibration (:data:`INPUT_DATA`) is
        missing.

    See also
    --------
    :ref:`macro-input-data`
    """
    from ixmp.backend import ItemType

    from .models import MACRO

    if not base.has_solution():
        raise RuntimeError("Scenario must have a solution to add MACRO")

    c = Reporter.from_scenario(base)

    # Also add the target scenario, if any
    c.add("target", target)

    # "data" key: either literal data, or a task to read it from file
    if isinstance(data, Mapping):
        c.add("data", data)
    else:
        # Handle a file path
        try:
            assert data is not None
            data_path = Path(data)
        except (AssertionError, TypeError):
            raise TypeError(f"neither a dict nor a valid path: {data}")
        else:
            data = dict()

        if not data_path.exists() or data_path.suffix != ".xlsx":
            raise ValueError(f"not an Excel data file: {data_path}")

        c.add(
            "data",
            partial(pd.read_excel, sheet_name=None, engine="openpyxl"),
            data_path,
        )

    # Configuration
    c.add("config::macro", itemgetter("config"), "data")

    # Structure information derived from `config`
    mms = c.add("mapping_macro_sector", mapping_macro_sector, "config::macro")
    c.add("level::macro", partial(unique_set, "level"), mms)
    c.add("node::macro", partial(unique_set, "node"), "config::macro")
    c.add("sector::macro", partial(unique_set, "sector"), mms)

    # Periods in `DEMAND` variable and also in `config`
    c.add("year::macro", macro_periods, "DEMAND:y", "config::macro")

    # Collect structure information in a class for easier reference
    c.add("_s", Structures, *[f"{n}::macro" for n in "level node sector year".split()])

    # Collection of keys to run to check input data formats
    checks = []

    # Add keys to retrieve, validate, and transform input data
    for name in INPUT_DATA:
        # Extract a single data frame from the dict, validate, and transform
        c.add(name, partial(validate_transform, name), "data", "_s")
        checks.append(name)

    # First year in `data` before model horizon; derived from "gdp_calibrate"
    c.add("ym1", ym1, "gdp_calibrate", "year::macro")
    checks.append("ym1")

    # Also check config
    c.add("check config", partial(validate_transform, "config"), "data", "_s")
    checks.append("check config")

    # "Clean" data from some MESSAGE variables for use in MACRO calibration functions
    cleaned = {}  # Keys for the cleaned data
    for name in "COST_NODAL_NET", "DEMAND", "PRICE_COMMODITY":
        key = c.full_key(name)
        assert isinstance(key, Key)
        cleaned[name] = c.add(key.add_tag("macro"), clean_model_data, key, "_s")

        # Configuration key for corresponding reference data
        k_ref = name.split("_")[0].lower() + "_ref"

        # Maybe extrapolate reference data from variable data
        if len(data) and k_ref not in data:
            log.info(f"Data for {k_ref} will be extrapolated from {cleaned[name]}")
            c.add(k_ref, extrapolate, cleaned[name], mms, "ym1")

    # Main calculation methods. Formerly these were given by Calculate.derive_data().
    c.add("grow", growth, "gdp_calibrate")
    c.add("rho", rho, "esub")
    c.add("historical_gdp", gdp0, "gdp_calibrate", "ym1")
    # Capital in the base period (``k0``). This is the product of the capital to GDP
    # ratio (`kgdp`) and the reference GDP (`historical_gdp`).
    c.add("k0", mul, "historical_gdp", "kgdp")
    c.add("cost_MESSAGE", total_cost, cleaned["COST_NODAL_NET"], "cost_ref", "ym1")
    c.add(
        "price_MESSAGE",
        price,
        cleaned["PRICE_COMMODITY"],
        "price_ref",
        mms,
        "_s",
        "ym1",
    )
    c.add("demand_MESSAGE", demand, cleaned["DEMAND"], "demand_ref", mms, "ym1")
    c.add("prfconst", bconst, "demand_ref", "historical_gdp", "price_ref", "rho")
    c.add(
        "lakl", aconst, "prfconst", "demand_ref", "historical_gdp", "k0", "kpvs", "rho"
    )

    # Add the data to the scenario for each MACRO parameter. Some of these are directly
    # from the input (also appearing in VERIFY_INPUT_DATA); others are from calculations
    # above.
    added = []  # List of keys for tasks that add data
    for item in filter(lambda i: i.type == ItemType.PAR, MACRO.items.values()):
        name = item.name
        added.append(
            c.add(f"add {name}", partial(add_par, name=name), "target", name, "ym1")
        )

    # Run all checks
    c.add("check all", checks)

    # Compute and add all data to "target"
    c.add("add data", added)

    # Add structures to "target"
    c.add("add structure", add_structure, "target", mms, "_s", "ym1")

    # commented: used to generate the diagram in the documentation
    # c.visualize("macro-calibrate.svg", key="add data")

    return c
