* Run MACRO in stand-alone mode, without MESSAGE.
* To run coupled with MESSAGE, use MESSAGE-MACRO_run.gms instead of this file.
$SETGLOBAL macromode "standalone"

$INCLUDE MACRO/setup.gms
$INCLUDE MACRO/macro_data_load.gms
$INCLUDE MACRO/macro_core.gms
$INCLUDE MACRO/macro_calibration.gms
$INCLUDE MACRO/macro_reporting.gms

* dump all input data, processed data and results to a gdx file (with additional comment as name extension if provided)
execute_unload "%out%"
