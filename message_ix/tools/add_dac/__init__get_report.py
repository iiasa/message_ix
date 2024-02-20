# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import ixmp
import message_ix
import numpy as np
import os
import pandas as pd
import yaml
from collections.abc import Mapping
from itertools import repeat
from message_ix.models import MESSAGE_ITEMS
from message_ix.utils import make_df


def get_values(scenario,
               variable = '', valuetype = 'lvl',
               #filters = {}
              ): 
    # filters must use 'cat_tec' to aggregate technology
    # don't forget to include check unit
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    variable    : string
        name of variable to report
    valuetype   : string, 'lvl' or 'mrg'
        type of values reported to report,
        either level or marginal.
        default is 'lvl'
    """
    
    if isinstance(scenario.var(variable), pd.DataFrame):
        df = scenario.var(variable)
        dimensions = [col for col in df.columns if col not in ['lvl','mrg']]
        return df.set_index(dimensions)[[valuetype]]
    else:
        return scenario.var(variable)[valuetype]


groups = {'DACs': ['LT_DAC','HT_DAC']}
def get_report(scenario,
               technologies = '',
              ): 
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    technologies    : string or list 
        name of technology to be reported
    variable    : string or list
        name of variable to report
    """
    var_dict  = {var: [] for var in ['CAP','CAP_NEW','INVESTMENT','REMOVAL']}
    
    # listing model years to be reported
    years_rep = (sorted(scenario.set('cat_year')
                        .set_index('type_year')
                        .loc['cumulative','year'].to_list()))
    
    # Create dataframe
    for var in var_dict.keys():
        # primary variables
        if var in ['CAP','CAP_NEW']:
            df = (get_values(scenario,var)['lvl'].unstack()
                  .loc[:,groups.get(technologies),:]
                  .groupby(['node_loc']).sum()
                 )[years_rep]
            
        # investment
        elif var == 'INVESTMENT':
            depl = (get_values(scenario,'CAP_NEW')['lvl'].unstack()
                   .loc[:,groups.get(technologies),:]
                   )[years_rep]
            
            dfic = scen.par('inv_cost')
            
            inv  = (dfic.loc[dfic['technology'].isin(groups.get(technologies))]
                    .set_index(['node_loc','technology','year_vtg'])['value'].unstack())
            
            df = depl.mul(inv).groupby(['node_loc']).sum()
        
        # removal
        elif var == 'REMOVAL':
            acts = get_values(scen,'ACT').droplevel(['mode','time'])
            df   = acts.loc[:,groups.get(technologies),:,:]['lvl'].unstack().groupby(['node_loc']).sum()
            
        df.loc['World'] = df.sum(axis=0)
        
        var_dict[var] = df

    # Create dictionary for variable dataframes and write variables to excel
    with pd.ExcelWriter('get_report_output.xlsx', engine='openpyxl') as writer:
        for var in var_dict.keys():
            var_dict[var].to_excel(writer, sheet_name=var)
    
    return var_dict
