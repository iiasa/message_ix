Parameters
         demand_scale(node,sector,year_all)
         demand_new(node,sector,year_all)
         aeei_correction(node,sector,year_all)
         growth_correction(node,year_all)
         gdp_scale(node, year_all)
         gdp_mer_macro(node, year_all)
;

Scalar
         max_scale / 0.2 /
         max_it    / 100 /
;

Variables
         aeei_calibrate(node,sector,year_all)
         grow_calibrate(node,year_all)
         N_ITER
         MAX_ITER
;

* ------------------------------------------------------------------------------
* solving the model region by region
* ------------------------------------------------------------------------------

* no check is made to see if a certain convergence criteria is acheived.
* MAX_ITER will determine the number of iterations after which the calibration is automatically halted.
FOR (ctr = 1 TO max_it BY 1,

* ------------------------------------------------------------------------------
* solve MACRO model
* ------------------------------------------------------------------------------

$INCLUDE MACRO/macro_solve.gms

demand_new(node_macro,sector,year) = PHYSENE.L(node_macro, sector, year) * 1000 ;
aeei_correction(node_macro,sector,year) = 0 ;
growth_correction(node_macro,year) = 0 ;

demand_scale(node_macro,sector,year) = min(demand_new(node_macro,sector,year) / demand_MESSAGE(node_macro,sector,year), 1 + max_scale) ;
demand_scale(node_macro,sector,year) = max(demand_scale(node_macro,sector,year), 1 - max_scale) ;
demand_new(node_macro,sector,year) = demand_scale(node_macro,sector,year) * demand_MESSAGE(node_macro,sector,year) ;

If (mod(ctr, 2) eq 0,
* calculate correction factor for labour force growth rate and apply for next iteration of MACRO
    gdp_mer_macro(node_macro,year) = (I.L(node_macro,year) + C.L(node_macro,year) + EC.L(node_macro,year)) * 1000 ;
    gdp_scale(node_macro,year) = gdp_mer_macro(node_macro,year)/gdp_calibrate(node_macro,year) ;
    growth_correction(node_macro,year) $ (NOT macro_base_period(year)) = SUM(year2 $ seq_period(year2,year), ((gdp_calibrate(node_macro,year)/gdp_calibrate(node_macro,year2))**(1/duration_period(year)))
                                                                                                           - ((gdp_mer_macro(node_macro,year)/gdp_mer_macro(node_macro,year2))**(1/duration_period(year))) ) ;
    grow(node_macro,year) = grow(node_macro,year) + growth_correction(node_macro,year) ;
Elseif mod(ctr, 2) eq 1,
* calculate correction factor for aeei and apply for next iteration of MACRO
    aeei_correction(node_macro,sector,year) $ (NOT macro_base_period(year)) = SUM(year2 $ seq_period(year2,year), ((demand_new(node_macro,sector,year)/demand_MESSAGE(node_macro,sector,year)) / (demand_new(node_macro,sector,year2)/demand_MESSAGE(node_macro,sector,year2)))**(1/duration_period(year)) - 1) ;
    aeei(node_macro,sector,year) = aeei(node_macro,sector,year) + aeei_correction(node_macro,sector,year);
) ;
DISPLAY demand_scale, aeei_correction ;
DISPLAY growth_correction, gdp_mer_macro, gdp_scale ;

* ------------------------------------------------------------------------------
* recalculation of parameters that are AEEI or growth dependent
* ------------------------------------------------------------------------------

* calculate cumulative growth effect and potential GDP
growth_factor(node_macro, macro_base_period) = 1;

LOOP(year $ (NOT macro_base_period(year)),
    growth_factor(node_macro, year) = SUM(year2$( seq_period(year2,year) ), growth_factor(node_macro, year2) * (1 + grow(node_macro, year))**(duration_period(year))) ;
) ;

potential_gdp(node_macro, year) = sum(macro_base_period, historical_gdp(node_macro, macro_base_period)/1000) * growth_factor(node_macro, year) ;

* calculation of cumulative effect of AEEI over time
aeei_factor(node_macro, sector, macro_initial_period) = 1;

LOOP(year_all $ ( ORD(year_all) > sum(year_all2$( macro_initial_period(year_all2) ), ORD(year_all2) ) ),
aeei_factor(node_macro, sector, year_all) = SUM(year_all2$( seq_period(year_all2,year_all) ), ( (1 - aeei(node_macro, sector, year_all)) ** duration_period(year_all) ) * aeei_factor(node_macro, sector, year_all2))
);

* recalculate total labor supply, new labor supply and utility discount factor
udf(node_macro, macro_base_period)   = 1 ;
labor(node_macro, macro_base_period) = 1 ;

LOOP(year_all $( ORD(year_all) > sum(year_all2$( macro_initial_period(year_all2) ), ORD(year_all2) ) ),
* exogenous labor supply growth (including both changes in labor force and labor productivity growth)
   labor(node_macro, year_all)  = SUM(year_all2$( seq_period(year_all2,year_all) ), labor(node_macro, year_all2) * (1 + grow(node_macro, year_all))**duration_period(year_all)) ;
* new labor supply
   newlab(node_macro, year_all) = SUM(year_all2$( seq_period(year_all2,year_all) ), (labor(node_macro, year_all) - labor(node_macro, year_all2)*(1 - depr(node_macro))**duration_period(year_all))$((labor(node_macro, year_all) - labor(node_macro, year_all2)*(1 - depr(node_macro))**duration_period(year_all)) > 0)) + epsilon ;
* calculation of utility discount factor based on discount rate (drate)
   udf(node_macro, year_all)    = SUM(year_all2$( seq_period(year_all2,year_all) ), udf(node_macro, year_all2) * (1 - (drate(node_macro) - grow(node_macro, year_all)))**duration_period(year_all)) ;
);

* recalcualte finite time horizon correction of utility function
finite_time_corr(node_macro, year) = abs(drate(node_macro) - grow(node_macro, year)) ;

) ;

* export calibration results as reporting variables to GDX
aeei_calibrate.L(node_macro,sector,year) = aeei(node_macro,sector,year) ;
grow_calibrate.L(node_macro,year) = grow(node_macro,year) ;

* subtract one due to 1-based indexing
N_ITER.L = ctr - 1;
MAX_ITER.L = max_it ;

* write solution statistics
status('MESSAGE_MACRO','modelstat') = 1 ;
status('MESSAGE_MACRO','solvestat') = 1 ;
status('MESSAGE_MACRO','resUsd')    = MESSAGE_MACRO.resUsd ;
status('MESSAGE_MACRO','objEst')    = MESSAGE_MACRO.objEst ;
status('MESSAGE_MACRO','objVal')    = MESSAGE_MACRO.objVal ;
