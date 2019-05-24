import pandas as pd

from . import Scenario
from .utils import make_df


models = {
    'dantzig': {
        'model': 'Canning problem (MESSAGE scheme)',
        'scenario': 'standard',
    },
}


def make_dantzig(mp, solve=False, multi_year=False):
    """Define and optionally solve Dantzig's transport problem.

    Parameters
    ----------
    mp : ixmp.Platform
    solve : bool
        If True, the scenario is solved.
    multi_year : bool
        If True, the scenario has years 1964–1965 inclusive. Otherwise, the
        scenario has the single year 1963.

    Returns
    -------
    :class:`ixmp.Scenario`
    """
    anno = "Dantzig's canning problem as a MESSAGE-scheme Scenario"
    args = models['dantzig'].copy()
    scen = Scenario(mp, **args, version='new', annotation=anno)

    # Sets
    # NB commit() is refused if technology and year are not given
    t = ['canning_plant', 'transport_from_seattle', 'transport_from_san-diego']
    sets = {
        'technology': t,
        'year': [1963],
        'node': 'seattle san-diego new-york chicago topeka'.split(),
        'mode': 'production to_new-york to_chicago to_topeka'.split(),
        'level': 'supply consumption'.split(),
        'commodity': ['cases'],
    }

    for name, values in sets.items():
        scen.add_set(name, values)

    # Parameters
    par = {}

    demand = {'node': 'new-york chicago topeka'.split(),
              'value': [325, 300, 275]}
    par['demand'] = make_df(
        pd.DataFrame.from_dict(demand), commodity='cases', level='consumption',
        time='year', unit='cases', year=1963)

    b_a_u = {'node_loc': ['seattle', 'san-diego'],
             'value': [350, 600]}
    par['bound_activity_up'] = make_df(
        pd.DataFrame.from_dict(b_a_u), mode='production',
        technology='canning_plant', time='year', unit='cases', year_act=1963)
    par['ref_activity'] = par['bound_activity_up'].copy()

    input = pd.DataFrame([
        ['to_new-york', 'seattle', 'seattle', t[1]],
        ['to_chicago', 'seattle', 'seattle', t[1]],
        ['to_topeka', 'seattle', 'seattle', t[1]],
        ['to_new-york', 'san-diego', 'san-diego', t[2]],
        ['to_chicago', 'san-diego', 'san-diego', t[2]],
        ['to_topeka', 'san-diego', 'san-diego', t[2]],
    ], columns=['mode', 'node_loc', 'node_origin', 'technology'])
    par['input'] = make_df(
        input, commodity='cases', level='supply', time='year',
        time_origin='year', unit='%', value=1, year_act=1963,
        year_vtg=1963)

    output = pd.DataFrame([
        ['supply', 'production', 'seattle', 'seattle', t[0]],
        ['supply', 'production', 'san-diego', 'san-diego', t[0]],
        ['consumption', 'to_new-york', 'new-york', 'seattle', t[1]],
        ['consumption', 'to_chicago', 'chicago', 'seattle', t[1]],
        ['consumption', 'to_topeka', 'topeka', 'seattle', t[1]],
        ['consumption', 'to_new-york', 'new-york', 'san-diego', t[2]],
        ['consumption', 'to_chicago', 'chicago', 'san-diego', t[2]],
        ['consumption', 'to_topeka', 'topeka', 'san-diego', t[2]],
    ], columns=['level', 'mode', 'node_dest', 'node_loc', 'technology'])
    par['output'] = make_df(
        output, commodity='cases', time='year', time_dest='year', unit='%',
        value=1, year_act=1963, year_vtg=1963)

    var_cost = pd.DataFrame([
        ['to_new-york', 'seattle', 'transport_from_seattle', 0.225],
        ['to_chicago', 'seattle', 'transport_from_seattle', 0.153],
        ['to_topeka', 'seattle', 'transport_from_seattle', 0.162],
        ['to_new-york', 'san-diego', 'transport_from_san-diego', 0.225],
        ['to_chicago', 'san-diego', 'transport_from_san-diego', 0.162],
        ['to_topeka', 'san-diego', 'transport_from_san-diego', 0.126],
    ], columns=['mode', 'node_loc', 'technology', 'value'])
    par['var_cost'] = make_df(
        var_cost, time='year', unit='USD', year_act=1963, year_vtg=1963)

    for name, value in par.items():
        scen.add_par(name, value)

    if multi_year:
        scen.add_set('year', [1964, 1965])
        scen.add_par('technical_lifetime', ['seattle', 'canning_plant', 1964],
                     3, 'y')

    scen.commit('Created a MESSAGE-scheme version of the transport problem.')
    scen.set_as_default()

    if solve:
        scen.solve()

    return scen


def make_westeros(mp, solve=False):
    """Define and optionally solve the Westeros model."""
    raise NotImplementedError
