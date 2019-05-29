import subprocess


def test_dl_default(tmp_path):
    cmd = ['messageix-dl', '--local_path={}'.format(tmp_path)]
    subprocess.check_call(cmd)


def test_dl_master(tmp_path):
    cmd = ['messageix-dl', '--branch=master',
           '--local_path={}'.format(tmp_path)]
    subprocess.check_call(cmd)
