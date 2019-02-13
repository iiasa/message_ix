import collections
import ixmp
import itertools
import warnings

import pandas as pd
import numpy as np

from ixmp.utils import pd_read, pd_write
from message_ix.utils import isscalar, logger


def _init_scenario(s, commit=False):
    """Initialize a MESSAGEix Scenario object with default values"""
    inits = (
        # {
        #  'test': False  # some test,
        #  'exec': [(pass, {'args': ()}), ],
        # },
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
    """|MESSAGEix| Scenario.

    This class extends :class:`ixmp.Scenario` and inherits all its methods. It
    defines additional methods specific to |MESSAGEix|.

    """

    def __init__(self, mp, model, scenario=None, version=None, annotation=None,
                 cache=False, clone=None, **kwargs):
        """Initialize a new message_ix.Scenario (structured input data and solution)
        or get an existing scenario from the ixmp database instance

        Parameters
        ----------
        mp : ixmp.Platform
        model : string
            model name
        scenario : string
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
        if 'scen' in kwargs:
            warnings.warn(
                '`scen` is deprecated and will be removed in the next' +
                ' release, please use `scenario`')
            scenario = kwargs.pop('scen')

        if version is not None and clone is not None:
            raise ValueError(
                'Can not provide both version and clone as arguments')
        if clone is not None:
            jscen = clone._jobj.clone(model, scenario, annotation,
                                      clone._keep_sol, clone._first_model_year)
        elif version == 'new':
            scheme = 'MESSAGE'
            jscen = mp._jobj.newScenario(model, scenario, scheme, annotation)
        elif isinstance(version, int):
            jscen = mp._jobj.getScenario(model, scenario, version)
        else:
            jscen = mp._jobj.getScenario(model, scenario)

        self.is_message_scheme = True

        super(Scenario, self).__init__(mp, model, scenario, jscen, cache=cache)

        if not self.has_solution():
            _init_scenario(self, commit=version != 'new')

    def cat_list(self, name):
        """return a list of all categories for a set

        Parameters
        ----------
        name : string
            name of the set
        """
        return ixmp.to_pylist(self._jobj.getTypeList(name))

    def add_cat(self, name, cat, keys, is_unique=False):
        """Map elements from *keys* to category *cat* within set *name*.

        Parameters
        ----------
        name : str
            Name of the set.
        cat : str
            Name of the category.
        keys : str or list of str
            Element keys to be added to the category mapping.
        is_unique: bool, optional
            If `True`, then *cat* must have only one element. An exception is
            raised if *cat* already has an element, or if ``len(keys) > 1``.
        """
        self._jobj.addCatEle(name, str(cat), ixmp.to_jlist(keys), is_unique)

    def cat(self, name, cat):
        """return a list of all set elements mapped to a category

        Parameters
        ----------
        name : string
            name of the set
        cat : string
            name of the category
        """
        return ixmp.to_pylist(self._jobj.getCatEle(name, cat))

    def has_solution(self):
        """Returns True if scenario currently has a solution"""
        try:
            return not np.isnan(self.var('OBJ')['lvl'])
        except Exception:
            return False

    def add_spatial_sets(self, data):
        """Add sets related to spatial dimensions of the model.

        Parameters
        ----------
        data : dict
            Mapping of `level` → `member`. Each member may be:

            - A single label for elements.
            - An iterable of labels for elements.
            - A recursive :class:`dict` following the same convention, defining
              sub-levels and their members.

        Examples
        --------
        >>> s = message_ix.Scenario()
        >>> s.add_spatial_sets({'country': 'Austria'})
        >>> s.add_spatial_sets({'country': ['Austria', 'Germany']})
        >>> s.add_spatial_sets({'country': {
        ...     'Austria': {'state': ['Vienna', 'Lower Austria']}}})

        """
        # TODO test whether unbalanced data or multiply-defined levels are
        # handled correctly. How to define 'Germany' as a country *only* but
        # two states within 'Austria'?
        # >>> s.add_spatial_sets({'country': {
        # ...     'Austria': {'country': 'Vienna'}}})
        # >>> s.add_spatial_sets({'country': {
        # ...     'Austria': {'state': 'Vienna'},
        # ...     'Canada': {'province': 'Ontario'},
        # ...     }})

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

    def add_horizon(self, data):
        """Add sets related to temporal dimensions of the model.

        Parameters
        ----------
        data : dict-like
            Year sets. "year" is a required key. "firstmodelyear" is optional;
            if not provided, the first element of "year" is used.

        Examples
        --------
        >>> s = message_ix.Scenario()
        >>> s.add_horizon({'year': [2010, 2020]})
        >>> s.add_horizon({'year': [2010, 2020], 'firstmodelyear': 2020})

        """
        if 'year' not in data:
            raise ValueError('"year" must be in temporal sets')
        horizon = data['year']
        self.add_set("year", horizon)

        first = data['firstmodelyear'] if 'firstmodelyear'\
            in data else horizon[0]
        self.add_cat("year", "firstmodelyear", first, is_unique=True)

    def vintage_and_active_years(self, ya_args=None, in_horizon=True):
        """Return sets of vintage and active years for use in data input.

        For a valid pair `(year_vtg, year_act)`, the following conditions are
        satisfied:

        1. Both the vintage year (`year_vtg`) and active year (`year_act`) are
           in the model's ``year`` set.
        2. `year_vtg` <= `year_act`.
        3. `year_act` <= the model's first year **or** `year_act` is in the
           smaller subset :meth:`ixmp.Scenario.years_active` for the given
           `ya_args`.

        Parameters
        ----------
        ya_args : tuple of (node, technology, year_vtg), optional
            Arguments to :meth:`ixmp.Scenario.years_active`.
        in_horizon : bool, optional
            Restrict years returned to be within the current model horizon.

        Returns
        -------
        pandas.DataFrame
            with columns, "year_vtg" and "year_act", in which each row is a
            valid pair.
        """
        horizon = self.set('year')
        first = self.cat('year', 'firstmodelyear')[0] or horizon[0]

        if ya_args:
            if len(ya_args) != 3:
                raise ValueError('3 arguments are required if using `ya_args`')
            years_active = self.years_active(*ya_args)
            combos = itertools.product([ya_args[2]], years_active)
        else:
            combos = itertools.product(horizon, horizon)

        # TODO: casting to int here is probably bad, but necessary for now
        first = int(first)
        combos = [(int(y1), int(y2)) for y1, y2 in combos]

        def valid(y_v, y_a):
            # TODO: casting to int here is probably bad
            ret = y_v <= y_a
            if in_horizon:
                ret &= y_a >= first
            return ret

        year_pairs = [(y_v, y_a) for y_v, y_a in combos if valid(y_v, y_a)]
        v_years, a_years = zip(*year_pairs)
        return pd.DataFrame({'year_vtg': v_years, 'year_act': a_years})

    def solve(self, model='MESSAGE', **kwargs):
        """Solve the Scenario.

        By default, :meth:`ixmp.Scenario.solve` is called with "MESSAGE" as the
        *model* argument; see the documentation of that method for other
        arguments. *model* may also be overwritten, e.g.:

        >>> s.solve(model='MESSAGE-MACRO')

        """
        return super(Scenario, self).solve(model=model, **kwargs)

    def clone(self, model=None, scenario=None, annotation=None,
              keep_solution=True, first_model_year=None, **kwargs):
        """clone the current scenario and return the new scenario

        Parameters
        ----------
        model : string
            new model name
        scenario : string
            new scenario name
        annotation : string
            explanatory comment (optional)
        keep_solution : boolean, default, True
            indicator whether to include an existing solution
            in the cloned scenario
        first_model_year: int, default None
            new first model year in cloned scenario
            ('slicing', only available for MESSAGE-scheme scenarios)
        """
        if 'keep_sol' in kwargs:
            warnings.warn(
                '`keep_sol` is deprecated and will be removed in the next' +
                ' release, please use `keep_solution`')
            keep_solution = kwargs.pop('keep_sol')
        if 'scen' in kwargs:
            warnings.warn(
                '`scen` is deprecated and will be removed in the next' +
                ' release, please use `scenario`')
            scenario = kwargs.pop('scen')

        self._keep_sol = keep_solution
        self._first_model_year = first_model_year or 0
        model = self.model if not model else model
        scenario = self.scenario if not scenario else scenario
        return Scenario(self.platform, model, scenario, annotation=annotation,
                        cache=self._cache, clone=self)

    def rename(self, name, mapping, keep=False):
        """Rename an element in a set

        Parameters
        ----------
        name : str
            name of the set to change (e.g., 'technology')
        mapping : str
            mapping of old (current) to new set element names
        keep : bool, optional, default: False
            keep the old values in the model
        """
        try:
            self.check_out()
            commit = True
        except:
            commit = False
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
                df = self.par(item, filters={name: [key]})
                if not df.empty:
                    df[name] = value
                    self.add_par(item, df)

        # this removes all instances of from_tech in the model
        if not keep:
            for key in keys:
                self.remove_set(name, key)

        # commit
        if commit:
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

    def read_excel(self, fname, add_units=False, commit_steps=False):
        """Read Excel file data and load into the scenario.

        Parameters
        ----------
        fname : string
            path to file
        add_units : bool
            add missing units, if any,  to the platform instance.
            default: False
        commit_steps : bool
            commit changes after every data addition.
            default: False
        """
        funcs = {
            'set': self.add_set,
            'par': self.add_par,
        }

        logger().info('Reading data from {}'.format(fname))
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
                logger().info('Loading data for {}'.format(name))
                funcs[ix_type](name, data)
        if commit_steps:
            self.commit('Loaded initial data from {}'.format(fname))
            self.check_out()

        # fill all other pars and sets, skipping those already done
        skip_sheets = ['ix_type_mapping'] + prefill
        for sheet_name, df in dfs.items():
            if sheet_name not in skip_sheets and not df.empty:
                logger().info('Loading data for {}'.format(sheet_name))
                if add_units and 'unit' in df.columns:
                    # add missing units
                    units = set(self.platform.units())
                    missing = set(df['unit'].unique()) - units
                    for unit in missing:
                        logger().info('Adding missing unit: {}'.format(unit))
                        self.platform.add_unit(unit)
                # load data
                ix_type = ix_types[sheet_name]
                funcs[ix_type](sheet_name, df)
                if commit_steps:
                    self.commit('Loaded {} from {}'.format(sheet_name, fname))
                    self.check_out()
