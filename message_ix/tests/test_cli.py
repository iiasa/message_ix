from pathlib import Path

import pytest

import message_ix
from message_ix import config


def test_copy_model(message_ix_cli, tmp_path, tmp_env):
    r = message_ix_cli('copy-model', str(tmp_path))
    assert r.exit_code == 0

    # Copying again without --overwrite fails
    r = message_ix_cli('copy-model', str(tmp_path))
    assert r.exit_code == 0
    assert 'will not overwrite' in r.output

    # Copying with --overwrite succeeds
    r = message_ix_cli('copy-model', '--overwrite', str(tmp_path))
    assert r.exit_code == 0
    assert 'Overwriting' in r.output

    # --set-default causes a configuration change
    assert config.get('message model dir') == \
        Path(message_ix.__file__).parent / 'model'
    r = message_ix_cli('copy-model', '--set-default', str(tmp_path))
    assert r.exit_code == 0
    assert config.get('message model dir') == tmp_path


@pytest.mark.parametrize('opts', [
    '',
    '--branch=master',
    '--tag=v1.2.0',
    # Nonexistent tag
    pytest.param('--tag=v999', marks=pytest.mark.xfail(raises=AssertionError)),
])
def test_dl(message_ix_cli, opts, tmp_path):
    r = message_ix_cli('dl', opts, str(tmp_path))

    if r.exit_code != 0:
        # Debugging information
        print(r.exception, r.output)
        assert False
    print(r.exception, r.output)

    if opts == "":
        assert "Default: latest release v2.0.0" in r.output
