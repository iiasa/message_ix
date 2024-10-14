"""Command-line interface to :mod:`.lp_diag`."""

# Written by Marek Makowski, ECE Program of IIASA, in March 2023.
# Developed in PyCharm, with Python 3.10.4.
#
# app was tested on two (1+ GB) MPSs posted by OFR in /t/fricko on Feb 16, 2023:
# OFR_test_led_barrier.mps
# baseline_barrier.mps
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
    # Default MPS for testing
    default=Path(__file__).parents[2].joinpath("tests", "data", "lp_diag", "aez.mps"),
    help="MPS file name or path.",
)
@click.option(
    "--lo-tail",
    "-L",
    type=int,
    default=-7,
    help="Magnitude order of the lower tail (default: -7).",
)
@click.option(
    "--up-tail",
    "-U",
    type=int,
    default=-5,
    help="Magnitude order of the upper tail (default: 5).",
)
@click.option("--outp", "fn_outp", metavar="PATH", help="Path for file output.")
def main(w_dir: Path, prob_id: Path, fn_outp: Optional[Path], lo_tail, up_tail) -> None:
    """Diagnostics of basic properties of LP problems stored in the MPS format.

    \b
    Examples:
      message-ix lp-diag
      message-ix lp-diag --help
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

    if not prob_id.is_absolute():
        # Resolve a relative path or bare file name relative to the working directory
        mps_path = Path.cwd().joinpath(prob_id)
    else:
        mps_path = prob_id

    # Check the existence and accessibility of the MPS file
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
    lp.print_statistics(lo_tail=lo_tail, up_tail=up_tail)

    # Locations of small-value outliers
    lp.locate_outliers(small=True, thresh=lo_tail, max_rec=100)
    # Locations of large-value outliers
    # NB(PNK) This thresh was hard-coded as 6, versus print_statistics(…, up_tail=5)
    #         above. Assuming these represent sane defaults reached through testing,
    #         keep the difference of +1.
    lp.locate_outliers(small=False, thresh=up_tail + 1, max_rec=500)

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
