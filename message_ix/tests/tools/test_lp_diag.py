from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import Result

from message_ix.tools.lp_diag import LPdiag


def test_cli(
    tmp_path: Path, message_ix_cli: Callable[..., Result], test_data_path: Path
) -> None:
    """Test lpdiag.main() script."""

    p = str(test_data_path.joinpath("lp_diag"))
    outp = tmp_path.joinpath("diet_output.txt")

    # Command runs without error
    result = message_ix_cli(
        "lp-diag", "--wdir", p, "--mps", "diet.mps", "--outp", str(outp)
    )
    # Console output shows the output file path
    assert "Stdout redirected to" in result.output

    # Output file was created, contains the output
    assert outp.exists()
    assert "Reading MPS-format file" in outp.read_text()

    # Invalid --wdir
    result = message_ix_cli("lp-diag", "--wdir", "/surely this dir cannot/exist/")
    assert 2 == result.exit_code
    assert "Path '/surely this dir cannot/exist/' does not exist" in result.output


def test_aez(test_data_path: Path) -> None:
    """Test reading of aez.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the default MPS file for testing (aez.mps in test_mps folder)
    file = test_data_path.joinpath("lp_diag", "aez.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Check that the matrix has the correct shape
    assert lp.mat.shape == (8895, 5)

    # Check that the number of lines is correct
    assert lp.n_lines == 5528

    # Check that the number of rows is correct
    assert len(lp.row_name) == 329

    # Check that the number of columns is correct
    assert len(lp.col_name) == 637

    # Check matrix density
    dens = f"{float(len(lp.mat)) / (len(lp.row_name) * len(lp.col_name)):.2e}"
    assert dens == "4.24e-02"

    # Check that sequence number of the goal function is not -1
    assert lp.gf_seq != -1


def test_diet(test_data_path: Path) -> None:
    """Test reading of diet.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = test_data_path.joinpath("lp_diag", "diet.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Check that the matrix has the correct shape
    assert lp.mat.shape == (39, 5)

    # Check that the number of lines is correct
    assert lp.n_lines == 66

    # Check that the number of rows is correct
    assert len(lp.row_name) == 5

    # Check that the number of columns is correct
    assert len(lp.col_name) == 8

    # Check matrix density
    dens = f"{float(len(lp.mat)) / (len(lp.row_name) * len(lp.col_name)):.2e}"
    assert dens == "9.75e-01"

    # Check that sequence number of the goal function is not -1
    assert lp.gf_seq != -1


def test_jg_korh(test_data_path: Path) -> None:
    """Test reading of jg_korh.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = test_data_path.joinpath("lp_diag", "jg_korh.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Check that the matrix has the correct shape
    assert lp.mat.shape == (10, 5)

    # Check that the number of lines is correct
    assert lp.n_lines == 21

    # Check that the number of rows is correct
    assert len(lp.row_name) == 4

    # Check that the number of columns is correct
    assert len(lp.col_name) == 3

    # Check matrix density
    dens = f"{float(len(lp.mat)) / (len(lp.row_name) * len(lp.col_name)):.2e}"
    assert dens == "8.33e-01"

    # Check that sequence number of the goal function is not -1
    assert lp.gf_seq != -1


def test_lotfi(test_data_path: Path) -> None:
    """Test reading of lotfi.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = test_data_path.joinpath("lp_diag", "lotfi.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Check that the matrix has the correct shape
    assert lp.mat.shape == (1086, 5)

    # Check that the number of lines is correct
    assert lp.n_lines == 785

    # Check that the number of rows is correct
    assert len(lp.row_name) == 154

    # Check that the number of columns is correct
    assert len(lp.col_name) == 308

    # Check matrix density
    dens = f"{float(len(lp.mat)) / (len(lp.row_name) * len(lp.col_name)):.2e}"
    assert dens == "2.29e-02"

    # Check that sequence number of the goal function is not -1
    assert lp.gf_seq != -1


# TODO Continue expanding these tests. Mostly, this means calling the last functions
#      defined in lp_diag.py, but some lines also require special edge cases (mps files
#      defined with 6 and 7 sections)
@pytest.mark.parametrize(
    "filename, exception",
    (
        ("error_err_tst.mps", AssertionError),
        # Required sections are in the wrong order
        ("error_sections_required_order.mps", NameError),
        # Unknown section
        ("error_sections_unknown.mps", ValueError),
        # Optional sections are in the wrong order
        ("error_sections_optional_order.mps", AttributeError),
        # File with all sections, error when going through section-content lines
        ("error_sections_all.mps", RuntimeError),
        # File with too many sections, error when going through section definition lines
        ("error_sections_too_many.mps", RuntimeError),
        # String coefficients too short
        ("error_coefficient_string_short.mps", ValueError),
        # String coefficients too long
        ("error_coefficient_string_long.mps", ValueError),
        # RHS string too short
        ("error_rhs_string_short.mps", ValueError),
        # RHS string too long
        ("error_rhs_string_long.mps", ValueError),
        # RHS too short
        ("error_rhs_too_short.mps", AssertionError),
        # String ranges too short
        ("error_ranges_string_short.mps", ValueError),
        # String ranges too long
        ("error_ranges_string_long.mps", ValueError),
        # Ranges too show
        ("error_ranges_too_short.mps", AssertionError),
        # String bounds too short
        ("error_bounds_string_short.mps", ValueError),
        # Bounds too short
        ("error_bounds_too_short.mps", AssertionError),
        # Bounds type not required
        ("error_bounds_type_not_needed.mps", TypeError),
        # Bounds of unknown type
        ("error_bounds_unknown_type.mps", TypeError),
    ),
)
def test_error_cases(
    test_data_path: Path, filename: str, exception: type[Exception]
) -> None:
    """Test error cases"""

    lp = LPdiag()

    # The expected `exception` is raised when reading the MPS file with `filename`
    with pytest.raises(exception):
        lp.read_mps(test_data_path.joinpath("lp_diag", filename))


def test_lpdiag_print_statistics(test_data_path: Path) -> None:
    """Test auxiliary stat function."""

    # Read in the diet.mps file
    file = test_data_path.joinpath("lp_diag", "jg_korh.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Stats of matrix coeffs, incl. distrib. tails
    lp.print_statistics(lo_tail=-7, up_tail=5)
    # To get numbers of coeffs for each magnitute specify equal/overlapping tails:
    lp.print_statistics(lo_tail=1, up_tail=0)

    # The function only prints, so we can only ...
    # Check that the matrix has the correct shape
    assert lp.mat.shape == (10, 5)


def test_lpdiag_locate_outliers(test_data_path: Path) -> None:
    """Test locating outliers."""

    # Read in the diet.mps file
    file = test_data_path.joinpath("lp_diag", "lotfi.mps")
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    lp.read_mps(file)

    # Test (lotfi) small-value outliers:
    lp.locate_outliers(small=True, thresh=-1, max_rec=100)
    # Test (lotfi) large-value outliers
    lp.locate_outliers(small=False, thresh=2, max_rec=500)

    # The function doesn't return anything, so we can only ...
    # Check that the matrix has the correct shape
    assert lp.mat.shape == (1086, 5)
