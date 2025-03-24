*----------------------------------------------------------------------------------------------------------------------*
* assignment and computation of auxiliary parameters                                                                   *
*----------------------------------------------------------------------------------------------------------------------*

* additional sets and parameters created in GAMS to make notation more concise for myopic/rolling-horizon optimization
Sets
    historical(year_all)             set of periods prior to the start of the model horizon
    model_horizon(year_all)          set of periods included in the model horizon
    macro_horizon(year_all)          set of periods included in the MACRO model horizon
    seq_period(year_all,year_all2)    mapping of one period ('year_all') to the next ('year_all2')
    map_period(year_all,year_all2)    mapping of one period ('year_all') to itself and all subsequent periods ('year_all2')
    map_first_period(type_year, year_all) mapping of a 'type_year' to the first 'year'
    first_period(year_all)           flag for first period in model horizon
    last_period(year_all)            flag for last period in model horizon
    macro_initial_period(year_all)   flag for period in model horizon in which to initialize model parameters in (period prior to first model period) - used in MACRO
    macro_base_period(year_all)      flag for base year period in model horizon (period prior to first model period) - used in MACRO
;

Parameter
    duration_period_sum(year_all,year_all2) number of years between two periods ('year_all' must precede 'year_all2')
    duration_time_rel(time,time2)         relative duration of subannual time slice 'time2' relative to parent 'time' (only for 'time' specified in set 'time_relative')
    elapsed_years(year_all)    elapsed years since the start of the model horizon (not including 'year_all' period)
    remaining_years(year_all)  remaining years until the end of the model horizon (including last period)
    year_order(year_all)       order for members of set 'year_all'
;
*----------------------------------------------------------------------------------------------------------------------*
* assignment auxiliary dynamic sets                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

** treatment of periods **

* sanity checks to ensure that not more than one period is assigned to the first- and lastyear categories
if ( sum(year_all$( cat_year("firstmodelyear",year_all) ), 1 ) > 1 ,
    abort "There is more than one period assigned as category 'firstmodelyear'!" ) ;
if ( sum(year_all$( cat_year("lastmodelyear",year_all) ), 1 ) > 1 ,
    abort "There is more than one period assigned as category 'lastmodelyear'!" ) ;
if ( sum(year_all$( cat_year("initializeyear_macro",year_all) ), 1 ) > 1 ,
    abort "There is more than one period assigned as category 'initializeyear_macro'!" ) ;

* mapping of sequence of periods over the model horizon
seq_period(year_all,year_all2)$( ORD(year_all) + 1 = ORD(year_all2) ) = yes ;
map_period(year_all,year_all2)$( ORD(year_all) <= ORD(year_all2) ) = yes ;

* dynamic sets (singleton) with first and last periods in model horizon of MESSAGEix (for easier reference)
if ( sum(year_all$( cat_year("firstmodelyear",year_all) ), 1 ),
    first_period(year_all)$( cat_year("firstmodelyear",year_all) ) = yes ;
else
    first_period(year_all)$( ORD(year_all) eq 1 ) = yes ;
) ;
if ( sum(year_all$( cat_year("lastmodelyear",year_all) ), 1 ),
    last_period(year_all)$( cat_year("lastmodelyear",year_all) ) = yes;
else
    last_period(year_all)$( ORD(year_all) = CARD(year_all) ) = yes ;
) ;

* dynamic sets for MACRO initialization and base periods
macro_initial_period(year_all) = no ;
macro_initial_period(year_all)$( cat_year("initializeyear_macro",year_all) ) = yes ;
macro_base_period(year_all) = no ;
macro_base_period(year_all)$( ORD(year_all) = sum(year_all2$( first_period(year_all2) ), ORD(year_all2) - 1 ) )  = yes ;

* assign set of historical years, the model horizon and the MACRO hoizon (includes 'macro_base_period')
historical(year_all)$( ORD(year_all) < sum(year_all2$cat_year("firstmodelyear",year_all2), ORD(year_all2) ) ) = yes ;
model_horizon(year_all) = no ;
model_horizon(year_all)$( ORD(year_all) >= sum(year_all2$first_period(year_all2), ORD(year_all2) )
    AND ORD(year_all) <= sum(year_all2$last_period(year_all2), ORD(year_all2) ) ) = yes ;
macro_horizon(year_all) = no ;
macro_horizon(year_all)$macro_base_period(year_all) = yes;
macro_horizon(year_all)$model_horizon(year_all) = yes;

*----------------------------------------------------------------------------------------------------------------------*
* assignment of (cumulative) discount factors over time                                                                *
*----------------------------------------------------------------------------------------------------------------------*

* simple method to compute discount factor (but this approach implicitly assumes a constant interest rate)
*df_year(year_all) = POWER( 1 / ( 1+interestrate(year_all) ), sum(year_all2$( ORD(year_all2) < ORD(year_all) ),
*    duration_period(year_all2) ) ) ;

* compute per-year discount factor (using a recursive method) - set to 1 by default (interest rate = 0)
df_year(year_all) = 1 ;

* recursively compute the per-year discount factor
loop(year_all$( ORD(year_all) > 1 ),
    df_year(year_all) =
        sum(year_all2$( seq_period(year_all2,year_all) ), df_year(year_all2)
            * POWER( 1 / ( 1 + interestrate(year_all) ), duration_period(year_all) ) ) ;
) ;

* multiply per-year discount factor by discounted period duration
df_period(year_all) =
    df_year(year_all) * (
* multiply the per-year discount factor by the geometric series of over the duration of the period
        ( ( POWER( 1 + interestrate(year_all) , duration_period(year_all) ) - 1 )
        / interestrate(year_all) )$( interestrate(year_all) )
* if interest rate = 0, multiply by the number of years in that period
        + ( duration_period(year_all) )$( interestrate(year_all) eq 0 ) )
;

*----------------------------------------------------------------------------------------------------------------------*
* assignment of auxiliary first-period-per-category mapping and parameters for duration of periods                     *
*----------------------------------------------------------------------------------------------------------------------*

* define order of set 'year_all' (to use as equivalent of ORD operator on the dynamic set year (subset of 'year_all') )
year_order(year_all) = ORD(year_all) ;

* assign the first year of each category to a specific mapping set for use in computing emissions prices
map_first_period(type_year,year_all)$( cat_year(type_year,year_all)
    AND year_order(year_all) = SMIN(year_all2$( cat_year(type_year,year_all2) ), year_order(year_all2) ) ) = yes ;

* auxiliary parameters for duration between periods (years) - not including the final period 'year_all2'
duration_period_sum(year_all,year_all2) =
    SUM(year_all3$( ORD(year_all) <= ORD(year_all3) AND ORD(year_all3) < ORD(year_all2) ) , duration_period(year_all3) ) ;

* auxiliary parameter for duration since the first year of the model horizon - not including the period 'year_all'
elapsed_years(year_all) = sum(first_period, duration_period_sum(first_period,year_all) ) ;

* auxiliary parameter for duration until the end of the model horizon - including the last period
remaining_years(year_all) = SUM(year_all2$( ORD(year_all) <= ORD(year_all2) ) , duration_period(year_all2) ) ;
