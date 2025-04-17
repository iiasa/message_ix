***
* MESSAGE core formulation
* ========================
*
* The |MESSAGEix| systems-optimization model minimizes total costs while satisfying given demand levels for commodities/services and considering a broad range of technical/engineering constraints and societal restrictions (e.g. bounds on greenhouse gas emissions, pollutants, system reliability).
* Demand levels are static (i.e. non-elastic), but the demand response can be integrated by linking |MESSAGEix| to the single sector general-economy MACRO model included in this framework.
*
* For the complete list of sets, mappings and parameters, refer to the auto-documentation page :ref:`sets_maps_def` and :ref:`parameter_def`.
* The mathematical notation that is used to represent sets and mappings in the equations below can also be found in the tables in :ref:`sets_maps_def`.
*
* .. contents::
*    :local:
*    :backlinks: none
*
***

*----------------------------------------------------------------------------------------------------------------------*
* Variable definitions                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_variable_def:
*
* Variable definitions
* --------------------
*
* .. _section_decision_variable_def:
*
* Decision variables
* ^^^^^^^^^^^^^^^^^^
* =============================================================== ====================================================================================
* Variable                                                        Explanatory text
* =============================================================== ====================================================================================
* :math:`\text{OBJ} \in \mathbb{R}`                               Objective value of the optimization program
* :math:`\text{EXT}_{n,c,g,y} \in \mathbb{R}_+`                   Extraction of non-renewable/exhaustible resources from reserves
* :math:`\text{STOCK}_{n,c,l,y} \in \mathbb{R}_+`                 Quantity in stock (storage) at start of period :math:`y`
* :math:`\text{STOCK_CHG}_{n,c,l,y,h} \in \mathbb{R}`             Input or output quantity into intertemporal commodity stock (storage)
* :math:`\text{COST_NODAL}_{n,y} \in \mathbb{R}`                  System costs at the node level over time
* :math:`\text{REN}_{n,t,c,g,y,h} \in \mathbb{R}_+`               Activity of renewable technologies per grade
* :math:`\text{CAP_NEW}_{n,t,y} \in \mathbb{R}_+`                 Newly installed capacity (yearly average over period duration)
* :math:`\text{CAP}_{n,t,y^V,y} \in \mathbb{R}_+`                 Maintained capacity in year :math:`y` of vintage :math:`y^V`
* :math:`\text{CAP_FIRM}_{n,t,c,l,y,q} \in \mathbb{R}_+`          Capacity counting towards firm (dispatchable)
* :math:`\text{ACT}_{n,t,y^V,y,m,h} \in \mathbb{R}`               Activity of a technology (by vintage, mode, subannual time)
* :math:`\text{ACT_RATING}_{n,t,y^V,y,c,l,h,q} \in \mathbb{R}_+`  Auxiliary variable for activity attributed to a particular rating bin [#ACT_RATING]_
* :math:`\text{CAP_NEW_UP}_{n,t,y} \in \mathbb{R}_+`              Relaxation of upper dynamic constraint on new capacity
* :math:`\text{CAP_NEW_LO}_{n,t,y} \in \mathbb{R}_+`              Relaxation of lower dynamic constraint on new capacity
* :math:`\text{ACT_UP}_{n,t,y,h} \in \mathbb{R}_+`                Relaxation of upper dynamic constraint on activity [#ACT_BD]_
* :math:`\text{ACT_LO}_{n,t,y,h} \in \mathbb{R}_+`                Relaxation of lower dynamic constraint on activity [#ACT_BD]_
* :math:`\text{LAND}_{n,s,y} \in [0,1]`                           Relative share of land-use scenario (for land-use model emulator)
* :math:`\text{EMISS}_{n,e,\widehat{t},y} \in \mathbb{R}`         Auxiliary variable for aggregate emissions by technology type
* :math:`\text{REL}_{r,n,y} \in \mathbb{R}`                       Auxiliary variable for left-hand side of relations (linear constraints)
* :math:`\text{COMMODITY_USE}_{n,c,l,y} \in \mathbb{R}`           Auxiliary variable for amount of commodity used at specific level
* :math:`\text{COMMODITY_BALANCE}_{n,c,l,y,h} \in \mathbb{R}`     Auxiliary variable for right-hand side of :ref:`commodity_balance`
* :math:`\text{STORAGE}_{n,t,m,l,c,y,h} \in \mathbb{R}`           State of charge or content of storage at each sub-annual time slice
* :math:`\text{STORAGE_CHARGE}_{n,t,m,l,c,y,h} \in \mathbb{R}`    Charging of storage in each sub-annual time slice (negative for discharging)
* =============================================================== ====================================================================================
*
* The index :math:`y^V` is the year of construction (vintage) wherever it is necessary to
* clearly distinguish between year of construction and the year of operation.
*
* All decision variables are by year, not by (multi-year) period, except :math:`\text{STOCK}_{n,c,l,y}`.
* In particular, the new capacity variable :math:`\text{CAP_NEW}_{n,t,y}` has to be multiplied by the number of years
* in a period :math:`|y| = \text{duration_period}_{y}` to determine the available capacity :math:`\text{CAP}_{n,t,y^V,y}`
* in subsequent periods (assuming the newly build capacity is not immediately decommissioned):
*
* :math:`\text{CAP}_{n,t,y^V,y} = \text{CAP_NEW}_{n,t,y} \cdot \text{duration_period}_{y}`
*
* :math:`\text{CAP_NEW}_{n,t,y}` is therefore the amount of newly installed capacity *in one year* and
* :math:`\text{CAP}_{n,t,y^V,y}` the amount, which is installed at the *end of a (usually multi-year) period*.
* This formulation gives more flexibility when it comes to using periods of different duration
* (more intuitive comparison across different periods).
*
* The current model framework allows both input or output normalized formulation.
* This will affect the parametrization, see Section :ref:`efficiency_output` for more details.
*
* .. [#ACT_RATING] The auxiliary variable :math:`\text{ACT_RATING}_{n,t,y^V,y,c,l,h,q}` is defined in terms of input or
*    output of the technology.
*
* .. [#ACT_BD] The dynamic activity constraints are implemented as summed over all modes;
*    therefore, the variables for the relaxation are not indexed over the set ``mode``.
*
***

Variables
    OBJ objective value of the optimisation problem
;

Positive Variables
* resource production/extraction variable
    EXT(node,commodity,grade,year_all)   extraction of fossil resources
* commodity in inter-temporal stock
    STOCK(node,commodity,level,year_all) total quantity in intertemporal stock (storage)
* use of renewable resources
    REN(node, tec, commodity, grade, year_all, time)     activity of renewables specified per renewables grade
* investment and capacity variables
    CAP_NEW(node,tec,year_all)       new capacity by year
    CAP(node,tec,vintage,year_all)   total installed capacity by year
    CAP_FIRM(node,tec,commodity,level,year_all) capacity counting towards system reliability constraints
* auxiliary variable for distributing total activity of a technology to a number of "rating bins"
    ACT_RATING(node,tec,vintage,year_all,commodity,level,time,rating)
* variables for soft relaxation of dynamic activity constraints
    CAP_NEW_UP(node,tec,year_all)    relaxation variable for dynamic constraints on new capacity (upwards)
    CAP_NEW_LO(node,tec,year_all)    relaxation variable for dynamic constraints on new capacity (downwards)
    ACT_UP(node,tec,year_all,time)   relaxation variable for dynamic constraints on activity (upwards)
    ACT_LO(node,tec,year_all,time)   relaxation variable for dynamic constraints on activity (downwards)
* land-use model emulator
    LAND(node,land_scenario,year_all) relative share of land-use scenario
* content of storage
    STORAGE(node,tec,mode,level,commodity,year_all,time)       state of charge (SoC) of storage at each sub-annual time slice (positive)
;

Variables
* intertemporal stock variables (input or output quantity into the stock)
    STOCK_CHG(node,commodity,level,year_all,time) annual input into and output from stocks of commodities
* technology activity variables (can be negative for some technologies, upper and lower bounds stated explicitly)
    ACT(node,tec,vintage,year_all,mode,time)     activity of technology by mode-year-timeperiod
* auxiliary variables for finrm-capacity formulation
    COMMODITY_USE(node,commodity,level,year_all) total amount of a commodity & level that was used or consumed
* nodal system costs over time
    COST_NODAL(node, year_all)                   system costs at the node level over time
* auxiliary variable for aggregate emissions by technology type and land-use model emulator
    EMISS(node,emission,type_tec,year_all)       aggregate emissions by technology type and land-use model emulator
* auxiliary variable for left-hand side of relations (linear constraints)
    REL(relation,node,year_all)                  auxiliary variable for left-hand side of user-defined relations
* change in the content of storage device
    STORAGE_CHARGE(node,tec,mode,level,commodity,year_all,time)    charging of storage in each time slice (negative for discharge)
;

***
* .. _section_auxiliary_variable_def:
*
* Auxiliary variables
* ^^^^^^^^^^^^^^^^^^^
* =========================================================================== =======================================================================================================
* Variable                                                                    Explanatory text
* =========================================================================== =======================================================================================================
* :math:`\text{DEMAND}_{n,c,l,y,h} \in \mathbb{R}`                            Demand level (in equilibrium with MACRO integration)
* :math:`\text{PRICE_COMMODITY}_{n,c,l,y,h} \in \mathbb{R}`                   Commodity price (undiscounted marginals of :ref:`commodity_balance_gt` and :ref:`commodity_balance_lt`)
* :math:`\text{PRICE_EMISSION}_{n,\widehat{e},\widehat{t},y} \in \mathbb{R}`  Emission price (undiscounted marginals of :ref:`emission_equivalence`)
* :math:`\text{COST_NODAL_NET}_{n,y} \in \mathbb{R}`                          System costs at the node level net of energy trade revenues/cost
* :math:`\text{GDP}_{n,y} \in \mathbb{R}`                                     Gross domestic product (GDP) in market exchange rates for MACRO reporting
* =========================================================================== =======================================================================================================
***

Variables
* auxiliary variables for demand, prices, costs and GDP (for reporting when MESSAGE is run with MACRO)
    DEMAND(node,commodity,level,year_all,time) demand
    PRICE_COMMODITY(node,commodity,level,year_all,time)  commodity price (derived from marginals of COMMODITY_BALANCE constraint)
    PRICE_EMISSION(node,type_emission,type_tec,year_all) emission price (derived from marginals of EMISSION_EQUIVALENCE constraint)
    COST_NODAL_NET(node,year_all)              system costs at the node level over time including effects of energy trade
    GDP(node,year_all)                         gross domestic product (GDP) in market exchange rates for MACRO reporting
;

*----------------------------------------------------------------------------------------------------------------------*
* auxiliary bounds on activity variables (debugging mode, avoid inter-vintage arbitrage, investment technology)                                                        *
*----------------------------------------------------------------------------------------------------------------------*

* include upper and lower bounds (to avoid unbounded models)
%AUX_BOUNDS% ACT.lo(node,tec,year_all,year_all2,mode,time)$( map_tec_lifetime(node,tec,year_all,year_all2)
%AUX_BOUNDS%    AND map_tec_act(node,tec,year_all2,mode,time) ) = -%AUX_BOUND_VALUE% ;
%AUX_BOUNDS% ACT.up(node,tec,year_all,year_all2,mode,time)$( map_tec_lifetime(node,tec,year_all,year_all2)
%AUX_BOUNDS%    AND map_tec_act(node,tec,year_all2,mode,time) ) = %AUX_BOUND_VALUE% ;

* to avoid "inter-vintage arbitrage" (across different vintages of technologies), all activities that
* have positive lower bounds are assumed to be non-negative
ACT.lo(node,tec,year_all,year_all2,mode,time)$( map_tec_lifetime(node,tec,year_all,year_all2)
    AND map_tec_act(node,tec,year_all2,mode,time) AND bound_activity_lo(node,tec,year_all2,mode,time) >= 0 ) = 0 ;
* previous implementation using upper bounds
* ACT.lo(node,tec,year_all,year_all2,mode,time)$( map_tec_lifetime(node,tec,year_all,year_all2)
*    AND map_tec_act(node,tec,year_all2,mode,time)
*    AND ( NOT bound_activity_up(node,tec,year_all2,mode,time)
*        OR bound_activity_up(node,tec,year_all2,mode,time) >= 0 ) ) = 0 ;

* assume that all "investment" technologies must have non-negative activity levels
ACT.lo(node,inv_tec,year_all,year_all2,mode,time)$( map_tec_lifetime(node,inv_tec,year_all,year_all2)
    AND map_tec_act(node,inv_tec,year_all2,mode,time) ) = 0 ;

*----------------------------------------------------------------------------------------------------------------------*
* fixing variables to pre-specified values                                                                             *
*----------------------------------------------------------------------------------------------------------------------*

EXT.fx(node,commodity,grade,year_all)$( is_fixed_extraction(node,commodity,grade,year_all) ) =
    fixed_extraction(node,commodity,grade,year_all);
STOCK.fx(node,commodity,level,year_all)$( is_fixed_stock(node,commodity,level,year_all) ) =
    fixed_stock(node,commodity,level,year_all) ;
CAP_NEW.fx(node,tec,year_all)$( is_fixed_new_capacity(node,tec,year_all) ) =
    fixed_new_capacity(node,tec,year_all) ;
CAP.fx(node,tec,vintage,year_all)$( is_fixed_capacity(node,tec,vintage,year_all) ) =
    fixed_capacity(node,tec,vintage,year_all) ;
ACT.fx(node,tec,vintage,year_all,mode,time)$( is_fixed_activity(node,tec,vintage,year_all,mode,time) ) =
    fixed_activity(node,tec,vintage,year_all,mode,time) ;
LAND.fx(node,land_scenario,year_all)$( is_fixed_land(node,land_scenario,year_all) ) =
    fixed_land(node,land_scenario,year_all) ;

*----------------------------------------------------------------------------------------------------------------------*
* auxiliary variables for debugging mode (identifying infeasibilities)                                                 *
*----------------------------------------------------------------------------------------------------------------------*

* report mapping for debugging
Set
    AUX_ACT_BOUND_UP(node,tec,year_all,year_all2,mode,time) indicator whether auxiliary upper bound on activity is binding
    AUX_ACT_BOUND_LO(node,tec,year_all,year_all2,mode,time) indicator whether auxiliary upper bound on activity is binding
;

* slack variables for debugging
Positive variables
    SLACK_COMMODITY_EQUIVALENCE_UP(node,commodity,level,year_all,time) slack variable for commodity balance (upwards)
    SLACK_COMMODITY_EQUIVALENCE_LO(node,commodity,level,year_all,time) slack variable for commodity balance (downwards)
    SLACK_CAP_NEW_BOUND_UP (node,tec,year_all)        slack variable for bound on new capacity (upwards)
    SLACK_CAP_NEW_BOUND_LO (node,tec,year_all)        slack variable for bound on new capacity (downwards)
    SLACK_CAP_TOTAL_BOUND_UP (node,tec,year_all)      slack variable for upper bound on total installed capacity
    SLACK_CAP_TOTAL_BOUND_LO (node,tec,year_all)      slack variable for lower bound on total installed capacity
    SLACK_CAP_NEW_DYNAMIC_UP(node,tec,year_all)       slack variable for dynamic new capacity constraint (upwards)
    SLACK_CAP_NEW_DYNAMIC_LO(node,tec,year_all)       slack variable for dynamic new capacity constraint (downwards)
    SLACK_ACT_BOUND_UP(node,tec,year_all,mode,time)   slack variable for upper bound on activity
    SLACK_ACT_BOUND_LO(node,tec,year_all,mode,time)   slack variable for lower bound on activity
    SLACK_ACT_DYNAMIC_UP(node,tec,year_all,time)      slack variable for dynamic activity constraint relaxation (upwards)
    SLACK_ACT_DYNAMIC_LO(node,tec,year_all,time)      slack variable for dynamic activity constraint relaxation (downwards)
    SLACK_LAND_SCEN_UP(node,land_scenario,year_all)   slack variable for dynamic land scenario constraint relaxation (upwards)
    SLACK_LAND_SCEN_LO(node,land_scenario,year_all)   slack variable for dynamic land scenario constraint relaxation (downwards)
    SLACK_LAND_TYPE_UP(node,year_all,land_type)       slack variable for dynamic land type constraint relaxation (upwards)
    SLACK_LAND_TYPE_LO(node,year_all,land_type)       slack variable for dynamic land type constraint relaxation (downwards)
    SLACK_RELATION_BOUND_UP(relation,node,year_all)   slack variable for upper bound of generic relation
    SLACK_RELATION_BOUND_LO(relation,node,year_all)   slack variable for lower bound of generic relation
;

*----------------------------------------------------------------------------------------------------------------------*
* equation definitions                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

Equations
    OBJECTIVE                       objective value of the optimisation problem
    COST_ACCOUNTING_NODAL           cost accounting at node level over time
    EXTRACTION_EQUIVALENCE          auxiliary equation to simplify the resource extraction formulation
    EXTRACTION_BOUND_UP             upper bound on extraction (by grade)
    RESOURCE_CONSTRAINT             constraint on resources remaining in each period (maximum extraction per period)
    RESOURCE_HORIZON                constraint on extraction over entire model horizon (resource volume in place)
    COMMODITY_BALANCE_GT            commodity supply greater than or equal demand
    COMMODITY_BALANCE_LT            commodity supply lower than or equal demand
    STOCKS_BALANCE                  commodity inter-temporal balance of stocks
    CAPACITY_CONSTRAINT             capacity constraint for technology (by sub-annual time slice)
    CAPACITY_MAINTENANCE_HIST       constraint for capacity maintenance  historical installation (built before start of model horizon)
    CAPACITY_MAINTENANCE_NEW        constraint for capacity maintenance of new capacity built in the current period (vintage == year)
    CAPACITY_MAINTENANCE            constraint for capacity maintenance over the technical lifetime
    OPERATION_CONSTRAINT            constraint on maximum yearly operation (scheduled down-time for maintenance)
    MIN_UTILIZATION_CONSTRAINT      constraint for minimum yearly operation (aggregated over the course of a year)
    RENEWABLES_POTENTIAL_CONSTRAINT constraint on renewable resource potential
    RENEWABLES_CAPACITY_REQUIREMENT lower bound on required overcapacity when using lower grade potentials
    RENEWABLES_EQUIVALENCE          equation to define the renewables extraction
    ADDON_ACTIVITY_UP               addon-technology activity upper constraint
    ADDON_ACTIVITY_LO               addon technology activity lower constraint
    COMMODITY_USE_LEVEL             aggregate use of commodity by level as defined by total input into technologies
    ACTIVITY_BY_RATING              constraint on auxiliary rating-specific activity variable by rating bin
    ACTIVITY_RATING_TOTAL           equivalence of auxiliary rating-specific activity variables to actual activity
    FIRM_CAPACITY_PROVISION         contribution of dispatchable technologies to auxiliary firm-capacity variable
    SYSTEM_RELIABILITY_CONSTRAINT   constraint on total system reliability (firm capacity)
    SYSTEM_FLEXIBILITY_CONSTRAINT   constraint on total system flexibility
    NEW_CAPACITY_BOUND_UP           upper bound on technology capacity investment
    NEW_CAPACITY_BOUND_LO           lower bound on technology capacity investment
    TOTAL_CAPACITY_BOUND_UP         upper bound on total installed capacity
    TOTAL_CAPACITY_BOUND_LO         lower bound on total installed capacity
    NEW_CAPACITY_CONSTRAINT_UP      dynamic constraint for capacity investment (learning and spillovers upper bound)
    NEW_CAPACITY_SOFT_CONSTRAINT_UP bound on soft relaxation of dynamic new capacity constraints (upwards)
    NEW_CAPACITY_CONSTRAINT_LO      dynamic constraint on capacity investment (lower bound)
    NEW_CAPACITY_SOFT_CONSTRAINT_LO bound on soft relaxation of dynamic new capacity constraints (downwards)
    ACTIVITY_BOUND_UP               upper bound on activity summed over all vintages
    ACTIVITY_BOUND_LO               lower bound on activity summed over all vintages
    ACTIVITY_BOUND_ALL_MODES_UP     upper bound on activity summed over all vintages and modes
    ACTIVITY_BOUND_ALL_MODES_LO     lower bound on activity summed over all vintages and modes
    SHARE_CONSTRAINT_COMMODITY_UP   upper bounds on share constraints for commodities
    SHARE_CONSTRAINT_COMMODITY_LO   lower bounds on share constraints for commodities
    SHARE_CONSTRAINT_MODE_UP        upper bounds on share constraints for modes of a given technology
    SHARE_CONSTRAINT_MODE_LO        lower bounds on share constraints for modes of a given technology
    ACTIVITY_CONSTRAINT_UP          dynamic constraint on the market penetration of a technology activity (upper bound)
    ACTIVITY_SOFT_CONSTRAINT_UP     bound on relaxation of the dynamic constraint on market penetration (upper bound)
    ACTIVITY_CONSTRAINT_LO          dynamic constraint on the market penetration of a technology activity (lower bound)
    ACTIVITY_SOFT_CONSTRAINT_LO     bound on relaxation of the dynamic constraint on market penetration (lower bound)
    EMISSION_EQUIVALENCE            auxiliary equation to simplify the notation of emissions
    EMISSION_CONSTRAINT             nodal-regional-global constraints on emissions (by category)
    LAND_CONSTRAINT                 constraint on total land use (linear combination of land scenarios adds up to 1)
    DYNAMIC_LAND_SCEN_CONSTRAINT_UP dynamic constraint on land scenario change (upper bound)
    DYNAMIC_LAND_SCEN_CONSTRAINT_LO dynamic constraint on land scenario change (lower bound)
    DYNAMIC_LAND_TYPE_CONSTRAINT_UP dynamic constraint on land-use change (upper bound)
    DYNAMIC_LAND_TYPE_CONSTRAINT_LO dynamic constraint on land-use change (lower bound)
    RELATION_EQUIVALENCE            auxiliary equation to simplify the implementation of relations
    RELATION_CONSTRAINT_UP          upper bound of relations (linear constraints)
    RELATION_CONSTRAINT_LO          lower bound of relations (linear constraints)
    STORAGE_CHANGE                  change in the state of charge of storage
    STORAGE_BALANCE                 balance of the state of charge of storage
    STORAGE_BALANCE_INIT            balance of the state of charge of storage at sub-annual time slices with initial storage content
    STORAGE_INPUT                   connecting an input commodity to maintain the activity of storage container (not stored commodity)
;
*----------------------------------------------------------------------------------------------------------------------*
* equation statements                                                                                                  *
*----------------------------------------------------------------------------------------------------------------------*

***
* .. _section_objective:
*
* Objective function
* ------------------
*
* The objective function of the |MESSAGEix| core model
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_objective:
*
* Equation OBJECTIVE
* """"""""""""""""""
*
* The objective function (of the core model) minimizes total discounted systems costs including costs for emissions,
* relaxations of dynamic constraints
*
* .. math::
*    \text{OBJ} = \sum_{n,y \in Y^{M}} \text{df_period}_{y} \cdot \text{COST_NODAL}_{n,y}
*
***
OBJECTIVE..
    OBJ =E= SUM( (node,year), df_period(year) * COST_NODAL(node,year) ) ;

***
* Regional system cost accounting function
* ----------------------------------------
*
* Accounting of regional system costs over time
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_cost_accounting_nodal:
*
* Equation COST_ACCOUNTING_NODAL
* """"""""""""""""""""""""""""""
*
* Accounting of regional systems costs over time as well as costs for emissions (taxes),
* land use (from the model land-use model emulator), relaxations of dynamic constraints,
* and linear relations.
*
* .. math::
*    \text{COST_NODAL}_{n,y} & = \sum_{c,g} \ \text{resource_cost}_{n,c,g,y} \cdot \text{EXT}_{n,c,g,y} \\
*      & + \sum_{t} \
*          \bigg( \text{inv_cost}_{n,t,y} \cdot \text{construction_time_factor}_{n,t,y} \\
*      & \quad \quad \quad \cdot \text{end_of_horizon_factor}_{n,t,y} \cdot \text{CAP_NEW}_{n,t,y} \\[4 pt]
*      & \quad \quad + \sum_{y^V \leq y} \ \text{fix_cost}_{n,t,y^V,y} \cdot \text{CAP}_{n,t,y^V,y} \\
*      & \quad \quad + \sum_{\substack{y^V \leq y \\ m,h}} \ \text{var_cost}_{n,t,y^V,y,m,h} \cdot \text{ACT}_{n,t,y^V,y,m,h} \\
*      & \quad \quad + \Big( \text{abs_cost_new_capacity_soft_up}_{n,t,y} \\
*      & \quad \quad \quad
*          + \text{level_cost_new_capacity_soft_up}_{n,t,y} \cdot\ \text{inv_cost}_{n,t,y}
*          \Big) \cdot \text{CAP_NEW_UP}_{n,t,y} \\[4pt]
*      & \quad \quad + \Big( \text{abs_cost_new_capacity_soft_lo}_{n,t,y} \\
*      & \quad \quad \quad
*          + \text{level_cost_new_capacity_soft_lo}_{n,t,y} \cdot\ \text{inv_cost}_{n,t,y}
*          \Big) \cdot \text{CAP_NEW_LO}_{n,t,y} \\[4pt]
*      & \quad \quad + \sum_{m,h} \ \Big( \text{abs_cost_activity_soft_up}_{n,t,y,m,h} \\
*      & \quad \quad \quad
*          + \text{level_cost_activity_soft_up}_{n,t,y,m,h} \cdot\ \text{levelized_cost}_{n,t,y,m,h}
*          \Big) \cdot \text{ACT_UP}_{n,t,y,h} \\
*      & \quad \quad + \sum_{m,h} \ \Big( \text{abs_cost_activity_soft_lo}_{n,t,y,m,h} \\
*      & \quad \quad \quad
*          + \text{level_cost_activity_soft_lo}_{n,t,y,m,h} \cdot\ \text{levelized_cost}_{n,t,y,m,h}
*          \Big) \cdot \text{ACT_LO}_{n,t,y,h} \bigg) \\
*      & + \sum_{\substack{\widehat{e},\widehat{t} \\ e \in E(\widehat{e})}}
*            \text{emission_scaling}_{\widehat{e},e} \cdot \ \text{emission_tax}_{n,\widehat{e},\widehat{t},y}
*            \cdot \text{EMISS}_{n,e,\widehat{t},y} \\
*      & + \sum_{s} \text{land_cost}_{n,s,y} \cdot \text{LAND}_{n,s,y} \\
*      & + \sum_{r} \text{relation_cost}_{r,n,y} \cdot \text{REL}_{r,n,y}
***

COST_ACCOUNTING_NODAL(node, year)..
    COST_NODAL(node, year) =E=
* resource extraction costs
    SUM((commodity,grade)$( map_resource(node,commodity,grade,year) ),
         resource_cost(node,commodity,grade,year) * EXT(node,commodity,grade,year) )
* technology capacity investment, maintainance, operational cost
    + SUM((tec)$( map_tec(node,tec,year) ),
            ( inv_cost(node,tec,year) * construction_time_factor(node,tec,year)
                * end_of_horizon_factor(node,tec,year) * CAP_NEW(node,tec,year)
            + SUM(vintage$( map_tec_lifetime(node,tec,vintage,year) ),
                fix_cost(node,tec,vintage,year) * CAP(node,tec,vintage,year) ) )$( inv_tec(tec) )
            + SUM((vintage,mode,time)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_act(node,tec,year,mode,time) ),
                var_cost(node,tec,vintage,year,mode,time) * ACT(node,tec,vintage,year,mode,time) )
            )
* additional cost terms (penalty) for relaxation of 'soft' dynamic new capacity constraints
    + SUM((inv_tec)$( map_tec(node,inv_tec,year) ),
        SUM((mode,time)$map_tec_act(node,inv_tec,year,mode,time),
            ( ( abs_cost_new_capacity_soft_up(node,inv_tec,year)
                + level_cost_new_capacity_soft_up(node,inv_tec,year) * inv_cost(node,inv_tec,year)
                ) * CAP_NEW_UP(node,inv_tec,year) )$( soft_new_capacity_up(node,inv_tec,year) )
            + ( ( abs_cost_new_capacity_soft_lo(node,inv_tec,year)
                + level_cost_new_capacity_soft_lo(node,inv_tec,year) * inv_cost(node,inv_tec,year)
                ) * CAP_NEW_LO(node,inv_tec,year) )$( soft_new_capacity_lo(node,inv_tec,year) )
            )
        )
* additional cost terms (penalty) for relaxation of 'soft' dynamic activity constraints
    + SUM((tec)$( map_tec(node,tec,year) ),
        SUM(time$( map_tec_time(node,tec,year,time) ),
            ( ( abs_cost_activity_soft_up(node,tec,year,time)
                + level_cost_activity_soft_up(node,tec,year,time) * levelized_cost(node,tec,year,time)
                ) * ACT_UP(node,tec,year,time) )$( soft_activity_up(node,tec,year,time) )
            + ( ( abs_cost_activity_soft_lo(node,tec,year,time)
                + level_cost_activity_soft_lo(node,tec,year,time)  * levelized_cost(node,tec,year,time)
                ) * ACT_LO(node,tec,year,time) )$( soft_activity_lo(node,tec,year,time) )
            )
        )
* emission taxes (by parent node, type of technology, type of year and type of emission)
    + SUM((type_emission,emission,type_tec,type_year)$( emission_scaling(type_emission,emission)
            AND cat_year(type_year,year) ),
        emission_scaling(type_emission,emission)
        * tax_emission(node,type_emission,type_tec,type_year)
        * EMISS(node,emission,type_tec,year) )
* cost terms from land-use model emulator (only includes valid node-land_scenario-year combinations)
    + SUM(land_scenario$( land_cost(node,land_scenario,year) ),
        land_cost(node,land_scenario,year) * LAND(node,land_scenario,year) )
* cost terms associated with linear relations
    + SUM(relation$( relation_cost(relation,node,year) ),
        relation_cost(relation,node,year) * REL(relation,node,year) )
* implementation of slack variables for constraints to aid in debugging
    + SUM((commodity,level,time)$( map_commodity(node,commodity,level,year,time) ), ( 0
%SLACK_COMMODITY_EQUIVALENCE%   + SLACK_COMMODITY_EQUIVALENCE_UP(node,commodity,level,year,time)
%SLACK_COMMODITY_EQUIVALENCE%   + SLACK_COMMODITY_EQUIVALENCE_LO(node,commodity,level,year,time)
        ) * 1e6 )
    + SUM((tec)$( map_tec(node,tec,year) ), ( 0
%SLACK_CAP_NEW_BOUND_UP%    + 10 * SLACK_CAP_NEW_BOUND_UP(node,tec,year)
%SLACK_CAP_NEW_BOUND_LO%    + 10 * SLACK_CAP_NEW_BOUND_LO(node,tec,year)
%SLACK_CAP_NEW_DYNAMIC_UP%  + 10 * SLACK_CAP_NEW_DYNAMIC_UP(node,tec,year)
%SLACK_CAP_NEW_DYNAMIC_LO%  + 10 * SLACK_CAP_NEW_DYNAMIC_LO(node,tec,year)
%SLACK_CAP_TOTAL_BOUND_UP%  + 10 * SLACK_CAP_TOTAL_BOUND_UP(node,tec,year)
%SLACK_CAP_TOTAL_BOUND_LO%  + 10 * SLACK_CAP_TOTAL_BOUND_LO(node,tec,year)
        ) * ABS( 1000 + inv_cost(node,tec,year) ) )
    + SUM((tec,time)$( map_tec_time(node,tec,year,time) ), ( 0
%SLACK_ACT_BOUND_UP%   + 10 * SUM(mode$( map_tec_act(node,tec,year,mode,time) ), SLACK_ACT_BOUND_UP(node,tec,year,mode,time) )
%SLACK_ACT_BOUND_LO%   + 10 * SUM(mode$( map_tec_act(node,tec,year,mode,time) ), SLACK_ACT_BOUND_LO(node,tec,year,mode,time) )
%SLACK_ACT_DYNAMIC_UP% + 10 * SLACK_ACT_DYNAMIC_UP(node,tec,year,time)
%SLACK_ACT_DYNAMIC_LO% + 10 * SLACK_ACT_DYNAMIC_LO(node,tec,year,time)
        ) * ( 1e8
            + ABS( SUM(mode$map_tec_act(node,tec,year,mode,time), var_cost(node,tec,year,year,mode,time) ) )
            + fix_cost(node,tec,year,year) ) )
    + SUM(land_scenario, 0
%SLACK_LAND_SCEN_UP% + 1e6 * SLACK_LAND_SCEN_UP(node,land_scenario,year)
%SLACK_LAND_SCEN_LO% + 1e6 * SLACK_LAND_SCEN_LO(node,land_scenario,year)
        )
    + SUM(land_type, 0
%SLACK_LAND_TYPE_UP% + 1e6 * SLACK_LAND_TYPE_UP(node,year,land_type)
%SLACK_LAND_TYPE_LO% + 1e6 * SLACK_LAND_TYPE_LO(node,year,land_type)
        )
    + SUM((relation), 0
%SLACK_RELATION_BOUND_UP% + 1e6 * SLACK_RELATION_BOUND_UP(relation,node,year)$( is_relation_upper(relation,node,year) )
%SLACK_RELATION_BOUND_LO% + 1e6 * SLACK_RELATION_BOUND_LO(relation,node,year)$( is_relation_lower(relation,node,year) )
        )
;

***
* Here, :math:`n^L \in N(n)` are all nodes :math:`n^L` that are sub-nodes of node :math:`n`.
* The subset of technologies :math:`t \in T(\widehat{t})` are all tecs that belong to category :math:`\widehat{t}`,
* and similar notation is used for emissions :math:`e \in E`.
***

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_resource_commodity:
*
* Resource and commodity section
* ------------------------------
*
* Constraints on resource extraction
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _extraction_equivalence:
*
* Equation EXTRACTION_EQUIVALENCE
* """""""""""""""""""""""""""""""
*
* This constraint translates the quantity of resources extracted (summed over all grades) to the input used by
* all technologies (drawing from that node). It is introduced to simplify subsequent notation in input/output relations
* and nodal balance constraints.
*
*  .. math::
*     \sum_{g} \text{EXT}_{n,c,g,y} =
*     \sum_{\substack{n^L,t,m,h,h^{\text{OD}} \\ y^V \leq y  \\ \ l \in L^{\text{RES}} \subseteq L }}
*         \text{input}_{n^L,t,y^V,y,m,n,c,l,h,h^{\text{OD}}} \cdot \text{ACT}_{n^L,t,m,y,h}
*
* The set :math:`L^{\text{RES}} \subseteq L` denotes all levels for which the detailed representation of resources applies.
***
EXTRACTION_EQUIVALENCE(node,commodity,year)..
    SUM(grade$( map_resource(node,commodity,grade,year) ), EXT(node,commodity,grade,year) )
    =G= SUM((location,tec,vintage,mode,level_resource,time_act,time_od)$( map_tec_act(node,tec,year,mode,time_act)
            AND map_tec_lifetime(node,tec,vintage,year) ),
        input(location,tec,vintage,year,mode,node,commodity,level_resource,time_act,time_od)
        * ACT(location,tec,vintage,year,mode,time_act) ) ;

***
* .. _equation_extraction_bound_up:
*
* Equation EXTRACTION_BOUND_UP
* """"""""""""""""""""""""""""
*
* This constraint specifies an upper bound on resource extraction by grade.
*
*  .. math::
*     \text{EXT}_{n,c,g,y} \leq \text{bound_extraction_up}_{n,c,g,y}
*
***
EXTRACTION_BOUND_UP(node,commodity,grade,year)$( map_resource(node,commodity,grade,year)
        AND is_bound_extraction_up(node,commodity,grade,year) )..
    EXT(node,commodity,grade,year) =L= bound_extraction_up(node,commodity,grade,year) ;

***
* .. _equation_resource_constraint:
*
* Equation RESOURCE_CONSTRAINT
* """"""""""""""""""""""""""""
*
* This constraint restricts that resource extraction in a year guarantees the "remaining resources" constraint,
* i.e., only a given fraction of remaining resources can be extracted per year.
*
*  .. math::
*     \text{EXT}_{n,c,g,y} \leq
*     \text{resource_remaining}_{n,c,g,y} \cdot
*         \Big( & \text{resource_volume}_{n,c,g} \\
*               & - \sum_{y' < y} \text{duration_period}_{y'} \cdot \text{EXT}_{n,c,g,y'} \Big)
*
***
RESOURCE_CONSTRAINT(node,commodity,grade,year)$( map_resource(node,commodity,grade,year)
        AND resource_remaining(node,commodity,grade,year) )..
* extraction per year
    EXT(node,commodity,grade,year) =L=
* remaining resources multiplied by remaining-resources-factor
    resource_remaining(node,commodity,grade,year)
    * ( resource_volume(node,commodity,grade)
        - SUM(year2$( year_order(year2) < year_order(year) ),
            duration_period(year2) * EXT(node,commodity,grade,year2) ) ) ;

***
* .. _equation_resource_horizon:
*
* Equation RESOURCE_HORIZON
* """""""""""""""""""""""""
* This constraint ensures that total resource extraction over the model horizon does not exceed the available resources.
*
*  .. math::
*     \sum_{y} \text{duration_period}_{y} \cdot \text{EXT}_{n,c,g,y} \leq  \text{resource_volume}_{n,c,g}
*
***
RESOURCE_HORIZON(node,commodity,grade)$( SUM(year$map_resource(node,commodity,grade,year), 1 ) )..
    SUM(year, duration_period(year) * EXT(node,commodity,grade,year) ) =L= resource_volume(node,commodity,grade) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* Constraints on commodities and stocks
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _commodity_balance:
*
* Auxiliary COMMODITY_BALANCE
* """""""""""""""""""""""""""
* For the commodity balance constraints below, we introduce an auxiliary variable called :math:`\text{COMMODITY_BALANCE}`. This is implemented
* as a GAMS ``$macro`` function.
*
*  .. math::
*     \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h}
*         \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A} & \\
*     - \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h}
*         \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,m,y,h^A} & \\
*     + \ \text{STOCK_CHG}_{n,c,l,y,h} + \ \sum_s \Big( \text{land_output}_{n,s,y,c,l,h} - \text{land_input}_{n,s,y,c,l,h} \Big) \cdot & \text{LAND}_{n,s,y} \\[4pt]
*     - \ \text{demand_fixed}_{n,c,l,y,h}
*     = \text{COMMODITY_BALANCE}_{n,c,l,y,h} \quad \forall \ l \notin (L^{\text{RES}}, & L^{\text{REN}}, L^{\text{STOR}} \subseteq L)
*
* The commodity balance constraint at the resource level is included in the `Equation RESOURCE_CONSTRAINT`_,
* while at the renewable level, it is included in the `Equation RENEWABLES_EQUIVALENCE`_,
* and at the storage level, it is included in the `Equation STORAGE_BALANCE`_.
***
$macro COMMODITY_BALANCE(node,commodity,level,year,time) (                                                             \
    SUM( (location,tec,vintage,mode,time2)$( map_tec_act(location,tec,year,mode,time2)                                 \
            AND map_tec_lifetime(location,tec,vintage,year) ),                                                         \
* import into node and output by all technologies located at 'location' sending to 'node' and 'time2' sending to 'time'
        output(location,tec,vintage,year,mode,node,commodity,level,time2,time)                                         \
        * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode,time2)                                    \
* export from node and input into technologies located at 'location' taking from 'node' and 'time2' taking from 'time'
        - input(location,tec,vintage,year,mode,node,commodity,level,time2,time)                                        \
        * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode,time2) )                                  \
* quantity taken out from ( >0 ) or put into ( <0 ) inter-period stock (storage)
    + STOCK_CHG(node,commodity,level,year,time)$( map_stocks(node,commodity,level,year) )                              \
* yield from land-use model emulator
    + SUM(land_scenario,                                                                                               \
        ( land_output(node,land_scenario,year,commodity,level,time)                                                    \
          - land_input(node,land_scenario,year,commodity,level,time) ) * LAND(node,land_scenario,year) )               \
* final demand (exogenous parameter to be satisfied by the commodity system)
    - demand_fixed(node,commodity,level,year,time)                                                                     \
    )$( map_commodity(node,commodity,level,year,time) AND NOT level_resource(level) AND NOT level_renewable(level) )

***
* .. _commodity_balance_gt:
*
* Equation COMMODITY_BALANCE_GT
* """""""""""""""""""""""""""""
* This constraint ensures that supply is greater or equal than demand for every commodity-level combination.
*
*  .. math::
*     \text{COMMODITY_BALANCE}_{n,c,l,y,h} \geq 0
*
***
COMMODITY_BALANCE_GT(node,commodity,level,year,time)$( map_commodity(node,commodity,level,year,time)
        AND NOT level_resource(level) AND NOT level_renewable(level) AND NOT level_storage(level) )..
    COMMODITY_BALANCE(node,commodity,level,year,time)
* relaxation of constraints for debugging
%SLACK_COMMODITY_EQUIVALENCE% + SLACK_COMMODITY_EQUIVALENCE_UP(node,commodity,level,year,time)
     =G= 0 ;

***
* .. _commodity_balance_lt:
*
* Equation COMMODITY_BALANCE_LT
* """""""""""""""""""""""""""""
* This constraint ensures that the supply is smaller than or equal to the demand for all commodity-level combinations
* given in the :math:`\text{balance_equality}_{c,l}`. In combination with the constraint above, it ensures that supply
* is (exactly) equal to demand.
*
*  .. math::
*     \text{COMMODITY_BALANCE}_{n,c,l,y,h} \leq 0
*
***
COMMODITY_BALANCE_LT(node,commodity,level,year,time)$( map_commodity(node,commodity,level,year,time)
        AND NOT level_resource(level) AND NOT level_renewable(level) AND NOT level_storage(level)
        AND balance_equality(commodity,level) )..
    COMMODITY_BALANCE(node,commodity,level,year,time)
* relaxation of constraints for debugging
%SLACK_COMMODITY_EQUIVALENCE% - SLACK_COMMODITY_EQUIVALENCE_LO(node,commodity,level,year,time)
    =L= 0 ;

***
* .. equation_stock_balance:
*
* Equation STOCKS_BALANCE
* """""""""""""""""""""""
* This constraint ensures the inter-temporal balance of commodity stocks.
* The parameter :math:`\text{commodity_stocks}_{n,c,l}` can be used to model exogenous additions to the stock
*
*  .. math::
*     \text{STOCK}_{n,c,l,y} + \text{commodity_stock}_{n,c,l,y} =
*         \text{duration_period}_{y} \cdot & \sum_{h} \text{STOCK_CHG}_{n,c,l,y,h} \\
*                                    & + \text{STOCK}_{n,c,l,y+1}
*
***
STOCKS_BALANCE(node,commodity,level,year)$( map_stocks(node,commodity,level,year) )..
    STOCK(node,commodity,level,year)$( NOT first_period(year) )
    + commodity_stock(node,commodity,level,year) =E=
    duration_period(year) * SUM(time$( map_commodity(node,commodity,level,year,time) ),
         STOCK_CHG(node,commodity,level,year,time) )
    + SUM(year2$( seq_period(year,year2) ), STOCK(node,commodity,level,year2) ) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_technology:
*
* Technology section
* ------------------
*
* Technical and engineering constraints
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The first set of constraints concern technologies that have explicit investment decisions
* and where installed/maintained capacity is relevant for operational decisions.
* The set where :math:`T^{\text{INV}} \subseteq T` is the set of all these technologies.

*
* .. _equation_capacity_constraint:
*
* Equation CAPACITY_CONSTRAINT
* """"""""""""""""""""""""""""
* This constraint ensures that the actual activity of a technology at a node cannot exceed available (maintained)
* capacity summed over all vintages, including the technology capacity factor :math:`\text{capacity_factor}_{n,t,y,t}`.
*
*  .. math::
*     \sum_{m} \text{ACT}_{n,t,y^V,y,m,h}
*         \leq \text{duration_time}_{h} \cdot \text{capacity_factor}_{n,t,y^V,y,h} \cdot \text{CAP}_{n,t,y^V,y}
*         \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
CAPACITY_CONSTRAINT(node,inv_tec,vintage,year,time)$( map_tec_time(node,inv_tec,year,time)
        AND map_tec_lifetime(node,inv_tec,vintage,year) )..
    SUM(mode$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) )
        =L= duration_time(time) * capacity_factor(node,inv_tec,vintage,year,time) * CAP(node,inv_tec,vintage,year) ;

***
* .. _equation_capacity_maintenance_hist:
*
* Equation CAPACITY_MAINTENANCE_HIST
* """"""""""""""""""""""""""""""""""
* The following three constraints implement technology capacity maintenance over time to allow early retirement.
* The optimization problem determines the optimal timing of retirement, when fixed operation-and-maintenance costs
* exceed the benefit in the objective function.
*
* The first constraint ensures that historical capacity (built prior to the model horizon) is available
* as installed capacity in the first model period.
*
*   .. math::
*      \text{CAP}_{n,t,y^V,\text{'first_period'}} & \leq
*          \text{remaining_capacity}_{n,t,y^V,\text{'first_period'}} \cdot
*          \text{duration_period}_{y^V} \cdot
*          \text{historical_new_capacity}_{n,t,y^V} \\
*      & \text{if } y^V  < \text{'first_period'} \text{ and } |y| - |y^V| < \text{technical_lifetime}_{n,t,y^V}
*      \quad \forall \ t \in T^{\text{INV}}
*
***
CAPACITY_MAINTENANCE_HIST(node,inv_tec,vintage,first_period)$( map_tec_lifetime(node,inv_tec,vintage,first_period)
        AND historical(vintage))..
    CAP(node,inv_tec,vintage,first_period)
    =L= remaining_capacity(node,inv_tec,vintage,first_period) *
        duration_period(vintage) * historical_new_capacity(node,inv_tec,vintage) ;

***
* .. _equation_capacity_maintenance_new:
*
* Equation CAPACITY_MAINTENANCE_NEW
* """""""""""""""""""""""""""""""""
* The second constraint ensures that capacity is fully maintained throughout the model period
* in which it was constructed (no early retirement in the period of construction).
*
*   .. math::
*      \text{CAP}_{n,t,y^V,y^V} =
*          \text{remaining_capacity}_{n,t,y^V,y^V} \cdot
*          \text{duration_period}_{y^V} \cdot
*          \text{CAP_NEW}_{n,t,y^V}
*      \quad \forall \ t \in T^{\text{INV}}
*
* The current formulation does not account for construction time in the constraints, but only adds a mark-up
* to the investment costs in the objective function.
***
CAPACITY_MAINTENANCE_NEW(node,inv_tec,vintage,vintage)$( map_tec_lifetime(node,inv_tec,vintage,vintage) )..
    CAP(node,inv_tec,vintage,vintage)
    =E= remaining_capacity(node,inv_tec,vintage,vintage)
        * duration_period(vintage) * CAP_NEW(node,inv_tec,vintage) ;

***
* .. _equation_capacity_maintenance:
*
* Equation CAPACITY_MAINTENANCE
* """""""""""""""""""""""""""""
* The third constraint implements the dynamics of capacity maintenance throughout the model horizon.
* Installed capacity can be maintained over time until decommissioning, which is irreversible.
*
*   .. math::
*      \text{CAP}_{n,t,y^V,y} & \leq
*          \text{remaining_capacity}_{n,t,y^V,y} \cdot
*          \text{CAP}_{n,t,y^V,y-1} \\
*      \quad & \text{if } y > y^V \text{ and } y^V  > \text{'first_period'} \text{ and } |y| - |y^V| < \text{technical_lifetime}_{n,t,y^V}
*      \quad \forall \ t \in T^{\text{INV}}
*
***
CAPACITY_MAINTENANCE(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year)
        AND NOT first_period(year) AND year_order(vintage) < year_order(year))..
    CAP(node,inv_tec,vintage,year)
    =L= remaining_capacity(node,inv_tec,vintage,year) *
        ( SUM(year2$( seq_period(year2,year) ),
              CAP(node,inv_tec,vintage,year2) ) ) ;

***
* .. _equation_operation_constraint:
*
* Equation OPERATION_CONSTRAINT
* """""""""""""""""""""""""""""
* This constraint provides an upper bound on the total operation of installed capacity over a year.
* It can be used to represent reuqired scheduled unavailability of installed capacity.
*
*   .. math::
*      \sum_{m,h} \text{ACT}_{n,t,y^V,y,m,h}
*          \leq \text{operation_factor}_{n,t,y^V,y} \cdot \text{capacity_factor}_{n,t,y^V,y,m,\text{'year'}} \cdot \text{CAP}_{n,t,y^V,y}
*      \quad \forall \ t \in T^{\text{INV}}
*
* This constraint is only active if :math:`\text{operation_factor}_{n,t,y^V,y} < 1`.
***
OPERATION_CONSTRAINT(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year)
        AND operation_factor(node,inv_tec,vintage,year) < 1 )..
    SUM((mode,time)$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) ) =L=
        operation_factor(node,inv_tec,vintage,year) * capacity_factor(node,inv_tec,vintage,year,'year')
        * CAP(node,inv_tec,vintage,year) ;

***
* .. _equation_min_utlitation_constraint:
*
* Equation MIN_UTILIZATION_CONSTRAINT
* """""""""""""""""""""""""""""""""""
* This constraint provides a lower bound on the total utilization of installed capacity over a year.
*
*   .. math::
*      \sum_{m,h} \text{ACT}_{n,t,y^V,y,m,h} \geq \text{min_utilization_factor}_{n,t,y^V,y} \cdot \text{CAP}_{n,t,y^V,y}
*      \quad \forall \ t \in T^{\text{INV}}
*
* This constraint is only active if :math:`\text{min_utilization_factor}_{n,t,y^V,y}` is defined.
***
MIN_UTILIZATION_CONSTRAINT(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year)
        AND min_utilization_factor(node,inv_tec,vintage,year) )..
    SUM((mode,time)$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) ) =G=
        min_utilization_factor(node,inv_tec,vintage,year) * CAP(node,inv_tec,vintage,year) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_renewable_integration:
*
* Constraints representing renewable integration
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_renewables_equivalence:
*
* Equation RENEWABLES_EQUIVALENCE
* """""""""""""""""""""""""""""""
* This constraint defines the auxiliary variables :math:`\text{REN}`
* to be equal to the output of renewable technologies (summed over grades).
*
*  .. math::
*     \sum_{g} \text{REN}_{n,t,c,g,y,h} \leq
*     \sum_{\substack{n,t,m,l,h,h^{\text{OD}} \\ y^V \leq y  \\ \ l \in L^{\text{REN}} \subseteq L }}
*         \text{input}_{n^L,t,y^V,y,m,n,c,l,h,h^{\text{OD}}} \cdot \text{ACT}_{n^L,t,m,y,h}
*
* The set :math:`L^{\text{REN}} \subseteq L` denotes all levels for which the detailed representation of renewables applies.
***
RENEWABLES_EQUIVALENCE(node,renewable_tec,commodity,year,time)$(
        map_tec(node,renewable_tec,year) AND map_ren_com(node,renewable_tec,commodity,year) )..
    SUM(grade$( map_ren_grade(node,commodity,grade,year) ), REN(node,renewable_tec,commodity,grade,year,time) )
    =E= SUM((location,vintage,mode,level_renewable,time_act)$(
                 map_tec_act(node,renewable_tec,year,mode,time_act)
                 AND map_tec_lifetime(node,renewable_tec,vintage,year) ),
        input(location,renewable_tec,vintage,year,mode,node,commodity,level_renewable,time_act,time)
        * ACT(location,renewable_tec,vintage,year,mode,time_act) ) ;

***
* .. _equation_renewables_potential_constraint:
*
* Equation RENEWABLES_POTENTIAL_CONSTRAINT
* """"""""""""""""""""""""""""""""""""""""
* This constraint sets the potential potential by grade as the upper bound for the auxiliary variable :math:`REN`.
*
*  .. math::
*     \sum_{\substack{t,h \\ \ t \in T^{R} \subseteq t }} \text{REN}_{n,t,c,g,y,h}
*         \leq \sum_{\substack{l \\ l \in L^{R} \subseteq L }} \text{renewable_potential}_{n,c,g,l,y}
*
***
RENEWABLES_POTENTIAL_CONSTRAINT(node,commodity,grade,year)$( map_ren_grade(node,commodity,grade,year) )..
    SUM((renewable_tec,time)$( map_ren_com(node,renewable_tec,commodity,year) ),
        REN(node,renewable_tec,commodity,grade,year,time) )
    =L= SUM(level_renewable, renewable_potential(node,commodity,grade,level_renewable,year) ) ;

***
* .. _equation_renewables_capacity_requirement:
*
* Equation RENEWABLES_CAPACITY_REQUIREMENT
* """"""""""""""""""""""""""""""""""""""""
* This constraint connects the capacity factor of a renewable grade to the
* installed capacity of a technology. It sets the lower limit for the capacity
* of a renewable technology to the summed activity over all grades (REN) devided
* by the capactiy factor of this grade.
* It represents the fact that different renewable grades require different installed
* capacities to provide their full potential.
*
*  .. math::
*     \sum_{y^V, h} & \text{CAP}_{n,t,y^V,y} \cdot \text{operation_factor}_{n,t,y^V,y} \cdot \text{capacity_factor}_{n,t,y^V,y,h} \\
*        & \quad \geq \sum_{g,h,l} \frac{1}{\text{renewable_capacity_factor}_{n,c,g,l,y}} \cdot \text{REN}_{n,t,c,g,y,h}
*
* This constraint is only active if :math:`\text{renewable_capacity_factor}_{n,c,g,l,y}` is defined.
***
RENEWABLES_CAPACITY_REQUIREMENT(node,inv_tec,commodity,year)$(
        SUM( (vintage,mode,time,grade,level_renewable),
            map_tec_lifetime(node,inv_tec,vintage,year) AND map_tec_act(node,inv_tec,year,mode,time)
            AND map_ren_com(node,inv_tec,commodity,year)
            AND renewable_capacity_factor(node,commodity,grade,level_renewable,year) > 0 ) )..
    SUM( (vintage,time)$map_ren_com(node,inv_tec,commodity,year),
        CAP(node,inv_tec,vintage,year)
        * operation_factor(node,inv_tec,vintage,year)
        * capacity_factor(node,inv_tec,vintage,year,time) )
    =G= SUM((grade,time,level_renewable)$(renewable_capacity_factor(node,commodity,grade,level_renewable,year) > 0),
            REN(node,inv_tec,commodity,grade,year,time)
                 / renewable_capacity_factor(node,commodity,grade,level_renewable,year)) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_addon_technologies:
*
* Constraints for addon technologies
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_addon_activity_up:
*
* Equation ADDON_ACTIVITY_UP
* """"""""""""""""""""""""""
* This constraint provides an upper bound on the activity of an addon technology that can only be operated
* jointly with a parent technology (e.g., abatement option, SO2 scrubber, power plant cooling technology).
*
*   .. math::
*      \sum_{\substack{t^a, y^V \leq y}} \text{ACT}_{n,t^a,y^V,y,m,h}
*      \leq
*      \sum_{\substack{t, y^V \leq y}}
*          & \text{addon_up}_{n,t,y,m,h,\widehat{t^a}} \cdot
*          \text{addon_conversion}_{n,t,y^V,y,m,h,\widehat{t^a}} \\
*          & \cdot \text{ACT}_{n,t,y^V,y,m,h} \quad \forall \ t^a \in T^{A}
*
***
ADDON_ACTIVITY_UP(node,type_addon,year,mode,time)..
* activity of addon technology
    sum( (addon,vintage)$(
            cat_addon(type_addon,addon) AND
            map_tec_act(node,addon,year,mode,time) AND
            map_tec_lifetime(node,addon,vintage,year) ),
        ACT(node,addon,vintage,year,mode,time) )
    =L=
* activity of corresponding parent-technology multiplied by upper bound of share
      sum((tec,vintage)$(
          map_tec_addon(tec,type_addon) AND
          map_tec_act(node,tec,year,mode,time) AND
          map_tec_lifetime(node,tec,vintage,year)
      ),
          addon_up(node,tec,year,mode,time,type_addon)
          * addon_conversion(node,tec,vintage,year,mode,time,type_addon)
          * ACT(node,tec,vintage,year,mode,time) )
;

***
* .. _equation_addon_activity_lo:
*
* Equation ADDON_ACTIVITY_LO
* """"""""""""""""""""""""""
* This constraint provides a lower bound on the activity of an addon technology that has to be operated
* jointly with a parent technology (e.g., power plant cooling technology). The parameter `addon_lo` allows to define
* a minimum level of operation of addon technologies relative to the activity of the parent technology.
* If `addon_lo = 1`, this means that it is mandatory to operate the addon technology at the same level as the
* parent technology (i.e., full mitigation).
*
*   .. math::
*      \sum_{\substack{t^a, y^V \leq y}} \text{ACT}_{n,t^a,y^V,y,m,h}
*      \geq
*      \sum_{\substack{t, y^V \leq y}}
*          & \text{addon_lo}_{n,t,y,m,h,\widehat{t^a}} \cdot
*          \text{addon_conversion}_{n,t,y^V,y,m,h,\widehat{t^a}} \\
*          & \cdot \text{ACT}_{n,t,y^V,y,m,h} \quad \forall \ t^a \in T^{A}
*
***
ADDON_ACTIVITY_LO(node,type_addon,year,mode,time)..
* activity of addon technology
    sum( (addon,vintage)$(
            cat_addon(type_addon,addon) AND
            map_tec_act(node,addon,year,mode,time) AND
            map_tec_lifetime(node,addon,vintage,year) ),
        ACT(node,addon,vintage,year,mode,time) )
    =G=
* activity of corresponding parent-technology times lower bound of share
      sum((tec,vintage)$(
          map_tec_addon(tec,type_addon) AND
          map_tec_act(node,tec,year,mode,time) AND
          map_tec_lifetime(node,tec,vintage,year)
      ),
          addon_lo(node,tec,year,mode,time,type_addon)
          * addon_conversion(node,tec,vintage,year,mode,time,type_addon)
          * ACT(node,tec,vintage,year,mode,time) ) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_system_reliability:
*
* System reliability and flexibility requirements
* -----------------------------------------------
* This section followi allows to include system-wide reliability and flexility considerations.
* The current formulation is based on Sullivan et al., 2013 :cite:`Sullivan-2013`.
*
* Aggregate use of a commodity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The system reliability and flexibility constraints are implemented using an auxiliary variable representing
* the total use (i.e., input of each commodity per level).
*
* .. _equation_commodity_use_level:
*
* Equation COMMODITY_USE_LEVEL
* """"""""""""""""""""""""""""
* This constraint defines the auxiliary variable :math:`\text{COMMODITY_USE}_{n,c,l,y}`, which is used to define
* the rating bins and the peak-load that needs to be offset with firm (dispatchable) capacity.
*
*   .. math::
*      \text{COMMODITY_USE}_{n,c,l,y}
*      = & \sum_{n^L,t,y^V,m,h} \text{input}_{n^L,t,y^V,y,m,n,c,l,h,h} \\
*        & \quad    \cdot \text{duration_time_rel}_{h,h} \cdot \text{ACT}_{n^L,t,y^V,y,m,h}
*
* This constraint and the auxiliary variable is only active if :math:`\text{peak_load_factor}_{n,c,l,y,h}` or
* :math:`\text{flexibility_factor}_{n,t,y^V,y,m,c,l,h,r}` is defined.
***
COMMODITY_USE_LEVEL(node,commodity,level,year,time)$(
         peak_load_factor(node,commodity,level,year,time) OR
         SUM( (tec,vintage,mode,rating), flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating) ) )..
    COMMODITY_USE(node,commodity,level,year)
    =E=
    SUM( (location,tec,vintage,mode,time2)$( map_tec_act(location,tec,year,mode,time2)
                                             AND map_tec_lifetime(location,tec,vintage,year) ),
        input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time_rel(time,time2)
        * ACT(location,tec,vintage,year,mode,time2) ) ;

***
* .. _rating_bin:
*
* Auxilary variables for technology activity by "rating bins"
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The capacity and activity of certain (usually non-dispatchable) technologies
* can be assumed to only partially contribute to the system reliability and flexibility requirements.
*
* .. _equation_activity_rating_bin:
*
* Equation ACTIVITY_RATING_BIN
* """"""""""""""""""""""""""""
* The auxiliary variable for rating-specific activity of each technology cannot exceed
* the share of the rating bin in relation to the total commodity use.
*
* .. math::
*    \text{ACT_RATING}_{n,t,y^V,y,c,l,h,q}
*    \leq \text{rating_bin}_{n,t,y,c,l,h,q} \cdot \text{COMMODITY_USE}_{n,c,l,y}
*
***
ACTIVITY_BY_RATING(node,tec,year,commodity,level,time,rating)$(
         rating_bin(node,tec,year,commodity,level,time,rating) )..
   sum(vintage$( sum(mode,map_tec_act(node,tec,year,mode,time) ) AND map_tec_lifetime(node,tec,vintage,year) ),
            ACT_RATING(node,tec,vintage,year,commodity,level,time,rating) )
    =L= rating_bin(node,tec,year,commodity,level,time,rating) * COMMODITY_USE(node,commodity,level,year)
;

***
* .. _equation_activity_share_total:
*
* Equation ACTIVITY_SHARE_TOTAL
* """""""""""""""""""""""""""""
* The sum of the auxiliary rating-specific activity variables need to equal the total input and/or output
* of the technology.
*
* .. math::
*    \sum_q \text{ACT_RATING}_{n,t,y^V,y,c,l,h,q}
*    = \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
*         ( \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad    \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A} \\
*
***
ACTIVITY_RATING_TOTAL(node,tec,vintage,year,commodity,level,time)$(
        sum(rating$( rating_bin(node,tec,year,commodity,level,time,rating) ), 1 )
        AND sum(mode, map_tec_act(node,tec,year,mode,time))
        AND map_tec_lifetime(node,tec,vintage,year) )..
    sum(rating$( rating_bin(node,tec,year,commodity,level,time,rating) ),
        ACT_RATING(node,tec,vintage,year,commodity,level,time,rating) )
    =E=
        SUM((location,mode,time2)$(
              map_tec_act(location,tec,year,mode,time2)
              AND map_tec_lifetime(location,tec,vintage,year) ),
            ( output(location,tec,vintage,year,mode,node,commodity,level,time2,time)
              + input(location,tec,vintage,year,mode,node,commodity,level,time2,time) )
                * duration_time_rel(time,time2)
                * ACT(location,tec,vintage,year,mode,time2) ) ;

***
* .. _reliability_constraint:
*
* Reliability of installed capacity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The "firm capacity" that a technology can contribute to system reliability depends on its dispatch characteristics.
* For dispatchable technologies, the total installed capacity counts toward the firm capacity constraint.
* This is active if the parameter is defined over :math:`\text{reliability_factor}_{n,t,y,c,l,h,\text{'firm'}}`.
* For non-dispatchable technologies, or those that do not have explicit investment decisions,
* the contribution to system reliability is calculated
* by using the auxiliary variable :math:`\text{ACT_RATING}_{n,t,y^V,y,c,l,h,q}` as a proxy,
* with the :math:`\text{reliability_factor}_{n,t,y,c,l,h,q}` defined per rating bin :math:`q`.
*
* .. _equation_firm_capacity_provision:
*
* Equation FIRM_CAPACITY_PROVISION
* """"""""""""""""""""""""""""""""
* Technologies where the reliability factor is defined with the rating `firm`
* have an auxiliary variable :math:`\text{CAP_FIRM}_{n,t,c,l,y}`, defined in terms of output.
*
*   .. math::
*      \text{CAP_FIRM}_{n,t,c,l,y}
*      = \sum_{y^V \leq y} & \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} \cdot \text{duration_time}_h \\
*        & \quad    \cdot \text{capacity_factor}_{n,t,y^V,y,h} \cdot \text{CAP}_{n,t,y^Y,y}
*      \quad \forall \ t \in T^{\text{INV}}
*
***
FIRM_CAPACITY_PROVISION(node,inv_tec,year,commodity,level,time)$(
        reliability_factor(node,inv_tec,year,commodity,level,time,'firm') )..
    CAP_FIRM(node,inv_tec,commodity,level,year) =E=
    SUM( (location,vintage,mode,time2)$(
           map_tec_act(location,inv_tec,year,mode,time2)
           AND map_tec_lifetime(location,inv_tec,vintage,year) ),
        output(location,inv_tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time(time)
        * capacity_factor(node,inv_tec,vintage,year,time)
        * CAP(node,inv_tec,vintage,year) ) ;

***
* .. _equation_system_reliability_constraint:
*
* Equation SYSTEM_RELIABILITY_CONSTRAINT
* """"""""""""""""""""""""""""""""""""""
* This constraint ensures that there is sufficient firm (dispatchable) capacity in each period.
* The formulation is based on Sullivan et al., 2013 :cite:`Sullivan-2013`.
*
*   .. math::
*      \sum_{t, q \substack{t \in T^{\text{INV}} \\ y^V \leq y} } &
*          \text{reliability_factor}_{n,t,y,c,l,h,\text{'firm'}}
*          \cdot \text{CAP_FIRM}_{n,t,c,l,y} \\
*      + \sum_{t,q,y^V \leq y} &
*          \text{reliability_factor}_{n,t,y,c,l,h,q}
*         \cdot \text{ACT_RATING}_{n,t,y^V,y,c,l,h,q} \\
*         & \quad \geq \text{peak_load_factor}_{n,c,l,y,h} \cdot \text{COMMODITY_USE}_{n,c,l,y}
*
* This constraint is only active if :math:`\text{peak_load_factor}_{n,c,l,y,h}` is defined.
***
SYSTEM_RELIABILITY_CONSTRAINT(node,commodity,level,year,time)$( peak_load_factor(node,commodity,level,year,time) )..
    SUM(inv_tec$( reliability_factor(node,inv_tec,year,commodity,level,time,'firm') ),
        reliability_factor(node,inv_tec,year,commodity,level,time,'firm')
        * CAP_FIRM(node,inv_tec,commodity,level,year) )
    + SUM((tec, mode, vintage, rating_unfirm)$(
        reliability_factor(node,tec,year,commodity,level,time,rating_unfirm)
            AND map_tec_act(node,tec,year,mode,time)
            AND map_tec_lifetime(node,tec,vintage,year) ),
        reliability_factor(node,tec,year,commodity,level,time,rating_unfirm)
        * ACT_RATING(node,tec,vintage,year,commodity,level,time,rating_unfirm) )
    =G= peak_load_factor(node,commodity,level,year,time) * COMMODITY_USE(node,commodity,level,year) ;

***
* .. _flexibility_constraint:
*
* Equation SYSTEM_FLEXIBILITY_CONSTRAINT
* """"""""""""""""""""""""""""""""""""""
* This constraint ensures that, in each sub-annual time slice, there is a sufficient
* contribution from flexible technologies to ensure smooth system operation.
*
*   .. math::
*      \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
*          \text{flexibility_factor}_{n^L,t,y^V,y,m,c,l,h,\text{'unrated'}} \\
*      & \quad   \cdot ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad   \cdot \text{duration_time_rel}_{h,h^A}
*                \cdot \text{ACT}_{n,t,y^V,y,m,h} \\
*      + \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
*         \text{flexibility_factor}_{n^L,t,y^V,y,m,c,l,h,1} \\
*      & \quad   \cdot ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad   \cdot \text{duration_time_rel}_{h,h^A}
*                \cdot \text{ACT_RATING}_{n,t,y^V,y,c,l,h,q}
*      \geq 0
*
***
SYSTEM_FLEXIBILITY_CONSTRAINT(node,commodity,level,year,time)$(
        SUM( (tec, vintage, mode, rating),
                flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating) ) )..
    SUM( (tec, vintage, mode)$( flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,'unrated') ),
        flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,'unrated')
        * SUM((location,time2)$(
              map_tec_act(location,tec,year,mode,time2)
              AND map_tec_lifetime(location,tec,vintage,year) ),
            ( output(location,tec,vintage,year,mode,node,commodity,level,time2,time)
              + input(location,tec,vintage,year,mode,node,commodity,level,time2,time) )
                * duration_time_rel(time,time2)
                * ACT(location,tec,vintage,year,mode,time2) ) )
    + SUM((tec, vintage, mode, rating_unrated)$(
            flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating_unrated)
            AND map_tec_act(node,tec,year,mode,time)
            AND map_tec_lifetime(node,tec,vintage,year)),
        flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating_unrated)
        * ACT_RATING(node,tec,vintage,year,commodity,level,time,rating_unrated) )
    =G= 0 ;

ACT.LO(node,tec,vintage,year,mode,time)$sum(
    (commodity,level,rating), flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating) ) = 0 ;

***
* .. _section_bounds_capacity_activity:
*
* Bounds on capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_new_capacity_bound_up:
*
* Equation NEW_CAPACITY_BOUND_UP
* """"""""""""""""""""""""""""""
* This constraint provides upper bounds on new capacity installation.
*
*   .. math::
*      \text{CAP_NEW}_{n,t,y} \leq \text{bound_new_capacity_up}_{n,t,y} \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
NEW_CAPACITY_BOUND_UP(node,inv_tec,year)$( is_bound_new_capacity_up(node,inv_tec,year) )..
    CAP_NEW(node,inv_tec,year) =L= bound_new_capacity_up(node,inv_tec,year)
%SLACK_CAP_NEW_BOUND_UP% + SLACK_CAP_NEW_BOUND_UP(node,inv_tec,year)
;

***
* .. _equation_new_capacity_bound_lo:
*
* Equation NEW_CAPACITY_BOUND_LO
* """"""""""""""""""""""""""""""
* This constraint provides lower bounds on new capacity installation.
*
*   .. math::
*      \text{CAP_NEW}_{n,t,y} \geq \text{bound_new_capacity_lo}_{n,t,y} \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
NEW_CAPACITY_BOUND_LO(node,inv_tec,year)$( is_bound_new_capacity_lo(node,inv_tec,year) )..
    CAP_NEW(node,inv_tec,year) =G= bound_new_capacity_lo(node,inv_tec,year)
%SLACK_CAP_NEW_BOUND_LO% - SLACK_CAP_NEW_BOUND_LO(node,inv_tec,year)
;

***
* .. _equation_total_capacity_bound_up:
*
* Equation TOTAL_CAPACITY_BOUND_UP
* """"""""""""""""""""""""""""""""
* This constraint gives upper bounds on the total installed capacity of a technology in a specific year of operation
* summed over all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} \text{CAP}_{n,t,y,y^V} \leq \text{bound_total_capacity_up}_{n,t,y} \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
TOTAL_CAPACITY_BOUND_UP(node,inv_tec,year)$( is_bound_total_capacity_up(node,inv_tec,year) )..
    SUM(vintage$( map_period(vintage,year) AND map_tec_lifetime(node,inv_tec,vintage,year) ),
        CAP(node,inv_tec,vintage,year) )
    =L= bound_total_capacity_up(node,inv_tec,year)
%SLACK_CAP_TOTAL_BOUND_UP% + SLACK_CAP_TOTAL_BOUND_UP(node,inv_tec,year)
;

***
* .. _equation_total_capacity_bound_lo:
*
* Equation TOTAL_CAPACITY_BOUND_LO
* """"""""""""""""""""""""""""""""
* This constraint gives lower bounds on the total installed capacity of a technology.
*
*   .. math::
*      \sum_{y^V \leq y} \text{CAP}_{n,t,y,y^V} \geq \text{bound_total_capacity_lo}_{n,t,y} \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
TOTAL_CAPACITY_BOUND_LO(node,inv_tec,year)$( is_bound_total_capacity_lo(node,inv_tec,year) )..
    SUM(vintage$( map_period(vintage,year) AND map_tec_lifetime(node,inv_tec,vintage,year) ),
        CAP(node,inv_tec,vintage,year) )
     =G= bound_total_capacity_lo(node,inv_tec,year)
%SLACK_CAP_TOTAL_BOUND_LO% - SLACK_CAP_TOTAL_BOUND_LO(node,inv_tec,year)
;

***
* .. _activity_bound_up:
*
* Equation ACTIVITY_BOUND_UP
* """"""""""""""""""""""""""
* This constraint provides upper bounds by mode of a technology activity, summed over all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} \text{ACT}_{n,t,y^V,y,m,h} \leq \text{bound_activity_up}_{n,t,m,y,h}
*
***
ACTIVITY_BOUND_UP(node,tec,year,mode,time)$(
    is_bound_activity_up(node,tec,year,mode,time) AND map_tec_act(node,tec,year,mode,time)
)..
    SUM(
        vintage$( map_tec_lifetime(node,tec,vintage,year) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =L=
    bound_activity_up(node,tec,year,mode,time)
%SLACK_ACT_BOUND_UP% + SLACK_ACT_BOUND_UP(node,tec,year,mode,time)
;

***
* .. _equation_activity_bound_all_modes_up:
*
* Equation ACTIVITY_BOUND_ALL_MODES_UP
* """"""""""""""""""""""""""""""""""""
* This constraint provides upper bounds of a technology activity across all modes and vintages.
*
*   .. math::
*      \sum_{y^V \leq y, m} \text{ACT}_{n,t,y^V,y,m,h} \leq \text{bound_activity_up}_{n,t,y,'all',h}
*
***
ACTIVITY_BOUND_ALL_MODES_UP(node,tec,year,time)$( is_bound_activity_up(node,tec,year,'all',time) )..
    SUM(
        (vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =L=
    bound_activity_up(node,tec,year,'all',time)
%SLACK_ACT_BOUND_UP% + SLACK_ACT_BOUND_UP(node,tec,year,'all',time)
;

***
* .. _activity_bound_lo:
*
* Equation ACTIVITY_BOUND_LO
* """"""""""""""""""""""""""
* This constraint provides lower bounds by mode of a technology activity, summed over
* all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} \text{ACT}_{n,t,y^V,y,m,h} \geq \text{bound_activity_lo}_{n,t,y,m,h}
*
* We assume that :math:`\text{bound_activity_lo}_{n,t,y,m,h} = 0`
* unless explicitly stated otherwise.
***
ACTIVITY_BOUND_LO(node,tec,year,mode,time)$( map_tec_act(node,tec,year,mode,time) )..
    SUM(
        vintage$( map_tec_lifetime(node,tec,vintage,year) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =G=
    bound_activity_lo(node,tec,year,mode,time)
%SLACK_ACT_BOUND_LO% - SLACK_ACT_BOUND_LO(node,tec,year,mode,time)
;

***
* .. _equation_activity_bound_all_modes_lo:
*
* Equation ACTIVITY_BOUND_ALL_MODES_LO
* """"""""""""""""""""""""""""""""""""
* This constraint provides lower bounds of a technology activity across all modes and vintages.
*
*   .. math::
*      \sum_{y^V \leq y, m} \text{ACT}_{n,t,y^V,y,m,h} \geq \text{bound_activity_lo}_{n,t,y,'all',h}
*
* We assume that :math:`\text{bound_activity_lo}_{n,t,y,'all',h} = 0`
* unless explicitly stated otherwise.
***
ACTIVITY_BOUND_ALL_MODES_LO(node,tec,year,time)$( bound_activity_lo(node,tec,year,'all',time) )..
    SUM(
        (vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =G=
    bound_activity_lo(node,tec,year,'all',time)
%SLACK_ACT_BOUND_LO% - SLACK_ACT_BOUND_LO(node,tec,year,'all',time)
;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _share_constraints:
*
* Constraints on shares of technologies and commodities
* -----------------------------------------------------
* This section allows to include upper and lower bounds on the shares of modes used by a technology
* or the shares of commodities produced or consumed by groups of technologies.
*
* Share constraints on activity by mode
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* .. _equation_shares_mode_up:
*
* Equation SHARES_MODE_UP
* """""""""""""""""""""""
* This constraint provides upper bounds of the share of the activity of one mode
* of a technology. For example, it could limit the share of heat that can be produced
* in a combined heat and electricity power plant.
*
*   .. math::
*     \text{ACT}_{n^L,t,y^V,y,m,h^A}
*     \leq \text{share_mode_up}_{p,n,t,y,m,h} \cdot
*     \sum_{m'} \text{ACT}_{n^L,t,y^V,y,m',h^A}
*
***
SHARE_CONSTRAINT_MODE_UP(shares,node,tec,mode,year,time)$(
    map_tec_act(node,tec,year,mode,time) AND
    share_mode_up(shares,node,tec,mode,year,time)
)..
* activity of mode to be constrained
    SUM(
        vintage$( map_tec_lifetime(node,tec,vintage,year) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =L=
    share_mode_up(shares,node,tec,mode,year,time) *
* activity aggregated over all modes
    SUM(
        (vintage,mode2)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode2) ),
        ACT(node,tec,vintage,year,mode2,time)
    ) ;

***
* .. _equation_shares_mode_lo:
*
* Equation SHARES_MODE_LO
* """""""""""""""""""""""
* This constraint provides lower bounds of the share of the activity of one mode of a technology.
*
*   .. math::
*     \text{ACT}_{n^L,t,y^V,y,m,h^A}
*     \geq \text{share_mode_lo}_{p,n,t,y,m,h} \cdot
*     \sum_{m'} \text{ACT}_{n^L,t,y^V,y,m',h^A}
*
***
SHARE_CONSTRAINT_MODE_LO(shares,node,tec,mode,year,time)$(
    map_tec_act(node,tec,year,mode,time) AND
    share_mode_lo(shares,node,tec,mode,year,time)
)..
* activity of mode to be constrained
    SUM(
        vintage$( map_tec_lifetime(node,tec,vintage,year) ),
        ACT(node,tec,vintage,year,mode,time)
    )
    =G=
    share_mode_lo(shares,node,tec,mode,year,time) *
* activity aggregated over all modes
    SUM(
        (vintage,mode2)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode2) ),
        ACT(node,tec,vintage,year,mode2,time)
    ) ;

***
* .. _section_share_constraints_commodities:
*
* Share constraints on commodities
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* These constraints allow to set upper and lower bound on the quantity of commodities produced or consumed by a group
* of technologies relative to the commodities produced or consumed by another group.
*
* The implementation is generic and flexible, so that any combination of commodities, levels, technologies and nodes
* can be put in relation to any other combination.
*
* The notation :math:`P^{\text{share}}` represents the mapping set `map_shares_commodity_share` denoting all technology types,
* nodes, commodities and levels to be included in the numerator, and :math:`P^{\text{total}}` is
* the equivalent mapping set `map_shares_commodity_total` for the denominator.
*
* .. _equation_share_constraint_commodity_up:
*
* Equation SHARE_CONSTRAINT_COMMODITY_UP
* """"""""""""""""""""""""""""""""""""""
*   .. math::
*      & \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim P^{\text{share}}}}
*         ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A} \\
*      & \geq
*        \text{share_commodity_up}_{p,n,y,h} \cdot
*        \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim P^{\text{total}}}}
*            ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A}
*
* This constraint is only active if :math:`\text{share_commodity_up}_{p,n,y,h}` is defined.
***
SHARE_CONSTRAINT_COMMODITY_UP(shares,node_share,year,time)$( share_commodity_up(shares,node_share,year,time) )..
* activity by type_tec_share technologies with map_shares_generic_share entries and a specific mode
    SUM( (node,location,type_tec_share,tec,vintage,mode,commodity,level,time2)$(
        ( map_shares_commodity_share(shares,node_share,node,type_tec_share,mode,commodity,level) OR
          map_shares_commodity_share(shares,node_share,node,type_tec_share,'all',commodity,level) ) AND
        cat_tec(type_tec_share,tec) AND
        map_tec_act(location,tec,year,mode,time2) AND
        map_tec_lifetime(location,tec,vintage,year)
    ),
        (
            output(location,tec,vintage,year,mode,node,commodity,level,time2,time) +
            input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        ) *
        duration_time_rel(time,time2) *
        ACT(location,tec,vintage,year,mode,time2)
    )
    =L=
    share_commodity_up(shares,node_share,year,time) * (
* total input and output by `type_tec_total` technologies mapped to respective commodity, level and node
    SUM( (node,location,type_tec_total,tec,vintage,mode,commodity,level,time2)$(
        ( map_shares_commodity_total(shares,node_share,node,type_tec_total,mode,commodity,level) OR
           map_shares_commodity_total(shares,node_share,node,type_tec_total,'all',commodity,level) ) AND
        cat_tec(type_tec_total,tec) AND
        map_tec_act(location,tec,year,mode,time2) AND
        map_tec_lifetime(location,tec,vintage,year)
    ),
        (
            output(location,tec,vintage,year,mode,node,commodity,level,time2,time) +
            input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        ) *
        duration_time_rel(time,time2) *
        ACT(location,tec,vintage,year,mode,time2)
    ) ) ;

***
* .. _equation_share_constraint_commodity_lo:
*
* Equation SHARE_CONSTRAINT_COMMODITY_LO
* """"""""""""""""""""""""""""""""""""""
*   .. math::
*      & \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim P^{\text{share}}}}
*         ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A} \\
*      & \leq
*        \text{share_commodity_lo}_{p,n,y,h} \cdot
*        \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim P^{\text{total}}}}
*            ( \text{output}_{n^L,t,y^V,y,m,n,c,l,h^A,h} + \text{input}_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
*      & \quad \cdot \text{duration_time_rel}_{h,h^A} \cdot \text{ACT}_{n^L,t,y^V,y,m,h^A}
*
* This constraint is only active if :math:`\text{share_commodity_lo}_{p,n,y,h}` is defined.
***
SHARE_CONSTRAINT_COMMODITY_LO(shares,node_share,year,time)$( share_commodity_lo(shares,node_share,year,time) )..
* total input and output by `type_tec_share` technologies mapped to respective commodity, level and node
    SUM( (node,location,type_tec_share,tec,vintage,mode,commodity,level,time2)$(
        ( map_shares_commodity_share(shares,node_share,node,type_tec_share,mode,commodity,level) OR
           map_shares_commodity_share(shares,node_share,node,type_tec_share,'all',commodity,level) ) AND
        cat_tec(type_tec_share,tec) AND
        map_tec_act(location,tec,year,mode,time2) AND
        map_tec_lifetime(location,tec,vintage,year)
    ),
        (
            output(location,tec,vintage,year,mode,node,commodity,level,time2,time) +
            input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        ) *
        duration_time_rel(time,time2) *
        ACT(location,tec,vintage,year,mode,time2)
    )
    =G=
    share_commodity_lo(shares,node_share,year,time) * (
* total input and output by `type_tec_total` technologies mapped to respective commodity, level and node
    SUM( (node,location,type_tec_total,tec,vintage,mode,commodity,level,time2)$(
        ( map_shares_commodity_total(shares,node_share,node,type_tec_total,mode,commodity,level) OR
           map_shares_commodity_total(shares,node_share,node,type_tec_total,'all',commodity,level) ) AND
        cat_tec(type_tec_total,tec) AND
        map_tec_act(location,tec,year,mode,time2) AND
        map_tec_lifetime(location,tec,vintage,year)
    ),
        (
            output(location,tec,vintage,year,mode,node,commodity,level,time2,time) +
            input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        ) *
        duration_time_rel(time,time2) *
        ACT(location,tec,vintage,year,mode,time2)
    ) ) ;

***
* .. _dynamic_constraints:
*
* Dynamic constraints on new capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* The constraints in this section specify dynamic upper and lower bounds on new capacity and activity.
* These can be used to model limits on market penetration and/or rates of expansion or phase-out of a technology.
*
* The formulation directly includes the option for 'soft' relaxations of dynamic constraints
* (cf. Keppo and Strubegger, 2010 :cite:`Keppo-2010`).
*
* See also the :ref:`corresponding parameter definitions <section_parameter_dynamic_constraints>`.
*
* .. _equation_new_capacity_constraint_up:
*
* Equation NEW_CAPACITY_CONSTRAINT_UP
* """""""""""""""""""""""""""""""""""
* The level of new capacity additions cannot be greater than an initial value (compounded over the period duration),
* annual growth of the existing 'capital stock', and a "soft" relaxation of the upper bound.
*
*  .. math::
*     gncu^1_{n,t,y} =
*       & \left( 1 + \text{growth_new_capacity_up}_{n,t,y} \right)^{|y|} \\
*     gncu^2_{n,t,y} =
*       & \frac{gncu^1_{n,t,y} -1 }{|y| \cdot \log{\left(1 + \text{growth_new_capacity_up}_{n,t,y} \right)}} \\
*     k^{gncu}_{n,t,y_a,y_b} =
*       & \frac{gncu^1_{n,t,y_a} \cdot gncu^2_{n,t,y_b}}{gncu^2_{n,t,y_a}} \\
*     \text{CAP_NEW}_{n,t,y} \leq
*       & \big(   \text{CAP_NEW}_{n,t,y_{-1}} + \text{historical_new_capacity}_{n,t,y_{-1}} \big. \\
*       & \big. + \text{initial_new_capacity_up}_{n,t,y} \big) \cdot k^{gncu}_{n,t,y_{-1},y} \\
*       & + \left(\text{CAP_NEW_UP}_{n,t,y} \cdot \left((1 + \text{soft_new_capacity_up}_{n,t,y})^{|y|} - 1 \right)\right) \\
*     \forall & \ t \ \in \ T^{\text{INV}}
*
* Here, :math:`|y|` is the number of years in period :math:`y`, i.e., :math:`\text{duration_period}_{y}`.
***

* Compute auxiliary values
gncu_1(n,t,y_all)$inv_tec(t) = POWER(1 + growth_new_capacity_up(n,t,y_all), duration_period(y_all));

gncu_2(n,t,y_all) = 1;
gncu_2(n,t,y_all)$growth_new_capacity_up(n,t,y_all) = (
  (gncu_1(n,t,y_all) - 1) / (duration_period(y_all) * LOG(1 + growth_new_capacity_up(n,t,y_all)))
);

* Ratio of CAP_NEW(n,t,y_all) to CAP_NEW(n,t,y_prev)
k_gncu(n,t,y_prev,y_all)$(
    seq_period(y_prev,y_all)
    # Same condition as the equation, below
    AND inv_tec(t) AND map_tec(n,t,y_all) AND is_dynamic_new_capacity_up(n,t,y_all)
) = gncu_1(n,t,y_prev) * gncu_2(n,t,y_all) / gncu_2(n,t,y_prev);

NEW_CAPACITY_CONSTRAINT_UP(n,t,y_)$(
    inv_tec(t) AND map_tec(n,t,y_) AND is_dynamic_new_capacity_up(n,t,y_)
)..
  CAP_NEW(n,t,y_)

  =L=

  # 'Hard' constraint value
  SUM(
    y_prev$seq_period(y_prev, y_),
    (
      # New capacity in previous model period
      CAP_NEW(n,t,y_prev)$(model_horizon(y_prev) AND map_tec(n,t,y_prev))

      # New capacity in previous historical period
      + historical_new_capacity(n,t,y_prev)

      # Otherwise, maximum initial value
      # FIXME Do not use this if any of the above are non-zero
      + initial_new_capacity_up(n,t,y_)
    )
    * k_gncu(n,t,y_prev,y_)
  )

  # 'Soft' relaxation of constraint
  + (
    CAP_NEW_UP(n,t,y_) * (POWER(1 + soft_new_capacity_up(n,t,y_), duration_period(y_)) - 1)
  )$soft_new_capacity_up(n,t,y_)

  # Additional relaxation for calibration and debugging
%SLACK_CAP_NEW_DYNAMIC_UP% + SLACK_CAP_NEW_DYNAMIC_UP(n,t,y_)
;

* GAMS implementation comment:
* The sums in the constraint have to be over `year_all2` (not `year2`) to also get the dynamic effect from historical
* new capacity. If one were to sum over `year2`, periods prior to the first model year would be ignored.
* Furthermore, as `CAP_NEW` is derived from the value in a previous period, any change in the duration of two consecutive
* model periods needs to be accounted for. This is done by using the ratio of two consecutive model periods as a
* multiplication factor.

***
* .. _equation_new_capacity_soft_constraint_up:
*
* Equation NEW_CAPACITY_SOFT_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic constraint on new capacity (investment) does not exceed
* the level of the investment in the previous period (cf. Keppo and Strubegger, 2010 :cite:`Keppo-2010`).
*
*   .. math::
*      \text{CAP_NEW_UP}_{n,t,y} \leq \sum_{y-1} \text{CAP_NEW}_{n^L,t,y-1} & \text{if } y \neq \text{'first_period'} \\
*                                + \sum_{y-1} \text{historical_new_capacity}_{n^L,t,y-1} & \text{if } y = \text{'first_period'} \\
*                           \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
NEW_CAPACITY_SOFT_CONSTRAINT_UP(node,inv_tec,year)$( soft_new_capacity_up(node,inv_tec,year) )..
    CAP_NEW_UP(node,inv_tec,year) =L=
        SUM(year2$( seq_period(year2,year) ),
            CAP_NEW(node,inv_tec,year2)) $ (NOT first_period(year))
      + SUM(year_all2$( seq_period(year_all2,year) ),
            historical_new_capacity(node,inv_tec,year_all2)) $ first_period(year)
;

***
* .. _equation_new_capacity_constraint_lo:
*
* Equation NEW_CAPACITY_CONSTRAINT_LO
* """""""""""""""""""""""""""""""""""
* This constraint gives dynamic lower bounds on new capacity.
*
*  .. math::
*     \text{CAP_NEW}_{n,t,y}
*         \geq & \Bigg(- \text{initial_new_capacity_lo}_{n,t,y}
*             \cdot \frac{ \Big( 1 + \text{growth_new_capacity_lo}_{n,t,y} \Big)^{|y|} }
*                        { \text{growth_new_capacity_lo}_{n,t,y} } \\
*              & + \Big( \text{CAP_NEW}_{n,t,y-1} + \text{historical_new_capacity}_{n,t,y-1} \Big) \\
*              & \hspace{2 cm} \cdot \Big( 1 + \text{growth_new_capacity_lo}_{n,t,y} \Big)^{|y|} \\
*              & - \text{CAP_NEW_LO}_{n,t,y} \cdot \Bigg( \Big( 1 + \text{soft_new_capacity_lo}_{n,t,y}\Big)^{|y|} - 1 \Bigg)\Bigg) \\
*              & * \frac{|y-1|}{|y|} \\
*         & \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
NEW_CAPACITY_CONSTRAINT_LO(node,inv_tec,year)$( map_tec(node,inv_tec,year)
        AND is_dynamic_new_capacity_lo(node,inv_tec,year) )..
* actual new capacity
    CAP_NEW(node,inv_tec,year) =G=
* initial new capacity (compounded over the duration of the period)
        (- initial_new_capacity_lo(node,inv_tec,year) * (
            ( ( POWER( 1 + growth_new_capacity_lo(node,inv_tec,year) , duration_period(year) ) - 1 )
                / growth_new_capacity_lo(node,inv_tec,year) )$( growth_new_capacity_lo(node,inv_tec,year) )
              + ( duration_period(year) )$( NOT growth_new_capacity_lo(node,inv_tec,year) )
            )
* growth of 'capital stock' from previous period
        + SUM(year_all2$( seq_period(year_all2,year) ),
                CAP_NEW(node,inv_tec,year_all2)$( map_tec(node,inv_tec,year_all2) AND model_horizon(year_all2) )
                + historical_new_capacity(node,inv_tec,year_all2)
                # placeholder for spillover across nodes, technologies, periods (other than immediate predecessor)
            ) * POWER( 1 + growth_new_capacity_lo(node,inv_tec,year) , duration_period(year) )
* 'soft' relaxation of dynamic constraints
        - ( CAP_NEW_LO(node,inv_tec,year)
            * ( POWER( 1 + soft_new_capacity_lo(node,inv_tec,year) , duration_period(year) ) - 1 )
           )$( soft_new_capacity_lo(node,inv_tec,year) ))
       * SUM(year_all2$( seq_period(year_all2,year) ),
            ( duration_period(year_all2) / duration_period(year) ))
* optional relaxation for calibration and debugging
%SLACK_CAP_NEW_DYNAMIC_LO% - SLACK_CAP_NEW_DYNAMIC_LO(node,inv_tec,year)
;

* GAMS implementation comment:
* The sums in the constraint have to be over `year_all2` (not `year2`) to also get the dynamic effect from historical
* new capacity. If one would sum over `year2`, periods prior to the first model year would be ignored.
* Furthermore, as `CAP_NEW` is derived from the value in a previous period, any change in the duration of two consecutive
* model periods needs to be accounted for. This is done by using the ratio of two consecutive model periods as a
* multiplication factor.

***
* .. _equation_new_capacity_soft_constraint_lo:
*
* Equation NEW_CAPACITY_SOFT_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic constraint on new capacity does not exceed
* level of the investment in the previous year.
*
*   .. math::
*      \text{CAP_NEW_LO}_{n,t,y} \leq \sum_{y-1} \text{CAP_NEW}_{n^L,t,y-1} & \text{if } y \neq \text{'first_period'} \\
*                                + \sum_{y-1} \text{historical_new_capacity}_{n^L,t,y-1} & \text{if } y = \text{'first_period'} \\
*                           \quad \forall \ t \ \in \ T^{\text{INV}}
*
***
NEW_CAPACITY_SOFT_CONSTRAINT_LO(node,inv_tec,year)$( soft_new_capacity_lo(node,inv_tec,year) )..
    CAP_NEW_LO(node,inv_tec,year) =L=
        SUM(year2$( seq_period(year2,year) ),
            CAP_NEW(node,inv_tec,year2) ) $ (NOT first_period(year))
      + SUM(year_all2$( seq_period(year_all2,year) ),
            historical_new_capacity(node,inv_tec,year_all2) ) $ first_period(year)
;

***
* .. _equation_activity_constraint_up:
*
* Equation ACTIVITY_CONSTRAINT_UP
* """""""""""""""""""""""""""""""
* This constraint gives dynamic upper bounds on the market penetration of a technology activity.
*
*  .. math::
*     \sum_{y^V \leq y,m} \text{ACT}_{n,t,y^V,y,m,h}
*         \leq & ~ \text{initial_activity_up}_{n,t,y,h}
*             \cdot \frac{ \Big( 1 + \text{growth_activity_up}_{n,t,y,h} \Big)^{|y|} - 1 }
*                        { \text{growth_activity_up}_{n,t,y,h} } \\
*             & + \bigg( \sum_{y^V \leq y-1,m} \text{ACT}_{n,t,y^V,y-1,m,h}
*                         + \sum_{m} \text{historical_activity}_{n,t,y-1,m,h} \bigg) \\
*             & \hspace{2 cm} \cdot \Big( 1 + \text{growth_activity_up}_{n,t,y,h} \Big)^{|y|} \\
*             & + \text{ACT_UP}_{n,t,y,h} \cdot \Bigg( \Big( 1 + \text{soft_activity_up}_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)
*
***
ACTIVITY_CONSTRAINT_UP(node,tec,year,time)$( map_tec_time(node,tec,year,time)
        AND is_dynamic_activity_up(node,tec,year,time) )..
* actual activity (summed over modes)
    SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode) ),
            ACT(node,tec,vintage,year,mode,time) ) =L=
* initial activity (compounded over the duration of the period)
        initial_activity_up(node,tec,year,time) * (
            ( ( POWER( 1 + growth_activity_up(node,tec,year,time) , duration_period(year) ) - 1 )
                / growth_activity_up(node,tec,year,time) )$( growth_activity_up(node,tec,year,time) )
              + ( duration_period(year) )$( NOT growth_activity_up(node,tec,year,time) )
            )
* growth of 'capital stock' from previous period
        + SUM((year_all2)$( seq_period(year_all2,year) ),
            SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year_all2) AND map_tec_mode(node,tec,year_all2,mode)
                                 AND model_horizon(year_all2) ),
                        ACT(node,tec,vintage,year_all2,mode,time) )
                + SUM(mode, historical_activity(node,tec,year_all2,mode,time) )
                # placeholder for spillover across nodes, technologies, periods (other than immediate predecessor)
                )
            * POWER( 1 + growth_activity_up(node,tec,year,time) , duration_period(year) )
* 'soft' relaxation of dynamic constraints
        + ( ACT_UP(node,tec,year,time)
                * ( POWER( 1 + soft_activity_up(node,tec,year,time) , duration_period(year) ) - 1 )
            )$( soft_activity_up(node,tec,year,time) )
* optional relaxation for calibration and debugging
%SLACK_ACT_DYNAMIC_UP% + SLACK_ACT_DYNAMIC_UP(node,tec,year,time)
;

***
* .. _equation_activity_soft_constraint_up:
*
* Equation ACTIVITY_SOFT_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
* level of the activity in the previous period.
*
*   .. math::
*      \text{ACT_UP}_{n,t,y,h} \leq \sum_{y^V \leq y,m,y-1} \text{ACT}_{n^L,t,y^V,y-1,m,h} & \text{if } y \neq \text{'first_period'} \\
*                             + \sum_{m,y-1} \text{historical_activity}_{n^L,t,y-1,m,h} & \text{if } y = \text{'first_period'}
*
*
***
ACTIVITY_SOFT_CONSTRAINT_UP(node,tec,year,time)$( soft_activity_up(node,tec,year,time) )..
    ACT_UP(node,tec,year,time) =L=
        SUM((vintage,mode,year2)$( map_tec_lifetime(node,tec,vintage,year2) AND map_tec_act(node,tec,year2,mode,time)
                                   AND seq_period(year2,year) ),
            ACT(node,tec,vintage,year2,mode,time) ) $ (NOT first_period(year))
      + SUM((mode,year_all2)$( seq_period(year_all2,year) ),
            historical_activity(node,tec,year_all2,mode,time) ) $ first_period(year)
;

***
* Equation ACTIVITY_CONSTRAINT_LO
* """""""""""""""""""""""""""""""
* This constraint gives dynamic lower bounds on the market penetration of a technology activity.
*
*  .. math::
*     \sum_{y^V \leq y,m} \text{ACT}_{n,t,y^V,y,m,h}
*         \geq & - \text{initial_activity_lo}_{n,t,y,h}
*             \cdot \frac{ \Big( 1 + \text{growth_activity_lo}_{n,t,y,h} \Big)^{|y|} - 1 }
*                        { \text{growth_activity_lo}_{n,t,y,h} } \\
*             & + \bigg( \sum_{y^V \leq y-1,m} \text{ACT}_{n,t,y^V,y-1,m,h}
*                         + \sum_{m} \text{historical_activity}_{n,t,y-1,m,h} \bigg) \\
*             & \hspace{2 cm} \cdot \Big( 1 + \text{growth_activity_lo}_{n,t,y,h} \Big)^{|y|} \\
*             & - \text{ACT_LO}_{n,t,y,h} \cdot \Bigg( \Big( 1 + \text{soft_activity_lo}_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)
*
***
ACTIVITY_CONSTRAINT_LO(node,tec,year,time)$( map_tec_time(node,tec,year,time)
        AND is_dynamic_activity_lo(node,tec,year,time) )..
* actual activity (summed over modes)
    SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_mode(node,tec,year,mode) ),
            ACT(node,tec,vintage,year,mode,time) ) =G=
* initial activity (compounded over the duration of the period)
        - initial_activity_lo(node,tec,year,time) * (
            ( ( POWER( 1 + growth_activity_lo(node,tec,year,time) , duration_period(year) ) - 1 )
                / growth_activity_lo(node,tec,year,time) )$( growth_activity_lo(node,tec,year,time) )
              + ( duration_period(year) )$( NOT growth_activity_lo(node,tec,year,time) )
            )
* growth of 'capital stock' from previous period
        + SUM((year_all2)$( seq_period(year_all2,year) ),
            SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year_all2) AND map_tec_mode(node,tec,year_all2,mode)
                                 AND model_horizon(year_all2)),
                        ACT(node,tec,vintage,year_all2,mode,time) )
                + SUM(mode, historical_activity(node,tec,year_all2,mode,time) )
                # placeholder for spillover across nodes, technologies, periods (other than immediate predecessor)
                )
            * POWER( 1 + growth_activity_lo(node,tec,year,time) , duration_period(year) )
* 'soft' relaxation of dynamic constraints
        - ( ACT_LO(node,tec,year,time)
            * ( POWER( 1 + soft_activity_lo(node,tec,year,time) , duration_period(year) ) - 1 )
            )$( soft_activity_lo(node,tec,year,time) )
* optional relaxation for calibration and debugging
%SLACK_ACT_DYNAMIC_LO% - SLACK_ACT_DYNAMIC_LO(node,tec,year,time)
;

***
* .. _equation_activity_soft_constraint_lo:
*
* Equation ACTIVITY_SOFT_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
* level of the activity in the previous period.
*
*   .. math::
*      \text{ACT_LO}_{n,t,y,h} \leq \sum_{y^V \leq y,m,y-1} \text{ACT}_{n^L,t,y^V,y-1,m,h} & \text{if } y \neq \text{'first_period'} \\
*                             + \sum_{m,y-1} \text{historical_activity}_{n^L,t,y-1,m,h} & \text{if } y = \text{'first_period'}
*
***
ACTIVITY_SOFT_CONSTRAINT_LO(node,tec,year,time)$( soft_activity_lo(node,tec,year,time) )..
    ACT_LO(node,tec,year,time) =L=
        SUM((vintage,mode,year2)$( map_tec_lifetime(node,tec,vintage,year2) AND map_tec_act(node,tec,year2,mode,time)
                                   AND seq_period(year2,year) ),
            ACT(node,tec,vintage,year2,mode,time) ) $ (NOT first_period(year))
      + SUM((mode,year_all2)$( seq_period(year_all2,year) ),
            historical_activity(node,tec,year_all2,mode,time) ) $ first_period(year)
;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_emission:
*
* Emission section
* ----------------
*
* Auxiliary variable for aggregate emissions
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_emission_equivalence:
*
* Equation EMISSION_EQUIVALENCE
* """""""""""""""""""""""""""""
* This constraint simplifies the notation of emissions aggregated over different technology types
* and the land-use model emulator. The formulation includes emissions from all sub-nodes :math:`n^L` of :math:`n`.
*
*   .. math::
*      \text{EMISS}_{n,e,\widehat{t},y} =
*          \sum_{n^L \in N(n)} \Bigg(
*              \sum_{t \in T(\widehat{t}),y^V \leq y,m,h }
*                  \text{emission_factor}_{n^L,t,y^V,y,m,e} \cdot \text{ACT}_{n^L,t,y^V,y,m,h} \\
*              + \sum_{s} \ \text{land_emission}_{n^L,s,y,e} \cdot \text{LAND}_{n^L,s,y}
*                   \text{ if } \widehat{t} \in \widehat{T}^{LAND} \Bigg)
*
* .. versionchanged:: v3.11.0
*
*    ``type_tec`` elements that appear in either of the :ref:`mapping sets <section_maps_def>`
*    ``map_shares_commodity_share`` or ``map_shares_commodity_total`` are excluded from this equation,
*    and thus also from the domain of the ``EMISS`` :ref:`variable <section_decision_variable_def>`.
***
EMISSION_EQUIVALENCE(node,emission,type_tec,year)$(
  NOT type_tec_share(type_tec) AND NOT type_tec_total(type_tec)
)..
    EMISS(node,emission,type_tec,year)
    =E=
    SUM(location$( map_node(node,location) ),
* emissions from technology activity
        SUM((tec,vintage,mode,time)$( cat_tec(type_tec,tec)
            AND map_tec_act(location,tec,year,mode,time) AND map_tec_lifetime(location,tec,vintage,year) ),
        emission_factor(location,tec,vintage,year,mode,emission) * ACT(location,tec,vintage,year,mode,time) )
* emissions from land use if 'type_tec' is included in the dynamic set 'type_tec_land'
        + SUM(land_scenario$( type_tec_land(type_tec) ),
            land_emission(location,land_scenario,year,emission) * LAND(location,land_scenario,year) )
      ) ;

***
* Bound on emissions
* ^^^^^^^^^^^^^^^^^^
*
* .. _emission_constraint:
*
* Equation EMISSION_CONSTRAINT
* """"""""""""""""""""""""""""
* This constraint enforces upper bounds on emissions (by emission type). For all bounds that include multiple periods,
* the parameter :math:`\text{bound_emission}_{n,\widehat{e},\widehat{t},\widehat{y}}` is scaled to represent average annual
* emissions over all years included in the year-set :math:`\widehat{y}`.
*
* The formulation includes historical emissions and allows to model constraints ranging over both the model horizon
* and historical periods.
*
*   .. math::
*      \frac{
*          \sum_{y' \in Y(\widehat{y}), e \in E(\widehat{e})}
*              \begin{array}{l}
*                  \text{duration_period}_{y'} \cdot \text{emission_scaling}_{\widehat{e},e} \cdot \\
*                  \Big( \text{EMISS}_{n,e,\widehat{t},y'} + \sum_{m} \text{historical_emission}_{n,e,\widehat{t},y'} \Big)
*              \end{array}
*          }
*        { \sum_{y' \in Y(\widehat{y})} \text{duration_period}_{y'} }
*      \leq \text{bound_emission}_{n,\widehat{e},\widehat{t},\widehat{y}}
*
***
EMISSION_CONSTRAINT(node,type_emission,type_tec,type_year)$is_bound_emission(node,type_emission,type_tec,type_year)..
    SUM( (year_all2,emission)$( cat_year(type_year,year_all2) AND cat_emission(type_emission,emission) ),
        duration_period(year_all2) * emission_scaling(type_emission,emission) *
            ( EMISS(node,emission,type_tec,year_all2)$( year(year_all2) )
                + historical_emission(node,emission,type_tec,year_all2) )
      )
    / SUM(year_all2$( cat_year(type_year,year_all2) ), duration_period(year_all2) )
    =L= bound_emission(node,type_emission,type_tec,type_year) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_landuse_emulator:
*
* Land-use model emulator section
* -------------------------------
*
* Bounds on total land use
* ^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_land_constraint:
*
* Equation LAND_CONSTRAINT
* """"""""""""""""""""""""
* This constraint enforces a meaningful result of the land-use model emulator,
* in particular a bound on the total land used in |MESSAGEix|.
* The linear combination of land scenarios must be equal to 1.
*
*  .. math::
*     \sum_{s \in S} \text{LAND}_{n,s,y} = 1
*
***
LAND_CONSTRAINT(node,year)$( SUM(land_scenario$( map_land(node,land_scenario,year) ), 1 ) ) ..
    SUM(land_scenario$( map_land(node,land_scenario,year) ), LAND(node,land_scenario,year) ) =E= 1 ;

***
* Dynamic constraints on land use
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* These constraints enforces upper and lower bounds on the change rate per land scenario.
*
* .. _equation_dynamic_land_scen_constraint_up:
*
* Equation DYNAMIC_LAND_SCEN_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \text{LAND}_{n,s,y}
*         \leq & \text{initial_land_scen_up}_{n,s,y}
*             \cdot \frac{ \Big( 1 + \text{growth_land_scen_up}_{n,s,y} \Big)^{|y|} - 1 }
*                        { \text{growth_land_scen_up}_{n,s,y} } \\
*              & + \big( \text{LAND}_{n,s,y-1} + \text{historical_land}_{n,s,y-1} \big)
*                  \cdot \Big( 1 + \text{growth_land_scen_up}_{n,s,y} \Big)^{|y|}
*
***
DYNAMIC_LAND_SCEN_CONSTRAINT_UP(node,land_scenario,year)$( map_land(node,land_scenario,year)
        AND is_dynamic_land_scen_up(node,land_scenario,year) )..
* share of land scenario in
    LAND(node,land_scenario,year) =L=
* initial 'new' land used for that type (compounded over the duration of the period)
        initial_land_scen_up(node,land_scenario,year) * (
            ( ( POWER( 1 + growth_land_scen_up(node,land_scenario,year) , duration_period(year) ) - 1 )
                / growth_land_scen_up(node,land_scenario,year) )$( growth_land_scen_up(node,land_scenario,year) )
              + ( duration_period(year) )$( NOT growth_land_scen_up(node,land_scenario,year) )
            )
* expansion of land scenario from previous period
        + SUM((year_all2)$( seq_period(year_all2,year) ),
                ( LAND(node,land_scenario,year_all2)$( model_horizon(year_all2) )
                  + historical_land(node,land_scenario,year_all2) )
                * POWER( 1 + growth_land_scen_up(node,land_scenario,year) , duration_period(year) )
            )
* optional relaxation for calibration and debugging
%SLACK_LAND_SCEN_UP% + SLACK_LAND_SCEN_UP(node,land_scenario,year)
;

***
* .. _equation_dynamic_land_scen_constraint_lo:
*
* Equation DYNAMIC_LAND_SCEN_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \text{LAND}_{n,s,y}
*         \geq & - \text{initial_land_scen_lo}_{n,s,y}
*             \cdot \frac{ \Big( 1 + \text{growth_land_scen_lo}_{n,s,y} \Big)^{|y|} - 1 }
*                        { \text{growth_land_scen_lo}_{n,s,y} } \\
*              & + \big( \text{LAND}_{n,s,y-1} + \text{historical_land}_{n,s,y-1} \big)
*                  \cdot \Big( 1 + \text{growth_land_scen_lo}_{n,s,y} \Big)^{|y|}
*
***
DYNAMIC_LAND_SCEN_CONSTRAINT_LO(node,land_scenario,year)$( map_land(node,land_scenario,year)
        AND is_dynamic_land_scen_lo(node,land_scenario,year) )..
* share of land scenario in
    LAND(node,land_scenario,year) =G=
* initial 'new' land used for that type (compounded over the duration of the period)
        - initial_land_scen_lo(node,land_scenario,year) * (
            ( ( POWER( 1 + growth_land_scen_lo(node,land_scenario,year) , duration_period(year) ) - 1 )
                / growth_land_scen_lo(node,land_scenario,year) )$( growth_land_scen_lo(node,land_scenario,year) )
              + ( duration_period(year) )$( NOT growth_land_scen_lo(node,land_scenario,year) )
            )
* reduction of land scenario from previous period
        + SUM((year_all2)$( seq_period(year_all2,year) ),
                ( LAND(node,land_scenario,year_all2)$( model_horizon(year_all2) )
                  + historical_land(node,land_scenario,year_all2) )
                * POWER( 1 + growth_land_scen_lo(node,land_scenario,year) , duration_period(year) )
            )
* optional relaxation for calibration and debugging
%SLACK_LAND_SCEN_LO% - SLACK_LAND_SCEN_LO(node,land_scenario,year)
;

***
* These constraints enforces upper and lower bounds on the change rate per land type
* determined as a linear combination of land use scenarios.
*
* .. _equation_dynamic_land_type_constraint_up:
*
* Equation DYNAMIC_LAND_TYPE_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \sum_{s \in S} \text{land_use}_{n,s,y,u} &\cdot \text{LAND}_{n,s,y}
*         \leq \text{initial_land_up}_{n,y,u}
*             \cdot \frac{ \Big( 1 + \text{growth_land_up}_{n,y,u} \Big)^{|y|} - 1 }
*                        { \text{growth_land_up}_{n,y,u} } \\
*              & + \Big( \sum_{s \in S} \big( \text{land_use}_{n,s,y-1,u}
*                          + \text{dynamic_land_up}_{n,s,y-1,u} \big) \\
*                            & \quad \quad \cdot \big( \text{LAND}_{n,s,y-1} + \text{historical_land}_{n,s,y-1} \big) \Big) \\
*                            & \quad \cdot \Big( 1 + \text{growth_land_up}_{n,y,u} \Big)^{|y|}
*
***
DYNAMIC_LAND_TYPE_CONSTRAINT_UP(node,year,land_type)$( is_dynamic_land_up(node,year,land_type) )..
* amount of land assigned to specific type in current period
    SUM(land_scenario$( map_land(node,land_scenario,year) ),
        land_use(node,land_scenario,year,land_type) * LAND(node,land_scenario,year) ) =L=
* initial 'new' land used for that type (compounded over the duration of the period)
        initial_land_up(node,year,land_type) * (
            ( ( POWER( 1 + growth_land_up(node,year,land_type) , duration_period(year) ) - 1 )
                / growth_land_up(node,year,land_type) )$( growth_land_up(node,year,land_type) )
              + ( duration_period(year) )$( NOT growth_land_up(node,year,land_type) )
            )
* expansion of previously used land of this type from previous period and upper bound on land use transformation
        + SUM((year_all2)$( seq_period(year_all2,year) ),
            SUM(land_scenario$( map_land(node,land_scenario,year) ),
                ( land_use(node,land_scenario,year_all2,land_type)
                  + dynamic_land_up(node,land_scenario,year_all2,land_type) )
                * ( LAND(node,land_scenario,year_all2)$( model_horizon(year_all2) )
                    + historical_land(node,land_scenario,year_all2) )
                * POWER( 1 + growth_land_up(node,year,land_type) , duration_period(year) )
              )
          )
* optional relaxation for calibration and debugging
%SLACK_LAND_TYPE_UP% + SLACK_LAND_TYPE_UP(node,year,land_type)
;

***
* .. _equation_dynamic_land_type_constraint_lo:
*
* Equation DYNAMIC_LAND_TYPE_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \sum_{s \in S} \text{land_use}_{n,s,y,u} &\cdot \text{LAND}_{n,s,y}
*         \geq - \text{initial_land_lo}_{n,y,u}
*             \cdot \frac{ \Big( 1 + \text{growth_land_lo}_{n,y,u} \Big)^{|y|} - 1 }
*                        { \text{growth_land_lo}_{n,y,u} } \\
*              & + \Big( \sum_{s \in S} \big( \text{land_use}_{n,s,y-1,u}
*                          + \text{dynamic_land_lo}_{n,s,y-1,u} \big) \\
*                            & \quad \quad \cdot \big( \text{LAND}_{n,s,y-1} + \text{historical_land}_{n,s,y-1} \big) \Big) \\
*                            & \quad \cdot \Big( 1 + \text{growth_land_lo}_{n,y,u} \Big)^{|y|}
*
***
DYNAMIC_LAND_TYPE_CONSTRAINT_LO(node,year,land_type)$( is_dynamic_land_lo(node,year,land_type) )..
* amount of land assigned to specific type in current period
    SUM(land_scenario$( map_land(node,land_scenario,year) ),
        land_use(node,land_scenario,year,land_type) * LAND(node,land_scenario,year) ) =G=
* initial 'new' land used for that type (compounded over the duration of the period)
        - initial_land_lo(node,year,land_type) * (
            ( ( POWER( 1 + growth_land_up(node,year,land_type) , duration_period(year) ) - 1 )
                / growth_land_lo(node,year,land_type) )$( growth_land_lo(node,year,land_type) )
              + ( duration_period(year) )$( NOT growth_land_lo(node,year,land_type) )
            )
* expansion of previously used land of this type from previous period and lower bound on land use transformation
        + SUM((year_all2)$( seq_period(year_all2,year) ),
            SUM(land_scenario$( map_land(node,land_scenario,year) ),
                ( land_use(node,land_scenario,year_all2,land_type)
                  + dynamic_land_lo(node,land_scenario,year_all2,land_type) )
                * ( LAND(node,land_scenario,year_all2)$( model_horizon(year_all2) )
                    + historical_land(node,land_scenario,year_all2) )
                * POWER( 1 + growth_land_lo(node,year,land_type) , duration_period(year) )
              )
          )
* optional relaxation for calibration and debugging
%SLACK_LAND_TYPE_LO% - SLACK_LAND_TYPE_LO(node,year,land_type)
;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _section_of_generic_relations:
*
* Section of generic relations (linear constraints)
* -------------------------------------------------
*
* This feature is intended for development and testing only - all new features should be implemented
* as specific new mathematical formulations and associated sets & parameters!
*
* Auxiliary variable for left-hand side
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_relation_equivalence:
*
* Equation RELATION_EQUIVALENCE
* """""""""""""""""""""""""""""
*   .. math::
*      \text{REL}_{r,n,y} = \sum_{t} \Bigg(
*          & \ \text{relation_new_capacity}_{r,n,y,t} \cdot \text{CAP_NEW}_{n,t,y} \\[4 pt]
*          & + \text{relation_total_capacity}_{r,n,y,t} \cdot \sum_{y^V \leq y} \ \text{CAP}_{n,t,y^V,y} \\
*          & + \sum_{n^L,y',m,h} \ \text{relation_activity}_{r,n,y,n^L,t,y',m} \\
*          & \quad \quad \cdot \Big( \sum_{y^V \leq y'} \text{ACT}_{n^L,t,y^V,y',m,h}
*                              + \text{historical_activity}_{n^L,t,y',m,h} \Big) \Bigg)
*
* The parameter :math:`\text{historical_new_capacity}_{r,n,y}` is not included here, because relations can only be active
* in periods included in the model horizon and there is no "writing" of capacity relation factors across periods.
***

RELATION_EQUIVALENCE(relation,node,year)..
    REL(relation,node,year)
        =E=
    SUM(tec,
        ( relation_new_capacity(relation,node,year,tec) * CAP_NEW(node,tec,year)
          + relation_total_capacity(relation,node,year,tec)
            * SUM(vintage$( map_tec_lifetime(node,tec,vintage,year) ), CAP(node,tec,vintage,year) )
          )$( inv_tec(tec) )
        + SUM((location,year_all2,mode,time)$( map_tec_act(location,tec,year_all2,mode,time) ),
            relation_activity(relation,node,year,location,tec,year_all2,mode)
            * ( SUM(vintage$( map_tec_lifetime(location,tec,vintage,year_all2) ),
                  ACT(location,tec,vintage,year_all2,mode,time) )
                  + historical_activity(location,tec,year_all2,mode,time) )
          )
      ) ;

***
* Upper and lower bounds on user-defined relations
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_relation_constraint_up:
*
* Equation RELATION_CONSTRAINT_UP
* """""""""""""""""""""""""""""""
*   .. math::
*      \text{REL}_{r,n,y} \leq \text{relation_upper}_{r,n,y}
***
RELATION_CONSTRAINT_UP(relation,node,year)$( is_relation_upper(relation,node,year) )..
    REL(relation,node,year)
%SLACK_RELATION_BOUND_UP% - SLACK_RELATION_BOUND_UP(relation,node,year)
    =L= relation_upper(relation,node,year) ;

***
* .. _equation_relation_constraint_lo:
*
* Equation RELATION_CONSTRAINT_LO
* """""""""""""""""""""""""""""""
*   .. math::
*      \text{REL}_{r,n,y} \geq \text{relation_lower}_{r,n,y}
***
RELATION_CONSTRAINT_LO(relation,node,year)$( is_relation_lower(relation,node,year) )..
    REL(relation,node,year)
%SLACK_RELATION_BOUND_LO% + SLACK_RELATION_BOUND_LO(relation,node,year)
    =G= relation_lower(relation,node,year) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* .. _gams-storage:
*
* Storage section
* ---------------
*
* MESSAGEix offers a set of equations to represent a wide range of storage solutions flexibly.
* Storage solutions are modeled as "technologies" that can be used to store a "commodity" (e.g., water, heat, electricity, etc.)
* and shift it over sub-annual time slices within one model period. The storage solution presented here has three
* distinct parts: (i) Charger: a technology for charging a commodity to the storage container,
* for example, a pump in a pumped hydropower storage (PHS) plant. (ii) Discharger: a technology
* to convert the stored commodity to the output commodity, e.g., a turbine in PHS.
* (iii) Storage container: a device for storing a commodity over time, such as a water reservoir in PHS.
* If desired, the user can combine charger and discharger parts into one technology, using two different "modes" of operation
* for that technology like turbo-machinery in PHS. This way the capacity related information, like investment cost, lifetime, capacity factor, etc.,
* will be defined only for one technology (i.e., charger-discharger), as opposed to modeling these two parts separately.
*
* .. figure:: ../../_static/storage.png
*
* Storage equations
* ^^^^^^^^^^^^^^^^^
* The content of storage device depends on three factors: charge or discharge in
* one time slice (represented by `Equation STORAGE_CHANGE`_), linked to the state of charge in the previous
* time slice and storage losses between these two consecutive time slices (represented by `Equation STORAGE_BALANCE`_).
* Moreover, the storage device can be optionally filled with an initial value as percentage of its capacity (see more details under `Equation STORAGE_BALANCE_INIT`_).
* Another option is to link a commodity for maintaining the operation of storage device over time (see `Equation STORAGE_INPUT`_).
*
* .. _equation_storage_change:
*
* Equation STORAGE_CHANGE
* """""""""""""""""""""""
* This equation shows the change in the content of the storage container in each
* sub-annual time slice. This change is based on the activity of charger and discharger
* technologies connected to that storage container. The notation :math:`S^{\text{storage}}`
* represents the mapping set `map_tec_storage` denoting charger-discharger
* technologies connected to a specific storage container in a specific node and
* storage level. Where:
*
* - :math:`t^{C}` is a charging technology and :math:`t^{D}` is the corresponding discharger.
* - :math:`h-1` is the time slice prior to :math:`h`.
* - :math:`l^{T}` is `lvl_temporal`, i.e., the temporal level at which storage is operating
* - :math:`m^{S}` is `mode` of operation for storage container technology

*   .. math::
*      \text{STORAGE_CHARGE}_{n,t,m^s,l,c,y,h} =
*          \sum_{\substack{n^L,m,h-1 \\ y^V \leq y, (n,t^C,t,l,y) \sim S^{\text{storage}}}} \text{output}_{n^L,t^C,y^V,y,m,n,c,l,h-1,h}
*             \cdot & \text{ACT}_{n^L,t^C,y^V,y,m,h-1} \\
*          - \sum_{\substack{n^L,m,c,h-1 \\ y^V \leq y, (n,t^D,t,l,y) \sim S^{\text{storage}}}} \text{input}_{n^L,t^D,y^V,y,m,n,c,l,h-1,h}
*              \cdot \text{ACT}_{n^L,t^D,y^V,y,m,h-1} \quad \forall \ t \in T^{\text{STOR}}, & \forall \ l \in L^{\text{STOR}}
***
STORAGE_CHANGE(node,storage_tec,mode,level_storage,commodity,year,time)$sum(
               (tec,mode2,lvl_temporal), map_tec_storage(node,tec,mode2,storage_tec,mode,level_storage,commodity,lvl_temporal) ) ..
* change in the content of storage in the examined time slice
    STORAGE_CHARGE(node,storage_tec,mode,level_storage,commodity,year,time) =E=
* increase in the content of storage due to the activity of charging technologies
        SUM( (location,vintage,tec,mode2,time2,time3,lvl_temporal)$(
        map_tec_lifetime(node,tec,vintage,year) AND map_temporal_hierarchy(lvl_temporal,time,time3
                )$map_tec_storage(node,tec,mode2,storage_tec,mode,level_storage,commodity,lvl_temporal) ),
            output(location,tec,vintage,year,mode2,node,commodity,level_storage,time2,time)
            * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode2,time2) )
* decrease in the content of storage due to the activity of discharging technologies
        - SUM( (location,vintage,tec,mode2,time2,time3,lvl_temporal)$(
        map_tec_lifetime(node,tec,vintage,year) AND map_temporal_hierarchy(lvl_temporal,time,time3
                )$map_tec_storage(node,tec,mode2,storage_tec,mode,level_storage,commodity,lvl_temporal) ),
            input(location,tec,vintage,year,mode2,node,commodity,level_storage,time2,time)
            * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode2,time2) );

***
* .. _equation_storage_balance:
*
* Equation STORAGE_BALANCE
* """"""""""""""""""""""""
*
* This equation ensures the commodity balance of storage technologies, where the commodity is shifted between sub-annual
* time slices within a model period. If the state of charge of storage is set exogenously in one time slice through
* :math:`\storageinitial_{ntlcyh}`, the content from the previous time slice is not carried over to this time slice.
*
* .. math::
*    \STORAGE_{ntmlcyh} =\ & \STORAGECHARGE_{ntmlcyh} \\
*    & + \STORAGE_{ntmlcy(h-1)} \cdot (1 - \storageselfdischarge_{ntmly(h-1)}) \\
*    \forall\ & t \in T^{\text{STOR}}, l \in L^{\text{STOR}}, \storageinitial_{ntmlcyh} = 0
***
STORAGE_BALANCE(node,storage_tec,mode,level,commodity,year,time2,lvl_temporal)$ (
    SUM((tec,mode2), map_tec_storage(node,tec,mode2,storage_tec,mode,level,commodity,lvl_temporal) )
*    AND NOT storage_initial(node,storage_tec,mode,level,commodity,year,time2)
)..
* Showing the the state of charge of storage at each time slice
    STORAGE(node,storage_tec,mode,level,commodity,year,time2) =E=
* change in the content of storage in the examined time slice
    + STORAGE_CHARGE(node,storage_tec,mode,level,commodity,year,time2)
* storage content in the previous subannual time slice
    + SUM(time$map_time_period(year,lvl_temporal,time,time2),
        STORAGE(node,storage_tec,mode,level,commodity,year,time)
* considering storage self-discharge losses due to keeping the storage media between two subannual time slices
        * (1 - storage_self_discharge(node,storage_tec,mode,level,commodity,year,time) ) ) ;

***
* .. _equation_storage_balance_init:
*
* Equation STORAGE_BALANCE_INIT
* """""""""""""""""""""""""""""
*
* Where :math:`\storageinitial_{ntlyh}` has a non-zero value, this equation ensures that the amount of commodity stored
* at the end of a sub-annual time slice is equal or greater than the initialized content of storage in the following time slice.
* The values in parameter :math:`\storageinitial_{ntlyh}` are percentages showing
* a fraction of installed capacity of storage device (container) that can be filled initially.
*
* .. math::
*    \STORAGE_{ntmlcy(h-1)} \geq &  \storageinitial_{ntmlcyh} \cdot \text{duration_time}_{h} \cdot \text{capacity_factor}_{n,t,y^V,y,h} \cdot \text{CAP}_{n,t,y^V,y}  \\
*    \quad \forall \ t \ \in \ T^{\text{INV}}, \forall\ & \storageinitial_{ntmlcyh} \neq 0
***

STORAGE_BALANCE_INIT(node,storage_tec,mode,level,commodity,year,time,time2)$ (
    SUM((tec,mode2,lvl_temporal), map_tec_storage(node,tec,mode2,storage_tec,mode,level,commodity,lvl_temporal)
        AND map_time_period(year,lvl_temporal,time,time2) )
    AND storage_initial(node,storage_tec,mode,level,commodity,year,time2) )..
* Showing the state of charge of storage at a time slice prior to a time slice that has initial storage content
    STORAGE(node,storage_tec,mode,level,commodity,year,time) =G=
* Initial content of storage in the examined time slice as a percentage multiplier in available capacity of storage
        storage_initial(node,storage_tec,mode,level,commodity,year,time2)
        * SUM(vintage$( map_tec_lifetime(node,storage_tec,vintage,year) ), capacity_factor(node,storage_tec,vintage,year,time2)
             * CAP(node,storage_tec,vintage,year) / duration_time(time2)  )
;
***
* .. _equation_storage_input:
*
* Equation STORAGE_INPUT
* """"""""""""""""""""""""""""
*
* This equation links :math:`\STORAGE` to an input commodity to maintain the activity (:math:`\ACT`) of each active storage *container* technology
* :math:`t`. This input commodity is distinct from the stored commodity. For example, in a pumped hydro storage solution, a user can link heating
* for keeping the stored water warm. In this case, the input commodity is not a function of charge or discharge, but the amount of stored media in the container over time.
* Therefore, the input commodity specified here is distinct from the one stored and discharged by *(dis)charge* technologies :math:`t^C,t^D` appearing in
* :ref:`equation_storage_change`.
*
* .. math::
*    \STORAGE_{ntmlcy^Ah} =\ & \sum_{\{n^Ly^Vh^O \vert K\}} \durationtimerel_{hh^O} \cdot \ACT_{n^Lty^Vy^Amh^O} \\
*    \forall\ & n,t,l,c,m,y^A,h \vert t \in T^{\text{STOR}} \\
*    K:\ & \\text{input}_{n^Lty^Vy^Amn^Oclhh^O} \neq 0
*
***

STORAGE_INPUT(node,storage_tec,level,commodity,level_storage,commodity2,mode,year,time)$
    ( map_time_commodity_storage(node,storage_tec,level,commodity,mode,year,time) AND
      SUM( (tec,mode2,lvl_temporal), map_tec_storage(node,tec,mode2,storage_tec,mode,level_storage,commodity2,lvl_temporal) ) ) ..
* Connecting an input commodity to maintain the operation of storage container over time (optional)
  STORAGE(node,storage_tec,mode,level_storage,commodity2,year,time) =E=
        SUM( (location,vintage,time2)$(map_tec_lifetime(node,storage_tec,vintage,year)$(
              input(location,storage_tec,vintage,year,mode,node,commodity,level,time,time2) ) ),
              duration_time_rel(time,time2) * ACT(location,storage_tec,vintage,year,mode,time) )
;

*----------------------------------------------------------------------------------------------------------------------*
* model statements                                                                                                     *
*----------------------------------------------------------------------------------------------------------------------*

Model MESSAGE_LP / all / ;

MESSAGE_LP.holdfixed = 1 ;
MESSAGE_LP.optfile = 1 ;
MESSAGE_LP.optcr = 0 ;
