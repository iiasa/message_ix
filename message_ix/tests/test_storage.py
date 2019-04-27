# -*- coding: utf-8 -*-
"""
This is a unit test for representing storage in the MESSAGEix model, and
testing the functionality of storage equations. The workflow is as follows:
    - building a stylized MESSAGEix model
    - adding seasonality and modifying parameters accordingly
    - adding storage implementation
    - testing storage functionality and equations

"""

from message_ix import Scenario

# A flag to show if storage variables/parameters are added to ixmp java backend
storage_in_java = False


# A function for generating a simple MESSAGEix model
def model_setup(scen, years):
    scen.add_set('node', 'node')
    scen.add_set('commodity', 'electr')
    scen.add_set('level', 'level')
    scen.add_set('year', years)
    scen.add_set('type_year', years)
    scen.add_set('technology', ['tec1', 'tec2'])
    scen.add_set('mode', 'mode')
    output_specs = ['node', 'electr', 'level', 'year', 'year']
    dict_var_cost = {'tec1': 1, 'tec2': 2}

    for yr in years:
        scen.add_par('demand', ['node', 'electr', 'level', yr, 'year'],
                     1, 'GWa')
        for t in dict_var_cost.keys():
            tec_specs = ['node', t, yr, yr, 'mode']
            scen.add_par('output', tec_specs + output_specs, 1, 'GWa')
            scen.add_par('var_cost',
                         tec_specs + ['year'], dict_var_cost[t], 'USD/GWa')


# A function for adding sub-annual time steps to a MESSAGEix model
def add_seasonality(scen, seasons_dict):
    scen.add_set('time', list(set(seasons_dict.keys())))
    scen.add_set('lvl_temporal', 'season')
    for h in seasons_dict.keys():
        scen.add_set('map_temporal_hierarchy', ['season', h, 'year'])
        scen.add_par('duration_time', [h], seasons_dict[h], '-')


# A function for modifying model parameters after adding sub-annual time steps
def year_to_time(scen, parname, dict_par, filters=None):
    if filters:
        old = scen.par(parname, filters)
    else:
        old = scen.par(parname)
    scen.remove_par(parname, old)
    time_idx = [x for x in scen.idx_names(parname) if 'time' in x]
    for h in dict_par.keys():
        new = old.copy()
        for index in time_idx:
            new[index] = h
        new['value'] = dict_par[h] * old['value']
        scen.add_par(parname, new)


# A function for initiating sets/parameters required for storage equations
# NOTICE: this function can be deleted when storage parameters/sets are added
# to ixmp java backend
def init_storage(scen):

    # Initiating a set to specifiy storage level (no commodity balance needed)
    scen.init_set('level_storage')

    # Initiating a set to specifiy storage reservoir technology
    scen.init_set('storage_tec')

    # Initiating a set to map storage reservoir to its charger/discharger
    scen.init_set('map_tec_storage', idx_sets=['technology', 'storage_tec'])

    # Initiating a parameter to specify the order of sub-annual time steps
    scen.init_par('time_seq', idx_sets=['time'])

    # Initiating two parameters for specifying lower and upper bounds of
    # storage reservoir as percentage of installed reservoir capacity
    par_list_stor = ['bound_storage_lo', 'bound_storage_up']
    for parname in par_list_stor:
        scen.init_par(parname, idx_sets=['node', 'technology', 'commodity',
                                         'level', 'year', 'time'])
    # Initiating a parameter for specifying storage losses (percentage)
    scen.init_par('storage_loss', idx_sets=['node', 'technology', 'commodity',
                                         'level', 'year', 'time'])


# A function for adding storage technologies and parameterization
def add_storage_data(scen, time_order):
    # Adding level of storage
    scen.add_set('level', 'storage')

    # Adding storage technologies (reservoir, charger, and discharger)
    scen.add_set('technology', ['dam', 'pump', 'turbine'])

    # Adding a storage commodity
    scen.add_set('commodity', 'stored_com')

    # Specifying storage reservoir technology
    scen.add_set('storage_tec', 'dam')

    # Specifying storage level
    scen.add_set('level_storage', 'storage')

    # Adding mapping for storage and charger/discharger technologies
    for tec in ['pump', 'turbine']:
        scen.add_set('map_tec_storage', [tec, 'dam'])

    # Adding time sequence
    for h in time_order.keys():
        scen.add_par('time_seq', h, time_order[h], '-')

    # Adding minimum and maximum bound, and losses for storage (percentage)
    for y in set(scen.set('year')):
        for h in time_order.keys():
            scen.add_par('bound_storage_lo', ['node', 'dam', 'electr',
                                 'storage', y, h], 0.0, '%')

            scen.add_par('bound_storage_up', ['node', 'dam', 'electr',
                                 'storage', y, h], 1.0, '%')

            scen.add_par('storage_loss', ['node', 'dam', 'electr',
                                 'storage', y, h], 0.05, '%')

    # input, output, and capacity factor for storage technologies
    output = {'dam': ['node', 'stored_com', 'storage'],
                    'pump': ['node', 'stored_com', 'storage'],
                    'turbine': ['node', 'electr', 'level']}

    inp = {'dam': ['node', 'stored_com', 'storage'],
                    'pump': ['node', 'electr', 'level'],
                    'turbine': ['node', 'stored_com', 'storage']}

    var_cost = {'dam': 0, 'pump': 0.2, 'turbine': 0.3}

    for y in set(scen.set('year')):
        for h in time_order.keys():
            for t in ['dam', 'pump', 'turbine']:
                tec_sp = ['node', t, y, y, 'mode']
                scen.add_par('output', tec_sp + output[t] + [h, h], 1, 'GWa')
                scen.add_par('input', tec_sp + inp[t] + [h, h], 1, 'GWa')
                scen.add_par('var_cost', tec_sp + [h], var_cost[t], 'USD/GWa')


# Main function for building a model and adding seasonality and storage
def test_storage(test_mp):
    # First building a simple model
    scen = Scenario(test_mp, 'no_storage', 'standard', version='new')
    model_setup(scen, [2020])

    # Initiating missing sets/parameters if not yet in ixmp backend
    if not storage_in_java:
        init_storage(scen)
    scen.commit('initialized test model')
    scen.solve(case='no_seasonality')

    # Second, adding seasonality
    seasons_dict = {'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25}
    scen.remove_solution()
    scen.check_out()
    add_seasonality(scen, seasons_dict)
    dict_fixed = {'a': 1, 'b': 1, 'c': 1, 'd': 1}
    year_to_time(scen, 'output', dict_fixed)
    year_to_time(scen, 'var_cost', dict_fixed)
    dict_dem = {'a': 0.15, 'b': 0.2, 'c': 0.4, 'd': 0.25}
    year_to_time(scen, 'demand', dict_dem)
    scen.commit('initialized test model')
    scen.solve(case='no_storage')

    # Third, adding bound on the activity of the cheap technology
    scen.remove_solution()
    scen.check_out()
    for h in seasons_dict.keys():
        scen.add_par('bound_activity_up',
                     ['node', 'tec1', 2020, 'mode', h], 0.25, 'GWa')
    scen.commit('activity bounded')
    scen.solve(case='no_storage_bounded')
    cost_no_storage = scen.var('OBJ')['lvl']
    act_no = scen.var('ACT', {'technology': 'tec2'})['lvl'].sum()

    # Forth, adding storage technologies and their parameters
    scen.remove_solution()
    scen.check_out()
    time_order = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    add_storage_data(scen, time_order)
    scen.commit('storage added')
    scen.solve(case='with_storage')
    cost_with_storage = scen.var('OBJ')['lvl']
    act_with = scen.var('ACT', {'technology': 'tec2'})['lvl'].sum()

    # I. Tests for functionality of storage
    # I.1. Contribution of storage to the system
    assert cost_with_storage < cost_no_storage
    # Or, activity of expensive technology should be lower with storage
    assert act_with < act_no

    # I.2. Activity of discharger should be always =< activity of charger
    act_pump = scen.var('ACT', {'technology': 'pump'})['lvl']
    act_turb = scen.var('ACT', {'technology': 'turbine'})['lvl']
    assert act_turb.sum() < act_pump.sum()

    # I.3. Max activity of charger is lower than storage capacity
    max_pump = max(act_pump)
    cap_storage = float(scen.var('CAP', {'technology': 'dam'})['lvl'])
    assert max_pump <= cap_storage

    # I.4. Max activity of discharger is lower than storage capacity - losses
    max_turb = max(act_turb)
    loss = scen.par('storage_loss')['value'][0]
    assert max_turb <= cap_storage * (1 - loss)

    # II. Testing equations of storage (when added to ixmp variables)
    if storage_in_java:
        # II.1. Equality: storage content in the beginning and end is equal
        assert scen.var('STORAGE', {'time': 'a'})['lvl'] == scen.var('STORAGE',
                {'time': 'd'})['lvl']

        # II.2. Storage content should never exceed storage capacity
        assert max(scen.var('STORAGE')['lvl']) <= cap_storage

        # II.3. Commodity balance: charge - discharge - losses = 0
        change = scen.var('STORAGE_CHG').set_index(['year_act', 'time'])['lvl']
        loss = scen.par('storage_loss').set_index(['year', 'time'])['value']
        assert sum(change[change > 0] * (1 - loss)) == -sum(change[change < 0])

        # II.4. Energy balance: storage change + losses = storage content
        storage = scen.var('STORAGE').set_index(['year', 'time'])['lvl']
        assert storage[(2020, 'b')] * (1 - loss[(2020, 'b')]
                                       ) == -change[(2020, 'c')]