* a scenario name is mandatory to load the gdx file - abort the run if not specified or file does not exist
$IF NOT set data                        $ABORT "No scenario specified for the MESSAGE model run!"
$IF NOT EXIST 'data/MSGdata_%data%.gdx' $ABORT "No file 'data/MSGdata_%data%' exists in the 'data' folder!"

** option to run MACRO standalone or interactively linked (iterating) with MESSAGE **
*$SETGLOBAL macromode "linked"
$SETGLOBAL macromode "standalone"

$INCLUDE MACRO/macro_data_load.gms
$INCLUDE MACRO/macro_core.gms
$INCLUDE MACRO/macro_calibration.gms
*$INCLUDE MACRO/macro_solve.gms
$INCLUDE MACRO/macro_reporting.gms

* dump all input data, processed data and results to a gdx file (with additional comment as name extension if provided)
$IF NOT %comment%=="" $SETGLOBAL comment "_%comment%"
execute_unload "output/MsgOutput_%data%%comment%.gdx"

