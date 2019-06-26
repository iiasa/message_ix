
MACRO_INIT = {
    'sets': [
        ['sector', ],
        ['mapping_macro_sector', ['sector', 'commodity', 'level', ], ],
    ],
    'pars': [
        ['demand_MESSAGE', ['node', 'sector', 'year', ], ],
        ['price_MESSAGE', ['node', 'sector', 'year', ], ],
        ['cost_MESSAGE', ['node', 'year', ], ],
        ['gdp_calibrate', ['node', 'year', ], ],
        ['MERtoPPP', ['node', 'year', ], ],
        ['kgdp', ['node', ], ],
        ['kpvs', ['node', ], ],
        ['depr', ['node', ], ],
        ['drate', ['node', ], ],
        ['esub', ['node', ], ],
        ['lotol', ['node', ], ],
        ['p_ref', ['node', 'sector', ], ],
        ['lakl', ['node', ], ],
        ['prfconst', ['node', 'sector', ], ],
        ['grow', ['node', 'year', ], ],
        ['aeei', ['node', 'sector', 'year', ], ],
    ],
    'vars': [
        ['DEMAND', ['node', 'commodity', 'level', 'year', 'time', ], ],
        ['PRICE', ['node', 'commodity', 'level', 'year', 'time', ], ],
        ['COST_NODAL', ['node', 'year', ], ],
        ['COST_NODAL_NET', ['node', 'year', ], ],
        ['GDP', ['node', 'year', ], ],
        ['I', ['node', 'year', ], ],
        ['C', ['node', 'year', ], ],
        ['K', ['node', 'year', ], ],
        ['KN', ['node', 'year', ], ],
        ['Y', ['node', 'year', ], ],
        ['YN', ['node', 'year', ], ],
        ['EC', ['node', 'year', ], ],
        ['UTILITY', ],
        ['PHYSENE', ['node', 'sector', 'year', ], ],
        ['PRODENE', ['node', 'sector', 'year', ], ],
        ['NEWENE', ['node', 'sector', 'year', ], ],
        ['EC', ['node', 'year', ], ],
        ['grow_calibrate', ['node', 'year', ], ],
        ['aeei_calibrate', ['node', 'sector', 'year', ], ],
    ],
    'equs': [
        ['COST_ACCOUNTING_NODAL', ['node', 'year', ], ]
    ],
}


def init(s):
    for args in MACRO_INIT['sets']:
        s.init_set(*args)
    for args in MACRO_INIT['pars']:
        s.init_par(*args)
    for args in MACRO_INIT['vars']:
        if not s.has_var(args[0]):
            try:
                # TODO: this seems required because for some reason DEMAND (and
                # perhaps others) seem to already be listed in the java code,
                # but still needs to be initialized in the python code. However,
                # you cannot init it with dimensions, only with the variable
                # name.
                s.init_var(*args)
            except:
                s.init_var(args[0])
    for args in MACRO_INIT['equs']:
        s.init_equ(*args)
