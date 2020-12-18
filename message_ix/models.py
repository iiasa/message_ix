from collections import ChainMap
from copy import copy, deepcopy
from functools import lru_cache
from pathlib import Path

import ixmp.model.gams
from ixmp import config

from .macro import MACRO_ITEMS

#: Solver options used by :meth:`message_ix.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    "advind": 0,
    "lpmethod": 2,
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
    "n": ("node", "node"),
    "nd": ("node", "node_dest"),
    "nl": ("node", "node_loc"),
    "no": ("node", "node_origin"),
    "nr": ("node", "node_rel"),
    "ns": ("node", "node_share"),
    "r": ("rating", "rating"),
    "s": ("shares", "shares"),
    "t": ("technology", "technology"),
    "h": ("time", "time"),
    "hd": ("time", "time_dest"),
    "ho": ("time", "time_origin"),
    "y": ("year", "year"),
    "ya": ("year", "year_act"),
    "yr": ("year", "year_rel"),
    "yv": ("year", "year_vtg"),
}


@lru_cache()
def item(ix_type, expr):
    """Return a dict with idx_sets and idx_names, given a string `expr`.

    Used only to build `MESSAGE_ITEMS`, below. The following are equivalent::

    >>> item("var", "nl t ya")
    >>> dict(
    ...     ix_type="var",
    ...     idx_sets=["node", "technology", "year"]
    ...     idx_names=["node_loc", "technology", "year_act"]
    ... )
    """
    # Split expr on spaces. For each dimension, use an abbreviation (if one)
    # exists, else the set name for both idx_sets and idx_names
    sets, names = zip(*[_ABBREV.get(dim, (dim, dim)) for dim in expr.split()])

    # Assemble the result
    result = dict(ix_type=ix_type, idx_sets=sets)

    if names != sets:
        # Index names are distinct from index sets; also return these
        result["idx_names"] = names

    return result


# NB order by ix_type (set, par, var, equ), then alphabetically.
#: List of ixmp items for MESSAGE.
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
    # commented: in test_solve_legacy_scenario(), ixmp_source complains that
    # the item already exists
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
    "map_tec_storage": item("set", "n t storage_tec l c"),
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
    "storage_initial": item("par", "n t l c y h"),
    # Storage losses as a percentage of installed capacity
    "storage_self_discharge": item("par", "n t l c y h"),
    "subsidy": item("par", "nl type_tec ya"),
    "tax_emission": dict(
        ix_type="par", idx_sets=["node", "type_emission", "type_tec", "type_year"]
    ),
    "tax": item("par", "nl type_tec ya"),
    "technical_lifetime": item("par", "nl t yv"),
    # Order of sub-annual time steps
    "time_order": dict(ix_type="par", idx_sets=["lvl_temporal", "time"]),
    "var_cost": item("par", "nl t yv ya m h"),
    #
    # commented: for both variables and equations, ixmp_source requires that
    # the `idx_sets` and `idx_names` parameters be empty, but then internally
    # uses the correct sets and names to initialize.
    # TODO adjust ixmp_source to accept these values, then uncomment.
    #
    # Variables
    #
    # # Activity
    # "ACT": item("var", "nl t yv ya m h"),
    # # Maintained capacity
    # "CAP": item("var", "nl t yv ya"),
    # # New capacity
    # "CAP_NEW": item("var", "nl t yv"),
    # # Emissions
    # "EMISS": item("var", "n e type_tec y"),
    # # Extraction
    # "EXT": item("var", "n c g y"),
    # # Land scenario share
    # "LAND": item("var", "n land_scenario y"),
    # # Objective (scalar)
    # "OBJ": dict(ix_type="var", idx_sets=[]),
    # # Relation (lhs)
    # "REL": item("var", "relation nr yr"),
    # # Stock
    # "STOCK": item("var", "n c l y"),
    #
    # # Equations
    # # Commodity balance
    # "RESOURCE_HORIZON": item("equ", "n c g"),
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
            # Disable the feature to put input/output GDX files, list files, etc.
            # in a temporary directory
            "use_temp_dir": False,
        },
        ixmp.model.gams.GAMSModel.defaults,
    )

    @classmethod
    def initialize(cls, scenario):
        """Set up *scenario* with required sets and parameters for MESSAGE.

        See Also
        --------
        :data:`MESSAGE_ITEMS`
        """
        # Initialize the ixmp items
        cls.initialize_items(scenario, MESSAGE_ITEMS)

    def __init__(self, name=None, **model_options):
        # Update the default options with any user-provided options
        model_options.setdefault("model_dir", config.get("message model dir"))
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(model_options.pop("solve_options", {}))

        super().__init__(name, **model_options)

    def run(self, scenario):
        """Execute the model.

        GAMSModel creates a file named ``cplex.opt`` in the model directory
        containing the options in :obj:`DEFAULT_CPLEX_OPTIONS`, or any
        overrides passed to :meth:`~message_ix.Scenario.solve`.

        .. warning:: GAMSModel can solve Scenarios in two or more Python
           processes simultaneously; but using *different* CPLEX options in
           each process may produced unexpected results.
        """
        # If two runs are kicked off simulatenously with the same
        # self.model_dir, then they will try to write the same optfile, and may
        # write different contents.
        #
        # TODO Re-enable the 'use_temp_dir' feature from ixmp.GAMSModel
        #      (disabled above). Then cplex.opt will be specific to that
        #      directory.

        # Write CPLEX options into an options file
        optfile = self.model_dir / "cplex.opt"
        lines = ("{} = {}".format(*kv) for kv in self.cplex_opts.items())
        optfile.write_text("\n".join(lines))

        try:
            result = super().run(scenario)
        finally:
            # Remove the optfile regardless of whether the run completed
            # without error. The file may have been removed already by another
            # run (in a separate process) that completed before this one.
            # py37 compat: check for existence instead of using
            # unlink(missing_ok=True)
            if optfile.exists():
                optfile.unlink()

        return result


class MESSAGE(GAMSModel):
    """Model class for MESSAGE."""

    name = "MESSAGE"


class MACRO(GAMSModel):
    """Model class for MACRO."""

    name = "MACRO"

    #: MACRO uses the GAMS ``break;`` statement, and thus requires GAMS 24.8.1
    #: or later.
    GAMS_min_version = "24.8.1"

    def __init__(self, *args, **kwargs):
        version = ixmp.model.gams.gams_version()
        if version < self.GAMS_min_version:
            message = (
                "{0.name} requires GAMS >= {0.GAMS_min_version}; " "found {1}"
            ).format(self, version)
            raise RuntimeError(message)

        super().__init__(*args, **kwargs)

    @classmethod
    def initialize(cls, scenario, with_data=False):
        """Initialize the model structure."""
        # NB some scenarios already have these items. This method simply adds
        #    any missing items.

        # FIXME the Java code under the JDBCBackend (ixmp_source) refuses to
        #       initialize these items with specified idx_sets—even if the
        #       sets are correct.
        items = deepcopy(MACRO_ITEMS)
        for name in "C", "COST_NODAL", "COST_NODAL_NET", "DEMAND", "GDP", "I":
            items[name].pop("idx_sets")

        # Initialize the ixmp items
        cls.initialize_items(scenario, items)


class MESSAGE_MACRO(MACRO):
    """Model class for MESSAGE_MACRO."""

    name = "MESSAGE-MACRO"

    def __init__(self, *args, **kwargs):
        # Remove M-M iteration options from kwargs and convert to GAMS
        # command-line options
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
