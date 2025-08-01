
*----------------------------------------------------------------------------------------------------------------------*
* load sets and parameters from dataset gdx                                                                            *
*----------------------------------------------------------------------------------------------------------------------*

put_utility 'log' /"+++ Importing data from '%in%'... +++ " ;

* all sets and general parameters from the gdx file
$GDXIN '%in%'
$LOAD node, tec=technology, year_all=year, commodity, level, grade, mode, time, rating
$LOAD emission, land_scenario, land_type, relation
$LOAD level_resource, level_renewable
$LOAD lvl_spatial, lvl_temporal, map_spatial_hierarchy, map_temporal_hierarchy
$LOAD map_node, map_time, map_commodity, map_resource, map_stocks, map_tec, map_tec_time, map_tec_mode
$LOAD is_capacity_factor
$LOAD map_land, map_relation
$LOAD type_tec, cat_tec, type_year, cat_year, type_emission, cat_emission, type_tec_land
$LOAD inv_tec, renewable_tec
$LOAD balance_equality, time_relative
$LOAD shares
$LOAD addon, type_addon, cat_addon, map_tec_addon
$LOAD storage_tec, level_storage, map_tec_storage

* Version information; conditional load to allow older GDX files
$ifthen gdxSetType ixmp_version
$load ixmp_version
$endif

$GDXIN

Execute_load '%in%'
* general parameters
duration_period, duration_time, interestrate,
* resources parameters
resource_volume, resource_cost, is_bound_extraction_up, bound_extraction_up, resource_remaining,
* technology technical-engineering parameters and economic costs
input, output, construction_time, technical_lifetime
capacity_factor, operation_factor, min_utilization_factor, inv_cost, fix_cost, var_cost,
* upper and lower bounds on new capacity investment, total installed capacity and activity (including mapping sets)
is_bound_new_capacity_up, is_bound_new_capacity_lo, bound_new_capacity_up, bound_new_capacity_lo,
is_bound_total_capacity_up, is_bound_total_capacity_lo, bound_total_capacity_up, bound_total_capacity_lo,
is_bound_activity_up, bound_activity_up, bound_activity_lo,
* dynamic constraints on new capacity investment and activity of technologies
is_dynamic_new_capacity_up, initial_new_capacity_up, growth_new_capacity_up,
is_dynamic_new_capacity_lo, initial_new_capacity_lo, growth_new_capacity_lo,
is_dynamic_activity_up, initial_activity_up, growth_activity_up,
is_dynamic_activity_lo, initial_activity_lo, growth_activity_lo,
* parameters for soft relaxation of dynamic constraints
abs_cost_new_capacity_soft_up, abs_cost_new_capacity_soft_lo, level_cost_new_capacity_soft_up, level_cost_new_capacity_soft_lo,
abs_cost_activity_soft_up, abs_cost_activity_soft_lo, level_cost_activity_soft_up, level_cost_activity_soft_lo,
soft_new_capacity_up, soft_new_capacity_lo, soft_activity_up, soft_activity_lo,
* share constraints
map_shares_commodity_share,map_shares_commodity_total,share_commodity_up,share_commodity_lo
share_mode_up,share_mode_lo,
* addon technologies
addon_conversion, addon_up, addon_lo
* parameters for reliability, flexibility and renewable potential constraints
rating_bin, reliability_factor, peak_load_factor, flexibility_factor
renewable_capacity_factor, renewable_potential
* emission factors, bounds and taxes on emissions (including mapping sets)
historical_emission, emission_factor, emission_scaling, is_bound_emission, bound_emission, tax_emission,
* historical values of new capacity investment, activity and extraction
historical_new_capacity, historical_activity, historical_extraction
* parameters for land-use model emulator
historical_land, land_cost, land_input, land_output, land_use, land_emission,
is_dynamic_land_scen_up, initial_land_scen_up, growth_land_scen_up,
is_dynamic_land_scen_lo, initial_land_scen_lo, growth_land_scen_lo,
is_dynamic_land_up, initial_land_up, dynamic_land_up, growth_land_up,
is_dynamic_land_lo, initial_land_lo, dynamic_land_lo, growth_land_lo, growth_land_lo,
* parameters for generic relations (linear constraints)
is_relation_upper, is_relation_lower, relation_upper, relation_lower,
relation_cost, relation_total_capacity, relation_new_capacity, relation_activity,
* energy stocks
commodity_stock,
* demand parameters
demand_fixed=demand
* fixing variables to pre-specified values
is_fixed_extraction, is_fixed_stock, is_fixed_new_capacity, is_fixed_capacity, is_fixed_activity, is_fixed_land
fixed_extraction, fixed_stock, fixed_new_capacity, fixed_capacity, fixed_activity, fixed_land
* storage parameters
storage_initial, storage_self_discharge, time_order
;

emission_cumulative(emission) = no;
emission_cumulative('TCE_CO2') = yes;
emission_cumulative('LU_CO2') = yes;
emission_cumulative('TCE') = yes;
emission_annual(emission) = yes;
emission_annual(emission_cumulative) = no;

sets
land_scenario_bio
/ BIO00, BIO05, BIO07, BIO10, BIO15, BIO25, BIO45 /

land_scenario_ghg_zero(land_scenario)
/ BIO00GHG000, BIO05GHG000, BIO07GHG000, BIO10GHG000, BIO15GHG000, BIO25GHG000, BIO45GHG000 /

map_scenario_bio(land_scenario_bio,land_scenario) 
/   BIO00 . (BIO00GHG000,BIO00GHG010,BIO00GHG020,BIO00GHG050,BIO00GHG100,BIO00GHG200,BIO00GHG400,BIO00GHG600,BIO00GHG990,BIO00GHG2000,BIO00GHG3000,BIO00GHG4000)
    BIO05 . (BIO05GHG000,BIO05GHG010,BIO05GHG020,BIO05GHG050,BIO05GHG100,BIO05GHG200,BIO05GHG400,BIO05GHG600,BIO05GHG990,BIO05GHG2000,BIO05GHG3000,BIO05GHG4000)
    BIO07 . (BIO07GHG000,BIO07GHG010,BIO07GHG020,BIO07GHG050,BIO07GHG100,BIO07GHG200,BIO07GHG400,BIO07GHG600,BIO07GHG990,BIO07GHG2000,BIO07GHG3000,BIO07GHG4000)
    BIO10 . (BIO10GHG000,BIO10GHG010,BIO10GHG020,BIO10GHG050,BIO10GHG100,BIO10GHG200,BIO10GHG400,BIO10GHG600,BIO10GHG990,BIO10GHG2000,BIO10GHG3000,BIO10GHG4000)
    BIO15 . (BIO15GHG000,BIO15GHG010,BIO15GHG020,BIO15GHG050,BIO15GHG100,BIO15GHG200,BIO15GHG400,BIO15GHG600,BIO15GHG990,BIO15GHG2000,BIO15GHG3000,BIO15GHG4000)
    BIO25 . (BIO25GHG000,BIO25GHG010,BIO25GHG020,BIO25GHG050,BIO25GHG100,BIO25GHG200,BIO25GHG400,BIO25GHG600,BIO25GHG990,BIO25GHG2000,BIO25GHG3000,BIO25GHG4000)
    BIO45 . (BIO45GHG000,BIO45GHG010,BIO45GHG020,BIO45GHG050,BIO45GHG100,BIO45GHG200,BIO45GHG400,BIO45GHG600,BIO45GHG990,BIO45GHG2000,BIO45GHG3000,BIO45GHG4000)
/

map_bio_ghg_zero(land_scenario_bio,land_scenario) 
/ BIO00 . BIO00GHG000
  BIO05 . BIO05GHG000
  BIO07 . BIO07GHG000
  BIO10 . BIO10GHG000
  BIO15 . BIO15GHG000
  BIO25 . BIO25GHG000
  BIO45 . BIO45GHG000
/

map_scenario_zero(land_scenario_ghg_zero,land_scenario) 
/   BIO00GHG000 . (BIO00GHG000,BIO00GHG010,BIO00GHG020,BIO00GHG050,BIO00GHG100,BIO00GHG200,BIO00GHG400,BIO00GHG600,BIO00GHG990,BIO00GHG2000,BIO00GHG3000,BIO00GHG4000)
    BIO05GHG000 . (BIO05GHG000,BIO05GHG010,BIO05GHG020,BIO05GHG050,BIO05GHG100,BIO05GHG200,BIO05GHG400,BIO05GHG600,BIO05GHG990,BIO05GHG2000,BIO05GHG3000,BIO05GHG4000)
    BIO07GHG000 . (BIO07GHG000,BIO07GHG010,BIO07GHG020,BIO07GHG050,BIO07GHG100,BIO07GHG200,BIO07GHG400,BIO07GHG600,BIO07GHG990,BIO07GHG2000,BIO07GHG3000,BIO07GHG4000)
    BIO10GHG000 . (BIO10GHG000,BIO10GHG010,BIO10GHG020,BIO10GHG050,BIO10GHG100,BIO10GHG200,BIO10GHG400,BIO10GHG600,BIO10GHG990,BIO10GHG2000,BIO10GHG3000,BIO10GHG4000)
    BIO15GHG000 . (BIO15GHG000,BIO15GHG010,BIO15GHG020,BIO15GHG050,BIO15GHG100,BIO15GHG200,BIO15GHG400,BIO15GHG600,BIO15GHG990,BIO15GHG2000,BIO15GHG3000,BIO15GHG4000)
    BIO25GHG000 . (BIO25GHG000,BIO25GHG010,BIO25GHG020,BIO25GHG050,BIO25GHG100,BIO25GHG200,BIO25GHG400,BIO25GHG600,BIO25GHG990,BIO25GHG2000,BIO25GHG3000,BIO25GHG4000)
    BIO45GHG000 . (BIO45GHG000,BIO45GHG010,BIO45GHG020,BIO45GHG050,BIO45GHG100,BIO45GHG200,BIO45GHG400,BIO45GHG600,BIO45GHG990,BIO45GHG2000,BIO45GHG3000,BIO45GHG4000)
/


;



*----------------------------------------------------------------------------------------------------------------------*
* ensure that each node is mapped to itself                                                                            *
*----------------------------------------------------------------------------------------------------------------------*

map_node(node,node) = yes ;

*----------------------------------------------------------------------------------------------------------------------*
* auxiliary mappings for the implementation of bounds over all modes and system reliability/flexibility constraints    *
*----------------------------------------------------------------------------------------------------------------------*

Set all_modes (mode) ;
all_modes('all') = yes ;

Set rating_unfirm(rating) ;
rating_unfirm(rating) = yes ;
rating_unfirm('firm') = no ;

Set rating_unrated(rating) ;
rating_unrated(rating) = yes ;
rating_unrated('unrated') = no ;

*----------------------------------------------------------------------------------------------------------------------*
* auxiliary mappings for split between cumulative and annualland-use emission calculations                             *
*----------------------------------------------------------------------------------------------------------------------*

* remove all emission types from subset for cumulative land-use emission accounting
emission_cumulative(emission) = no;
* add emission types where land-use emissions should use the cumulative accounting approach
* TO DO: to avoid having to declarde these emissions in gams code, this section should be translated into a Python process
emission_cumulative('TCE_CO2') = yes;
emission_cumulative('LU_CO2') = yes;
emission_cumulative('TCE') = yes;
* add all emission types to subset for annual land-use emission accounting,
* then remove the emission types that have been declared in the cumulative accounting set
emission_annual(emission) = yes;
emission_annual(emission_cumulative) = no;

*----------------------------------------------------------------------------------------------------------------------*
* assignment and computation of MESSAGE-specific auxiliary parameters                                                  *
*----------------------------------------------------------------------------------------------------------------------*

* get assignment of auxiliary parameter for period mappings and duration
$INCLUDE includes/period_parameter_assignment.gms

* compute auxiliary parameters for relative duration of subannual time periods
duration_time_rel(time,time2)$( map_time(time,time2) ) = duration_time(time2) / duration_time(time) ;
* making duration_time_rel equal to 1, i.e., a consistent unit for ACT in sub-annual time slices, for parent 'time' not specified in set 'time_relative'
duration_time_rel(time,time2)$( Not time_relative(time) ) = 1 ;

* assign an additional mapping set for technologies to nodes, modes and subannual time slices (for shorter reference)
map_tec_act(node,tec,year_all,mode,time)$( map_tec_time(node,tec,year_all,time) AND
   map_tec_mode(node,tec,year_all,mode) ) = yes ;

* mapping of technology lifetime to all 'current' periods (for all non-investment technologies)
map_tec_lifetime(node,tec,year_all,year_all)$( map_tec(node,tec,year_all) ) = yes ;

* mapping of technology lifetime to all periods 'year_all' which are within the economic lifetime
* (if built in period 'vintage')
map_tec_lifetime(node,tec,vintage,year_all)$( map_tec(node,tec,vintage) AND map_tec(node,tec,year_all)
    AND map_period(vintage,year_all)
    AND duration_period_sum(vintage,year_all) < technical_lifetime(node,tec,vintage) ) = yes ;

* mapping of technology lifetime to all periods 'year_all' which were built prior to the beginning of the model horizon
map_tec_lifetime(node,tec,historical,year_all)$(
    map_tec(node,tec,year_all)
    AND map_period(historical,year_all)
    AND historical_new_capacity(node,tec,historical)
    AND duration_period_sum(historical,year_all) < technical_lifetime(node,tec,historical)
) = yes ;

* mapping of renewable technologies to their input commodities
map_ren_com(node,renewable_tec,commodity,year_all)$(
    SUM((node2,year_all2,mode,level_renewable,time_act,time),
        input(node2,renewable_tec,year_all,year_all2,mode,node,commodity,level_renewable,time_act,time) ) ) = yes;

* mapping of renewable commodities to grades
map_ren_grade(node,commodity,grade,year_all)$(
    SUM(level_renewable, renewable_potential(node,commodity,grade,level_renewable,year_all) ) ) = yes;

* mapping of technologies to commodities and ratings
map_rating(node,inv_tec,commodity,level,rating,year_all)$(
    SUM(time, reliability_factor(node,inv_tec,year_all,commodity,level,time,rating) ) ) = yes;

* assign the yearly average capacity factor (used in equation OPERATION_CONSTRAINT)
capacity_factor(node,tec,year_all2,year_all,'year') =
    sum(time$map_tec_time(node,tec,year_all,time), duration_time(time)
        * capacity_factor(node,tec,year_all2,year_all,time) );

* update the masking set for capacity factor based on the average values added above
is_capacity_factor(node,tec,year_all2,year_all,time)$(capacity_factor(node,tec,year_all2,year_all,'year') ) = yes;

* set the default capacity factor for technologies where no parameter value is provided in the input data
capacity_factor(node,tec,year_all2,year_all,time)$( map_tec_time(node,tec,year_all,time)
    AND map_tec_lifetime(node,tec,year_all2,year_all) AND NOT is_capacity_factor(node,tec,year_all2,year_all,time) ) = 1 ;

* set the default operation factor for technologies where no parameter value is provided in the input data
operation_factor(node,tec,year_all2,year_all)$( map_tec(node,tec,year_all)
    AND map_tec_lifetime(node,tec,year_all2,year_all) AND NOT operation_factor(node,tec,year_all2,year_all) ) = 1 ;

* set the upper bound on addon-technology activity to 1 by default
addon_up(node,tec,year_all,mode,time,type_addon)$(
    map_tec_addon(tec,type_addon)
    AND map_tec_act(node,tec,year_all,mode,time)
    AND NOT addon_up(node,tec,year_all,mode,time,type_addon) ) = 1 ;

* set the emission scaling parameter to 1 by default
emission_scaling(type_emission,emission)$( cat_emission(type_emission,emission)
        and not emission_scaling(type_emission,emission) ) = 1 ;

* mapping of storage technologies to their level and commodity (can be different from level and commodity of storage media)
map_time_commodity_storage(node,tec,level,commodity,mode,year_all,time)$( storage_tec(tec) AND
    SUM( (node2,year_all2,time_act), input(node2,tec,year_all,year_all2,mode,node,commodity,level,time_act,time) ) ) = yes;

* mapping of sequence of sub-annual time slices in a period and temporal level
map_time_period(year_all,lvl_temporal,time,time2)$( time_order(lvl_temporal,time) AND
     time_order(lvl_temporal,time) + 1 = time_order(lvl_temporal,time2) ) = yes;

* mapping of sequence of the last sub-annual time slice to the first to create a close the order of time slices
map_time_period(year_all,lvl_temporal,time,time2)$( time_order(lvl_temporal,time) AND
     time_order(lvl_temporal,time) = SMAX(time3,time_order(lvl_temporal,time3) ) AND time_order(lvl_temporal,time2) = 1 ) = yes;
*----------------------------------------------------------------------------------------------------------------------*
* sanity checks on the data set                                                                                        *
*----------------------------------------------------------------------------------------------------------------------*

Parameter check ;

* check whether all relevant technology/vintage/year combinations have positove input/output values assigned
*loop((node,tec,vintage,year_all)$( map_tec_lifetime(node,tec,vintage,year_all) ),
*    if ( sum( (mode,node2,commodity,level,time,time2),
*            input(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2)
*            + output(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2) ) eq 0 ,
*        put_utility 'log'/" Warning: No input or output not defined for '"node.tl:0"|"tec.tl:0"|"vintage.tl:0"|"year_all.tl:0"' !" ;
*    ) ;
*) ;

* check that the economic and technical lifetime are defined and consistent for all investment technologies
loop((node,inv_tec,model_horizon)$( map_tec(node,inv_tec,model_horizon) ),
    if ( technical_lifetime(node,inv_tec,model_horizon) <= 0 ,
        put_utility 'log'/" Error: Technical lifetime not defined for '"node.tl:0"|"inv_tec.tl:0"|"model_horizon.tl:0"' !" ;
        check = 1 ;
    ) ;
) ;
if (check,
    abort "There is a problem with the definition of the technical lifetime!" ;
) ;

* check for validity of temporal resolution with an accepted difference in the scale of 1e-12, due to the different percision between GAMS and python values.
loop(lvl_temporal,
    loop(time2$( sum(time, map_temporal_hierarchy(lvl_temporal,time,time2) ) ),
        check = 1$( abs( sum( time$( map_temporal_hierarchy(lvl_temporal,time,time2) ),
            duration_time(time) ) - duration_time(time2) ) > 1e-12 );
    ) ;
) ;
if (check,
    abort "There is a problem in the definition of the temporal resolution!" ;
);

* check that the resources-remaining parameter is in the interval (0,1]
loop( (node,commodity,grade,year_all)$( map_resource(node,commodity,grade,year_all)
        AND resource_remaining(node,commodity,grade,year_all) ),
    if( ( resource_remaining(node,commodity,grade,year_all) > 1
            or resource_remaining(node,commodity,grade,year_all) <= 0 ),
        put_utility 'log'/" Error: Inconsistent value of parameter 'resources_remaining' "
            "for '"node.tl:0"|"commodity.tl:0"|"grade.tl:0"|"year_all.tl:0 "' !" ;
        check = 1 ;
    ) ;
) ;
if (check,
    abort "There is a problem with the parameter 'resources_remaining'!" ;
) ;

* check that the sum of rating bins (if used for firm-cacpacity or flexibility) is greater than 1
loop( (node,tec,year_all,commodity,level,time)$(
    ( sum((vintage,rating_unfirm), reliability_factor(node,tec,year_all,commodity,level,time,rating_unfirm) )
    OR sum((vintage,mode,rating_unrated)$(
        flexibility_factor(node,tec,vintage,year_all,mode,commodity,level,time,rating_unrated) ), 1 ) )
    ),
    if ( ( sum( rating, rating_bin(node,tec,year_all,commodity,level,time,rating) ) < 1 ),
        put_utility 'log'/" Error: Insufficient rating bin assignment ' "
            "for '"node.tl:0"|"tec.tl:0"|"year_all.tl:0 "'" ;
        check = 1 ;
    ) ;
) ;
if (check,
    abort "There is a problem with assignment of rating bins!" ;
) ;
