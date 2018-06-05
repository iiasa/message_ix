import os
import pytest
import shutil
import tempfile
import ixmp


here = os.path.dirname(os.path.realpath(__file__))


def tempdir():
    return os.path.join(tempfile._get_default_tempdir(),
                        next(tempfile._get_candidate_names()))


@pytest.fixture(scope="session")
def test_mp():
    # start jvm
    ixmp.start_jvm()

    # launch Platform and connect to testdb (reconnect if closed)
    mp = ixmp.Platform(tempdir(), dbtype='HSQLDB')
    mp.open_db()

    yield mp
