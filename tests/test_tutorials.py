import io
import os
import subprocess
import sys
import pytest

import numpy as np

from conftest import here

is_py2 = sys.version_info[0] == 2

try:
    import nbformat
    jupyter_installed = True
except ImportError:
    jupyter_installed = False

ene_path = os.path.join(here, '..', 'tutorial', 'Austrian_energy_system')
westeros_path = os.path.join(here, '..', 'tutorial', 'westeros')

py2_deprecated = 'Python 2 is deprecated in the tutorials'
jupyter_required = 'requires Jupyter Notebook to be installed'

# taken from the execellent example here:
# https://blog.thedataincubator.com/2016/06/testing-jupyter-notebooks/


def _notebook_run(path, kernel=None, capsys=None):
    """Execute a notebook via nbconvert and collect output.
    :returns (parsed nb object, execution errors)
    """
    major_version = sys.version_info[0]
    kernel = kernel or 'python{}'.format(major_version)
    dirname, __ = os.path.split(path)
    os.chdir(dirname)
    fname = os.path.join(here, 'test.ipynb')
    args = [
        "jupyter", "nbconvert", "--to", "notebook", "--execute",
        "--ExecutePreprocessor.timeout=60",
        "--ExecutePreprocessor.kernel_name={}".format(kernel),
        "--output", fname, path]
    subprocess.check_call(args)

    nb = nbformat.read(io.open(fname, encoding='utf-8'),
                       nbformat.current_nbformat)

    errors = [
        output for cell in nb.cells if "outputs" in cell
        for output in cell["outputs"] if output.output_type == "error"
    ]

    os.remove(fname)

    return nb, errors


def get_cell_by_name(nb, name):
    """Retrieve a cell from *nb* according to its metadata *name*:

    The Jupyter notebook format allows specifying a document-wide unique 'name'
    metadata attribute for each cell:

    https://nbformat.readthedocs.io/en/latest/format_description.html
                                                                #cell-metadata

    Return the cell matching the name, or raise ValueError.
    """
    for i, cell in enumerate(nb.cells):
        try:
            cell_name = cell.metadata.jupyter.name
            if cell_name == name:
                return cell
        except AttributeError:
            continue

    raise ValueError("no cell named '{}'".format(name))


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_westeros_baseline(capsys):
    fname = os.path.join(westeros_path, 'westeros_baseline.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []

    # On Python 2, the returned objective value is different
    if sys.version_info[0] == 3:
        return

    cell = get_cell_by_name(nb, 'solve-objective-value')
    obs = eval(cell['outputs'][0]['data']['text/plain'])
    exp = 187445.953125
    assert np.isclose(obs, exp)


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_westeros_emissions(capsys):
    fname = os.path.join(westeros_path, 'westeros_emissions_bounds.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_westeros_emissions_tax(capsys):
    fname = os.path.join(westeros_path, 'westeros_emissions_taxes.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_westeros_firm_capacity(capsys):
    fname = os.path.join(westeros_path, 'westeros_firm_capacity.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_westeros_flexible_generation(capsys):
    fname = os.path.join(westeros_path, 'westeros_flexible_generation.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_austria(capsys):
    fname = os.path.join(ene_path, 'austria.ipynb')
    nb, errors = _notebook_run(fname, capsys=capsys)
    assert errors == []

    # FIXME use get_cell_by_name instead of assuming cell count/order is fixed
    obs = eval(nb.cells[-13]['outputs'][0]['data']['text/plain'])
    exp = 133105106944.0
    assert np.isclose(obs, exp)


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_austria_single_policy():
    fname = os.path.join(ene_path, 'austria_single_policy.ipynb')
    nb, errors = _notebook_run(fname)
    assert errors == []

    # FIXME use get_cell_by_name instead of assuming cell count/order is fixed
    obs = eval(nb.cells[-8]['outputs'][0]['data']['text/plain'])
    exp = 132452155392.0
    assert np.isclose(obs, exp)


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_austria_multiple_policies():
    fname = os.path.join(ene_path, 'austria_multiple_policies.ipynb')
    nb, errors = _notebook_run(fname)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_austria_multiple_policies_answers():
    fname = os.path.join(ene_path, 'austria_multiple_policies-answers.ipynb')
    nb, errors = _notebook_run(fname)
    assert errors == []


@pytest.mark.skipif(is_py2, reason=py2_deprecated)
@pytest.mark.skipif(not jupyter_installed, reason=jupyter_required)
def test_austria_load():
    fname = os.path.join(ene_path, 'austria_load_scenario.ipynb')
    nb, errors = _notebook_run(fname)
    assert errors == []
