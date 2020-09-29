from message_ix.reporting import Reporter
from ixmp.reporting import configure

configure(units={'replace': {'-': ''}})


def _tec_collapse_callback(df):
    """Callback function to populate the IAMC 'variable' column."""
    df['variable'] = df['t']
    return df.drop(['t'], axis=1)


def _com_collapse_callback(df):
    """Callback function to populate the IAMC 'variable' column."""
    df['variable'] = df['c']
    return df.drop(['c'], axis=1)


class Plots(object):
    def __init__(self, scenario, region, input_costs='$/GWa'):
        self.rep = Reporter.from_scenario(scenario)
        self.region = region

        if input_costs == "$/MWa":
            self.cost_unit_conv = 1e3
        elif input_costs == "$/kWa":
            self.cost_unit_conv = 1e6
        else:
            self.cost_unit_conv = 1

    def plot_output(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.get('out:pyam')
        df.rename(variable={i: i.split('|')[3] for i
                            in df.variables()},
                  region={i: i.split('|')[0] for i
                          in df.regions()},
                  inplace=True)
        ax = df.filter(variable=tecs).bar_plot(stacked=True)
        ax.set_ylabel('GWa')
        ax.set_title('{} System Activity'.format(self.region))

    def plot_capacity(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.get('CAP:pyam')
        df.rename(variable={i: i.split('|')[1] for i
                            in df.variables()},
                  region={i: i.split('|')[0] for i
                          in df.regions()},
                  inplace=True)
        ax = df.filter(variable=tecs).bar_plot(stacked=True)
        ax.set_ylabel('GW')
        ax.set_title('{} System Capacity'.format(self.region))

    def plot_prices(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.full_key('PRICE_COMMODITY')
        new_key = self.rep.convert_pyam(
            quantities=df.drop('l'),
            year_time_dim='y',
            collapse=_com_collapse_callback)
        df = self.rep.get(new_key[0])
        df = df.filter(variable=tecs)
        df = df.convert_unit('', 'cents/kWhr',
                             1/8760*100*self.cost_unit_conv)
        ax = df.bar_plot(stacked=True)
        ax.set_ylabel('cents/kWhr')
        ax.set_title('{} System Prices'.format(self.region))
