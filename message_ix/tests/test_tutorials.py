import logging
import os
import sys
from shutil import copyfile
from typing import Union

import numpy as np
import pytest
from ixmp.testing import get_cell_output, run_notebook

# Shorthands for tutorial directories/file names.
AT = "Austrian_energy_system"
W = "westeros"

# Common marks for some test cases
GHA = "GITHUB_ACTIONS" in os.environ
MARK = [
    pytest.mark.skipif(  # 0
        condition=GHA and sys.platform == "linux",
        reason="IR kernel times out on GitHub Actions Ubuntu runners",
    ),
    pytest.mark.xfail(  # 1
        condition=GHA and sys.platform == "darwin",
        reason="Always fails on GitHub Action macOS runners",
    ),
]

# Affects all tests in the file
pytestmark = [
    pytest.mark.tutorial,
    pytest.mark.flaky(
        reruns=5,
        rerun_delay=2,
        condition=GHA,
        reason="Flaky; fails occasionally on GitHub Actions runners",
    ),
]


def _t(group: Union[str, None], basename: str, *, check=None, marks=None):
    """Shorthand for defining tutorial test cases.

    Parameters
    ----------
    basename : str
       Base of the file name (without extension).
    group : str, optional
       Group ID. When pytest-xdist is used, tests in the same group are run in sequence
       on the same worker. If one tutorial depends on contents in the temporary test
       database produced by another tutorial, they should be in the same group.
    check : list of 2-tuple, optional
       Each tuple consists of:

       1. Name or index of cell whose output will contain a certain value, e.g. the
          MESSAGE objective function value.
       2. Expected value for that cell output.
    marks : list, optional
       Any pytest marks applicable to the test.
    """
    # Determine the directory containing the notebook
    dir_ = W if basename.startswith(f"{W}_") else AT

    marks = marks or []
    if group:
        # Mark the test as belonging to an xdist group
        marks.append(pytest.mark.xdist_group(name=group))

    return pytest.param((dir_, basename), check or [], marks=marks)


#: Argument values to parametrize :func:`test_tutorial`.
TUTORIALS: list[tuple] = [
    # IPython kernel
    _t("w0", f"{W}_baseline", check=[("solve-objective-value", 159025.82812)]),
    # NB could also check objective function values in the following tutorials; however,
    #    better to test features directly (not via Jupyter/IPython)
    _t("w0", f"{W}_baseline_using_xlsx_import_part1"),
    _t("w0", f"{W}_baseline_using_xlsx_import_part2"),
    _t("w0", f"{W}_emissions_bounds"),
    _t("w0", f"{W}_emissions_taxes"),
    _t("w0", f"{W}_firm_capacity"),
    _t("w0", f"{W}_flexible_generation"),
    _t("w0", f"{W}_fossil_resource"),
    _t("w0", f"{W}_share_constraint"),
    _t("w0", f"{W}_soft_constraints"),
    _t("w0", f"{W}_addon_technologies"),
    _t("w0", f"{W}_historical_new_capacity"),
    _t("w0", f"{W}_multinode_energy_trade"),
    _t("w0", f"{W}_sankey"),
    # NB this is the same value as in test_reporter()
    _t(None, f"{W}_report", check=[("len-rep-graph", 13724)]),
    _t("at0", "austria", check=[("solve-objective-value", 206321.90625)]),
    _t("at0", "austria_single_policy", check=[("solve-objective-value", 205310.34375)]),
    _t("at0", "austria_multiple_policies"),
    _t("at0", "austria_multiple_policies-answers"),
    _t("at0", "austria_load_scenario"),
    # R tutorials using the IR Jupyter kernel
    _t("at1", "R_austria", marks=[MARK[0], MARK[1]]),
    _t("at1", "R_austria_load_scenario", marks=[MARK[0], MARK[1]]),
]

# Short, readable IDs for the tests. Use getattr() to unpack the values from
# pytest.param()
IDS = [getattr(arg, "values", arg)[0][-1] for arg in TUTORIALS]

#: List of data files required by "westeros_baseline_using_xlsx_import_part2".
DATA_FILES = [
    "westeros_baseline_demand.xlsx",
    "westeros_baseline_technology_basic.xlsx",
    "westeros_baseline_technology_constraint.xlsx",
    "westeros_baseline_technology_economic.xlsx",
    "westeros_baseline_technology_historic.xlsx",
]


@pytest.fixture
def nb_path(request, tutorial_path):
    """Prepare the `nb_path` fixture to `test_tutorial`."""
    # Combine the filename parts with the tutorial_path fixture
    yield tutorial_path.joinpath(*request.param).with_suffix(".ipynb")


def default_args():
    """Default arguments for :func:`.run_notebook."""
    if GHA:
        # Use a longer timeout
        return dict(timeout=30)
    else:
        return dict()


# Parametrize the first 3 arguments using the variables *TUTORIALS* and *IDS*.
# Argument 'nb_path' is indirect so that the above function can modify it.
@pytest.mark.parametrize("nb_path,checks", TUTORIALS, ids=IDS, indirect=["nb_path"])
def test_tutorial(caplog, nb_path, checks, tmp_path, tmp_env):
    """Test tutorial in the IPython or IR notebook at `nb_path`.

    If `checks` are given, values in the specified cells are tested.
    """
    caplog.set_level(logging.INFO, "traitlets")
    tmp_env.update(PYDEVD_DISABLE_FILE_VALIDATION="1")

    if nb_path.name == "westeros_baseline_using_xlsx_import_part2.ipynb":
        # Copy data files used by this tutorial to `tmp_path`
        for name in DATA_FILES:
            copyfile(nb_path.parent / name, tmp_path / name)

    # Determine arguments for run_notebook()
    args = default_args()
    if nb_path.name.startswith("R_"):
        args.update(kernel_name="IR")

    # The notebook can be run without errors
    nb, errors = run_notebook(nb_path, tmp_path, tmp_env, **args)
    assert errors == []

    # Cell(s) identified by name or index have a particular value
    for cell, value in checks:
        assert np.isclose(get_cell_output(nb, cell), value)
