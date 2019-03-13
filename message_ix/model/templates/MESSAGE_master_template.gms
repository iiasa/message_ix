$TITLE The MESSAGEix Integrated Assessment Model
$ONDOLLAR
$ONTEXT

   Copyright 2018 IIASA Energy Program

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

This is the GAMS implementation of the integrated assessment and system optimization model MESSAGEix
For the most recent version of the framework, please visit `github.com/iiasa/message_ix`.
For a comprehensive documentation of the latest release of the MESSAGEix framework
and the ix modeling platform, please visit `MESSAGEix.iiasa.ac.at/`.

When using the MESSAGEix framework, please cite as:

   Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, Clara Orthofer,
   Michael Pimmer, Nikolay Kushin, Adriano Vinca, Alessio Mastrucci,
   Keywan Riahi, and Volker Krey.
   "The |MESSAGEix| Integrated Assessment Model and the ix modeling platform".
   Environmental Modelling & Software 112:143-156, 2019.
   doi: 10.1016/j.envsoft.2018.11.012
   electronic pre-print available at pure.iiasa.ac.at/15157/

Please review the NOTICE at `MESSAGEix.iiasa.ac.at/notice.html`
and included in the GitHub repository for further user guidelines.
The community forum and mailing list is hosted at `groups.google.com/d/forum/message_ix`.

$OFFTEXT

* activate dollar commands on a global level
$ONGLOBAL

*----------------------------------------------------------------------------------------------------------------------*
* model setup, data set selection, scenario selection, other settings                                                  *
*----------------------------------------------------------------------------------------------------------------------*

** scenario/case selection - this must match the name of the MsgData_<%%%>.gdx input data file **
$SETGLOBAL data "<your datafile name here>"

** MACRO mode
* "none": MESSAGEix is run in stand-alone mode
* "linked": MESSAGEix-MACRO is run in iterative mode **
$SETGLOBAL macromode "none"

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
