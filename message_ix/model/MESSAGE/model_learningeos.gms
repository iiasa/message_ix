Sets
  size           'size'  / small, medium, large / ;

Alias (size,size2);
Parameters
  cap_new2(node,newtec,year_all2)   'annual newly installed capacity'
  rho(newtec) 'economy of scale parameter'
         / wind_ppl      1 / #0.8
  b(newtec)   'technology cost learning parameter'
         / wind_ppl      0.9 / #0.9
  u(size)   'unit size'
         / small      5
           medium     10
           large      50     /
  inv_cost0(node,newtec) 'initial capex'
  n_unit0(newtec) 'initial number of unit'
         / wind_ppl   100 /
  u0(newtec) 'reference size'
         / wind_ppl   5 / ;
inv_cost0(node,newtec)=1500;

scalar hist_length the length of historical periods;
hist_length = card(year_all2) - card(model_horizon);

*Table
*  cap_new2(node,newtec,year_all2)   'annual newly installed capacity'
*                         690      700     710     720
*  Westeros.wind_ppl      100      10      0       0 ;

Variables
  N_unit(node,newtec,size,year_all2)  number of units for each size every year
  CapexTec(node,newtec,year_all2)  capital cost in dollar per kW
  Object            objective function ;

Positive Variables
  N_unit;

Equations
  Objective_inner        total investment cost
  C_balance              installed capacity balance
  Capex_estimate         estimating average capex
  Annual_investment      annual investment cost
;


Objective_inner..        Object =e= sum((node,newtec,year_all2), CapexTec(node,newtec,year_all2)*cap_new2(node,newtec,year_all2)) ;
C_balance(node,newtec,year_all2)..         sum(size, N_unit(node,newtec,size,year_all2)*u(size)) =e= cap_new2(node,newtec,year_all2) ;
Capex_estimate(node,newtec,year_all2)..    CapexTec(node,newtec,year_all2)*cap_new2(node,newtec,year_all2) =g= sum(size,inv_cost0(node,newtec)
                                              *N_unit(node,newtec,size,year_all2)*u(size)
                                              *[(((sum((size2,year_all3)$(ord(year_all3) le ord(year_all2) and ord(year_all3) gt hist_length), N_unit(node,newtec,size2,year_all3))+n_unit0(newtec))/n_unit0(newtec))**(-b(newtec)))]
                                              *[((u(size)/u0(newtec))**rho(newtec))]) ;
Annual_investment(node,newtec,year_all2).. sum(year_all3$(ord(year_all3) le ord(year_all2) and ord(year_all3) gt hist_length), CapexTec(node,newtec,year_all3)*cap_new2(node,newtec,year_all3))
                                           - sum(year_all3$(ord(year_all3) le (ord(year_all2)-1) and ord(year_all3) gt hist_length), CapexTec(node,newtec,year_all3)*cap_new2(node,newtec,year_all3)) =g= 0 ;

model leaningeos / all /;

$ontext

Objective_inner..        Object =e= sum((node,newtec,year_all2), CapexTec(node,newtec,year_all2)*cap_new2(node,newtec,year_all2)) ;
C_balance(node,newtec,year_all2)..         sum(size, N_unit(node,newtec,size,year_all2)*u(size)) =e= cap_new2(node,newtec,year_all2) ;
Capex_estimate(node,newtec,year_all2)..    CapexTec(node,newtec,year_all2)*cap_new2(node,newtec,year_all2) =g= sum(size,inv_cost0(node,newtec)
                                              *N_unit(node,newtec,size,year_all2)*u(size)
                                              *[(((sum((size2,year_all3)$(ord(year_all3) le ord(year_all2) and ord(year_all3) gt hist_length), N_unit(node,newtec,size2,year_all3))+n_unit0(newtec))/n_unit0(newtec))**(-b(newtec)))]
                                              *[((u(size)/u0(newtec))**rho(newtec))]) ;

model leaningeos / all /;

$offtext