import pytest

import pandas as pd

from message_ix import Scenario
import message_ix.utils as utils
import message_ix.testing
import pandas.util.testing as pdt


def test_make_df():
    base = {'foo': 'bar'}
    exp = pd.DataFrame({'foo': 'bar', 'baz': [42, 42]})
    obs = utils.make_df(base, baz=[42, 42])
    pdt.assert_frame_equal(obs, exp)


def test_make_df_raises():
    pytest.raises(ValueError, utils.make_df, 42, baz=[42, 42])


def test_testing(test_mp):
    # Check the model creation functions in testing.py
    scen = message_ix.testing.make_dantzig(test_mp, True)
    assert isinstance(scen, Scenario)

    scen = message_ix.testing.make_dantzig(test_mp, solve=True,
                                           multi_year=True)
    assert isinstance(scen, Scenario)

    with pytest.raises(NotImplementedError):
        message_ix.testing.make_westeros(test_mp, True)
