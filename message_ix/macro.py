import logging
from functools import lru_cache
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


# TODO all demands and prices are assumed to be on 'useful' level, need to extend this
#      to support others

DATA_KEY = dict(
    cost_MESSAGE="total_cost",
    demand_MESSAGE="demand",
    grow="growth",
    historical_gdp="gdp0",
    lakl="aconst",
    prfconst="bconst",
    price_MESSAGE="price",
)

UNITS = dict(
    cost_MESSAGE="G$",
    demand_MESSAGE="GWa",
    gdp_calibrate="T$",
    historical_gdp="T$",
    price_MESSAGE="USD/kWa",
    # Used in calibrate()
    aeei="-",
    grow="-",
)

#: ixmp items (sets, parameters, variables, and equations) in MACRO.
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
    # commented: see description in models.py.
    # PRICE_COMMODITY=dict(
    #     ix_type="var", idx_sets=["node", "commodity", "level", "year", "time"]
    # ),
    # PRICE_EMISSION=dict(
    #     ix_type="var", idx_sets=["node", "type_emission", "type_tec", "y"]
    # ),
    PRODENE=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    UTILITY=dict(ix_type="var", idx_sets=None),
    Y=dict(ix_type="var", idx_sets=["node", "year"]),
    YN=dict(ix_type="var", idx_sets=["node", "year"]),
    aeei_calibrate=dict(ix_type="var", idx_sets=["node", "sector", "year"]),
    grow_calibrate=dict(ix_type="var", idx_sets=["node", "year"]),
    COST_ACCOUNTING_NODAL=dict(ix_type="equ", idx_sets=["node", "year"]),
)


MACRO_DATA_FOR_DERIVATION = {
    "cost_ref": ["node"],
    "demand_ref": ["node", "sector"],
    "price_ref": ["node", "sector"],
}

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


def _validate_data(name, df, nodes, sectors, years):
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
    # TODO: cols += ['unit'] ?
    col_diff = set(cols) - set(df.columns)
    if col_diff:
        raise ValueError(f"Missing expected columns for {name}: {col_diff}")

    # check required column values
    checks = (
        ("node", nodes),
        ("sector", sectors),
        ("year", years),
    )

    for kind, values in checks:
        validate(kind, values, df)

    return cols


class Calculate:
    """Perform and store MACRO calibration calculations.

    The :class:`.Scenario` *s* must:

    - have a solution;
    - have demand on the level 'useful'.

    s : .Scenario
    data : dict (str -> pd.DataFrame) or os.PathLike
        If :class:`.PathLike`, the path to an Excel file containing parameter data, one
        per sheet. If :class:`dict`, a dictionary mapping parameter names to data
        frames.
    """

    # TODO add comments
    # TODO add docstrings
    def __init__(self, s, data):
        self.s = s

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

        demand = s.var("DEMAND", filters={"level": "useful"})
        self.nodes = set(demand["node"].unique())
        self.sectors = set(demand["commodity"].unique())
        self.years = set(demand["year"].unique())

    def read_data(self):
        if "config" in self.data:
            # users may remove certain nodes and sectors from the MACRO set
            # definitions
            config = self.data["config"]
            self.nodes -= set(config.get("ignore_nodes", []))
            self.sectors -= set(config.get("ignore_sectors", []))

        par_diff = set(VERIFY_INPUT_DATA) - set(self.data)
        if par_diff:
            raise ValueError(f"Missing required input data: {par_diff}")

        for name in self.data:
            # no need to validate configuration, it was processed above
            if name == "config":
                continue
            idx = _validate_data(
                name, self.data[name], self.nodes, self.sectors, self.years
            )
            self.data[name] = self.data[name].set_index(idx)["value"]

        # special check for gdp_calibrate - it must have at minimum two years
        # prior to the model horizon in order to compute growth rates in the
        # historical period (MACRO's "initializeyear")
        data_years = self.data["gdp_calibrate"].index.get_level_values("year")
        min_year_model = min(self.years)
        data_years_before_model = data_years[data_years < min_year_model]
        if len(data_years_before_model) < 2:
            raise ValueError(
                "Must provide two gdp_calibrate data points prior to the modeling "
                "period in order to calculate growth rates"
            )
        # init year is most recent period PRIOR to the modeled period
        self.init_year = max(data_years_before_model)
        # base year is first model period
        self.base_year = min_year_model

    def _clean_model_data(self, data):
        if "node" in data:
            data = data[data["node"].isin(self.nodes)]
        if "commodity" in data:
            data = data[data["commodity"].isin(self.sectors)]
        if "year" in data:
            data = data[data["year"].isin(self.years)]
        return data

    def derive_data(self):
        # calculate all necessary derived data, adding to self.data this is
        # done through method chaining, the bottom of which is aconst()
        # NB this means it could be rewritten using reporting
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
        esub = self.data["esub"]
        self.data["rho"] = (esub - 1) / esub
        return self.data["rho"]

    @lru_cache()
    def _gdp0(self):
        gdp = self.data["gdp_calibrate"]
        gdp0 = gdp.iloc[gdp.index.isin([self.init_year], level="year")]
        self.data["gdp0"] = gdp0
        return self.data["gdp0"]

    @lru_cache()
    def _k0(self):
        kgdp = self.data["kgdp"]
        gdp0 = self._gdp0()
        self.data["k0"] = kgdp * gdp0
        return self.data["k0"]

    @lru_cache()
    def _total_cost(self):
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
        total_cost = pd.concat([cost_ref, model_cost]).set_index(idx)["value"]
        if total_cost.isnull().any():
            raise RuntimeError("NaN values found in total_cost calculation")
        self.data["total_cost"] = total_cost
        return total_cost

    @lru_cache()
    def _price(self):
        # read from scenario
        idx = ["node", "sector", "year"]
        model_price = self._clean_model_data(
            self.s.var("PRICE_COMMODITY", filters={"level": "useful"})
        )
        if np.isclose(model_price["lvl"], 0).any():  # pragma: no cover
            # TODO this needs a test
            raise RuntimeError("0-price found in MESSAGE variable PRICE_COMMODITY")
        model_price.rename(
            columns={"lvl": "value", "commodity": "sector"}, inplace=True
        )
        model_price = model_price[idx + ["value"]]

        # get data provided in init year from data
        price_ref = self.data["price_ref"].reset_index()
        price_ref["year"] = self.init_year
        # combine into one value
        price = pd.concat([price_ref, model_price]).set_index(idx)["value"]
        if price.isnull().any():
            raise RuntimeError("NaN values found in price calculation")
        self.data["price"] = price
        return price

    @lru_cache()
    def _demand(self):
        # read from scenario
        idx = ["node", "sector", "year"]
        model_demand = self._clean_model_data(
            self.s.var("DEMAND", filters={"level": "useful"})
        )
        model_demand.rename(
            columns={"lvl": "value", "commodity": "sector"}, inplace=True
        )
        model_demand = model_demand[idx + ["value"]]
        # get data provided in init year from data
        demand_ref = self.data["demand_ref"].reset_index()
        demand_ref["year"] = self.init_year
        # combine into one value
        demand = pd.concat([demand_ref, model_demand]).set_index(idx)["value"]
        if demand.isnull().any():
            raise RuntimeError("NaN values found in demand calculation")
        self.data["demand"] = demand
        return demand

    @lru_cache()
    def _bconst(self):
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
        bconst = self._bconst()
        demand_ref = self.data["demand_ref"]
        rho = self._rho()
        gdp0 = self._gdp0()
        k0 = self._k0()
        kpvs = self.data["kpvs"]
        # TODO: why name this partmp??
        partmp = (bconst * demand_ref ** rho).groupby(level="node").sum()
        # TODO: automatically get the units here!!
        aconst = ((gdp0 / 1e3) ** rho - partmp) / (k0 / 1e3) ** (rho * kpvs)
        # want the series to only have index of node
        self.data["aconst"] = aconst.reset_index(level="year", drop=True)
        return self.data["aconst"]


def add_model_data(base, clone, data):
    c = Calculate(base, data)
    c.read_data()
    c.derive_data()

    # add temporal set structure
    clone.add_set("type_year", "initializeyear_macro")
    clone.add_set("cat_year", ["initializeyear_macro", c.init_year])
    clone.add_set("type_year", "baseyear_macro")
    clone.add_set("cat_year", ["baseyear_macro", c.base_year])

    # add nodal set structure
    clone.add_set("type_node", "economy")
    for n in c.nodes:
        clone.add_set("cat_node", ["economy", n])

    # add sectoral set structure
    # TODO we shouldn't need a loop here
    for s in c.sectors:
        clone.add_set("sector", s)
        clone.add_set("mapping_macro_sector", [s, s, "useful"])

    # add parameters
    for name, info in MACRO_ITEMS.items():
        if info["ix_type"] != "par":
            continue

        try:
            key = DATA_KEY.get(name, name)
            data = c.data[key].reset_index()
            data["unit"] = UNITS.get(name, "-")
            # some data may have information prior to the MACRO initialization
            # year which we need to remove in order to add it to the scenario
            if "year" in data:
                data = data[data["year"] >= c.init_year]
            clone.add_par(name, data)
        except Exception as e:
            raise type(e)(f"Error in adding parameter {name}\n{e}")


def calibrate(s, check_convergence=True, **kwargs):
    # solve MACRO standalone
    var_list = ["N_ITER", "MAX_ITER", "aeei_calibrate", "grow_calibrate"]
    gams_args = ["LogOption=2"]  # pass everything to log file
    s.solve(model="MACRO", var_list=var_list, gams_args=gams_args)
    n_iter = s.var("N_ITER")["lvl"]
    max_iter = s.var("MAX_ITER")["lvl"]
    msg = "MACRO converged after {} of a maximum of {} iterations"
    log.info(msg.format(n_iter, max_iter))

    # get out calibrated values
    aeei = (
        s.var("aeei_calibrate")
        .rename(columns={"lvl": "value"})
        .drop("mrg", axis=1)
        .assign(unit=UNITS["aeei"])
    )
    grow = (
        s.var("grow_calibrate")
        .rename(columns={"lvl": "value"})
        .drop("mrg", axis=1)
        .assign(unit=UNITS["grow"])
    )

    # update calibrated value parameters
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
