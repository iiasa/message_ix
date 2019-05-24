import os
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

import ixmp
from ixmp.testing import create_local_testdb
import message_ix
import pytest


# pytest hooks

def pytest_report_header(config, startdir):
    """Add the message_ix import path to the pytest report header."""
    return 'message_ix location: {}'.format(Path(message_ix.__file__).parent)


def pytest_sessionstart(session):
    """Unset any configuration read from the user's directory."""
    ixmp.config._config.clear()
    print(ixmp.config._config.values)


# Fixtures

@pytest.fixture(scope='session')
def test_data_path(request):
    """Path to the directory containing test data."""
    return Path(__file__).parent / 'data'


@pytest.fixture
def tutorial_path(request):
    """Path to the directory containing tutorials."""
    return Path(__file__).parent / '..' / 'tutorial'


@pytest.fixture(scope='session')
def tmp_env(tmp_path_factory):
    """Return the os.environ dict with the IXMP_DATA variable set.

    IXMP_DATA will point to a temporary directory that is unique to the
    test session. ixmp configuration (i.e. the 'config.json' file) can be
    written and read in this directory without modifying the current user's
    configuration.
    """
    os.environ['IXMP_DATA'] = str(tmp_path_factory.mktemp('config'))

    yield os.environ


@pytest.fixture(scope="session")
def test_mp(tmp_path_factory, test_data_path):
    """An ixmp.Platform connected to a temporary, local database.

    *test_mp* is used across the entire test session, so the contents of the
    database may reflect other tests already run.
    """
    # casting to Path(str()) is a hotfix due to errors upstream in pytest on
    # Python 3.5 (at least, perhaps others), there is an implicit cast to
    # python2's pathlib which is incompatible with python3's pathlib Path
    # objects.  This can be taken out once it is resolved upstream and CI is
    # setup on multiple Python3.x distros.
    db_path = Path(str(tmp_path_factory.mktemp('test_mp')))
    test_props = create_local_testdb(db_path, test_data_path / 'testdb')

    # launch Platform and connect to testdb (reconnect if closed)
    mp = ixmp.Platform(test_props)
    mp.open_db()

    yield mp


@pytest.fixture(scope="session")
def test_mp_props(tmp_path_factory, test_data_path):
    """Path to a database properties file referring to a test database."""
    # casting to Path(str()) is a hotfix due to errors upstream in pytest on
    # Python 3.5 (at least, perhaps others), there is an implicit cast to
    # python2's pathlib which is incompatible with python3's pathlib Path
    # objects.  This can be taken out once it is resolved upstream and CI is
    # setup on multiple Python3.x distros.
    db_path = Path(str(tmp_path_factory.mktemp('test_mp_props')))
    test_props = create_local_testdb(db_path, test_data_path / 'testdb')

    yield test_props
