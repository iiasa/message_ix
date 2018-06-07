import subprocess
import sys

from contextlib import contextmanager

import ixmp

def check_local_model(model, notebook, shell=False):
    mp = ixmp.Platform(dbtype='HSQLDB')
    if model in mp.scenario_list().model.unique():
        mp.close_db()
        return

    mp.close_db()
    pyversion = sys.version_info[0]
    cmd = "jupyter nbconvert {} --ExecutePreprocessor.kernel_name='python{}' --execute"
    cmd = cmd.format(notebook, pyversion)
    subprocess.check_call(cmd.split(), shell=shell)


@contextmanager
def read_scenario(platform, name, scen):
    mp = platform
    close = mp.dbtype == 'HSQLDB'
    if close:
        mp.open_db()
    ds = mp.Scenario(name, scen)
    yield ds
    if close:
        try:
            mp.close_db()
        except:
            return


@contextmanager
def make_scenario(platform, country, name, base_scen, scen):
    mp = platform
    close = mp.dbtype == 'HSQLDB'
    if close:
        mp.open_db()
    base_ds = mp.Scenario(name, base_scen)
    ds = base_ds.clone(
        name, scen, "scenario generated by 'tutorial/tools.py:scenario_ds()', {} - {}".format(name, scen), keep_sol=False)
    ds.check_out()
    yield ds
    ds.commit(
        "changes committed by 'tutorial/tools.py:scenario_ds()' {} - {}".format(name, scen))
    ds.set_as_default()
    ds.solve('MESSAGE')
    if close:
        try:
            mp.close_db()
        except:
            return
