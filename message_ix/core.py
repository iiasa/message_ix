import collections
import ixmp
import itertools

import pandas as pd

from ixmp.utils import pd_read, pd_write
from message_ix.utils import isscalar, logger


def _init_scenario(s, commit=False):
    """Initialize a MESSAGEix Scenario object with default values"""
    inits = (
        {  # required for subset all_modes, see model/data_load.gms
            'test': 'all' not in s.set('mode'),
            'exec': [(s.add_set, {'args': ('mode', 'all')})],
        },
        {  # required for share constraints
            'test': 'shares' not in s.set_list(),
            'exec': [
                (s.init_set, {'args': ('shares',)}),
                (s.init_set, {
                    'args': ('map_shares_commodity_level',),
                    'kwargs': dict(idx_sets=['shares', 'commodity', 'level', 'type_tec', 'type_tec'],
                                   idx_names=['shares', 'commodity', 'level', 'type_tec_share', 'type_tec_total'])
                }),
                (s.init_par, {
                    'args': ('share_factor_up',),
                    'kwargs': dict(idx_sets=['shares', 'node', 'year', 'time'],
                                   idx_names=['shares', 'node_loc', 'year_act', 'time'])
                }),
                (s.init_par, {
                    'args': ('share_factor_lo',),
                    'kwargs': dict(idx_sets=['shares', 'node', 'year', 'time'],
                                   idx_names=['shares', 'node_loc', 'year_act', 'time'])
                }),
            ],
        },
    )

    pass_idx = [i for i, init in enumerate(inits) if init['test']]
    if len(pass_idx) == 0:
        return  # leave early, all init tests pass

    if commit:
        s.check_out()
    for idx in pass_idx:
        for exec_info in inits[idx]['exec']:
            func = exec_info[0]
            args = exec_info[1].pop('args', tuple())
            kwargs = exec_info[1].pop('kwargs', dict())
            func(*args, **kwargs)

    if commit:
        s.commit('Initialized wtih standard sets and params')


class Scenario(ixmp.Scenario):

    def __init__(self, platform, model, scen, version=None, annotation=None,
                 cache=False, clone=None):
        """Initialize a new message_ix.Scenario (structured input data and solution)
        or get an existing scenario from the ixmp database instance

        Parameters
        ----------
        platform : ixmp.Platform
        model : string
            model name
        scen : string
            scenario name
        version : string or integer
            initialize a new scenario (if version == 'new'), or
            load a specific version from the database (if version is integer)
        annotation : string
            a short annotation/comment (when initializing a new scenario)
        cache : boolean
            keep all dataframes in memory after first query (default: False)
        clone : Scenario, optional
            make a clone of an existing scenario
        """
        if version is not None and clone is not None:
            raise ValueError(
                'Can not provide both version and clone as arguments')
        jobj = platform._jobj
        if clone is not None:
            jscen = clone._jobj.clone(model, scen, annotation,
                                      clone._keep_sol, clone._first_model_year)
        elif version == 'new':
            scheme = 'MESSAGE'
            jscen = jobj.newScenario(model, scen, scheme, annotation)
        elif isinstance(version, int):
            jscen = jobj.getScenario(model, scen, version)
        else:
            jscen = jobj.getScenario(model, scen)

        super(Scenario, self).__init__(
            platform, model, scen, jscen, cache=cache)

        if not self.has_solution():
            _init_scenario(self, commit=version != 'new')

    def has_solution(self):
        """Returns True if scenario currently has a solution"""
        try:
            return len(self.var('ACT')) > 0
        except:
            return False

    def add_spatial_sets(self, data):
        """Add sets related to spatial dimensions of the model

        Parameters
        ----------
        data : dict or other

        Examples
        --------
        data = {'country': 'Austria'}
        data = {'country': ['Austria', 'Germany']}
        data = {'country': {'Austria': {'state': ['Vienna', 'Lower Austria']}}}
        """
        nodes = []
        levels = []
        hierarchy = []

        def recurse(k, v, parent='World'):
            if isinstance(v, collections.Mapping):
                for _parent, _data in v.items():
                    for _k, _v in _data.items():
                        recurse(_k, _v, parent=_parent)

            level = k
            children = [v] if isscalar(v) else v
            for child in children:
                hierarchy.append([level, child, parent])
                nodes.append(child)
            levels.append(level)

        for k, v in data.items():
            recurse(k, v)

        self.add_set("node", nodes)
        self.add_set("lvl_spatial", levels)
        self.add_set("map_spatial_hierarchy", hierarchy)

    def add_horizon(scenario, data):
        """Add sets related to temporal dimensions of the model

        Parameters
        ----------
        scenario : ixmp.Scenario
        data : dict or other

        Examples
        --------
        data = {'year': [2010, 2020]}
        data = {'year': [2010, 2020], 'firstmodelyear': 2020}
        """
        if 'year' not in data:
            raise ValueError('"year" must be in temporal sets')
        horizon = data['year']
        scenario.add_set("year", horizon)

        first = data['firstmodelyear'] if 'firstmodelyear' in data else horizon[0]
        scenario.add_cat("year", "firstmodelyear", first, is_unique=True)

    def vintage_and_active_years(self):
        """Return a 2-tuple of valid pairs of vintage years and active years for
        use with data input.
        """
        horizon = self.set('year')
        combinations = itertools.product(horizon, horizon)
        year_pairs = [(y_v, y_a) for y_v, y_a in combinations if y_v <= y_a]
        v_years, a_years = zip(*year_pairs)
        return v_years, a_years

    def solve(self, **kwargs):
        """Solve a MESSAGE Scenario. See ixmp.Scenario.solve() for arguments"""
        return super(Scenario, self).solve(model='MESSAGE', **kwargs)

    def clone(self, model=None, scen=None, annotation=None, keep_sol=True,
              first_model_year=None):
        """clone the current scenario and return the new scenario

        Parameters
        ----------
        model : string
            new model name
        scen : string
            new scenario name
        annotation : string
            explanatory comment (optional)
        keep_sol : boolean, default: True
            indicator whether to include an existing solution
            in the cloned scenario
        first_model_year: int, default None
            new first model year in cloned scenario
            ('slicing', only available for MESSAGE-scheme scenarios)
        """
        self._keep_sol = keep_sol
        self._first_model_year = first_model_year or 0
        model = self.model if not model else model
        scen = self.scenario if not scen else scen
        return Scenario(self.platform, model, scen, annotation=annotation,
                        cache=self._cache, clone=self)

    def rename(self, name, mapping):
        """Rename an element in a set

        Parameters
        ----------
        name : str
            name of the set to change (e.g., 'technology')
        mapping : str
            mapping of old (current) to new set element names
        """
        self.check_out()
        keys = list(mapping.keys())
        values = list(mapping.values())

        # search for from_tech in sets and replace
        for item in self.set_list():
            ix_set = self.set(item)
            if isinstance(ix_set, pd.DataFrame):
                if name in ix_set.columns and not ix_set.empty:
                    for key, value in mapping.items():
                        df = ix_set[ix_set[name] == key]
                        if not df.empty:
                            df[name] = value
                            self.add_set(item, df)
            elif ix_set.isin(keys).any():  # ix_set is pd.Series
                for key, value in mapping.items():
                    if ix_set.isin([key]).any():
                        self.add_set(item, value)

        # search for from_tech in pars and replace
        for item in self.par_list():
            if name not in self.idx_names(item):
                continue
            for key, value in mapping.items():
                df = self.par(item, filters={name: key})
                if not df.empty:
                    df[name] = value
                    self.add_par(item, df)

        # this removes all instances of from_tech in the model
        for key in keys:
            self.remove_set(name, key)

        # commit
        self.commit('Renamed {} using mapping {}'.format(name, mapping))

    def to_excel(self, fname):
        """Save a scenario as an Excel file. NOTE: Cannot export
        solution currently (only model data) due to limitations in excel sheet
        names (cannot have multiple sheet names which are identical except for
        upper/lower case).

        Parameters
        ----------
        fname : string
            path to file
        """
        funcs = {
            'set': (self.set_list, self.set),
            'par': (self.par_list, self.par),
        }
        ix_name_map = {}
        dfs = {}
        for ix_type, (list_func, get_func) in funcs.items():
            for item in list_func():
                df = get_func(item)
                df = pd.Series(df) if isinstance(df, dict) else df
                if not df.empty:
                    dfs[item] = df
                    ix_name_map[item] = ix_type

        # map names to ix types
        df = pd.Series(ix_name_map).to_frame(name='ix_type')
        df.index.name = 'item'
        df = df.reset_index()
        dfs['ix_type_mapping'] = df

        pd_write(dfs, fname, index=False)

    def read_excel(self, fname):
        """Read Excel file data and load into the scenario.

        Parameters
        ----------
        fname : string
            path to file
        """
        funcs = {
            'set': self.add_set,
            'par': self.add_par,
        }

        dfs = pd_read(fname, sheet_name=None)

        # get item-type mapping
        df = dfs['ix_type_mapping']
        ix_types = dict(zip(df['item'], df['ix_type']))

        # fill in necessary items first (only sets for now)
        col = 0  # special case for prefill set Series

        def is_prefill(x):
            return dfs[x].columns[0] == col and len(dfs[x].columns) == 1

        prefill = [x for x in dfs if is_prefill(x)]
        for name in prefill:
            data = list(dfs[name][col])
            if len(data) > 0:
                ix_type = ix_types[name]
                funcs[ix_type](name, data)

        # fill all other pars and sets, skipping those already done
        skip_sheets = ['ix_type_mapping'] + prefill
        for sheet_name, df in dfs.items():
            if sheet_name not in skip_sheets and not df.empty:
                ix_type = ix_types[sheet_name]
                funcs[ix_type](sheet_name, df)
