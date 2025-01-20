$TITLE The MESSAGEix Integrated Assessment Model
$ONDOLLAR
$INCLUDE includes/copyright.gms

* activate dollar commands on a global level
$ONGLOBAL

*----------------------------------------------------------------------------------------------------------------------*
* model setup, data set selection, scenario selection, other settings                                                  *
*----------------------------------------------------------------------------------------------------------------------*

** scenario/case selection - this must match the name of the MsgData_<%%%>.gdx input data file **
$SETGLOBAL data "<your datafile name here>"

* MACRO mode. This can take 3 possible values, only 2 of which are usable with this file:
*
* - "none": MACRO is not run, MESSAGE is run in stand-alone mode.
* - "linked": MESSAGE and MACRO are run in linked/iterative mode.
* - "standalone": MACRO is run without MESSAGE. Not valid when using this file; use MACRO_run.gms instead.
$IF NOT SET macromode $SETGLOBAL macromode "none"

** define the time horizon over which the model optimizes (perfect foresight, myopic or rolling horizon) **
* perfect foresight - 0
* myopic optimization (period-by-period, recursive-dynamic without any foresight) - 1
* rolling horizon (period-by-period, recursive-dynamic with limited foresight - 'number of years of foresight'
$SETGLOBAL foresight "0"

** add a comment and name extension for model report files (e.g. run-specific info, calibration notes) - optional **
$SETGLOBAL comment ""

** specify optional calibration output **
$SETGLOBAL calibration ""
* mark as "*" to include detailed calibration information in outputs and get a longer listing file

*----------------------------------------------------------------------------------------------------------------------*
* debugging mode settings for support and assistance during model development and calibration                          *
*----------------------------------------------------------------------------------------------------------------------*
* mark as "*" to deactivate, mark as "" to activate

* set auxiliary upper/lower bounds on the actitivity variables to prevent unbounded rays during model development
$SETGLOBAL AUX_BOUNDS "*"
$SETGLOBAL AUX_BOUND_VALUE "1e9"

* include relaxations for specific constraint blocks to identify infeasibilities during model development/calibration
* by adding 'slack' variables in the constraints and associated penalty factors in the objective function
$SETGLOBAL SLACK_COMMODITY_EQUIVALENCE "*"

$SETGLOBAL SLACK_CAP_NEW_BOUND_UP "*"
$SETGLOBAL SLACK_CAP_NEW_BOUND_LO "*"
$SETGLOBAL SLACK_CAP_TOTAL_BOUND_UP "*"
$SETGLOBAL SLACK_CAP_TOTAL_BOUND_LO "*"
$SETGLOBAL SLACK_CAP_NEW_DYNAMIC_UP "*"
$SETGLOBAL SLACK_CAP_NEW_DYNAMIC_LO "*"

$SETGLOBAL SLACK_ACT_BOUND_UP "*"
$SETGLOBAL SLACK_ACT_BOUND_LO "*"
$SETGLOBAL SLACK_ACT_DYNAMIC_UP "*"
$SETGLOBAL SLACK_ACT_DYNAMIC_LO "*"

$SETGLOBAL SLACK_LAND_SCEN_UP "*"
$SETGLOBAL SLACK_LAND_SCEN_LO "*"
$SETGLOBAL SLACK_LAND_TYPE_UP "*"
$SETGLOBAL SLACK_LAND_TYPE_LO "*"

$SETGLOBAL SLACK_RELATION_BOUND_UP "*"
$SETGLOBAL SLACK_RELATION_BOUND_LO "*"

*----------------------------------------------------------------------------------------------------------------------*
* launch the MESSAGEix or MESSAGEix-MACRO run file with the settings as defined above                                      *
*----------------------------------------------------------------------------------------------------------------------*

$SETGLOBAL in "data/MsgData_%data%.gdx"
$IFTHEN %comment%==""
$SETGLOBAL out "output/MsgOutput_%data%.gdx"
$SETGLOBAL iter "output/MsgIterationReport_%data%.gdx"
$ELSE
$SETGLOBAL out "output/MsgOutput_%data%_%comment%.gdx"
$SETGLOBAL iter "output/MsgIterationReport_%data%_%comment%.gdx"
$ENDIF

$IFTHEN %macromode%=="none" $INCLUDE MESSAGE_run.gms
$ELSE $INCLUDE MESSAGE-MACRO_run.gms
$ENDIF

*----------------------------------------------------------------------------------------------------------------------*
* end of file - have a nice day!                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*
