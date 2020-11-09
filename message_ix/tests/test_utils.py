import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import Scenario
import message_ix.utils
import message_ix.testing


def test_make_df():
    base = {'foo': 'bar'}
    exp = pd.DataFrame({'foo': 'bar', 'baz': [42, 42]})
    obs = message_ix.utils.make_df(base, baz=[42, 42])
    pdt.assert_frame_equal(obs, exp)


def test_make_df_raises():
    pytest.raises(ValueError, message_ix.utils.make_df, 42, baz=[42, 42])


def test_testing_make_scenario(test_mp):
    """Check the model creation functions in message_ix.testing."""

    # MESSAGE-scheme Dantzig problem can be created
    scen = message_ix.testing.make_dantzig(test_mp, True)
    assert isinstance(scen, Scenario)

    # Multi-year variant can be created
    scen = message_ix.testing.make_dantzig(test_mp, solve=True,
                                           multi_year=True)
    assert isinstance(scen, Scenario)

    # Westeros model can be created
    scen = message_ix.testing.make_westeros(test_mp, True)
    assert isinstance(scen, Scenario)
