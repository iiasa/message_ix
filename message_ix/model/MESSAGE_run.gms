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

    Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, 
    Clara Orthofer, Michael Pimmer, Adriano Vinca, Alessio Mastrucci, Keywan Riahi, and Volker Krey.
    "The MESSAGEix Integrated Assessment Model and the ix modeling platform". 2018, submitted. 
    Electronic pre-print available at `pure.iiasa.ac.at/15157/`.

Please review the NOTICE at `MESSAGEix.iiasa.ac.at/notice.html`
and included in the GitHub repository for further user guidelines.
The community forum and mailing list is hosted at `groups.google.com/d/forum/message_ix`.

$OFFTEXT

***
* Run script for |MESSAGEix| (stand-alone)
* ========================================
* This page is generated from the auto-documentation in ``model/MESSAGE_run.gms``.
*
* This is |MESSAGEix| version |version|. The version number must match the version number
* of the ``ixmp`` ``MESSAGE``-scheme specifications used for exporting data and importing results.
*
* This file contains the workflow of a |MESSAGEix|-standalone run. It can be called:
*  - Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
*    calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the tutorials).
*  - using the file ``MESSAGE_master.gms`` with the option ``$SETGLOBAL macromode "none"``,
*    where the input data file name and other options are stated explicitly, or
*  - directly from the command line, with the input data file name
*    and other options specific as command line parameters, e.g.
*
*    ``gams MESSAGE_run.gms --in="<data-file>" [--out="<output-file>"]``
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

* calculation of commodity import costs by node, commodity and year
import_cost(node2, commodity, year) =
          SUM( (node,tec,vintage,mode,level,time,time2)$( (NOT sameas(node,node2)) AND map_tec_act(node2,tec,year,mode,time2)
            AND map_tec_lifetime(node2,tec,vintage,year) AND map_commodity(node,commodity,level,year,time) ),
* import into node2 from other nodes
          input(node2,tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time_rel(time,time2) * ACT.L(node2,tec,vintage,year,mode,time2)
        * COMMODITY_BALANCE.M(node,commodity,level,year,time) / discountfactor(year) )
;

* calculation of commodity export costs by node, commodity and year
export_cost(node2, commodity, year) =
          SUM( (node,tec,vintage,mode,level,time,time2)$( (NOT sameas(node,node2)) AND map_tec_act(node2,tec,year,mode,time2)
            AND map_tec_lifetime(node2,tec,vintage,year) AND map_commodity(node,commodity,level,year,time) ),
* export from node2 to other market
          output(node2,tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time_rel(time,time2) * ACT.L(node2,tec,vintage,year,mode,time2)
        * COMMODITY_BALANCE.M(node,commodity,level,year,time) / discountfactor(year) )
;

* net commodity trade costs by node and year
trade_cost(node2, year) = SUM(commodity, import_cost(node2, commodity, year) - export_cost(node2, commodity, year)) ;

* reporting of net total costs (excluding emission taxes) as result of MESSAGE run
COST_NODAL_NET.L(location,year) =
    COST_NODAL.L(location,year) + trade_cost(location,year)
* subtract emission taxes applied at any higher nodal level (via map_node set)
    - sum((type_emission,emission,type_tec,type_year,node)$( emission_scaling(type_emission,emission)
            AND map_node(node,location) AND cat_year(type_year,year) ),
        emission_scaling(type_emission,emission) * tax_emission(node,type_emission,type_tec,type_year)
        * EMISS.L(location,emission,type_tec,year) )
;

* include MESSAGE reporting
$INCLUDE MESSAGE/reporting.gms

* dump all input data, processed data and results to a gdx file
execute_unload "%out%"

put_utility 'log' / /"+++ End of MESSAGEix (stand-alone) run - have a nice day! +++ " ;

*----------------------------------------------------------------------------------------------------------------------*
* end of file - have a nice day!                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*

