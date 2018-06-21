import collections
import ixmp
import itertools

import pandas as pd

from message_ix.utils import isscalar, logger


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
        """Rename a technology in a scenario

        Parameters
        ----------
        name : str
            name of the scenario object to change (e.g., 'technology')
        mapping : str
            mapping of old (current) to new names
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
