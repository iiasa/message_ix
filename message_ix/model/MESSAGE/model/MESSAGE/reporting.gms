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
