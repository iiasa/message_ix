* A scenario name is mandatory to load the gdx file - abort the run if not specified or file does not exist
$IF NOT SET in       $ABORT "no input data file provided!"
$IF NOT EXIST '%in%' $ABORT "input GDX file '%in%' does not exist!"
$IF NOT SET out      $SETGLOBAL out "output/MsgOutput.gdx"

* MACRO mode. This can take 3 possible values:
*
* - "none": MACRO is not run, MESSAGE is run in stand-alone mode.
* - "linked": MESSAGE and MACRO are run in linked/iterative mode.
*   This value is set in MESSAGE-MACRO_run.gms.
* - "standalone": MACRO is run without MESSAGE.
*   This value is set in MACRO_run.gms
$IF NOT SET macromode $ABORT "The global setting/command line option --macromode must be set"

* Option to solve MACRO either…
*
* - 0: in sequence
* - 1: in parallel
*
* See macro_solve.gms
$IF NOT SET MACRO_CONCURRENT $SETGLOBAL MACRO_CONCURRENT "0"
