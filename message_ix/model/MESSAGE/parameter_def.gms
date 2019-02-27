***
* .. _parameter_def:
*
* Parameter definition
* ====================
*
* This file contains the definition of all parameters used in |MESSAGEix|.
*
* In |MESSAGEix|, all parameters are understood as yearly values, not as per (multi-year) period.
* This provides flexibility when changing the resolution of the model horizon (i.e., the set ``year``).
*
* Parameters written in *italics* are auxiliary parameters
* that are either generated automatically when exporting a ``message_ix.Scenario`` to gdx
* or that are computed during the pre-processing stage in GAMS.
***

***
* General parameters of the |MESSAGEix| implementation
* ----------------------------------------------------
*
* .. list-table::
*    :widths: 25 20 55
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*      - Explanatory comments
*    * - *duration_period* (:math:`|y|`) [#short_dur]_
*      - ``year``
*      - duration of multi-year period (in number of years) [#year_auto]_
*    * - duration_time
*      - ``time``
*      - duration of sub-annual time slices (relative to 1) [#duration_time_year]_
*    * - *duration_time_rel*
*      - ``time`` | ``time``
*      - relative duration between sub-annual time slices [#df_auto]_
*    * - interestrate
*      - ``year``
*      - economy-wide interest rate or social discount rate
*    * - *discountfactor*
*      - ``year``
*      -  cumulative discount factor over period duration [#df_auto]_
*
* .. [#short_dur] The short-hand notation :math:`|y|` is used for the parameters :math:`duration\_period_y`
*    in the mathematical model documentation for exponents.
*
* .. [#year_auto] The values for this parameter are computed automatically when exporting a ``MESSAGE``-scheme
*    ``ixmp``.Scenario to gdx.
*    Note that in |MESSAGEix|, the elements of the ``year`` set are understood to be the last year in a period,
*    see :ref:`this footnote <period_year_footnote>`.
*
* .. [#duration_time_year] The element 'year' in the set of subannual time slices ``time`` has the value of 1.
*    This value is assigned by default when creating a new ``ixmp``.Scenario based on the ``MESSAGE`` scheme.
*
* .. [#df_auto] This parameter is computed during the GAMS execution.
***

Parameters
* general parameters
    duration_period(year_all)      duration of one multi-year period (in years)
    duration_time(time)            duration of one time slice (relative to 1)
    duration_period_sum(year_all,year_all2)  number of years between two periods ('year_all' must precede 'year_all2')
    duration_time_rel(time,time2)  relative duration of subannual time period ('time2' relative to parent 'time')
    interestrate(year_all)         interest rate (to compute discount factor)
    discountfactor(*)              cumulative discount facor
;

***
* Parameters of the `Resources` section
* -------------------------------------
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - resource_volume
*      - ``node`` | ``commodity`` | ``grade``
*    * - resource_cost
*      - ``node`` | ``commodity`` | ``grade`` | ``year``
*    * - resource_remaining
*      - ``node`` | ``commodity`` | ``grade`` | ``year``
*    * - bound_extraction_up
*      - ``node`` | ``commodity`` | ``level`` | ``year``
*    * - commodity_stock [#stock]_
*      - ``node`` | ``commodity`` | ``level`` | ``year``
*    * - historical_extraction [#hist]_
*      - ``node`` | ``commodity`` | ``grade`` | ``year``
*
* .. [#stock] This parameter allows (exogenous) additions to the commodity stock over the model horizon,
*    e.g., precipitation that replenishes the water table.
*
* .. [#hist] Historical values of new capacity and activity can be used for parametrising the vintage structure
*    of existing capacity and implement dynamic constraints in the first model period.
*
***

Parameter
* resource and commodity parameters
    resource_volume(node,commodity,grade)               volume of resources in-situ at start of the model horizon
    resource_cost(node,commodity,grade,year_all)        extraction costs for resource
    resource_remaining(node,commodity,grade,year_all)   maximum extraction relative to remaining resources (by year)
    bound_extraction_up(node,commodity,grade,year_all)  upper bound on extraction of resources by grade
    commodity_stock(node,commodity,level,year_all)      exogenous (initial) quantity of commodity in stock
    historical_extraction(node,commodity,grade,year_all) historical extraction
;

***
* Parameters of the `Demand` section
* ----------------------------------
*
* .. list-table::
*    :widths: 30 70
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - demand [demand_fixed] [#demand]_
*      - ``node`` | ``commodity`` | ``level`` | ``year`` | ``time``
*    * - peak_load_factor [#peakload]_
*      - ``node`` | ``commodity`` | ``year``
*
* .. [#demand] The parameter ``demand`` in a ``MESSAGE``-scheme ``ixmp``.Scenario is translated
*    to the parameter ``demand_fixed`` in the MESSAGE implementation in GAMS. The variable ``DEMAND`` is introduced
*    as an auxiliary reporting variable; it equals ``demand_fixed`` in a `MESSAGE`-standalone run and reports
*    the final demand including the price response in an iterative `MESSAGE-MACRO` solution.
*
* .. [#peakload] The parameters ``peak_load_factor`` and ``reliability_factor`` are based on the formulation proposed
*    by Sullivan et al., 2013 :cite:`sullivan_VRE_2013`. It is used in :ref:`reliability_constraint`.
*
***

Parameter
    demand_fixed(node,commodity,level,year_all,time)     exogenous demand levels
    peak_load_factor(node,commodity,level,year_all,time) maximum peak load factor for reliability constraint of firm capacity
;

***
* Parameters of the `Technology` section
* --------------------------------------
*
* Input/output mapping, costs and engineering specifications
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - input [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` |
*        ``node_origin`` | ``commodity`` | ``level`` | ``time`` | ``time_origin``
*    * - output [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` |
*        ``node_dest`` | ``commodity`` | ``level`` | ``time`` | ``time_dest``
*    * - inv_cost [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - fix_cost [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act``
*    * - var_cost [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``time``
*    * - levelized_cost [#levelizedcost]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``time``
*    * - construction_time
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - technical_lifetime
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - capacity_factor [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``time``
*    * - operation_factor [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act``
*    * - min_utilization_factor [#tecvintage]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act``
*    * - rating_bin [#rating]_
*      - ``node`` | ``technology`` | ``year_act`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - reliability_factor [#peakload]_
*      - ``node`` | ``technology`` | ``year_act`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - flexibility_factor
*      - ``node_loc`` | ``technology`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - renewable_capacity_factor
*      - ``node_loc`` | ``commodity`` | ``grade`` | ``level`` | ``year``
*    * - renewable_potential
*      - ``node`` | ``commodity`` | ``grade`` | ``level`` | ``year``
*    * - emission_factor
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``emission``
*
* .. [#tecvintage] Fixed and variable cost parameters and technical specifications are indexed over both
*    the year of construction (vintage) and the year of operation (actual).
*    This allows to represent changing technology characteristics depending on the age of the plant.
*
* .. [#levelizedcost] The parameter ``levelized_cost`` is computed in the GAMS pre-processing under the assumption of
*    full capacity utilization until the end of the technical lifetime.
*
* .. [#construction] The construction time only has an effect on the investment costs; in |MESSAGEix|,
*    each unit of new-built capacity is available instantaneously at the beginning of the model period.
*
* .. [#rating] The upper bound of a contribution by any technology to the constraints on system reliability
*    (:ref:`reliability_constraint`) and flexibility (:ref:`flexibility_constraint`) can depend on the share
*    of the technology output in the total commodity use at a specific level.
***

Parameters
* technology input-output mapping and costs parameters
    input(node,tec,vintage,year_all,mode,node,commodity,level,time,time)  relative share of input per unit of activity
    output(node,tec,vintage,year_all,mode,node,commodity,level,time,time) relative share of output per unit of activity
    inv_cost(node,tec,year_all)                         investment costs (per unit of new capacity)
    fix_cost(node,tec,vintage,year_all)                 fixed costs per year (per unit of capacity maintained)
    var_cost(node,tec,vintage,year_all,mode,time)       variable costs of operation (per unit of capacity maintained)
    levelized_cost(node,tec,year_all,time)              levelized costs (per unit of new capacity)

* engineering parameters
    construction_time(node,tec,vintage)                     duration of construction of new capacity (in years)
    technical_lifetime(node,tec,vintage)                    maximum technical lifetime (from year of construction)
    capacity_factor(node,tec,vintage,year_all,time)         capacity factor by subannual time slice
    operation_factor(node,tec,vintage,year_all)             yearly total operation factor
    min_utilization_factor(node,tec,vintage,year_all)       yearly minimum utilization factor
    emission_factor(node,tec,year_all,year_all,mode,emission) emission intensity of activity
    rating_bin(node,tec,year_all,commodity,level,time,rating) maximum share of technology in commodity use per rating
    reliability_factor(node,tec,year_all,commodity,level,time,rating) reliability of a technology (per rating)
    flexibility_factor(node,tec,vintage,year_all,mode,commodity,level,time,rating) contribution of technologies towards operation flexibility constraint
    renewable_capacity_factor(node,commodity,grade,level,year_all) quality of renewable potential grade (>= 1)
    renewable_potential(node,commodity,grade,level,year_all) size of renewable potential per grade
;

***
* Bounds on capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The following parameters specify upper and lower bounds on new capacity, total installed capacity, and activity.
*
* .. list-table::
*    :widths: 20 80
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - bound_new_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - bound_new_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - bound_total_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_act``
*    * - bound_total_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_act``
*    * - bound_activity_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``mode`` | ``time``
*    * - bound_activity_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``mode`` | ``time``
*
* The bounds on activity are implemented as the aggregate over all vintages in a specific period
* (cf. Equation ``ACTIVITY_BOUND_UP`` and ``ACTIVITY_BOUND_LO``).
***

Parameters
    bound_new_capacity_up(node,tec,year_all)         upper bound on new capacity
    bound_new_capacity_lo(node,tec,year_all)         lower bound on new capacity
    bound_total_capacity_up(node,tec,year_all)       upper bound on total installed capacity
    bound_total_capacity_lo(node,tec,year_all)       lower bound on total installed capacity
    bound_activity_up(node,tec,year_all,mode,time)   upper bound on activity (aggregated over all vintages)
    bound_activity_lo(node,tec,year_all,mode,time)   lower bound on activity
;

***
* Dynamic constraints on capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The following parameters specify constraints on the growth of new capacity and activity, i.e., market penetration.
*
* .. list-table::
*    :widths: 30 70
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - initial_new_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - growth_new_capacity_up [#mpx]_
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - soft_new_capacity_up [#mpx]_
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - initial_new_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - growth_new_capacity_lo [#mpx]_
*      - ``node_loc`` | ``tec_actual`` | ``year_vtg``
*    * - soft_new_capacity_lo [#mpx]_
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - initial_activity_up [#mpa]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - growth_activity_up [#mpx]_ [#mpa]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - soft_activity_up [#mpx]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - initial_activity_lo [#mpa]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - growth_activity_lo [#mpx]_ [#mpa]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - soft_activity_lo [#mpx]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*
* .. [#mpx] All parameters related to the dynamic constraints are understood as the bound on the rate
*    of growth/decrease, not as in percentage points and not as (1+growth rate).
*
* .. [#mpa] The dynamic constraints are not indexed over modes in the |MESSAGEix| implementation.
*
***

Parameters
    initial_new_capacity_up(node,tec,year_all)     dynamic upper bound on new capacity (fixed initial term)
    growth_new_capacity_up(node,tec,year_all)      dynamic upper bound on new capacity (growth rate)
    soft_new_capacity_up(node,tec,year_all)        soft relaxation of dynamic upper bound on new capacity (growth rate)

    initial_new_capacity_lo(node,tec,year_all)     dynamic lower bound on new capacity (fixed initial term)
    growth_new_capacity_lo(node,tec,year_all)      dynamic lower bound on new capacity (growth rate)
    soft_new_capacity_lo(node,tec,year_all)        soft relaxation of dynamic lower bound on new capacity (growth rate)

    initial_activity_up(node,tec,year_all,time)    dynamic upper bound on activity (fixed initial term)
    growth_activity_up(node,tec,year_all,time)     dynamic upper bound on activity (growth rate)
    soft_activity_up(node,tec,year_all,time)       soft relaxation of dynamic upper bound on activity (growth rate)

    initial_activity_lo(node,tec,year_all,time)    dynamic lower bound on activity (fixed initial term)
    growth_activity_lo(node,tec,year_all,time)     dynamic lower bound on activity (growth rate)
    soft_activity_lo(node,tec,year_all,time)       soft relaxation of dynamic lower bound on activity (growth rate)
;

*----------------------------------------------------------------------------------------------------------------------*
* Add-on technology parameters                                                                                         *
*----------------------------------------------------------------------------------------------------------------------*

***
* Parameters for the add-on technologies
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The implementation of |MESSAGEix| includes the functionality to introduce "add-on technologies" that are specifically
* linked to parent technologies. This feature can be used to model mitigation options (scrubber, cooling).
* Note, that no default addon_conversion is set, to avoid default conversion factors of 1 being set for technologies
* with mutiple modes, of which only a single mode should be linked to the add-on technology.
*
* .. list-table::
*    :widths: 20 80
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - addon_conversion
*      - ``node`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``time`` | ``type_addon``
*    * - addon_up
*      - ``node`` | ``tec`` | ``vintage`` | ``year`` | ``mode`` | ``time`` | ``type_addon``
*    * - addon_lo
*      - ``node`` | ``tec`` | ``vintage`` | ``year`` | ``mode`` | ``time`` | ``type_addon``
*
* The upper bound of
***

Parameters
    addon_conversion(node,tec,vintage,year_all,mode,time,type_addon) conversion factor between add-on and parent technology activity
    addon_up(node,tec,year_all,mode,time,type_addon)    upper bound of add-on technologies relative to parent technology
    addon_lo(node,tec,year_all,mode,time,type_addon)    lower bound of add-on technologies relative to parent technology
;

*----------------------------------------------------------------------------------------------------------------------*
* Soft relaxations of dynamic constraints                                                                              *
*----------------------------------------------------------------------------------------------------------------------*

***
* Cost parameters for 'soft' relaxations of dynamic constraints
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The implementation of |MESSAGEix| includes the functionality for 'soft' relaxations of dynamic constraints on
* new-built capacity and activity (see Keppo and Strubegger, 2010 :cite:`keppo_short_2010`).
* Refer to the section :ref:`dynamic_constraints`.
*
* .. list-table::
*    :widths: 20 80
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - abs_cost_new_capacity_soft_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - abs_cost_new_capacity_soft_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - level_cost_new_capacity_soft_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - level_cost_new_capacity_soft_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - abs_cost_activity_soft_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - abs_cost_activity_soft_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - level_cost_activity_soft_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - level_cost_activity_soft_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*
***

Parameters
    abs_cost_new_capacity_soft_up(node,tec,year_all) absolute cost of dynamic new capacity constraint relaxation (upwards)
    abs_cost_new_capacity_soft_lo(node,tec,year_all) absolute cost of dynamic new capacity constraint relaxation (downwards)
    level_cost_new_capacity_soft_up(node,tec,year_all) levelized cost multiplier of dynamic new capacity constraint relaxation (upwards)
    level_cost_new_capacity_soft_lo(node,tec,year_all) levelized cost multiplier of dynamic new capacity constraint relaxation (downwards)

    abs_cost_activity_soft_up(node,tec,year_all,time)  absolute cost of dynamic activity constraint relaxation (upwards)
    abs_cost_activity_soft_lo(node,tec,year_all,time)  absolute cost of dynamic activity constraint relaxation (downwards)
    level_cost_activity_soft_up(node,tec,year_all,time) levelized cost multiplier of dynamic activity constraint relaxation (upwards)
    level_cost_activity_soft_lo(node,tec,year_all,time) levelized cost multiplier of dynamic activity constraint relaxation (downwards)
;

***
* Historical capacity and activity values
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Historical data on new capacity and activity levels are included in |MESSAGEix| for
* correct accounting of the vintage portfolio and a seamless implementation of dynamic constraints from
* historical years to model periods.
*
* .. list-table::
*    :widths: 35 65
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - historical_new_capacity [#hist]_
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - historical_activity [#hist]_
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``mode`` | ``time``
*
***

Parameters
    historical_new_capacity(node,tec,year_all)           historical new capacity
    historical_activity(node,tec,year_all,mode,time)     historical acitivity
;

***
* Auxiliary investment cost parameters and multipliers
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Documentation not yet included.
***

Parameters
    construction_time_factor(node,tec,year_all) scaling factor to account for construction time of new capacity
    remaining_capacity(node,tec,year_all,year_all) scaling factor to account for remaining capacity in period
    end_of_horizon_factor(node,tec,year_all)    multiplier for value of investment at end of model horizon
    beyond_horizon_lifetime(node,tec,year_all)  remaining technical lifetime at the end of model horizon
    beyond_horizon_factor(node,tec,year_all)    discount factor of remaining lifetime beyond model horizon
;

*----------------------------------------------------------------------------------------------------------------------*
* Emissions                                                                                                            *
*----------------------------------------------------------------------------------------------------------------------*

***
* Parameters of the `Emission` section
* ------------------------------------
*
* The implementation of |MESSAGEix| includes a flexible and versatile accounting of emissions across different
* categories and species, with the option to define upper bounds and taxes on various (aggregates of) emissions
* and pollutants), (sets of) technologies, and (sets of) years.
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - historical_emission [#hist]_
*      - ``node`` | ``emission`` | ``type_tec`` | ``year``
*    * - emission_scaling [#em_scaling]_
*      - ``type_emission`` | ``emission``
*    * - bound_emission
*      - ``node`` | ``type_emission`` | ``type_tec`` | ``type_year``
*    * - tax_emission
*      - ``node`` | ``type_emission`` | ``type_tec`` | ``type_year``
*
* .. [#em_scaling] The parameters ``emission_scaling`` allows to efficiently aggregate different emissions/pollutants
*    and set bounds or taxes on various categories.
***

Parameters
    historical_emission(node,emission,type_tec,year_all)    historical emissions by technology type (including land)
    emission_scaling(type_emission,emission)                scaling factor to harmonize bounds or taxes across tpes
    bound_emission(node,type_emission,type_tec,type_year)   upper bound on emissions
    tax_emission(node,type_emission,type_tec,type_year)     emission tax
;

*----------------------------------------------------------------------------------------------------------------------*
* Land-use model emulator                                                                                              *
*----------------------------------------------------------------------------------------------------------------------*

***
* Parameters of the `Land-Use model emulator` section
* ---------------------------------------------------
*
* The implementation of |MESSAGEix| includes a land-use model emulator, which draws on exogenous land-use scenarios
* (provided by another model) to derive supply of commodities (e.g., biomass) and emissions
* from agriculture and forestry.
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - historical_land [#hist]_
*      - ``node`` | ``land_scenario`` | ``year``
*    * - land_cost
*      - ``node`` | ``land_scenario`` | ``year``
*    * - land_input
*      - ``node`` | ``land_scenario`` | ``year`` | ``commodity`` | ``level`` | ``time``
*    * - land_output
*      - ``node`` | ``land_scenario`` | ``year`` | ``commodity`` | ``level`` | ``time``
*    * - land_use
*      - ``node`` | ``land_scenario`` | ``year`` | ``land_type``
*    * - land_emission
*      - ``node`` | ``land_scenario`` | ``year`` | ``emission``
*    * - initial_land_scen_up
*      - ``node`` | ``land_scenario`` | ``year``
*    * - growth_land_scen_up
*      - ``node`` | ``land_scenario`` | ``year``
*    * - initial_land_scen_lo
*      - ``node`` |  ``land_scenario`` | ``year``
*    * - growth_land_scen_lo
*      - ``node`` | ``land_scenario`` | ``year``
*    * - initial_land_up
*      - ``node`` | ``year`` | ``land_type``
*    * - dynamic_land_up
*      - ``node`` | ``land_scenario`` | ``year`` | ``land_type``
*    * - growth_land_up
*      - ``node`` | ``year`` | ``land_type``
*    * - initial_land_lo
*      - ``node`` | ``year`` | ``land_type``
*    * - dynamic_land_lo
*      - ``node`` | ``land_scenario`` | ``year`` | ``land_type``
*    * - growth_land_lo
*      - ``node`` | ``year`` | ``land_type``
*
***

Parameters
    historical_land(node,land_scenario,year_all)            historical land scenario assignment
    land_cost(node,land_scenario,year_all)                  costs of land-use scenario
    land_input(node,land_scenario,year_all,commodity,level,time) commodity input requirement of land-use scenario
    land_output(node,land_scenario,year_all,commodity,level,time) commodity output (yield) of land-use scenario
    land_use(node,land_scenario,year_all,land_type)         land type used in specific scenario
    land_emission(node,land_scenario,year_all,emission)     emissions from land-use scenario
    initial_land_scen_up(node,land_scenario,year_all)       initial bound on land-scenario change (upwards)
    growth_land_scen_up(node,land_scenario,year_all)        relative bound on land-scenario change (upwards)
    initial_land_scen_lo(node,land_scenario,year_all)       initial bound on land-scenario change (downwards)
    growth_land_scen_lo(node,land_scenario,year_all)        relative bound on land-scenario change (downwards)
    initial_land_up(node,year_all,land_type)                initial bound on land-type use change (upwards)
    dynamic_land_up(node,land_scenario,year_all,land_type)  absolute bound on land-type use change (upwards)
    growth_land_up(node,year_all,land_type)                 relative bound on land-type use change (upwards)
    initial_land_lo(node,year_all,land_type)                initial bound on land-type use change (downwards)
    dynamic_land_lo(node,land_scenario,year_all,land_type)  absolute bound on land-type use change (upwards)
    growth_land_lo(node,year_all,land_type)                 relative bound on land-type use change (downwards)
;

*----------------------------------------------------------------------------------------------------------------------*
* Share constraints                                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

***
* Parameters of the `Share Constraints` section
* ---------------------------------------------
*
* Share constraints define the share of a given commodity to be active on a certain level
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - share_commodity_up
*      - ``shares`` | ``node_share`` | ``year_act`` | ``time``
*    * - share_commodity_lo
*      - ``shares`` | ``node`` | ``year_act`` | ``time``
*    * - share_mode_up
*      - ``shares`` | ``node_loc`` | ``technology`` | ``mode`` | ``year_act`` | ``time``
*    * - share_mode_lo
*      - ``shares`` | ``node_loc`` | ``technology`` | ``mode`` | ``year_act`` | ``time``
*
***

Parameters
    share_commodity_up(shares,node,year_all,time)    upper bound of commodity share constraint
    share_commodity_lo(shares,node,year_all,time)    lower bound of commodity share constraint
    share_mode_up(shares,node,tec,mode,year_all,time)    upper bound of mode share constraint
    share_mode_lo(shares,node,tec,mode,year_all,time)    lower bound of mode share constraint
;

*----------------------------------------------------------------------------------------------------------------------*
* Generic linear relations                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*

***
* Parameters of the `Relations` section
* -------------------------------------
*
* Generic linear relations are implemented in |MESSAGEix|.
* This feature is intended for development and testing only - all new features should be implemented
* as specific new mathematical formulations and associated sets & parameters.
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - relation_upper
*      - ``relation`` | ``node_rel`` | ``year_rel``
*    * - relation_lower
*      - ``relation`` | ``node_rel`` | ``year_rel``
*    * - relation_cost
*      - ``relation`` | ``node_rel`` | ``year_rel``
*    * - relation_new_capacity
*      - ``relation`` | ``node_rel`` | ``year_rel`` | ``tec``
*    * - relation_total_capacity
*      - ``relation`` | ``node_rel`` | ``year_rel`` | ``tec``
*    * - relation_activity
*      - ``relation`` | ``node_rel`` | ``year_rel`` | ``node_loc`` | ``tec`` | ``year_act`` | ``mode``
*
***

Parameters
    relation_upper(relation,node,year_all)    upper bound of generic relation
    relation_lower(relation,node,year_all)    lower bound of generic relation
    relation_cost(relation,node,year_all)     cost of investment and activities included in generic relation
    relation_new_capacity(relation,node,year_all,tec)   new capacity factor (multiplier) of generic relation
    relation_total_capacity(relation,node,year_all,tec) total capacity factor (multiplier) of generic relation
    relation_activity(relation,node,year_all,node,tec,year_all,mode) activity factor (multiplier) of generic relation
;

*----------------------------------------------------------------------------------------------------------------------*
* Fixed variable values                                                                                                *
*----------------------------------------------------------------------------------------------------------------------*

***
* Fixed variable values
* ---------------------
*
* The following parameters allow to set variable values to a specific value.
* The value is usually taken from a solution of another model instance
* (e.g., scenarios where a shock sets in later to mimick imperfect foresight).
*
* The fixed values do not override any upper or lower bounds that may be defined,
* so fixing variables to values outside of that range will yield an infeasible model.
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - fixed_extraction
*      - ``node`` | ``commodity`` | ``grade`` | ``year``
*    * - fixed_stock
*      - ``node`` | ``commodity`` | ``level`` | ``year``
*    * - fixed_new_capacity
*      - ``node`` | ``technology`` | ``year_vtg``
*    * - fixed_capacity
*      - ``node`` | ``technology`` | ``year_vtg`` | ``year_act``
*    * - fixed_activity
*      - ``node`` | ``technology`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``time``
*    * - fixed_land
*      - ``node`` | ``land_scenario`` | ``year``
*
* Note that the variable :math:`STOCK\_CHG` is determined implicitly by the :math:`STOCK` variable
* and therefore does not need to be explicitly fixed.
***

Parameters
    fixed_extraction(node,commodity,grade,year_all)     fixed extraction level
    fixed_stock(node,commodity,level,year_all)          fixed stock level
    fixed_new_capacity(node,tec,year_all)               fixed new-built capacity
    fixed_capacity(node,tec,vintage,year_all)           fixed maintained capacity
    fixed_activity(node,tec,vintage,year_all,mode,time) fixed activity level
    fixed_land(node,land_scenario,year_all)             fixed land level
;

*----------------------------------------------------------------------------------------------------------------------*
* Auxiliary reporting parameters                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*

Parameters
    total_cost(node, year_all)              total system costs net of trade costs and emissions taxes by node and year
    trade_cost(node, year_all)              net of commodity import costs and commodity export revenues by node and year
    import_cost(node, commodity, year_all)  import costs by commodity and node and year
    export_cost(node, commodity, year_all)  export revenues by commodity and node and year
;

*----------------------------------------------------------------------------------------------------------------------*
* Auxiliary parameters for GAMS workflow                                                                               *
*----------------------------------------------------------------------------------------------------------------------*

Parameters
    ctr               counter parameter for loops
    status(*,*)       model solution status parameter for log writing
;
