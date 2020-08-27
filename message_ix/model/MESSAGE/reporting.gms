***
* Standard output reports
* =======================
*
* This part of the code contains the definitions and scripts for a number of standard output reports.
* These default reports will be created after every MESSAGE run.
***

*----------------------------------------------------------------------------------------------------------------------*
* The following parts are quick-and-dirty reporting 'flags'
*----------------------------------------------------------------------------------------------------------------------*

Set
    report_aux_bounds_up(node,tec,year_all,year_all2,mode,time)
    report_aux_bounds_lo(node,tec,year_all,year_all2,mode,time)
;

report_aux_bounds_up(node,tec,year_all,year_all2,mode,time) = no ;
report_aux_bounds_up(node,tec,year_all,year_all2,mode,time)$(
    map_tec_lifetime(node,tec,year_all,year_all2) AND map_tec_act(node,tec,year_all2,mode,time)
    AND ( ACT.l(node,tec,year_all,year_all2,mode,time) = %AUX_BOUND_VALUE%) ) = yes ;

report_aux_bounds_lo(node,tec,year_all,year_all2,mode,time) = no ;
report_aux_bounds_lo(node,tec,year_all,year_all2,mode,time)$(
    map_tec_lifetime(node,tec,year_all,year_all2) AND map_tec_act(node,tec,year_all2,mode,time)
    AND ( ACT.l(node,tec,year_all,year_all2,mode,time) = -%AUX_BOUND_VALUE% ) ) = yes ;


Parameter
    report_new_capacity(*,*,*)
    report_total_capacity(*,*,*)
    report_activity(*,*,*,*)
;

* write the 'new capacity' into a specific reporting parameter
report_new_capacity(node,inv_tec,historical) =
    historical_new_capacity(node,inv_tec,historical) ;

report_new_capacity(node,inv_tec,year)$( map_tec(node,inv_tec,year) ) =
    CAP_NEW.l(node,inv_tec,year) ;

* write the 'total maintained capacity' into a specific reporting parameter
report_total_capacity(node,inv_tec,year)$( map_tec(node,inv_tec,year) ) =
    sum(vintage, CAP.l(node,inv_tec,vintage,year) ) ;

report_total_capacity(node,inv_tec,historical) $( sum(vintage, map_tec_lifetime(node,inv_tec,vintage,historical) ) ) =
    sum(vintage, remaining_capacity(node,inv_tec,vintage,historical) *
        duration_period(historical) * historical_new_capacity(node,inv_tec,vintage) );

* write the total 'activity' (summed over all vintages)
*report_activity(node,tec,year_all,"ref")$( map_tec(node,tec,year_all) ) =
*    sum((mode,time), ref_activity(node,tec,year_all,mode,time) ) ;

report_activity(node,tec,historical,"actual")$( map_tec(node,tec,historical) ) =
    sum((mode,time), historical_activity(node,tec,historical,mode,time) ) ;

report_activity(node,tec,year,"actual")$( map_tec(node,tec,year) ) =
    sum((location,vintage,mode,time)$( map_node(node,location) ),
        ACT.l(location,tec,vintage,year,mode,time) ) ;