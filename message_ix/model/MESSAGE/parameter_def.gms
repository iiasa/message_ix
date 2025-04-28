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
***

***
* .. _section_parameter_general:
* .. _duration_period:
* .. _duration_time_rel:
*
* General parameters of the |MESSAGEix| implementation
* ----------------------------------------------------
*
* .. caution::
*
*    Parameters written in **bold** are auxiliary parameters
*    that are either generated automatically when exporting a :class:`message_ix.Scenario` to gdx
*    or that are computed during the *pre-processing* stage in GAMS (see the footnotes for more
*    individual details). These are **not** meant to be edited through the API when editing scenarios.
*
* .. list-table::
*    :widths: 25 20 55
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*      - Explanatory comments
*    * - interestrate
*      - ``year``
*      - Economy-wide interest rate or social discount rate
*    * - duration_time
*      - ``time``
*      - Duration of sub-annual time slices (relative to 1) [#duration_time_year]_
*    * - **duration_period** (:math:`|y|`) [#short_dur]_
*      - ``year``
*      - Duration of multi-year period (in number of years) [#year_auto]_
*    * - **duration_period_sum**
*      - ``year`` | ``year``
*      - Number of years between two periods [#df_auto]_
*    * - **duration_time_rel**
*      - ``time`` | ``time``
*      - Relative duration between sub-annual time slices [#df_auto]_
*    * - **df_period**
*      - ``year``
*      - Cumulative discount factor over period duration [#df_auto]_
*    * - **df_year**
*      - ``year``
*      - Discount factor of the last year in the period [#df_auto]_
*
* .. [#duration_time_year] The element 'Year' in the set of subannual time slices ``time`` has the value of 1.
*    This value is assigned by default when creating a new :class:`ixmp.Scenario` based on the ``MESSAGE`` scheme.
*
* .. [#short_dur] The short-hand notation :math:`|y|` is used for the parameters :math:`\text{duration_period}_y`
*    in the mathematical model documentation for exponents.
*
* .. [#year_auto] The values for this parameter are computed automatically when exporting a ``MESSAGE``-scheme
*    :class:`ixmp.Scenario` to gdx.
*    Note that in |MESSAGEix|, the elements of the ``year`` set are understood to be the last year in a period.
*    See :doc:`/time`.
*
* .. [#df_auto] These parameters are computed during the GAMS execution.
*
* .. _duration_period_sum:
*
* duration_period_sum (dimensions :math:`y_a, y_b`)
*    This parameter measures the total time from the **start** of period :math:`y_a`
*    until the **start** of any following period :math:`y_b`
*    (equivalently: until the **end** of the period immediately preceding :math:`y_b`).
*
*    For example, with periods labelled '1000', '1010', '1015', and '1020':
*
*    - The period '1000' ends on and includes the day 1000-12-31.
*    - The period '1010' starts on 1001-01-01 and ends on 1010-12-31.
*    - The period '1020' starts on 1016-01-01.
*    - Thus ``duration_period_sum(1010, 1020)`` measures the total time from 1001-01-01 to 1016-01-01,
*      which is 15 years.
*    - This is the same as ``duration_period(1010) + duration_period(1015)``.
*
*    This parameter is used,
*    *inter alia*,
*    to populate |map_tec_lifetime| and compute |remaining_capacity|.
***

Parameters
* general parameters
    interestrate(year_all)         interest rate (to compute discount factor)
    duration_time(time)            duration of one time slice (relative to 1)
    duration_period(year_all)      duration of one multi-year period (in years)
    duration_period_sum(year_all,year_all2)  number of years between two periods ('year_all' must precede 'year_all2')
    duration_time_rel(time,time2)  relative duration of subannual time period ('time2' relative to parent 'time')
    df_period(year_all)            cumulative discount factor over period duration
    df_year(year_all)              discount factor of the last year in the period
;

***
* .. _section_parameter_resources:
*
* Parameters of the `Resources` section
* -------------------------------------
*
* In |MESSAGEix|, the volume of resources at the start of the model horizon is defined by ``resource_volume``. The quantity of the
* resources that are extracted per year is dependent on two parameters. The first is ``bound_extraction_up``, which constraints
* the maximum extraction of the resources (by grade) in a year. The second is ``resource_remaining``, which is the maximum
* extraction of the remaining resources in a certain year, as a percentage. Extraction costs for resources are represented by
* ``resource_cost`` parameter.
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
* .. [#stock] Commodity stock refers to an exogenous (initial) quantity of commodity in stock. This parameter allows
*    (exogenous) additions to the commodity stock over the model horizon, e.g., precipitation that replenishes the water table.
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
* .. _section_parameter_demand:
*
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
* .. [#demand] The parameter ``demand`` in a ``MESSAGE``-scheme ``ixmp.Scenario`` is translated
*    to the parameter ``demand_fixed`` in the |MESSAGEix| implementation in GAMS. The variable ``DEMAND`` is introduced
*    as an auxiliary reporting variable; it equals ``demand_fixed`` in a `MESSAGE`-standalone run and reports
*    the final demand including the price response in an iterative `MESSAGE-MACRO` solution.
*
* .. [#peakload] The parameters ``peak_load_factor`` (maximum peak load factor for reliability constraint of firm capacity) and
*    ``reliability_factor`` (reliability of a technology (per rating)) are based on the formulation proposed by Sullivan et al., 2013 :cite:`Sullivan-2013`.
*    It is used in :ref:`reliability_constraint`.
*
***

Parameter
    demand_fixed(node,commodity,level,year_all,time)     exogenous demand levels
    peak_load_factor(node,commodity,level,year_all,time) maximum peak load factor for reliability constraint of firm capacity
;

***
* .. _params-tech:
*
* Parameters of the `Technology` section
* --------------------------------------
*
* Input/output mapping, costs and engineering specifications
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. list-table::
*    :widths: 25 60
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
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
*    * - construction_time [#construction]_
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
*      - ``node`` | ``tec`` | ``year_act`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - reliability_factor [#peakload]_
*      - ``node`` | ``tec`` | ``year_act`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - flexibility_factor [#flexfactor]_
*      - ``node_loc`` | ``tec`` | ``year_vtg`` | ``year_act`` | ``mode`` | ``commodity`` | ``level`` | ``time`` | ``rating``
*    * - renewable_capacity_factor [#renewables]_
*      - ``node_loc`` | ``commodity`` | ``grade`` | ``level`` | ``year``
*    * - renewable_potential [#renewables]_
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
*    As these are calculated in the preprocessing, the reported ``levelized_cost`` in the output GDX-file exclude fuel costs.
*
* .. [#construction] The construction time only has an effect on the investment costs; in |MESSAGEix|,
*    each unit of new-built capacity is available instantaneously at the beginning of the model period.
*
* .. [#rating] Maximum share of technology in commodity use per rating. The upper bound of a contribution by any technology to the constraints on system reliability
*    (:ref:`reliability_constraint`) and flexibility (:ref:`flexibility_constraint`) can depend on the share of the technology output in the total commodity use at
*    a specific level.
*
* .. [#flexfactor] Contribution of technologies towards operation flexibility constraint. It is used in :ref:`flexibility_constraint`.
*
* .. [#renewables] ``renewable_capacity_factor`` refers to the quality of renewable potential by grade and ``renewable_potential`` refers to the size of the renewable potential per grade.
*
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
    rating_bin(node,tec,year_all,commodity,level,time,rating) maximum share of technology in commodity use per rating
    reliability_factor(node,tec,year_all,commodity,level,time,rating) reliability of a technology (per rating)
    flexibility_factor(node,tec,vintage,year_all,mode,commodity,level,time,rating) contribution of technologies towards operation flexibility constraint
    renewable_capacity_factor(node,commodity,grade,level,year_all) quality of renewable potential grade (>= 1)
    renewable_potential(node,commodity,grade,level,year_all) size of renewable potential per grade
    emission_factor(node,tec,year_all,year_all,mode,emission) emission intensity of activity
;

***
* .. _section_parameter_bounds:
*
* Bounds on capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The following parameters specify upper and lower bounds on new capacity, total installed capacity, and activity. The bounds
* on activity are implemented as the aggregate over all vintages in a specific period (:ref:`activity_bound_up` and :ref:`activity_bound_lo`).
*
* .. list-table::
*    :widths: 25 60
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
* .. _section_parameter_dynamic_constraints:
* .. _growth_new_capacity_up:
* .. _initial_new_capacity_up:
*
* Dynamic constraints on new capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* These parameters are used in the :ref:`dynamic constraint equations <dynamic_constraints>` to limit the growth (or decline) of activity or of new capacity in each period, relative to the preceding period.
* The ``soft_`` parameters control ‘soft’ relaxation of these dynamic constraints, using the method of Keppo and Strubegger (2010) :cite:`Keppo-2010`.
*
* The ``growth_`` and ``soft_`` parameters are expressed as *relative annual change* and are unitless.
* Because these are annual values, are compounded in the :ref:`constraint equations <dynamic_constraints>` by ``duration_period`` (:math:`|y|`) to obtain the relative *inter-period* change.
*
* **Example:** a value of 0.05 for ``growth_activity_up`` sets an upper bound of :math:`1 + 0.05 = 105\%` activity in one year relative to activity in the preceding year.
* In a period with duration :math:`|y| = 5 \text{ years}`, the activity in the :doc:`representative year </time>` is bounded at :math:`(1.05)^5 = 128\%` of the activity in the representative year of the preceding period.
*
* Because these parameters do not have a ``mode`` (:math:`m`) dimension, they cannot be used to constraint the activity/new capacity of *single modes* of technologies; only the total across all modes.
*
* .. list-table::
*    :widths: 30 70
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - initial_new_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - growth_new_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - soft_new_capacity_up
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - initial_new_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - growth_new_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - soft_new_capacity_lo
*      - ``node_loc`` | ``tec`` | ``year_vtg``
*    * - initial_activity_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - growth_activity_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - soft_activity_up
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - initial_activity_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - growth_activity_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
*    * - soft_activity_lo
*      - ``node_loc`` | ``tec`` | ``year_act`` | ``time``
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
    soft_activity_lo(node,tec,year_all,time)       soft relaxation of dynamic lower bound on activity (growth rate),

    # Auxiliaries for growth_new_capacity_up
    gncu_1(node,tec,year_all)                      Auxiliary for growth_new_capacity_up,
    gncu_2(node,tec,year_all)                      Auxiliary for growth_new_capacity_up,
    k_gncu(node,tec,year_all2,year_all)            Auxiliary for growth_new_capacity_up
;

*----------------------------------------------------------------------------------------------------------------------*
* Add-on technology parameters                                                                                         *
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_parameter_addon:
*
* Parameters for the add-on technologies
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The implementation of |MESSAGEix| includes the functionality to introduce "add-on technologies" that are specifically
* linked to parent technologies. This feature can be used to model mitigation options (scrubber, cooling). Upper and
* lower bounds of add-on technologies are defined relative to the parent: ``addon_up`` and ``addon_lo``, respectively.
*
* .. note::
*    No default ``addon_conversion`` factor (conversion factor between add-on and parent technology activity) is set.
*    This is to avoid default conversion factors of 1 being set for technologies with multiple modes, of which only a
*    single mode should be linked to the add-on technology.
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
*      - ``node`` | ``tec`` | ``year_act`` | ``mode`` | ``time`` | ``type_addon``
*    * - addon_lo
*      - ``node`` | ``tec`` | ``year_act`` | ``mode`` | ``time`` | ``type_addon``
*
***

Parameters
    addon_conversion(node,tec,vintage,year_all,mode,time,type_addon) conversion factor between add-on and parent technology activity
    addon_up(node,tec,year_all,mode,time,type_addon)    upper bound of add-on technologies relative to parent technology
    addon_lo(node,tec,year_all,mode,time,type_addon)    lower bound of add-on technologies relative to parent technology
;

*----------------------------------------------------------------------------------------------------------------------*
* Storage parameters
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_parameter_storage:
*
* Parameters for representing storage solutions
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The |MESSAGEix| formulation includes "storage" solutions to model sub-annual, inter-temporal storage of commodities in each period.
* This feature can be used to model electricity storage (pumped hydro, batteries, compressed air energy storage, etc.), thermal energy storage,
* demand side management, and in general any technology for storing commodities (gas, hydrogen, water, etc.) over sub-annual timesteps.
* The user defines the chronological order of sub-annual time slices by assigning a number to them in parameter ``time_order``.
* This order is used by storage equations to shift the stored commodity in a correct timeline, e.g., from Jan through to Dec, and not vice versa.
* The last sub-annual time slice is linked to the first one to close the loop of the year. Parameter ``storage_initial`` is to set an initial amount
* for the content of storage in any desirable time slice (optionally). This initial value is a cost-free stored media that storage can discharge
* in the same or following time slices. ``storage_self_discharge`` represents the self-discharge (loss) of storage as % of the level of stored media
* in each time slice. This allows to model time-related losses in storage separately, in addition to charging and discharging losses.
*
* .. list-table::
*    :widths: 20 80
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - storage_initial
*      - ``node`` | ``tec`` | ``level`` | ``commodity`` | ``year_act`` | ``time``
*    * - storage_self_discharge
*      - ``node`` | ``tec`` | ``level`` | ``commodity`` | ``year_act`` | ``time``
*    * - time_order
*      - ``lvl_temporal`` | ``time``
*
***

Parameters
    storage_initial(node,tec,mode,level,commodity,year_all,time)                       initial content of storage
    storage_self_discharge(node,tec,mode,level,commodity,year_all,time)                self-discharge (loss) of storage as % of storage level in each time slice
    time_order(lvl_temporal,time)                                                 sequence of subannual time slices
;

*----------------------------------------------------------------------------------------------------------------------*
* Soft relaxations of dynamic constraints                                                                              *
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_parameter_soft_constraints:
*
* Cost parameters for 'soft' relaxations of dynamic constraints
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The implementation of |MESSAGEix| includes the functionality for 'soft' relaxations of dynamic constraints on
* new-built capacity and activity (see Keppo and Strubegger, 2010 :cite:`Keppo-2010`).
* Refer to the section :ref:`dynamic_constraints`. Absolute cost and levelized cost multipliers are used
* for the relaxation of upper and lower bounds.
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
* .. _section_parameter_historical:
* .. _historical_new_capacity:
*
* Historical capacity and activity values
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* To model the transition of an energy system, the initial energy system with its energy mix
* needs to be defined first. The historical activity and the historical new capacity do this.
* These parameters have to be defined in order to limit the capacity in the first model period.
*
* Historical data on new capacity and activity levels are therefore included in |MESSAGEix| for
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
* The activity in the historic period can be defined with
*
* .. math::
*    \sum_{m} \text{ACT}_{n,t,y^V,y,m,h} \leq \text{duration_time}_{h} \cdot \text{capacity_factor}_{n,t,y^V,y,h} \\
*    \cdot \text{CAP}_{n,t,y^V,y} \quad t \ \in \ T^{\text{INV}}
*
* and the historical new capacity with
*
* .. math::
*    \text{CAP_NEW}_{n,t,y^V} = \frac{\text{CAP}_{n,t,y^V,y}}{\text{duration_period}_{y}}
*
* Both equations are equally valid for model periods. However, to calculate ``historical_new_capacity``
* and ``historical_activity`` all parameters must describe the historic period.
*
* The ``duration_period`` of the first period (historic period) is set to the value that appears
* most frequently in the model. If, for example, the majority of periods in the model
* consists of 10 years, the ``duration_period`` of the first period is likewise 10 years.
*
***

Parameters
    historical_new_capacity(node,tec,year_all)           historical new capacity
    historical_activity(node,tec,year_all,mode,time)     historical activity
;

***
* .. _section_parameter_investment:
* .. _remaining_capacity:
*
* Auxiliary investment cost parameters and multipliers
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Auxiliary investment cost parameters include the remaining technical lifetime at the end of model horizon (``beyond_horizon_lifetime``) in addition to the
* different scaling factors and multipliers as listed below. These factors account for remaining capacity (``remaining_capacity``) or construction time of new capacity (``construction_time_factor``),
* the value of investment at the end of model horizon (``end_of_horizon_factor``) or the discount factor of remaining lifetime beyond model horizon (``beyond_horizon_factor``).
*
* .. list-table::
*    :widths: 35 50
*    :header-rows: 1
*
*    * - Parameter name
*      - Index names
*    * - construction_time_factor
*      - ``node`` | ``tec`` | ``year``
*    * -  remaining_capacity
*      - ``node`` | ``tec`` | ``year``
*    * - end_of_horizon_factor
*      - ``node`` | ``tec`` | ``year``
*    * - beyond_horizon_lifetime
*      - ``node`` | ``tec`` | ``year``
*    * - beyond_horizon_factor
*      - ``node`` | ``tec`` | ``year``
*
*
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
* .. _section_parameter_emissions:
*
* Parameters of the `Emission` section
* ------------------------------------
*
* The implementation of |MESSAGEix| includes a flexible and versatile accounting of emissions across different
* categories and species, with the option to define upper bounds and taxes on various (aggregates of) emissions
* and pollutants, (sets of) technologies, and (sets of) years.
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
* .. [#em_scaling] The parameter ``emission_scaling`` is the scaling factor to harmonize bounds or taxes across types of
*    emissions. It allows to efficiently aggregate different emissions/pollutants and set bounds or taxes on various categories.
*
***

Parameters
    historical_emission(node,emission,type_tec,year_all)    historical emissions by technology type (including land)
    emission_scaling(type_emission,emission)                scaling factor to harmonize bounds or taxes across types
    bound_emission(node,type_emission,type_tec,type_year)   upper bound on emissions
    tax_emission(node,type_emission,type_tec,type_year)     emission tax
;

*----------------------------------------------------------------------------------------------------------------------*
* Land-use model emulator                                                                                              *
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_parameter_landuse_emulator:
*
* Parameters of the `Land-Use model emulator` section
* ---------------------------------------------------
*
* The implementation of |MESSAGEix| includes a land-use model emulator, which draws on exogenous land-use scenarios
* (provided by another model) to derive supply of commodities (e.g., biomass) and emissions
* from agriculture and forestry. The parameters listed below refer to the assigned land scenario.
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
* .. _section_parameter_share_constraints:
*
* Parameters of the `Share Constraints` section
* ---------------------------------------------
*
* Share constraints define the share of a given commodity/mode to be active on a certain level. For the mathematical
* formulation, refer to :ref:`share_constraints`.
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
* .. _section_parameter_generic_relations:
*
* Parameters of the `Relations` section
* -------------------------------------
*
* Generic linear relations are implemented in |MESSAGEix|. This feature is intended for development and testing only - all new features
* should be implemented as specific new mathematical formulations and associated *sets* & *parameters*. For the formulation of the relations,
* refer to :ref:`section_of_generic_relations`.
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
* .. _section_parameter_fixed:
*
* Fixed variable values
* ---------------------
*
* The following parameters allow to set variable values to a specific value.
* The value is usually taken from a solution of another model instance
* (e.g., scenarios where a shock sets in later to mimic imperfect foresight).
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
* Note that the variable :math:`\text{STOCK_CHG}` is determined implicitly by the :math:`\text{STOCK}` variable
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

***
* .. _section_parameter_auxiliary_reporting:
*
* Auxiliary reporting parameters
* ------------------------------
*
* The following parameters are used for reporting (post-processing) solved models. They assign monetary value to
* the `net` total system costs from trading and emission taxes (``total_cost``). Morevoer, they also assign a value
* to the `total` trade of commodities (the difference between the revenues from exports and the costs of imports,
* ``trade_cost``) and to the costs from importing (``import_cost``) and the revenues from exporting (``export_cost``)
* in each node and year.
*
* .. list-table::
*    :widths: 25 75
*    :header-rows: 1
*
*    * - Parameter name
*      - Index dimensions
*    * - total_cost
*      - ``node`` | ``year``
*    * - trade_cost
*      - ``node`` | ``year``
*    * - import_cost
*      - ``node`` | ``commodity`` | ``year``
*    * - export_cost
*      - ``node`` | ``commodity`` | ``year``
***

Parameters
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
