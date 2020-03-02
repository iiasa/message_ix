
*----------------------------------------------------------------------------------------------------------------------*
* set and parameter definitions                                                                                        *
*----------------------------------------------------------------------------------------------------------------------*

* indices to parameters will always be in the following order:
* node(location),commodity,level,year(actual),year(vintage),


$IF %macromode% == 'linked' $GOTO macro_sets

* main sets shared with MESSAGE (imported from database)
Sets
    node           all nodes included in the MESSAGE datastructure
    type_node      types of node categories
    cat_node(type_node,node) mapping of node types to nodes
    commodity       commodity ( resources - oil - gas - electricty - water - land availability - etc. )
    level           level ( primary - secondary - ... - useful )
    year_all        years (over entire model horizon)
    year(year_all)  years included in a model instance (for myopic or rolling-horizon optimization)
    time            subannual time periods (seasons - days - hours)
    type_year                types of year aggregations (for easy creation of subsets etc.)
    cat_year(type_year,year_all) mapping of years to respective categories (for simple reference in summations etc.)
;

* definition of aliases shared with MESSAGE

Alias(year_all,year_all2);
Alias(year_all,year_all3);
Alias(year,year2);
Alias(year,year3);
Alias(time,time2);

$LABEL macro_sets

* sets specific to MACRO

Sets
    node_macro(node) nodes actually relevant for the MACRO mode
    node_active(node)   active node - region - grid cell
    sector      Energy Sectors for macro-economic analysis in MACRO
    mapping_macro_sector(sector, commodity, level) mapping of energy sectors in MACRO to MESSAGE commodity and level combinations
;

* parameters specific to MACRO

SCALAR node_counter   'node counter for looping over regions' ;

SCALAR  epsilon            small number to avoid divergences
        / 0.01 /
;

PARAMETERS
         i0(node)                    Initial investment in base year
         c0(node)                    Initial consumption in base year
         k0(node)                    Initial capital in base year
         y0(node)                    Initial output in base year

         gdp_calibrate(node, year_all) Calibrated GDP (Trillion $)
         gdp_base(node)              Initial GDP (Trillion $) in base year
         kgdp(node)                  Initial capital to GDP ratio in base year
         depr(node)                  Annual percent depreciation
* VK, 10 April 2008: DRATE (social discount rate, i.e. net rate of return on capital from MESSAGE) introduced as a new parameter as in MERGE 5
         drate(node)                 Social discount rate
         esub(node)                  Elasticity between capital-labor (K-L) and energy (Sum E)
         rho(node)                   Production function exponent between capital-labor and energy nest (rho = (esub - 1) : esub)
         kpvs(node)                  Capital value share parameter
         ecst0(node)                 Energy costs in base year
         demand_base(node,sector)    base year consumption level of energy services from MESSAGE

         lakl(node)                  Production function coefficient of capital and labor
         prfconst(node, sector)      Production function coefficient of different energy sectors

         enestart(node,sector,year_all)  Consumption level of energy services from MESSAGE model run
         eneprice(node,sector,year_all)  Shadow prices of energy services from MESSAGE model run
         total_cost(node,year_all)       Total energy system costs from MESSAGE model run

* the following three parameters are used for running MACRO standalone and for calibration purposes
         demand_MESSAGE(node,sector,year_all) consumption level of energy services from MESSAGE model run
         price_MESSAGE(node,sector,year_all)  shadow prices of energy services from MESSAGE model run
         cost_MESSAGE(node,year_all)          total energy system costs from MESSAGE model run

         udf(node, year_all)             Utility discount factor in period year
         labor(node, year_all)           Labor force (efficiency units) in period year
         newlab(node, year_all)          New vintage of labor force in period year

         grow(node, year_all)            Annual growth rates of potential GDP
         aeei(node, sector, year_all)    Annual potential decrease of energy intensity in sector sector
         aeei_factor(node, sector, year_all) Cumulative effect of autonomous energy efficiency improvement (AEEI)

         finite_time_corr(node, year_all) finite time horizon correction factor in utility function
         lotol(node)                 Tolerance factor for lower bounds on MACRO variabales

         SVKN(node, year_all)    'start values for new capital variable KN'
         SVNEWE(node, sector, year_all)    'start values for new energy variable'

         historical_gdp(node,year_all)     historical GDP used for the base year (including running MACRO with slicing)
;
Parameters
* general parameters
    duration_period(year_all)     duration of one multi-year period (in years)
* parameters for spatially and temporally flexible formulation, and for myopic/rolling-horizon optimization
    duration_period_sum(year_all,year_all2)   number of years between two periods ('year_all' must precede 'year_all2')
    interestrate(year_all)         interest rate (to compute discount factor)
    df_period(year_all)            cumulative discount factor over period duration
    df_year(year_all)              discount factor of the last year in the period
;

*----------------------------------------------------------------------------------------------------------------------*
* Auxiliary variables for workflow                                                                                     *
*----------------------------------------------------------------------------------------------------------------------*

Parameters
    ctr               counter parameter for loops
    status(*,*)       model solution status parameter for log writing
;

*----------------------------------------------------------------------------------------------------------------------*
* load relevant sets and parameters from dataset gdx                                                                            *
*----------------------------------------------------------------------------------------------------------------------*

$GDXIN '%in%'
$IF %macromode% == 'linked' $GOTO macro_data

$LOAD node
$LOAD year_all = year,type_year,cat_year,time
$LOAD duration_period
$LOAD commodity,level
$LOAD interestrate
$LABEL macro_data

$LOAD type_node,cat_node
$LOAD sector,mapping_macro_sector
$LOAD kpvs,kgdp,esub,depr,drate,lotol
$LOAD lakl,prfconst
$LOAD aeei,grow
$LOAD gdp_calibrate,historical_gdp
$LOAD demand_MESSAGE,price_MESSAGE,cost_MESSAGE
$GDXIN

node_macro(node)$( cat_node('economy',node) ) = yes ;

DISPLAY node_macro ;
*cat_year("baseyear_macro","2010") = no ;
*cat_year("baseyear_macro","2030") = yes ;
*cat_year("firstmodelyear","2020") = no ;
*cat_year("firstmodelyear","2040") = yes ;

* ------------------------------------------------------------------------------
* define sets for period structure
* ------------------------------------------------------------------------------

* compute auxiliary parameters for duration over periods (years)
$INCLUDE includes/period_parameter_assignment.gms

year(year_all) = no ;
year(year_all)$( ORD(year_all) >= sum(year_all2$cat_year("initializeyear_macro",year_all2), ORD(year_all2) ) ) = yes ;

DISPLAY cat_year, macro_base_period, first_period, last_period, macro_horizon, year ;

* order parameters for set node

PARAMETER node_order(node)     'order for members of set node' ;
node_order(node)  = ORD(node) ;

DISPLAY node_macro, node_order ;

* ------------------------------------------------------------------------------
* use externally (via GDX) supplied scenario parameters as default starting values for MACRO (these will be overwritten in the actual iteration process)
* ------------------------------------------------------------------------------

* useful energy/service demand levels from MESSAGE get mapped onto MACRO sector structure
enestart(node_macro,sector,year) = demand_MESSAGE(node_macro,sector,year) / 1000;
* useful energy/service demand prices from MESSAGE get mapped onto MACRO sector structure
eneprice(node_macro,sector,year) = price_MESSAGE(node_macro,sector,year) ;
* total energy system costs by node and time
total_cost(node_macro,year) = cost_MESSAGE(node_macro,year) ;

$LABEL macro_input_end

* base year useful energy/service demand levels from MESSAGE get mapped onto MACRO sector structure
demand_base(node_macro,sector) = sum(macro_base_period, enestart(node_macro,sector,macro_base_period) ) ;

DISPLAY enestart, eneprice, total_cost;

* ------------------------------------------------------------------------------
* calculate start values
* ------------------------------------------------------------------------------

PARAMETER growth_factor(node, year_all)  'cumulative growth factor' ;

growth_factor(node_macro, macro_base_period) = 1;

LOOP(year $ (NOT macro_base_period(year)),
    growth_factor(node_macro, year) = SUM(year2$( seq_period(year2,year) ), growth_factor(node_macro, year2) * (1 + grow(node_macro, year))**(duration_period(year))) ;
) ;

PARAMETER potential_gdp(node, year_all) ;

potential_gdp(node_macro, year) = sum(macro_base_period, historical_gdp(node_macro,macro_base_period)/1000) * growth_factor(node_macro, year) ;

DISPLAY growth_factor, potential_gdp ;

* ------------------------------------------------------------------------------
* assigning parameters and calculation of cumulative effect of AEEI over time
* ------------------------------------------------------------------------------

* calculation of cumulative effect of AEEI over time
aeei_factor(node_macro, sector, macro_initial_period) = 1;

LOOP(year_all $ ( ORD(year_all) > sum(year_all2$( macro_initial_period(year_all2) ), ORD(year_all2) ) ),
aeei_factor(node_macro, sector, year_all) = SUM(year_all2$( seq_period(year_all2,year_all) ), ( (1 - aeei(node_macro, sector, year_all)) ** duration_period(year_all) ) * aeei_factor(node_macro, sector, year_all2))
);

DISPLAY aeei_factor ;

* ------------------------------------------------------------------------------
* calculation of total labor supply, new labor supply and utility discount factor
* ------------------------------------------------------------------------------

* caluclate production function exponent between capital-labor and energy nest from elasticity of substitution
rho(node_macro) = (esub(node_macro) - 1)/esub(node_macro) ;
DISPLAY rho ;

udf(node_macro, macro_initial_period)   = 1 ;
labor(node_macro, macro_initial_period) = 1 ;

LOOP(year_all $( ORD(year_all) > sum(year_all2$( macro_initial_period(year_all2) ), ORD(year_all2) ) ),
* exogenous labor supply growth (including both changes in labor force and labor productivity growth)
   labor(node_macro, year_all)  = SUM(year_all2$( seq_period(year_all2,year_all) ), labor(node_macro, year_all2) * (1 + grow(node_macro, year_all))**duration_period(year_all)) ;
* new labor supply
   newlab(node_macro, year_all) = SUM(year_all2$( seq_period(year_all2,year_all) ), (labor(node_macro, year_all) - labor(node_macro, year_all2)*(1 - depr(node_macro))**duration_period(year_all))$((labor(node_macro, year_all) - labor(node_macro, year_all2)*(1 - depr(node_macro))**duration_period(year_all)) > 0)) + epsilon ;
* calculation of utility discount factor based on discount rate (drate)
   udf(node_macro, year_all)    = SUM(year_all2$( seq_period(year_all2,year_all) ), udf(node_macro, year_all2) * (1 - (drate(node_macro) - grow(node_macro, year_all)))**duration_period(year_all)) ;
);

DISPLAY labor, newlab, udf;

* ------------------------------------------------------------------------------
* Calculation of base year energy system costs, capital stock and GDP components (investment, consumption, production)
* ------------------------------------------------------------------------------

ecst0(node_macro) = sum(macro_base_period, total_cost(node_macro,macro_base_period)) ;

gdp_base(node_macro) = sum(macro_base_period, historical_gdp(node_macro,macro_base_period) / 1000) ;

k0(node_macro) = kgdp(node_macro) * gdp_base(node_macro) ;

* pseudo loop over base_period set which includes single element
LOOP(macro_base_period,
* VK, 08 April 2008: avoid negative starting values as this causes error in program execution
     i0(node_macro) = (k0(node_macro) * (grow(node_macro, macro_base_period) + depr(node_macro)))$(k0(node_macro) * (grow(node_macro, macro_base_period) + depr(node_macro)) > 0) + epsilon ;
);
c0(node_macro) = gdp_base(node_macro) - i0(node_macro) - ecst0(node_macro)/1000 ;
y0(node_macro) = gdp_base(node_macro) ;

DISPLAY ecst0, k0, i0, c0, y0 ;

* ------------------------------------------------------------------------------
* Introduced fix for running MACRO myopically when the finite time horizon correction
* of the utility function causes problems in case of labour productivity growth rates
* that are greater than drate = depr. To avoid negative values the absolute value is
* simply taken.
* ------------------------------------------------------------------------------

finite_time_corr(node_macro, year) = abs(drate(node_macro) - grow(node_macro, year)) ;
