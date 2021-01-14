from pathlib import Path

import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import pytest

from message_ix import Scenario, make_df
from message_ix.testing import make_dantzig, make_westeros
from message_ix.util.sphinx_gams import files, transcribe_docs


def test_make_df():
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


def test_make_df_deprecated():
    # Importing from the old location generates a warning
    with pytest.warns(DeprecationWarning, match="from 'message_ix.utils' instead of"):
        from message_ix.utils import make_df as make_df_unused  # noqa: F401

    base = {"foo": "bar"}
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


def test_testing_make_scenario(test_mp):
    """Check the model creation functions in message_ix.testing."""
    # MESSAGE-scheme Dantzig problem can be created
    scen = make_dantzig(test_mp, True)
    assert isinstance(scen, Scenario)

    # Multi-year variant can be created
    scen = make_dantzig(test_mp, solve=True, multi_year=True)
    assert isinstance(scen, Scenario)

    # Westeros model can be created
    scen = make_westeros(test_mp, True)
    assert isinstance(scen, Scenario)


def test_files(tmp_path):
    # Names of input files
    in_exp = [tmp_path.joinpath(n).with_suffix(".gms") for n in ("foo", "bar")]
    # Touch files
    [p.write_text("") for p in in_exp]

    in_obs, out_obs = files(tmp_path, "baz")
    assert sorted(in_obs) == sorted(in_exp)
    assert sorted(out_obs) == [Path("baz", "bar.rst"), Path("baz", "foo.rst")]


CONTENT = """
** foo bar
 ***
  * bz baz2
  * bz * baz2
  *** bz baz3
***fig newton
"""

OUTPUT = """.. note:: This page is generated from inline documentation in ``a/b.gms``.

bz baz2
bz * baz2

"""


def test_transcribe_docs(tmp_path):
    """Full unit tests are a bit much for the nonce.."""

    f_in = tmp_path / "in.gms"
    f_out = tmp_path / "out.rst"

    f_in.write_text(CONTENT)

    with open(f_out, "w") as outfp:
        transcribe_docs(open(f_in), outfp, "a/b.gms")

    assert f_out.read_text() == OUTPUT
