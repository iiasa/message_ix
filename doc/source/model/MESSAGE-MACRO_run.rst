.. note:: This page is generated from inline documentation in ``MESSAGE-MACRO_run.gms``.

Run script for |MESSAGEix| and MACRO
====================================

This is |MESSAGEix|-MACRO version |version|. The version number must match the version number
of the ``ixmp`` ``MESSAGE``-scheme specifications used for exporting data and importing results.

This file contains the workflow of a |MESSAGEix|-MACRO run. It can be called:
 - Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
   calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the tutorials).
 - using the file ``MESSAGE_master.gms`` with the option ``$SETGLOBAL macromode "linked"``,
   where the input data file name and other options are stated explicitly, or
 - directly from the command line, with the input data file name
   and other options specific as command line parameters, e.g.

   ``gams MESSAGE-MACRO_run.gms --in="<data-file>" [--out="<output-file>"]``

By default, the data file (in gdx format) should be located in the ``model/data`` folder
and be named in the format ``MsgData_<name>.gdx``. Upon completion of the GAMS execution,
a results file ``<output-file>`` will be written
(or ``model\output\MsgOutput.gdx`` if ``--out`` is not provided).

