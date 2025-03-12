$TITLE The MESSAGEix-MACRO Integrated Assessment Model
$ONDOLLAR
$INCLUDE includes/copyright.gms

***
* Run script for |MESSAGEix| and MACRO
* ====================================
*
* This is |MESSAGEix|-MACRO version |version|. The version number must match the version number
* of the ``ixmp`` ``MESSAGE``-scheme specifications used for exporting data and importing results.
*
* This file contains the workflow of a |MESSAGEix|-MACRO run. It can be called:
*
* - Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
*   calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the tutorials).
* - using the file ``MESSAGE_master.gms`` with the option ``$SETGLOBAL macromode "linked"``,
*   where the input data file name and other options are stated explicitly, or
* - directly from the command line, with the input data file name
*   and other options specific as command line parameters, e.g.::
*
*   ``gams MESSAGE-MACRO_run.gms --in="<data-file>" [--out="<output-file>"]``
*
* By default, the data file (in gdx format) should be located in the ``model/data`` folder
* and be named in the format ``MsgData_<name>.gdx``. Upon completion of the GAMS execution,
* a results file ``<output-file>`` will be written
* (or ``model\output\MsgOutput.gdx`` if ``--out`` is not provided).
***

* Run MESSAGE and MACRO in linked/iterative mode mode.
* To run MACRO alone, use MACRO_run.gms instead of this file.
* To run MESSAGE alone, use MESSAGE_run.gms or MESSAGE_master.gms instead of this file.
$SETGLOBAL macromode "linked"
$EOLCOM #
$INCLUDE MESSAGE/model_setup.gms

*----------------------------------------------------------------------------------------------------------------------*
* load additional equations and parameters for MACRO                                                                   *
*----------------------------------------------------------------------------------------------------------------------*

$INCLUDE MACRO/setup.gms
$INCLUDE MACRO/macro_data_load.gms
$INCLUDE MACRO/macro_core.gms

*----------------------------------------------------------------------------------------------------------------------*
* initialize sets, parameters and counters for the iteration between MESSAGEix and MACRO                               *
*----------------------------------------------------------------------------------------------------------------------*

* command-line parameters for convergence and oscillation detection
$IF NOT set CONVERGENCE_CRITERION    $SETGLOBAL CONVERGENCE_CRITERION "0.01"
$IF NOT set MAX_ADJUSTMENT           $SETGLOBAL MAX_ADJUSTMENT "0.2"
$IF NOT set MAX_ITERATION            $SETGLOBAL MAX_ITERATION "50"
DISPLAY "%CONVERGENCE_CRITERION%", "%MAX_ADJUSTMENT%", "%MAX_ITERATION%";

Set
    iteration          allowable iterations                                         / 1*%MAX_ITERATION% /
;

* NB MAX_ADJUSTMENT and max_adjustment have different meanings:
* - MAX_ADJUSTMENT is a fixed threshold used to truncate the relative demand change produced by MACRO.
* - max_adjustment is the amount of that change, after any truncation.
Scalar
    max_adjustment_pre maximum adjustment in previous iteration                     / 0 /
    max_adjustment_pos maximum positive adjustment in current iteration
    max_adjustment_neg maximum negative adjustment in current iteration
    max_adjustment     maximum adjustment in current iteration
    convergence_status status of convergence (1 if successful)                      / 0 /
    scaling            scaling factor to adjust step size when iteration oscillates / 1 /
    max_it             maximum number of iterations                                 / %MAX_ITERATION% /
    ctr                iteration counter                                            / 0 /
    obj_func_chng      change of objective function compared to iteration-1         / 0 /
    obj_func_chng_pre  change of objective function of iteration-1 compared to iteration-2 / 0 /
    obj_func_pre       objective function from iteration-1                          / 0 /
    osc_check          tracks which oscillation check is used                       / 0 /
    osc_check_final    tracks if any oscillation check has been triggered           / 0 /
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

* variables to report back to user if needed
Variables
    N_ITER
    MAX_ITER
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

ctr = ctr + 1 ;

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

* Add entries to log-file
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
    if ( osc_check_final = 1,
        put_utility 'log' /"+++ Convergence achieved via oscillation check mechanism; check iteration log for further details +++ " ;
    else
        put_utility 'log' /"+++ Natural convergence achieved +++ " ;
    ) ;
    break ;
) ;

* Calculate change in objective function for use in oscillation check 3
if ( ORD(iteration) > 1,
    obj_func_chng = 1 - (OBJ.l / obj_func_pre);
) ;

* Perform oscillation checks:
* Oscillation check 1: Does the sign of the `max_adjustment` parameter change?
if ( ORD(iteration) > 1 AND sign(max_adjustment_pre) = -sign(max_adjustment)
        AND abs(max_adjustment_pre) > abs(max_adjustment) * 0.9,
    scaling = scaling * sqrt(2) ;
    osc_check = 1 ;
    osc_check_final = 1;
    put_utility 'log' /"+++ Indication of oscillation, increase the scaling parameter (", scaling:0:0, ") +++" ;
* Oscillation check 2: Are the maximum-positive and maximum-negative adjustments equal to each other?
elseif abs( max_adjustment_pos + max_adjustment_neg ) < 1e-4 ,
    scaling = scaling * sqrt(2) ;
    osc_check = 2 ;
    osc_check_final = 1 ;
    put_utility 'log' /"+++ Indication of instability, increase the scaling parameter (", scaling:0:0, ") +++" ;
* Oscillation check 3: Do the solutions jump between two objective functions?
elseif ORD(iteration) > 2 AND abs(obj_func_chng_pre + obj_func_chng) < 1e-4 ,
    scaling = scaling * sqrt(2) ;
    osc_check = 3 ;
    osc_check_final = 1;
    put_utility 'log' /"+++ Indication of oscillating objective function, increase the scaling parameter (", scaling:0:0, ") +++" ;
) ;

* Add entry to log-file about which of the checks have been used.
report_iteration(iteration, 'oscillation check') = osc_check ;
* Reset check for next iteration.
osc_check = 0;

* Store current calculated change in objective function to *_pre* for use in the next iteration.
obj_func_pre = OBJ.l
if ( ORD(Iteration) > 1,
    obj_func_chng_pre = obj_func_chng;
) ;

* In the case that the model solves with unscaled infeasibilities, the cplex options file `cplex.op2`
* will be used which forces the use of `Dual Crossover` when solving with Barrier. This will avoid
* solving further with unscaled infeasibilities.
* When encountering unscaled infeasibilities, modelstat = 1 and solvestat = 4.

if( MESSAGE_LP.solvestat = 4,
   put_utility 'log' /'+++ Detected issues solving with unscaled infeasibilities. Enforcing Dual crossover +++ ' ;
   MESSAGE_LP.optFile = 2;
   report_iteration(iteration, 'unscaled infeasibilities') = 1 ;
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

N_ITER.L = ctr ;
MAX_ITER.L = max_it ;


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
