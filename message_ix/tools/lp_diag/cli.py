"""Command-line interface to :mod:`.lp_diag`.

Written by Marek Makowski, ECE Program of IIASA, in March 2023.
Developed in PyCharm, with Python 3.10.4.
"""
# large (1+ GB) MPSs files, shall not be posted to gitHub.
# app was tested on two (1+ GB) MPSs posted by OFR in /t/fricko on Feb 16, 2023:
# OFR_test_led_barrier.mps
# baseline_barrier.mps
#
# small MPSs, for testing the code, posted to 'test_mps' subdirectory:
# errors/err_tst  - small MPS with various errors for testing the diagnostics
# aez  - agro-ecological zones, medium size; two matrix elems in a row
# diet - classical small LP
# jg_korh - tiny testing problem
# lotfi - classical medium size; two matrix elems in a row
#
# TODO TBD, if the MPS-standard should be observed; should it cause error or info in
#      particular, range of values: 10^{-10} < abs(val) < 10^{10}
# TODO naive scaling? might not be informative due to the later preprocessing
# TODO plots of distributions of coeffs, if indeed useful

import os
import sys  # for redirecting stdout
from datetime import datetime as dt
from pathlib import Path
from typing import Optional

import click


@click.command("lp-diag")
@click.option(
    "--wdir",
    "w_dir",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Working directory.",
)
@click.option(
    "--mps",
    "prob_id",
    type=click.Path(path_type=Path),
    default="test_mps/aez",  # Default MPS for testing
    # commented: Alternate specs of test-MPS commented below
    # default="test_mps/diet"
    # default="test_mps/errors/err_tst"
    # default="test_mps/jg_korh"
    # default="test_mps/lotfi"
    help="MPS file name or path.",
)
@click.option("--outp", "fn_outp", help="Path for file output.")
def main(w_dir: Path, prob_id: Path, fn_outp: Optional[Path]) -> None:
    """Diagnostics of basic properties of LP Problems represented by the MPS-format.

    Examples:
    message-ix lp-diag
    message-ix lp-diag -h
    message-ix lp-diag --mps test_mps/aez --outp foo.txt
    """
    # This function is a driver of the LP diagnostics provided by LPdiag class. It
    # defines the working space, then controls the flow by executing the desired methods
    # of the LPdiag class.

    # Only import if the command is to be run
    from . import LPdiag

    # Start time
    tstart = dt.now()

    # Change the working directory, if specified
    work_dir = Path.cwd()
    print(f"work_dir: '{work_dir}'")

    if len(str(w_dir)) > 1:
        print(f"Changing work-directory to: {w_dir}.")
        # NB click.Path(exists=True) ensures this directory, if given, exists
        os.chdir(w_dir)

    # Check the existence and accessibility of the MPS file
    mps_path = Path.cwd().joinpath(prob_id)

    if not mps_path.is_file():
        raise click.ClickException(
            f"MPS file {prob_id} not accessible from {Path.cwd()}\n"
            "Try to use the --wdir option to set the work-directory."
        )
    elif not os.access(mps_path, os.R_OK):
        raise click.ClickException(f"MPS file {prob_id} is not readable.")

    default_stdout = sys.stdout
    if fn_outp:
        print(f"Stdout redirected to: {fn_outp}")
        f_out = open(fn_outp, "w")
        sys.stdout = f_out
    else:
        f_out = None

    # Read MPS file and store the matrix in a data frame
    lp = LPdiag()
    lp.read_mps(mps_path)

    # Print statistics of matrix coefficients including distribution tails
    lp.print_statistics(lo_tail=-7, up_tail=5)

    # To get numbers of coeffs for each magnitude specify equal/overlapping tails
    # lp.print_statistics(lo_tail=0, up_tail=0)

    # Locations of small-value outliers
    lp.locate_outliers(small=True, thresh=-7, max_rec=100)
    # Locations of large-value outliers
    lp.locate_outliers(small=False, thresh=6, max_rec=500)

    if f_out:
        # Close the redirected output
        f_out.close()
        sys.stdout = default_stdout
        print(f"\nRedirected stdout stored in {fn_outp}. Now writing to the console.")

    # Change directory back to work_dir
    if len(str(w_dir)) > 1:
        os.chdir(work_dir)

    tend = dt.now()
    time_diff = tend - tstart
    print("\nStarted at: ", str(tstart))
    print("Finished at:", str(tend))
    print(f"Wall-clock execution time: {time_diff.seconds} sec.")
