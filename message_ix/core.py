import collections
from functools import lru_cache
from itertools import product
import logging

import ixmp
from ixmp.utils import as_str_list, isscalar
import pandas as pd


log = logging.getLogger(__name__)

# Also print warnings to stderr
_sh = logging.StreamHandler()
_sh.setLevel(level=logging.WARNING)
log.addHandler(_sh)


class Scenario(ixmp.Scenario):
    """|MESSAGEix| Scenario.

    See :class:`ixmp.TimeSeries` for the meaning of arguments `mp`, `model`,
    `scenario`, `version`, and `annotation`. The `scheme` of a newly-created
    Scenario is always 'MESSAGE'.
    """
    def __init__(self, mp, model, scenario=None, version=None, annotation=None,
                 scheme=None, **kwargs):
        # If not a new scenario, use the scheme stored in the Backend
        if version == 'new':
            scheme = scheme or 'MESSAGE'

        if scheme not in ('MESSAGE', None):
            msg = f'Instantiate message_ix.Scenario with scheme {scheme}'
            raise ValueError(msg)

        super().__init__(
            mp=mp,
            model=model,
            scenario=scenario,
            version=version,
            annotation=annotation,
            scheme=scheme,
            **kwargs
        )

        # Scheme returned by database
        assert self.scheme == 'MESSAGE', self.scheme

    # Utility methods used by .equ(), .par(), .set(), and .var()

    @lru_cache()
    def _year_idx(self, name):
        """Return a sequence of (idx_set, idx_name) for 'year'-indexed dims.

        Since item dimensionality does not change, the the return value is
        lru_cache()'d for performance.
        """
        # filter() returns a 1-time generator, so convert to a fixed tuple()
        return tuple(
            # Keep only tuples where the idx_set is 'year'
            filter(lambda e: e[0] == 'year',
                   # Generate 2-tuples of (idx_set, idx_name)
                   zip(self.idx_sets(name), self.idx_names(name))))

    def _year_as_int(self, name, df):
        """Convert 'year'-indexed columns of *df* to :obj:`int` dtypes.

        :meth:`_year_idx` is used to retrieve a sequence of (idx_set, idx_name)
        for *only* the 'year'-indexed dimensions of item *name*.

        If at least one dimension is indexed by 'year', all such dimensions are
        converted to :obj:`int`. Otherwise, *df* is returned unmodified.
        """
        year_idx = self._year_idx(name)

        if len(year_idx):
            return df.astype({col_name: 'int' for _, col_name in year_idx})
        elif name == 'year':
            # The 'year' set itself
            return df.astype(int)
        else:
            return df

    # Override ixmp methods to convert 'year'-indexed columns to int

    def equ(self, name, filters=None):
        """Return equation data.

        Same as :meth:`ixmp.Scenario.equ`, except columns indexed by the
        |MESSAGEix| set ``year`` are returned with :obj:`int` dtype.

        Parameters
        ----------
        name : str
            Name of the equation.
        filters : dict (str -> list of str), optional
            Filters for the dimensions of the equation.

        Returns
        -------
        pd.DataFrame
            Filtered elements of the equation.
        """
        # Call ixmp.Scenario.equ(), then convert 'year'-indexed columns to ints
        return self._year_as_int(name, super().equ(name, filters))

    def par(self, name, filters=None):
        """Return parameter data.

        Same as :meth:`ixmp.Scenario.par`, except columns indexed by the
        |MESSAGEix| set ``year`` are returned with :obj:`int` dtype.

        Parameters
        ----------
        name : str
            Name of the parameter.
        filters : dict (str -> list of str), optional
            Filters for the dimensions of the parameter.

        Returns
        -------
        pd.DataFrame
            Filtered elements of the parameter.
        """
        return self._year_as_int(name, super().par(name, filters))

    def set(self, name, filters=None):
        """Return elements of a set.

        Same as :meth:`ixmp.Scenario.set`, except columns for multi-dimensional
        sets indexed by the |MESSAGEix| set ``year`` are returned with
        :obj:`int` dtype.

        Parameters
        ----------
        name : str
            Name of the set.
        filters : dict (str -> list of str), optional
            Mapping of `dimension_name` → `elements`, where `dimension_name`
            is one of the `idx_names` given when the set was initialized (see
            :meth:`init_set`), and `elements` is an iterable of labels to
            include in the return value.

        Returns
        -------
        pd.Series
            If *name* is an index set.
        pd.DataFrame
            If *name* is a set defined over one or more other, index sets.
        """
        return self._year_as_int(name, super().set(name, filters))

    def var(self, name, filters=None):
        """Return variable data.

        Same as :meth:`ixmp.Scenario.var`, except columns indexed by the
        |MESSAGEix| set ``year`` are returned with :obj:`int` dtype.

        Parameters
        ----------
        name : str
            Name of the variable.
        filters : dict (str -> list of str), optional
            Filters for the dimensions of the variable.

        Returns
        -------
        pd.DataFrame
            Filtered elements of the variable.
        """
        return self._year_as_int(name, super().var(name, filters))

    def cat_list(self, name):
        """Return a list of all categories for a mapping set.

        Parameters
        ----------
        name : str
            Name of the set.
        """
        return self._backend('cat_list', name)

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
        self._backend('cat_set_elements', name, str(cat), as_str_list(keys),
                      is_unique)

    def cat(self, name, cat):
        """Return a list of all set elements mapped to a category.

        Parameters
        ----------
        name : str
            Name of the set.
        cat : str
            Name of the category.

        Returns
        -------
        list of str or list of int
            :class:`int` is returned if *name* is 'year'.
        """
        return list(
            map(
                int if name == 'year' else lambda v: v,
                self._backend('cat_get_elements', name, cat)
            )
        )

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
        self.add_cat('year', 'firstmodelyear', first, is_unique=True)

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
        ya_args : tuple of (node, tec, yr_vtg), optional
            Arguments to :meth:`years_active`.
        in_horizon : bool, optional
            Only return years within the model horizon
            (:obj:`firstmodelyear` or later).

        Returns
        -------
        pandas.DataFrame
            with columns 'year_vtg' and 'year_act', in which each row is a
            valid pair.
        """
        first = self.firstmodelyear

        # Prepare lists of vintage (yv) and active (ya) years
        if ya_args:
            if len(ya_args) != 3:
                raise ValueError('3 arguments are required if using `ya_args`')
            ya = self.years_active(*ya_args)
            yv = ya[0:1]  # Just the first element, as a list
        else:
            # Product of all years
            yv = ya = self.set('year')

        # Predicate for filtering years
        def _valid(elem):
            yv, ya = elem
            return (yv <= ya) and (not in_horizon or (first <= ya))

        # - Cartesian product of all yv and ya.
        # - Filter only valid years.
        # - Convert to data frame.
        return pd.DataFrame(
            filter(_valid, product(yv, ya)),
            columns=['year_vtg', 'year_act'])

    def years_active(self, node, tec, yr_vtg):
        """Return years in which *tec* of *yr_vtg* can be active in *node*.

        The :ref:`parameters <params-tech>` ``duration_period`` and
        ``technical_lifetime`` are used to determine which periods are partly
        or fully within the lifetime of the technology.

        Parameters
        ----------
        node : str
            Node name.
        tec : str
            Technology name.
        yr_vtg : int or str
            Vintage year.

        Returns
        -------
        list of int
        """
        # Handle arguments
        filters = dict(node_loc=[node], technology=[tec])
        yv = int(yr_vtg)

        # Lifetime of the technology at the node
        lt = self.par('technical_lifetime', filters=filters).at[0, 'value']

        # Duration of periods
        data = self.par('duration_period')
        # Cumulative sum for periods including the vintage period
        data['age'] = data.where(data.year >= yv, 0)['value'].cumsum()

        # Return periods:
        # - the tec's age at the end of the *prior* period is less than or
        #   equal to its lifetime, and
        # - at or later than the vintage year.
        return data.where(data.age.shift(1, fill_value=0) < lt) \
                   .where(data.year >= yv)['year'] \
                   .dropna().astype(int).tolist()

    @property
    def firstmodelyear(self):
        """The first model year of the scenario.

        Returns
        -------
        int
        """
        return int(self.cat('year', 'firstmodelyear')[0])

    def clone(self, *args, **kwargs):
        """Clone the current scenario and return the clone.

        See :meth:`ixmp.Scenario.clone` for other parameters.

        Parameters
        ----------
        keep_solution : bool, optional
            If :py:const:`True`, include all timeseries data and the solution
            (vars and equs) from the source Scenario in the clone.
            Otherwise, only timeseries data marked as `meta=True` (see
            :meth:`TimeSeries.add_timeseries`) or prior to `first_model_year`
            (see :meth:`TimeSeries.add_timeseries`) are cloned.
        shift_first_model_year: int, optional
            If given, the values of the solution are transfered to parameters
            `historical_*`, parameter `resource_volume` is updated, and the
            `first_model_year` is shifted. The solution is then discarded,
            see :meth:`TimeSeries.remove_solution`.
        """
        # Call the parent method
        return super().clone(*args, **kwargs)

    def solve(self, model='MESSAGE', solve_options={}, **kwargs):
        """Solve MESSAGE or MESSAGE-MACRO for the Scenario.

        By default, :meth:`ixmp.Scenario.solve` is called with 'MESSAGE' as the
        *model* argument. *model* may also be overwritten, e.g.:

        >>> s.solve(model='MESSAGE-MACRO')

        Parameters
        ----------
        model : 'MESSAGE' or 'MACRO' or 'MESSAGE-MACRO', optional
            Model to solve.
        solve_options : dict (str -> str), optional
            Name to value mapping to use for GAMS CPLEX solver options file.
            See the :class:`.MESSAGE` class and :obj:`.DEFAULT_CPLEX_OPTIONS`.
        kwargs
            Many other options control the execution of the underlying GAMS
            code; see the :class:`.MESSAGE_MACRO` class and
            :class:`.GAMSModel`.
        """
        super().solve(model=model, solve_options=solve_options, **kwargs)

    def add_macro(self, data, scenario=None, check_convergence=True, **kwargs):
        """Add MACRO parametrization to the Scenario and calibrate."""
        # TODO document
        from .macro import EXPERIMENTAL, add_model_data, calibrate
        from .models import MACRO

        # Display a warning
        log.warning(EXPERIMENTAL)

        scenario = scenario or '_'.join([self.scenario, 'macro'])
        clone = self.clone(self.model, scenario, keep_solution=False)
        clone.check_out()

        # Add ixmp items: sets, parameters, variables, and equations
        MACRO.initialize(clone)

        add_model_data(self, clone, data)
        clone.commit('finished adding macro')
        calibrate(clone, check_convergence=check_convergence, **kwargs)
        return clone

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
        except RuntimeError:
            commit = False
        keys = list(mapping.keys())

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
