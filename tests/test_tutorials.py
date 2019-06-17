try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import sys

from ixmp.testing import run_notebook, get_cell_output
import numpy as np
import pytest


# Skip the entire file on Python 2
if sys.version_info[0] == 2:
    py2_deprecated = 'Python 2 is deprecated in the tutorials'
    pytestmark = pytest.mark.skip(reason=py2_deprecated)


AT = 'Austrian_energy_system'

# Argument values to parametrize test_tutorial
#
# Each item is a 2-tuple:
# 1. Path fragments under tutorials directory,
# 2. List containing 0 or more 2-tuples, each:
#    a. Name or index of cell containing objective value,
#    b. Expected objective value.
tutorials = [
    (('westeros', 'westeros_baseline'),
     [('solve-objective-value', 207544.09375)]),
    # on Python 2:
    # 'solve-objective-value', 187445.953125),
    (('westeros', 'westeros_emissions_bounds'), []),
    (('westeros', 'westeros_emissions_taxes'), []),
    (('westeros', 'westeros_firm_capacity'), []),
    (('westeros', 'westeros_flexible_generation'), []),
    # FIXME use get_cell_by_name instead of assuming cell count/order is fixed
    ((AT, 'austria'), [(-13, 133105106944.0)]),
    ((AT, 'austria_single_policy'), [(-8, 132452155392.0)]),
    ((AT, 'austria_multiple_policies'), []),
    ((AT, 'austria_multiple_policies-answers'), []),
    ((AT, 'austria_load_scenario'), []),
]

# Short, readable IDs for the tests
ids = [arg[0][-1] for arg in tutorials]


@pytest.fixture
def nb_path(request, tutorial_path):
    # Combine the filename parts with the tutorial_path fixture
    yield Path(tutorial_path, *request.param).with_suffix('.ipynb')


# Parametrize the first 3 arguments using the variables *tutorial* and *ids*.
# Argument 'nb_path' is indirect so that the above fixture can modify it.
@pytest.mark.parametrize('nb_path,cell_values', tutorials, ids=ids,
                         indirect=['nb_path'])
def test_tutorial(nb_path, cell_values, tmp_path, tmp_env):
    """Test tutorial in the IPython notebook at *fname*.

    If *cell_values* are given, values in the specified cells are tested.
    """
    # The notebook can be run without errors
    nb, errors = run_notebook(nb_path, tmp_path, tmp_env)
    assert errors == []

    for cell, value in cell_values:
        # Cell identified by name or index has a particular value
        assert np.isclose(get_cell_output(nb, cell), value)
