$TITLE The MESSAGEix Integrated Assessment Model
$ONDOLLAR
$INCLUDE includes/copyright.gms

***
* Run script for |MESSAGEix| (stand-alone)
* ========================================
*
* This is |MESSAGEix| version |version|. The version number must match the version number
* of the ``ixmp`` ``MESSAGE``-scheme specifications used for exporting data and importing results.
*
* This file contains the workflow of a |MESSAGEix|-standalone run. It can be called:
*
* - Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
*   calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the tutorials).
* - using the file ``MESSAGE_master.gms`` with the option ``$SETGLOBAL macromode "none"``,
*   where the input data file name and other options are stated explicitly, or
* - directly from the command line, with the input data file name
*   and other options specific as command line parameters, e.g.::
*
*   ``gams MESSAGE_run.gms --in="<data-file>" [--out="<output-file>"]``
*
* By default, the data file (in gdx format) should be located in the ``model/data`` folder
* and be named in the format ``MsgData_<name>.gdx``. Upon completion of the GAMS execution,
* a results file ``<output-file>`` will be written
* (or ``model\output\MsgOutput.gdx`` if ``--out`` is not provided).
***

$EOLCOM #
$INCLUDE MESSAGE/model_setup.gms

*----------------------------------------------------------------------------------------------------------------------*
* solve statements (including the loop for myopic or rolling-horizon optimization)                                     *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MESSAGE/model_solve.gms

*----------------------------------------------------------------------------------------------------------------------*
* post-processing and export to gdx                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

* include MESSAGE GAMS-internal reporting
$INCLUDE MESSAGE/reporting.gms

* dump all input data, processed data and results to a gdx file
execute_unload "%out%"

put_utility 'log' / /"+++ End of MESSAGEix (stand-alone) run - have a nice day! +++ " ;

*----------------------------------------------------------------------------------------------------------------------*
* end of file - have a nice day!                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*
