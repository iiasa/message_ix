from functools import partial
import logging

from ixmp.reporting import (
    Key,
    Reporter as IXMPReporter,
    configure,
)

from . import computations
from .pyam import collapse_message_cols


__all__ = [
    'Key',
    'Reporter',
    'configure',
]

log = logging.getLogger(__name__)


# Adjust the ixmp default reporting for MESSAGEix
configure(
    # Units appearing in MESSAGEix test data
    units={
        'define': 'y = year',
    },
    # Short names for dimensions
    rename_dims={
        # As defined in the documentation
        'commodity': 'c',
        'emission': 'e',
        'grade': 'g',
        'land_scenario': 's',
        'land_type': 'u',
        'level': 'l',
        'mode': 'm',
        'node': 'n',
        'rating': 'q',
        'relation': 'r',
        'technology': 't',
        'time': 'h',
        'year': 'y',

        # Aliases
        'node_dest': 'nd',
        'node_loc': 'nl',
        'node_origin': 'no',
        'node_rel': 'nr',
        'node_share': 'ns',
        'time_dest': 'hd',
        'time_origin': 'ho',
        'year_act': 'ya',
        'year_vtg': 'yv',
        'year_rel': 'yr',

        # Created by reporting
        'technology_addon': 'ta',
        'technology_primary': 'tp',
    }
)

#: Automatic quantities that are the :meth:`~computations.product` of two
#: others.
PRODUCTS = (
    ('out',
        ('output', 'ACT')),
    ('in',
        ('input', 'ACT')),
    ('rel',
        ('relation_activity', 'ACT')),
    ('emi',
        ('emission_factor', 'ACT')),
    ('inv',
        ('inv_cost', 'CAP_NEW')),
    ('fom',
        ('fix_cost', 'CAP')),
    ('vom',
        ('var_cost', 'ACT')),
    ('land_out',
        ('land_output', 'LAND')),
    ('land_use_qty',  # TODO: better name!
        ('land_use', 'LAND')),
    ('land_emi',
        ('land_emission', 'LAND')),
    ('addon ACT',
        ('addon conversion:n-tp-yv-ya-m-h-t:full', 'ACT')),
    ('addon in',
        ('input', 'addon ACT')),
    ('addon out',
        ('output', 'addon ACT')),
)

#: Automatic quantities derived by other calculations.
DERIVED = [
    ('tom:nl-t-yv-ya', (computations.add, 'fom:nl-t-yv-ya', 'vom:nl-t-yv-ya')),
    # addon_conversion broadcast across technology_addon
    ('addon conversion:n-tp-yv-ya-m-h-t:full',
        (partial(computations.broadcast_map,
                 rename={'t': 'tp', 'ta': 't', 'n': 'nl'}),
         'addon_conversion:n-t-yv-ya-m-h-type_addon',
         'map_addon')),
]

#: Quantities to automatically convert to IAMC format using
#: :meth:`~computations.as_pyam`.
PYAM_CONVERT = [
    ('out:nl-t-ya-m-nd-c-l', 'ya', dict(kind='ene', var='out')),
    ('in:nl-t-ya-m-no-c-l', 'ya', dict(kind='ene', var='in')),
    ('CAP:nl-t-ya', 'ya', dict(var='capacity')),
    ('CAP_NEW:nl-t-yv', 'yv', dict(var='new capacity')),
    ('inv:nl-t-yv', 'yv', dict(var='inv cost')),
    ('fom:nl-t-ya', 'ya', dict(var='fom cost')),
    ('vom:nl-t-ya', 'ya', dict(var='vom cost')),
    ('tom:nl-t-ya', 'ya', dict(var='total om cost')),
    ('emi:nl-t-ya-m-e', 'ya', dict(kind='emi', var='emis')),
]


#: Automatic reports that :meth:`~computations.concat` quantities converted to
#: IAMC format.
REPORTS = {
    'message:system': ['out:pyam', 'in:pyam', 'CAP:pyam', 'CAP_NEW:pyam'],
    'message:costs': ['inv:pyam', 'fom:pyam', 'vom:pyam', 'tom:pyam'],
    'message:emissions': ['emi:pyam'],
}


#: MESSAGE mapping sets, converted to quantities using
#: :meth:`~computations.map_as_qty`.
MAPPING_SETS = [
    'addon',
    'emission',
    # 'node',  # Automatic addition fails because 'map_node' is defined
    'tec',
    'year',
]


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""
    @classmethod
    def from_scenario(cls, scenario, **kwargs):
        """Create a Reporter by introspecting *scenario*.

        Returns
        -------
        message_ix.reporting.Reporter
            A reporter for *scenario*.
        """
        if not scenario.has_solution():
            raise RuntimeError('Scenario must have a solution to be reported')

        # Invoke the ixmp method
        rep = super().from_scenario(scenario, **kwargs)

        # Use a queue pattern. This is more forgiving; e.g. 'addon ACT' from
        # PRODUCTS depends on 'addon conversion::full'; but the latter is added
        # to the queue later (from DERIVED). Using strict=True below means that
        # this will raise an exception; so the failed item is re-appended to
        # the queue and tried 1 more time later.

        # Queue of items to add. Each element is a tuple:
        # - The first element is the count of attempts to add the item;
        # - the second element is the method to call;
        # - the remainder are positional arguments.
        to_add = []

        def put(*args, **kwargs):
            """Helper to add elements to the queue."""
            to_add.append(tuple([0, partial(args[0], **kwargs)]
                                + list(args[1:])))

        # Quantities that represent mapping sets
        for name in MAPPING_SETS:
            put(rep.add, f'map_{name}',
                (computations.map_as_qty, f'cat_{name}'), strict=True)

        # Product quantities
        for name, quantities in PRODUCTS:
            put(rep.add_product, name, *quantities)

        # Derived quantities
        for key, args in DERIVED:
            put(rep.add, key, args, strict=True, index=True, sums=True)

        # Conversions to IAMC format/pyam objects
        for qty, year_dim, collapse_kw in PYAM_CONVERT:
            collapse_cb = partial(collapse_message_cols, **collapse_kw)
            put(rep.convert_pyam, qty, year_dim, 'pyam', collapse=collapse_cb)

        # Standard reports
        for group, pyam_keys in REPORTS.items():
            put(rep.add, group, tuple([computations.concat] + pyam_keys),
                strict=True)

        # Add all standard reporting to the default message node
        put(rep.add, 'message:default',
            tuple([computations.concat] + list(REPORTS.keys())),
            strict=True)

        # Process the queue until empty
        while len(to_add):
            # Next call
            count, method, *args = to_add.pop(0)

            try:
                # Call the method to add quantities
                method(*args)
            except KeyError as e:
                # Adding failed

                # Information for debugging
                info = [repr(e), str(method), str(args)]

                if count == 0:
                    # First failure: this may only be due to items being out of
                    # order, so retry silently
                    to_add.append(tuple([count + 1, method] + args))

                    log.debug('\n  '.join(['Will retry adding:'] + info))
                elif count == 1:
                    # Second failure: something is genuinely missing, discard
                    log.info('\n  '.join(['Failed to add:'] + info))

        return rep

    def convert_pyam(self, quantities, year_time_dim, tag='iamc', drop={},
                     collapse=None):
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
            # Dimensions to drop automatically
            qty = Key.from_str_or_key(qty)
            to_drop = set(drop) | set(qty.dims) & (
                {'h', 'y', 'ya', 'yr', 'yv'} - {year_time_dim})
            new_key = ':'.join([qty.name, tag])
            comp = partial(computations.as_pyam,
                           year_time_dim=year_time_dim,
                           drop=to_drop,
                           collapse=collapse)
            self.add(new_key, (comp, 'scenario', qty))
            keys.append(new_key)
        return keys

    def write(self, key, path):
        """Compute *key* and write its value to the file at *path*.

        In addition to the formats handled by :meth:`ixmp.Reporter.write`,
        this version will write :class:`pyam.IamDataFrame` to CSV or Excel
        files using built-in methods.
        """
        computations.write_report(self.get(key), path)
