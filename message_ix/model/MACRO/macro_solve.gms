
* ------------------------------------------------------------------------------
* Start values of variables inside feasible domain (positive variables)
* ------------------------------------------------------------------------------

SVKN(node_macro, year) = ((potential_gdp(node_macro, year) - SUM(year2$( seq_period(year2,year) ), potential_gdp(node_macro, year2)) * (1 - depr(node_macro))**duration_period(year)) * kgdp(node_macro)) $ (NOT macro_base_period(year));
SVNEWE(node_macro, sector, year) = (demand_base(node_macro, sector) * growth_factor(node_macro, year) - demand_base(node_macro, sector) * (1 - depr(node_macro))**(SUM(year2 $ macro_base_period(year2), duration_period_sum(year2, year)))) $ (NOT macro_base_period(year));

NEWENE.L(node_macro, sector, macro_horizon)  = SVNEWE(node_macro, sector, macro_horizon)$(SVNEWE(node_macro, sector, macro_horizon) > 0) + epsilon ;
PHYSENE.L(node_macro, sector, year)  = enestart(node_macro, sector, year) ;
KN.L(node_macro, macro_horizon)  = SVKN(node_macro, macro_horizon) $ (SVKN(node_macro, macro_horizon) > 0) + epsilon ;

* ------------------------------------------------------------------------------
* Lower bounds on variables help to avoid singularities
* ------------------------------------------------------------------------------

K.LO(node_macro, macro_horizon)  = LOTOL(node_macro) * k0(node_macro) ;
KN.LO(node_macro, macro_horizon) = LOTOL(node_macro) * i0(node_macro) * duration_period(macro_horizon) ;
Y.LO(node_macro, macro_horizon)  = LOTOL(node_macro) * y0(node_macro) ;
YN.LO(node_macro, macro_horizon) = LOTOL(node_macro) * y0(node_macro) * newlab(node_macro, macro_horizon) ;

C.LO(node_macro, macro_horizon)  = LOTOL(node_macro) * c0(node_macro) ;
I.LO(node_macro, macro_horizon)  = LOTOL(node_macro) * i0(node_macro) ;

PRODENE.LO(node_macro, sector, macro_horizon) = LOTOL(node_macro) * enestart(node_macro, sector, macro_horizon) / aeei_factor(node_macro, sector, macro_horizon) ;
NEWENE.LO(node_macro, sector, macro_horizon)  = LOTOL(node_macro) * enestart(node_macro, sector, macro_horizon) / aeei_factor(node_macro, sector, macro_horizon) ;

* ------------------------------------------------------------------------------
* Base year values of variables are fixed to historical values
* ------------------------------------------------------------------------------

* division by aeei_factor is necesary in case MACRO starts after initialize_period (in case of slicing)
PRODENE.FX(node_macro, sector, macro_base_period) = demand_base(node_macro, sector) / aeei_factor(node_macro, sector, macro_base_period) ;

Y.FX(node_macro, macro_base_period) = y0(node_macro) ;
K.FX(node_macro, macro_base_period) = k0(node_macro) ;
C.FX(node_macro, macro_base_period) = c0(node_macro) ;
I.FX(node_macro, macro_base_period) = i0(node_macro) ;
EC.FX(node_macro, macro_base_period) = y0(node_macro) - i0(node_macro) - c0(node_macro) ;

* ------------------------------------------------------------------------------
* solving the model region by region
* ------------------------------------------------------------------------------

node_active(node) = no ;

LOOP(node $ node_macro(node),

    node_active(node_macro) = no ;
    node_active(node) = YES;
*    DISPLAY node_active ;

* ------------------------------------------------------------------------------
* solve statement
* ------------------------------------------------------------------------------

    SOLVE MESSAGE_MACRO MAXIMIZING UTILITY USING NLP ;

* write model status summary (by node)
*    status(node,'modelstat') = MESSAGE_MACRO.modelstat ;
*    status(node,'solvestat') = MESSAGE_MACRO.solvestat ;
*    status(node,'resUsd')    = MESSAGE_MACRO.resUsd ;
*    status(node,'objEst')    = MESSAGE_MACRO.objEst ;
*    status(node,'objVal')    = MESSAGE_MACRO.objVal ;

) ;

