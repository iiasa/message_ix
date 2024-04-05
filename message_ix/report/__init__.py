import logging
from functools import lru_cache, partial
from operator import itemgetter
from typing import List, Mapping, Tuple, Union, cast

from genno.operator import broadcast_map
from ixmp.report import (
    ComputationError,
    Key,
    KeyExistsError,
    MissingKeyError,
    Quantity,
    configure,
)
from ixmp.report import Reporter as IXMPReporter

from message_ix.models import DIMS

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

# Configure genno for message_ix.
configure(
    # Units appearing in MESSAGEix test data
    units={"define": "y = year"},
    # Short names for dimensions, where they differ from the full name
    rename_dims={full: short for short, (_, full) in DIMS.items() if full != short},
)

#: Common reporting tasks. These include:
#:
#: 1. MESSAGE mapping sets, converted to reporting quantities via
#:    :func:`~ixmp.report.operator.map_as_qty`.
#:
#:    For instance, the mapping set ``cat_addon`` is available at the reporting key
#:    ``map_addon``, which produces a :class:`genno.Quantity` with the two dimensions
#:    ``type_addon`` and ``ta`` (short form of ``technology_addon``). This Quantity
#:    contains the value 1 at every valid (type_addon, ta) location, and 0 elsewhere.
#: 2. Simple products of 2 or mode quantities.
#: 3. Other derived quantities.
TASKS0: Tuple[Tuple, ...] = (
    # Mapping sets
    ("map_addon", "map_as_qty", "cat_addon", "t"),
    ("map_emission", "map_as_qty", "cat_emission", "e"),
    ("map_tec", "map_as_qty", "cat_tec", "t"),
    ("map_year", "map_as_qty", "cat_year", "y"),
    #
    # Products
    ("out", "mul", "output", "ACT"),
    ("in", "mul", "input", "ACT"),
    ("rel", "mul", "relation_activity", "ACT"),
    ("emi", "mul", "emission_factor", "ACT"),
    ("inv", "mul", "inv_cost", "CAP_NEW"),
    ("fom", "mul", "fix_cost", "CAP"),
    ("vom", "mul", "var_cost", "ACT"),
    ("land_out", "mul", "land_output", "LAND"),
    ("land_use_qty", "mul", "land_use", "LAND"),  # TODO: better name!
    ("land_emi", "mul", "land_emission", "LAND"),
    #
    # Others
    ("y::model", "model_periods", "y", "cat_year"),
    ("y0", itemgetter(0), "y::model"),
    # NB Cannot use the full dimensions of `fom` and `vom`` here, as they are not
    #    matched, resulting in null indices in `tom`.
    ("tom", "add", "fom:nl-t-yv-ya", "vom:nl-t-yv-ya"),
    # Broadcast from type_addon to technology_addon
    (
        (
            "addon conversion:nl-t-yv-ya-m-h-ta",
            broadcast_map,
            "addon_conversion:n-t-yv-ya-m-h-type_addon",
            "map_addon",
        ),
        dict(rename={"n": "nl"}),
    ),
    ("addon ACT", "mul", "addon conversion", "ACT"),
    ("addon in", "mul", "input", "addon ACT"),
    ("addon out", "mul", "output", "addon ACT"),
    (
        (
            "addon up:nl-t-ya-m-h-ta",
            broadcast_map,
            "addon_up:n-t-ya-m-h-type_addon",
            "map_addon",
        ),
        dict(rename={"n": "nl"}),
    ),
    ("addon potential", "mul", "addon up", "addon ACT"),
    # Double broadcast over type_emission, then type_tec, in a nested task
    (
        "price emission:n-e-t-y",
        broadcast_map,
        (broadcast_map, "PRICE_EMISSION:n-type_emission-type_tec-y", "map_emission"),
        "map_tec",
    ),
)

#: Quantities to automatically convert to IAMC format using
#: :func:`~genno.compat.pyam.operator.as_pyam`.
PYAM_CONVERT = [
    ("out:nl-t-ya-m-nd-c-l", dict(kind="ene", var="out")),
    ("in:nl-t-ya-m-no-c-l", dict(kind="ene", var="in")),
    ("CAP:nl-t-ya", dict(var="capacity")),
    ("CAP_NEW:nl-t-yv", dict(var="new capacity")),
    ("inv:nl-t-yv", dict(var="inv cost")),
    ("fom:nl-t-ya", dict(var="fom cost")),
    ("vom:nl-t-ya", dict(var="vom cost")),
    ("tom:nl-t-ya", dict(var="total om cost")),
    ("emi:nl-t-ya-m-e", dict(kind="emi", var="emis")),
]

#: Automatic reports that :func:`~genno.operator.concat` quantities converted to IAMC
#: format.
TASKS1 = (
    (
        "message::system",
        "concat",
        "out::pyam",
        "in::pyam",
        "CAP::pyam",
        "CAP_NEW::pyam",
    ),
    ("message::costs", "concat", "inv::pyam", "fom::pyam", "vom::pyam", "tom::pyam"),
    ("message::emissions", "concat", "emi::pyam"),
    (
        "message::default",
        "concat",
        "message::system",
        "message::costs",
        "message::emissions",
    ),
)


@lru_cache(1)
def get_tasks() -> List[Tuple[Tuple, Mapping]]:
    """Return a list of tasks describing MESSAGE reporting calculations."""
    # Assemble queue of items to add. Each element is a 2-tuple of (positional, keyword)
    # arguments for Reporter.add()
    to_add: List[Tuple[Tuple, Mapping]] = []

    strict = dict(strict=True)

    for t in TASKS0:
        if len(t) == 2 and isinstance(t[1], dict):
            # (args, kwargs) → update kwargs with strict
            t[1].update(strict)
            to_add.append(cast(Tuple[Tuple, Mapping], t))
        else:
            # args only → use strict as kwargs
            to_add.append((t, strict))

    # Conversions to IAMC data structure and pyam objects

    for qty, collapse_kw in PYAM_CONVERT:
        # Column to set as year dimension + standard renames from MESSAGE to IAMC dims
        rename = {
            next(filter(lambda d: d.startswith("y"), Key(qty).dims)): "year",
            "n": "region",
            "nl": "region",
        }
        # Callback function to further collapse other columns into IAMC columns
        cb = partial(collapse_message_cols, **collapse_kw)

        to_add.append(((qty, "as_pyam", "pyam"), dict(rename=rename, collapse=cb)))

    # Standard reports
    to_add.extend((t, strict) for t in TASKS1)

    return to_add


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Append message_ix.report.operator to the modules in which the Computer will
        # look up operator names.
        self.require_compat("message_ix.report.operator")

    @classmethod
    def from_scenario(cls, scenario, **kwargs) -> "Reporter":
        """Create a Reporter by introspecting `scenario`.

        Warnings are logged if `scenario` does not have a solution. In this case, any
        keys/computations based on model output (ixmp variables and equations) may
        return an empty Quantity, fail, or behave unpredictably. Keys/computations
        based only on model input (ixmp sets and parameters) should function normally.

        Returns
        -------
        .Reporter
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
        fail_action : "raise" or int
            :mod:`logging` level or level name, passed to the `fail` argument of
            :meth:`.Reporter.add_queue`.
        """
        # Ensure that genno.compat.pyam is usable
        self.require_compat("pyam")

        # Use a queue pattern via Reporter.add_queue()
        self.add_queue(get_tasks(), fail=fail_action)
