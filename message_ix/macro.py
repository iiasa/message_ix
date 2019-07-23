
MACRO_INIT = {
    'sets': {
        'sector': None,
        'mapping_macro_sector': ['sector', 'commodity', 'level', ],
    },
    'pars': {
        'demand_MESSAGE': ['node', 'sector', 'year', ],
        'price_MESSAGE': ['node', 'sector', 'year', ],
        'cost_MESSAGE': ['node', 'year', ],
        'gdp_calibrate': ['node', 'year', ],
        'MERtoPPP': ['node', 'year', ],
        'kgdp': ['node', ],
        'kpvs': ['node', ],
        'depr': ['node', ],
        'drate': ['node', ],
        'esub': ['node', ],
        'lotol': ['node', ],
        'p_ref': ['node', 'sector', ],
        'lakl': ['node', ],
        'prfconst': ['node', 'sector', ],
        'grow': ['node', 'year', ],
        'aeei': ['node', 'sector', 'year', ],
    },
    'vars': {
        'DEMAND': ['node', 'commodity', 'level', 'year', 'time', ],
        'PRICE': ['node', 'commodity', 'level', 'year', 'time', ],
        'COST_NODAL': ['node', 'year', ],
        'COST_NODAL_NET': ['node', 'year', ],
        'GDP': ['node', 'year', ],
        'I': ['node', 'year', ],
        'C': ['node', 'year', ],
        'K': ['node', 'year', ],
        'KN': ['node', 'year', ],
        'Y': ['node', 'year', ],
        'YN': ['node', 'year', ],
        'EC': ['node', 'year', ],
        'UTILITY': None,
        'PHYSENE': ['node', 'sector', 'year', ],
        'PRODENE': ['node', 'sector', 'year', ],
        'NEWENE': ['node', 'sector', 'year', ],
        'EC': ['node', 'year', ],
        'grow_calibrate': ['node', 'year', ],
        'aeei_calibrate': ['node', 'sector', 'year', ],
    },
    'equs': {
        'COST_ACCOUNTING_NODAL': ['node', 'year', ],
    },
}

MACRO_DATA_FOR_DERIVATION = {
    'cost_ref': ['node', 'sector', ],
    'demand_ref': ['node', 'sector', ],
}

VERIFY_INPUT_DATA = [
    'p_ref', 'lotol', 'esub', 'drate', 'depr', 'kpvs', 'kgdp',
    'gdp_calibrate', 'aeei', 'cost_ref', 'demand_ref', 'MERtoPPP',
]


def init(s):
    for key, values in MACRO_INIT['sets'].items():
        s.init_set(key, values)
    for key, values in MACRO_INIT['pars'].items():
        s.init_par(key, values)
    for key, values in MACRO_INIT['vars'].items():
        if not s.has_var(key):
            try:
                # TODO: this seems required because for some reason DEMAND (and
                # perhaps others) seem to already be listed in the java code,
                # but still needs to be initialized in the python code. However,
                # you cannot init it with dimensions, only with the variable
                # name.
                s.init_var(key, values)
            except:
                s.init_var(key)
    for key, values in MACRO_INIT['equs'].items():
        s.init_equ(key, values)
