import logging
from collections import ChainMap
from copy import copy
from functools import lru_cache
from pathlib import Path
from typing import Optional
from warnings import warn

import ixmp.model.gams
from ixmp import config
from ixmp.util import maybe_check_out, maybe_commit

from .macro import MACRO_ITEMS

log = logging.getLogger(__name__)

#: Solver options used by :meth:`.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    "advind": 0,
    "lpmethod": 4,
    "threads": 4,
    "epopt": 1e-6,
}

# Abbreviations for index sets and index names; the same used in the inline
# documentation of the GAMS code.
_ABBREV = {
    "c": ("commodity", "commodity"),
    "e": ("emission", "emission"),
    "g": ("grade", "grade"),
    "l": ("level", "level"),
    "m": ("mode", "mode"),
    "ms": ("mode", "storage_mode"),
    "n": ("node", "node"),
    "nd": ("node", "node_dest"),
    "nl": ("node", "node_loc"),
    "no": ("node", "node_origin"),
    "nr": ("node", "node_rel"),
    "ns": ("node", "node_share"),
    "r": ("rating", "rating"),
    "s": ("shares", "shares"),
    "t": ("technology", "technology"),
    "ts": ("technology", "storage_tec"),
    "h": ("time", "time"),
    "hd": ("time", "time_dest"),
    "ho": ("time", "time_origin"),
    "y": ("year", "year"),
    "ya": ("year", "year_act"),
    "yr": ("year", "year_rel"),
    "yv": ("year", "year_vtg"),
}


@lru_cache()
def item(ix_type, expr, description: Optional[str] = None):
    """Return a dict with idx_sets and idx_names, given a string `expr`.

    Used only to build `MESSAGE_ITEMS`, below. The following are equivalent::

    >>> item("var", "nl t ya")
    >>> dict(
    ...     ix_type="var",
    ...     idx_sets=["node", "technology", "year"]
    ...     idx_names=["node_loc", "technology", "year_act"]
    ... )
    """
    if len(expr):
        # Split expr on spaces. For each dimension, use an abbreviation (if one) exists,
        # else the set name for both idx_sets and idx_names
        sets, names = zip(*[_ABBREV.get(dim, (dim, dim)) for dim in expr.split()])
    else:
        sets, names = tuple(), tuple()

    # Assemble the result
    result = dict(ix_type=ix_type, idx_sets=sets)

    if names != sets:
        # Index names are distinct from index sets; also return these
        result["idx_names"] = names

    return result


# NB order by ix_type (set, par, var, equ), then alphabetically.
#: ixmp items (sets, parameters, variables, and equations) for MESSAGE.
MESSAGE_ITEMS = {
    # Index sets
    "commodity": dict(ix_type="set"),
    "emission": dict(ix_type="set"),
    "grade": dict(ix_type="set"),
    "land_scenario": dict(ix_type="set"),
    "land_type": dict(ix_type="set"),
    "level_storage": dict(ix_type="set"),  # Storage level
    "level": dict(ix_type="set"),
    "lvl_spatial": dict(ix_type="set"),
    "lvl_temporal": dict(ix_type="set"),
    "mode": dict(ix_type="set"),
    "node": dict(ix_type="set"),
    "rating": dict(ix_type="set"),
    "relation": dict(ix_type="set"),
    "shares": dict(ix_type="set"),
    "storage_tec": dict(ix_type="set"),  # Storage reservoir technology
    "technology": dict(ix_type="set"),
    "time": dict(ix_type="set"),
    "time_relative": dict(ix_type="set"),
    "type_addon": dict(ix_type="set"),
    "type_emission": dict(ix_type="set"),
    "type_node": dict(ix_type="set"),
    "type_relation": dict(ix_type="set"),
    "type_tec": dict(ix_type="set"),
    "type_year": dict(ix_type="set"),
    "year": dict(ix_type="set"),
    #
    # Indexed sets
    "addon": dict(ix_type="set", idx_sets=["technology"]),
    # commented: in test_solve_legacy_scenario(), ixmp_source complains that the item
    # already exists
    # "balance_equality": item("set", "c l"),
    "cat_addon": dict(
        ix_type="set",
        idx_sets=["type_addon", "technology"],
        idx_names=["type_addon", "technology_addon"],
    ),
    "cat_emission": item("set", "type_emission e"),
    "cat_node": item("set", "type_node n"),
    "cat_relation": item("set", "type_relation relation"),
    "cat_tec": item("set", "type_tec t"),
    "cat_year": item("set", "type_year y"),
    "is_capacity_factor": item("set", "nl t yv ya h"),
    "level_renewable": dict(ix_type="set", idx_sets=["level"]),
    "level_resource": dict(ix_type="set", idx_sets=["level"]),
    "level_stocks": dict(ix_type="set", idx_sets=["level"]),
    "map_node": dict(
        ix_type="set", idx_sets=["node", "node"], idx_names=["node_parent", "node"]
    ),
    "map_shares_commodity_share": item("set", "s ns n type_tec m c l"),
    "map_shares_commodity_total": item("set", "s ns n type_tec m c l"),
    "map_spatial_hierarchy": dict(
        ix_type="set",
        idx_sets=["lvl_spatial", "node", "node"],
        idx_names=["lvl_spatial", "node", "node_parent"],
    ),
    "map_tec_addon": dict(ix_type="set", idx_sets=["technology", "type_addon"]),
    # Mapping of storage reservoir to charger/discharger
    "map_tec_storage": item("set", "n t m ts ms l c lvl_temporal"),
    "map_temporal_hierarchy": dict(
        ix_type="set",
        idx_sets=["lvl_temporal", "time", "time"],
        idx_names=["lvl_temporal", "time", "time_parent"],
    ),
    "map_time": dict(
        ix_type="set", idx_sets=["time", "time"], idx_names=["time_parent", "time"]
    ),
    "type_tec_land": dict(ix_type="set", idx_sets=["type_tec"]),
    #
    # Parameters
    "abs_cost_activity_soft_lo": item("par", "nl t ya h"),
    "abs_cost_activity_soft_up": item("par", "nl t ya h"),
    "abs_cost_new_capacity_soft_lo": item("par", "nl t yv"),
    "abs_cost_new_capacity_soft_up": item("par", "nl t yv"),
    "addon_conversion": item("par", "n t yv ya m h type_addon"),
    "addon_lo": item("par", "n t ya m h type_addon"),
    "addon_up": item("par", "n t ya m h type_addon"),
    "bound_activity_lo": item("par", "nl t ya m h"),
    "bound_activity_up": item("par", "nl t ya m h"),
    "bound_emission": item("par", "n type_emission type_tec type_year"),
    "bound_extraction_up": item("par", "n c g y"),
    "bound_new_capacity_lo": item("par", "nl t yv"),
    "bound_new_capacity_up": item("par", "nl t yv"),
    "bound_total_capacity_lo": item("par", "nl t ya"),
    "bound_total_capacity_up": item("par", "nl t ya"),
    "capacity_factor": item("par", "nl t yv ya h"),
    "commodity_stock": item("par", "n c l y"),
    "construction_time": item("par", "nl t yv"),
    "demand": item("par", "n c l y h"),
    "duration_period": dict(ix_type="par", idx_sets=["year"]),
    "duration_time": dict(ix_type="par", idx_sets=["time"]),
    "dynamic_land_lo": item("par", "n land_scenario y land_type"),
    "dynamic_land_up": item("par", "n land_scenario y land_type"),
    "emission_factor": item("par", "nl t yv ya m e"),
    "emission_scaling": item("par", "type_emission e"),
    "fix_cost": item("par", "nl t yv ya"),
    "fixed_activity": item("par", "nl t yv ya m h"),
    "fixed_capacity": item("par", "nl t yv ya"),
    "fixed_extraction": item("par", "n c g y"),
    "fixed_land": item("par", "n land_scenario y"),
    "fixed_new_capacity": item("par", "nl t yv"),
    "fixed_stock": item("par", "n c l y"),
    "flexibility_factor": item("par", "nl t yv ya m c l h r"),
    "growth_activity_lo": item("par", "nl t ya h"),
    "growth_activity_up": item("par", "nl t ya h"),
    "growth_land_lo": item("par", "n y land_type"),
    "growth_land_scen_lo": item("par", "n land_scenario y"),
    "growth_land_scen_up": item("par", "n land_scenario y"),
    "growth_land_up": item("par", "n y land_type"),
    "growth_new_capacity_lo": item("par", "nl t yv"),
    "growth_new_capacity_up": item("par", "nl t yv"),
    "historical_activity": item("par", "nl t ya m h"),
    "historical_emission": dict(
        ix_type="par", idx_sets=["node", "type_emission", "type_tec", "type_year"]
    ),
    "historical_extraction": item("par", "n c g y"),
    "historical_gdp": dict(ix_type="par", idx_sets=["node", "year"]),
    "historical_land": item("par", "n land_scenario y"),
    "historical_new_capacity": item("par", "nl t yv"),
    "initial_activity_lo": item("par", "nl t ya h"),
    "initial_activity_up": item("par", "nl t ya h"),
    "initial_land_lo": item("par", "n y land_type"),
    "initial_land_scen_lo": item("par", "n land_scenario y"),
    "initial_land_scen_up": item("par", "n land_scenario y"),
    "initial_land_up": item("par", "n y land_type"),
    "initial_new_capacity_lo": item("par", "nl t yv"),
    "initial_new_capacity_up": item("par", "nl t yv"),
    "input": item("par", "nl t yv ya m no c l h ho"),
    "interestrate": dict(ix_type="par", idx_sets=["year"]),
    "inv_cost": item("par", "nl t yv"),
    "land_cost": item("par", "n land_scenario y"),
    "land_emission": item("par", "n land_scenario y e"),
    "land_input": item("par", "n land_scenario y c l h"),
    "land_output": item("par", "n land_scenario y c l h"),
    "land_use": item("par", "n land_scenario y land_type"),
    "level_cost_activity_soft_lo": item("par", "nl t ya h"),
    "level_cost_activity_soft_up": item("par", "nl t ya h"),
    "level_cost_new_capacity_soft_lo": item("par", "nl t yv"),
    "level_cost_new_capacity_soft_up": item("par", "nl t yv"),
    "min_utilization_factor": item("par", "nl t yv ya"),
    "operation_factor": item("par", "nl t yv ya"),
    "output": item("par", "nl t yv ya m nd c l h hd"),
    "peak_load_factor": item("par", "n c l y h"),
    "rating_bin": item("par", "n t ya c l h r"),
    "ref_activity": item("par", "nl t ya m h"),
    "ref_extraction": item("par", "n c g y"),
    "ref_new_capacity": item("par", "nl t yv"),
    "ref_relation": item("par", "relation nr yr"),
    "relation_activity": item("par", "relation nr yr nl t ya m"),
    "relation_cost": item("par", "relation nr yr"),
    "relation_lower": item("par", "relation nr yr"),
    "relation_new_capacity": item("par", "relation nr yr t"),
    "relation_total_capacity": item("par", "relation nr yr t"),
    "relation_upper": item("par", "relation nr yr"),
    "reliability_factor": item("par", "n t ya c l h r"),
    "renewable_capacity_factor": item("par", "n c g l y"),
    "renewable_potential": item("par", "n c g l y"),
    "resource_cost": item("par", "n c g y"),
    "resource_remaining": item("par", "n c g y"),
    "resource_volume": item("par", "n c g"),
    "share_commodity_lo": item("par", "s ns ya h"),
    "share_commodity_up": item("par", "s ns ya h"),
    "share_mode_lo": item("par", "s ns t m ya h"),
    "share_mode_up": item("par", "s ns t m ya h"),
    "soft_activity_lo": item("par", "nl t ya h"),
    "soft_activity_up": item("par", "nl t ya h"),
    "soft_new_capacity_lo": item("par", "nl t yv"),
    "soft_new_capacity_up": item("par", "nl t yv"),
    # Initial amount of storage
    "storage_initial": item("par", "n t m l c y h"),
    # Storage losses as a percentage of installed capacity
    "storage_self_discharge": item("par", "n t m l c y h"),
    "subsidy": item("par", "nl type_tec ya"),
    "tax_emission": dict(
        ix_type="par", idx_sets=["node", "type_emission", "type_tec", "type_year"]
    ),
    "tax": item("par", "nl type_tec ya"),
    "technical_lifetime": item("par", "nl t yv"),
    # Order of sub-annual time slices
    "time_order": dict(ix_type="par", idx_sets=["lvl_temporal", "time"]),
    "var_cost": item("par", "nl t yv ya m h"),
    #
    # Variables
    "ACT_LO": item(
        "var",
        "n t y h",
        "relaxation variable for dynamic constraints on activity (downwards)",
    ),
    "ACT_RATING": item("var", "n t yv ya c l h r", ""),
    "ACT_UP": item(
        "var",
        "n t y h",
        "relaxation variable for dynamic constraints on activity (upwards)",
    ),
    "ACT": item("var", "nl t yv ya m h", "Activity of technology"),
    "CAP_FIRM": item(
        "var", "n t c l y", "capacity counting towards system reliability constraints"
    ),
    "CAP_NEW_LO": item(
        "var",
        "n t y",
        "relaxation variable for dynamic constraints on new capacity (downwards)",
    ),
    "CAP_NEW_UP": item(
        "var",
        "n t y",
        "relaxation variable for dynamic constraints on new capacity (upwards)",
    ),
    "CAP_NEW": item("var", "nl t yv", "New capacity"),
    "CAP": item("var", "nl t yv ya", "Total installed capacity"),
    "COMMODITY_USE": item(
        "var",
        "n c l y",
        "total amount of a commodity & level that was used or consumed",
    ),
    "COST_NODAL_NET": item(
        "var",
        "n y",
        "system costs at the node level over time including effects of energy trade",
    ),
    "COST_NODAL": item("var", "n y", "system costs at the node level over time"),
    "DEMAND": item("var", "n c l y h", "demand"),
    "EMISS": item("var", "n e type_tec y", "Aggregate emissions by technology type"),
    "EXT": item("var", "n c g y", "Extraction of fossil resources"),
    "GDP": item(
        "var",
        "n y",
        "gross domestic product (GDP) in market exchange rates for MACRO reporting",
    ),
    "LAND": item("var", "n land_scenario y", "Share of given land-use scenario"),
    "OBJ": item("var", "", "Objective value of the optimisation problem (scalar)"),
    "PRICE_COMMODITY": item(
        "var",
        "n c l y h",
        "commodity price (derived from marginals of COMMODITY_BALANCE constraint)",
    ),
    "PRICE_EMISSION": item(
        "var",
        "n type_emission type_tec y",
        "emission price (derived from marginals of EMISSION_BOUND constraint)",
    ),
    "REL": item(
        "var",
        "relation nr yr",
        "Auxiliary variable for left-hand side of user-defined relations",
    ),
    "REN": item(
        "var",
        "n t c g y h",
        "activity of renewables specified per renewables grade",
    ),
    "SLACK_ACT_BOUND_LO": item(
        "var", "n t y m h", "slack variable for lower bound on activity"
    ),
    "SLACK_ACT_BOUND_UP": item(
        "var", "n t y m h", "slack variable for upper bound on activity"
    ),
    "SLACK_ACT_DYNAMIC_LO": item(
        "var",
        "n t y h",
        "slack variable for dynamic activity constraint relaxation (downwards)",
    ),
    "SLACK_ACT_DYNAMIC_UP": item(
        "var",
        "n t y h",
        "slack variable for dynamic activity constraint relaxation (upwards)",
    ),
    "SLACK_CAP_NEW_BOUND_LO": item(
        "var", "n t y", "slack variable for bound on new capacity (downwards)"
    ),
    "SLACK_CAP_NEW_BOUND_UP": item(
        "var", "n t y", "slack variable for bound on new capacity (upwards)"
    ),
    "SLACK_CAP_NEW_DYNAMIC_LO": item(
        "var", "n t y", "slack variable for dynamic new capacity constraint (downwards)"
    ),
    "SLACK_CAP_NEW_DYNAMIC_UP": item(
        "var", "n t y", "slack variable for dynamic new capacity constraint (upwards)"
    ),
    "SLACK_CAP_TOTAL_BOUND_LO": item(
        "var", "n t y", "slack variable for lower bound on total installed capacity"
    ),
    "SLACK_CAP_TOTAL_BOUND_UP": item(
        "var", "n t y", "slack variable for upper bound on total installed capacity"
    ),
    "SLACK_COMMODITY_EQUIVALENCE_LO": item(
        "var", "n c l y h", "slack variable for commodity balance (downwards)"
    ),
    "SLACK_COMMODITY_EQUIVALENCE_UP": item(
        "var", "n c l y h", "slack variable for commodity balance (upwards)"
    ),
    "SLACK_LAND_SCEN_LO": item(
        "var",
        "n land_scenario y",
        "slack variable for dynamic land scenario constraint relaxation (downwards)",
    ),
    "SLACK_LAND_SCEN_UP": item(
        "var",
        "n land_scenario y",
        "slack variable for dynamic land scenario constraint relaxation (upwards)",
    ),
    "SLACK_LAND_TYPE_LO": item(
        "var",
        "n y land_type",
        "slack variable for dynamic land type constraint relaxation (downwards)",
    ),
    "SLACK_LAND_TYPE_UP": item(
        "var",
        "n y land_type",
        "slack variable for dynamic land type constraint relaxation (upwards)",
    ),
    "SLACK_RELATION_BOUND_LO": item(
        "var", "relation n y", "slack variable for lower bound of generic relation"
    ),
    "SLACK_RELATION_BOUND_UP": item(
        "var", "relation n y", "slack variable for upper bound of generic relation"
    ),
    "STOCK_CHG": item(
        "var", "n c l y h", "annual input into and output from stocks of commodities"
    ),
    "STOCK": item("var", "n c l y", "Total quantity in intertemporal stock (storage)"),
    "STORAGE_CHARGE": item(
        "var",
        "n t m l c y h",
        "charging of storage in each time slice (negative for discharge)",
    ),
    "STORAGE": item(
        "var",
        "n t m l c y h",
        "state of charge (SoC) of storage at each sub-annual time slice (positive)",
    ),
    #
    # Equations
    "ACTIVITY_BOUND_ALL_MODES_LO": item(
        "equ", "n t y h", "Lower bound on activity summed over all vintages and modes"
    ),
    "ACTIVITY_BOUND_ALL_MODES_UP": item(
        "equ", "n t y h", "Upper bound on activity summed over all vintages and modes"
    ),
    "ACTIVITY_BOUND_LO": item(
        "equ", "", "Lower bound on activity summed over all vintages"
    ),
    "ACTIVITY_BOUND_UP": item(
        "equ", "", "Upper bound on activity summed over all vintages"
    ),
    "ACTIVITY_BY_RATING": item(
        "equ",
        "",
        "Constraint on auxiliary rating-specific activity variable by rating bin",
    ),
    "ACTIVITY_CONSTRAINT_LO": item(
        "equ",
        "",
        "Dynamic constraint on the market penetration of a technology activity"
        " (lower bound)",
    ),
    "ACTIVITY_CONSTRAINT_UP": item(
        "equ",
        "",
        "Dynamic constraint on the market penetration of a technology activity"
        " (upper bound)",
    ),
    "ACTIVITY_RATING_TOTAL": item("equ", "", "Equivalence of `ACT_RATING` to `ACT`"),
    "ACTIVITY_SOFT_CONSTRAINT_LO": item(
        "equ",
        "",
        "Bound on relaxation of the dynamic constraint on market penetration"
        " (lower bound)",
    ),
    "ACTIVITY_SOFT_CONSTRAINT_UP": item(
        "equ",
        "",
        "Bound on relaxation of the dynamic constraint on market penetration"
        " (upper bound)",
    ),
    "ADDON_ACTIVITY_LO": item("equ", "", "Addon technology activity lower constraint"),
    "ADDON_ACTIVITY_UP": item("equ", "", "Addon-technology activity upper constraint"),
    "CAPACITY_CONSTRAINT": item(
        "equ", "", "Capacity constraint for technology (by sub-annual time slice)"
    ),
    "CAPACITY_MAINTENANCE_HIST": item(
        "equ",
        "",
        "Constraint for capacity maintenance  historical installation (built before "
        "start of model horizon)",
    ),
    "CAPACITY_MAINTENANCE_NEW": item(
        "equ",
        "",
        "Constraint for capacity maintenance of new capacity built in the current "
        "period (vintage == year)",
    ),
    "CAPACITY_MAINTENANCE": item(
        "equ", "", "Constraint for capacity maintenance over the technical lifetime"
    ),
    # Already exists
    # "COMMODITY_BALANCE_GT": item(
    #     "equ", "", "Commodity supply greater than or equal demand"
    # ),
    "COMMODITY_BALANCE_LT": item(
        "equ", "", "Commodity supply lower than or equal demand"
    ),
    "COMMODITY_USE_LEVEL": item(
        "equ",
        "",
        "Aggregate use of commodity by level as defined by total input into "
        "technologies",
    ),
    "COST_ACCOUNTING_NODAL": item("equ", "", "Cost accounting at node level over time"),
    "DYNAMIC_LAND_SCEN_CONSTRAINT_LO": item(
        "equ", "", "Dynamic constraint on land scenario change (lower bound)"
    ),
    "DYNAMIC_LAND_SCEN_CONSTRAINT_UP": item(
        "equ", "", "Dynamic constraint on land scenario change (upper bound)"
    ),
    "DYNAMIC_LAND_TYPE_CONSTRAINT_LO": item(
        "equ", "", "Dynamic constraint on land-use change (lower bound)"
    ),
    "DYNAMIC_LAND_TYPE_CONSTRAINT_UP": item(
        "equ", "", "Dynamic constraint on land-use change (upper bound)"
    ),
    "EMISSION_CONSTRAINT": item(
        "equ", "", "Nodal-regional-global constraints on emissions (by category)"
    ),
    "EMISSION_EQUIVALENCE": item(
        "equ", "", "Auxiliary equation to simplify the notation of emissions"
    ),
    "EXTRACTION_BOUND_UP": item("equ", "", "Upper bound on extraction (by grade)"),
    "EXTRACTION_EQUIVALENCE": item(
        "equ", "", "Auxiliary equation to simplify the resource extraction formulation"
    ),
    "FIRM_CAPACITY_PROVISION": item(
        "equ",
        "",
        "Contribution of dispatchable technologies to auxiliary firm-capacity variable",
    ),
    "LAND_CONSTRAINT": item(
        "equ",
        "",
        "Constraint on total land use (partial sum of `LAND` on `land_scenario` is 1)",
    ),
    "MIN_UTILIZATION_CONSTRAINT": item(
        "equ",
        "",
        "Constraint for minimum yearly operation (aggregated over the course of a "
        "year)",
    ),
    "NEW_CAPACITY_BOUND_LO": item(
        "equ", "", "Lower bound on technology capacity investment"
    ),
    "NEW_CAPACITY_BOUND_UP": item(
        "equ", "", "Upper bound on technology capacity investment"
    ),
    "NEW_CAPACITY_CONSTRAINT_LO": item(
        "equ", "", "Dynamic constraint on capacity investment (lower bound)"
    ),
    "NEW_CAPACITY_CONSTRAINT_UP": item(
        "equ",
        "",
        "Dynamic constraint for capacity investment (learning and spillovers upper "
        "bound)",
    ),
    "NEW_CAPACITY_SOFT_CONSTRAINT_LO": item(
        "equ",
        "",
        "Bound on soft relaxation of dynamic new capacity constraints (downwards)",
    ),
    "NEW_CAPACITY_SOFT_CONSTRAINT_UP": item(
        "equ",
        "",
        "Bound on soft relaxation of dynamic new capacity constraints (upwards)",
    ),
    "OBJECTIVE": item("equ", "", "Objective value of the optimisation problem"),
    "OPERATION_CONSTRAINT": item(
        "equ",
        "",
        "Constraint on maximum yearly operation (scheduled down-time for maintenance)",
    ),
    "RELATION_CONSTRAINT_LO": item(
        "equ", "", "Lower bound of relations (linear constraints)"
    ),
    "RELATION_CONSTRAINT_UP": item(
        "equ", "", "Upper bound of relations (linear constraints)"
    ),
    "RELATION_EQUIVALENCE": item(
        "equ", "", "Auxiliary equation to simplify the implementation of relations"
    ),
    "RENEWABLES_CAPACITY_REQUIREMENT": item(
        "equ",
        "",
        "Lower bound on required overcapacity when using lower grade potentials",
    ),
    "RENEWABLES_EQUIVALENCE": item(
        "equ", "", "Equation to define the renewables extraction"
    ),
    "RENEWABLES_POTENTIAL_CONSTRAINT": item(
        "equ", "", "Constraint on renewable resource potential"
    ),
    "RESOURCE_CONSTRAINT": item(
        "equ",
        "",
        "Constraint on resources remaining in each period (maximum extraction per "
        "period)",
    ),
    "RESOURCE_HORIZON": item(
        "equ",
        "n c g",
        "Constraint on extraction over entire model horizon (resource volume in place)",
    ),
    "SHARE_CONSTRAINT_COMMODITY_LO": item(
        "equ", "", "Lower bounds on share constraints for commodities"
    ),
    "SHARE_CONSTRAINT_COMMODITY_UP": item(
        "equ", "", "Upper bounds on share constraints for commodities"
    ),
    "SHARE_CONSTRAINT_MODE_LO": item(
        "equ", "", "Lower bounds on share constraints for modes of a given technology"
    ),
    "SHARE_CONSTRAINT_MODE_UP": item(
        "equ", "", "Upper bounds on share constraints for modes of a given technology"
    ),
    "STOCKS_BALANCE": item("equ", "", "Commodity inter-temporal balance of stocks"),
    "STORAGE_BALANCE_INIT": item(
        "equ",
        "",
        "Balance of the state of charge of storage at sub-annual time slices with "
        "initial storage content",
    ),
    "STORAGE_BALANCE": item("equ", "", "Balance of the state of charge of storage"),
    "STORAGE_CHANGE": item("equ", "", "Change in the state of charge of storage"),
    "STORAGE_INPUT": item(
        "equ",
        "",
        "Connecting an input commodity to maintain the activity of storage container "
        "(not stored commodity)",
    ),
    "SYSTEM_FLEXIBILITY_CONSTRAINT": item(
        "equ", "", "Constraint on total system flexibility"
    ),
    "SYSTEM_RELIABILITY_CONSTRAINT": item(
        "equ", "", "Constraint on total system reliability (firm capacity)"
    ),
    "TOTAL_CAPACITY_BOUND_LO": item(
        "equ", "", "Lower bound on total installed capacity"
    ),
    "TOTAL_CAPACITY_BOUND_UP": item(
        "equ", "", "Upper bound on total installed capacity"
    ),
}


def _template(*parts):
    """Helper to make a template string relative to model_dir."""
    return str(Path("{model_dir}", *parts))


class GAMSModel(ixmp.model.gams.GAMSModel):
    """Extended :class:`ixmp.model.gams.GAMSModel` for MESSAGE & MACRO."""

    #: Default model options.
    defaults = ChainMap(
        {
            # New keys for MESSAGE & MACRO
            "model_dir": Path(__file__).parent / "model",
            # Override keys from GAMSModel
            "model_file": _template("{model_name}_run.gms"),
            "in_file": _template("data", "MsgData_{case}.gdx"),
            "out_file": _template("output", "MsgOutput_{case}.gdx"),
            "solve_args": [
                '--in="{in_file}"',
                '--out="{out_file}"',
                '--iter="{}"'.format(
                    _template("output", "MsgIterationReport_{case}.gdx")
                ),
            ],
            # Disable the feature to put input/output GDX files, list files, etc. in a
            # temporary directory
            "use_temp_dir": False,
        },
        ixmp.model.gams.GAMSModel.defaults,
    )

    def __init__(self, name=None, **model_options):
        # Update the default options with any user-provided options
        model_options.setdefault("model_dir", config.get("message model dir"))
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(config.get("message solve options") or dict())
        self.cplex_opts.update(model_options.pop("solve_options", {}))

        super().__init__(name, **model_options)

    def run(self, scenario):
        """Execute the model.

        GAMSModel creates a file named ``cplex.opt`` in the model directory containing
        the “solve_options”, as described above.

        .. warning:: GAMSModel can solve Scenarios in two or more Python processes
           simultaneously; but using *different* CPLEX options in each process may
           produce unexpected results.
        """
        # Ensure the data in `scenario` is consistent with the MESSAGE formulation
        self.enforce(scenario)

        # If two runs are kicked off simultaneously  with the same self.model_dir, then
        # they will try to write the same optfile, and may write different contents.
        #
        # TODO Re-enable the 'use_temp_dir' feature from ixmp.GAMSModel (disabled above)
        #      so that cplex.opt will be specific to that directory.

        # Write CPLEX options into an options file
        optfile = Path(self.model_dir).joinpath("cplex.opt")
        lines = ("{} = {}".format(*kv) for kv in self.cplex_opts.items())
        optfile.write_text("\n".join(lines))
        log.info(f"Use CPLEX options {self.cplex_opts}")

        self.cplex_opts.update({"barcrossalg": 2})
        optfile2 = Path(self.model_dir).joinpath("cplex.op2")
        lines2 = ("{} = {}".format(*kv) for kv in self.cplex_opts.items())
        optfile2.write_text("\n".join(lines2))

        result = super().run(scenario)

        # In previous versions, the `cplex.opt` file(s) were removed at this point
        # in the workflow. This has been removed due to issues when running
        # scenarios asynchronously.

        return result


def _check_structure(scenario):
    """Check dimensionality of some items related to the storage representation.

    Yields a sequence of 4-tuples:

    1. Item name.
    2. Item ix_type.
    3. Number of data points in the item; -1 if it does not exist in `scenario`.
    4. A warning/error message, *if* the index names/sets do not match those in
       `MESSAGE_ITEMS` and the item contains data. Otherwise, the message is an empty
       string.
    """
    if scenario.has_solution():
        return

    # NB could rename this e.g. _check_structure_0 if there are multiple such methods
    for name in ("storage_initial", "storage_self_discharge", "map_tec_storage"):
        info = MESSAGE_ITEMS[name]
        message = ""

        try:
            # Retrieve the index names and data length of the item
            idx_names = tuple(scenario.idx_names(name))
            N = len(getattr(scenario, info["ix_type"])(name))
        except KeyError:
            N = -1  # Item does not exist
        else:
            # Item exists
            expected_names = info.get("idx_names", info["idx_sets"])
            if expected_names != idx_names and N > 0:
                message = (
                    f"{info['ix_type']} {name!r} has data with dimensions {idx_names!r}"
                    f" != {expected_names!r} and cannot be solved; try expand_dims()"
                )
        finally:
            yield name, info["ix_type"], N, message


class MESSAGE(GAMSModel):
    """Model class for MESSAGE."""

    name = "MESSAGE"

    @staticmethod
    def enforce(scenario):
        """Enforce data consistency in `scenario`."""
        # Raise an exception if any of the storage items have incorrect dimensions, i.e.
        # non-empty error messages
        messages = list(filter(None, [msg for *_, msg in _check_structure(scenario)]))
        if messages:
            raise ValueError("\n".join(messages))

        # Check masks ("mapping sets") that indicate which elements of corresponding
        # parameters are active/non-zero. Note that there are other masks currently
        # handled in JDBCBackend. For the moment, this code does not backstop that
        # behaviour.
        # TODO Extend to handle all masks, e.g. for new backends.
        for par_name in ("capacity_factor",):
            # Name of the corresponding set
            set_name = f"is_{par_name}"

            # Existing and expected contents
            existing = scenario.set(set_name)
            expected = scenario.par(par_name).drop(columns=["value", "unit"])

            if existing.equals(expected):
                continue  # Contents are as expected; do nothing

            # Not consistent; empty and then re-populate the set
            with scenario.transact(f"Enforce consistency of {set_name} and {par_name}"):
                scenario.remove_set(set_name, existing)
                scenario.add_set(set_name, expected)

    @classmethod
    def initialize(cls, scenario):
        """Set up *scenario* with required sets and parameters for MESSAGE.

        See Also
        --------
        :data:`MESSAGE_ITEMS`
        """
        # Check for storage items that may contain incompatible data or need to be
        # re-initialized
        state = None
        for name, ix_type, N, message in _check_structure(scenario):
            if len(message):
                warn(message)  # Existing, incompatible data → conspicuous warning
            elif N == 0:
                # Existing, empty item → remove, even if it has the correct dimensions.
                state = maybe_check_out(scenario, state)
                getattr(scenario, f"remove_{ix_type}")(name)

        # Initialize the ixmp items for MESSAGE
        cls.initialize_items(scenario, MESSAGE_ITEMS)

        # Commit if anything was removed
        maybe_commit(scenario, state, f"{cls.__name__}.initialize")


class MACRO(GAMSModel):
    """Model class for MACRO."""

    name = "MACRO"

    #: MACRO uses the GAMS ``break;`` statement, and thus requires GAMS 24.8.1 or later.
    GAMS_min_version = "24.8.1"

    def __init__(self, *args, **kwargs):
        version = ixmp.model.gams.gams_version()
        if version < self.GAMS_min_version:
            raise RuntimeError(
                f"{self.name} requires GAMS >= {self.GAMS_min_version}; found {version}"
            )

        super().__init__(*args, **kwargs)

    @classmethod
    def initialize(cls, scenario, with_data=False):
        """Initialize the model structure."""
        # NB some scenarios already have these items. This method simply adds any
        #    missing items.

        # Initialize the ixmp items
        cls.initialize_items(scenario, MACRO_ITEMS)


class MESSAGE_MACRO(MESSAGE, MACRO):
    """Model class for MESSAGE_MACRO."""

    name = "MESSAGE-MACRO"

    def __init__(self, *args, **kwargs):
        # Remove M-M iteration options from kwargs and convert to GAMS command-line
        # options
        mm_iter_args = []
        for name in "convergence_criterion", "max_adjustment", "max_iteration":
            try:
                mm_iter_args.append(f"--{name.upper()}={kwargs.pop(name)}")
            except KeyError:
                continue

        # Let the parent constructor handle other solve_args
        super().__init__(*args, **kwargs)

        # Append to the prepared solve_args
        self.solve_args.extend(mm_iter_args)

    @classmethod
    def initialize(cls, scenario, with_data=False):
        MESSAGE.initialize(scenario)
        MACRO.initialize(scenario, with_data)
