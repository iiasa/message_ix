import logging
import re
from collections import ChainMap
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from copy import copy
from dataclasses import InitVar, dataclass, field
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import ixmp.model.gams
from ixmp import config
from ixmp.backend import ItemType

if TYPE_CHECKING:
    from logging import LogRecord

    from genno import Key
    from ixmp.types import InitializeItemsKwargs


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
# Inverse mapping
DIMS_INVERSE = {v[1]: k for k, v in DIMS.items()}


@dataclass(unsafe_hash=True)
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
    description: str | None = None

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

    @property
    @cache
    def key(self) -> "Key":
        """:class:`genno.Key` for this Item in a :class:`.Reporter`.

        Read-only.
        """
        from genno import Key

        dims = [DIMS_INVERSE.get(d, d) for d in self.dims or self.coords]
        return Key(self.name, dims)

    def to_dict(self) -> "InitializeItemsKwargs":
        """Return the :class:`dict` representation used internally in :mod:`ixmp`."""
        result: "InitializeItemsKwargs" = dict(
            ix_type=self.ix_type, idx_sets=self.coords
        )
        if self.dims:
            result["idx_names"] = self.dims
        return result


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

    #: Optional minimum version of GAMS.
    GAMS_min_version: str | None = None

    #: Keyword arguments to map to GAMS `solve_args`.
    keyword_to_solve_arg: list[tuple[str, type, str]]

    def __init__(self, name: str | None = None, **model_options) -> None:
        if gmv := self.GAMS_min_version:
            # Check the minimum GAMS version.
            version = ixmp.model.gams.gams_version() or ""
            if version < gmv:
                raise RuntimeError(f"{self.name} requires GAMS >= {gmv}; got {version}")

        # Convert optional `keyword` arguments to GAMS CLI arguments like ``--{target}``
        solve_args = []
        for keyword, callback, target in self.keyword_to_solve_arg:
            try:
                raw = model_options.pop(keyword)
                solve_args.append(f"--{target}={callback(raw)!s}")
            except KeyError:
                pass
            except ValueError:
                raise ValueError(f"{keyword} = {raw}")

        # Update the default options with any user-provided options
        model_options.setdefault("model_dir", config.get("message model dir"))
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(config.get("message solve options") or dict())
        self.cplex_opts.update(model_options.pop("solve_options", {}))

        super().__init__(name, **model_options)

        self.solve_args.extend(solve_args)

    def run(self, scenario: "ixmp.Scenario") -> None:
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


class _boollike(str):
    """Handle a :class:`bool`-like argument; return :py:`"0"` or :py:`"1"`."""

    def __new__(cls, value: Any):
        if value in {"0", 0, False, "False"}:
            return "0"
        elif value in {"1", 1, True, "True"}:
            return "1"
        else:
            raise ValueError


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


def _item_shorthand(cls, type, name, expr="", description=None, **kwargs):
    """Helper to populate :attr:`MESSAGE.items` or :attr:`MACRO.items`."""
    assert name not in cls.items
    cls.items[name] = Item(name, type, expr, description=description, **kwargs)


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
