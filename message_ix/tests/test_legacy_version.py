import numpy as np
from ixmp import Platform
from ixmp.testing import create_test_platform

from message_ix import Scenario


def test_solve_legacy_scenario(tmp_path, test_data_path):
    db_path = create_test_platform(tmp_path, test_data_path, "legacy")
    mp = Platform(backend="jdbc", driver="hsqldb", path=db_path)
    scen = Scenario(mp, model="canning problem (MESSAGE scheme)", scenario="standard")
    exp = scen.var("OBJ")["lvl"]

    # solve scenario, assert that the new objective value is close to previous
    scen = scen.clone(keep_solution=False)
    scen.solve()
    assert np.isclose(exp, scen.var("OBJ")["lvl"])
