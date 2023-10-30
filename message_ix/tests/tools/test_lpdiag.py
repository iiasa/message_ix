import os

import pytest

from message_ix.tools.lp_diag.lp_diag import LPdiag


def test_aez():
    """Test reading of aez.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the default MPS file for testing (aez.mps in test_mps folder)
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "aez"
    )
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


def test_diet():
    """Test reading of diet.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "diet"
    )
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


def test_jg_korh():
    """Test reading of jg_korh.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "jg_korh"
    )
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


def test_lotfi():
    """Test reading of lotfi.mps file

    Check that the number of lines, rows and columns are correct"""

    # Read in the diet.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "lotfi"
    )
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


# TODO: continue expanding tests
# Mostly, this means calling the last functions defined in lp_diag.py, but some
# lines also require special edge cases (mps files defined with 6 and 7 sections)
def test_error_cases():
    """Test error cases"""

    # Read in the err_tst.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "err_tst"
    )
    lp = LPdiag()

    # Read MPS, store the matrix in dataFrame
    with pytest.raises(AssertionError):
        lp.read_mps(file)


def test_lpdiag_print_statistics():
    """Test auxiliary stat function."""

    # Read in the diet.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "jg_korh"
    )
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


def test_lpdiag_locate_outliers():
    """Test locating outliers."""

    # Read in the diet.mps file
    file = os.path.join(
        os.getcwd(), "message_ix", "tools", "lp_diag", "test_mps", "lotfi"
    )
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
