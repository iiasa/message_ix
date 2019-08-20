$TITLE The MESSAGEix-MACRO Integrated Assessment Model
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

***
* Run script for |MESSAGEix| and MACRO
* ====================================
*
* This is |MESSAGEix|-MACRO version |version|. The version number must match the version number
* of the ``ixmp`` ``MESSAGE``-scheme specifications used for exporting data and importing results.
*
* This file contains the workflow of a |MESSAGEix|-MACRO run. It can be called:
*  - Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
*    calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the tutorials).
*  - using the file ``MESSAGE_master.gms`` with the option ``$SETGLOBAL macromode "linked"``,
*    where the input data file name and other options are stated explicitly, or
*  - directly from the command line, with the input data file name
*    and other options specific as command line parameters, e.g.
*
*    ``gams MESSAGE-MACRO_run.gms --in="<data-file>" [--out="<output-file>"]``
*
* By default, the data file (in gdx format) should be located in the ``model/data`` folder
* and be named in the format ``MsgData_<name>.gdx``. Upon completion of the GAMS execution,
* a results file ``<output-file>`` will be written
* (or ``model\output\MsgOutput.gdx`` if ``--out`` is not provided).
***

$SETGLOBAL macromode "linked"
$EOLCOM #
$INCLUDE MESSAGE/model_setup.gms

*----------------------------------------------------------------------------------------------------------------------*
* load additional equations and parameters for MACRO                                                                   *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MACRO/macro_data_load.gms
$INCLUDE MACRO/macro_core.gms

*----------------------------------------------------------------------------------------------------------------------*
* initialize sets, parameters and counters for the iteration between MESSAGEix and MACRO                               *
*----------------------------------------------------------------------------------------------------------------------*

* set default maximum iteration count and
$IF NOT set MAX_ITERATION            $SETGLOBAL MAX_ITERATION "50"
$IF NOT set MAX_ADJUSTMENT           $SETGLOBAL MAX_ADJUSTMENT "0.2"
$IF NOT set CONVERGENCE_CRITERION    $SETGLOBAL CONVERGENCE_CRITERION "0.01"

Set
    iteration / 1*%MAX_ITERATION% /
;

Scalar
    max_adjustment_pre maximum adjustment in previous iteration / 0 /
    max_adjustment_pos maximum positive adjustment in current iteration
    max_adjustment_neg maximum negative adjustment in current iteration
    max_adjustment     maximum adjustment in current iteration
    convergence_status status of convergence (1 if successful) / 0 /
    scaling            scaling factor to adjust step size when iteration oscillates / 1 /
;

* declarations moved from solve files to avoid inclusion in loop
Parameters
    demand_init(node,sector,year_all)
    demand_new(node,sector,year_all)
    demand_scale(node,sector,year_all)
    demand_diff_abs(*,node,sector,year_all)
    demand_diff_rel(*,node,sector,year_all)

    price_init(node,sector,year_all)
    price_diff_abs(*,node,sector,year_all)
    price_diff_rel(*,node,sector,year_all)

    report_iteration(iteration,*)
;

price_init(node,sector,year_all) = 0 ;

*----------------------------------------------------------------------------------------------------------------------*
* consistency checks                                                                                                   *
*----------------------------------------------------------------------------------------------------------------------*

* check that the historical-gdp values are assigned for the MACRO baseyear (period prior to 'firstmodelyear')
* otherwise, this will result in a LOG(0) error after the first MESSAGE solve
loop((node_macro,macro_base_period),
    if( not historical_gdp(node_macro,macro_base_period),
        put_utility 'log'/" Error: Historical GDP not assigned for MACRO base-year for node '"node_macro.tl:0"' !" ;
        check = 1 ;
    ) ;
) ;
if (check,
    abort "There is a problem with the parameter 'historical_gdp'!" ;
) ;

*----------------------------------------------------------------------------------------------------------------------*
* solve statements (including the loop for myopic or rolling-horizon optimization)                                     *
*----------------------------------------------------------------------------------------------------------------------*

LOOP(iteration,

put_utility 'log' /"+++ Starting iteration ", ORD(iteration):0:0, " of MESSAGEix-MACRO... +++ " ;

*----------------------------------------------------------------------------------------------------------------------*
* solve MESSAGE model                                                                                                  *
*----------------------------------------------------------------------------------------------------------------------*

* to keep the model in memory between runs, this will speed up computation
MESSAGE_LP.solvelink = 1 ;

$INCLUDE MESSAGE/model_solve.gms

report_iteration(iteration, 'MESSAGEix OBJ') = OBJ.l ;

*----------------------------------------------------------------------------------------------------------------------*
* calculate scenario dependent MACRO parameters based on MESSAGE model run                                             *
*----------------------------------------------------------------------------------------------------------------------*

* include the period prior to the first model horizon in the MACRO solve loop
year(year_all) = no ;
year(year_all)$( model_horizon(year_all) ) = yes ;
year(year_all)$( macro_base_period(year_all) ) = yes ;

* useful energy/service demand levels from MESSAGE get mapped onto MACRO sector structure
enestart(node_macro,sector,year) = SUM((commodity, level, time) $ mapping_macro_sector(sector, commodity, level),
                                 DEMAND.L(node_macro,commodity,level,year,time) * duration_time(time) ) / 1000
;

demand_init(node_macro,sector,year) = SUM((commodity, level, time)$mapping_macro_sector(sector, commodity, level),
    demand_fixed(node_macro,commodity,level,year,time) ) ;

* useful energy/service demand prices from MESSAGE get mapped onto MACRO sector structure

eneprice(node_macro,sector,year) $(NOT macro_base_period(year)) = SUM((commodity, level, time) $ mapping_macro_sector(sector, commodity, level),
                                 PRICE_COMMODITY.L(node_macro,commodity,level,year,time) * duration_time(time) )
;

price_diff_abs(iteration,node_macro,sector,year)$( price_init(node_macro,sector,year) ) =
    eneprice(node_macro,sector,year) - price_init(node_macro,sector,year) ;
price_diff_rel(iteration,node_macro,sector,year)$( price_init(node_macro,sector,year) ) =
    price_diff_abs(iteration,node_macro,sector,year) / price_init(node_macro,sector,year) ;

price_init(node_macro,sector,year) = SUM((commodity, level, time) $ mapping_macro_sector(sector, commodity, level),
                                        PRICE_COMMODITY.l(node_macro,commodity,level,year,time) ) ;

DISPLAY enestart, eneprice, total_cost ;

*----------------------------------------------------------------------------------------------------------------------*
* solve MACRO model                                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MACRO/macro_solve.gms

*----------------------------------------------------------------------------------------------------------------------*
* adjust MESSAGE useful energy/service demand levels to MACRO demand levels                                            *
*----------------------------------------------------------------------------------------------------------------------*

demand_new(node_macro,sector,year) = PHYSENE.L(node_macro, sector, year) * 1000 ;

demand_diff_abs(iteration,node_macro,sector,year) $(NOT macro_base_period(year)) =
    demand_new(node_macro,sector,year) - demand_init(node_macro,sector,year) ;
demand_diff_rel(iteration,node_macro,sector,year) $(NOT macro_base_period(year)) =
    demand_diff_abs(iteration,node_macro,sector,year) / demand_init(node_macro,sector,year) ;

* compute the relative difference between the previous demand and the updated demand from MACRO
demand_scale(node_macro,sector,year)$(NOT macro_base_period(year)) =
    demand_new(node_macro,sector,year)
        / SUM((commodity, level, time) $ mapping_macro_sector(sector, commodity, level),
            demand_fixed(node_macro,commodity,level,year,time) * duration_time(time) ) ;

* limit MACRO demand scaling to relative the maximum adjustment level (defined using SETGLOBAL from command line)
demand_scale(node_macro,sector,year)$(NOT macro_base_period(year)) =
    min(demand_scale(node_macro,sector,year), 1 + %MAX_ADJUSTMENT% / scaling) ;
demand_scale(node_macro,sector,year)$(NOT macro_base_period(year)) =
    max(demand_scale(node_macro,sector,year), 1 - %MAX_ADJUSTMENT% / scaling) ;

* reporting of net total costs (excluding emission taxes) and GDP as result of MESSAGE-MACRO iteration
COST_NODAL_NET.L(node_macro,year) =
    COST_NODAL.L(node_macro,year) + trade_cost(node_macro,year)
* subtract emission taxes applied at any higher nodal level (via map_node set)
    - sum((type_emission,emission,type_tec,type_year,node)$( emission_scaling(type_emission,emission)
            AND map_node(node,node_macro) AND cat_year(type_year,year) ),
        emission_scaling(type_emission,emission) * tax_emission(node,type_emission,type_tec,type_year)
        * EMISS.L(node_macro,emission,type_tec,year) )
;

GDP.L(node_macro,year) = (I.L(node_macro,year) + C.L(node_macro,year) + EC.L(node_macro,year)) * 1000 ;

* calculate convergence level (maximum absolute scaling factor minus 1 across all regions, sectors, and years)
max_adjustment_pos = smax((node_macro,sector,year)$( NOT macro_base_period(year) AND demand_scale(node_macro,sector,year) > 1),
    demand_scale(node_macro,sector,year) - 1 ) ;
max_adjustment_neg = smin((node_macro,sector,year)$( NOT macro_base_period(year) AND demand_scale(node_macro,sector,year) < 1),
    demand_scale(node_macro,sector,year) - 1 ) ;
max_adjustment = max_adjustment_pos ;
max_adjustment$( max_adjustment_neg < - max_adjustment_pos ) = max_adjustment_neg ;

report_iteration(iteration, 'max adjustment pos') = max_adjustment_pos ;
report_iteration(iteration, 'max adjustment neg') = -max_adjustment_neg ;
report_iteration(iteration, 'absolute max adjustment max/min') = abs(max_adjustment) ;
report_iteration(iteration, 'adjustment bound') = %MAX_ADJUSTMENT% / scaling ;

* terminate iteration if convergence criterion is satisfied
if ( abs(max_adjustment) < %CONVERGENCE_CRITERION%,
    convergence_status = 1 ;
    if ( ORD(iteration) = 1,
        put_utility 'log' /"+++ Convergence criteria satisfied after the first iteration +++ " ;
    else
        put_utility 'log' /"+++ Convergence criteria satisfied after ", ORD(iteration):0:0, " iterations +++ " ;
    ) ;
    break ;
) ;

* check whether oscillation occurs during the iteration - if the sign of the adjusment switches, reduce maximum adjustment
if ( ORD(iteration) > 1 AND sign(max_adjustment_pre) = -sign(max_adjustment)
        AND abs(max_adjustment_pre) > abs(max_adjustment) * 0.9,
    scaling = scaling * sqrt(2) ;
    put_utility 'log' /"+++ Indication of oscillation, increase the scaling parameter (", scaling:0:0, ") +++" ;
elseif abs( max_adjustment_pos + max_adjustment_neg ) < 1e-4 ,
    scaling = scaling * sqrt(2) ;
*    scaling = scaling + 1;
    put_utility 'log' /"+++ Indication of instability, increase the scaling parameter (", scaling:0:0, ") +++" ;
) ;

* store the maximum adjustment in this iteration for the oscillation-prevention query in the next iteration
max_adjustment_pre = max_adjustment;

* demand adjustment for next iteration (only implemented if convergence criterion not met)
demand_fixed(node_macro,commodity,level,year,time) $(NOT macro_base_period(year) AND (SUM(sector $ mapping_macro_sector(sector, commodity, level), 1) > 0)) =
    SUM(sector $ mapping_macro_sector(sector, commodity, level), demand_scale(node_macro,sector,year) * demand_fixed(node_macro,commodity,level,year,time)) ;
DEMAND.L(node_macro,commodity,level,year,time) $(NOT macro_base_period(year)) = demand_fixed(node_macro,commodity,level,year,time) ;

DISPLAY COST_NODAL_NET.L, DEMAND.L, GDP.L, demand_scale ;

execute_unload "%iter%" report_iteration;

* write computation time to log file
$INCLUDE includes/aux_computation_time.gms
) ;

*----------------------------------------------------------------------------------------------------------------------*
* post-processing and export to gdx                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MESSAGE/reporting.gms

* dump all input data, processed data and results to a gdx file (with additional comment as name extension if provided)
execute_unload "%out%"

if (convergence_status = 0,
    put_utility 'log' /"+++ ERROR: Convergence criterion not satisfied after ", CARD(iteration):0:0, " iterations! +++ " ;
    put_utility 'log' /"+++ Adjustment in last iteration: ", abs(max_adjustment):6:3, " (", %CONVERGENCE_CRITERION%, ") +++" ;
    abort "MESSAGEix-MACRO did not converge!"
) ;

put_utility 'log' /"+++ End of MESSAGEix-MACRO run - have a nice day! +++ " ;

*----------------------------------------------------------------------------------------------------------------------*
* end of file - have a nice day!                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*
