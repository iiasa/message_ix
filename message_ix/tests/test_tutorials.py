import sys

import numpy as np
import pytest
from ixmp.testing import get_cell_output, run_notebook

AT = "Austrian_energy_system"

# Argument values to parametrize test_tutorial
#
# Each item is a 2-tuple:
# 1. Path fragments under tutorials directory,
# 2. List containing 0 or more 2-tuples, each:
#    a. Name or index of cell containing objective value,
#    b. Expected objective value.
# 3. Dictionary with extra keyword arguments to run_notebook().

# FIXME check objective function of the rest of tutorials.
tutorials = [
    # IPython kernel
    (
        ("westeros", "westeros_baseline"),
        [("solve-objective-value", 369297.75)],
        {},
    ),
    (("westeros", "westeros_emissions_bounds"), [], {}),
    (("westeros", "westeros_emissions_taxes"), [], {}),
    (("westeros", "westeros_firm_capacity"), [], {}),
    (("westeros", "westeros_flexible_generation"), [], {}),
    (("westeros", "westeros_fossil_resource"), [], {}),
    (("westeros", "westeros_share_constraint"), [], {}),
    # NB this is the same value as in test_reporter()
    (("westeros", "westeros_report"), [("len-rep-graph", 12688)], {}),
    ((AT, "austria"), [("solve-objective-value", 206321.90625)], {}),
    (
        (AT, "austria_single_policy"),
        [("solve-objective-value", 815183232.0)],
        {},
    ),
    ((AT, "austria_multiple_policies"), [], {}),
    ((AT, "austria_multiple_policies-answers"), [], {}),
    ((AT, "austria_load_scenario"), [], {}),
    # R tutorials / IR kernel
    ((AT, "R_austria"), [], dict(kernel="IR")),
    ((AT, "R_austria_load_scenario"), [], dict(kernel="IR")),
]

# Short, readable IDs for the tests
ids = [arg[0][-1] for arg in tutorials]


@pytest.fixture
def nb_path(request, tutorial_path):
    """Prepare the `nb_path` fixture to `test_tutorial`."""
    # Combine the filename parts with the tutorial_path fixture
    yield tutorial_path.joinpath(*request.param).with_suffix(".ipynb")


# Parametrize the first 3 arguments using the variables *tutorial* and *ids*.
# Argument 'nb_path' is indirect so that the above function can modify it.
@pytest.mark.parametrize(
    "nb_path,cell_values,run_args", tutorials, ids=ids, indirect=["nb_path"]
)
def test_tutorial(nb_path, cell_values, run_args, tmp_path, tmp_env):
    """Test tutorial in the IPython or IR notebook at *fname*.

    If *cell_values* are given, values in the specified cells are tested.
    """
    # Add the tutorial directory to PYTHONPATH. The tutorials are executed in
    # `tmp_path`; but they import from a tools.py file in the same directory as
    # the notebook, ie. under `tutorial_path`.
    # TODO remove the reliance on this 'hidden' code
    path_sep = ";" if sys.platform.startswith("win") else ":"
    tmp_env["PYTHONPATH"] = path_sep.join(
        [str(nb_path.parent), tmp_env.get("PYTHONPATH", "")]
    )

    # The notebook can be run without errors
    nb, errors = run_notebook(nb_path, tmp_path, tmp_env, **run_args)
    assert errors == []

    for cell, value in cell_values:
        # Cell identified by name or index has a particular value
        assert np.isclose(get_cell_output(nb, cell), value)
