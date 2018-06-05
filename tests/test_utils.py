import pytest

import pandas as pd

import message_ix.utils as utils
import pandas.util.testing as pdt


def test_make_df():
    base = {'foo': 'bar'}
    exp = pd.DataFrame({'foo': 'bar', 'baz': [42, 42]})
    obs = utils.make_df(base, baz=[42, 42])
    pdt.assert_frame_equal(obs, exp)


def test_make_df_raises():
    pytest.raises(ValueError, utils.make_df, 42, baz=[42, 42])
