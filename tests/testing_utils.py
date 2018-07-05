import os
import pytest
import shutil
import subprocess
import tempfile

import ixmp

from ixmp.default_path_constants import CONFIG_PATH

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


@pytest.fixture()
def test_mp_use_db_config_path():
    assert not os.path.exists(CONFIG_PATH)

    test_props = create_local_testdb()
    dirname = os.path.dirname(test_props)
    basename = os.path.basename(test_props)

    # configure
    cmd = 'ixmp-config --db_config_path {}'.format(dirname)
    subprocess.check_call(cmd.split())

    # start jvm
    ixmp.start_jvm()

    # launch Platform and connect to testdb (reconnect if closed)
    try:
        mp = ixmp.Platform(basename)
        mp.open_db()
    except:
        os.remove(CONFIG_PATH)
        raise

    yield mp

    os.remove(CONFIG_PATH)


@pytest.fixture()
def test_mp_use_default_dbprops_file():
    assert not os.path.exists(CONFIG_PATH)

    test_props = create_local_testdb()

    # configure
    cmd = 'ixmp-config --default_dbprops_file {}'.format(test_props)
    subprocess.check_call(cmd.split())

    # start jvm
    ixmp.start_jvm()

    # launch Platform and connect to testdb (reconnect if closed)
    try:
        mp = ixmp.Platform()
        mp.open_db()
    except:
        os.remove(CONFIG_PATH)
        raise

    yield mp

    os.remove(CONFIG_PATH)


@pytest.fixture(scope="session")
def test_mp_props():
    test_props = create_local_testdb()

    # start jvm
    ixmp.start_jvm()

    yield test_props
