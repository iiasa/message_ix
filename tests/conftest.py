from pathlib import Path

from click.testing import CliRunner
import message_ix
import pytest


# Use the fixtures test_mp, test_mp_props, and tmp_env from ixmp.testing
pytest_plugins = ['ixmp.testing']


# Hooks

def pytest_report_header(config, startdir):
    """Add the message_ix import path to the pytest report header."""
    return 'message_ix location: {}'.format(Path(message_ix.__file__).parent)


# Fixtures

@pytest.fixture(scope='session')
def test_data_path(request):
    """Path to the directory containing test data."""
    return Path(__file__).parent / 'data'


@pytest.fixture(scope='session')
def tutorial_path(request):
    """Path to the directory containing the tutorials."""
    return Path(__file__).parent / '..' / 'tutorial'


@pytest.fixture(scope='function')
def test_legacy_mp(request, tmp_env, test_data_path):
    """Path to a database properties file referring to a test database."""
    from ixmp.testing import create_test_mp

    yield from create_test_mp(request, test_data_path, 'message_ix_legacy')


@pytest.fixture(scope='session')
def message_ix_cli(tmp_env):
    """A CliRunner object that invokes the message_ix command-line interface.

    :obj:`None` in *args* is automatically discarded.
    """
    from message_ix import cli

    class Runner(CliRunner):
        def invoke(self, *args, **kwargs):
            return super().invoke(cli.main, list(filter(None, args)),
                                  env=tmp_env, **kwargs)

    yield Runner().invoke
