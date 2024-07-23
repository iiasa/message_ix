*----------------------------------------------------------------------------------------------------------------------*
* sanity check of model run parameters, set defaults if not specified                                                  *
*----------------------------------------------------------------------------------------------------------------------*

* set # as end-of-line comment; all text after # is ignored
* (for proper display in GAMS IDE, this needs to be specified in the options, too)

*----------------------------------------------------------------------------------------------------------------------*
* sanity check of model run parameters, set defaults if not specified                                                  *
*----------------------------------------------------------------------------------------------------------------------*

* a datastructure name is mandatory to load the gdx file - abort the run if not specified or file does not exist
$IF NOT SET in       $ABORT "no input data file provided!"
$IF NOT EXIST '%in%' $ABORT "input GDX file '%in%' does not exist!"
$IF NOT SET iter     $SETGLOBAL iter "output/MsgIterationReport"
$IF NOT SET out      $SETGLOBAL out "output/MsgOutput.gdx"

** define the time horizon over which the model optimizes (perfect foresight, myopic or rolling horizon) **
* perfect foresight - 0 (assumed as default if not specified
* myopic optimization (period-by-period, recursive-dynamic without any foresight) - 1
* rolling horizon (period-by-period, recursive-dynamic with limited foresight - 'number of years of foresight'
$IF NOT SET foresight   $SETGLOBAL foresight "0"

** specify optional additional calibration output **
$IF NOT SET calibration $SETGLOBAL calibration ""
* mark with * to include detailed calibration information in outputs and get an extended GAMS listing (.lst) file

** debugging mode settings for support and assistance during model development and calibration **
* assume that all debugging options are deactivated by default
* mark as "*" to deactivate, mark as "" to activate

* set auxiliary upper and lower bounds on the actitivity variables to prevent unbounded models
$IF NOT SET AUX_BOUNDS               $SETGLOBAL AUX_BOUNDS "*"
$IF NOT SET AUX_BOUND_VALUE          $SETGLOBAL AUX_BOUND_VALUE "1e9"

* include relaxations for specific constraint blocks to identify infeasibilities during model development/calibration
* by adding 'slack' variables in the constraints and associated penalty factors in the objective function
$IF NOT SET SLACK_COMMODITY_EQUIVALENCE  $SETGLOBAL SLACK_COMMODITY_EQUIVALENCE "*"

$IF NOT SET SLACK_CAP_NEW_BOUND_UP   $SETGLOBAL SLACK_CAP_NEW_BOUND_UP "*"
$IF NOT SET SLACK_CAP_NEW_BOUND_LO   $SETGLOBAL SLACK_CAP_NEW_BOUND_LO "*"
$IF NOT SET SLACK_CAP_TOTAL_BOUND_UP $SETGLOBAL SLACK_CAP_TOTAL_BOUND_UP "*"
$IF NOT SET SLACK_CAP_TOTAL_BOUND_LO $SETGLOBAL SLACK_CAP_TOTAL_BOUND_LO "*"
$IF NOT SET SLACK_CAP_NEW_DYNAMIC_UP $SETGLOBAL SLACK_CAP_NEW_DYNAMIC_UP "*"
$IF NOT SET SLACK_CAP_NEW_DYNAMIC_LO $SETGLOBAL SLACK_CAP_NEW_DYNAMIC_LO "*"

$IF NOT SET SLACK_ACT_BOUND_UP       $SETGLOBAL SLACK_ACT_BOUND_UP "*"
$IF NOT SET SLACK_ACT_BOUND_LO       $SETGLOBAL SLACK_ACT_BOUND_LO "*"
$IF NOT SET SLACK_ACT_DYNAMIC_UP     $SETGLOBAL SLACK_ACT_DYNAMIC_UP "*"
$IF NOT SET SLACK_ACT_DYNAMIC_LO     $SETGLOBAL SLACK_ACT_DYNAMIC_LO "*"

$IF NOT SET SLACK_LAND_SCEN_UP       $SETGLOBAL SLACK_LAND_SCEN_UP "*"
$IF NOT SET SLACK_LAND_SCEN_LO       $SETGLOBAL SLACK_LAND_SCEN_LO "*"
$IF NOT SET SLACK_LAND_TYPE_UP       $SETGLOBAL SLACK_LAND_TYPE_UP "*"
$IF NOT SET SLACK_LAND_TYPE_LO       $SETGLOBAL SLACK_LAND_TYPE_LO "*"

$IF NOT SET SLACK_RELATION_BOUND_UP  $SETGLOBAL SLACK_RELATION_BOUND_UP "*"
$IF NOT SET SLACK_RELATION_BOUND_LO  $SETGLOBAL SLACK_RELATION_BOUND_LO "*"

*----------------------------------------------------------------------------------------------------------------------*
* initialize sets, mappings, parameters, load data, do pre-processing                                                  *
*----------------------------------------------------------------------------------------------------------------------*

** load auxiliary settings from include file (solver options, resource/time limits, prefered solvers) **
* recommended only for advanced users
$INCLUDE MESSAGE/auxiliary_settings.gms

* check that the version of MESSAGEix and the ixToolbox used for exporting the data to gdx match
$INCLUDE version.gms
$INCLUDE MESSAGE/version_check.gms

** initialize sets, mappings, parameters
$INCLUDE MESSAGE/sets_maps_def.gms
$INCLUDE MESSAGE/parameter_def.gms

** load data from gdx, run processing scripts of auxiliary parameters
$INCLUDE MESSAGE/data_load.gms

** compute auxiliary parameters for capacity and investment cost accounting
$INCLUDE MESSAGE/scaling_investment_costs.gms

*----------------------------------------------------------------------------------------------------------------------*
* variable and equation definition, model declaration                                                                  *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MESSAGE/model_core.gms
