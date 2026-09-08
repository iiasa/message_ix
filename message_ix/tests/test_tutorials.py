import logging
import os
import sys
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from shutil import copyfile
from typing import Any

import ixmp.backend
import numpy.testing as npt
import pytest
from ixmp.testing import get_cell_output, run_notebook
from nbclient.exceptions import CellExecutionError, CellTimeoutError

from message_ix.testing import GHA
from message_ix.tests.test_report import MISSING_IXMP4

log = logging.getLogger(__name__)

#: Marks for all tests in this module.
pytestmark = [
    pytest.mark.tutorial,
    pytest.mark.flaky(
        reruns=2,
        rerun_delay=2,
        condition=GHA,
        reason="Flaky; fails occasionally on GitHub Actions runners",
    ),
]

#: Mapping from tutorial base name to data files to be copied into the temporary dir.
DATA_FILES = {
    "westeros_baseline_using_xlsx_import_part2.ipynb": (
        "westeros_baseline_demand.xlsx",
        "westeros_baseline_technology_basic.xlsx",
        "westeros_baseline_technology_constraint.xlsx",
        "westeros_baseline_technology_economic.xlsx",
        "westeros_baseline_technology_historic.xlsx",
    ),
}

#: Path to the directory containing tutorials.
TUTORIAL_DIR = Path(files(__name__.partition(".")[0])).with_name("tutorial")  # type: ignore[arg-type]

#: Parameters to :func:`test_tutorial`. This is populated using the shorthand functions
#: below.
TUTORIALS: list[tuple] = []


@dataclass
class Tutorial:
    """A test case for a single tutorial notebook."""

    #: Relative path to the notebook file. This path is resolved within
    #: :data:`TUTORIAL_DIR`.
    path: Path = field(default_factory=Path)

    #: Group ID. When pytest-xdist is used, tests in the same group are run in sequence
    #: on the same worker. If one tutorial depends on contents in the temporary test
    #: database produced by another tutorial, they should be in the same group.
    group: str | None = None

    #: Each tuple consists of:
    #:
    #: 1. Name or index of cell whose output will contain a certain value, e.g. the
    #:    MESSAGE objective function value. This cell's output is retrieved and passed
    #:    as the first positional argument (`actual`) to
    #:    :func:`numpy.testing.assert_allclose`.
    #: 2. Further positional arguments to :func:`numpy.testing.assert_allclose`:
    #:    `desired`, `rtol`, `atol`, etc.
    check: list[tuple] = field(default_factory=list)

    #: Any :mod:`pytest` marks applicable to the test.
    marks: list[pytest.MarkDecorator] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.path = TUTORIAL_DIR.joinpath(self.path).with_suffix(".ipynb")

        if self.group:
            # Mark the test as belonging to an xdist group
            self.marks.append(pytest.mark.xdist_group(name=self.group))

        TUTORIALS.append(pytest.param(self, marks=self.marks))

    @property
    def args(self) -> dict[str, Any]:
        """Keyword arguments to :func:`.run_notebook`."""
        result: dict[str, Any] = {}
        if self.path.name.startswith("R_"):
            result["kernel_name"] = "IR"  # Use a different kernel for R notebooks
        return result


def W(basename, **kwargs) -> None:
    """Shorthand for Westeros tutorials."""
    kwargs.setdefault("group", "w0")
    Tutorial(Path("westeros", f"westeros_{basename}"), **kwargs)


W("baseline", check=[("solve-objective-value", 159025.82812)])
# NB could also check objective function values in the following tutorials; however,
#    better to test features directly (not via Jupyter/IPython).
W("baseline_using_xlsx_import_part1")
W("baseline_using_xlsx_import_part2")
W("emissions_bounds")
W("emissions_taxes")
W("firm_capacity")
W("flexible_generation")
W("fossil_resource")
W("share_constraint")
W("soft_constraints")
W("addon_technologies")
W("historical_new_capacity")
W("multinode_energy_trade")
W("sankey")

# NB This is the same count as in test_report.test_reporter_from_scenario. Using
#    len(MISSING_IXMP4) for atol allows the test to pass when the value is N - 8.
W("report", group=None, check=[("len-rep-graph", 28764, 1e-7, len(MISSING_IXMP4))])


def AT(basename, **kwargs) -> None:
    """Shorthand for Austria tutorials."""
    kwargs.update(group="at0")
    Tutorial(Path("Austrian_energy_system", f"austria{basename}"), **kwargs)


AT("", check=[("solve-objective-value", 206321.90625)])
AT("_single_policy", check=[("solve-objective-value", 205310.34375)])
AT("_multiple_policies")
AT("_multiple_policies-answers")
AT("_load_scenario")


def AT_R(basename) -> None:
    """Shorthand for R tutorials using the IR kernel."""
    Tutorial(
        Path("Austrian_energy_system", f"R_austria{basename}"),
        group="at1",
        marks=[
            pytest.mark.skipif(
                condition=sys.platform == "linux", reason="IR kernel times out on Linux"
            )
        ],
    )


AT_R("")
AT_R("_load_scenario")


@pytest.mark.parametrize("ixmp_backend", ixmp.backend.available())
@pytest.mark.parametrize("tutorial", TUTORIALS, ids=lambda t: t.path.stem)
def test_tutorial(
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    tmp_env: os._Environ[str],
    tutorial_path: Path,
    ixmp_backend: str,
    tutorial: Tutorial,
) -> None:
    """Test the IPython or IR notebook in `tutorial`.

    If :attr:`Tutorial.check` has entries, values in the specified cells are tested.
    """
    caplog.set_level(logging.INFO, "traitlets")
    tmp_env.update(PYDEVD_DISABLE_FILE_VALIDATION="1")

    # Copy any data files used by this tutorial to `tmp_path`
    for name in DATA_FILES.get(tutorial.path.name, ()):
        copyfile(tutorial.path.parent / name, tmp_path / name)

    # Arguments for run_notebook()
    # - Set the "default" platform to be either the platform named "local" or
    #   "ixmp4-local", according to the ixmp_backend parameter
    args = tutorial.args | dict(
        default_platform={"jdbc": "local", "ixmp4": "ixmp4-local"}[ixmp_backend]
    )

    # The notebook can be run without errors
    try:
        nb, errors = run_notebook(tutorial.path, tmp_path, tmp_env, **args)
    except (CellExecutionError, CellTimeoutError) as e:
        if ixmp_backend == "ixmp4":
            # Show errors but make these non-fatal. We do this because it is complicated
            # to apply an XFAIL mark that is conditional on the value of `ixmp_backend`.
            log.error(f"with IXMP4Backend:\n{e!r}")
            return
        elif GHA and sys.platform == "darwin" and ixmp_backend == "jdbc":
            # All tests with JDBCBackend time out on macOS runners
            log.error(f"with JDBCBackend on macOS: {e}")
            return
        raise  # all other exceptions

    assert errors == []

    # Cell(s) identified by name or index have a particular value
    for cell, *check_args in tutorial.check:
        npt.assert_allclose(get_cell_output(nb, cell), *check_args)
