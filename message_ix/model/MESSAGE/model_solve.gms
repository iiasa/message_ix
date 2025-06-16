***
* Solve statement workflow
* ========================
*
* This part of the code includes the perfect-foresight, myopic and rolling-horizon model solve statements
* including the required accounting of investment costs beyond the model horizon.
***

Parameter
    count_iter                           'iteration counter'
    prev_OBJ                             'previous objective value'
    delta_OBJ                            'difference between current and previous objective value'
    inv_cost_ini(node,newtec)            'initial investment cost assumption at first model year'
;

count_iter = 1;
prev_OBJ   = 0;
delta_OBJ  = 1;
inv_cost_ini(node,newtec) = sum(first_period, inv_cost(node,newtec,first_period));

if (%foresight% = 0,
***
* Perfect-foresight model
* ~~~~~~~~~~~~~~~~~~~~~~~
* For the perfect foresight version of |MESSAGEix|, include all years in the model horizon and solve the entire model.
* This is the standard option; the GAMS global variable ``%foresight%=0`` by default.
*
* .. math::
*    \min_x OBJ = \sum_{y \in Y} OBJ_y(x_y)
***

* reset year in case it was set by MACRO to include the base year before
    year(year_all) = no ;
* include all model periods in the optimization horizon (excluding historical periods prior to 'first_period')
    year(year_all)$( model_horizon(year_all) ) = yes ;

    IF(%learningmode% = 1,
        put_utility 'log' /'+++ Solve the perfect-foresight with learning version of MESSAGEix +++ ' ;
        option threads = 4 ;
        while(count_iter <= 10 and
              delta_OBJ >= 0.01,
              Solve MESSAGE_LP using LP minimizing OBJ ;

*             passing CAP_NEW values to update cap_new2 data for unit and size optimization,
*             make bin parameters equal to 1 when technology is built, and 0 if otherwise,
*             and passing log2_cap_new parameter to learning module
*             NOTE: there is no log 0, thus binary parameter is added as helper to avoid error.
*                   multiplication with the binary parameter in learning module negates effect of this helper
              cap_new2(newtec,year_all2) = sum(node, CAP_NEW.l(node,newtec,year_all2));
              bin_cap_new(newtec,year_all2) = sum(node, CAP_NEW.l(node,newtec,year_all2));
              bin_cap_new(newtec,year_all2)$(bin_cap_new(newtec,year_all2) > 1E-10) = 1 ;
              log2_cap_new2(newtec,year_all2) = log2(sum(node, CAP_NEW.l(node,newtec,year_all2)) + [1-bin_cap_new(newtec,year_all2)] ) ;
              Solve learningeos using nlp minimizing OBJECT;

*             update inv_cost values using indexed (normalized) cost IC
              inv_cost(node,newtec,year_all2) = IC.l(newtec,year_all2) * inv_cost_ini(node,newtec);
              if(count_iter = 1,
                      delta_OBJ = 1 ;
              else
                      delta_OBJ = (prev_OBJ - OBJ.l)/prev_OBJ ;
              );
              prev_OBJ = OBJ.l ;
              display count_iter, delta_OBJ;
              display year,year_all,year_all2,model_horizon,inv_cost_ini ;
              count_iter = count_iter + 1 ;
        );

    ELSE
*       write a status update to the log file, solve the model
        put_utility 'log' /'+++ Solve the perfect-foresight version of MESSAGEix +++ ' ;
        option threads = 4 ;
        Solve MESSAGE_LP using LP minimizing OBJ ;
        display year,year_all,year_all2,model_horizon,inv_cost_ini ;
    );

* write a status update to the log file, solve the model
    put_utility 'log' /'+++ Solve the perfect-foresight version of MESSAGEix +++ ' ;
    Solve MESSAGE_LP using LP minimizing OBJ ;

* write model status summary
    status('perfect_foresight','modelstat') = MESSAGE_LP.modelstat ;
    status('perfect_foresight','solvestat') = MESSAGE_LP.solvestat ;
    status('perfect_foresight','resUsd')    = MESSAGE_LP.resUsd ;
    status('perfect_foresight','objEst')    = MESSAGE_LP.objEst ;
    status('perfect_foresight','objVal')    = MESSAGE_LP.objVal ;

* write an error message if model did not solve to optimality
    IF( NOT ( MESSAGE_LP.modelstat = 1 OR MESSAGE_LP.modelstat = 8 ),
        put_utility 'log' /'+++ MESSAGEix did not solve to optimality - run is aborted, no output produced! +++ ' ;
        ABORT "MESSAGEix did not solve to optimality!"
    ) ;

* assign auxiliary variables DEMAND for integration with MACRO
    DEMAND.l(node,commodity,level,year,time) = demand_fixed(node,commodity,level,year,time) ;

* assign auxiliary variables PRICE_COMMODITY and PRICE_EMISSION for reporting
    PRICE_COMMODITY.l(node,commodity,level,year,time) =
        ( COMMODITY_BALANCE_GT.m(node,commodity,level,year,time) + COMMODITY_BALANCE_LT.m(node,commodity,level,year,time) )
            / df_period(year) ;

* calculate PRICE_EMISSION based on the marginals of EMISSION_EQUIVALENCE
    PRICE_EMISSION.l(node,type_emission,type_tec,year)$( SUM(emission$( cat_emission(type_emission,emission) ),
         EMISSION_EQUIVALENCE.m(node,emission,type_tec,year) ) ) =
        SMAX(emission$( cat_emission(type_emission,emission) ),
               EMISSION_EQUIVALENCE.m(node,emission,type_tec,year) / emission_scaling(type_emission,emission) )
            / df_period(year);
    PRICE_EMISSION.l(node,type_emission,type_tec,year)$(
        ( PRICE_EMISSION.l(node,type_emission,type_tec,year) = eps ) or
        ( PRICE_EMISSION.l(node,type_emission,type_tec,year) = -inf ) ) = 0 ;

%AUX_BOUNDS% AUX_ACT_BOUND_LO(node,tec,year_all,year_all2,mode,time)$( ACT.l(node,tec,year_all,year_all2,mode,time) < 0 AND
%AUX_BOUNDS%    ACT.l(node,tec,year_all,year_all2,mode,time) = -%AUX_BOUND_VALUE% ) = yes ;
%AUX_BOUNDS% AUX_ACT_BOUND_UP(node,tec,year_all,year_all2,mode,time)$( ACT.l(node,tec,year_all,year_all2,mode,time) > 0 AND
%AUX_BOUNDS%    ACT.l(node,tec,year_all,year_all2,mode,time) = %AUX_BOUND_VALUE% ) = yes ;

else
***
* Recursive-dynamic and myopic model
* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* For the myopic and rolling-horizon models, loop over horizons and iteratively solve the model, keeping the decision
* variables from prior periods fixed.
* This option is selected by setting the GAMS global variable ``%foresight%`` to a value greater than 0,
* where the value represents the number of years that the model instance is considering when iterating over the periods
* of the optimization horizon.
*
* Loop over :math:`\hat{y} \in Y`, solving
*
* .. math::
*     \min_x \ OBJ = \sum_{y \in \hat{Y}(\hat{y})} OBJ_y(x_y) \\
*     \text{s.t. } x_{y'} = x_{y'}^* \quad \forall \ y' < y
*
* where :math:`\hat{Y}(\hat{y}) = \{y \in Y | \ |\hat{y}| - |y| < optimization\_horizon \}` and
* :math:`x_{y'}^*` is the optimal value of :math:`x_{y'}` in iteration :math:`|y'|` of the iterative loop.
*
* The advantage of this implementation is that there is no need to 'store' the optimal values of all decision
* variables in additional reporting parameters - the last model solve automatically includes the results over the
* entire model horizon and can be imported via the ixmp interface.
***

    year(year_all) = no ;

    LOOP(year_all$( model_horizon(year_all) ),

* include all past periods and future periods including the period where the %foresight% is reached
        year(year_all) = yes ;

* reset the investment cost scaling parameter
        year(year_all2)$( ORD(year_all2) > ORD(year_all)
            AND duration_period_sum(year_all,year_all2) < %foresight% ) = yes ;
        year4(year_all2)$((ord(year_all2) < ord(year_all))) = yes ;

* write a status update and time elapsed to the log file, solve the model
        put_utility 'log' /'+++ Solve the recursive-dynamic version of MESSAGEix - iteration ' year_all.tl:0 '  +++ ' ;
        $$INCLUDE includes/aux_computation_time.gms
        Solve MESSAGE_LP using LP minimizing OBJ ;

* write model status summary
        status(year_all,'modelstat') = MESSAGE_LP.modelstat ;
        status(year_all,'solvestat') = MESSAGE_LP.solvestat ;
        status(year_all,'resUsd')    = MESSAGE_LP.resUsd ;
        status(year_all,'objEst')    = MESSAGE_LP.objEst ;
        status(year_all,'objVal')    = MESSAGE_LP.objVal ;

* write an error message AND ABORT THE SOLVE LOOP if model did not solve to optimality
        IF( NOT ( MESSAGE_LP.modelstat = 1 OR MESSAGE_LP.modelstat = 8 ),
            put_utility 'log' /'+++ MESSAGEix did not solve to optimality - run is aborted, no output produced! +++ ' ;
            ABORT "MESSAGEix did not solve to optimality!"
        ) ;

        IF(%learningmode% = 1,
*       passing CAP_NEW values to update cap_new2 data for unit and size optimization,
*       make bin parameters equal to 1 when technology is built, and 0 if otherwise,
*       and passing log2_cap_new parameter to learning module
*       NOTE: there is no log 0, thus binary parameter is added as helper to avoid error.
*       multiplication with the binary parameter in learning module negates effect of this helper
        cap_new2(newtec,year_all2) = sum(node, CAP_NEW.l(node,newtec,year_all2));
        bin_cap_new(newtec,year_all2) = sum(node, CAP_NEW.l(node,newtec,year_all2));
        bin_cap_new(newtec,year_all2)$(bin_cap_new(newtec,year_all2) > 1E-10) = 1 ;
        log2_cap_new2(newtec,year_all2) = log2(sum(node, CAP_NEW.l(node,newtec,year_all2)) + [1-bin_cap_new(newtec,year_all2)] ) ;
        
        Solve learningeos using nlp minimizing OBJECT;

*       update inv_cost values using indexed (normalized) cost IC
        inv_cost(node,newtec,year_all2) = IC.l(newtec,year_all2) * inv_cost_ini(node,newtec);

        display hist_length, bin_cap_new, IC.l, inv_cost, cap_new2, CAP_NEW.l,inv_cost_ini;
        );

* fix all variables of the current iteration period 'year_all' to the optimal levels
        ext_fix(node,commodity,grade,year4) =  EXT.l(node,commodity,grade,year4) ;
        cap_new_fix(node,newtec,year4) = CAP_NEW.l(node,newtec,year4) ;
        cap_fix(node,newtec,year4,year4) = CAP.l(node,newtec,year4,year4) ;
        act_fix(node,newtec,year4,year4,mode,time) = ACT.l(node,newtec,year4,year4,mode,time) ;

        ext_fix(node,commodity,grade,year4)$(ext_fix(node,commodity,grade,year4) > 1E-10) =  1 ;
        cap_new_fix(node,newtec,year4)$(cap_new_fix(node,newtec,year4) > 1E-10) = 1 ;
        cap_fix(node,newtec,year4,year4)$(cap_fix(node,newtec,year4,year4) > 1E-10) = 1 ;
        act_fix(node,newtec,year4,year4,mode,time)$(act_fix(node,newtec,year4,year4,mode,time) > 1E-10) = 1 ;

*        EXT.fx(node,commodity,grade,year4) =  EXT.l(node,commodity,grade,year4) ;
        CAP_NEW.fx(node,newtec,year4)$(cap_new_fix(node,newtec,year4) = 1) = CAP_NEW.l(node,newtec,year4) ;
*        CAP.fx(node,newtec,year4,year4) = CAP.l(node,newtec,year4,year4) ;
        ACT.fx(node,newtec,year4,year4,mode,time)$(act_fix(node,newtec,year4,year4,mode,time) = 1) = ACT.l(node,newtec,year4,year4,mode,time) ;
*        CAP_NEW_UP.fx(node,newtec,year4) = CAP_NEW_UP.l(node,newtec,year4) ;
*        CAP_NEW_LO.fx(node,newtec,year4) = CAP_NEW_LO.l(node,newtec,year4) ;
*        ACT_UP.fx(node,newtec,year4,time) = ACT_UP.l(node,newtec,year4,time) ;
*        ACT_LO.fx(node,newtec,year4,time) = ACT_LO.l(node,newtec,year4,time) ;
* relaxed "fix"
*        EXT.up(node,commodity,grade,year4) = 1.000001*EXT.l(node,commodity,grade,year4) ;
*        EXT.lo(node,commodity,grade,year4) = 0.999999*EXT.l(node,commodity,grade,year4) ;
**        CAP_NEW.up(node,newtec,year4) = 1.000001*CAP_NEW.l(node,newtec,year4) ;
**        CAP_NEW.lo(node,newtec,year4) = 0.999999*CAP_NEW.l(node,newtec,year4) ;
*        CAP.up(node,newtec,year4,year4) = 1.000001*CAP.l(node,newtec,year4,year4) ;
*        CAP.lo(node,newtec,year4,year4) = 0.999999*CAP.l(node,newtec,year4,year4) ;
**        ACT.up(node,newtec,year4,year4,mode,time) = 1.000001*ACT.l(node,newtec,year4,year4,mode,time) ;
**        ACT.lo(node,newtec,year4,year4,mode,time) = 0.999999*ACT.l(node,newtec,year4,year4,mode,time) ;

$ontext
        EXT.fx(node,commodity,grade,year_all) =  EXT.l(node,commodity,grade,year_all) ;
        CAP_NEW.fx(node,tec,year_all) = CAP_NEW.l(node,tec,year_all) ;
        CAP.fx(node,tec,year_all2,year_all)$( map_period(year_all2,year_all) ) = CAP.l(node,tec,year_all,year_all2) ;
        ACT.fx(node,tec,year_all2,year_all,mode,time)$( map_period(year_all2,year_all) )
            = ACT.l(node,tec,year_all2,year_all,mode,time) ;
        CAP_NEW_UP.fx(node,tec,year_all) = CAP_NEW_UP.l(node,tec,year_all) ;
        CAP_NEW_LO.fx(node,tec,year_all) = CAP_NEW_LO.l(node,tec,year_all) ;
        ACT_UP.fx(node,tec,year_all,time) = ACT_UP.l(node,tec,year_all,time) ;
        ACT_LO.fx(node,tec,year_all,time) = ACT_LO.l(node,tec,year_all,time) ;
$offtext
        
        Display year,year4,year_all,year_all2,model_horizon,inv_cost_ini ;
    ) ; # end of the recursive-dynamic loop

) ; # end of if statement for the selection betwen perfect-foresight or recursive-dynamic model

*----------------------------------------------------------------------------------------------------------------------*
* post-processing of trade costs and total costs                                                                       *
*----------------------------------------------------------------------------------------------------------------------*

* calculation of commodity import costs by node, commodity and year
import_cost(node2, commodity, year) =
          SUM( (node,tec,vintage,mode,level,time,time2)$( (NOT sameas(node,node2)) AND map_tec_act(node2,tec,year,mode,time2)
            AND map_tec_lifetime(node2,tec,vintage,year) AND map_commodity(node,commodity,level,year,time) ),
* import into node2 from other nodes
    input(node2,tec,vintage,year,mode,node,commodity,level,time2,time)
    * duration_time_rel(time,time2) * ACT.L(node2,tec,vintage,year,mode,time2)
    * PRICE_COMMODITY.l(node,commodity,level,year,time) )
;

* calculation of commodity export costs by node, commodity and year
export_cost(node2, commodity, year) =
          SUM( (node,tec,vintage,mode,level,time,time2)$( (NOT sameas(node,node2)) AND map_tec_act(node2,tec,year,mode,time2)
            AND map_tec_lifetime(node2,tec,vintage,year) AND map_commodity(node,commodity,level,year,time) ),
* export from node2 to other market
    output(node2,tec,vintage,year,mode,node,commodity,level,time2,time)
    * duration_time_rel(time,time2) * ACT.L(node2,tec,vintage,year,mode,time2)
    * PRICE_COMMODITY.l(node,commodity,level,year,time) )
;

* net commodity trade costs by node and year
trade_cost(node2, year) = SUM(commodity, import_cost(node2, commodity, year) - export_cost(node2, commodity, year)) ;

* total energy system costs excluding taxes by node and time (CAVEAT: lacking regional corrections due to emission trading)
COST_NODAL_NET.L(node, year)$(NOT macro_base_period(year)) = (
    COST_NODAL.L(node, year) + trade_cost(node, year)
* subtract emission taxes applied at any higher nodal level (via map_node set)
    - sum((type_emission,emission,type_tec,type_year,node2)$( emission_scaling(type_emission,emission)
            AND map_node(node2,node) AND cat_year(type_year,year) ),
        emission_scaling(type_emission,emission) * tax_emission(node2,type_emission,type_tec,type_year)
        * EMISS.L(node,emission,type_tec,year) )
) ;
