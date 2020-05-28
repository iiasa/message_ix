from contextlib import contextmanager
import subprocess
import sys

import ixmp
import message_ix


def check_local_model(model, notebook, shell=False):
    mp = ixmp.Platform()
    if model in mp.scenario_list().model.unique():
        mp.close_db()
        return

    mp.close_db()
    pyversion = sys.version_info[0]
    cmd = [
        "jupyter",
        "nbconvert",
        notebook,
        f"--ExecutePreprocessor.kernel_name='python{pyversion}'",
        "--execute",
    ]
    subprocess.check_call(cmd, shell=shell)


@contextmanager
def read_scenario(platform, name, scen):
    mp = platform
    mp.open_db()
    ds = message_ix.Scenario(mp, name, scen)

    yield ds

    mp.close_db()


@contextmanager
def make_scenario(platform, country, name, base_scen, scen):
    mp = platform

    mp.open_db()
    base_ds = message_ix.Scenario(mp, name, base_scen)

    by = "by 'tutorial/utils/run_scenarios.py:make_scenario()'"
    ds = base_ds.clone(
        name, scen, "scenario generated {}, {} - {}".format(by, name, scen),
        keep_solution=False)
    ds.check_out()

    yield ds

    ds.commit("changes committed {}, {} - {}".format(by, name, scen))
    ds.set_as_default()
    ds.solve('MESSAGE')

    mp.close_db()
