from functools import partial

from ixmp.reporting import Reporter as IXMPReporter, configure
from ixmp.reporting.utils import Key, rename_dims

from .pyam import as_pyam

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
