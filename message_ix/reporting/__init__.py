import logging
from functools import partial

from ixmp.reporting import Key
from ixmp.reporting import Reporter as IXMPReporter
from ixmp.reporting import configure

from . import computations
from .pyam import collapse_message_cols

__all__ = [
    "Key",
    "Reporter",
    "configure",
]

log = logging.getLogger(__name__)


# Adjust the ixmp default reporting for MESSAGEix
configure(
    # Units appearing in MESSAGEix test data
    units={
        "define": "y = year",
    },
    # Short names for dimensions
    rename_dims={
        # As defined in the documentation
        "commodity": "c",
        "emission": "e",
        "grade": "g",
        "land_scenario": "s",
        "land_type": "u",
        "level": "l",
        "mode": "m",
        "node": "n",
        "rating": "q",
        "relation": "r",
        "technology": "t",
        "time": "h",
        "year": "y",
        # Aliases
        "node_dest": "nd",
        "node_loc": "nl",
        "node_origin": "no",
        "node_rel": "nr",
        "node_share": "ns",
        "time_dest": "hd",
        "time_origin": "ho",
        "year_act": "ya",
        "year_vtg": "yv",
        "year_rel": "yr",
        # Created by reporting
        "technology_addon": "ta",
        "technology_primary": "tp",
    },
)

#: Automatic quantities that are the :meth:`~computations.product` of two
#: others.
PRODUCTS = (
    # Each entry is ('output key', ('quantities', 'to', 'multiply')). Full keys
    # are inferred automatically, by add_product().
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
    # Each entry is ('full key', (computation tuple,)). Full keys are not
    # inferred and must be given explicitly.
    ("tom:nl-t-yv-ya", (computations.add, "fom:nl-t-yv-ya", "vom:nl-t-yv-ya")),
    # Broadcast from type_addon to technology_addon
    (
        "addon conversion:nl-t-yv-ya-m-h-ta",
        (
            partial(computations.broadcast_map, rename={"n": "nl"}),
            "addon_conversion:n-t-yv-ya-m-h-type_addon",
            "map_addon",
        ),
    ),
    (
        "addon up:nl-t-ya-m-h-ta",
        (
            partial(computations.broadcast_map, rename={"n": "nl"}),
            "addon_up:n-t-ya-m-h-type_addon",
            "map_addon",
        ),
    ),
    # Double broadcast over type_emission, then type_tec, in a nested task
    (
        "price emission:n-e-t-y",
        (
            computations.broadcast_map,
            (
                computations.broadcast_map,
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


#: Automatic reports that :meth:`~computations.concat` quantities converted to
#: IAMC format.
REPORTS = {
    "message:system": ["out:pyam", "in:pyam", "CAP:pyam", "CAP_NEW:pyam"],
    "message:costs": ["inv:pyam", "fom:pyam", "vom:pyam", "tom:pyam"],
    "message:emissions": ["emi:pyam"],
}


#: MESSAGE mapping sets, converted to reporting quantities via
#: :meth:`~.map_as_qty`.
#:
#: For instance, the mapping set ``cat_addon`` is available at the reporting
#: key ``map_addon``, which produces a :class:`.Quantity` with the two
#: dimensions ``type_addon`` and ``ta`` (short form of ``technology_addon``).
#: This Quantity contains the value 1 at every valid (type_addon, ta) location,
#: and 0 elsewhere.
MAPPING_SETS = [
    ("addon", "t"),  # Mapping name, and full target set
    ("emission", "e"),
    # 'node',  # Automatic addition fails because 'map_node' is defined
    ("tec", "t"),
    ("year", "y"),
]


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""

    # Module containing predefined computations, including those defined in
    # message_ix.reporting.computations
    _computations = computations

    @classmethod
    def from_scenario(cls, scenario, **kwargs):
        """Create a Reporter by introspecting *scenario*.

        Returns
        -------
        message_ix.reporting.Reporter
            A reporter for *scenario*.
        """
        if not scenario.has_solution():
            raise RuntimeError("Scenario must have a solution to be reported")

        # Invoke the ixmp method
        rep = super().from_scenario(scenario, **kwargs)

        # Use a queue pattern via Reporter.add_queue(). This is more forgiving;
        # e.g. 'addon ACT' from PRODUCTS depends on 'addon conversion::full';
        # but the latter is added to the queue later (from DERIVED). Using
        # strict=True below means that this will raise an exception; so the
        # failed item is re-appended to the queue and tried 1 more time later.

        # Assemble queue of items to add. Each element is a 2-tuple:
        # - Positional arguments for Reporter.add();
        # - Keyword arguments
        to_add = []

        def put(*args, **kwargs):
            """Helper to add elements to the queue."""
            to_add.append((args, kwargs))

        # Quantities that represent mapping sets
        for name, full_set in MAPPING_SETS:
            put("map_as_qty", f"map_{name}", f"cat_{name}", full_set, strict=True)

        # Product quantities
        for name, quantities in PRODUCTS:
            put("product", name, *quantities)

        # Derived quantities
        for key, args in DERIVED:
            put(key, *args, strict=True, index=True, sums=True)

        # Conversions to IAMC format/pyam objects
        for qty, year_dim, collapse_kw in PYAM_CONVERT:
            collapse_cb = partial(collapse_message_cols, **collapse_kw)
            put("as_pyam", qty, year_dim, "pyam", collapse=collapse_cb)

        # Standard reports
        for group, pyam_keys in REPORTS.items():
            put(group, computations.concat, *pyam_keys, strict=True)

        # Add all standard reporting to the default message node
        put("message:default", computations.concat, *REPORTS.keys(), strict=True)

        # Use ixmp.Reporter.add_queue() to process the entries. Retry at most
        # once; raise an exception if adding fails after that.
        rep.add_queue(to_add, max_tries=2, fail="raise")

        return rep

    def convert_pyam(
        self,
        quantities,
        year_time_dim,
        tag="iamc",
        drop={},
        collapse=None,
        unit=None,
        replace_vars=None,
    ):
        """Add conversion of one or more **quantities** to IAMC format.

        Parameters
        ----------
        quantities : str or Key or list of (str, Key)
            Quantities to transform to :mod:`pyam`/IAMC format.
        year_time_dim : str
            Label of the dimension use for the ‘Year’ or ‘Time’ column of the
            resulting :class:`pyam.IamDataFrame`. The column is labelled ‘Time’
            if ``year_time_dim=='h'``, otherwise ‘Year’.
        tag : str, optional
            Tag to append to new Keys.
        drop : iterable of str, optional
            Label of additional dimensions to drop from the resulting data
            frame. Dimensions ``h``, ``y``, ``ya``, ``yr``, and ``yv``—
            except for the one named by `year_time_dim`—are automatically
            dropped.
        collapse : callable, optional
            Callback to handle additional dimensions of the quantity. A
            :class:`pandas.DataFrame` is passed as the sole argument to
            `collapse`, which must return a modified dataframe.
        unit : str or pint.Unit, optional
            Convert values to these units.
        replace_vars : str or Key
            Other reporting key containing a :class:`dict` mapping variable
            names to replace.

        Returns
        -------
        list of Key
            Each key converts a :class:`Quantity
            <ixmp.reporting.utils.Quantity>` into a :class:`pyam.IamDataFrame`.

        See also
        --------
        message_ix.reporting.computations.as_pyam
        """
        if isinstance(quantities, (str, Key)):
            quantities = [quantities]
        quantities = self.check_keys(*quantities)

        keys = []
        for qty in quantities:
            # Key for the new quantity
            qty = Key.from_str_or_key(qty)
            new_key = ":".join([qty.name, tag])

            # Dimensions to drop automatically
            to_drop = set(drop) | set(qty.dims) & (
                {"h", "y", "ya", "yr", "yv"} - {year_time_dim}
            )

            # Prepare the computation
            comp = [
                partial(
                    computations.as_pyam,
                    year_time_dim=year_time_dim,
                    drop=to_drop,
                    collapse=collapse,
                    unit=unit,
                ),
                "scenario",
                qty,
            ]
            if replace_vars:
                comp.append(replace_vars)

            # Add and store
            self.add(new_key, tuple(comp))
            keys.append(new_key)

        return keys

    # Use convert_pyam as a helper for computations.as_pyam
    add_as_pyam = convert_pyam

    def write(self, key, path):
        """Compute *key* and write its value to the file at *path*.

        In addition to the formats handled by :meth:`ixmp.Reporter.write`,
        this version will write :class:`pyam.IamDataFrame` to CSV or Excel
        files using built-in methods.
        """
        computations.write_report(self.get(key), path)
