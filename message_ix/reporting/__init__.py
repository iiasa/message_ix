from functools import partial
import logging

from ixmp.reporting import (
    Reporter as IXMPReporter,
    configure,
)
from ixmp.reporting.utils import Key, rename_dims

from . import computations
from .pyam import as_pyam


log = logging.getLogger(__name__)


# Adjust the ixmp default reporting for MESSAGEix

# Units appearing in MESSAGEix test data
configure(units='y = year')

# Short names for dimensions
rename_dims.update({
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
    # New
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


class Reporter(IXMPReporter):
    """MESSAGEix Reporter."""
    @classmethod
    def from_scenario(self, scenario, **kwargs):
        # Invoke the ixmp method
        rep = super().from_scenario(scenario, **kwargs)

        # Add basic derived quantities
        # NB this could be moved out to a utility method + YAML config
        products = [
            ('out',      ['output', 'ACT']),
            ('out_hist', ['output', 'ref_activity']),
            ('in',       ['input', 'ACT']),
            ('in_hist',  ['input', 'ref_activity']),
            ('emi',      ['emission_factor', 'ACT']),
            ('emi_hist', ['emission_factor', 'ref_activity']),
            ('inv',      ['inv_cost', 'CAP_NEW']),
            ('inv_hist', ['inv_cost', 'ref_new_capacity']),
            ('fom',      ['fix_cost', 'CAP']),
            ('fom_hist', ['fix_cost', 'ref_capacity']),
            ('vom',      ['var_cost', 'ACT']),
            ('vom_hist', ['var_cost', 'ref_activity']),
        ]
        for name, quantities in products:
            # Fetch the full key for each quantity
            try:
                base_keys = [rep.full_key(q) for q in quantities]
            except KeyError as e:
                log.info('{} not in scenario → not adding {}'
                         .format(e.args[0], name))

            # Compute a key for the result
            key = Key.product(name, *base_keys)

            # Add the basic product to the graph and index
            rep.add(key, tuple([computations.product] + base_keys))
            rep._index[name] = key

            # Add partial sums of the product
            rep.apply(key.iter_sums)

        return rep

    def as_pyam(self, quantities, year_time_dim, drop={}, collapse=None):
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
