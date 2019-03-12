# -*- coding: utf-8 -*-

import numpy as np
import message_ix
import ixmp
from ixmp import logger
import pyam

GROUP_IDX = pyam.IAMC_IDX + ['year']


class Reporting(object):
    """Execute reporting on a message_ix.Scenario

    Parameters
    ----------
    scenario : message_ix.Scenario
    """
    def __init__(self, scenario):
        if not isinstance(scenario, message_ix.Scenario):
            msg = '`Reporting` can only be used with a `message_ix.Scenario`!'
            raise ValueError(msg)
        if np.isnan(scenario.var('OBJ')['lvl']):
            raise ValueError('This scenario has not been solved!')

        self.platform = scenario.platform
        self.scenario = scenario
        self.report = pyam.IamDataFrame(scenario)
        self.args = dict(model=self.scenario.model,
                         scenario=self.scenario.scenario, inplace=True)

        # check that scenario nodes are defined as regions in the database,
        # add if necessary
        regions = self.platform.regions()
        for i, (level, node, parent) \
                in self.scenario.set('map_spatial_hierarchy').iterrows():
            if node not in list(regions.region):
                self.platform.add_region(node, level, parent)
                logger().info('Added `{}` as a timeseries region'.format(node))
            else:
                rows = regions[regions.region == node][['hierarchy', 'parent']]
                _rows = list(map(tuple, rows.values))
                if (level, parent) not in _rows:
                    msg = 'The regional hierarchy of node `{}` differs '\
                          'from the defined region mapping in the platform!\n'\
                          'scenario: ({}, {}), database: {}'
                    logger().warning(msg.format(node, level, parent, _rows))

    def activity(self, variable, unit='', region='node_loc', year='year_act',
                 **kwargs):
        """Report the activity :math:`ACT` by technology, vintage, mode, etc.

        Parameters
        ----------
        variable: str
            variable identifier following the IAMC convention,
            e.g. (`Category|Subcategory|Specification`)
        unit: str
            the unit in which the technology activity is modelled
        region: str
            the variable/parameter column to be used for the IAMC region column
        year: str
            the variable/parameter column to be used for the IAMC year column
        **kwargs
            filters for variable columns
        """
        act = _apply_filters(self.scenario.var('ACT'), kwargs)\
            .groupby([region, year]).sum()['lvl'].reset_index()
        self.report.append(act, value='lvl', region=region, variable=variable,
                           unit=unit, year=year, **self.args)

    def aggregate(self, variable, components=None, units=None):
        """Compute the aggregate of timeseries components or sub-categories

        Parameters
        ----------
        variable: str
            variable identifier for which the aggregate should be computed
        components: list of str, default None
            list of variables, defaults to all sub-categories of `variable`
        units: str or list of str, default None
            filter variable and components for given unit(s)
        """
        self.report.aggregate(variable, components, units, append=True)

    def finalize(self, comment=None):
        """Finalizes the reporting by committing to the modeling platform

        Parameters
        ----------
        comment: str, optional
            annotation for commit of timeseries to the database
        """
        try:
            self.scenario.check_out(timeseries_only=True)
            self.scenario.add_timeseries(self.report.data)
            self.scenario.commit(comment or 'MESSAGEix postprocessing')
        except Exception:
            self.scenario.discard_changes()
            ixmp.logger().error('Error saving timeseries data to the database')


# %%  auxiliary functions

def _apply_filters(data, filters):
    """Downselect `data` using a `filters` dictionary like `col: values`"""
    keep = np.array([True] * len(data))
    for col, values in filters.items():
        values = [values] if pyam.isstr(values) else values
        keep &= [i in values for i in data[col]]
    return data[keep].copy()
