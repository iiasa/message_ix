import subprocess

from conftest import tempdir


def test_dl_default():
    cmd = 'messageix-dl --local_path={}'.format(tempdir())
    subprocess.check_call(cmd.split())


def test_dl_master():
    cmd = 'messageix-dl --branch=master --local_path={}'.format(tempdir())
    subprocess.check_call(cmd.split())
