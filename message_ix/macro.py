import logging
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


EXPERIMENTAL = """
======================= WARNING =======================

You are using *experimental*, incomplete features from
`message_ix.macro`—please exercise caution. Read more:
- https://github.com/iiasa/message_ix/issues/315
- https://github.com/iiasa/message_ix/issues/317
- https://github.com/iiasa/message_ix/issues/318
- https://github.com/iiasa/message_ix/issues/319
- https://github.com/iiasa/message_ix/issues/320

======================================================
"""

# Pairing MACRO calibration parameters with variable names used in this module
DATA_KEY = dict(
    cost_MESSAGE="total_cost",
    demand_MESSAGE="demand",
    grow="growth",
    historical_gdp="gdp0",
    lakl="aconst",
    prfconst="bconst",
    price_MESSAGE="price",
)

# Pairing MACRO calibration parameters with input data for consistency of units
UNITS = dict(
    cost_MESSAGE="cost_ref",
    demand_MESSAGE="demand_ref",
    historical_gdp="gdp_calibrate",
    price_MESSAGE="price_ref",
)

# ixmp items (sets, parameters, variables, and equations) in MACRO.
MACRO_ITEMS = dict(
    sector=dict(ix_type="set"),
    mapping_macro_sector=dict(ix_type="set", idx_sets=["sector", "commodity", "level"]),
    MERtoPPP=dict(ix_type="par", idx_sets=["node", "year"]),
    aeei=dict(ix_type="par", idx_sets=["node", "sector", "year"]),
    cost_MESSAGE=dict(ix_type="par", idx_sets=["node", "year"]),
    demand_MESSAGE=dict(ix_type="par", idx_sets=["node", "sector", "year"]),
    depr=dict(ix_type="par", idx_sets=["node"]),
    drate=dict(ix_type="par", idx_sets=["node"]),
    esub=dict(ix_type="par", idx_sets=["node"]),
    gdp_calibrate=dict(ix_type="par", idx_sets=["node", "year"]),
    grow=dict(ix_type="par", idx_sets=["node", "year"]),
    historical_gdp=dict(ix_type="par", idx_sets=["node", "year"]),
    kgdp=dict(ix_type="par", idx_sets=["node"]),
    kpvs=dict(ix_type="par", idx_sets=["node"]),
    lakl=dict(ix_type="par", idx_sets=["node"]),
    lotol=dict(ix_type="par", idx_sets=["node"]),
    prfconst=dict(ix_type="par", idx_sets=["node", "sector"]),
    price_MESSAGE=dict(ix_type="par", idx_sets=["node", "sector", "year"]),
    # Total consumption
    C=dict(ix_type="var", idx_sets=["node", "year"]),
    COST_NODAL=dict(ix_type="var", idx_sets=["node", "year"]),
    # Net of trade and emissions costs
    COST_NODAL_NET=dict(ix_type="var", idx_sets=["node", "year"]),
    DEMAND=dict(ix_type="var", idx_sets=["node", "commodity", "level", "year", "time"]),
    EC=dict(ix_type="var", idx_sets=["node", "year"]),
    GDP=dict(ix_type="var", idx_sets=["node", "year"]),
    # Total investment
    I=dict(ix_type="var", idx_sets=["node", "year"]),  # noqa: E741
    K=dict(ix_type="var", idx_sets=["node", "year"]),
    KN=dict(ix_type="var", idx_sets=["node", "year"]),
    MAX_ITER=dict(ix_type="var", idx_sets=None),
    N_ITER=dict(ix_type="var", idx_sets=None),
    NEWENE=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    PHYSENE=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    PRICE=dict(ix_type="var", idx_sets=["node", "commodity", "level", "year", "time"]),
    PRODENE=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    UTILITY=dict(ix_type="var", idx_sets=None),
    Y=dict(ix_type="var", idx_sets=["node", "year"]),
    YN=dict(ix_type="var", idx_sets=["node", "year"]),
    aeei_calibrate=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    grow_calibrate=dict(ix_type="var", idx_sets=["node", "year"]),
    COST_ACCOUNTING_NODAL=dict(ix_type="equ", idx_sets=["node", "year"]),
)

# Required index sets when deriving MACRO calibration parameters
MACRO_DATA_FOR_DERIVATION = {
    "cost_ref": ["node"],
    "demand_ref": ["node", "sector"],
    "price_ref": ["node", "sector"],
}

# MACRO calibration parameters to be verified when reading the input data
VERIFY_INPUT_DATA = [
    "price_ref",
    "lotol",
    "esub",
    "drate",
    "depr",
    "kpvs",
    "kgdp",
    "gdp_calibrate",
    "aeei",
    "cost_ref",
    "demand_ref",
    "MERtoPPP",
]


def _validate_data(name, df, nodes, sectors, levels, years):
    """
    Validate the input data for MACRO calibration to ensure the
    format is compatibale with MESSAGEix.

    Parameters
    ----------
    name : string
        MESSAGEix parameter name related to MACRO calibration. When reading
        data from Excel, these names are the Excel sheet names.
    df : Pandas DataFrame
        Data of each MACRO calibration parameter.
    nodes : list
        List of nodes for MACRO calibration.
    sectors : list
        List of sectors for MACRO calibration.
    levels : list
        List of levels for MACRO calibration.
    years : list
        List of model years for which MACRO calibration is applied.

    Raises
    ------
    ValueError
        Assert if some required set elements missing in MACRO calibration data.

    Returns
    -------
    cols : List
        Index sets of the validated MESSAGEix parameter.

    """

    def validate(kind, values, df):
        if kind not in df:
            return

        diff = set(values) - set(df[kind])
        if diff:
            raise ValueError(f"Not all {kind}s included in {name} data: {diff}")

    # check required columns
    if name in MACRO_DATA_FOR_DERIVATION:
        cols = MACRO_DATA_FOR_DERIVATION[name]
    else:
        cols = MACRO_ITEMS[name]["idx_sets"]
    col_diff = set(cols + ["unit"]) - set(df.columns)
    if col_diff:
        raise ValueError(f"Missing expected columns for {name}: {col_diff}")

    # check required column values
    checks = (
        ("node", nodes),
        ("sector", sectors),
        ("year", years),
        ("level", levels),
    )

    for kind, values in checks:
        validate(kind, values, df)

    return cols


class Calculate:
    """Perform and store MACRO calibration calculations.

    Parameters
    ----------
    s : message_ix.Scenario
        Must have a stored solution.
    data : dict (str -> pd.DataFrame) or os.PathLike
        If :class:`.PathLike`, the path to an Excel file containing parameter data, one
        per sheet. If :class:`dict`, a dictionary mapping parameter names to data
        frames.
    """

    def __init__(self, s, data):
        self.s = s
        self.units = {}

        if isinstance(data, Mapping):
            self.data = data
        else:
            # Handle a file path
            try:
                data_path = Path(data)
            except TypeError:
                raise TypeError(f"neither a dict nor a valid path: {data}")

            if not data_path.exists() or data_path.suffix != ".xlsx":
                raise ValueError(f"not an Excel data file: {data_path}")

            self.data = pd.read_excel(data_path, sheet_name=None, engine="openpyxl")

        if not s.has_solution():
            raise RuntimeError("Scenario must have a solution to add MACRO")
        # check if "config" exists and has required information
        if "config" not in self.data:
            raise KeyError("Missing config in input data")
        else:
            config = self.data["config"]
            for key in ["node", "sector", "level", "commodity", "year"]:
                try:
                    config[key]
                except KeyError:
                    raise KeyError('Missing config data for "{}"'.format(key))
                else:
                    if config[key].dropna().empty:
                        raise ValueError('Config data for "{}" is empty'.format(key))

        demand = s.var("DEMAND")
        self.years = set(demand["year"])

    def read_data(self):
        """Check and validate structure of data in ``self.data``.

        Raises
        ------
        ValueError
            if any of the require parameters for MACRO calibration
            (:data:`VERIFY_INPUT_DATA`) is missing.
        """
        # Store sets (node, sector, level) and mappings based on configuration
        self.nodes = set(self.data["config"]["node"].dropna())
        self.sectors = set(self.data["config"]["sector"].dropna())
        self.levels = set(self.data["config"]["level"].dropna())
        self.sector_mapping = self.data["config"]

        # Filter, keeping only years that are included in the model results
        yrs = set(self.data["config"]["year"].dropna())
        self.years = [x for x in yrs if x in self.years]
        max_macro_year = max(self.years)

        # Ensure input data are complete
        missing = set(VERIFY_INPUT_DATA) - set(self.data)
        if missing:
            raise ValueError(f"Missing required input data: {missing}")

        # Process each parameter
        for name, df in self.data.items():
            if name == "config":
                # Configuration was processed above
                continue

            # Validate this parameter, retrieving the index columns/dimensions
            idx = _validate_data(
                name, df, self.nodes, self.sectors, self.levels, self.years
            )

            # Store units of this parameter
            units = df["unit"].unique()
            assert 1 == len(units), f"Non-unique units for parameter {name}"
            self.units[name] = units[0]

            if "year" in df.columns:
                # Discard data beyond `max_macro_year`
                df = df.loc[df["year"] <= max_macro_year].copy()

            if name == "gdp_calibrate":
                # Check that gdp_calibrate has at least 2 periods before the model
                # horizon. This is required in order to compute growth rates in the
                # historical periods (MACRO's "initializeyear")
                data_years_before_model = sorted(
                    filter(lambda y: y < min(self.years), df["year"].unique())
                )
                if len(data_years_before_model) < 2:
                    raise ValueError(
                        "Must provide two gdp_calibrate data points prior to the model "
                        "horizon in order to calculate growth rates"
                    )

                # Store init_year, the most recent period PRIOR to the model horizon
                self.init_year = max(data_years_before_model)

            # Store as pd.Series with multi-index
            self.data[name] = df.set_index(idx)["value"]

    def _clean_model_data(self, data):
        """
        Clean input data for MACRO calibration by slicing relevant data.

        Parameters
        ----------
        data : pandas DataFrame
            Input data of MESSAGEix MACRO calibration parameters.

        Returns
        -------
        data : pandas DataFrame
            Required data of MESSAGEix MACRO calibration parameters.

        """
        if "node" in data:
            data = data[data["node"].isin(self.nodes)]
        if "commodity" in data:
            data = data[data["commodity"].isin(self.sectors)]
        if "year" in data:
            data = data[data["year"].isin(self.years)]
        if "level" in data:
            data = data[data["level"].isin(self.levels)]
        return data

    def derive_data(self):
        """
        Calculate all necessary derived data, adding to self.data.
        (This is done through method chaining, the bottom of which is aconst()
        # NB this means it could be rewritten using reporting)

        """
        self._growth()
        self._rho()
        self._gdp0()
        self._k0()
        self._total_cost()
        self._price()
        self._demand()
        self._bconst()
        self._aconst()

    @lru_cache()
    def _growth(self):
        """
        Calculate GDP growth rates between model periods.

        Returns
        -------
        pandas DataFrame
            Calculated "growth" parameter.

        """
        gdp = self.data["gdp_calibrate"]
        diff = gdp.groupby(level="node").diff()
        years = sorted(gdp.index.get_level_values("year").unique())
        dt = pd.Series(years, index=pd.Index(years, name="year")).diff()
        growth = (diff / gdp + 1) ** (1 / dt) - 1
        growth.name = "value"
        self.data["growth"] = growth.dropna()
        return self.data["growth"]

    @lru_cache()
    def _rho(self):
        """
        Calculate "rho" based on "esub", elasticity of substitution, for MACRO
        calibration.

        Returns
        -------
        pandas Series
            Calculated "rho" parameter.

        """
        esub = self.data["esub"]
        self.data["rho"] = (esub - 1) / esub
        return self.data["rho"]

    @lru_cache()
    def _gdp0(self):
        """
        Derive GDP reference values from "gdp_calibrate" for MACRO calibration.

        Returns
        -------
        pandas Series
            Calculated "gdp0" parameter.

        """
        gdp = self.data["gdp_calibrate"]
        gdp0 = gdp.iloc[gdp.index.isin([self.init_year], level="year")]
        self.data["gdp0"] = gdp0
        return self.data["gdp0"]

    @lru_cache()
    def _k0(self):
        """
        Derive initial capital to GDP ratio in the base year ("kgdp") from
        reference GDP.

        Returns
        -------
        pandas Series
            Calculated "k0" parameter.
        """
        kgdp = self.data["kgdp"]
        gdp0 = self._gdp0()
        self.data["k0"] = kgdp * gdp0
        return self.data["k0"]

    @lru_cache()
    def _total_cost(self):
        """
        Extract total systems cost from a solution of MESSAGEix and combine them
        with the cost values for the reference year.

        Raises
        ------
        RuntimeError
            If NaN values in the cost data.

        Returns
        -------
        total_cost : pandas DataFrame
            Total cost of the system.

        """
        # read from scenario
        idx = ["node", "year"]
        model_cost = self._clean_model_data(self.s.var("COST_NODAL_NET"))
        model_cost.rename(columns={"lvl": "value"}, inplace=True)
        model_cost = model_cost[idx + ["value"]]
        # TODO: in the R code, this value is divided by 1000
        # do we need to do that here?!!?
        model_cost["value"] /= 1e3
        # get data provided in init year from data
        cost_ref = self.data["cost_ref"].reset_index()
        cost_ref["year"] = self.init_year
        # combine into one value
        total_cost = pd.concat([cost_ref, model_cost], sort=True).set_index(idx)[
            "value"
        ]
        if total_cost.isnull().any():
            raise RuntimeError("NaN values found in total_cost calculation")
        self.data["total_cost"] = total_cost
        return total_cost

    @lru_cache()
    def _price(self):
        """
        Reads PRICE_COMMODITY from MESSAGEix, validates the data, and combines
        the data with a reference price specified for the base year of MACRO.

        Raises
        ------
        RuntimeError
            If there zero or missing values in PRICE_COMMODITY.

        Returns
        -------
        price : pandas DataFrame
            Data of price per commodity, region, and level.

        """
        # read from scenario
        idx = ["node", "sector", "year"]
        model_price = self._clean_model_data(
            self.s.var("PRICE_COMMODITY", filters={"level": self.levels})
        )
        for node, com in product(self.nodes, self.sectors):
            test_price = model_price.loc[
                (model_price["node"] == node) & (model_price["commodity"] == com)
            ]
            missing = len(test_price["year"]) < len(self.years)
            if np.isclose(test_price["lvl"], 0).any() or missing:
                msg = (
                    "0-price found in MESSAGE variable PRICE_COMMODITY"
                    ' for commodity "{}" in node "{}".'
                ).format(com, node)
                raise RuntimeError(msg)
        model_price.rename(
            columns={"lvl": "value", "commodity": "sector"}, inplace=True
        )
        model_price = model_price[idx + ["value"]]

        # get data provided in init year from data
        price_ref = self.data["price_ref"].reset_index()
        price_ref["year"] = self.init_year
        # combine into one value
        price = pd.concat([price_ref, model_price], sort=True).set_index(idx)["value"]
        if price.isnull().any():
            raise RuntimeError("NaN values found in price calculation")
        self.data["price"] = price
        return price

    @lru_cache()
    def _demand(self):
        """
        Reads DEMAND from MESSAGEix, validates the data, and combines
        the data with a reference demand specified for the base year of MACRO.

        Raises
        ------
        RuntimeError
            If there zero or missing values in DEMAND.

        Returns
        -------
        price : pandas DataFrame
            Data of demand per commodity, region, and level.

        """
        # read from scenario
        idx = ["node", "sector", "year"]
        model_demand = self._clean_model_data(
            self.s.var("DEMAND", filters={"level": self.levels})
        )
        model_demand.rename(
            columns={"lvl": "value", "commodity": "sector"}, inplace=True
        )
        model_demand = model_demand[idx + ["value"]]
        # get data provided in init year from data
        demand_ref = self.data["demand_ref"].reset_index()
        demand_ref["year"] = self.init_year
        # combine into one value
        demand = pd.concat([demand_ref, model_demand], sort=True).set_index(idx)[
            "value"
        ]
        if demand.isnull().any():
            raise RuntimeError("NaN values found in demand calculation")
        self.data["demand"] = demand
        return demand

    @lru_cache()
    def _bconst(self):
        """
        Calculate production function coefficient of different energy sectors ("bcosnt")
        for MACRO calibration (specified as "prfconst" in GAMS formulation).

        Returns
        -------
        pandas Series
            Data as initial value for parameter "prfconst".

        """
        price_ref = self.data["price_ref"]
        demand_ref = self.data["demand_ref"]
        rho = self._rho()
        gdp0 = self._gdp0()
        # TODO: automatically get the units here!!
        bconst = price_ref / 1e3 * (gdp0 / demand_ref) ** (rho - 1)
        self.data["bconst"] = bconst
        return self.data["bconst"]

    @lru_cache()
    def _aconst(self):
        """
        Calculate production function coefficient of capital and labor ("aconst"),
        for MACRO calibration (specified as "lakl" in GAMS formulation).

        Returns
        -------
        pandas Series
            Data as initial value for parameter "lakl".

        """
        bconst = self._bconst()
        demand_ref = self.data["demand_ref"]
        rho = self._rho()
        gdp0 = self._gdp0()
        k0 = self._k0()
        kpvs = self.data["kpvs"]
        partmp = (bconst * demand_ref**rho).groupby(level="node").sum()
        # TODO: automatically get the units here!!
        aconst = ((gdp0 / 1e3) ** rho - partmp) / (k0 / 1e3) ** (rho * kpvs)
        # want the series to only have index of node
        self.data["aconst"] = aconst.reset_index(level="year", drop=True)
        return self.data["aconst"]


def add_model_data(base, clone, data):
    """Calculate required parameters and add data to `clone`.

    Parameters
    ----------
    base : message_ix.Scenario()
        Base scenario with a solution.
    clone : message_ix.Scenario()
        Clone of base scenario for adding calibration parameters.
    data : dict
        Data of calibration.

    Raises
    ------
    type
        If the data format is not compatible with MESSAGEix parameters.
    """
    c = Calculate(base, data)
    c.read_data()
    c.derive_data()

    # Removing old initializeyear_macro before adding new one
    cat = clone.set("cat_year", {"type_year": "initializeyear_macro"})
    if not cat.empty:
        clone.remove_set("cat_year", cat)

    # Add temporal set structure
    clone.add_set("type_year", "initializeyear_macro")
    clone.add_set("cat_year", ["initializeyear_macro", c.init_year])

    # Add nodal set structure
    clone.add_set("type_node", "economy")
    for n in c.nodes:
        clone.add_set("cat_node", ["economy", n])

    # Obtain the mapping data frame inlcuding sector, level and commodity
    sector_mapping_df = c.sector_mapping[["sector", "commodity", "level"]].dropna()

    # Add sectoral set structure
    # Itearte throguh rows in the mapping data frame

    for i in sector_mapping_df.index:
        sec = sector_mapping_df.iloc[i, sector_mapping_df.columns.get_loc("sector")]
        com = sector_mapping_df.iloc[i, sector_mapping_df.columns.get_loc("commodity")]
        lvl = sector_mapping_df.iloc[i, sector_mapping_df.columns.get_loc("level")]
        clone.add_set("sector", sec)
        clone.add_set("mapping_macro_sector", [sec, com, lvl])

    # Add parameters
    for name, info in MACRO_ITEMS.items():
        if info["ix_type"] != "par":
            continue

        try:
            key = DATA_KEY.get(name, name)

            # Retrieve data; assign units
            data = (
                c.data[key]
                .reset_index()
                .assign(unit=c.units.get(UNITS.get(name, name), "-"))
            )

            # Remove data prior to the MACRO initialization year so as not to add this
            # to the scenario
            if "year" in data:
                data = data[data["year"] >= c.init_year]

            clone.add_par(name, data)
        except Exception as e:
            raise type(e)(f"Error in adding parameter {name}\n{e}")


def calibrate(s, check_convergence=True, **kwargs):
    """
    Calibrates a MESSAGEix scenario to parameters of MACRO

    Parameters
    ----------
    s : message_ix.Scenario()
        MESSAGEix scenario with calibration data.
    check_convergence : bool, optional, default: True
        Test is MACRO-calibrated scenario converges in one iteration.
    **kwargs : keyword arguments
        To be passed to message_ix.Scenario.solve().

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
    var_list = ["N_ITER", "MAX_ITER", "aeei_calibrate", "grow_calibrate"]
    gams_args = ["LogOption=2"]  # pass everything to log file
    s.solve(model="MACRO", var_list=var_list, gams_args=gams_args)
    n_iter = s.var("N_ITER")["lvl"]
    max_iter = s.var("MAX_ITER")["lvl"]
    msg = "MACRO converged after {} of a maximum of {} iterations"
    log.info(msg.format(n_iter, max_iter))

    units = s.par("grow")["unit"].unique()
    assert 1 == len(units), "Non-unique units for 'grow'"

    # Get out calibrated values
    aeei = (
        s.var("aeei_calibrate")
        .rename(columns={"lvl": "value"})
        .drop("mrg", axis=1)
        .assign(unit=units[0])
    )
    grow = (
        s.var("grow_calibrate")
        .rename(columns={"lvl": "value"})
        .drop("mrg", axis=1)
        .assign(unit=units[0])
    )

    # Update calibrated value parameters
    s.remove_solution()
    s.check_out()
    s.add_par("aeei", aeei)
    s.add_par("grow", grow)
    s.commit("Updating MACRO values after calibration")
    s.set_as_default()

    # test to make sure number of iterations is 1
    if check_convergence:
        test = s.clone(s.model, "test to confirm MACRO converges")
        var_list = ["N_ITER"]
        kwargs["gams_args"] = kwargs.get("gams_args", gams_args)
        test.solve(model="MESSAGE-MACRO", var_list=var_list, **kwargs)
        test.set_as_default()

        n_iter = test.var("N_ITER")["lvl"]
        if n_iter > 1:
            raise RuntimeError(f"Number of iterations after calibration {n_iter} is >1")

    return s
