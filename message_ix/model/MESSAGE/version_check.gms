* Version check                                                                                                 *
*
* See technical description in ../version.gms.

Parameter MESSAGE_ix_version(*);

$GDXIN '%in%'
$LOAD MESSAGE_IX_version
$GDXIN

IF ( NOT ( MESSAGE_IX_version("major") = %VERSION_MAJOR% AND MESSAGE_IX_version("minor") = %VERSION_MINOR% ),
    logfile.nw = 1;
    logfile.nd = 0;

    put_utility 'log' / '***';
    put_utility 'log' / '*** ABORT';
    put_utility 'log' / '*** GDX file was written by an ixmp.jar incompatible with this version of MESSAGEix:';
    put_utility 'log' / '***   %in%';
    put_utility 'log' / '***   ...has version ' MESSAGE_IX_version("major") '.' MESSAGE_IX_version("minor")
      ' while version.gms has %VERSION_MAJOR%.%VERSION_MINOR%';
    put_utility 'log' / '***';

    abort "GDX file incompatible with current version of MESSAGEix";
) ;
