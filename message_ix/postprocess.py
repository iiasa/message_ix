# -*- coding: utf-8 -*-

import pandas as pd

import ixmp as ix

from ixmp.postprocess_replace import utils


def tec_filter(row):
    _filter = {'input': {'commodity': row['input_commodity'],
                         'level': row['input_level']},
               'output': {'commodity': row['output_commodity'],
                          'level': row['output_level']}}
    for p, f in _filter.items():
        _filter[p] = {k: v for k, v in f.items() if str(v) != 'nan'}
    _filter = {k: v for k, v in _filter.items() if v != {}}
    return _filter


class PostProcess(object):
    def __init__(self, ds):
        self.ds = ds

    def par_filter(self, par, col, f):
        return self.ds.par(par, f)[col]

    def technologies(self, filters={}, tec_set=None):
        '''This function finds the list of technologies based on the input/output
        and cat_tec filters and returns the list of unique technologies.
        '''
        apply_filter = lambda p, f: self.par_filter(
            p, 'technology', f).unique().tolist()

        if filters != {}:
            all_tecs = [apply_filter(p, f) for p, f in filters.items()]
        else:
            all_tecs = [self.ds.set('technology').tolist()]
        if tec_set is not None:
            all_tecs.append(tec_set)
        if all_tecs != []:
            all_tecs = set.intersection(*map(set, [list(i) for i in all_tecs]))
        return all_tecs

    def activity(self, tecs, time_col, metadata={}):
        _filter = {'technology': tecs}
        act = self.ds.var('ACT', _filter)
        return utils.make_ts(act, time_col, 'lvl', metadata=metadata)

    def total_capacity(self, tecs, time_col, metadata={}):
        _filter = {'technology': tecs}
        act = self.ds.var('CAP', _filter)
        return utils.make_ts(act, time_col, 'lvl', metadata=metadata)

    def new_capacity(self, tecs, time_col, metadata={}):
        _filter = {'technology': tecs}
        act = self.ds.var('CAP_NEW', _filter)
        return utils.make_ts(act, time_col, 'lvl', metadata=metadata)

    def activity_output(self, tecs, out_filter, time_col, metadata={}):
        _filter1 = {'technology': tecs}
        act = self.ds.var('ACT', _filter1)
        _filter2 = dict(out_filter, **_filter1)
        op = self.ds.par('output', _filter2)
        _df = utils.multiply_df(act, 'lvl', op, 'value')
        return utils.make_ts(_df, time_col, 'product', metadata=metadata)

    def activity_input(self, tecs, in_filter, time_col, metadata={}):
        _filter1 = {'technology': tecs}
        act = self.ds.var('ACT', _filter1)
        _filter2 = dict(in_filter, **_filter1)
        op = self.ds.par('input', _filter2)
        _df = utils.multiply_df(act, 'lvl', op, 'value')
        return utils.make_ts(_df, time_col, 'product', metadata=metadata)

    def emission(self, tecs, emis_filter, time_col, metadata={}):
        _filter1 = {'technology': tecs}
        act = self.ds.var('ACT', _filter1)
        _filter2 = dict(emis_filter, **_filter1)
        op = self.ds.par('emission_factor', _filter2)
        _df = utils.multiply_df(act, 'lvl', op, 'value')
        return utils.make_ts(_df, time_col, 'product', metadata=metadata)


def postprocess_from_excel(fname, ds):

    # import Excel
    xls = pd.ExcelFile(fname)

    pp = PostProcess(ds)

    data = {}
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        for i, row in df.iterrows():
            # Find Tecs
            tec_filters = tec_filter(row)
            tecs = pp.technologies(tec_filters)

            # create Timeseries
            if row['reporting_func'] == 'ACT':
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                data[row['variable']] = pp.activity(tecs, row['year'],
                                                    metadata=metadata)

            elif row['reporting_func'] == 'CAP':
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                data[row['variable']] = pp.total_capacity(tecs, row['year'],
                                                          metadata=metadata)

            elif row['reporting_func'] == 'CAP_NEW':
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                data[row['variable']] = pp.new_capacity(tecs, row['year'],
                                                        metadata=metadata)

            elif row['reporting_func'] == 'output':
                out_filter = tec_filters['output']
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                data[row['variable']] = pp.activity_output(tecs, out_filter,
                                                           row['year'],
                                                           metadata=metadata)

            elif row['reporting_func'] == 'input':
                in_filter = tec_filters['input']
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                data[row['variable']] = pp.activity_input(tecs, in_filter,
                                                          row['year'],
                                                          metadata=metadata)

            elif row['reporting_func'] == 'EMISS':
                metadata = {'unit': row['unit'], 'variable': row['variable']}
                emis_filter = {'emission': row['emission']}
                data[row['variable']] = pp.emission(tecs, emis_filter,
                                                    row['year'],
                                                    metadata=metadata)
    return data


if __name__ == '__main__':
    print('test')
