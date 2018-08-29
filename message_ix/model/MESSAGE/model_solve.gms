***
* Solve statement workflow
* ========================
* This page is generated from the auto-documentation in ``MESSAGE/model_solve.gms``.
*
* This part of the code includes the perfect-foresight, myopic and rolling-horizon model solve statements
* including the required accounting of investment costs beyond the model horizon.
***

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

* rescale the dual of the emission constraint to account that the constraint is defined on the average year, not total
EMISSION_CONSTRAINT.m(node,type_emission,type_tec,type_year)$(
        EMISSION_CONSTRAINT.m(node,type_emission,type_tec,type_year) ) =
    EMISSION_CONSTRAINT.m(node,type_emission,type_tec,type_year) / sum(year$( cat_year(type_year,year) ), 1 ) ;

* assign auxiliary variables DEMAND, PRICE_COMMODITY and PRICE_EMISSION for integration with MACRO and reporting
    DEMAND.l(node,commodity,level,year,time) = demand_fixed(node,commodity,level,year,time) ;
    PRICE_COMMODITY.l(node,commodity,level,year,time) = COMMODITY_BALANCE.m(node,commodity,level,year,time)
        / discountfactor(year) ;
    PRICE_EMISSION.l(node,type_emission,type_tec,year)$( SUM(type_year$( cat_year(type_year,year) ), 1 ) ) =
            SMAX(type_year$( cat_year(type_year,year) ),
                - EMISSION_CONSTRAINT.m(node,type_emission,type_tec,type_year) / discountfactor(year) ) ;
    PRICE_EMISSION.l(node,type_emission,type_tec,year)$(
        PRICE_EMISSION.l(node,type_emission,type_tec,year) = - inf ) = 0 ;

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

* fix all variables of the current iteration period 'year_all' to the optimal levels
        EXT.fx(node,commodity,grade,year_all) =  EXT.l(node,commodity,grade,year_all) ;
        CAP_NEW.fx(node,tec,year_all) = CAP_NEW.l(node,tec,year_all) ;
        CAP.fx(node,tec,year_all2,year_all)$( map_period(year_all2,year_all) ) = CAP.l(node,tec,year_all,year_all2) ;
        ACT.fx(node,tec,year_all2,year_all,mode,time)$( map_period(year_all2,year_all) )
            = ACT.l(node,tec,year_all2,year_all,mode,time) ;
        CAP_NEW_UP.fx(node,tec,year_all) = CAP_NEW_UP.l(node,tec,year_all) ;
        CAP_NEW_LO.fx(node,tec,year_all) = CAP_NEW_LO.l(node,tec,year_all) ;
        ACT_UP.fx(node,tec,year_all,time) = ACT_UP.l(node,tec,year_all,time) ;
        ACT_LO.fx(node,tec,year_all,time) = ACT_LO.l(node,tec,year_all,time) ;

    ) ; # end of the recursive-dynamic loop

) ; # end of if statement for the selection betwen perfect-foresight or recursive-dynamic model
