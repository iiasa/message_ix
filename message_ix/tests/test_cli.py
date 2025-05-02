import os
import re
from collections.abc import Callable
from pathlib import Path

import click
import pytest
from click.testing import Result

import message_ix
from message_ix import config


def test_copy_model(
    monkeypatch: pytest.MonkeyPatch,
    message_ix_cli: Callable[..., Result],
    tmp_path: Path,
    tmp_env: os._Environ[str],
    request: pytest.FixtureRequest,
    tmp_model_dir: Path,
) -> None:
    # Use Pytest monkeypatch fixture; this ensures the original value is restored at the
    # end of the test
    monkeypatch.setattr(
        config.values, "message_model_dir", config.get("message model dir")
    )

    r = message_ix_cli("copy-model", str(tmp_path))
    assert r.exit_code == 0, (r.exception, r.output)

    # Copying again without --overwrite fails
    r = message_ix_cli("copy-model", str(tmp_path))
    assert r.exit_code == 0
    assert "will not overwrite" in r.output

    # Copying with --overwrite succeeds
    r = message_ix_cli("copy-model", "--overwrite", str(tmp_path))
    assert r.exit_code == 0
    assert "Overwrite" in r.output

    # --set-default causes a configuration change
    assert config.get("message model dir") == Path(message_ix.__file__).parent / "model"
    r = message_ix_cli("copy-model", "--set-default", str(tmp_path))
    assert r.exit_code == 0
    assert config.get("message model dir") == tmp_path

    # Check if specific directory will be skipped

    # Create a GAMS runtime directory; these have names like "225a", etc.
    model_path = tmp_model_dir.joinpath("225c")
    model_path.mkdir()

    message_ix_cli("copy-model", "--source-dir", tmp_model_dir, f"{tmp_path}-dest")

    # Directory is ignored
    assert not Path(f"{tmp_path}-dest/225c").exists()


@pytest.mark.parametrize(
    "opts, exit_code",
    [
        ([""], 0),
        (["--branch=main"], 0),
        (["--tag=v1.2.0"], 0),
        # Nonexistent tag
        pytest.param(["--tag=v999"], 0, marks=pytest.mark.xfail(raises=ValueError)),
        # Can't use both --tag and --branch
        # TODO Why is this not actually raising a click.UsageError?
        pytest.param(
            ["--branch=main", "--tag=v1.2.0"],
            2,
            marks=pytest.mark.xfail(raises=click.UsageError),
        ),
    ],
)
def test_dl(
    message_ix_cli: Callable[..., Result],
    opts: list[str],
    exit_code: int,
    tmp_path: Path,
) -> None:
    r = message_ix_cli("dl", *opts, str(tmp_path))
    assert r.exit_code == exit_code, (r.exception, r.output)

    if opts == "":
        # Guess what the latest release will be from GitHub, using __version__.
        # This string is provided by setuptools-scm based on the most recent
        # Git tag, e.g. if the tag is 'v3.0.0' it may be '3.0.1.devN+etc'.
        major = message_ix.__version__.split(".")[0]

        # 'message-ix dl' defaults to the latest release
        pattern = re.compile(rf"Default: latest release v{major}\.\d+\.\d+")
        assert pattern.match(r.output)
