from typing import Any

import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import make_df


def test_make_df() -> None:
    # DataFrame prepared for the message_ix parameter 'input' has the correct
    # shape
    result = make_df("input")
    assert result.shape == (1, 12)

    # …and column name(s)
    assert result.columns[0] == "node_loc"
    npt.assert_array_equal(result.columns[-2:], ("value", "unit"))

    # Check correct behaviour when adding key-worded args:
    defaults = dict(mode="all", time="year", time_origin="year", time_dest="year")
    result = make_df("output", **defaults)
    pdt.assert_series_equal(result["mode"], pd.Series("all", name="mode"))
    pdt.assert_series_equal(result["time"], pd.Series("year", name="time"))
    pdt.assert_series_equal(result["time_dest"], pd.Series("year", name="time_dest"))


def test_make_df_deprecated() -> None:
    # Importing from the old location generates a warning
    with pytest.warns(DeprecationWarning, match="from 'message_ix.utils' instead of"):
        from message_ix.utils import make_df as make_df_unused  # noqa: F401

    base: dict[str, Any] = {"foo": "bar"}
    exp = pd.DataFrame({"foo": "bar", "baz": [42, 43]})

    # Deprecated signature generates a warning
    with pytest.warns(DeprecationWarning, match="with a mapping or pandas object"):
        obs = make_df(base, baz=[42, 43])
    pdt.assert_frame_equal(obs, exp)

    with pytest.raises(ValueError):
        make_df(42, baz=[42, 42])

    # Equivalent
    base.update(baz=[42, 43])
    pdt.assert_frame_equal(pd.DataFrame.from_dict(base), exp)
