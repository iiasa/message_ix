from functools import partial
import logging

from ixmp.reporting import (
    Reporter as IXMPReporter,
    configure,
)
from ixmp.reporting.utils import Key

from . import computations
from .pyam import as_pyam


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
    })

# Basic derived quantities that are the product of two others
products = (
    ('out',
        ('output', 'ACT')),
    ('out_hist',
        ('output', 'ref_activity')),
    ('in',
        ('input', 'ACT')),
    ('in_hist',
        ('input', 'ref_activity')),
    ('emi',
        ('emission_factor', 'ACT')),
    ('emi_hist',
        ('emission_factor', 'ref_activity')),
    ('inv',
        ('inv_cost', 'CAP_NEW')),
    ('inv_hist',
        ('inv_cost', 'ref_new_capacity')),
    ('fom',
        ('fix_cost', 'CAP')),
    ('fom_hist',
        ('fix_cost', 'ref_capacity')),
    ('vom',
        ('var_cost', 'ACT')),
    ('vom_hist',
        ('var_cost', 'ref_activity')),
)


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""
    @classmethod
    def from_scenario(cls, scenario, **kwargs):
        """Create a Reporter by introspecting *scenario*.

        In addition to the keys automatically added by
        :meth:`ixmp.reporting.Reporter.from_scenario`, keys are added for
        derived quantities specific to the MESSAGEix framework. For instance:

        - ``out``: the product of ``output`` (output efficiency) and ``ACT``
          (activity).
        - ``out_hist``: ``output`` × ``ref_activity`` (historical reference
          activity),
        - ``in``:      ``input`` × ``ACT``,
        - ``in_hist``: ``input`` × ``ref_activity``,
        - ``emi``:      ``emission_factor`` × ``ACT``,
        - ``emi_hist``: ``emission_factor`` × ``ref_activity``,
        - ``inv``:      ``inv_cost`` × ``CAP_NEW``,
        - ``inv_hist``: ``inv_cost`` × ``ref_new_capacity``,
        - ``fom``:      ``fix_cost`` × ``CAP``,
        - ``fom_hist``: ``fix_cost`` × ``ref_capacity``,
        - ``vom``:      ``var_cost`` × ``ACT``, and
        - ``vom_hist``: ``var_cost`` × ``ref_activity``.

        .. tip:: Use :meth:`full_key` to retrieve the full-dimensionality
           :class:`Key` for these quantities.

        Returns
        -------
        message_ix.reporting.Reporter
        """
        # Invoke the ixmp method
        rep = super().from_scenario(scenario, **kwargs)

        # Add basic derived quantities for MESSAGEix models
        for name, quantities in products:
            new_key = rep.add_product(name, *quantities)

            # Give some log output
            if new_key is None:
                missing = [q for q in quantities if q not in rep._index]
                log.info('{} not in scenario → not adding {}'
                         .format(missing, name))

        return rep

    def as_pyam(self, quantities, year_time_dim, drop={}, collapse=None):
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
        if not isinstance(quantities, list):
            quantities = [quantities]
        keys = []
        for qty in quantities:
            # Dimensions to drop automatically
            qty = Key.from_str_or_key(qty)
            to_drop = set(drop) | set(qty._dims) & (
                {'h', 'y', 'ya', 'yr', 'yv'} - {year_time_dim})
            key = Key.from_str_or_key(qty, tag='iamc')
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
