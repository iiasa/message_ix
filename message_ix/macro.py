import collections
import os

import pandas as pd

from functools import lru_cache

#
# TODOS:
#
# 1) all demands/prices assumed to be on USEFUL level, need to extend this
#    to support others
#

MACRO_INIT = {
    'sets': {
        'sector': None,
        'mapping_macro_sector': ['sector', 'commodity', 'level', ],
    },
    'pars': {
        'demand_MESSAGE': {
            'idx': ['node', 'sector', 'year', ],
            'unit': 'GWa',
            'data_key': 'demand',
        },
        'price_MESSAGE': {
            'idx': ['node', 'sector', 'year', ],
            'unit': 'USD/kWa',
            'data_key': 'price',
        },
        'cost_MESSAGE': {
            'idx': ['node', 'year', ],
            'unit': 'G$',
            'data_key': 'total_cost',
        },
        'gdp_calibrate': {
            'idx': ['node', 'year', ],
            'unit': 'T$',
        },
        'historical_gdp': {
            'idx': ['node', 'year', ],
            'unit': 'T$',
            'data_key': 'gdp0',
        },
        'MERtoPPP': {
            'idx': ['node', 'year', ],
            'unit': '-',
        },
        'kgdp': {
            'idx': ['node', ],
            'unit': '-',
        },
        'kpvs': {
            'idx': ['node', ],
            'unit': '-',
        },
        'depr': {
            'idx': ['node', ],
            'unit': '-',
        },
        'drate': {
            'idx': ['node', ],
            'unit': '-',
        },
        'esub': {
            'idx': ['node', ],
            'unit': '-',
        },
        'lotol': {
            'idx': ['node', ],
            'unit': '-',
        },
        'price_ref': {
            'idx': ['node', 'sector', ],
            'unit': 'USD/kWa',
        },
        'lakl': {
            'idx': ['node', ],
            'unit': '-',
            'data_key': 'aconst',
        },
        'prfconst': {
            'idx': ['node', 'sector', ],
            'unit': '-',
            'data_key': 'bconst',
        },
        'grow': {
            'idx': ['node', 'year', ],
            'unit': '-',
            'data_key': 'growth',
        },
        'aeei': {
            'idx': ['node', 'sector', 'year', ],
            'unit': '-',
        },
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
    'cost_ref': ['node', ],
    'demand_ref': ['node', 'sector', ],
}

VERIFY_INPUT_DATA = [
    'price_ref', 'lotol', 'esub', 'drate', 'depr', 'kpvs', 'kgdp',
    'gdp_calibrate', 'aeei', 'cost_ref', 'demand_ref', 'MERtoPPP',
]


def _validate_data(name, df, nodes, sectors, years):
    def validate(kind, values, df):
        if kind not in df:
            return

        diff = set(values) - set(df[kind])
        if diff:
            raise ValueError(
                'Not all {}s included in {} data: {}'.format(kind, name, diff)
            )

    # check required columns
    if name in MACRO_DATA_FOR_DERIVATION:
        cols = MACRO_DATA_FOR_DERIVATION[name]
    else:
        cols = MACRO_INIT['pars'][name]['idx']
    # TODO: cols += ['unit'] ?
    col_diff = set(cols) - set(df.columns)
    if col_diff:
        msg = 'Missing expected columns for {}: {}'
        raise ValueError(msg.format(name, col_diff))

    # check required column values
    checks = (
        ('node', nodes),
        ('sector', sectors),
        ('year', years),
    )

    for kind, values in checks:
        validate(kind, values, df)

    return cols


class Calculate(object):

    def __init__(self, s, data):
        """
        s : solved message scenario
        data : dict of parameter names to dataframes
        """
        self.data = data
        self.s = s

        good = isinstance(data, collections.Mapping) or os.path.exists(data)
        if not good:
            raise ValueError('Data argument is not a dictionary nor a file')
        if not isinstance(data, collections.Mapping) and os.path.exists(data):
            if not str(self.data).endswith('xlsx'):
                raise ValueError('Must provide excel-based data file')
            self.data = pd.read_excel(self.data, sheet_name=None)

        if not s.has_solution():
            raise RuntimeError('Scenario must have a solution to add MACRO')

        demand = s.var('DEMAND', filters={'level': 'useful'})
        self.nodes = demand['node'].unique()
        self.sectors = demand['commodity'].unique()
        self.years = demand['year'].unique()

    def read_data(self):
        par_diff = set(VERIFY_INPUT_DATA) - set(self.data)
        if par_diff:
            raise ValueError(
                'Missing required input data: {}'.format(par_diff))

        for name in self.data:
            idx = _validate_data(name, self.data[name],
                                 self.nodes, self.sectors, self.years)
            self.data[name] = self.data[name].set_index(idx)['value']

        # special check for gdp_calibrate
        check = self.data['gdp_calibrate']
        data_years = check.index.get_level_values('year')
        min_year_model = min(self.years)
        min_year_data = min(data_years)
        if not min_year_data < min_year_model:
            raise ValueError(
                'Must provide gdp_calibrate data prior to the modeling' +
                ' period in order to calculate growth rates'
            )
        # base year is most recent period PRIOR to the modeled period
        self.base_year = max(data_years[data_years < min_year_model])

    def derive_data(self):
        # calculate all necessary derived data, adding to self.data this is
        # done through method chaining, the bottom of which is aconst()
        self._growth()
        self._rho()
        self._gdp0()
        self._k0()
        self._total_cost()
        self._price()
        self._demand()
        self._bconst()
        self._aconst()

    @lru_cache()
    def _growth(self):
        gdp = self.data['gdp_calibrate']
        diff = gdp.groupby(level='node').diff()
        years = gdp.index.get_level_values('year')
        dt = pd.Series(years, name='year', index=years).diff()
        growth = (diff / gdp + 1) ** (1 / dt) - 1
        self.data['growth'] = growth.dropna()
        return self.data['growth']

    @lru_cache()
    def _rho(self):
        esub = self.data['esub']
        self.data['rho'] = (esub - 1) / esub
        return self.data['rho']

    @lru_cache()
    def _gdp0(self):
        gdp = self.data['gdp_calibrate']
        gdp0 = gdp.iloc[gdp.index.isin([self.base_year], level='year')]
        # get rid of year index
        self.data['gdp0'] = gdp0.reset_index(level='year', drop=True)
        return self.data['gdp0']

    @lru_cache()
    def _k0(self):
        kgdp = self.data['kgdp']
        gdp0 = self._gdp0()
        self.data['k0'] = kgdp * gdp0
        return self.data['k0']

    @lru_cache()
    def _total_cost(self):
        # read from scenario
        idx = ['node', 'year']
        # TODO: in the R code, this value is divided by 1000
        # do we need to do that here?!!?
        model_cost = self.s.var('COST_NODAL_NET')
        model_cost.rename(columns={'lvl': 'value'}, inplace=True)
        model_cost = model_cost[idx + ['value']]
        # get data provided in base year from data
        cost_ref = self.data['cost_ref'].reset_index()
        cost_ref['year'] = self.base_year
        # combine into one value
        total_cost = pd.concat([cost_ref, model_cost]).set_index(idx)['value']
        if total_cost.isnull().any():
            raise RuntimeError('NaN values found in total_cost calculation')
        self.data['total_cost'] = total_cost
        return total_cost

    @lru_cache()
    def _price(self):
        # read from scenario
        idx = ['node', 'sector', 'year']
        model_price = self.s.var('PRICE_COMMODITY',
                                 filters={'level': 'useful'})
        model_price.rename(columns={'lvl': 'value', 'commodity': 'sector'},
                           inplace=True)
        model_price = model_price[idx + ['value']]
        # get data provided in base year from data
        price_ref = self.data['price_ref'].reset_index()
        price_ref['year'] = self.base_year
        # combine into one value
        price = pd.concat([price_ref, model_price]).set_index(idx)['value']
        if price.isnull().any():
            raise RuntimeError('NaN values found in price calculation')
        self.data['price'] = price
        return price

    @lru_cache()
    def _demand(self):
        # read from scenario
        idx = ['node', 'sector', 'year']
        model_demand = self.s.var('DEMAND', filters={'level': 'useful'})
        model_demand.rename(columns={'lvl': 'value', 'commodity': 'sector'},
                            inplace=True)
        model_demand = model_demand[idx + ['value']]
        # get data provided in base year from data
        demand_ref = self.data['demand_ref'].reset_index()
        demand_ref['year'] = self.base_year
        # combine into one value
        demand = pd.concat([demand_ref, model_demand]).set_index(idx)['value']
        if demand.isnull().any():
            raise RuntimeError('NaN values found in demand calculation')
        self.data['demand'] = demand
        return demand

    @lru_cache()
    def _bconst(self):
        price_ref = self.data['price_ref']
        demand_ref = self.data['demand_ref']
        rho = self._rho()
        gdp0 = self._gdp0()
        # TODO: automatically get the units here!!
        bconst = price_ref / 1e3 * (gdp0 / demand_ref) ** (rho - 1)
        self.data['bconst'] = bconst
        return self.data['bconst']

    @lru_cache()
    def _aconst(self):
        bconst = self._bconst()
        demand_ref = self.data['demand_ref']
        rho = self._rho()
        gdp0 = self._gdp0()
        k0 = self._k0()
        kpvs = self.data['kpvs']
        # TODO: why name this partmp??
        partmp = (bconst * demand_ref ** rho).groupby(level='node').sum()
        # TODO: automatically get the units here!!
        aconst = ((gdp0 / 1e3) ** rho - partmp) / (k0 / 1e3) ** (rho * kpvs)
        self.data['aconst'] = aconst
        return self.data['aconst']


def init(s):
    for key, values in MACRO_INIT['sets'].items():
        s.init_set(key, values)
    for key, values in MACRO_INIT['pars'].items():
        try:
            s.init_par(key, values['idx'])
        except:
            pass  # already exists in the model, known for 'historical_gdp'
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


def add_model_data(base, clone, data):
    c = Calculate(base, data)
    c.read_data()
    c.derive_data()

    # TODO: we shouldn't have to have a for loop here
    for s in c.sectors:
        clone.add_set('sector', s)

    for name, values in MACRO_INIT['pars'].items():
        try:
            key = values.get('data_key', name)
            data = c.data[key].reset_index()
            data['unit'] = values['unit']
            clone.add_par(name, data)
        except Exception as e:
            msg = 'Error in adding parameter {}\n'.format(name)
            raise type(e)(msg + str(e))
