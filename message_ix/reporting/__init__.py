import logging
from functools import lru_cache, partial
from typing import Mapping, Sequence, Tuple, Union, cast

import genno
from ixmp.reporting import (
    ComputationError,
    Key,
    KeyExistsError,
    MissingKeyError,
    Quantity,
)
from ixmp.reporting import Reporter as IXMPReporter
from ixmp.reporting import configure

from .pyam import collapse_message_cols

__all__ = [
    "ComputationError",
    "Key",
    "KeyExistsError",
    "MissingKeyError",
    "Quantity",
    "Reporter",
    "configure",
    "collapse_message_cols",
]

log = logging.getLogger(__name__)

#: Short names for dimensions (sets) in the |MESSAGEix| framework.
DIMS = dict(
    # As defined in the documentation
    commodity="c",
    emission="e",
    grade="g",
    land_scenario="s",
    land_type="u",
    level="l",
    mode="m",
    node="n",
    rating="q",
    relation="r",
    technology="t",
    time="h",
    year="y",
    # Aliases
    node_dest="nd",
    node_loc="nl",
    node_origin="no",
    node_rel="nr",
    node_share="ns",
    time_dest="hd",
    time_origin="ho",
    year_act="ya",
    year_vtg="yv",
    year_rel="yr",
    # Created by reporting
    technology_addon="ta",
    technology_primary="tp",
)

# Configure genno for message_ix.
configure(
    # Units appearing in MESSAGEix test data
    units={"define": "y = year"},
    # Short names for dimensions
    rename_dims=DIMS.copy(),
)

#: Automatic quantities that are the :meth:`~computations.product` of two others.
PRODUCTS = (
    # Each entry is ('output key', ('quantities', 'to', 'multiply')). Full keys are
    # inferred automatically, by add_product().
    ("out", ("output", "ACT")),
    ("in", ("input", "ACT")),
    ("rel", ("relation_activity", "ACT")),
    ("emi", ("emission_factor", "ACT")),
    ("inv", ("inv_cost", "CAP_NEW")),
    ("fom", ("fix_cost", "CAP")),
    ("vom", ("var_cost", "ACT")),
    ("land_out", ("land_output", "LAND")),
    ("land_use_qty", ("land_use", "LAND")),  # TODO: better name!
    ("land_emi", ("land_emission", "LAND")),
    ("addon ACT", ("addon conversion", "ACT")),
    ("addon in", ("input", "addon ACT")),
    ("addon out", ("output", "addon ACT")),
    ("addon potential", ("addon up", "addon ACT")),
)

#: Automatic quantities derived by other calculations.
DERIVED = [
    # Each entry is ('full key', (computation tuple,)). Full keys are not inferred and
    # must be given explicitly.
    ("tom:nl-t-yv-ya", (genno.computations.add, "fom:nl-t-yv-ya", "vom:nl-t-yv-ya")),
    # Broadcast from type_addon to technology_addon
    (
        "addon conversion:nl-t-yv-ya-m-h-ta",
        (
            partial(genno.computations.broadcast_map, rename={"n": "nl"}),
            "addon_conversion:n-t-yv-ya-m-h-type_addon",
            "map_addon",
        ),
    ),
    (
        "addon up:nl-t-ya-m-h-ta",
        (
            partial(genno.computations.broadcast_map, rename={"n": "nl"}),
            "addon_up:n-t-ya-m-h-type_addon",
            "map_addon",
        ),
    ),
    # Double broadcast over type_emission, then type_tec, in a nested task
    (
        "price emission:n-e-t-y",
        (
            genno.computations.broadcast_map,
            (
                genno.computations.broadcast_map,
                "PRICE_EMISSION:n-type_emission-type_tec-y",
                "map_emission",
            ),
            "map_tec",
        ),
    ),
]

#: Quantities to automatically convert to IAMC format using
#: :meth:`~computations.as_pyam`.
PYAM_CONVERT = [
    ("out:nl-t-ya-m-nd-c-l", "ya", dict(kind="ene", var="out")),
    ("in:nl-t-ya-m-no-c-l", "ya", dict(kind="ene", var="in")),
    ("CAP:nl-t-ya", "ya", dict(var="capacity")),
    ("CAP_NEW:nl-t-yv", "yv", dict(var="new capacity")),
    ("inv:nl-t-yv", "yv", dict(var="inv cost")),
    ("fom:nl-t-ya", "ya", dict(var="fom cost")),
    ("vom:nl-t-ya", "ya", dict(var="vom cost")),
    ("tom:nl-t-ya", "ya", dict(var="total om cost")),
    ("emi:nl-t-ya-m-e", "ya", dict(kind="emi", var="emis")),
]


#: Automatic reports that :meth:`~computations.concat` quantities converted to IAMC
#: format.
REPORTS = {
    "message::system": ["out::pyam", "in::pyam", "CAP::pyam", "CAP_NEW::pyam"],
    "message::costs": ["inv::pyam", "fom::pyam", "vom::pyam", "tom::pyam"],
    "message::emissions": ["emi::pyam"],
}


#: MESSAGE mapping sets, converted to reporting quantities via :meth:`~.map_as_qty`.
#:
#: For instance, the mapping set ``cat_addon`` is available at the reporting key
#: ``map_addon``, which produces a :class:`.Quantity` with the two dimensions
#: ``type_addon`` and ``ta`` (short form of ``technology_addon``). This Quantity
#: contains the value 1 at every valid (type_addon, ta) location, and 0 elsewhere.
MAPPING_SETS = [
    ("addon", "t"),  # Mapping name, and full target set
    ("emission", "e"),
    # 'node',  # Automatic addition fails because 'map_node' is defined explicitly
    ("tec", "t"),
    ("year", "y"),
]


@lru_cache(1)
def get_tasks() -> Sequence[Tuple[Tuple, Mapping]]:
    """Return a list of tasks describing MESSAGE reporting calculations."""
    # Assemble queue of items to add. Each element is a 2-tuple of (positional, keyword)
    # arguments for Reporter.add()
    to_add = []

    # Helper to add elements to the queue
    def put(*args, **kwargs):
        to_add.append((args, kwargs))

    # Quantities that represent mapping sets
    for name, full_set in MAPPING_SETS:
        put("map_as_qty", f"map_{name}", f"cat_{name}", full_set, strict=True)

    # Product quantities
    for name, quantities in PRODUCTS:
        put("product", name, *quantities)

    # Derived quantities
    for key, args in DERIVED:
        put(key, *args, strict=True, sums=True)

    # Conversions to IAMC-format (pyam) objects
    for qty, year_dim, collapse_kw in PYAM_CONVERT:
        # Standard renaming from dimensions to column names
        rename = dict(n="region", nl="region")
        # Column to set as year or time dimension
        rename[year_dim] = "year" if year_dim.lower().startswith("y") else "time"
        # Callback function to further collapse other columns into IAMC columns
        collapse_cb = partial(collapse_message_cols, **collapse_kw)

        put("convert_pyam", qty, "pyam", rename=rename, collapse=collapse_cb)

    # Standard reports
    for group, pyam_keys in REPORTS.items():
        put("concat", group, *pyam_keys, strict=True)

    # Add all standard reporting to the default message node
    put("concat", "message::default", *REPORTS.keys(), strict=True)

    return to_add


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Append message_ix.reporting.computations to the modules in which the Computer
        # will look up computations names.
        self.require_compat("message_ix.reporting.computations")

    @classmethod
    def from_scenario(cls, scenario, **kwargs) -> "Reporter":
        """Create a Reporter by introspecting `scenario`.

        Warnings are logged if `scenario` does not have a solution. In this case, any
        keys/computations based on model output (ixmp variables and equations) may
        return an empty Quantity, fail, or behave unpredictably. Keys/computations
        based only on model input (ixmp sets and parameters) should function normally.

        Returns
        -------
        message_ix.reporting.Reporter
            A reporter for `scenario`.
        """
        solved = scenario.has_solution()

        if not solved:
            log.warning(
                f'Scenario "{scenario.model}/{scenario.scenario}" has no solution'
            )
            log.warning("Some reporting may not function as expected")
            fail_action: Union[int, str] = logging.DEBUG
        else:
            fail_action = "raise"

        # Invoke the ixmp method
        rep = cast("Reporter", super().from_scenario(scenario, **kwargs))

        # Add the MESSAGEix calculations
        rep.add_tasks(fail_action)

        return rep

    def add_tasks(self, fail_action: Union[int, str] = "raise") -> None:
        """Add the pre-defined MESSAGEix reporting tasks to the Reporter.

        Parameters
        ----------
        fail_action : “raise” or logging level
            Passed to the `fail` argument of :meth:`.Reporter.add_queue`.
        """
        # Ensure that genno.compat.pyam is usable
        self.require_compat("pyam")

        # Use a queue pattern via Reporter.add_queue(). This is more forgiving; e.g.
        # 'addon ACT' from PRODUCTS depends on 'addon conversion::full'; but the latter
        # is added to the queue later (from DERIVED). Using strict=True in the various
        # add() calls means that that this will raise an exception; so the failed item
        # is re-appended to the queue and tried at most 1 more time later.
        self.add_queue(get_tasks(), max_tries=2, fail=fail_action)
