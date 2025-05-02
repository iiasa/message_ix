from pathlib import Path

from message_ix.util.sphinx_gams import files, transcribe_docs


def test_files(tmp_path: Path) -> None:
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


def test_transcribe_docs(tmp_path: Path) -> None:
    """Full unit tests are a bit much for the nonce.."""

    f_in = tmp_path / "in.gms"
    f_out = tmp_path / "out.rst"

    f_in.write_text(CONTENT)

    with open(f_out, "w") as outfp:
        transcribe_docs(open(f_in), outfp, "a/b.gms")

    assert f_out.read_text() == OUTPUT
