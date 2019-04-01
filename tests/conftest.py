import os
import pytest
import shutil
import tempfile

import ixmp


here = os.path.dirname(os.path.realpath(__file__))


def tempdir():
    return os.path.join(tempfile._get_default_tempdir(),
                        next(tempfile._get_candidate_names()))


def create_local_testdb():
    # copy testdb
    dst = tempdir()
    test_props = os.path.join(dst, 'test.properties')
    src = os.path.join(here, 'testdb')
    shutil.copytree(src, dst)

    # create properties file
    fname = os.path.join(here, 'testdb', 'test.properties_template')
    with open(fname, 'r') as f:
        lines = f.read()
        lines = lines.format(here=dst.replace("\\", "/"))
    with open(test_props, 'w') as f:
        f.write(lines)

    return test_props


@pytest.fixture(scope="session")
def test_mp():
    test_props = create_local_testdb()

    # start jvm
    ixmp.start_jvm()

    # launch Platform and connect to testdb (reconnect if closed)
    mp = ixmp.Platform(test_props)
    mp.open_db()

    yield mp


@pytest.fixture(scope="session")
def test_mp_props():
    test_props = create_local_testdb()

    # start jvm
    ixmp.start_jvm()

    yield test_props
