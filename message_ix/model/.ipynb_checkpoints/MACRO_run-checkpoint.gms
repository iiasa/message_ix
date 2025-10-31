* a scenario name is mandatory to load the gdx file - abort the run if not specified or file does not exist
$IF NOT SET in       $ABORT "no input data file provided!"
$IF NOT EXIST '%in%' $ABORT "input GDX file '%in%' does not exist!"

** option to run MACRO standalone or interactively linked (iterating) with MESSAGE **
*$SETGLOBAL macromode "linked"
$SETGLOBAL macromode "standalone"

$INCLUDE MACRO/macro_data_load.gms
$INCLUDE MACRO/macro_core.gms
$INCLUDE MACRO/macro_calibration.gms
$INCLUDE MACRO/macro_reporting.gms

* dump all input data, processed data and results to a gdx file (with additional comment as name extension if provided)
$IF NOT SET out      $SETGLOBAL out "output/MsgOutput.gdx"
execute_unload "%out%"

