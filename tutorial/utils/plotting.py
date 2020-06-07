import pandas as pd
import matplotlib.pyplot as plt


class Plots(object):
    def __init__(self, ds, country, firstyear=2010, input_costs='$/GWa'):
        self.ds = ds
        self.country = country
        self.firstyear = firstyear

        if input_costs == '$/MWa':
            self.cost_unit_conv = 1e3
        elif input_costs == '$/kWa':
            self.cost_unit_conv = 1e6
        else:
            self.cost_unit_conv = 1

    def historic_data(self, par, year_col, subset=None):
        df = self.ds.par(par)
        if subset is not None:
            df = df[df['technology'].isin(subset)]
        idx = [year_col, 'technology']
        df = df[idx + ['value']].groupby(idx).sum().reset_index()
        df = df.pivot(index=year_col, columns='technology',
                      values='value')
        return df

    def model_data(self, var, year_col='year_act', baseyear=False,
                   subset=None):
        df = self.ds.var(var)
        if subset is not None:
            df = df[df['technology'].isin(subset)]
        idx = [year_col, 'technology']
        df = (df[idx + ['lvl']]
              .groupby(idx)
              .sum()
              .reset_index()
              .pivot(index=year_col, columns='technology',
                     values='lvl')
              .rename(columns={'lvl': 'value'})
              )
        df = df[df.index >= self.firstyear]
        return df

    def equ_data(self, equ, value, baseyear=False, subset=None):
        df = self.ds.equ(equ)
        if not baseyear:
            df = df[df['year'] > self.firstyear]
        if subset is not None:
            df = df[df['commodity'].isin(subset)]
        df = df.pivot(index='year', columns='commodity', values=value)
        return df

    def plot_demand(self, light_demand, elec_demand):
        fig, ax = plt.subplots()
        light = light_demand['value']
        light.plot(ax=ax, label='light')
        e = elec_demand['value']
        e.plot(ax=ax, label='elec')
        (light + e).plot(ax=ax, label='total')
        plt.ylabel('GWa')
        plt.xlabel('Year')
        plt.legend(loc='best')

    def plot_activity(self, baseyear=False, subset=None):
        h = self.historic_data('historical_activity',
                               'year_act', subset=subset)
        m = self.model_data('ACT', baseyear=baseyear, subset=subset)
        df = pd.concat([h, m]) if not h.empty else m
        df.plot.bar(stacked=True)
        plt.title('{} Energy System Activity'.format(self.country.title()))
        plt.ylabel('GWa')
        plt.xlabel('Year')
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def plot_capacity(self, baseyear=False, subset=None):
        df = self.model_data('CAP', baseyear=baseyear, subset=subset)
        df.plot.bar(stacked=True)
        plt.title('{} Energy System Capacity'.format(self.country.title()))
        plt.ylabel('GW')
        plt.xlabel('Year')
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def plot_new_capacity(self, baseyear=False, subset=None):
        h = self.historic_data('historical_new_capacity',
                               'year_vtg', subset=subset)
        m = self.model_data('CAP_NEW', 'year_vtg',
                            baseyear=baseyear, subset=subset)
        df = pd.concat([h, m]) if not h.empty else m
        df.plot.bar(stacked=True)
        plt.title('{} Energy System New Capcity'.format(self.country.title()))
        plt.ylabel('GW')
        plt.xlabel('Year')
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def plot_prices(self, baseyear=False, subset=None):
        df = self.ds.var('PRICE_COMMODITY')
        if not baseyear:
            df = df[df['year'] > self.firstyear]
        if subset is not None:
            df = df[df['commodity'].isin(subset)]
        idx = ['year', 'commodity']
        df = (df[idx + ['lvl']]
              .groupby(idx)
              .sum().
              reset_index()
              .pivot(index='year', columns='commodity',
                     values='lvl')
              .rename(columns={'lvl': 'value'})
              )
        df = df / 8760 * 100 * self.cost_unit_conv
        df.plot.bar(stacked=False)
        plt.title('{} Energy System Prices'.format(self.country.title()))
        plt.ylabel('cents/kWhr')
        plt.xlabel('Year')
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
