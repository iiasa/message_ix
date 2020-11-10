***
* Auxiliary investment parameters
* ===============================
*
***

* compute the scaling investment parameters for all periods in the model horizon
year(year_all)$( model_horizon(year_all) ) = yes ;

* compute the technical lifetime remaining beyond the overall model horizon
beyond_horizon_lifetime(node,inv_tec,vintage)$( map_tec(node,inv_tec,vintage) ) =
    technical_lifetime(node,inv_tec,vintage) - remaining_years(vintage) ;
beyond_horizon_lifetime(node,inv_tec,vintage)$( beyond_horizon_lifetime(node,inv_tec,vintage) < 0 ) = 0 ;

***
* Levelized capital costs
* -----------------------
* For the 'soft' relaxations of the dynamic constraints and the associated penalty factor in the objective function,
* we need to compute the parameter :math:`levelized\_cost_{n,t,y}`.
*
* .. math::
*    levelized\_cost_{n,t,m,y,h} := \
*        & inv\_cost_{n,t,y} \cdot \frac{ interestrate_{y} \cdot \left( 1 + interestrate_{y} \right)^{|y|} }
*                                      { \left( 1 + interestrate_{y} \right)^{|y|} - 1 } \\
*        & + fix\_cost_{n,t,y,y} \cdot \frac{ 1 }{ \sum_{h'} duration\_time_{h'} \cdot capacity\_factor_{n,t,y,y,h'} } \\
*        & + var\_cost_{n,t,y,y,m,h}
*
* where :math:`|y| = technical\_lifetime_{n,t,y}`. This formulation implicitly assumes constant fixed
* and variable costs over time.
*
* **Warning:** All soft relaxations of the dynamic activity constraint are
* disabled if the levelized costs are negative!
***

levelized_cost(node,tec,year,time)$( map_tec_time(node,tec,year,time) AND inv_tec(tec) ) =
    inv_cost(node,tec,year)
        * (
* compute discounted annualized investment costs if interest rate > 0
            ( interestrate(year)
                * ( 1 + interestrate(year) ) ** technical_lifetime(node,tec,year)
                / ( ( 1 + interestrate(year) ) ** technical_lifetime(node,tec,year) - 1 )
              )$( interestrate(year) )
* if interest rate = 0, annualized investment costs are total investment costs divided by technical lifetime
            + ( 1 / technical_lifetime(node,tec,year) )$( interestrate(year) eq 0 )
          )
* add (proportional) fixed and variable costs, assuming that these remain constant over the technical lifetime
    + ( fix_cost(node,tec,year,year) /
          sum(time2$( map_tec_time(node,tec,year,time2) ),
             duration_time(time2) * capacity_factor(node,tec,year,year,time2) )
        )$( fix_cost(node,tec,year,year) )
    + sum(mode$( map_tec_act(node,tec,year,mode,time) ), var_cost(node,tec,year,year,mode,time) )
;

* the soft relaxations of the dynamic activity constraints are disabled if the levelized costs are negative
loop((node,tec,year,time)$( levelized_cost(node,tec,year,time) < 0
        AND ( soft_activity_up(node,tec,year,time) + soft_activity_lo(node,tec,year,time) ) > 0 ),
    put_utility 'log' /'Remove relaxations for dynamic activity constraints for ',node.tl,'|',tec.tl,'|',year.tl,'!' ;
    soft_activity_up(node,tec,year,time) = 0 ;
    soft_activity_lo(node,tec,year,time) = 0 ;
) ;

***
* Construction time accounting
* ----------------------------
* If the construction of new capacity takes a significant amount of time,
* investment costs have to be scaled up accordingly to account for the higher capital costs.
*
* .. math::
*    construction\_time\_factor_{n,t,y} = \left( 1 + interestrate_y \right)^{|y|}
*
* where :math:`|y| = construction\_time_{n,t,y}`. If no construction time is specified, the default value of the
* investment cost scaling factor defaults to 1. The model assumes that the construction time only plays a role
* for the investment costs, i.e., each unit of new-built capacity is available instantaneously.
*
* **Comment:** This formulation applies the discount rate of the vintage year
* (i.e., the year in which the new capacity becomes operational).
***

* set default construction_time_factor to 1
construction_time_factor(node,inv_tec,year)$( map_tec(node,inv_tec,year) ) = 1;

* compute the construction_time_factor
construction_time_factor(node,inv_tec,year)$( map_tec(node,inv_tec,year) AND construction_time(node,inv_tec,year) ) =
     ( 1 + interestrate(year) ) ** construction_time(node,inv_tec,year) ;

***
* Investment costs beyond the model horizon
* -----------------------------------------
* If the technical lifetime of a technology exceeds the model horizon :math:`Y^{model}`, the model has to add
* a scaling factor to the investment costs (:math:`end\_of\_horizon\_factor_{n,t,y}`). Assuming a constant
* stream of revenue (marginal value of the capacity constraint), this can be computed by annualizing investment costs
* from the condition that in an optimal solution, the investment costs must equal the discounted future revenues,
* if the investment variable :math:`CAP\_NEW_{n,t,y} > 0`:
*
* .. math::
*    inv\_cost_{n,t,y^V} = \sum_{y \in Y^{lifetime}_{n,t,y^V}} df\_year_{y} \cdot \beta_{n,t},
*
* Here, :math:`\beta_{n,t} > 0` is the dual variable to the capacity constraint (assumed constant over future periods)
* and :math:`Y^{lifetime}_{n,t,y^V}` is the set of periods in the lifetime of a plant built in period :math:`y^V`.
* Then, the scaling factor :math:`end\_of\_horizon\_factor_{n,t,y^V}` can be derived as follows:
*
* .. math::
*    end\_of\_horizon\_factor_{n,t,y^V} :=
*    \frac{\sum_{y \in Y^{lifetime}_{n,t,y^V} \cap Y^{model}} df\_year_{y} }
*        {\sum_{y' \in Y^{lifetime}_{n,t,y^V}} df\_year_{y'} + beyond\_horizon\_factor_{n,t,y^V} }
*    \in (0,1],
*
* where the parameter :math:`beyond\_horizon\_factor_{n,t,y^V}` accounts for the discount factor beyond the
* overall model horizon (the set :math:`Y` in contrast to the set :math:`Y^{model} \subseteq Y` of the periods
* included in the current model iteration (see the page on the recursive-dynamic model solution approach).
*
* .. math::
*    beyond\_horizon\_lifetime_{n,t,y^V} :=  \max \Big\{ 0,
*        economic\_lifetime_{n,t,y^V} - \sum_{y' \geq y^V} duration\_period_{y'} \Big\}
*
* .. math::
*    beyond\_horizon\_factor_{n,t,y^V} :=
*        df\_year_{\widehat{y}} \cdot \frac{1}{ \left( 1 + interestrate_{\widehat{y}} \right)^{|\widehat{y}|} }
*        \cdot \frac{ 1 - \left( \frac{1}{1 + interestrate_{\widehat{y}}} \right)^{|\widetilde{y}|}}
*                   { 1 - \frac{1}{1 + interestrate_{\widehat{y}}}}
*
* where :math:`\widehat{y}` is the last period included in the overall model horizon,
* :math:`|\widehat{y}| = period\_duration\_period_{\widehat{y}}`
* and :math:`|\widetilde{y}| = beyond\_horizon\_lifetime_{n,t,y^V}`.
*
* If the interest rate is zero, i.e., :math:`interestrate_{\widehat{y}} = 0`,
* the parameter :math:`beyond\_horizon\_factor_{n,t,y^V}` equals the remaining technical lifetime
* beyond the model horizon and the parameter :math:`end\_of\_horizon\_factor_{n,t,y^V}` equals
* the share of technical lifetime within the model horizon.
***

* compute the cumulative discount factor of the technical lifetime remaining beyond the model horizon
beyond_horizon_factor(node,inv_tec,vintage)$( beyond_horizon_lifetime(node,inv_tec,vintage) )
    = sum(last_period,
* compute the discount factor of the very last year (not period) in the model horizon
        df_year(last_period) * (
* multiply this by the geometric series of remaining technical lifetime if interestrate of last model period > 0
            (
                ( 1 - POWER( 1 / ( 1 + interestrate(last_period) ), beyond_horizon_lifetime(node,inv_tec,vintage) ) )
                / ( 1 - 1 / ( 1 + interestrate(last_period) ) )
            )$( interestrate(last_period) )
* if interest rate = 0, multiply by remaining technical lifetime
            + ( beyond_horizon_lifetime(node,inv_tec,vintage) )$( interestrate(last_period) eq 0 )
        )
    ) ;

* deterine the parameter end_of_horizon_factor used for scaling investment costs to account for
* technical lifetime beyond the model horizon
end_of_horizon_factor(node,inv_tec,vintage)$( map_tec(node,inv_tec,vintage) ) =
    sum(year_all$( map_tec_lifetime(node,inv_tec,vintage,year_all) ), df_period(year_all)  )
    / ( sum(year_all$( map_tec_lifetime(node,inv_tec,vintage,year_all) ), df_period(year_all) )
        + beyond_horizon_factor(node,inv_tec,vintage) ) ;

***
* **Possible extension:** Instead of assuming :math:`\beta_{n,t}` to be constant over time, one could include
* a simple (linear) projection of :math:`\beta_{n,t,y}` beyond the end of the model horizon. However, this would likely
* require to include the computation of dual variables endogenously, and thus a mixed-complementarity formulation of
* the model.
***

***
* Remaining installed capacity
* ----------------------------
* The model has to take into account that the technical lifetime of a technology may not coincide with the cumulative
* period duration. Therefore, the model introduces the parameter :math:`remaining\_capacity_{n,t,y^V,y}`
* as a factor of remaining technical lifetime in the last period of operation divided by the duration of that period.
*
***

# set default to 1 (assume that the full capacity is available over the entire period)
remaining_capacity(node,tec,vintage,year_all)$( map_tec_lifetime(node,tec,vintage,year_all) ) = 1 ;

# if technical lifetime ends in the respective period, set remaining_capacity factor as share of lifetime in that period
remaining_capacity(node,tec,vintage,year_all)$( map_tec_lifetime(node,tec,vintage,year_all)
        AND ( technical_lifetime(node,tec,vintage) - duration_period_sum(vintage,year_all) < duration_period(year_all) )
        AND ( technical_lifetime(node,tec,vintage) - duration_period_sum(vintage,year_all) > 0 ) )
    = ( technical_lifetime(node,tec,vintage) - duration_period_sum(vintage,year_all) ) / duration_period(year_all) ;

* unassign the dynamic set 'year'
year(year_all) = no;
