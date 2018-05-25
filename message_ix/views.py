import pandas as pd
import numpy as np

# Mapping of database columns to corresponding xlsx_import columns naming
xlsx_column_mapping = {
    'node_loc': 'Region',
    'node': 'Region',
    'technology': 'Technology',
    'unit': 'Unit',
    'year_vtg': 'Vintage/Year Relation',
    'node_origin': 'Region I/O',
    'node_dest': 'Region I/O',
    'node_rel': 'Region I/O',
    'commodity': 'Commodity/Species',
    'emission': 'Commodity/Species',
    'year_rel': 'Vintage/Year Relation',
    'mode': 'Mode',
    'level': 'Level',
    'rating': 'Rating',
    'par': 'Parameter'
}
column_mapping = {
    'node_loc': 'node',
    'technology': 'technology',
    'unit': 'unit',
    'year_vtg': 'year_vtg/year_rel',
    'node_origin': 'node I/O',
    'node_dest': 'node I/O',
    'node_rel': 'node I/O',
    'commodity': 'commodity/emission',
    'emission': 'commodity/emission',
    'year_rel': 'year_vtg/year_rel',
    'par': 'par'
}


def tec_view(scenario, tec=False, sort_by='technology', par=False, xlsx_mapping=False):
    """Returns technology parameters for a given sceanrio

    Parameter:
    ----------
    scenario : ixmp.Sceanrio 
    tec : string or list
        single or multiple technologies for which data should be retrieved
    sort_by : string (default is 'technology')
        allows the user to sort data by either the 'Technology'/'technology' or 'Parameter'/'par'
    par : string or list
        single or multiple parameters for technologies
    xlsx_mapping : string
        allows the user to view data either with database column names or in xlsx_import format
    """
    mapping = xlsx_column_mapping if xlsx_mapping else column_mapping

    if sort_by in ['technology', mapping['technology']]:
        idx_order = [mapping['technology'],
                     mapping['node_loc'], mapping['par']]
        sort_by = mapping['technology']
    elif sort_by in ['par', mapping['par']]:
        idx_order = [mapping['par'],
                     mapping['node_loc'], mapping['technology']]
        sort_by = mapping['par']

    if not tec:
        tec = list(scenario.set('technology'))
    else:
        tec = [tec] if type(tec) != list else tec

    if not par:
        par = scenario.par_list()
    else:
        par = [par] if type(par) != list else par

    dfs = []
    for parameter in par:
        if 'technology' in scenario.par(parameter).columns and not scenario.par(parameter, filters={'technology': tec}).empty:
            tmp = scenario.par(parameter, filters={'technology': tec})
            tmp = tmp.rename(columns=mapping)
            tmp[mapping['par']] = parameter
            if 'year_act' not in tmp.columns:
                tmp = pd.pivot_table(tmp, index=[c for c in tmp.columns if c not in [
                                     'value', mapping['year_vtg']]], columns=mapping['year_vtg'], values='value').reset_index()
            else:
                tmp = pd.pivot_table(tmp, index=[c for c in tmp.columns if c not in [
                                     'value', 'year_act']], columns='year_act', values='value').reset_index()
                del tmp.columns.name
            if mapping['year_vtg'] not in tmp.columns:
                tmp[mapping['year_vtg']] = ''
            tmp = tmp.drop(
                [c for c in ['time', 'time_dest', 'time_origin'] if c in tmp.columns], axis=1)
            idx = [c for c in tmp.columns if type(c) not in [float, int]]
            tmp = tmp.set_index(idx)
            dfs.append(tmp)

    idxs = set(np.concatenate([tuple(x.index.names) for x in dfs]))
    for df in dfs:
        df.reset_index(inplace=True)
        for i in idxs:
            if i not in df.columns:
                df[i] = ' '

    df = pd.concat(dfs)
    idx = idx_order + [mapping['unit']] + \
        sorted([i for i in idxs if i not in idx_order + [mapping['unit']]])
    df = df.set_index(idx).sort_index(axis=0, level=sort_by)

    return(df)
