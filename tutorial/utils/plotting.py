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
    def __init__(self, scenario, input_costs='$/GWa'):
        self.rep = Reporter.from_scenario(scenario)
        self.model_name = scenario.model
        self.scen_name = scenario.scenario

        if input_costs == "$/MWa":
            self.cost_unit_conv = 1e3
        elif input_costs == "$/kWa":
            self.cost_unit_conv = 1e6
        else:
            self.cost_unit_conv = 1

    def plot_output(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.full_key('out')
        new_key = self.rep.convert_pyam(
            quantities=df.drop('h', 'hd', 'm', 'nd',
                               'yv', 'c', 'l'),
            year_time_dim='ya',
            collapse=_tec_collapse_callback)
        df = self.rep.get(new_key[0])
        model = df.data.model.unique()[0]
        scenario = df.data.scenario.unique()[0]
        region = df.data.region.unique()[0]
        ax = df.filter(
            model=model,
            scenario=scenario,
            region=region,
            variable=tecs).bar_plot(stacked=True)
        ax.set_ylabel('GWa')
        ax.set_title('Westeros System Activity')

    def plot_capacity(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.full_key('CAP')
        new_key = self.rep.convert_pyam(
            quantities=df.drop('yv'),
            year_time_dim='ya',
            collapse=_tec_collapse_callback)
        df = self.rep.get(new_key[0])
        model = df.data.model.unique()[0]
        scenario = df.data.scenario.unique()[0]
        region = df.data.region.unique()[0]
        ax = df.filter(
            model=model,
            scenario=scenario,
            region=region,
            variable=tecs).bar_plot(stacked=True)
        ax.set_ylabel('GW')
        ax.set_title('Westeros System Capacity')

    def plot_prices(self, tecs):
        if type(tecs) != list:
            tecs = [tecs]
        df = self.rep.full_key('PRICE_COMMODITY')
        new_key = self.rep.convert_pyam(
            quantities=df.drop('l'),
            year_time_dim='y',
            collapse=_com_collapse_callback)
        df = self.rep.get(new_key[0])
        model = df.data.model.unique()[0]
        scenario = df.data.scenario.unique()[0]
        region = df.data.region.unique()[0]
        df = df.filter(
            model=model,
            scenario=scenario,
            region=region,
            variable=tecs)
        df = df.convert_unit('', 'cents/kWhr',
                             1/8760*100*self.cost_unit_conv)
        ax = df.bar_plot(stacked=True)
        ax.set_ylabel('cents/kWhr')
        ax.set_title('Westeros System Prices')
