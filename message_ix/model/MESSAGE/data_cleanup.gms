*----------------------------------------------------------------------------------------------------------------------*
* optional removal of numerically negligible input values                                                               *
*----------------------------------------------------------------------------------------------------------------------*
* enable with the command-line argument --clean_tol=<threshold>, e.g. gams_args=["--clean_tol=1e-10"]
* values with 0 < |value| < %clean_tol% are set to zero; for coefficient parameters this removes the matrix entry,
* for bounds/demands/historical values the existing is_bound_* flags are kept, so the bound becomes exactly zero.
* capacity_factor, operation_factor and cost parameters are deliberately not touched (zero has a different meaning).

$IF NOT SET clean_tol $GOTO skip_data_cleanup

input(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2)$(
    ABS(input(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2)) < %clean_tol% ) = 0 ;
output(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2)$(
    ABS(output(node,tec,vintage,year_all,mode,node2,commodity,level,time,time2)) < %clean_tol% ) = 0 ;
emission_factor(node,tec,vintage,year_all,mode,emission)$(
    ABS(emission_factor(node,tec,vintage,year_all,mode,emission)) < %clean_tol% ) = 0 ;
relation_activity(relation,node,year_all,node2,tec,year_all2,mode)$(
    ABS(relation_activity(relation,node,year_all,node2,tec,year_all2,mode)) < %clean_tol% ) = 0 ;
relation_new_capacity(relation,node,year_all,tec)$(
    ABS(relation_new_capacity(relation,node,year_all,tec)) < %clean_tol% ) = 0 ;
relation_total_capacity(relation,node,year_all,tec)$(
    ABS(relation_total_capacity(relation,node,year_all,tec)) < %clean_tol% ) = 0 ;

demand_fixed(node,commodity,level,year_all,time)$(
    ABS(demand_fixed(node,commodity,level,year_all,time)) < %clean_tol% ) = 0 ;
historical_activity(node,tec,year_all,mode,time)$(
    ABS(historical_activity(node,tec,year_all,mode,time)) < %clean_tol% ) = 0 ;
historical_new_capacity(node,tec,year_all)$(
    ABS(historical_new_capacity(node,tec,year_all)) < %clean_tol% ) = 0 ;
bound_activity_up(node,tec,year_all,mode,time)$(
    ABS(bound_activity_up(node,tec,year_all,mode,time)) < %clean_tol% ) = 0 ;
bound_activity_lo(node,tec,year_all,mode,time)$(
    ABS(bound_activity_lo(node,tec,year_all,mode,time)) < %clean_tol% ) = 0 ;

$LABEL skip_data_cleanup
