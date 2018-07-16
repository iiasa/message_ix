import pandas as pd
import numpy as np
from message_ix import utils
pd.set_option('display.max_rows', 500)

# Mapping of database columns to corresponding xlsx_import columns naming
mappings = {
    'file_mapping': {
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
    },
    'model_mapping': {
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
    },
    'raw_mapping': {
        'node_loc': 'node_loc',
        'technology': 'technology',
        'unit': 'unit',
        'year_vtg': 'year_vtg',
        'node_origin': 'node_origin',
        'node_dest': 'node_dest',
        'node_rel': 'node_rel',
        'commodity': 'commodity',
        'emission': 'emission',
        'year_rel': 'year_rel',
        'par': 'par'
    }}


def tec_view(scenario, tec=None, sort_by='technology', region=None, par=None,
             column_style='raw_mapping'):
    """Returns technology parameters for a given sceanrio

    Parameter:
    ----------
    scenario : ixmp.Sceanrio
    tec : string or list
        single or multiple technologies for which data should be retrieved
    sort_by : string (default is 'technology')
        allows the user to sort data by either the 'Technology'/'technology'
        or 'Parameter'/'par'
    region : string or list
        allows filtering by a specific region/node in the model
    par : string or list
        single or multiple parameters for technologies
    column_style : string
        allows the user to view data in raw format
            (as data is saved in the database),
        model format (aggregate of raw foramt) or as file format
            (based on xlsx-import column names)
    """
    mapping = mappings[column_style]

    if sort_by in ['technology', mapping['technology']]:
        idx_order = [mapping['technology'],
                     mapping['node_loc'], mapping['par']]
        sort_by = mapping['technology']
    elif sort_by in ['par', mapping['par']]:
        idx_order = [mapping['par'],
                     mapping['node_loc'], mapping['technology']]
        sort_by = mapping['par']
    else:
        raise ValueError("{} not supported.".format(sort_by))

    tec = utils.is_iter_not_string(
        tec) if tec is not None else list(scenario.set('technology'))

    par = utils.is_iter_not_string(
        par) if par is not None else list(scenario.par_list())

    region = utils.is_iter_not_string(
        region) if region else None

    dfs = []
    for parameter in par:
        # Filters out required parameters
        if not 'technology' in scenario.par(parameter).columns:
            continue
        if region and parameter in ['relation_activity',
                                    'relation_new_capacity',
                                    'relation_total_capacity']:
            filters = filters = {'technology': tec, 'node_rel': region}
        elif region and parameter in ['resource_volume', 'resource_remaining',
                                      'rating_bin', 'reliability_factor',
                                      'peak_load_factor',
                                      'renewable_potential',
                                      'renewable_capacity_factor']:
            filters = filters = {'technology': tec, 'node': region}
        elif region:
            filters = filters = {'technology': tec, 'node_loc': region}
        else:
            filters = filters = {'technology': tec}
        df = scenario.par(parameter, filters=filters)
        if df.empty:
            continue
        # Assigns correct naming to columns
        df = df.rename(columns=mapping)
        # Adds a column with parameter name
        df[mapping['par']] = parameter
        # Applies pivot table
        if 'year_rel' in df.columns:
            index = [c for c in df.columns if c not in [
                'value', mapping['year_rel']]]
            columns = mapping['year_rel']
        elif 'year_act' not in df.columns:
            index = [c for c in df.columns if c not in [
                'value', mapping['year_vtg']]]
            columns = mapping['year_vtg']
        else:
            index = [c for c in df.columns if c not in ['value', 'year_act']]
            columns = 'year_act'
        df = pd.pivot_table(df, index=index, columns=columns,
                            values='value').reset_index()
        df.columns.name = None
        # Adds empty year_vtg
        if mapping['year_vtg'] not in df.columns:
            df[mapping['year_vtg']] = ''
        # Drops non required columns
        if column_style != 'raw_mapping':
            df = df.drop(
                [c for c in ['time', 'time_dest', 'time_origin'] if c in df.columns], axis=1)
        # Sets index
        idx = [i for i in df.columns if i not in utils.numcols(
            df) or i in set(mapping.values())]
        df = df.set_index(idx)
        dfs.append(df)

    idxs = set(np.concatenate([tuple(x.index.names) for x in dfs]))
    for df in dfs:
        df.reset_index(inplace=True)
        add_empty_cols = set(idxs) - set(df.columns)
        for col in add_empty_cols:
            df[col] = ' '

    df = pd.concat(dfs)
    # When retrieving single parameters which dont have node_loc, then the idx_order needs to be updated.
    if 'node_loc' not in df.columns:
        if 'node_rel' in df.columns:
            idx_order = ['node_rel' if x ==
                         'node_loc' else x for x in idx_order]
        else:
            idx_order = ['node' if x == 'node_loc' else x for x in idx_order]
    idx = idx_order + [mapping['unit']]
    idx += sorted(list(set(idxs) - set(idx)))
    df = df.set_index(idx).sort_index(level=sort_by)

    return df
