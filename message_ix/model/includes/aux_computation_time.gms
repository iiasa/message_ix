* elegant reporting of GAMS computing time
* requires aux_computation_time_init.gms

if ( timeElapsed > 7200 ,
    put_utility 'log' / '    Time since GAMS start: ' floor( timeElapsed / 3600 ):0:0 ' hours, ' ( mod( timeElapsed, 3600 ) / 60 ):0:0 ' minutes' ;
elseif timeElapsed > 3720 ,
    put_utility 'log' / '    Time since GAMS start: 1 hour, ' ( timeElapsed / 60 - 60 ):0:0 ' minutes' ;
elseif timeElapsed > 3660 ,
    put_utility 'log' / '    Time since GAMS start: 1 hour, 1 minute' ;
elseif timeElapsed > 120 ,
    put_utility 'log' / '    Time since GAMS start: ' ( timeElapsed / 60 ):0:0 ' minutes' ;
else
    put_utility 'log' / '    Give it a bit more time, not even two minutes yet... ' ;
) ;
