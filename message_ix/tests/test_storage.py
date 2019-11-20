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
from itertools import product


# A function for generating a simple MESSAGEix model with two technologies
def model_setup(scen, years):
    scen.add_set('node', 'node')
    scen.add_set('commodity', 'electr')
    scen.add_set('level', 'level')
    scen.add_set('year', years)
    scen.add_set('type_year', years)
    scen.add_set('technology', ['tec1', 'tec2'])
    scen.add_set('mode', 'mode')
    output_specs = ['node', 'electr', 'level', 'year', 'year']
    # Two technologies, one cheaper than the other
    var_cost = {'tec1': 1, 'tec2': 2}
    for year, (tec, cost) in product(years, var_cost.items()):
        scen.add_par('demand', ['node', 'electr', 'level', year, 'year'],
                     1, 'GWa')
        tec_specs = ['node', tec, year, year, 'mode']
        scen.add_par('output', tec_specs + output_specs, 1, 'GWa')
        scen.add_par('var_cost', tec_specs + ['year'], cost, 'USD/GWa')


# A function for adding sub-annual time steps to a MESSAGEix model
def add_seasonality(scen, time_duration):
    scen.add_set('time', sorted(list(set(time_duration.keys()))))
    scen.add_set('lvl_temporal', 'season')
    for h, duration in time_duration.items():
        scen.add_set('map_temporal_hierarchy', ['season', h, 'year'])
        scen.add_par('duration_time', [h], duration, '-')


# A function for modifying model parameters after adding sub-annual time steps
def year_to_time(scen, parname, time_share):
    old = scen.par(parname)
    scen.remove_par(parname, old)
    time_idx = [x for x in scen.idx_names(parname) if 'time' in x]
    for h, share in time_share.items():
        new = old.copy()
        for index in time_idx:
            new[index] = h
        new['value'] = share * old['value']
        scen.add_par(parname, new)


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
        scen.add_par('time_seq', ['season', h], time_order[h], '-')

    # Adding input, output, and capacity factor for storage technologies
    output_spec = {'dam': ['node', 'stored_com', 'storage'],
                   'pump': ['node', 'stored_com', 'storage'],
                   'turbine': ['node', 'electr', 'level'],
                   }

    input_spec = {'dam': ['node', 'stored_com', 'storage'],
                  'pump': ['node', 'electr', 'level'],
                  'turbine': ['node', 'stored_com', 'storage'],
                  }

    var_cost = {'dam': 0, 'pump': 0.2, 'turbine': 0.3}
    stor_tecs = ['dam', 'pump', 'turbine']
    for year, h, tec in product(set(scen.set('year')), time_order.keys(),
                                stor_tecs):
        tec_sp = ['node', tec, year, year, 'mode']
        scen.add_par('output', tec_sp + output_spec[tec] + [h, h], 1, 'GWa')
        scen.add_par('input', tec_sp + input_spec[tec] + [h, h], 1, 'GWa')
        scen.add_par('var_cost', tec_sp + [h], var_cost[tec], 'USD/GWa')

    # Adding minimum and maximum bound, and losses for storage (percentage)
    for year, h in product(set(scen.set('year')), time_order.keys()):
        storage_spec = ['node', 'dam', 'storage', year, h]
        scen.add_par('bound_storage_lo', storage_spec, 0.0, '%')
        scen.add_par('bound_storage_up', storage_spec, 1.0, '%')
        scen.add_par('storage_loss', storage_spec, 0.05, '%')

    # Adding initial content of storage (optional)
    storage_spec = ['node', 'dam', 'storage', year, 'a']
    scen.add_par('init_storage', storage_spec, 0.08, 'GWa')

    # Adding a relation between storage content of two time steps (optional)
    yr_first = yr_last = scen.set('year').tolist()[0]
    time_first = 'a'
    time_last = 'd'
    scen.add_par('relation_storage', ['node', 'dam', 'storage',
                                      yr_first, yr_last,
                                      time_last, time_first], 0.5, '%')


# Main function for building a model with storage and testing the functionality
def storage_setup(test_mp, time_duration, comment):

    # First building a simple model and adding seasonality
    scen = Scenario(test_mp, 'no_storage', 'standard', version='new')
    model_setup(scen, [2020])
    add_seasonality(scen, time_duration)
    fixed_share = {'a': 1, 'b': 1, 'c': 1, 'd': 1}
    year_to_time(scen, 'output', fixed_share)
    year_to_time(scen, 'var_cost', fixed_share)
    demand_share = {'a': 0.15, 'b': 0.2, 'c': 0.4, 'd': 0.25}
    year_to_time(scen, 'demand', demand_share)
    scen.commit('initialized test model')
    scen.solve(case='no_storage' + comment)

    # Second adding bound on the activity of the cheap technology
    scen.remove_solution()
    scen.check_out()
    for h in time_duration.keys():
        scen.add_par('bound_activity_up',
                     ['node', 'tec1', 2020, 'mode', h], 0.25, 'GWa')
    scen.commit('activity bounded')
    scen.solve(case='no_storage_bounded' + comment)
    cost_no_storage = scen.var('OBJ')['lvl']
    act_no = scen.var('ACT', {'technology': 'tec2'})['lvl'].sum()

    # Third, adding storage technologies and their parameters
    scen.remove_solution()
    scen.check_out()
    time_order = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    add_storage_data(scen, time_order)
    scen.commit('storage added')
    scen.solve(case='with_storage' + comment)
    cost_with_storage = scen.var('OBJ')['lvl']
    act_with = scen.var('ACT', {'technology': 'tec2'})['lvl'].sum()

    # Forth. Tests for the functionality of storage
    # 1. Check the contribution of storage to the system
    assert cost_with_storage < cost_no_storage
    # Or, activity of expensive technology should be lower with storage
    assert act_with < act_no

    # 2. Activity of discharger <= activity of charger + initial content
    act_pump = scen.var('ACT', {'technology': 'pump'})['lvl']
    act_turb = scen.var('ACT', {'technology': 'turbine'})['lvl']
    initial_content = float(scen.par('init_storage')['value'])
    assert act_turb.sum() <= act_pump.sum() + initial_content

    # 3. Max activity of charger <= storage capacity
    max_pump = max(act_pump)
    cap_storage = float(scen.var('CAP', {'technology': 'dam'})['lvl'])
    assert max_pump <= cap_storage

    # 4. Max activity of discharger <= storage capacity - losses
    max_turb = max(act_turb)
    loss = scen.par('storage_loss')['value'][0]
    assert max_turb <= cap_storage * (1 - loss)

    # Fifth, testing equations of storage (when added to ixmp variables)
    if scen.has_var('STORAGE'):
        # 1. Equality: storage content in the beginning and end is equal
        storage_first = scen.var('STORAGE', {'time': 'a'})['lvl']
        storage_last = scen.var('STORAGE', {'time': 'd'})['lvl']
        assert storage_first == storage_last

        # 2. Storage content should never exceed storage capacity
        assert max(scen.var('STORAGE')['lvl']) <= cap_storage

        # 3. Commodity balance: charge - discharge - losses = 0
        change = scen.var('STORAGE_CHG').set_index(['year_act', 'time'])['lvl']
        loss = scen.par('storage_loss').set_index(['year', 'time'])['value']
        assert sum(change[change > 0] * (1 - loss)) == -sum(change[change < 0])

        # 4. Energy balance: storage change + losses = storage content
        storage = scen.var('STORAGE').set_index(['year', 'time'])['lvl']
        assert storage[(2020, 'b')] * (1 - loss[(2020, 'b')]
                                       ) == -change[(2020, 'c')]


# Storage test for different duration times
def test_storage(test_mp):
    '''
    Testing storage setup with equal and unequal duration of seasons"

    '''
    time_duration = {'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25}
    storage_setup(test_mp, time_duration, '_equal_time')

    time_duration = {'a': 0.3, 'b': 0.25, 'c': 0.25, 'd': 0.2}
    storage_setup(test_mp, time_duration, '_unequal_time')
