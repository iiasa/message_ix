import pytest

# Use the fixtures test_mp, test_mp_props, and tmp_env from ixmp.testing
pytest_plugins = ['ixmp.testing']


# Hooks

def pytest_addoption(parser):
    parser.addoption(
        '--test-r',
        action='store_true',
        help='also run tests of the ixmp R interface.',
    )


def pytest_runtest_setup(item):
    if 'rixmp' in item.keywords and \
       not item.config.getoption('--test-r'):
        pytest.skip('skipping rixmp test without --test-r flag')
