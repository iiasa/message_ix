"""
Prototype of simple analysis of the MPS-format file
Written by Marek Makowski, ECE Program of IIASA, in March 2023
Developed in PyCharm, with Python 3.10.4
"""

import argparse
import os
import sys  # needed for sys.exit() and redirecting stdout
from datetime import datetime as dt
from os import R_OK, access
from os.path import isfile

# from datetime import timedelta as td
# noinspection PyUnresolvedReferences
# LPdiag class for processing and analysis of LP matrices
from . import LPdiag

"""
The above import stmt works only in the message-ix editable environment; it is treated
as error by PyCharm (but it works); therefore, the noinspection option is applied for
this statement.
In other environments the import from message_ix... does not work; therefore, it has
to be replaced by the below (now commented-out) import statement. The latter, however,
mypy flags as error.
"""
# from lp_diag import LPdiag


def read_args(args):
    descr = """
    Diagnostics of basic properties of LP Problems represented by the MPS-format.

    Examples of usage:
    python lpdiag.py
    python lpdiag.py -h
    python lpdiag.py --mps test_mps/aez --outp foo.txt

    """
    # python lpdiag.py --path "message_ix/tools/lp_diag" --mps "test.mps" -s

    parser = argparse.ArgumentParser(
        description=descr, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    wdir = "--wdir : string\n    Working directory."
    parser.add_argument("--wdir", help=wdir)
    mps = "--mps : string\n  Name of the MPS file (optionally with path)."
    parser.add_argument("--mps", help=mps)
    outp = "--outp : string\n  Redirect output to the named file."
    parser.add_argument("--outp", help=outp)
    # parser.add_argument("-s", "--save", action="store_true")  # on/off flag

    # parse cli
    cl_args = parser.parse_args(args)
    return cl_args


def main(argv=None):
    """Driver of the LP diagnostics provided by LPdiag class.

    Defines the working space, then controls the flow by executing the desired
    functions of LPdiag class.
    """

    work_dir = os.getcwd()
    print(f"work_dir: '{work_dir}'.")
    tstart = dt.now()

    # Retrieve and assign arguments
    args = read_args(argv)
    w_dir = args.wdir or "."
    prob_id = args.mps or "test_mps/aez"  # default MPS for testing
    # alternative specs of test-MPS commented below
    # prob_id = args.mps or "test_mps/diet"  # default MPS for testing
    # prob_id = args.mps or "test_mps/errors/err_tst"  # default MPS for testing
    # prob_id = args.mps or "test_mps/jg_korh"  # default MPS for testing
    # prob_id = args.mps or "test_mps/lotfi"  # default MPS for testing
    if len(w_dir) > 1:
        print(f"Changing work-directory to: {w_dir}.")
        try:
            os.chdir(w_dir)
        except OSError as e:
            raise OSError(f"Cannot change work-directory to: {w_dir}.") from e
    assert isfile(prob_id), (
        f"MPS file {prob_id} not accessible from the work-directory:\n'{work_dir}'."
        "\nTry to use the --wdir command option to set the work-directory."
    )
    assert access(prob_id, R_OK), f"MPS file {prob_id} is not readable."

    # large (1+ GB) MPSs files, shall not be posted to gitHub.
    # app was tested on two (1+ GB) MPSs posted by OFR in /t/fricko on Feb 16, 2023:
    # OFR_test_led_barrier.mps
    # baseline_barrier.mps

    # small MPSs, for testing the code, posted to 'test_mps' subdirectory:
    # errors/err_tst  - small MPS with various errors for testing the diagnostics
    # aez  - agro-ecological zones, medium size; two matrix elems in a row
    # diet - classical small LP
    # jg_korh - tiny testing problem
    # lotfi - classical medium size; two matrix elems in a row

    fn_outp = args.outp or None  # optional redirection of stdout

    default_stdout = sys.stdout
    if fn_outp:
        print(f"Stdout redirected to: {fn_outp}")
        f_out = open(fn_outp, "w")
        sys.stdout = f_out

    lp = LPdiag()  # LPdiag ctor
    lp.read_mps(prob_id)  # read MPS, store the matrix in dataFrame
    lp.print_statistics(
        lo_tail=-7, up_tail=5
    )  # stats of matrix coeffs, incl. distrib. tails
    # To get numbers of coeffs for each magnitute specify equal/overlapping tails:
    # lp.print_statistics(lo_tail=0, up_tail=0)
    lp.locate_outliers(
        small=True, thresh=-7, max_rec=100
    )  # locations of small-value outliers
    lp.locate_outliers(
        small=False, thresh=6, max_rec=500
    )  # locations of large-value outliers

    if fn_outp:  # close the redirected output
        # noinspection PyUnboundLocalVariable
        f_out.close()
        sys.stdout = default_stdout
        print(f"\nRedirected stdout stored in {fn_outp}. Now writing to the console.")

    # Change directory back to work_dir
    if len(w_dir) > 1:
        os.chdir(work_dir)

    tend = dt.now()
    time_diff = tend - tstart
    print("\nStarted at: ", str(tstart))
    print("Finished at:", str(tend))
    print(f"Wall-clock execution time: {time_diff.seconds} sec.")

    # todo: TBD, if the MPS-standard should be observed; should it cause error or info
    #  in particular, range of values: 10^{-10} < abs(val) < 10^{10}
    # todo: naive scaling? might not be informative due to the later preprocessing
    # todo: plots of distributions of coeffs, if indeed useful


if __name__ == "__main__":
    sys.exit(main())