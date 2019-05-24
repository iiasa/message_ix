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
# Each item is a 3-tuple:
# 1. Path fragments under tutorials directory,
# 2. Name or index of cell containing objective value (or None),
# 3. Expected objective value.
tutorials = [
    (('westeros', 'westeros_baseline'),
     'solve-objective-value', 207544.09375),
    # on Python 2:
    # 'solve-objective-value', 187445.953125),
    (('westeros', 'westeros_emissions_bounds'), None, None),
    (('westeros', 'westeros_emissions_taxes'), None, None),
    (('westeros', 'westeros_firm_capacity'), None, None),
    (('westeros', 'westeros_flexible_generation'), None, None),
    # FIXME use get_cell_by_name instead of assuming cell count/order is fixed
    ((AT, 'austria'), -13, 133105106944.0),
    ((AT, 'austria_single_policy'), -8, 132452155392.0),
    ((AT, 'austria_multiple_policies'), None, None),
    ((AT, 'austria_multiple_policies-answers'), None, None),
    ((AT, 'austria_load_scenario'), None, None),
]

# Short, readable IDs for the tests
ids = [arg[0][-1] for arg in tutorials]


@pytest.fixture
def nb_path(request, tutorial_path):
    # Combine the filename parts with the tutorial_path fixture
    yield Path(tutorial_path, *request.param).with_suffix('.ipynb')


# Parametrize the first 3 arguments using the variables *tutorial* and *ids*.
# Argument 'nb_path' is indirect so that the above fixture can modify it.
@pytest.mark.parametrize('nb_path,obj_cell,obj_value', tutorials, ids=ids,
                         indirect=['nb_path'])
def test_tutorial(nb_path, obj_cell, obj_value, tmp_path, tmp_env):
    """Test tutorial in the IPython notebook at *fname*.

    If *obj_cell* and *obj_value* are given, the value in the specified cell is
    tested.
    """
    # The notebook can be run without errors
    nb, errors = run_notebook(nb_path, tmp_path, tmp_env)
    assert errors == []

    # Cell identified by obj_cell has a particular value
    assert not obj_cell or np.isclose(get_cell_output(nb, obj_cell), obj_value)
