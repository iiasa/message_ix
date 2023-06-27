"""
Prototype of simple analysis of the MPS-format file
Written by Marek Makowski, ECE Program of IIASA, in March 2023
Developed in PyCharm, with Python 3.10.4
"""

import argparse
import os
from os import access, R_OK
from os.path import isfile
import sys  # needed for sys.exit() and redirecting stdout
from datetime import datetime as dt
# from datetime import timedelta as td
# noinspection PyUnresolvedReferences
from message_ix.tools.lp_diag.lpdiag import (
    LPdiag,  # LPdiag class for processing and analysis of LP matrices
)

"""
The above import stmt works only in the message-ix editable environment; it is treated as error
by PyCharm (but it works); therefore, the noinspection option is applied for the statement.
In other environments the import from message_ix... does not work; therefore, it has to be
replaced by the below (now commented-out) import statement. The latter, however, mypy flags as error.
"""
# from lpdiag import LPdiag


def read_args():
    descr = """
    Diagnostics of basic properties of LP Problems represented by the MPS-format.

    Examples of usage:
    python main.py
    python main.py -h
    python main.py --mps data/mps_tst/aez --outp foo.txt

    """
    # python main.py --path "message_ix/tools/lp_diag" --mps "test.mps" -s

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
    cl_args = parser.parse_args()
    return cl_args


if __name__ == "__main__":
    """Driver of the LP diagnostics script.

    Defines the working space, then controls the flow by executing the desired
    functions of LPdiag class.
    """

    dir1 = os.getcwd()
    print(f'{dir1 =}')
    tstart = dt.now()
    # print('Started at:', str(tstart))

    # Retrieve and assign arguments
    args = read_args()
    dir2 = os.getcwd()
    print(f'{dir2 =}')
    w_dir = args.wdir or "."
    # todo: change Data/mps_tst to: Test_mps, remove other Data
    # prob_id = args.mps or "Data/mps_tst/diet"  # default MPS for testing
    prob_id = args.mps or "Data/mps_tst/aez"  # default MPS for testing
    # prob_id = args.mps or "Data/mps_tst/err_tst"  # default MPS for testing
    # prob_id = args.mps or "Data/mps_tst/lotfi"  # default MPS for testing
    # prob_id = args.mps or "Data/mps/of_led1"  # default MPS for testing
    if len(w_dir) > 1:
        print(f"Changing work-directory to: {w_dir}.")
        try:
            os.chdir(w_dir)
        except OSError:
            print(f"Cannot change work-directory to: {w_dir}.")
    dir3 = os.getcwd()
    print(f'{dir3 =}')
    assert isfile(prob_id), (
        f"MPS file {prob_id} not accessible from the dir:\n'{dir3}'.\n"
        "Try to use the --wdir command option to set the work-directory."
    )
    assert access(prob_id, R_OK), f"MPS file {prob_id} is not readable."

    # small MPSs, for testing the code, posted to Data/mps_tst dir
    # err_tst  - small MPS with various errors for testing the diagnostics
    # aez  - agro-ecological zones, medium size; two matrix elems in a row
    # diet - classical small LP
    # jg_korh - tiny testing problem
    # lotfi - classical medium size; two matrix elems in a row

    # trouble-makers MPSs, large (over 1G) files, not posted to gitHub, locally in
    # data/mps dir
    # all large MPS files should be preferably copied to /t/fricko/for_marek/
    # (see Oliver's slack post of Feb 16th)
    # of_led1     - posted by Oliver in /t/fricko... on Feb 16, 2023 at 10:39 as:
    # OFR_test_led_barrier.mps
    # of_baselin  - second MPS from Oliver, posted on Feb 16, 2023 at 12:13 as:
    # baseline_barrier.mps

    # data_dir = 'data/mps_tst/'
    # prob_id = 'err_tst'
    # prob_id = 'aez'
    # prob_id = 'diet'
    # prob_id = 'jg_korh'
    # prob_id = 'lotfi'
    # data_dir = "data/mps/"
    # prob_id = 'of_led1'
    # prob_id = "of_baselin"
    # fn_mps = data_dir + prob_id
    # repdir = 'rep_shared/'      # subdirectory for shared reports (NOT in git-repo)
    # repdir = "rep_tst/"  # subdirectory for test-reports (NOT in git-repo)

    # redir_stdo = args.save
    fn_outp = args.outp or None  # optional redirection of stdout

    # redir_stdo = False  # redirect stdout to the file in repdir
    default_stdout = sys.stdout
    if fn_outp:
        # fn_out = "./" + repdir + prob_id + ".txt"  # file for redirected stdout
        print(f"Stdout redirected to: {fn_outp}")
        f_out = open(fn_outp, "w")
        sys.stdout = f_out
    # else:  # defined to avoid warnings (only used when redir_stdo == True)
    #     fn_out = "foo"
    #     f_out = open(fn_out, "w")

    # lp = LPdiag(repdir)  # LPdiag ctor
    dir4 = os.getcwd()
    print(f'{dir4 =}')

    lp = LPdiag()  # LPdiag ctor
    lp.rd_mps(prob_id)  # read MPS, store the matrix in dataFrame
    lp.stat(lo_tail=-7, up_tail=5)  # stats of matrix coeffs, incl. distrib. tails
    # to get numbers of coeffs for each magnitute specify equal/overlapping tails:
    # lp.stat(lo_tail=0, up_tail=0)
    lp.out_loc(small=True, thresh=-7, max_rec=100)  # locations of small-value outliers
    lp.out_loc(small=False, thresh=6, max_rec=500)  # locations of large-value outliers
    # lp.out_loc(small=True, thresh=-1, max_rec=100) # test (lotfi) small-value outliers
    # lp.out_loc(small=False, thresh=2, max_rec=500) # test (lotfi) large-value outliers

    tend = dt.now()
    time_diff = tend - tstart
    print("\nStarted at: ", str(tstart))
    print("Finished at:", str(tend))
    print(f"Wall-clock execution time: {time_diff.seconds} sec.")

    if fn_outp:  # close the redirected output
        # noinspection PyUnboundLocalVariable
        f_out.close()
        sys.stdout = default_stdout
        print(f"\nRedirected stdout stored in {fn_outp}. Now writing to the console.")
        print("\nStarted at: ", str(tstart))
        print("Finished at:", str(tend))
        print(f"Wall-clock execution time: {time_diff.seconds} sec.")

    # TODO: plots of distributions of coeffs, if indeed usefull
    # TODO: naive scaling? might not be informative due to the later preprocessing
    # TODO: conform(?) to the MPS-standard: in particular, reject numbers of
    # abs(val): greater than 10^{10} or smaller than 10^{-10}
    #   to be discussed, if desired; also if it should be exception-error or info
