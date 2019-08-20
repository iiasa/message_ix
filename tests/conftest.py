try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

import message_ix
from ixmp import Platform
from ixmp.testing import create_local_testdb
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


@pytest.fixture(scope='session')
def test_legacy_mp(tmp_path_factory, test_data_path):
    """Path to a database properties file referring to a test database."""
    # adapting `ixmp.testing:test_mp()`
    db_path = Path(str(tmp_path_factory.mktemp('test_mp_props')))
    db_name = 'message_ix_legacy'
    props = create_local_testdb(db_path, test_data_path / 'testdb', db_name)
    mp = Platform(props)

    yield mp
