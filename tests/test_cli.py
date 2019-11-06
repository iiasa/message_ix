from click.testing import CliRunner
import pytest

from message_ix import cli


@pytest.fixture(scope='session')
def message_ix_cli(tmp_env):
    """A CliRunner object that invokes the message_ix command-line interface.

    :obj:`None` in *args* is automatically discarded.
    """
    class Runner(CliRunner):
        def invoke(self, *args, **kwargs):
            return super().invoke(cli.main, list(filter(None, args)),
                                  env=tmp_env, **kwargs)

    yield Runner().invoke


@pytest.mark.parametrize('opts', ['', '--branch=master', '--tag=1.2.0'])
def test_dl(message_ix_cli, opts, tmp_path):
    r = message_ix_cli('dl', opts, str(tmp_path))
    assert r.exit_code == 0
