# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import collections
import six

import message_ix
import ixmp


IAMC_IDX = ['region', 'variable', 'unit', 'year']


class PostProcess(object):
    """Execute postprocessing on a message_ix.Scenario

    Parameters
    ----------
    scenario : message_ix.Scenario
    """
    def __init__(self, scenario):
        if not isinstance(scenario, message_ix.Scenario):
            msg = 'Postprocess can only be used with a `message_ix.Scenario`'
            raise ValueError(msg)
        if np.isnan(scenario.var('OBJ')['lvl']):
            raise ValueError('this scenario has not been solved!')
        self.scenario = scenario
        self.data = pd.DataFrame(columns=IAMC_IDX + ['value'])
        self.data = self.data.reset_index(drop=True)\
            .set_index(IAMC_IDX)

    def activity(self, variable, region='node_loc', year='year_act'):
        """Aggregates the activity level across technologies
        and converts results to the IAMC template

        Parameters
        ----------
        variable: dict
            mapping of IAMC-variable to filters by variable/parameter columns
        region: str
            the variable/parameter column to be used for the IAMC region column
        year: str
            the variable/parameter column to be used for the IAMC year column
        """
        data = []
        act = self.scenario.var('ACT')
        for v, mapping in variable.items():
            df = _apply_filters(act, mapping)
            df['variable'] = v
            df['unit'] = ''
            df.rename(columns={region: 'region', year: 'year', 'lvl': 'value'},
                      inplace=True)
            df = df.groupby(IAMC_IDX).sum()['value']
            data.append(df)
        data = pd.concat(data).to_frame()
        self.data = data.combine_first(self.data)

    def finalize(self, comment=None):
        """Finalizes the reporting by committing to the database

        Parameters
        ----------
        comment: str, optional
            annotation for commit of timeseries to the database
        """
        try:
            self.scenario.check_out(timeseries_only=True)
            self.scenario.add_timeseries(self.data.reset_index())
            self.scenario.commit(comment or 'MESSAGEix postprocessing')
        except Exception:
            self.scenario.discard_changes()
            ixmp.logger().error('Error saving timeseries data to the database')


# %%  auxiliary functions

def _apply_filters(data, filters):
    keep = np.array([True] * len(data))
    for col, values in filters.items():
        values = values if islistable(values) else [values]
        keep &= [i in values for i in data[col]]
    return data[keep].copy()


def isstr(x):
    """Returns True if x is a string"""
    return isinstance(x, six.string_types)


def islistable(x):
    """Returns True if x is a list but not a string"""
    return isinstance(x, collections.Iterable) and not isstr(x)
