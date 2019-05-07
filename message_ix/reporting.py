from ixmp.reporting import Reporter as IXMPReporter
from ixmp.reporting.utils import ureg, rename_dims


# Adjust the ixmp default reporting for MESSAGEix

# Units appearing in MESSAGEix test data
ureg.define('y = year')

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
    def __init__(self):
        # TODO add MESSAGE_ix specific nodes from a file
        super().__init__()
