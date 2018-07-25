***
* Mathematical formulation (core model)
* =====================================
* This page is generated from the auto-documentation mark-up in ``MESSAGE/model_core.gms``.
*
* The |MESSAGEix| systems-optimization model minimizes total costs
* while satisfying given demand levels for commodities/services
* and considering a broad range of technical/engineering constraints and societal restrictions
* (e.g. bounds on greenhouse gas emissions, pollutants).
* Demand levels are static (i.e. non-elastic), but the demand response can be integrated by linking |MESSAGEix|
* to the single sector general-economy MACRO model included in this framework.
*
* For the complete list of sets, mappings and parameters,
* refer to the auto-documentation pages :ref:`sets_maps_def` and :ref:`parameter_def`.
***

*----------------------------------------------------------------------------------------------------------------------*
* Notation declaration                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* Notation declaration
* --------------------
* The following short notation is used in the mathematical description relative to the GAMS code:
*
* Mathematical notation of sets
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ================================== ===================================================================================
* Math notation                      GAMS set & index notation
* ================================== ===================================================================================
* :math:`n \in N`                    node (across spatial hierarchy levels)
* :math:`y \in Y`                    year (all periods including historical and model horizon)
* :math:`y \in Y^M \subset Y`        time periods included in model horizon
* :math:`y \in Y^H \subset Y`        historical time periods (prior to first model period)
* :math:`c \in C`                    commodity
* :math:`l \in L`                    level
* :math:`g \in G`                    grade
* :math:`t \in T`                    technology (a.k.a tec)
* :math:`h \in H`                    time (subannual time periods)
* :math:`m \in M`                    mode
* :math:`e \in E`                    emission, pollutants
* :math:`s \in S`                    scenarios of land use (for land-use model emulator)
* :math:`u \in U`                    land-use types
* :math:`r \in R`                    set of generic relations (linear constraints)
* :math:`t \in T^{INV} \subseteq T`  all technologies with investment decisions and capacity constraints
* :math:`t \in T^{REN} \subseteq T`  all technologies which draw their input from the renewable level
* :math:`n \in N(\widehat{n})`       all nodes that are subnodes of node :math:`\widehat{n}`
* :math:`y \in Y(\widehat{y})`       all years mapped to the category ``type_year`` :math:`\widehat{y}`
* :math:`t \in T(\widehat{t})`       all technologies mapped to the category ``type_tec`` :math:`\widehat{t}`
* :math:`e \in E(\widehat{e})`       all emissions mapped to the category ``type_emission`` :math:`\widehat{e}`
* ================================== ===================================================================================
*
***

*----------------------------------------------------------------------------------------------------------------------*
* Variable definitions                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* Decision variables
* ^^^^^^^^^^^^^^^^^^
* ============================================= ========================================================================
* Variable                                      Explanatory text
* ============================================= ========================================================================
* :math:`OBJ \in \mathbb{R}`                    Objective value of the optimization program
* :math:`EXT_{n,c,g,y} \in \mathbb{R}_+`        Extraction of non-renewable/exhaustible resources from reserves
* :math:`STOCK_{n,c,l,y} \in \mathbb{R}_+`      Quantity in stock (storage) at start of period :math:`y`
* :math:`STOCK\_CHG_{n,c,l,y,h} \in \mathbb{R}` Input or output quantity into intertemporal commodity stock (storage)
* :math:`REN_{n,t,c,g,y,h}`                     Activity of renewable technologies per grade
* :math:`CAP\_NEW_{n,t,y} \in \mathbb{R}_+`     New installed capacity (yearly average over period duration
* :math:`CAP_{n,t,y^V,y} \in \mathbb{R}_+`      Maintained capacity in year :math:`y` of vintage :math:`y^V`
* :math:`ACT_{n,t,y^V,y,m,h} \in \mathbb{R}`    Activity of a technology (by vintage, mode, subannual time)
* :math:`CAP\_NEW\_UP_{n,t,y} \in \mathbb{R}_+` Relaxation of upper dynamic constraint on new capacity
* :math:`CAP\_NEW\_LO_{n,t,y} \in \mathbb{R}_+` Relaxation of lower dynamic constraint on new capacity
* :math:`CAP\_FIRM_{n,t,c,l,y,q}`                   Dispatchable capacity of renewable technologies per grade
* :math:`ACT\_UP_{n,t,y,h} \in \mathbb{R}_+`    Relaxation of upper dynamic constraint on activity [#ACT]_
* :math:`ACT\_LO_{n,t,y,h} \in \mathbb{R}_+`    Relaxation of lower dynamic constraint on activity [#ACT]_
* :math:`LAND_{n,s,y} \in [0,1]`                Relative share of land-use scenario (for land-use model emulator)
* :math:`EMISS_{n,e,\widehat{t},y}`             Auxiliary variable for aggregate emissions by technology type
* :math:`REL_{r,n,y} \in \mathbb{R}`            Auxiliary variable for left-hand side of relations (linear constraints)
* :math:`COMMODITY\_USE_{n,c,l,y}`              Auxiliary variable for amount of commodity used at specific level
* ============================================= ========================================================================
*
* The index :math:`y^V` is the year of construction (vintage) wherever it is necessary to
* clearly distinguish between year of construction and the year of operation.
*
* All decision variables are by year, not by (multi-year) period, except :math:`STOCK_{n,c,l,y}`.
* In particular, the new capacity variable :math:`CAP\_NEW_{n,t,y}` has to be multiplied by the number of years
* in a period :math:`|y| = duration\_period_{y}` to determine the available capacity in subsequent periods.
* This formulation gives more flexibility when it comes to using periods of different duration
* (more intuitive comparison across different periods).
*
* The current model framework allows both input or output normalized formulation.
* This will affect the parametrization, see Section :ref:`efficiency_output` for more details.
*
* .. [#ACT] The dynamic activity constraints are implemented as summed over all modes;
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
    CAP_FIRM(node,tec,commodity,level,year_all)   firm capacity
* variables for soft relaxation of dynamic activity constraints
    CAP_NEW_UP(node,tec,year_all)    relaxation variable for dynamic constraints on new capacity (upwards)
    CAP_NEW_LO(node,tec,year_all)    relaxation variable for dynamic constraints on new capacity (downwards)
    ACT_UP(node,tec,year_all,time)   relaxation variable for dynamic constraints on activity (upwards)
    ACT_LO(node,tec,year_all,time)   relaxation variable for dynamic constraints on activity (downwards)
* land-use model emulator
    LAND(node,land_scenario,year_all) relative share of land-use scenario

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
;

***
* Auxiliary variables
* ^^^^^^^^^^^^^^^^^^^
* ============================================= ========================================================================
* Variable                                      Explanatory text
* ============================================= ========================================================================
* :math:`DEMAND_{n,c,l,y,h} \in \mathbb{R}`     Demand level (in equilibrium with MACRO integration)
* :math:`PRICE\_COMMODITY_{n,c,l,y,h}`          Commodity price (undiscounted marginals of COMMODITY_BALANCE constraint)
* :math:`PRICE\_EMISSION_{n,e,\widehat{t},y}`   Emission price (undiscounted marginals of EMISSION_BOUND constraint)
* :math:`COST\_NODAL\_NET_{n,y} \in \mathbb{R}` System costs at the node level net of energy trade revenues/cost
* :math:`GDP_{n,y} \in \mathbb{R}`              gross domestic product (GDP) in market exchange rates for MACRO reporting
* ============================================= ========================================================================
*
***

Variables
* auxiliary variables for demand, prices, costs and GDP (for reporting when MESSAGE is run with MACRO)
    DEMAND(node,commodity,level,year_all,time) demand
    PRICE_COMMODITY(node,commodity,level,year_all,time)  commodity price (derived from marginals of COMMODITY_BALANCE constraint)
    PRICE_EMISSION(node,type_emission,type_tec,year_all) emission price (derived from marginals of EMISSION_BOUND constraint)
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
* have positive upper bounds are assumed to be non-negative
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
    SLACK_COMMODITY_BALANCE_UP(node,commodity,level,year_all,time) slack variable for commodity balance (upwards)
    SLACK_COMMODITY_BALANCE_LO(node,commodity,level,year_all,time) slack variable for commodity balance (downwards)
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
    COMMODITY_BALANCE               commodity supply-demand balance constraint
    STOCKS_BALANCE                  commodity inter-temporal balance of stocks
    CAPACITY_CONSTRAINT             capacity constraint for technology (by sub-annual time slice)
    CAPACITY_MAINTENANCE            constraint for technology capacity maintainance
    OPERATION_CONSTRAINT            constraint on maximum yearly operation (scheduled down-time for maintainance)
    MIN_UTILIZATION_CONSTRAINT      constraint for minimum yearly operation (aggregated over the course of a year)
    RENEWABLES_POTENTIAL_CONSTRAINT constraint on renewable resource potential
    RENEWABLES_CAPACITY_REQUIREMENT lower bound on required overcapacity when using lower grade potentials
    RENEWABLES_EQUIVALENCE          equation to define the renewables extraction
    COMMODITY_USE_LEVEL             defines the COMMODITY_USE as the amount of a commodity at a level that was consumed
    ACTIVITY_SHARE_BIN
    ACTIVITY_SHARE_TOTAL
    FIRM_CAPACITY_PROVISION         lower bound on CAP as the minimum installed capacity of each technology
    FIRM_CAPACITY_CONSTRAINT
    OPERATING_RESERVE_CONSTRAINT
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
;

*----------------------------------------------------------------------------------------------------------------------*
* equation statements                                                                                                  *
*----------------------------------------------------------------------------------------------------------------------*

***
* Objective function
* ------------------
*
* The objective function of the |MESSAGEix| core model
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation OBJECTIVE
* """"""""""""""""""
*
* The objective function (of the core model) minimizes total discounted systems costs including costs for emissions,
* relaxations of dynamic constraints
*
* .. math::
*    OBJ = \sum_{n,y \in Y^{M}} discountfactor_{y} \cdot COST\_NODAL_{n,y}
*
***

OBJECTIVE..
    OBJ =E= SUM((node,year), discountfactor(year) * COST_NODAL(node, year))
;

***
* Regional system cost accounting function
* ----------------------------------------
*
* Accounting of regional system costs over time
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation COST_ACCOUNTING_NODAL
* """"""""""""""""""""""""""""""
*
* Accounting of regional systems costs over time as well as costs for emissions (taxes),
* land use (from the model land-use model emulator), relaxations of dynamic constraints,
* and linear relations.
*
* .. math::
*    COST\_NODAL_{n,y} & = \sum_{c,g} \ resource\_cost_{n,c,g,y} \cdot EXT_{n,c,g,y} \\
*      & + \sum_{t} \
*          \bigg( inv\_cost_{n,t,y} \cdot construction\_time\_factor_{n,t,y} \\
*      & \quad \quad \quad \cdot end\_of\_horizon\_factor_{n,t,y} \cdot CAP\_NEW_{n,t,y} \\[4 pt]
*      & \quad \quad + \sum_{y^V \leq y} \ fix\_cost_{n,t,y^V,y} \cdot CAP_{n,t,y^V,y} \\
*      & \quad \quad + \sum_{\substack{y^V \leq y \\ m,h}} \ var\_cost_{n,t,y^V,y,m,h} \cdot ACT_{n,t,y^V,y,m,h} \\
*      & \quad \quad + \Big( abs\_cost\_new\_capacity\_soft\_up_{n,t,y} \\
*      & \quad \quad \quad
*          + level\_cost\_new\_capacity\_soft\_up_{n,t,y} \cdot\ inv\_cost_{n,t,y}
*          \Big) \cdot CAP\_NEW\_UP_{n,t,y} \\[4pt]
*      & \quad \quad + \Big( abs\_cost\_new\_capacity\_soft\_lo_{n,t,y} \\
*      & \quad \quad \quad
*          + level\_cost\_new\_capacity\_soft\_lo_{n,t,y} \cdot\ inv\_cost_{n,t,y}
*          \Big) \cdot CAP\_NEW\_LO_{n,t,y} \\[4pt]
*      & \quad \quad + \sum_{m,h} \ \Big( abs\_cost\_activity\_soft\_up_{n,t,y,m,h} \\
*      & \quad \quad \quad
*          + level\_cost\_activity\_soft\_up_{n,t,y,m,h} \cdot\ levelized\_cost_{n,t,y,m,h}
*          \Big) \cdot ACT\_UP_{n,t,y,h} \\
*      & \quad \quad + \sum_{m,h} \ \Big( abs\_cost\_activity\_soft\_lo_{n,t,y,m,h} \\
*      & \quad \quad \quad
*          + level\_cost\_activity\_soft\_lo_{n,t,y,m,h} \cdot\ levelized\_cost_{n,t,y,m,h}
*          \Big) \cdot ACT\_LO_{n,t,y,h} \bigg) \\
*      & + \sum_{\substack{\widehat{e},\widehat{t} \\ e \in E(\widehat{e})}}
*            emission\_scaling_{\widehat{e},e} \cdot \ emission\_tax_{n,\widehat{e},\widehat{t},y}
*            \cdot EMISS_{n,e,\widehat{t},y} \\
*      & + \sum_{s} land\_cost_{n,s,y} \cdot LAND_{n,s,y} \\
*      & + \sum_{r} relation\_cost_{r,n,y} \cdot REL_{r,n,y}
***

COST_ACCOUNTING_NODAL(node, year)..
    COST_NODAL(node, year) =E=
* resource extration costs
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
%SLACK_COMMODITY_BALANCE%   + SLACK_COMMODITY_BALANCE_UP(node,commodity,level,year,time)
%SLACK_COMMODITY_BALANCE%   + SLACK_COMMODITY_BALANCE_LO(node,commodity,level,year,time)
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
* Resource and commodity section
* ------------------------------
*
* Constraints on resource extraction
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation EXTRACTION_EQUIVALENCE
* """""""""""""""""""""""""""""""
*
* This constraint translates the quantity of resources extracted (summed over all grades) to the input used by
* all technologies (drawing from that node). It is introduced to simplify subsequent notation in input/output relations
* and nodal balance constraints.
*
*  .. math::
*     \sum_{g} EXT_{n,c,g,y} =
*     \sum_{\substack{n^L,t,m,h,h^{OD} \\ y^V \leq y  \\ \ l \in L^{RES} \subseteq L }}
*         input_{n^L,t,y^V,y,m,n,c,l,h,h^{OD}} \cdot ACT_{n^L,t,m,y,h}
*
* The set :math:`L^{RES} \subseteq L` denotes all levels for which the detailed representation of resources applies.
***
EXTRACTION_EQUIVALENCE(node,commodity,year)..
    SUM(grade$( map_resource(node,commodity,grade,year) ), EXT(node,commodity,grade,year) )
    =G= SUM((location,tec,vintage,mode,level_resource,time_act,time_od)$( map_tec_act(node,tec,year,mode,time_act)
            AND map_tec_lifetime(node,tec,vintage,year) ),
        input(location,tec,vintage,year,mode,node,commodity,level_resource,time_act,time_od)
        * ACT(location,tec,vintage,year,mode,time_act) ) ;

***
* Equation EXTRACTION_BOUND_UP
* """"""""""""""""""""""""""""
*
* This constraint specifies an upper bound on resource extraction by grade.
*
*  .. math::
*     EXT_{n,c,g,y} \leq bound\_extraction\_up_{n,c,g,y}
*
***
EXTRACTION_BOUND_UP(node,commodity,grade,year)$( map_resource(node,commodity,grade,year)
        AND is_bound_extraction_up(node,commodity,grade,year) )..
    EXT(node,commodity,grade,year) =L= bound_extraction_up(node,commodity,grade,year) ;

***
* Equation RESOURCE_CONSTRAINT
* """"""""""""""""""""""""""""
*
* This constraint restricts that resource extraction in a year guarantees the "remaining resources" constraint,
* i.e., only a given fraction of remaining resources can be extracted per year.
*
*  .. math::
*     EXT_{n,c,g,y} \leq
*     resource\_remaining_{n,c,g,y} \cdot
*         \Big( & resource\_volume_{n,c,g} \\
*               & - \sum_{y' < y} duration\_period_{y'} \cdot EXT_{n,c,g,y'} \Big)
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
* Equation RESOURCE_HORIZON
* """""""""""""""""""""""""
* This constraint ensures that total resource extraction over the model horizon does not exceed the available resources.
*
*  .. math::
*     \sum_{y} duration\_period_{y} \cdot EXT_{n,c,g,y} \leq  resource\_volume_{n,c,g}
*
***
RESOURCE_HORIZON(node,commodity,grade)$( SUM(year$map_resource(node,commodity,grade,year), 1 ) )..
    SUM(year, duration_period(year) * EXT(node,commodity,grade,year) ) =L= resource_volume(node,commodity,grade) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* Constraints on commodities and stocks
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation COMMODITY_BALANCE
* """"""""""""""""""""""""""
* This constraint ensures the nodal and temporal balance of outputs/imports and inputs/exports for all commodities.
*
*  .. math::
*     \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} output_{n^L,t,y^V,y,m,n,c,l,h^A,h}
*         \cdot duration\_time\_rel_{h,h^A} \cdot & ACT_{n^L,t,y^V,y,m,h^A} \\
*     - \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} input_{n^L,t,y^V,y,m,n,c,l,h^A,h}
*         \cdot duration\_time\_rel_{h,h^A} \cdot & ACT_{n^L,t,m,y,h^A} \\
*     + \ STOCK\_CHG_{n,c,l,y,h} & \\[4pt]
*     + \ \sum_s \Big( land\_output_{n,s,y,c,l,h} - land\_input_{n,s,y,c,l,h} \Big) \cdot & LAND_{n,s,y} \\[4pt]
*     - \ demand\_fixed_{n,c,l,y,h}
*     & \geq 0 \quad \forall \ l \notin L^{RES} \subseteq L
*
* The commodity balance constraint at the resource level is included in the `Equation RESOURCE_CONSTRAINT`_,
* while at the renewable level, it is included in the `Equation RENEWABLES_EQUIVALENCE`_.
***
COMMODITY_BALANCE(node,commodity,level,year,time)$( map_commodity(node,commodity,level,year,time)
                  AND NOT level_resource(level) AND NOT level_renewable(level) )..
    SUM( (location,tec,vintage,mode,time2)$( map_tec_act(location,tec,year,mode,time2)
            AND map_tec_lifetime(location,tec,vintage,year) ),
* import into node and output by all technologies located at 'location' sending to 'node' and 'time2' sending to 'time'
        output(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode,time2)
* export from node and input into technologies located at 'location' taking from 'node' and 'time2' taking from 'time'
        - input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
        * duration_time_rel(time,time2) * ACT(location,tec,vintage,year,mode,time2) )
* quantity taken out from ( >0 ) or put into ( <0 ) inter-period stock (storage)
    + STOCK_CHG(node,commodity,level,year,time)$( map_stocks(node,commodity,level,year) )
* yield from land-use model emulator
    + SUM(land_scenario,
        ( land_output(node,land_scenario,year,commodity,level,time)
          - land_input(node,land_scenario,year,commodity,level,time) ) * LAND(node,land_scenario,year) )
* final consumption (exogenous parameter to be satisfied by the energy+water+xxx system)
    - demand_fixed(node,commodity,level,year,time)
* relaxation of constraints for debugging
%SLACK_COMMODITY_BALANCE%   + SLACK_COMMODITY_BALANCE_UP(node,commodity,level,year,time)
%SLACK_COMMODITY_BALANCE%   - SLACK_COMMODITY_BALANCE_LO(node,commodity,level,year,time)
    =G= 0 ;

***
* Equation STOCKS_BALANCE
* """""""""""""""""""""""
* This constraint ensures the inter-temporal balance of commodity stocks.
* The parameter :math:`commodity\_stocks_{n,c,l}` can be used to model exogenous additions to the stock
*
*  .. math::
*     STOCK_{n,c,l,y} + commodity\_stock_{n,c,l,y} =
*         duration\_period_{y} \cdot & \sum_{h} STOCK\_CHG_{n,c,l,y,h} \\
*                                    & + STOCK_{n,c,l,y+1}
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
* Technology section
* ------------------
*
* Technical and engineering constraints
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation CAPACITY_CONSTRAINT
* """"""""""""""""""""""""""""
* This constraint ensures that the actual activity of a technology at a node/time cannot exceed available (maintained)
* capacity summed over all vintages, including the technology capacity factor :math:`capacity\_factor_{n,t,y,t}`.
*
*  .. math::
*     \sum_{m} ACT_{n,t,y^V,y,m,h}
*         \leq duration\_time_{h} \cdot capacity\_factor_{n,t,y^V,y,h} \cdot CAP_{n,t,y^V,y}
*         \quad t \ \in \ T^{INV}
*
* where :math:`T^{INV} \subseteq T` is the set of all technologies
* for which investment decisions and capacity constraints are relevant.
***
CAPACITY_CONSTRAINT(node,inv_tec,vintage,year,time)$( map_tec_time(node,inv_tec,year,time)
        AND map_tec_lifetime(node,inv_tec,vintage,year) )..
    SUM(mode$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) )
        =L= duration_time(time) * capacity_factor(node,inv_tec,vintage,year,time) * CAP(node,inv_tec,vintage,year) ;

***
* Equation CAPACITY_MAINTENANCE
* """"""""""""""""""""""""""""""
* This constraint deals with fixed costs for operation and maintainance (O&M) of technology capacity_maintainance.
* Capacity must be maintained over time until decommissioning (no mothballing), and fixed O\&M costs must be paid
* immediately after commissioning.
*
*  .. math::
*     CAP_{n,t,y^V,y} \leq
*     remaining\_capacity_{n,t,y^V,y} \cdot
*     \left\{ \begin{array}{ll}
*         duration\_period_{y^V} \cdot historical\_new\_capacity_{n,t,y^V} \quad & \text{if } y \ \text{is first model period} \\
*         duration\_period_{y^V} \cdot CAP\_NEW_{n,t,y^V} \quad & \text{if } y = y^V \\
*         CAP_{n,t,y^V,y-1} & \text{if } y > y^V \text{ and }
*                                  |y| - |y^V| < technical\_lifetime_{n,t,y^V} \end{array} \right\}
*         \quad \forall \ t \in T^{INV}
*
* The current formulation does not account for construction time in the constraints, but only adds a mark-up
* to the investment costs in the objective function.
***
CAPACITY_MAINTENANCE(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year) )..
    CAP(node,inv_tec,vintage,year) =L=
* discount the capacity in case the technical lifetime ends within a period
    remaining_capacity(node,inv_tec,vintage,year) * (
* historical installation (built before start of model horizon)
        ( duration_period(vintage) * historical_new_capacity(node,inv_tec,vintage)
            )$( historical(vintage) AND first_period(year) )
* new capacity built in the current period (vintage == year)
        + ( duration_period(vintage) * CAP_NEW(node,inv_tec,vintage)
            )$( year_order(year) EQ year_order(vintage) AND NOT historical(vintage) )
* total installed capacity at the end of the previous period
        + SUM(year2$( seq_period(year2,year) AND map_tec_lifetime(node,inv_tec,vintage,year2) ),
            CAP(node,inv_tec,vintage,year2) )
    ) ;

***
* Equation OPERATION_CONSTRAINT
* """""""""""""""""""""""""""""
* This constraint provides an upper bound on the total operation of installed capacity over a year.
*
*   .. math::
*      \sum_{m,h} ACT_{n,t,y^V,y,m,h}
*          \leq operation\_factor_{n,t,y^V,y} \cdot capacity\_factor_{n,t,y^V,y,m,\text{'year'}} \cdot CAP_{n,t,y^V,y}
*
* This constraint is only active if :math:`operation\_factor_{n,t,y^V,y} < 1`.
***
OPERATION_CONSTRAINT(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year)
        AND operation_factor(node,inv_tec,vintage,year) < 1 )..
    SUM((mode,time)$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) ) =L=
        operation_factor(node,inv_tec,vintage,year) * capacity_factor(node,inv_tec,vintage,year,'year')
        * CAP(node,inv_tec,vintage,year) ;

***
* Equation MIN_UTILIZATION_CONSTRAINT
* """""""""""""""""""""""""""""""""""
* This constraint provides a lower bound on the total utilization of installed capacity over a year.
*
*   .. math::
*      \sum_{m,h} ACT_{n,t,y^V,y,m,h} \geq min\_utilization\_factor_{n,t,y^V,y} \cdot CAP_{n,t,y^V,y}
*
* This constraint is only active if :math:`min\_utilization\_factor_{n,t,y^V,y}` is defined.
***
MIN_UTILIZATION_CONSTRAINT(node,inv_tec,vintage,year)$( map_tec_lifetime(node,inv_tec,vintage,year)
        AND min_utilization_factor(node,inv_tec,vintage,year) )..
    SUM((mode,time)$( map_tec_act(node,inv_tec,year,mode,time) ), ACT(node,inv_tec,vintage,year,mode,time) ) =G=
        min_utilization_factor(node,inv_tec,vintage,year) * CAP(node,inv_tec,vintage,year) ;

***
* Constraints representing renewable integration
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation RENEWABLES_EQUIVALENCE
* """""""""""""""""""""""""""""""
*
* This constraint defines the auxiliary variables :math:`REN`
* to be equal to the output of renewable technologies (summed over grades).
*
*  .. math::
*     \sum_{g} REN_{n,t,c,g,y,h} \leq
*     \sum_{\substack{n,t,m,l,h,h^{OD} \\ y^V \leq y  \\ \ l \in L^{REN} \subseteq L }}
*         input_{n^L,t,y^V,y,m,n,c,l,h,h^{OD}} \cdot ACT_{n^L,t,m,y,h}
*
* The set :math:`L^{REN} \subseteq L` denotes all levels for which the detailed representation of renewables applies.
***
RENEWABLES_EQUIVALENCE(node,renewable_tec,commodity,year,time)$(
        map_tec(node,renewable_tec,year) AND map_ren_com(node,renewable_tec,commodity,year) )..
    SUM(grade$( map_ren_grade(node,commodity,grade,year) ), REN(node,renewable_tec,commodity,grade,year,time) )
    =E= SUM((location,vintage,mode,level_renewable,time_act)$(
                 map_tec_act(node,renewable_tec,year,mode,time)
                 AND map_tec_lifetime(node,renewable_tec,vintage,year) ),
        input(location,renewable_tec,vintage,year,mode,node,commodity,level_renewable,time_act,time)
        * ACT(location,renewable_tec,vintage,year,mode,time) )
;

***
* Equation RENEWABLES_POTENTIAL_CONSTRAINT
* """"""""""""""""""""""""""""""""""""""""
* This constraint sets the potential potential by grade as the upper bound for the auxiliary variable :math:`REN`.
*
*  .. math::
*     \sum_{\substack{t,h \\ \ t \in T^{R} \subseteq t }} REN_{n,t,c,g,y,h}
*         \leq \sum_{\substack{l \\ l \in L^{R} \subseteq L }} renewable\_potential_{n,c,g,l,y}
*
***
RENEWABLES_POTENTIAL_CONSTRAINT(node,commodity,grade,year)$( map_ren_grade(node,commodity,grade,year) )..
    SUM((renewable_tec,time)$( map_ren_com(node,renewable_tec,commodity,year) ),
        REN(node,renewable_tec,commodity,grade,year,time) )
    =L= SUM(level_renewable, renewable_potential(node,commodity,grade,level_renewable,year) )
;

***
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
*     \sum_{y^V, h} CAP_{n,t,y^V,y} \cdot operation\_factor_{n,t,y^V,y} \cdot  \\
*        capacity\_factor_{n,t,y^V,y,h} \geq \sum_{g,h,l} REN_{n,t,c,g,y,h} / \\
*        renewable\_capacity\_factor_{n,c,g,l,y}
*
* This constraint is only active if :math:`renewable\_capacity\_factor_{n,c,g,l,y}` is defined.
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
                 / renewable_capacity_factor(node,commodity,grade,level_renewable,year))
;

***
* Constraints representing the firm capacity requirement
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The following constraint ensures that there is sufficient firm (dispatchable) capacity in each period.
* The formulation is based on Sullivan et al., 2013 :cite:`sullivan_VRE_2013`.
*
* The firm capacity a technology provides depends on their reliability factor per rating.
* The rating are defined depending on the share the single technology provides to the
* system. The reliablitiy factor of conventional powerplants is equal to 1. Therefore
* they provide their nameplate capacity as firm capacity.
* The reliability factor of wind and solar dependens on the share they have in the
* energy system. Therefore their reliability factor depend on the rating.
*
* Equation COMMODITY_USE_LEVEL
* """"""""""""""""""""""""""""
* This constraint defines the COMMODITY_USE_LEVEL as summed consumption of a
* commodity at a certain level during one year.
*
*   .. math::
*      COMMODITY\_USE_{n,c,l,y} = \sum_{n,t,y^V,m,h} input_{n,t,y^V,y,m,n,c,l,h,h} \cdot \\
*                duration\_time\_rel_{h,h} \cdot ACT_{n,t,y^V,y,m,h}
*
* This constraint is only active if :math:`peak\_load\_factor_{n,c,l,y,h}` is defined.
* The auxiliary variable :math:`COMMODITY\_USE_{n,c,l,y}` is only required
* for the equations :math:`FIRM\_CAPACITY\_CONSTRAINT` and :math:`FIRM\_CAPACITY\_SHARE`.
* WENN ENTWEDER PEAK LOAD ODER FLEXIBILITY DEMAND DA IST MUSS DIE COMM_USE BERECHNET WERDEN
***

COMMODITY_USE_LEVEL(node,commodity,level,year,time)$(
         peak_load_factor(node,commodity,level,year,time) OR
         SUM( (tec,vintage,mode,rating), flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating) ) )..
    COMMODITY_USE(node,commodity,level,year)
    =E= SUM( (location,tec,vintage,mode,time2)$( map_tec_act(location,tec,year,mode,time2)
                                                    AND map_tec_lifetime(location,tec,vintage,year) ),
                input(location,tec,vintage,year,mode,node,commodity,level,time2,time)
                * duration_time_rel(time,time2)
                * ACT(location,tec,vintage,year,mode,time2) )
;

Positive Variable
    ACT_SHARE(node,tec,vintage,year_all,commodity,level,time,rating)
;

* WENN ENTWEDER PEAK LOAD ODER FLEXIBILITY DEMAND DA IST UND RATING MUSS ?BER ACT_SHARE DIE BIN SIZE BERECHNET WERDEN
ACTIVITY_SHARE_BIN(node,tec,year,commodity,level,time,rating)$(
         rating_bin(node,tec,year,commodity,level,time,rating) )..
   sum(vintage$(sum(mode,map_tec_act(node,tec,year,mode,time)) AND map_tec_lifetime(node,tec,vintage,year)),
            ACT_SHARE(node,tec,vintage,year,commodity,level,time,rating) )
    =L= rating_bin(node,tec,year,commodity,level,time,rating) * COMMODITY_USE(node,commodity,level,year)
;

ACTIVITY_SHARE_TOTAL(node,tec,vintage,year,commodity,level,time)$(
        sum(rating$( rating_bin(node,tec,year,commodity,level,time,rating) ), 1 )
        AND sum(mode, map_tec_act(node,tec,year,mode,time))
        AND map_tec_lifetime(node,tec,vintage,year) )..
    sum((rating)$( rating_bin(node,tec,year,commodity,level,time,rating) ),
        ACT_SHARE(node,tec,vintage,year,commodity,level,time,rating) )
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
* Equation FIRM_CAPACITY_PROVISION
* """"""""""""""""""""""""""""""""
* Limits the firm capacity of the renewables technologies to the total installed capacity of each technology.
*
*   .. math::
*      \sum_{q,h} CAP\_FIRM_{n,t,c,l,y,q} \leq \sum_{y^V \leq y} CAP_{n,t,y^Y,y} \quad \forall t \in T^{INV}
*
* This constraint is only active if :math:`reliability\_factor_{n,t,y,c,l,h,q}` is defined.
***
FIRM_CAPACITY_PROVISION(node,inv_tec,year,commodity,level,time)$(
    reliability_factor(node,inv_tec,year,commodity,level,time,'firm') )..
        CAP_FIRM(node,inv_tec,commodity,level,year) =E=
        SUM((location,vintage,mode,time2)$(
              map_tec_act(location,inv_tec,year,mode,time2)
              AND map_tec_lifetime(location,inv_tec,vintage,year) ),
            output(location,inv_tec,vintage,year,mode,node,commodity,level,time2,time)
                * capacity_factor(node,inv_tec,vintage,year,time)
                * CAP(node,inv_tec,vintage,year) ) ;


Set rating_unfirm(rating) ;
rating_unfirm(rating) = yes ;
rating_unfirm('firm') = no ;

Set rating_unrated(rating) ;
rating_unrated(rating) = yes ;
rating_unrated('unrated') = no ;


***
* Equation FIRM_CAPACITY_CONSTRAINT
* """""""""""""""""""""""""""""""""
* This constraint ensures that there is sufficient firm (dispatchable) capacity in each period.
* The formulation is based on Sullivan et al., 2013 :cite:`sullivan_VRE_2013`.
*
*   .. math::
*      \sum_{t, q \substack{t \in T^{INV} \\ y^V \leq y} } reliability\_factor_{n,t,y,c,l,h,q} \cdot
*                CAP\_FIRM_{n,t,c,l,y,q} \geq \\
*         peak\_load\_factor_{n,c,l,y,h} \cdot COMMODITY\_USE_{n,c,l,y}
*
* This constraint is only active if :math:`peak\_load\_factor_{n,c,l,y,h}` is defined.
***
FIRM_CAPACITY_CONSTRAINT(node,commodity,level,year,time)$( peak_load_factor(node,commodity,level,year,time) )..
    SUM(inv_tec$( reliability_factor(node,inv_tec,year,commodity,level,time,'firm') ),
        reliability_factor(node,inv_tec,year,commodity,level,time,'firm')
        * CAP_FIRM(node,inv_tec,commodity,level,year) )
    + SUM((tec, mode, vintage, rating_unfirm)$(
        reliability_factor(node,tec,year,commodity,level,time,rating_unfirm)
            AND map_tec_act(node,tec,year,mode,time)
            AND map_tec_lifetime(node,tec,vintage,year) ),
        reliability_factor(node,tec,year,commodity,level,time,rating_unfirm)
        * ACT_SHARE(node,tec,vintage,year,commodity,level,time,rating_unfirm) )
    =G= peak_load_factor(node,commodity,level,year,time) * COMMODITY_USE(node,commodity,level,year)
;


***
* .. _flexibility_constraint:
*
* Equation OPERATING_RESERVE_CONSTRAINT
* """""""""""""""""""""""""""""""""""""
* This constraint ensures that, in each sub-annual time slice, there is a sufficient share of flexible technologies in
* the power generation mix. This heading is a placeholder for a new formulation using the extended index set structure.
***
OPERATING_RESERVE_CONSTRAINT(node,commodity,level,year,time)$(
        sum( (tec, vintage, mode, rating),
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
    + SUM((tec, vintage, mode, rating_unrated)$( flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating_unrated)
            AND map_tec_act(node,tec,year,mode,time)
            AND map_tec_lifetime(node,tec,vintage,year)),
        flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating_unrated)
        * ACT_SHARE(node,tec,vintage,year,commodity,level,time,rating_unrated) )
    =G= 0
;

ACT.LO(node,tec,vintage,year,mode,time)$sum( ( commodity,level,rating), flexibility_factor(node,tec,vintage,year,mode,commodity,level,time,rating) ) = 0 ;

***
* Bounds on capacity and activity
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation NEW_CAPACITY_BOUND_UP
* """"""""""""""""""""""""""""""
* This constraint provides upper bounds on new capacity installation.
*
*   .. math::
*      CAP\_NEW_{n,t,y} \leq bound\_new\_capacity\_up_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
NEW_CAPACITY_BOUND_UP(node,inv_tec,year)$( is_bound_new_capacity_up(node,inv_tec,year) )..
    CAP_NEW(node,inv_tec,year) =L= bound_new_capacity_up(node,inv_tec,year)
%SLACK_CAP_NEW_BOUND_UP% + SLACK_CAP_NEW_BOUND_UP(node,inv_tec,year)
;

***
* Equation NEW_CAPACITY_BOUND_LO
* """"""""""""""""""""""""""""""
* This constraint provides lower bounds on new capacity installation.
*
*   .. math::
*      CAP\_NEW_{n,t,y} \geq bound\_new\_capacity\_lo_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
NEW_CAPACITY_BOUND_LO(node,inv_tec,year)$( is_bound_new_capacity_lo(node,inv_tec,year) )..
    CAP_NEW(node,inv_tec,year) =G= bound_new_capacity_lo(node,inv_tec,year)
%SLACK_CAP_NEW_BOUND_LO% - SLACK_CAP_NEW_BOUND_LO(node,inv_tec,year)
;

***
* Equation TOTAL_CAPACITY_BOUND_UP
* """"""""""""""""""""""""""""""""
* This constraint gives upper bounds on the total installed capacity of a technology in a specific year of operation
* summed over all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} CAP_{n,t,y,y^V} \leq bound\_total\_capacity\_up_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
TOTAL_CAPACITY_BOUND_UP(node,inv_tec,year)$( is_bound_total_capacity_up(node,inv_tec,year) )..
    SUM(vintage$( map_period(vintage,year) AND map_tec_lifetime(node,inv_tec,vintage,year) ),
        CAP(node,inv_tec,vintage,year) )
    =L= bound_total_capacity_up(node,inv_tec,year)
%SLACK_CAP_TOTAL_BOUND_UP% + SLACK_CAP_TOTAL_BOUND_UP(node,inv_tec,year)
;

***
* Equation TOTAL_CAPACITY_BOUND_LO
* """"""""""""""""""""""""""""""""
* This constraint gives lower bounds on the total installed capacity of a technology.
*
*   .. math::
*      \sum_{y^V \leq y} CAP_{n,t,y,y^V} \geq bound\_total\_capacity\_lo_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
TOTAL_CAPACITY_BOUND_LO(node,inv_tec,year)$( is_bound_total_capacity_lo(node,inv_tec,year) )..
    SUM(vintage$( map_period(vintage,year) AND map_tec_lifetime(node,inv_tec,vintage,year) ),
        CAP(node,inv_tec,vintage,year) )
     =G= bound_total_capacity_lo(node,inv_tec,year)
%SLACK_CAP_TOTAL_BOUND_LO% - SLACK_CAP_TOTAL_BOUND_LO(node,inv_tec,year)
;

***
* Equation ACTIVITY_BOUND_UP
* """"""""""""""""""""""""""
* This constraint provides lower bounds of a technology activity by mode, summed over all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} ACT_{n,t,y^V,y,m,h} \leq bound\_activity\_up_{n,t,m,y,h}
*
***
ACTIVITY_BOUND_UP(node,tec,year,mode,time)$( map_tec_act(node,tec,year,mode,time)
        AND is_bound_activity_up(node,tec,year,mode,time) )..
    SUM(vintage$( map_tec_lifetime(node,tec,vintage,year) ), ACT(node,tec,vintage,year,mode,time) ) =L=
    bound_activity_up(node,tec,year,mode,time)
%SLACK_ACT_BOUND_UP% + SLACK_ACT_BOUND_UP(node,tec,year,mode,time)
;

***
* Equation ACTIVITY_BOUND_LO
* """"""""""""""""""""""""""
* This constraint provides lower bounds of a technology activity by mode summed over all vintages.
*
*   .. math::
*      \sum_{y^V \leq y} ACT_{n,t,y^V,y,m,h} \geq bound\_activity\_lo_{n,t,y,m,h}
*
* We assume that :math:`bound\_activity\_lo_{n,t,y,m,h} = 0`
* unless explicitly stated otherwise.
***
ACTIVITY_BOUND_LO(node,tec,year,mode,time)$( map_tec_act(node,tec,year,mode,time) )..
    SUM(vintage$( map_tec_lifetime(node,tec,vintage,year) ), ACT(node,tec,vintage,year,mode,time) ) =G=
    bound_activity_lo(node,tec,year,mode,time)
%SLACK_ACT_BOUND_LO% - SLACK_ACT_BOUND_LO(node,tec,year,mode,time)
;

***
* .. _dynamic_constraints:
*
* Dynamic constraints on market penetration
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* The constraints in this section specify dynamic upper and lower bounds on new capacity and activity,
* i.e., constraints on market penetration and rate of expansion or phase-out of a technology.
*
* The formulation directly includes the option for 'soft' relaxations of dynamic constraints
* (cf. Keppo and Strubegger, 2010 :cite:`keppo_short_2010`).
*
* Equation NEW_CAPACITY_CONSTRAINT_UP
* """""""""""""""""""""""""""""""""""
* The level of new capacity additions cannot be greater than an initial value (compounded over the period duration),
* annual growth of the existing 'capital stock', and a "soft" relaxation of the upper bound.
*
*  .. math::
*     CAP\_NEW_{n,t,y}
*         \leq & ~ initial\_new\_capacity\_up_{n,t,y}
*             \cdot \frac{ \Big( 1 + growth\_new\_capacity\_up_{n,t,y} \Big)^{|y|} - 1 }
*                        { growth\_new\_capacity\_up_{n,t,y} } \\
*              & + \Big( CAP\_NEW_{n,t,y-1} + historical\_new\_capacity_{n,t,y-1} \Big) \\
*              & \hspace{2 cm} \cdot \Big( 1 + growth\_new\_capacity\_up_{n,t,y} \Big)^{|y|} \\
*              & + CAP\_NEW\_UP_{n,t,y} \cdot \Bigg( \Big( 1 + soft\_new\_capacity\_up_{n,t,y}\Big)^{|y|} - 1 \Bigg) \\
*         & \quad \forall \ t \ \in \ T^{INV}
*
* Here, :math:`|y|` is the number of years in period :math:`y`, i.e., :math:`duration\_period_{y}`.
***
NEW_CAPACITY_CONSTRAINT_UP(node,inv_tec,year)$( map_tec(node,inv_tec,year)
        AND is_dynamic_new_capacity_up(node,inv_tec,year) )..
* actual new capacity
    CAP_NEW(node,inv_tec,year) =L=
* initial new capacity (compounded over the duration of the period)
        initial_new_capacity_up(node,inv_tec,year) * (
            ( ( POWER( 1 + growth_new_capacity_up(node,inv_tec,year) , duration_period(year) ) - 1 )
                / growth_new_capacity_up(node,inv_tec,year) )$( growth_new_capacity_up(node,inv_tec,year) )
              + ( duration_period(year) )$( NOT growth_new_capacity_up(node,inv_tec,year) )
            )
* growth of 'capital stock' from previous period
        + SUM(year_all2$( seq_period(year_all2,year) ),
            CAP_NEW(node,inv_tec,year_all2)$( map_tec(node,inv_tec,year_all2) AND model_horizon(year_all2) )
              + historical_new_capacity(node,inv_tec,year_all2) )
              # placeholder for spillover across nodes, technologies, periods (other than immediate predecessor)
            * POWER( 1 + growth_new_capacity_up(node,inv_tec,year) , duration_period(year) )
* 'soft' relaxation of dynamic constraints
        + ( CAP_NEW_UP(node,inv_tec,year)
            * ( POWER( 1 + soft_new_capacity_up(node,inv_tec,year) , duration_period(year) ) - 1 )
           )$( soft_new_capacity_up(node,inv_tec,year) )
* optional relaxation for calibration and debugging
%SLACK_CAP_NEW_DYNAMIC_UP% + SLACK_CAP_NEW_DYNAMIC_UP(node,inv_tec,year)
;

* GAMS implementation comment:
* The sums in the constraint have to be over `year_all2` (not `year2`) to also get the dynamic effect from historical
* new capacity. If one would sum over `year2`, periods prior to the first model year would be ignored.

***
* Equation NEW_CAPACITY_SOFT_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic constraint on new capacity (investment) does not exceed
* the level of the investment in the same period (cf. Keppo and Strubegger, 2010 :cite:`keppo_short_2010`).
*
*  .. math::
*     CAP\_NEW\_UP_{n,t,y} \leq CAP\_NEW_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
NEW_CAPACITY_SOFT_CONSTRAINT_UP(node,inv_tec,year)$( soft_new_capacity_up(node,inv_tec,year) )..
    CAP_NEW_UP(node,inv_tec,year) =L= CAP_NEW(node,inv_tec,year) ;

***
* Equation NEW_CAPACITY_CONSTRAINT_LO
* """""""""""""""""""""""""""""""""""
* This constraint gives dynamic lower bounds on new capacity.
*
*  .. math::
*     CAP\_NEW_{n,t,y}
*         \geq & - initial\_new\_capacity\_lo_{n,t,y}
*             \cdot \frac{ \Big( 1 + growth\_new\_capacity\_lo_{n,t,y} \Big)^{|y|} }
*                        { growth\_new\_capacity\_lo_{n,t,y} } \\
*              & + \Big( CAP\_NEW_{n,t,y-1} + historical\_new\_capacity_{n,t,y-1} \Big) \\
*              & \hspace{2 cm} \cdot \Big( 1 + growth\_new\_capacity\_lo_{n,t,y} \Big)^{|y|} \\
*              & - CAP\_NEW\_LO_{n,t,y} \cdot \Bigg( \Big( 1 + soft\_new\_capacity\_lo_{n,t,y}\Big)^{|y|} - 1 \Bigg) \\
*         & \quad \forall \ t \ \in \ T^{INV}
*
***
NEW_CAPACITY_CONSTRAINT_LO(node,inv_tec,year)$( map_tec(node,inv_tec,year)
        AND is_dynamic_new_capacity_lo(node,inv_tec,year) )..
* actual new capacity
    CAP_NEW(node,inv_tec,year) =G=
* initial new capacity (compounded over the duration of the period)
        - initial_new_capacity_lo(node,inv_tec,year) * (
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
           )$( soft_new_capacity_lo(node,inv_tec,year) )
* optional relaxation for calibration and debugging
%SLACK_CAP_NEW_DYNAMIC_LO% - SLACK_CAP_NEW_DYNAMIC_LO(node,inv_tec,year)
;

***
* Equation NEW_CAPACITY_SOFT_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic constraint on new capacity does not exceed
* level of the investment in the same year.
*
*   .. math::
*      CAP\_NEW\_LO_{n,t,y} \leq CAP\_NEW_{n,t,y} \quad \forall \ t \ \in \ T^{INV}
*
***
NEW_CAPACITY_SOFT_CONSTRAINT_LO(node,inv_tec,year)$( soft_new_capacity_lo(node,inv_tec,year) )..
    CAP_NEW_LO(node,inv_tec,year) =L= CAP_NEW(node,inv_tec,year) ;

***
* Equation ACTIVITY_CONSTRAINT_UP
* """""""""""""""""""""""""""""""
* This constraint gives dynamic upper bounds on the market penetration of a technology activity.
*
*  .. math::
*     \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}
*         \leq & ~ initial\_activity\_up_{n,t,y,h}
*             \cdot \frac{ \Big( 1 + growth\_activity\_up_{n,t,y,h} \Big)^{|y|} - 1 }
*                        { growth\_activity\_up_{n,t,y,h} } \\
*             & + \bigg( \sum_{y^V \leq y-1,m} ACT_{n,t,y^V,y-1,m,h}
*                         + \sum_{m} historical\_activity_{n,t,y-1,m,h} \bigg) \\
*             & \hspace{2 cm} \cdot \Big( 1 + growth\_activity\_up_{n,t,y,h} \Big)^{|y|} \\
*             & + ACT\_UP_{n,t,y,h} \cdot \Bigg( \Big( 1 + soft\_activity\_up_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)
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
* Equation ACTIVITY_SOFT_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
* level of the activity.
*
*   .. math::
*      ACT\_UP_{n,t,y,h} \leq \sum_{y^V \leq y,m} ACT_{n^L,t,y^V,y,m,h}
*
***
ACTIVITY_SOFT_CONSTRAINT_UP(node,tec,year,time)$( soft_activity_up(node,tec,year,time) )..
    ACT_UP(node,tec,year,time) =L=
        SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_act(node,tec,year,mode,time) ),
            ACT(node,tec,vintage,year,mode,time) ) ;

***
* Equation ACTIVITY_CONSTRAINT_LO
* """""""""""""""""""""""""""""""
* This constraint gives dynamic lower bounds on the market penetration of a technology activity.
*
*  .. math::
*     \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}
*         \geq & - initial\_activity\_lo_{n,t,y,h}
*             \cdot \frac{ \Big( 1 + growth\_activity\_lo_{n,t,y,h} \Big)^{|y|} - 1 }
*                        { growth\_activity\_lo_{n,t,y,h} } \\
*             & + \bigg( \sum_{y^V \leq y-1,m} ACT_{n,t,y^V,y-1,m,h}
*                         + \sum_{m} historical\_activity_{n,t,y-1,m,h} \bigg) \\
*             & \hspace{2 cm} \cdot \Big( 1 + growth\_activity\_lo_{n,t,y,h} \Big)^{|y|} \\
*             & - ACT\_LO_{n,t,y,h} \cdot \Bigg( \Big( 1 + soft\_activity\_lo_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)
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
* Equation ACTIVITY_SOFT_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""
* This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
* level of the activity.
*
*   .. math::
*      ACT\_LO_{n,t,y,h} \leq \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}
*
***
ACTIVITY_SOFT_CONSTRAINT_LO(node,tec,year,time)$( soft_activity_lo(node,tec,year,time) )..
    ACT_LO(node,tec,year,time) =L=
        SUM((vintage,mode)$( map_tec_lifetime(node,tec,vintage,year) AND map_tec_act(node,tec,year,mode,time) ),
            ACT(node,tec,vintage,year,mode,time) ) ;

*----------------------------------------------------------------------------------------------------------------------*
***
* Emission section
* ----------------
*
* Auxiliary variable for aggregate emissions
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation EMISSION_EQUIVALENCE
* """""""""""""""""""""""""""""
* This constraint simplifies the notation of emissions aggregated over different technology types
* and the land-use model emulator. The formulation includes emissions from all sub-nodes :math:`n^L` of :math:`n`.
*
*   .. math::
*      EMISS_{n,e,\widehat{t},y} =
*          \sum_{n^L \in N(n)} \Bigg(
*              \sum_{t \in T(\widehat{t}),y^V \leq y,m,h }
*                  emission\_factor_{n^L,t,y^V,y,m,e} \cdot ACT_{n^L,t,y^V,y,m,h} \\
*              + \sum_{s} \ land\_emission_{n^L,s,y,e} \cdot LAND_{n^L,s,y}
*                   \text{ if } \widehat{t} \in \widehat{T}^{LAND} \Bigg)
*
***
EMISSION_EQUIVALENCE(node,emission,type_tec,year)..
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
* Equation EMISSION_CONSTRAINT
* """"""""""""""""""""""""""""
* This constraint enforces upper bounds on emissions (by emission type). For all bounds that include multiple periods,
* the parameter :math:`bound\_emission_{n,\widehat{e},\widehat{t},\widehat{y}}` is scaled to represent average annual
* emissions over all years included in the year-set :math:`\widehat{y}`.
*
* The formulation includes historical emissions and allows to model constraints ranging over both the model horizon
* and historical periods.
*
*   .. math::
*      \frac{
*          \sum_{y' \in Y(\widehat{y}), e \in E(\widehat{e})}
*              \begin{array}{l}
*                  duration\_period_{y'} \cdot emission\_scaling_{\widehat{e},e} \cdot \\
*                  \Big( EMISS_{n,e,\widehat{t},y'} + \sum_{m} historical\_emission_{n,e,\widehat{t},y'} \Big)
*              \end{array}
*          }
*        { \sum_{y' \in Y(\widehat{y})} duration\_period_{y'} }
*      \leq bound\_emission_{n,\widehat{e},\widehat{t},\widehat{y}}
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
* Land-use model emulator section
* -------------------------------
*
* Bounds on total land use
* ^^^^^^^^^^^^^^^^^^^^^^^^
*
* Equation LAND_CONSTRAINT
* """"""""""""""""""""""""
* This constraint enforces a meaningful result of the land-use model emulator,
* in particular a bound on the total land used in |MESSAGEix|.
* The linear combination of land scenarios must be equal to 1.
*
*  .. math::
*     \sum_{s \in S} LAND_{n,s,y} = 1
*
***
LAND_CONSTRAINT(node,year)$( SUM(land_scenario$( map_land(node,land_scenario,year) ), 1 ) ) ..
    SUM(land_scenario$( map_land(node,land_scenario,year) ), LAND(node,land_scenario,year) ) =E= 1 ;

***
* Dynamic constraints on land use
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* These constraints enforces upper and lower bounds on the change rate per land scenario.
*
* Equation DYNAMIC_LAND_SCEN_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     LAND_{n,s,y}
*         \leq & initial\_land\_scen\_up_{n,s,y}
*             \cdot \frac{ \Big( 1 + growth\_land\_scen\_up_{n,s,y} \Big)^{|y|} - 1 }
*                        { growth\_land\_scen\_up_{n,s,y} } \\
*              & + \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big)
*                  \cdot \Big( 1 + growth\_land\_scen\_up_{n,s,y} \Big)^{|y|}
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
* Equation DYNAMIC_LAND_SCEN_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     LAND_{n,s,y}
*         \geq & - initial\_land\_scen\_lo_{n,s,y}
*             \cdot \frac{ \Big( 1 + growth\_land\_scen\_lo_{n,s,y} \Big)^{|y|} - 1 }
*                        { growth\_land\_scen\_lo_{n,s,y} } \\
*              & + \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big)
*                  \cdot \Big( 1 + growth\_land\_scen\_lo_{n,s,y} \Big)^{|y|}
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
* Equation DYNAMIC_LAND_TYPE_CONSTRAINT_UP
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \sum_{s \in S} land\_use_{n,s,y,u} &\cdot LAND_{n,s,y}
*         \leq initial\_land\_up_{n,y,u}
*             \cdot \frac{ \Big( 1 + growth\_land\_up_{n,y,u} \Big)^{|y|} - 1 }
*                        { growth\_land\_up_{n,y,u} } \\
*              & + \Big( \sum_{s \in S} \big( land\_use_{n,s,y-1,u}
*                          + dynamic\_land\_up_{n,s,y-1,u} \big) \\
*                            & \quad \quad \cdot \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big) \Big) \\
*                            & \quad \cdot \Big( 1 + growth\_land\_up_{n,y,u} \Big)^{|y|}
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
* Equation DYNAMIC_LAND_TYPE_CONSTRAINT_LO
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \sum_{s \in S} land\_use_{n,s,y,u} &\cdot LAND_{n,s,y}
*         \geq - initial\_land\_lo_{n,y,u}
*             \cdot \frac{ \Big( 1 + growth\_land\_lo_{n,y,u} \Big)^{|y|} - 1 }
*                        { growth\_land\_lo_{n,y,u} } \\
*              & + \Big( \sum_{s \in S} \big( land\_use_{n,s,y-1,u}
*                          + dynamic\_land\_lo_{n,s,y-1,u} \big) \\
*                            & \quad \quad \cdot \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big) \Big) \\
*                            & \quad \cdot \Big( 1 + growth\_land\_lo_{n,y,u} \Big)^{|y|}
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
* RELATION_EQUIVALENCE
* """"""""""""""""""""
*   .. math::
*      REL_{r,n,y} = \sum_{t} \Bigg(
*          & \ relation\_new\_capacity_{r,n,y,t} \cdot CAP\_NEW_{n,t,y} \\[4 pt]
*          & + relation\_total\_capacity_{r,n,y,t} \cdot \sum_{y^V \leq y} \ CAP_{n,t,y^V,y} \\
*          & + \sum_{n^L,y',m,h} \ relation\_activity_{r,n,y,n^L,t,y',m} \\
*          & \quad \quad \cdot \Big( \sum_{y^V \leq y'} ACT_{n^L,t,y^V,y',m,h}
*                              + historical\_activity_{n^L,t,y',m,h} \Big) \Bigg)
*
* The parameter :math:`historical\_new\_capacity_{r,n,y}` is not included here, because relations can only be active
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
* Equation RELATION_CONSTRAINT_UP
* """""""""""""""""""""""""""""""
*   .. math::
*      REL_{r,n,y} \leq relation\_upper_{r,n,y}
***
RELATION_CONSTRAINT_UP(relation,node,year)$( is_relation_upper(relation,node,year) )..
    REL(relation,node,year)
%SLACK_RELATION_BOUND_UP% - SLACK_RELATION_BOUND_UP(relation,node,year)
    =L= relation_upper(relation,node,year) ;

***
* Equation RELATION_CONSTRAINT_LO
* """""""""""""""""""""""""""""""
*   .. math::
*      REL_{r,n,y} \geq relation\_lower_{r,n,y}
***
RELATION_CONSTRAINT_LO(relation,node,year)$( is_relation_lower(relation,node,year) )..
    REL(relation,node,year)
%SLACK_RELATION_BOUND_LO% + SLACK_RELATION_BOUND_LO(relation,node,year)
    =G= relation_lower(relation,node,year) ;

*----------------------------------------------------------------------------------------------------------------------*
* model statements                                                                                                     *
*----------------------------------------------------------------------------------------------------------------------*

Model MESSAGE_LP / all / ;

MESSAGE_LP.holdfixed = 1 ;
MESSAGE_LP.optfile = 1 ;
MESSAGE_LP.optcr = 0 ;



