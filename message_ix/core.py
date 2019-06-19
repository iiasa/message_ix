import collections
import copy
import itertools
import os

import ixmp
from ixmp.utils import pd_read, pd_write, isscalar, check_year, logger
import pandas as pd

from . import default_paths


DEFAULT_SOLVE_OPTIONS = {
    'advind': 0,
    'lpmethod': 2,
    'threads': 4,
    'epopt': 1e-6,
}


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
                 cache=False):
        """Initialize a new message_ix.Scenario (input data and solution)
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
        """
        # it not a new scenario, `ixmp.Scenario` uses scheme assigned in the db
        scheme = 'MESSAGE' if version == 'new' else None
        # `ixmp.Scenario` verifies that MESSAGE-scheme scenarios are
        # initialized as `message_ix.Scenario` for correct API
        self.is_message_scheme = True

        super(Scenario, self).__init__(mp, model, scenario, version, scheme,
                                       annotation, cache)

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

    def remove_solution(self):
        """Remove the solution from the scenario

        Delete the model solution (variables and equations) and timeseries
        data marked as `meta=False` (see :meth:`TimeSeries.add_timeseries`)
        prior to the first model year.
        """
        if self.has_solution():
            self.clear_cache()  # reset Python data cache
            self._jobj.removeSolution()
        else:
            raise ValueError('This Scenario does not have a solution!')

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
        first = self.firstmodelyear

        if ya_args:
            if len(ya_args) != 3:
                raise ValueError('3 arguments are required if using `ya_args`')
            years_active = self.years_active(*ya_args)
            combos = itertools.product([ya_args[2]], years_active)
        else:
            combos = itertools.product(horizon, horizon)

        combos = [(int(y1), int(y2)) for y1, y2 in combos]

        def valid(y_v, y_a):
            ret = y_v <= y_a
            if in_horizon:
                ret &= y_a >= first
            return ret

        year_pairs = [(y_v, y_a) for y_v, y_a in combos if valid(y_v, y_a)]
        v_years, a_years = zip(*year_pairs)
        return pd.DataFrame({'year_vtg': v_years, 'year_act': a_years})

    @property
    def firstmodelyear(self):
        """Returns the first model year of the scenario."""
        return self._jobj.getFirstModelYear()

    def clone(self, model=None, scenario=None, annotation=None,
              keep_solution=True, shift_first_model_year=None, platform=None):
        """Clone the current scenario and return the clone.

        If the (`model`, `scenario`) given already exist on the
        :class:`Platform`, the `version` for the cloned Scenario follows the
        last existing version. Otherwise, the `version` for the cloned Scenario
        is 1.

        .. note::
            :meth:`clone` does not set or alter default versions. This means
            that a clone to new (`model`, `scenario`) names has no default
            version, and will not be returned by
            :meth:`Platform.scenario_list` unless `default=False` is given.

        Parameters
        ----------
        model : str, optional
            New model name. If not given, use the existing model name.
        scenario : str, optional
            New scenario name. If not given, use the existing scenario name.
        annotation : str, optional
            Explanatory comment for the clone commit message to the database.
        keep_solution : bool, default True
            If :py:const:`True`, include all timeseries data and the solution
            (vars and equs) from the source scenario in the clone.
            Otherwise, only timeseries data marked as `meta=True` (see
            :meth:`TimeSeries.add_timeseries`) or prior to `first_model_year`
            (see :meth:`TimeSeries.add_timeseries`) are cloned.
        shift_first_model_year: int, optional
            If given, the values of the solution are transfered to parameters
            `historical_*`, parameter `resource_volume` is updated, and the
            `first_model_year` is shifted. The solution is then discarded,
            see :meth:`TimeSeries.remove_solution`.
        platform : :class:`Platform`, optional
            Platform to clone to (default: current platform)
        """
        err = 'Cloning across platforms is only possible {}'
        if platform is not None and not keep_solution:
            raise ValueError(err.format('with `keep_solution=True`!'))

        if platform is not None and shift_first_model_year is not None:
            raise ValueError(err.format('without shifting model horizon!'))

        if shift_first_model_year is not None:
            keep_solution = False
            msg = 'Shifting first model year to {} and removing solution'
            logger().info(msg.format(shift_first_model_year))

        platform = platform or self.platform
        model = model or self.model
        scenario = scenario or self.scenario
        args = [platform._jobj, model, scenario, annotation, keep_solution]
        if check_year(shift_first_model_year, 'shift_first_model_year'):
            args.append(shift_first_model_year)

        return Scenario(platform, model, scenario, cache=self._cache,
                        version=self._jobj.clone(*args))

    def solve(self, model='MESSAGE', solve_options={}, **kwargs):
        """Solve the model for the Scenario.

        By default, :meth:`ixmp.Scenario.solve` is called with 'MESSAGE' as the
        *model* argument; see the documentation of that method for other
        arguments. *model* may also be overwritten, e.g.:

        >>> s.solve(model='MESSAGE-MACRO')

        Parameters
        ----------
        model : str, optional
            Type of model to solve, e.g. 'MESSAGE' or 'MESSAGE-MACRO'.
        solve_options : dict, optional
            name, value pairs to use for GAMS solver optfile. See
            :obj:`message_ix.DEFAULT_SOLVE_OPTIONS` for defaults
            and https://www.gams.com/latest/docs/S_CPLEX.html for possible
            keys.

        """
        # TODO: we generate the cplex.opt file on the fly. this is *not* safe
        # against race conditions. It is possible to generate opt files with
        # random names (see
        # https://www.gams.com/latest/docs/UG_GamsCall.html#GAMSAOoptfile);
        # however, we need to clean up the code in ixmp that passes arguments
        # to gams to do so.
        fname = os.path.join(default_paths.model_path(), 'cplex.opt')
        opts = copy.deepcopy(DEFAULT_SOLVE_OPTIONS)
        opts.update(solve_options)
        lines = '\n'.join('{} = {}'.format(k, v) for k, v in opts.items())
        with open(fname, 'w') as f:
            f.writelines(lines)
        ret = super(Scenario, self).solve(model=model, **kwargs)
        os.remove(fname)
        return ret

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
