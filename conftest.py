import os

# Use the fixtures test_mp, test_mp_props, and tmp_env from ixmp.testing
pytest_plugins = ["ixmp.testing"]

# Hooks


def pytest_sessionstart(session):
    """Use only 2 threads for CPLEX on GitHub Actions runners with 2 CPU cores."""
    import message_ix.models

    if "GITHUB_ACTIONS" in os.environ:
        message_ix.models.DEFAULT_CPLEX_OPTIONS["threads"] = 2

