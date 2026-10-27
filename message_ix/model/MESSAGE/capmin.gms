***
* Minimum-activity objective (``--capmin=1``)
* ===========================================
*
* Included by ``model_setup.gms`` only when the GAMS flag ``--capmin=1`` is passed.
* The model ``MESSAGE_CAPMIN`` keeps every constraint of ``MESSAGE_LP`` (under either ``landusemode``)
* but replaces the cost objective by the summed activity of technologies tagged ``cat_tec('capmin', tec)``.
* ``model_solve.gms`` then solves ``MESSAGE_CAPMIN`` in place of ``MESSAGE_LP``.
*
* .. math::
*    \min_x OBJ = \sum_{n,t \in T^{capmin},y^V,y,m,h} ACT_{n,t,y^V,y,m,h}
***

$IF NOT "%foresight%" == "0" $ABORT "capmin requires the perfect-foresight model (foresight=0)"
$IF "%macromode%" == "linked" $ABORT "capmin is a MESSAGE-only objective; do not set it for MESSAGE-MACRO"

Equation
    OBJ_CAPMIN    summed activity of technologies tagged 'capmin'
;

OBJ_CAPMIN..
    OBJ =E= SUM( (type_tec,node,tec,vintage,year,mode,time)$( sameas(type_tec,'capmin') AND cat_tec(type_tec,tec)
        AND map_tec_lifetime(node,tec,vintage,year) AND map_tec_act(node,tec,year,mode,time) ),
        ACT(node,tec,vintage,year,mode,time) ) ;

Model MESSAGE_CAPMIN / MESSAGE_LP - OBJECTIVE + OBJ_CAPMIN / ;

MESSAGE_CAPMIN.holdfixed = 1 ;
MESSAGE_CAPMIN.optfile = 1 ;
MESSAGE_CAPMIN.optcr = 0 ;
