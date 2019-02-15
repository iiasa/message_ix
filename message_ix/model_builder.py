import pandas as pd
import message_ix


class ModelBuilder(object):

    def __init__(self, mp, model, scenario):
        self.scen = message_ix.Scenairo(mp, model, scenario, version='new')

    def finalize(self, msg):
        self.scen.commit('Using model builder to {}'.format(msg))

    def add_model_horizon(self, data):
        """Defines all time steps in the scenario.

        Parameters
        ----------
        data : list
            model data

        """
        if type(data) != list:
            raise ValueError(
                "Argument data needs to be type list")

        self.scen.add_set("year", data)

    def add_interestrate(self, data, unit='%'):
        """Defines the interest rate.

        Parameters
        ----------
        data : df, float
            intereste rate
        unit : string
            interest rate unit; default '%'

        """
        if type(data) not in [pd.core.frame.DataFrame, float]:
            raise ValueError(
                "Argument years needs to be either type",
                "pandas.DataFrame or float")

        if type(data) == pd.core.frame.DataFrame:
            df = data
        else:
            df = pd.DataFrame(
                {"year": self.scen.get_model_horizon(),
                 "value": data,
                 "unit": unit,
                 })

        self.scen.add_par("interestrate", df)

    def add_firstmodelyear(self, year):
        """Sets first model year.

        Parameters
        ----------
        year : int, string
            first model year
        update : boolean
            option whether to update existing values

        """
        if type(year) not in [str, int]:
            raise ValueError(
                "Argument years needs to be either type",
                "int or string")

        self.scen.add_cat("year", "firstmodelyear", year, unique=True)
