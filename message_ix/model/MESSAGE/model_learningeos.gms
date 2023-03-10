SETS
  size           'size'  / small, medium, large / ;

ALIAS (size,size2);
PARAMETERS
  cap_new2(node,newtec,year_all2)        'annual newly installed capacity'
  bin_cap_new(node,newtec,year_all2)     'binary of newly installed capacity'
  rho(newtec)                            'economy of scale parameter'            / wind_ppl      1.0       / #0.8
  b(newtec)                              'technology cost learning parameter'    / wind_ppl      0.9     / #0.9
  u(size)                                'unit size'
         / small      5
           medium     10
           large      50     /
  inv_cost_ref(node,newtec)              'initial capex'
  nbr_unit_ref(newtec)                   'initial number of unit'                / wind_ppl      100     /
  u_ref(newtec)                          'reference size'                        / wind_ppl      5       / ;
inv_cost_ref(node,newtec) = 1500;

SCALAR hist_length                       the length of historical periods;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
  NBR_UNIT(node,newtec,size,year_all2)   number of units for each size every year
  CAPEX_TEC(node,newtec,year_all2)       capital cost in dollar per kW
  OBJECT                                 objective function ;

POSITIVE VARIABLES
  NBR_UNIT ;

EQUATIONS
  OBJECTIVE_INNER        total investment cost
  CAP_NEW_BALANCE        installed capacity balance
  CAPEX_ESTIMATE         estimating average capex
  NO_BUILT_YEAR          annual investment cost
;


OBJECTIVE_INNER..                        OBJECT =e= sum((node,newtec,year_all2), CAPEX_TEC(node,newtec,year_all2)*cap_new2(node,newtec,year_all2)) ;
CAP_NEW_BALANCE(node,newtec,year_all2).. sum(size, NBR_UNIT(node,newtec,size,year_all2)*u(size)) =e= cap_new2(node,newtec,year_all2) ;
CAPEX_ESTIMATE(node,newtec,year_all2)..  CAPEX_TEC(node,newtec,year_all2)*cap_new2(node,newtec,year_all2) =g= sum(size,inv_cost_ref(node,newtec)
                                              * NBR_UNIT(node,newtec,size,year_all2)*u(size)
                                              * [(((sum((size2,year_all3)$(ord(year_all3) le ord(year_all2) and ord(year_all3) gt hist_length), NBR_UNIT(node,newtec,size2,year_all3))+nbr_unit_ref(newtec))/nbr_unit_ref(newtec))**(-b(newtec)))]
                                              * [((u(size)/u_ref(newtec))**rho(newtec))]) ;
NO_BUILT_YEAR(node,newtec,year_all2)..   CAPEX_TEC(node,newtec,year_all2) =e= bin_cap_new(node,newtec,year_all2)*CAPEX_TEC(node,newtec,year_all2)
                                                                              + (1-bin_cap_new(node,newtec,year_all2))*CAPEX_TEC(node,newtec,year_all2-1) ;

model learningeos / all /;
