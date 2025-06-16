
PARAMETERS
* inherrited parameters
  cap_new2(newtec,year_all2)             'newly installed capacity of learning technologies'
  bin_cap_new(newtec,year_all2)          'binary parameter of newly installed capacity'

* learning and economies of scale parameters
  alpha(newtec)                          'technology cost learning parameter                     n.a.'
  beta_unit(newtec)                      'economy of scale parameter at unit level               n.a.'
  beta_proj(newtec)                      'economy of scale parameter at project level            n.a.'
  gamma_unit(newtec)                     'unit scale-up rate                                     GW per experience'
  gamma_proj(newtec)                     'project scale-up rate                                  units per experience'

* initial condition
  inv_cost_refidx(newtec)                'initial capex (indexed to 1)                           n.a.'
  knref_unit(newtec)                     'initial number of unit                                 units'
  sizeref_unit(newtec)                   'initial size of unit                                   GW per unit'
  sizeref_proj(newtec)                   'initial size of project                                units per project'

* log2 parameters
  log2_cap_new2(newtec,year_all2)        'log2 of newly installed capacity                       n.a.'
  log2_inv_cost_refidx(newtec)           'log2 of indexed initial capex                          n.a.'
  log2_knref_unit(newtec)                'log2 of initial number of unit                         n.a.'
  log2_sizeref_unit(newtec)              'log2 of initial size of unit                           n.a.'
  log2_sizeref_proj(newtec)              'log2 of initial size of project                        n.a.'
;

* calculating log2 parameters value
log2_inv_cost_refidx(newtec)    = log2(inv_cost_refidx(newtec)) ;
log2_knref_unit(newtec)         = log2(knref_unit(newtec)) ;
log2_sizeref_unit(newtec)       = log2(sizeref_unit(newtec)) ;
log2_sizeref_proj(newtec)       = log2(sizeref_proj(newtec)) ;

* calculate the length of historical periods for indexing
SCALAR hist_length                       'the length of historical periods' ;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
* linear variables
  IC(newtec,year_all2)                   'specific capital cost                                  dollar per kW'
  N_UNIT(newtec,year_all2)               'number of new units                                    units'
  KN_UNIT(newtec,year_all2)              'number of cumulative units                             units'
  S_UNIT(newtec,year_all2)               'unit size                                              GW per unit or GtCO2 per unit'
  S_PROJ(newtec,year_all2)               'project size                                           units per project'

* log2 variables
  LOG2_IC(newtec,year_all2)              'log2 of capital cost                                   n.a.'
  LOG2_N_UNIT(newtec,year_all2)          'log2 of number of new units                            n.a.'
  LOG2_KN_UNIT(newtec,year_all2)         'log2 of number of cumulative units                     n.a.'
  LOG2_S_UNIT(newtec,year_all2)          'log2 of unit size                                      n.a.'
  LOG2_S_PROJ(newtec,year_all2)          'log2 of project size                                   n.a.'

* objective variable
  OBJECT                                 'objective function'
;

* initializing lower bound of variable to avoid log2 singularity
N_UNIT.lo(newtec,year_all2)  = 1E-15 ;
KN_UNIT.lo(newtec,year_all2) = 1E-15 ;
S_UNIT.lo(newtec,year_all2)  = sizeref_unit(newtec) ;
S_PROJ.lo(newtec,year_all2)  = sizeref_proj(newtec) ;


EQUATIONS
  OBJECTIVE_INNER                        'objective value: total investment cost of learning technologies'
  CAP_NEW_BALANCE                        'newly installed installed capacity balance'
  KN_UNIT_LOG                            'log2 of cumulative number of units equality'
  N_UNIT_LOG                             'log2 of number of units equality'
  S_UNIT_LOG                             'log2 of unit size equality'
  S_PROJ_LOG                             'log2 of project size equality'
  CAPEX_ESTIMATE                         'estimating average capex'
  CUMUL_UNIT_INI                         'calculate initial cumulative units'
  CUMUL_UNIT                             'calculate cumulative units'
  UNIT_SCALEUP_LIM_INI                   'calculate initial unit scale-up limit'
  UNIT_SCALEUP_LIM                       'calculate unit scale-up limit'
  PROJ_SCALEUP_LIM_INI                   'calculate initial project scale-up limit'
  PROJ_SCALEUP_LIM                       'calculate project scale-up limit'
  INV_COST_LOG                           'calculate investment cost'
  UNIT_SIZELB                            'unit size lower bound'
  UNIT_SIZE_NOBUILTYEAR                  'make unit size constant if no new capacity'
  PROJ_SIZELB                            'project size lower bound'
  PROJ_SIZE_NOBUILTYEAR                  'make project size constant if no new capacity'
;


OBJECTIVE_INNER..        OBJECT =e= sum((node,newtec,year_all2),
                         IC(newtec,year_all2) * cap_new2(newtec,year_all2)) ;

CAP_NEW_BALANCE(newtec,year_all2)$(bin_cap_new(newtec,year_all2) = 1)..
         log2_cap_new2(newtec,year_all2) =e=
         LOG2_N_UNIT(newtec,year_all2) + LOG2_S_UNIT(newtec,year_all2) ;

KN_UNIT_LOG(newtec,year_all2)..
         LOG2_KN_UNIT(newtec,year_all2) =e= log2(KN_UNIT(newtec,year_all2)) ;

N_UNIT_LOG(newtec,year_all2)$(bin_cap_new(newtec,year_all2) = 1)..
         LOG2_N_UNIT(newtec,year_all2) =e=
         log2(N_UNIT(newtec,year_all2)) ;

S_UNIT_LOG(newtec,year_all2)..
         LOG2_S_UNIT(newtec,year_all2) =e= log2(S_UNIT(newtec,year_all2)) ;

S_PROJ_LOG(newtec,year_all2)..
         LOG2_S_PROJ(newtec,year_all2) =e= log2(S_PROJ(newtec,year_all2)) ;

CAPEX_ESTIMATE(newtec,year_all2)..  LOG2_IC(newtec,year_all2) =e=
         LOG2_IC(newtec,year_all2-1)
         - alpha(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2)
         - beta_unit(newtec) * [LOG2_S_UNIT(newtec,year_all2) - LOG2_S_UNIT(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2)
         - beta_proj(newtec) * [LOG2_S_PROJ(newtec,year_all2) - LOG2_S_PROJ(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2) ;

CUMUL_UNIT_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         KN_UNIT(newtec,year_all2) =e=
         knref_unit(newtec) + N_UNIT(newtec,year_all2) * bin_cap_new(newtec,year_all2) ;

CUMUL_UNIT(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         KN_UNIT(newtec,year_all2) =e=
         KN_UNIT(newtec,year_all2-1) + N_UNIT(newtec,year_all2) * bin_cap_new(newtec,year_all2) ;

UNIT_SCALEUP_LIM_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         S_UNIT(newtec,year_all2) =l=
         sizeref_unit(newtec)
         + gamma_unit(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - log2_knref_unit(newtec)] ;

UNIT_SCALEUP_LIM(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         S_UNIT(newtec,year_all2) =l=
         S_UNIT(newtec,year_all2-1)
         + gamma_unit(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] ;

PROJ_SCALEUP_LIM_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         S_PROJ(newtec,year_all2) =l=
         sizeref_proj(newtec)
         + gamma_proj(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - log2_knref_unit(newtec)] ;

PROJ_SCALEUP_LIM(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         S_PROJ(newtec,year_all2) =l=
         S_PROJ(newtec,year_all2-1)
         + gamma_proj(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] ;

INV_COST_LOG(newtec,year_all2)..
         IC(newtec,year_all2) =e= 2**LOG2_IC(newtec,year_all2) ;

UNIT_SIZELB(newtec,year_all2)..
         S_UNIT(newtec,year_all2) =g= sizeref_unit(newtec) ;

UNIT_SIZE_NOBUILTYEAR(newtec,year_all2)$(bin_cap_new(newtec,year_all2) = 0 and
         ord(year_all2) gt (hist_length+1))..
         S_UNIT(newtec,year_all2) =e= S_UNIT(newtec,year_all2-1) ;

PROJ_SIZELB(newtec,year_all2)..
         S_PROJ(newtec,year_all2) =g= sizeref_proj(newtec) ;

PROJ_SIZE_NOBUILTYEAR(newtec,year_all2)$(bin_cap_new(newtec,year_all2) = 0 and
         ord(year_all2) gt (hist_length+1))..
         S_PROJ(newtec,year_all2) =e= S_PROJ(newtec,year_all2-1) ;


* declaring model equations
* please keep model equations listed in this format
* 'all' statement will include all MESSAGE-ix equations and increase learning module solution time
model learningeos /
  OBJECTIVE_INNER,  CAP_NEW_BALANCE,  KN_UNIT_LOG,  N_UNIT_LOG,  S_UNIT_LOG,
  S_PROJ_LOG, CAPEX_ESTIMATE, CUMUL_UNIT_INI, CUMUL_UNIT,  UNIT_SCALEUP_LIM_INI,
  UNIT_SCALEUP_LIM, PROJ_SCALEUP_LIM_INI, PROJ_SCALEUP_LIM, INV_COST_LOG,
  UNIT_SIZELB,
  UNIT_SIZE_NOBUILTYEAR,
  PROJ_SIZELB,
  PROJ_SIZE_NOBUILTYEAR
  /;
* keep this option for testing purpose
*option nlp = minos;