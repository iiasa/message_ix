import logging
import re
from collections import ChainMap
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from copy import copy
from dataclasses import InitVar, dataclass, field
from functools import cache, partial
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from warnings import warn

import ixmp.model.gams
from ixmp import config
from ixmp.backend import ItemType
from ixmp.backend.jdbc import JDBCBackend
from ixmp.util import maybe_check_out, maybe_commit

from message_ix.util.ixmp4 import on_ixmp4backend
from message_ix.util.scenario_data import REQUIRED_EQUATIONS, REQUIRED_VARIABLES

if TYPE_CHECKING:
    from logging import LogRecord

    import ixmp.core.scenario

    import message_ix.core


log = logging.getLogger(__name__)

#: Solver options used by :meth:`.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    "advind": 0,
    "lpmethod": 4,
    "threads": 4,
    "epopt": 1e-6,
}

#: Common dimension name abbreviations mapped to tuples with:
#:
#: 1. the respective coordinate/index set, and
#: 2. the full dimension name.
DIMS = {
    "c": ("commodity", "commodity"),
    "c2": ("commodity", "commodity2"),
    "e": ("emission", "emission"),
    "first_period": ("year", "first_period"),
    "g": ("grade", "grade"),
    "h": ("time", "time"),
    "h2": ("time", "time2"),
    "hd": ("time", "time_dest"),
    "ho": ("time", "time_origin"),
    "inv_tec": ("technology", "inv_tec"),
    "l": ("level", "level"),
    "m": ("mode", "mode"),
    "ms": ("mode", "storage_mode"),
    "n": ("node", "node"),
    "nd": ("node", "node_dest"),
    "nl": ("node", "node_loc"),
    "no": ("node", "node_origin"),
    "node_parent": ("node", "node_parent"),
    "nr": ("node", "node_rel"),
    "ns": ("node", "node_share"),
    "q": ("rating", "rating"),
    "r": ("relation", "relation"),
    "renewable_tec": ("technology", "renewable_tec"),
    "s": ("land_scenario", "land_scenario"),
    "t": ("technology", "technology"),
    "ta": ("technology", "technology_addon"),
    "time_parent": ("time", "time_parent"),
    "tp": ("technology", "technology_primary"),
    "ts": ("technology", "storage_tec"),
    "u": ("land_type", "land_type"),
    "y": ("year", "year"),
    "ya": ("year", "year_act"),
    "yr": ("year", "year_rel"),
    "yv": ("year", "year_vtg"),
}


@dataclass
class Item:
    """Description of an :mod:`ixmp` item: equation, parameter, set, or variable.

    Instances of this class carry only structural information, not data.
    """

    #: Name of the item.
    name: str

    #: Type of the item, for instance :attr:`ItemType.PAR <ixmp.backend.ItemType.PAR>`.
    type: "ixmp.backend.ItemType"

    #: String expression for :attr:`coords` and :attr:`dims`. Split on spaces and parsed
    #: using :data:`DIMS` so that, for instance, "nl yv" results in entries for
    #: for "node", "year" in :attr:`coords`, and "node_loc", "year_vtg" in :attr:`dims`.
    expr: InitVar[str] = ""

    #: Coordinates of the item; that is, the names of sets that index its dimensions.
    #: The same set name may be repeated if it indexes multiple dimensions.
    coords: tuple[str, ...] = field(default_factory=tuple)

    #: Dimensions of the item.
    dims: tuple[str, ...] = field(default_factory=tuple)

    #: Text description of the item.
    description: Optional[str] = None

    def __post_init__(self, expr):
        if expr == "":
            return

        # Split on spaces. For each dimension, use an abbreviation (if one) exists, else
        # the set name for both coords and dims
        self.coords, self.dims = zip(*[DIMS.get(d, (d, d)) for d in expr.split()])

        if self.dims == self.coords:
            # No distinct dimension names; don't store these
            self.dims = tuple()

    @property
    def ix_type(self) -> str:
        """Lower-case string form of :attr:`type`: "equ", "par", "set", or "var".

        Read-only.
        """
        return str(self.type.name).lower()

    def to_dict(self) -> dict:
        """Return the :class:`dict` representation used internally in :mod:`ixmp`.

        This has the keys:

        - :py:`ix_type`: same as :attr:`ix_type`.
        - :py:`idx_sets`: same as :attr:`coords`.
        - :py:`idx_names`: same as :attr:`dims`, but only included if these are (a)
          non-empty and (b) different from :attr:`coords`.
        """
        result = dict(ix_type=self.ix_type, idx_sets=self.coords)
        if self.dims:
            result.update(idx_names=self.dims)
        return result


def _item_shorthand(cls, type, name, expr="", description=None, **kwargs):
    """Helper to populate :attr:`MESSAGE.items` or :attr:`MACRO.items`."""
    assert name not in cls.items
    cls.items[name] = Item(name, type, expr, description=description, **kwargs)


def item(ix_type, expr, description: Optional[str] = None) -> dict:
    """Return a dict with idx_sets and idx_names, given a string `expr`.

    .. deprecated:: 3.8.0

       Instead, use :py:`Item(...).to_dict()`
    """
    item = Item("", ItemType[ix_type.upper()], expr, description=description)
    return item.to_dict()


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
            # Record versions of message_ix and ixmp in GDX I/O files
            "record_version_packages": ("message_ix", "ixmp"),
        },
        ixmp.model.gams.GAMSModel.defaults,
    )

    #: Mapping from model item (equation, parameter, set, or variable) names to
    #: :class:`.Item` describing the item.
    items: Mapping[str, Item]

    # Make default model options known to the class
    model_dir: Path

    def __init__(self, name=None, **model_options):
        # Update the default options with any user-provided options
        model_options.setdefault("model_dir", config.get("message model dir"))
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(config.get("message solve options") or dict())
        self.cplex_opts.update(model_options.pop("solve_options", {}))

        super().__init__(name, **model_options)

    def run(self, scenario: "ixmp.core.scenario.Scenario") -> None:
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


def _check_structure(scenario: "ixmp.core.scenario.Scenario"):
    """Check dimensionality of some items related to the storage representation.

    Yields a sequence of 4-tuples:

    1. Item name.
    2. Item ix_type.
    3. Number of data points in the item; -1 if it does not exist in `scenario`.
    4. A warning/error message, *if* the index names/sets do not match those in
       :attr:`.MESSAGE.items` and the item contains data. Otherwise, the message is an
       empty string.
    """
    if scenario.has_solution():
        return

    # NB could rename this e.g. _check_structure_0 if there are multiple such methods
    for name in ("storage_initial", "storage_self_discharge", "map_tec_storage"):
        info = MESSAGE.items[name]
        message = ""
        N = -1  # Item does not exist; default

        try:
            # Retrieve the index names and data length of the item
            idx_names = tuple(scenario.idx_names(name))
            N = len(getattr(scenario, info.ix_type)(name))
        except KeyError:
            pass
        else:
            # Item exists
            expected_names = info.dims or info.coords
            if expected_names != idx_names and N > 0:
                message = (
                    f"{info.ix_type} {name!r} has data with dimensions {idx_names!r}"
                    f" != {expected_names!r} and cannot be solved; try expand_dims()"
                )
        finally:
            yield name, info.ix_type, N, message


@cache
def _log_filter_pattern(cls: type[GAMSModel]) -> "re.Pattern":
    """Return a compiled :class:`re.Pattern` for filtering log messages.

    Messages like the following are matched:

    - "Existing index sets of 'FOO' [] do not match …"
    - "Existing index names of 'BAR' [] do not match …"

    …where "FOO" or "BAR" are :any:`ItemType.EQU` or :any:`ItemType.VAR` among
    the :attr:`cls.items <GAMSModel.items>`. Such log entries are generated by
    :meth:`ixmp.

    The result is :func:`functools.cache`'d, thus only generated once.
    """
    # Names of EQU or VAR-type items
    names = sorted(k for k, v in cls.items.items() if v.type & ItemType.SOLUTION)

    # Expression matching log message from ixmp.model.base.Model.initialize_items()
    return re.compile(
        rf"Existing index (set|name)s of '({'|'.join(names)})' \[\] do not match"
    )


@contextmanager
def _filter_log_initialize_items(cls: type[GAMSModel]) -> Iterator[None]:
    """Context manager to filter log messages related to existing items."""
    pattern = _log_filter_pattern(cls)

    def _filter(record: "LogRecord") -> bool:
        # Retrieve the compiled expression
        return not pattern.match(record.msg)

    # Attach the filter to the ixmp.model logger
    logger = logging.getLogger("ixmp.model.base")
    logger.addFilter(_filter)
    try:
        yield
    finally:
        logger.removeFilter(_filter)


class MESSAGE(GAMSModel):
    """Model class for MESSAGE."""

    name = "MESSAGE"

    #: All equations, parameters, sets, and variables in the MESSAGE formulation.
    items: MutableMapping[str, Item] = dict()

    @staticmethod
    def enforce(scenario: "message_ix.core.Scenario") -> None:
        """Enforce data consistency in `scenario`."""
        # Raise an exception if any of the storage items have incorrect dimensions, i.e.
        # non-empty error messages
        messages: list[str] = list(
            filter(None, [msg for *_, msg in _check_structure(scenario)])
        )
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
    def initialize(cls, scenario: "ixmp.core.scenario.Scenario") -> None:
        """Set up `scenario` with required sets and parameters for MESSAGE.

        See Also
        --------
        :attr:`items`
        """
        from message_ix.core import Scenario
        from message_ix.util.ixmp4 import platform_compat
        from message_ix.util.scenario_setup import add_default_data

        # Adjust the Platform on which `scenario` is stored for compatibility between
        # ixmp.{IXMP4,JDBC}Backend. Because message_ix does not subclass Platform, this
        # is the earliest opportunity to make these adjustments.
        platform_compat(scenario.platform)

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

        # Collect items to initialize
        items = {k: v.to_dict() for k, v in cls.items.items()}

        # Remove balance_equality for JDBC, where it seems to cause errors
        if isinstance(scenario.platform._backend, JDBCBackend):
            items.pop("balance_equality")

        # Hide verbose log messages if `scenario` was created with message_ix <3.10 and
        # is being loaded with v3.11 or later
        with _filter_log_initialize_items(cls):
            # Initialize the ixmp items for MESSAGE
            cls.initialize_items(scenario, items)

        if not isinstance(scenario, Scenario):
            # Narrow type of `scenario`
            # NB This should only occur if code constructs ixmp.Scenario(…,
            #    scheme="MESSAGE"), instead of message_ix.Scenario directly. User code
            #    *should* never do this, but it occurs in .test_models.test_initialize()
            return

        # NOTE I tried transcribing this from ixmp_source as-is, but the MESSAGE class
        # defined in models.py takes care of setting up the Scenario -- except for
        # adding default data.
        # ixmp_source does other things, too, which I don't think we need here, but I've
        # kept them in for completeness for now.

        # ixmp_source first sets up a Scenario and adds default data
        # models.MESSAGE seems to do the setup for us in all cases, while
        # add_default_data() only adds missing items, so can always run.
        # TODO Is this correct?
        # if version == "new":
        #     # If the Scenario already exists, we don't need these two
        # set_up_scenario(s=self)
        add_default_data(scenario=scenario)

        # TODO We don't seem to need this, but if we do, give them better names
        # self.tecParList = [
        #     parameter_info for parameter_info in PARAMETERS if parameter_info.is_tec
        # ]
        # self.tecActParList = [
        #     parameter_info
        #     for parameter_info in PARAMETERS
        #     if parameter_info.is_tec_act
        # ]

        # TODO the following could be activated in ixmp_source through the flag
        # parameter `sanity_checks`. This 'sanity_check' (there are more, s.b.) is
        # generally only active when loading a scenario from the DB (unless explicitly
        # loading via ID, in which case it's also inactive). We don't distinguish
        # loading from the DB and some tutorials failed, so disable.
        # ensure_required_indexsets_have_data(s=self)

        # TODO It does not seem useful to construct these because some required
        # indexsets won't have any data in them yet. They do get run in imxp_source at
        # this point, though.
        # compose_maps(scenario=scenario)

        # Commit if anything was removed
        maybe_commit(scenario, state, f"{cls.__name__}.initialize")

    def run(self, scenario: "ixmp.core.scenario.Scenario") -> None:
        from message_ix.core import Scenario
        from message_ix.util.gams_io import (
            add_auxiliary_items_to_container_data_list,
            add_default_data_to_container_data_list,
            store_message_version,
        )
        from message_ix.util.scenario_setup import (
            compose_maps,
            ensure_required_indexsets_have_data,
        )

        assert isinstance(scenario, Scenario)  # Narrow type

        # Run the sanity checks
        ensure_required_indexsets_have_data(scenario=scenario)

        compose_maps(scenario=scenario)

        if on_ixmp4backend(scenario):
            # ixmp.model.gams.GAMSModel.__init__() creates the container_data attribute
            # from its .defaults and any user kwargs

            # Add `MESSAGE_ix_version` parameter for validation by GAMS
            store_message_version(container_data=self.container_data)

            # TODO Why is this a dedicated function?
            # Add default data for some `Table`s to container data
            for name in ("cat_tec", "type_tec_land"):
                add_default_data_to_container_data_list(
                    container_data=self.container_data, name=name, scenario=scenario
                )

            # Add automatically created helper items to container data
            add_auxiliary_items_to_container_data_list(
                container_data=self.container_data, scenario=scenario
            )

            # Request only required Equations per default
            self.equ_list = self.equ_list or []
            self.equ_list.extend(equation.gams_name for equation in REQUIRED_EQUATIONS)

            # Request only required Variables per default
            self.var_list = self.var_list or []
            self.var_list.extend(variable.gams_name for variable in REQUIRED_VARIABLES)

        super().run(scenario)


equ = partial(_item_shorthand, MESSAGE, ItemType.EQU)
par = partial(_item_shorthand, MESSAGE, ItemType.PAR)
_set = partial(_item_shorthand, MESSAGE, ItemType.SET)
var = partial(_item_shorthand, MESSAGE, ItemType.VAR)


# Index sets
_set("commodity")
_set("emission")
_set("grade")
_set("land_scenario")
_set("land_type")
_set("level_storage", description="Storage level")
_set("level")
_set("lvl_spatial")
_set("lvl_temporal")
_set("mode")
_set("node")
_set("rating")
_set("relation")
_set("shares")
_set("storage_tec", description="Storage reservoir technology")
_set("technology")
_set("time")
_set("time_relative")
_set("type_addon")
_set("type_emission")
_set("type_node")
_set("type_relation")
_set("type_tec")
_set("type_year")
_set("year")

# Indexed sets
_set("addon", "t")
_set("balance_equality", "c l")
_set("cat_addon", "type_addon ta")
_set("cat_emission", "type_emission e")
_set("cat_node", "type_node n")
_set("cat_relation", "type_relation r")
_set("cat_tec", "type_tec t")
_set("cat_year", "type_year y")
_set("is_capacity_factor", "nl t yv ya h")
_set("level_renewable", "l")
_set("level_resource", "l")
_set("level_stocks", "l")
_set("map_node", "node_parent n")
_set("map_shares_commodity_share", "shares ns n type_tec m c l")
_set("map_shares_commodity_total", "shares ns n type_tec m c l")
_set("map_spatial_hierarchy", "lvl_spatial n node_parent")
_set("map_tec_addon", "t type_addon")
_set(
    "map_tec_storage",
    "n t m ts ms l c lvl_temporal",
    description="Mapping of storage reservoir to charger/discharger",
)
_set("map_temporal_hierarchy", "lvl_temporal h time_parent")
_set("map_time", "time_parent h")
_set("type_tec_land", "type_tec")

# Parameters
par("abs_cost_activity_soft_lo", "nl t ya h")
par("abs_cost_activity_soft_up", "nl t ya h")
par("abs_cost_new_capacity_soft_lo", "nl t yv")
par("abs_cost_new_capacity_soft_up", "nl t yv")
par("addon_conversion", "n t yv ya m h type_addon")
par("addon_lo", "n t ya m h type_addon")
par("addon_up", "n t ya m h type_addon")
par("bound_activity_lo", "nl t ya m h")
par("bound_activity_up", "nl t ya m h")
par("bound_emission", "n type_emission type_tec type_year")
par("bound_extraction_up", "n c g y")
par("bound_new_capacity_lo", "nl t yv")
par("bound_new_capacity_up", "nl t yv")
par("bound_total_capacity_lo", "nl t ya")
par("bound_total_capacity_up", "nl t ya")
par("capacity_factor", "nl t yv ya h")
par("commodity_stock", "n c l y")
par("construction_time", "nl t yv")
par("demand", "n c l y h")
par("duration_period", "y")
par("duration_time", "h")
par("dynamic_land_lo", "n s y u")
par("dynamic_land_up", "n s y u")
par("emission_factor", "nl t yv ya m e")
par("emission_scaling", "type_emission e")
par("fix_cost", "nl t yv ya")
par("fixed_activity", "nl t yv ya m h")
par("fixed_capacity", "nl t yv ya")
par("fixed_extraction", "n c g y")
par("fixed_land", "n s y")
par("fixed_new_capacity", "nl t yv")
par("fixed_stock", "n c l y")
par("flexibility_factor", "nl t yv ya m c l h q")
par("growth_activity_lo", "nl t ya h")
par("growth_activity_up", "nl t ya h")
par("growth_land_lo", "n y u")
par("growth_land_scen_lo", "n s y")
par("growth_land_scen_up", "n s y")
par("growth_land_up", "n y u")
par("growth_new_capacity_lo", "nl t yv")
par("growth_new_capacity_up", "nl t yv")
par("historical_activity", "nl t ya m h")
par("historical_emission", "n type_emission type_tec type_year")
par("historical_extraction", "n c g y")
par("historical_gdp", "n y")
par("historical_land", "n s y")
par("historical_new_capacity", "nl t yv")
par("initial_activity_lo", "nl t ya h")
par("initial_activity_up", "nl t ya h")
par("initial_land_lo", "n y u")
par("initial_land_scen_lo", "n s y")
par("initial_land_scen_up", "n s y")
par("initial_land_up", "n y u")
par("initial_new_capacity_lo", "nl t yv")
par("initial_new_capacity_up", "nl t yv")
par("input", "nl t yv ya m no c l h ho")
par("interestrate", "year")
par("inv_cost", "nl t yv")
par("land_cost", "n s y")
par("land_emission", "n s y e")
par("land_input", "n s y c l h")
par("land_output", "n s y c l h")
par("land_use", "n s y u")
par("level_cost_activity_soft_lo", "nl t ya h")
par("level_cost_activity_soft_up", "nl t ya h")
par("level_cost_new_capacity_soft_lo", "nl t yv")
par("level_cost_new_capacity_soft_up", "nl t yv")
par("min_utilization_factor", "nl t yv ya")
par("operation_factor", "nl t yv ya")
par("output", "nl t yv ya m nd c l h hd")
par("peak_load_factor", "n c l y h")
par("rating_bin", "n t ya c l h q")
par("ref_activity", "nl t ya m h")
par("ref_extraction", "n c g y")
par("ref_new_capacity", "nl t yv")
par("ref_relation", "r nr yr")
par("relation_activity", "r nr yr nl t ya m")
par("relation_cost", "r nr yr")
par("relation_lower", "r nr yr")
par("relation_new_capacity", "r nr yr t")
par("relation_total_capacity", "r nr yr t")
par("relation_upper", "r nr yr")
par("reliability_factor", "n t ya c l h q")
par("renewable_capacity_factor", "n c g l y")
par("renewable_potential", "n c g l y")
par("resource_cost", "n c g y")
par("resource_remaining", "n c g y")
par("resource_volume", "n c g")
par("share_commodity_lo", "shares ns ya h")
par("share_commodity_up", "shares ns ya h")
par("share_mode_lo", "shares ns t m ya h")
par("share_mode_up", "shares ns t m ya h")
par("soft_activity_lo", "nl t ya h")
par("soft_activity_up", "nl t ya h")
par("soft_new_capacity_lo", "nl t yv")
par("soft_new_capacity_up", "nl t yv")
par("storage_initial", "n t m l c y h", "Initial amount of storage")
par(
    "storage_self_discharge",
    "n t m l c y h",
    "Storage losses as a percentage of installed capacity",
)
par("subsidy", "nl type_tec ya")
par("tax_emission", "node type_emission type_tec type_year")
par("tax", "nl type_tec ya")
par("technical_lifetime", "nl t yv")
par("time_order", "lvl_temporal h", "Order of sub-annual time slices")
par("var_cost", "nl t yv ya m h")

# Variables
var(
    "ACT_LO",
    "n t y h",
    "Relaxation variable for dynamic constraints on activity (downwards)",
)
var(
    "ACT_RATING",
    "n t yv ya c l h q",
    "Auxiliary variable for distributing total activity of a technology to a number of"
    " 'rating bins'",
)
var(
    "ACT_UP",
    "n t y h",
    "Relaxation variable for dynamic constraints on activity (upwards)",
)
var("ACT", "nl t yv ya m h", "Activity of technology")
var("CAP_FIRM", "n t c l y", "Capacity counting towards system reliability constraints")
var(
    "CAP_NEW_LO",
    "n t y",
    "Relaxation variable for dynamic constraints on new capacity (downwards)",
)
var(
    "CAP_NEW_UP",
    "n t y",
    "Relaxation variable for dynamic constraints on new capacity (upwards)",
)
var("CAP_NEW", "nl t yv", "New capacity")
var("CAP", "nl t yv ya", "Total installed capacity")
var(
    "COMMODITY_USE",
    "n c l y",
    "Total amount of a commodity & level that was used or consumed",
)
var(
    "COST_NODAL_NET",
    "n y",
    "System costs at the node level over time including effects of energy trade",
)
var("COST_NODAL", "n y", "System costs at the node level over time")
var("DEMAND", "n c l y h", "Demand")
var("EMISS", "n e type_tec y", "Aggregate emissions by technology type")
var("EXT", "n c g y", "Extraction of fossil resources")
var(
    "GDP",
    "n y",
    "Gross domestic product (GDP) in market exchange rates for MACRO reporting",
)
var("LAND", "n s y", "Share of given land-use scenario")
var("OBJ", "", "Objective value of the optimisation problem (scalar)")
var(
    "PRICE_COMMODITY",
    "n c l y h",
    "Commodity price (derived from marginals of COMMODITY_BALANCE constraint)",
)
var(
    "PRICE_EMISSION",
    "n type_emission type_tec y",
    "Emission price (derived from marginals of EMISSION_EQUIVALENCE constraint)",
)
var(
    "REL",
    "r nr yr",
    "Auxiliary variable for left-hand side of user-defined relations",
)
var(
    "REN",
    "n t c g y h",
    "Activity of renewables specified per renewables grade",
)
var("SLACK_ACT_BOUND_LO", "n t y m h", "Slack variable for lower bound on activity")
var("SLACK_ACT_BOUND_UP", "n t y m h", "Slack variable for upper bound on activity")
var(
    "SLACK_ACT_DYNAMIC_LO",
    "n t y h",
    "Slack variable for dynamic activity constraint relaxation (downwards)",
)
var(
    "SLACK_ACT_DYNAMIC_UP",
    "n t y h",
    "Slack variable for dynamic activity constraint relaxation (upwards)",
)
var(
    "SLACK_CAP_NEW_BOUND_LO",
    "n t y",
    "Slack variable for bound on new capacity (downwards)",
)
var(
    "SLACK_CAP_NEW_BOUND_UP",
    "n t y",
    "Slack variable for bound on new capacity (upwards)",
)
var(
    "SLACK_CAP_NEW_DYNAMIC_LO",
    "n t y",
    "Slack variable for dynamic new capacity constraint (downwards)",
)
var(
    "SLACK_CAP_NEW_DYNAMIC_UP",
    "n t y",
    "Slack variable for dynamic new capacity constraint (upwards)",
)
var(
    "SLACK_CAP_TOTAL_BOUND_LO",
    "n t y",
    "Slack variable for lower bound on total installed capacity",
)
var(
    "SLACK_CAP_TOTAL_BOUND_UP",
    "n t y",
    "Slack variable for upper bound on total installed capacity",
)
var(
    "SLACK_COMMODITY_EQUIVALENCE_LO",
    "n c l y h",
    "Slack variable for commodity balance (downwards)",
)
var(
    "SLACK_COMMODITY_EQUIVALENCE_UP",
    "n c l y h",
    "Slack variable for commodity balance (upwards)",
)
var(
    "SLACK_LAND_SCEN_LO",
    "n s y",
    "Slack variable for dynamic land scenario constraint relaxation (downwards)",
)
var(
    "SLACK_LAND_SCEN_UP",
    "n s y",
    "Slack variable for dynamic land scenario constraint relaxation (upwards)",
)
var(
    "SLACK_LAND_TYPE_LO",
    "n y u",
    "Slack variable for dynamic land type constraint relaxation (downwards)",
)
var(
    "SLACK_LAND_TYPE_UP",
    "n y u",
    "Slack variable for dynamic land type constraint relaxation (upwards)",
)
var(
    "SLACK_RELATION_BOUND_LO",
    "r n y",
    "Slack variable for lower bound of generic relation",
)
var(
    "SLACK_RELATION_BOUND_UP",
    "r n y",
    "Slack variable for upper bound of generic relation",
)
var("STOCK_CHG", "n c l y h", "Annual input into and output from stocks of commodities")
var("STOCK", "n c l y", "Total quantity in intertemporal stock (storage)")
var(
    "STORAGE_CHARGE",
    "n t m l c y h",
    "Charging of storage in each time slice (negative for discharge)",
)
var(
    "STORAGE",
    "n t m l c y h",
    "State of charge (SoC) of storage at each sub-annual time slice (positive)",
)

# Equations
equ(
    "ACTIVITY_BOUND_ALL_MODES_LO",
    "n t y h",
    "Lower bound on activity summed over all vintages and modes",
)
equ(
    "ACTIVITY_BOUND_ALL_MODES_UP",
    "n t y h",
    "Upper bound on activity summed over all vintages and modes",
)
equ(
    "ACTIVITY_BOUND_LO", "n t y m h", "Lower bound on activity summed over all vintages"
)
equ(
    "ACTIVITY_BOUND_UP", "n t y m h", "Upper bound on activity summed over all vintages"
)
equ(
    "ACTIVITY_BY_RATING",
    "n t y c l h q",
    "Constraint on auxiliary rating-specific activity variable by rating bin",
)
equ(
    "ACTIVITY_CONSTRAINT_LO",
    "n t y h",
    "Dynamic constraint on the market penetration of a technology activity"
    " (lower bound)",
)
equ(
    "ACTIVITY_CONSTRAINT_UP",
    "n t y h",
    "Dynamic constraint on the market penetration of a technology activity"
    " (upper bound)",
)
equ("ACTIVITY_RATING_TOTAL", "n t yv y c l h", "Equivalence of `ACT_RATING` to `ACT`")
equ(
    "ACTIVITY_SOFT_CONSTRAINT_LO",
    "n t y h",
    "Bound on relaxation of the dynamic constraint on market penetration (lower bound)",
)
equ(
    "ACTIVITY_SOFT_CONSTRAINT_UP",
    "n t y h",
    "Bound on relaxation of the dynamic constraint on market penetration (upper bound)",
)
equ(
    "ADDON_ACTIVITY_LO",
    "n type_addon y m h",
    "Addon technology activity lower constraint",
)
equ(
    "ADDON_ACTIVITY_UP",
    "n type_addon y m h",
    "Addon-technology activity upper constraint",
)
# TODO I think inv_tec is defined only when writing out to GAMS, while this equation
# will need it to exist first -- but not populated, so just create it as a required set
# without data?
equ(
    "CAPACITY_CONSTRAINT",
    "n inv_tec yv y h",
    "Capacity constraint for technology (by sub-annual time slice)",
)
equ(
    "CAPACITY_MAINTENANCE_HIST",
    "n inv_tec yv first_period",
    "Constraint for capacity maintenance  historical installation (built before "
    "start of model horizon)",
)
equ(
    "CAPACITY_MAINTENANCE_NEW",
    "n inv_tec yv ya",
    "Constraint for capacity maintenance of new capacity built in the current "
    "period (vintage == year)",
)
equ(
    "CAPACITY_MAINTENANCE",
    "n inv_tec yv y",
    "Constraint for capacity maintenance over the technical lifetime",
)
# equ("COMMODITY_BALANCE_GT", "n c l y h", "Commodity supply greater than or equal demand") # noqa: E501
equ("COMMODITY_BALANCE_LT", "n c l y h", "Commodity supply lower than or equal demand")
equ(
    "COMMODITY_USE_LEVEL",
    "n c l y h",
    "Aggregate use of commodity by level as defined by total input into technologies",
)
equ("COST_ACCOUNTING_NODAL", "n y", "Cost accounting aggregated to the node")
equ(
    "DYNAMIC_LAND_SCEN_CONSTRAINT_LO",
    "n s y",
    "Dynamic constraint on land scenario change (lower bound)",
)
equ(
    "DYNAMIC_LAND_SCEN_CONSTRAINT_UP",
    "n s y",
    "Dynamic constraint on land scenario change (upper bound)",
)
equ(
    "DYNAMIC_LAND_TYPE_CONSTRAINT_LO",
    "n y u",
    "Dynamic constraint on land-use change (lower bound)",
)
equ(
    "DYNAMIC_LAND_TYPE_CONSTRAINT_UP",
    "n y u",
    "Dynamic constraint on land-use change (upper bound)",
)
equ(
    "EMISSION_CONSTRAINT",
    "n type_emission type_tec type_year",
    "Nodal-regional-global constraints on emissions (by category)",
)
equ(
    "EMISSION_EQUIVALENCE",
    "n e type_tec y",
    "Auxiliary equation to simplify the notation of emissions",
)
equ("EXTRACTION_BOUND_UP", "n c g y", "Upper bound on extraction (by grade)")
equ(
    "EXTRACTION_EQUIVALENCE",
    "n c y",
    "Auxiliary equation to simplify the resource extraction formulation",
)
equ(
    "FIRM_CAPACITY_PROVISION",
    "n inv_tec y c l h",
    "Contribution of dispatchable technologies to auxiliary firm-capacity variable",
)
equ(
    "LAND_CONSTRAINT",
    "n y",
    "Constraint on total land use (partial sum of `LAND` on `land_scenario` is 1)",
)
equ(
    "MIN_UTILIZATION_CONSTRAINT",
    "n inv_tec yv y",
    "Constraint for minimum yearly operation (aggregated over the course of a year)",
)
equ(
    "NEW_CAPACITY_BOUND_LO",
    "n inv_tec y",
    "Lower bound on technology capacity investment",
)
equ(
    "NEW_CAPACITY_BOUND_UP",
    "n inv_tec y",
    "Upper bound on technology capacity investment",
)
equ(
    "NEW_CAPACITY_CONSTRAINT_LO",
    "n inv_tec y",
    "Dynamic constraint on capacity investment (lower bound)",
)
equ(
    "NEW_CAPACITY_CONSTRAINT_UP",
    "n inv_tec y",
    "Dynamic constraint for capacity investment (learning and spillovers upper bound)",
)
equ(
    "NEW_CAPACITY_SOFT_CONSTRAINT_LO",
    "n inv_tec y",
    "Bound on soft relaxation of dynamic new capacity constraints (downwards)",
)
equ(
    "NEW_CAPACITY_SOFT_CONSTRAINT_UP",
    "n inv_tec y",
    "Bound on soft relaxation of dynamic new capacity constraints (upwards)",
)
equ("OBJECTIVE", "", "Objective value of the optimisation problem")
equ(
    "OPERATION_CONSTRAINT",
    "n inv_tec yv y",
    "Constraint on maximum yearly operation (scheduled down-time for maintenance)",
)
equ("RELATION_CONSTRAINT_LO", "r n y", "Lower bound of relations (linear constraints)")
equ("RELATION_CONSTRAINT_UP", "r n y", "Upper bound of relations (linear constraints)")
equ(
    "RELATION_EQUIVALENCE",
    "r n y",
    "Auxiliary equation to simplify the implementation of relations",
)
equ(
    "RENEWABLES_CAPACITY_REQUIREMENT",
    "n inv_tec c y",
    "Lower bound on required overcapacity when using lower grade potentials",
)
equ(
    "RENEWABLES_EQUIVALENCE",
    "n renewable_tec c y h",
    "Equation to define the renewables extraction",
)
equ(
    "RENEWABLES_POTENTIAL_CONSTRAINT",
    "n c g y",
    "Constraint on renewable resource potential",
)
equ(
    "RESOURCE_CONSTRAINT",
    "n c g y",
    "Constraint on resources remaining in each period (maximum extraction per period)",
)
equ(
    "RESOURCE_HORIZON",
    "n c g",
    "Constraint on extraction over entire model horizon (resource volume in place)",
)
equ(
    "SHARE_CONSTRAINT_COMMODITY_LO",
    "shares ns y h",
    "Lower bounds on share constraints for commodities",
)
equ(
    "SHARE_CONSTRAINT_COMMODITY_UP",
    "shares ns y h",
    "Upper bounds on share constraints for commodities",
)
equ(
    "SHARE_CONSTRAINT_MODE_LO",
    "shares n t m y h",
    "Lower bounds on share constraints for modes of a given technology",
)
equ(
    "SHARE_CONSTRAINT_MODE_UP",
    "shares n t m y h",
    "Upper bounds on share constraints for modes of a given technology",
)
equ("STOCKS_BALANCE", "n c l y", "Commodity inter-temporal balance of stocks")
# FIXME 'h2' or 'time2' are not indicative names, come up with better ones
equ(
    "STORAGE_BALANCE_INIT",
    "n ts m l c y h h2",
    "Balance of the state of charge of storage at sub-annual time slices with "
    "initial storage content",
)
# TODO Why is this using h2 and not h?
equ(
    "STORAGE_BALANCE",
    "n ts m l c y h2 lvl_temporal",
    "Balance of the state of charge of storage",
)
equ(
    "STORAGE_CHANGE",
    "n ts m level_storage c y h",
    "Change in the state of charge of storage",
)
equ(
    "STORAGE_INPUT",
    "n ts l c level_storage c2 m y h",
    "Connecting an input commodity to maintain the activity of storage container "
    "(not stored commodity)",
)
equ(
    "SYSTEM_FLEXIBILITY_CONSTRAINT",
    "n c l y h",
    "Constraint on total system flexibility",
)
equ(
    "SYSTEM_RELIABILITY_CONSTRAINT",
    "n c l y h",
    "Constraint on total system reliability (firm capacity)",
)
equ("TOTAL_CAPACITY_BOUND_LO", "n inv_tec y", "Lower bound on total installed capacity")
equ("TOTAL_CAPACITY_BOUND_UP", "n inv_tec y", "Upper bound on total installed capacity")


#: ixmp items (sets, parameters, variables, and equations) for :class:`.MESSAGE`.
#:
#: .. deprecated:: 3.8.0
#:    Access the model class attribute :attr:`MESSAGE.items` instead.
MESSAGE_ITEMS = {k: v.to_dict() for k, v in MESSAGE.items.items()}


class MACRO(GAMSModel):
    """Model class for MACRO."""

    name = "MACRO"

    #: All equations, parameters, sets, and variables in the MACRO formulation.
    items: MutableMapping[str, Item] = dict()

    #: MACRO uses the GAMS ``break;`` statement, and thus requires GAMS 24.8.1 or later.
    GAMS_min_version = "24.8.1"

    def __init__(self, *args, **kwargs):
        version = ixmp.model.gams.gams_version()
        if version < self.GAMS_min_version:
            raise RuntimeError(
                f"{self.name} requires GAMS >= {self.GAMS_min_version}; found {version}"
            )

        # Additional command-line arguments to GAMS
        solve_args = []
        try:
            concurrent = str(kwargs.pop("concurrent"))
        except KeyError:
            pass
        else:
            if concurrent not in ("0", "1"):
                raise ValueError(f"{concurrent = }")
            solve_args.append(f"--MACRO_CONCURRENT={concurrent}")

        super().__init__(*args, **kwargs)

        self.solve_args.extend(solve_args)

    @classmethod
    def initialize(cls, scenario, with_data=False):
        """Initialize the model structure."""
        # NB some scenarios already have these items. This method simply adds any
        #    missing items.

        # Initialize the ixmp items for MACRO
        cls.initialize_items(scenario, {k: v.to_dict() for k, v in cls.items.items()})


equ = partial(_item_shorthand, MACRO, ItemType.EQU)
par = partial(_item_shorthand, MACRO, ItemType.PAR)
_set = partial(_item_shorthand, MACRO, ItemType.SET)
var = partial(_item_shorthand, MACRO, ItemType.VAR)


#: ixmp items (sets, parameters, variables, and equations) for MACRO.
_set("sector")
_set("mapping_macro_sector", "sector c l")
par("MERtoPPP", "n y")
par("aeei", "n sector y")
par("cost_MESSAGE", "n y")
par("demand_MESSAGE", "n sector y")
par("depr", "node")
par("drate", "node")
par("esub", "node")
par("gdp_calibrate", "n y")
par("grow", "n y")
par("historical_gdp", "n y")
par("kgdp", "node")
par("kpvs", "node")
par("lakl", "node")
par("lotol", "node")
par("prfconst", "n sector")
par("price_MESSAGE", "n sector y")
var("C", "n y", "Total consumption")
var("COST_NODAL", "n y")
var("COST_NODAL_NET", "n y", "Net of trade and emissions cost")
var("DEMAND", "n c l y h")
var("EC", "n y")
var("GDP", "n y")
var("I", "n y", "Total investment")
var("K", "n y")
var("KN", "n y")
var("MAX_ITER", "")
var("N_ITER", "")
var("NEWENE", "n sector y")
var("PHYSENE", "n sector y")
var("PRICE", "n c l y h")
var("PRODENE", "n sector y")
var("UTILITY", "")
var("Y", "n y")
var("YN", "n y")
var("aeei_calibrate", "n sector y")
var("grow_calibrate", "n y")
equ("COST_ACCOUNTING_NODAL", "n y")

#: ixmp items (sets, parameters, variables, and equations) for :class:`.MACRO`.
#:
#: .. deprecated:: 3.8.0
#:    Access the model class attribute :attr:`MACRO.items` instead.
MACRO_ITEMS = {k: v.to_dict() for k, v in MACRO.items.items()}


class MESSAGE_MACRO(MESSAGE, MACRO):
    """Model class for MESSAGE_MACRO."""

    name = "MESSAGE-MACRO"
    #: All equations, parameters, sets, and variables in the MESSAGE-MACRO formulation.
    items = ChainMap(MESSAGE.items, MACRO.items)

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
