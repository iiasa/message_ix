from functools import partial
import logging

from ixmp.reporting import (
    Reporter as IXMPReporter,
    computations as ix_computations,
    configure,
)
from ixmp.reporting.utils import Key

from . import computations
from .pyam import (
    as_pyam,
    collapse_message_cols,
)


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
    }
)

#: Basic derived quantities that are the product of two others.
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
)

#: Other standard derived quantities.
DERIVED = [
    ('tom:nl-t-yv-ya', (computations.add, 'fom:nl-t-yv-ya', 'vom:nl-t-yv-ya')),
    ('tom:nl-t-ya', (ix_computations.sum, 'tom:nl-t-yv-ya', None, ['yv'])),
]

#: Quantities to automatically convert to pyam format.
PYAM_CONVERT = {
    'out': ('out:nl-t-ya-m-nd-c-l', 'ya', dict(kind='ene', var='out')),
    'in': ('in:nl-t-ya-m-no-c-l', 'ya', dict(kind='ene', var='in')),
    'cap': ('CAP:nl-t-ya', 'ya', dict(var='capacity')),
    'new_cap': ('CAP_NEW:nl-t-yv', 'yv', dict(var='new capacity')),
    'inv': ('inv:nl-t-yv', 'yv', dict(var='inv cost')),
    'fom': ('fom:nl-t-ya', 'ya', dict(var='fom cost')),
    'vom': ('vom:nl-t-ya', 'ya', dict(var='vom cost')),
    'tom': ('tom:nl-t-ya', 'ya', dict(var='total om cost')),
    'emis': ('emi:nl-t-ya-m-e', 'ya', dict(kind='emi', var='emis')),
}


#: Standard reports that collect quantities converted to pyam format.
REPORTS = {
    'message:system': ['out:pyam', 'in:pyam', 'cap:pyam', 'new_cap:pyam'],
    'message:costs': ['inv:pyam', 'fom:pyam', 'vom:pyam', 'tom:pyam'],
    'message:emissions': ['emis:pyam'],
}


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

        # Add basic quantities for MESSAGEix models
        for name, quantities in PRODUCTS:
            try:
                rep.add_product(name, *quantities)
            except KeyError as e:
                log.info(f'{e.args[0]} not in scenario → not adding {name}')

        # Add derived quantities for MESSAGEix models
        for key, args in DERIVED:
            try:
                rep.add(key, args, strict=True)
            except KeyError as e:
                log.info(f'{e.args[0]} not in scenario → not adding {key}')

        # Add conversions to pyam
        for key, args in PYAM_CONVERT.items():
            qty, year_dim, collapse_kw = args
            collapse_cb = partial(collapse_message_cols, **collapse_kw)
            key += ':pyam'
            try:
                rep.as_pyam(qty, year_dim, key, collapse=collapse_cb)
            except KeyError as e:
                log.info(f'{e.args[0]} not in scenario → not adding {key}')

        # Add standard reports
        for group, pyam_keys in REPORTS.items():
            # Filter out keys which are not added, above
            keys = list(filter(lambda k: k in rep, pyam_keys))

            # Log diagnostic information
            missing = sorted(set(pyam_keys) - set(keys))
            if missing:
                log.info(f'missing {missing} omitted from {group}')

            rep.add(group, tuple([computations.concat] + keys), strict=True)

        # Add all standard reporting to the default message node
        rep.add('message:default',
                tuple([computations.concat] + list(REPORTS.keys())),
                strict=True)

        return rep

    def as_pyam(self, quantities, year_time_dim, key=None, drop={},
                collapse=None):
        """Add conversion of **quantities** to :class:`pyam.IamDataFrame`.

        Parameters
        ----------
        quantities : str or Key or list of (str, Key)
            Quantities to transform to :mod:`pyam` format.
        year_time_dim : str
            Label of the dimension use for the `year` or `time` column of the
            :class:`pyam.IamDataFrame`. The column is labelled "Time" if
            `year_time_dim` is ``h``, otherwise "Year".
        drop : iterable of str, optional
            Label of additional dimensions to drop from the resulting data
            frame. Dimensions ``h``, ``y``, ``ya``, ``yr``, and ``yv``—
            except for the one named by `year_time_dim`—are automatically
            dropped.
        collapse : callable, optional
            Callback to handle additional dimensions of the data frame.

        Returns
        -------
        list of Key
            Keys for the reporting targets that create the IamDataFrames
            corresponding to *quantities*. The keys have the added tag ‘iamc’.
        """
        if isinstance(quantities, (str, Key)):
            quantities = [quantities]
        quantities = self.check_keys(*quantities)

        keys = []
        for qty in quantities:
            # Dimensions to drop automatically
            qty = Key.from_str_or_key(qty)
            to_drop = set(drop) | set(qty._dims) & (
                {'h', 'y', 'ya', 'yr', 'yv'} - {year_time_dim})
            key = key or Key.from_str_or_key(qty, tag='iamc')
            self.add(key, (partial(as_pyam, drop=to_drop, collapse=collapse),
                           'scenario', year_time_dim, qty))
            keys.append(key)
        return keys

    def write(self, key, path):
        """Write the report *key* to the file *path*.

        In addition to the formats handled by :meth:`ixmp.Reporter.write`,
        this version will write :mod:`pyam.IamDataFrame` to CSV or Excel files
        using built-in methods.
        """
        computations.write_report(self.get(key), path)
