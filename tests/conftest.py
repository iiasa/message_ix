try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

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
