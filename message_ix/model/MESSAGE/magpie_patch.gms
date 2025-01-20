Set commodity_tau /set.commodity/ ;

$onMulti
set commodity_tau /
"Landuse intensity indicator Tau"
/;
$offMulti

Parameters
bin_tau(commodity_tau)   binary parameter for k
par_land_output(node, land_scenario, year_all2, commodity,commodity_tau, level, time) parameter alias for a
land_output_(node, land_scenario, year_all2, level, time)   pseudo a
;

bin_tau("Landuse intensity indicator Tau") = yes ;

par_land_output(node, land_scenario, year_all2, commodity,commodity_tau, level, time)$(ord(commodity) eq ord(commodity_tau) and bin_tau(commodity_tau)) = land_output(node, land_scenario, year_all2, commodity, level, time) ;
land_output_(node, land_scenario, year_all2, level, time) = sum((commodity,commodity_tau), par_land_output(node, land_scenario, year_all2, commodity,commodity_tau, level, time));





Positive Variables
* land-use model emulator
    LAND_COST_NEW(node, year_all)                                land cost including debt from scenario switching
    LAND_COST_DEBT(node, year_all,year_all2)                     land cost debt from scenario switching
    EMISS_LU_AUX(node,emission,type_tec,year_all,year_all2)      positive emissions overshoot of historic emissions compared to chosen land scenario mix
;

Variables
* auxiliary variable for aggregate emissions from land-use model emulator
    EMISS_LU(node,emission,type_tec,year_all)                    aggregate emissions from land-use model emulator

Equations
    COST_ACCOUNTING_NODAL_MAgPIE                                 modified cost accounting nodal for MESSAGE-MAgPIE
    EMISSION_EQUIVALENCE_MAgPIE                                  for magpie
    EMISSION_EQUIVALENCE_AUX_ANNUAL                              auxiliary equation calculating land-use emissions from annual scenario input
    EMISSION_EQUIVALENCE_AUX_CUMU                                auxiliary equation calculating land-use emissions from cumulative scenario input
    EMISSION_EQUIVALENCE_AUX_CUMU_AUX                            auxiliary equation calculating the land-use emissions overshoot if positive compared to historic scenario mix
    LAND_COST_CUMU                                               land cost including debt from scenario switching
    LAND_COST_CUMU_DEBT                                          land cost debt from scenario switching
    DYNAMIC_LAND_TYPE_CONSTRAINT_LO_MAgPIE                       for magpie
    TAU_CONSTRAINT                                               constraint on land-use intensity growth (regional tau is not allowed to shrink)
;


***
* Regional system cost accounting function
* ----------------------------------------
*
* Accounting of regional system costs over time
* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*
* .. _equation_cost_accounting_nodal:
*
* Equation COST_ACCOUNTING_NODAL_MAgPIE
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
COST_ACCOUNTING_NODAL_MAgPIE(node, year)..
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
    + LAND_COST_NEW(node, year)
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


* Equation EMISSION_EQUIVALENCE_MAgPIE
* """""""""""""""""""""""""""""
* This constraint simplifies the notation of emissions aggregated over different technology types
* and the land-use model emulator. The formulation includes emissions from all sub-nodes :math:`n^L` of :math:`n`.
*
*   .. math::
*      \text{EMISS}_{n,e,\widehat{t},y} =
*          \sum_{n^L \in N(n)} \Bigg(
*              \sum_{t \in T(\widehat{t}),y^V \leq y,m,h }
*                  \text{emission_factor}_{n^L,t,y^V,y,m,e} \cdot \text{ACT}_{n^L,t,y^V,y,m,h} \\
*              + \text{EMISS_LU}_{n^L,e,\widehat{t},y} \text{ if } \widehat{t} \in \widehat{T}^{LAND} \Bigg)
*
***
EMISSION_EQUIVALENCE_MAgPIE(node,emission,type_tec,year)..
    EMISS(node,emission,type_tec,year)
    =E=
    SUM(location$( map_node(node,location) ),
* emissions from technology activity
        SUM((tec,vintage,mode,time)$( cat_tec(type_tec,tec)
            AND map_tec_act(location,tec,year,mode,time) AND map_tec_lifetime(location,tec,vintage,year) ),
        emission_factor(location,tec,vintage,year,mode,emission) * ACT(location,tec,vintage,year,mode,time) )
* emissions from land-use activity based on land scenario mix and its path dependencies
* for selected variables (emission_cumulative) if 'type_tec' is included in the dynamic set 'type_tec_land'
        + EMISS_LU(location,emission,type_tec,year) $ ( type_tec_land(type_tec) )
      ) ;


* .. _equation_emission_equivalence_aux_annual:
*
* Equation EMISSION_EQUIVALENCE_AUX_ANNUAL
* """""""""""""""""""""""""""""
* This auxillary equation accounts for emissions in set emission_annual without considering a path-dependent emission debt
*
*
*   .. math::
*      \text{EMISS_LU}_{n^L,e^a,\widehat{t},y} =
*               \sum_{s} \text{land_emission}_{n^L,s,y,e^a} \cdot \text{LAND}_{n^L,s,y}
*
***
EMISSION_EQUIVALENCE_AUX_ANNUAL(location,emission,type_tec,year) $ emission_annual(emission)..
    EMISS_LU(location,emission,type_tec,year)
    =E=
    SUM(land_scenario ,
            land_emission(location,land_scenario,year,emission) * LAND(location,land_scenario,year)
    ) ;


* .. _equation_emission_equivalence_aux_cumu:
*
* Equation EMISSION_EQUIVALENCE_AUX_CUMU
* """""""""""""""""""""""""""""
* This auxillary equation accounts for emissions in set emission_cumulative considering a path-dependent emission debt
* This debt is calculated by comparing the historic emissions of the current time step's land-use mix in variable LAND
* to the emissions of the actually chosen scenario mix of previous timesteps, including any emission debts accounted for
* before. To do so, first, for every previous model time step, the emissions in those steps under the current land-use
* scenario mix and the delta to the chosen mix in that time step are calculated. To ensure any historic emission debt is
* only accounted for the first time step(s) it occurs, the accounted debt towards any previous time step is subtracted
* towards a minimum of 0.
*
*
*   .. math::
*      \text{EMISS_LU}_{n^L,e^c,\widehat{t},y} =
*               \sum_{s} \text{land_emission}_{n^L,s,y,e^c} \cdot \text{LAND}_{n^L,s,y} \\
*              + \sum_{\widehat{y}} \text{EMISS_LU_AUX}_{n^L,e^c,\widehat{t},y,\widehat{y}}
*
***
EMISSION_EQUIVALENCE_AUX_CUMU(location,emission,type_tec,year) $ emission_cumulative(emission)..
    EMISS_LU(location,emission,type_tec,year)
    =E=
    SUM(land_scenario ,
            land_emission(location,land_scenario,year,emission) * LAND(location,land_scenario,year) )
    + SUM(year2, EMISS_LU_AUX(location,emission,type_tec,year, year2) )
    ;


* find positive emissions overshoot for history of current land scenario mix compared to mix of earlier time steps
EMISSION_EQUIVALENCE_AUX_CUMU_AUX(location,emission,type_tec,year,year2) $ (emission_cumulative(emission) AND model_horizon(year) AND year2.pos < year.pos)..
    EMISS_LU_AUX(location,emission,type_tec,year,year2) $ ( year2.pos < year.pos )
    =G=
    SUM(land_scenario,
            LAND(location, land_scenario, year) * land_emission(location, land_scenario, year2, emission)
            - LAND(location, land_scenario, year2) * land_emission(location, land_scenario, year2, emission) )
        - SUM(year3 $ ( year3.pos < year.pos AND year2.pos < year3.pos ), EMISS_LU_AUX(location, emission,type_tec, year3, year2) ) ;

* calculate scenario cost of current land scenario mix under consideration of its path dependencies and
* associated cost differences compared to the land scenario mix of earlier time steps
LAND_COST_CUMU(location, year)$( model_horizon(year) )..
       LAND_COST_NEW(location, year) =E=
       SUM(land_scenario$( land_cost(location,land_scenario,year) ),
       land_cost(location,land_scenario,year) * LAND(location,land_scenario,year) )
       + SUM(year2,
            LAND_COST_DEBT(location, year, year2)
            ) ;

LAND_COST_CUMU_DEBT(location, year, year2) $ (model_horizon(year) AND year2.pos < year.pos)..
        LAND_COST_DEBT(location, year, year2) $ ( year2.pos < year.pos ) =G=
        SUM(land_scenario$( land_cost(location,land_scenario,year) ),
            LAND(location, land_scenario, year) * land_cost(location,land_scenario,year2)
            - LAND(location, land_scenario, year2) * land_cost(location,land_scenario,year2) ) * df_period(year2) / df_period(year)
        - SUM(year3 $ ( year3.pos < year.pos AND year2.pos < year3.pos ), LAND_COST_DEBT(location, year3, year2) ) ;

***
* .. _equation_dynamic_land_type_constraint_lo:
*
* Equation DYNAMIC_LAND_TYPE_CONSTRAINT_LO_MAgPIE
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
DYNAMIC_LAND_TYPE_CONSTRAINT_LO_MAgPIE(node,year,land_type)$( is_dynamic_land_lo(node,year,land_type) )..
* amount of land assigned to specific type in current period
    SUM(land_scenario$( map_land(node,land_scenario,year) ),
        land_use(node,land_scenario,year,land_type) * LAND(node,land_scenario,year) ) =G=
* initial 'new' land used for that type (compounded over the duration of the period)
        - initial_land_lo(node,year,land_type) * (
            ( ( POWER( 1 + growth_land_lo(node,year,land_type) , duration_period(year) ) - 1 )
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


***
*
* To ensure correct replication of MAgPIE behavior, the following constraint ensures that
* land-use intensity cannot decrease over time
*
* .. _equation_tau_constraint:
*
* Equation TAU_CONSTRAINT
* """"""""""""""""""""""""""""""""""""""""
*
*  .. math::
*     \sum_{s \in S} \text{land_output Tau}_{n,s,y,l,h} &\cdot \text{LAND}_{n,s,y}
*         \geq \sum_{s \in S} \big( \text{land_output Tau}_{n,s,y-1,l,h}
*                            & \quad \quad \cdot \big( \text{LAND}_{n,s,y-1} + \text{historical_land}_{n,s,y-1} \big) \big)
*
***

TAU_CONSTRAINT(node, year, level, time) ..
   SUM(land_scenario$( map_land(node,land_scenario,year) ),
        land_output_(node, land_scenario, year, level, time)
          * LAND(node, land_scenario, year)
        ) =G=
    SUM((year_all2)$( seq_period(year_all2,year) ),
        SUM(land_scenario$( map_land(node,land_scenario,year) ),
            land_output_(node, land_scenario, year_all2, level, time)
              * ( LAND(node, land_scenario, year_all2) $ ( model_horizon(year_all2) )
                  + historical_land(node,land_scenario,year_all2) )
            )
      )
;


Model MESSAGE_MAgPIE_LP / all
*                       list all equations to be removed from MESSAGE-ix default
                        - COST_ACCOUNTING_NODAL
                        - EMISSION_EQUIVALENCE
                        - DYNAMIC_LAND_TYPE_CONSTRAINT_LO
*                       list all equations to be added for connection MAgPIE to MESSAGE-ix
                        + COST_ACCOUNTING_NODAL_MAgPIE
                        + EMISSION_EQUIVALENCE_MAgPIE
                        + EMISSION_EQUIVALENCE_AUX_ANNUAL
                        + EMISSION_EQUIVALENCE_AUX_CUMU
                        + EMISSION_EQUIVALENCE_AUX_CUMU_AUX
                        + LAND_COST_CUMU
                        + LAND_COST_CUMU_DEBT
                        + DYNAMIC_LAND_TYPE_CONSTRAINT_LO_MAgPIE
                        + TAU_CONSTRAINT
/ ;

MESSAGE_MAgPIE_LP.optfile = 1 ;