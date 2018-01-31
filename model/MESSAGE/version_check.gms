
*----------------------------------------------------------------------------------------------------------------------*
* load ixmp MESSAGE-scheme version number from the input gdx and check whether it matches the MESSAGEix version number *
*----------------------------------------------------------------------------------------------------------------------*

Parameter MESSAGE_ix_version(*);

$GDXIN '%in%'
$LOAD MESSAGE_IX_version
$GDXIN

IF ( NOT ( MESSAGE_IX_version("major") = %VERSION_MAJOR% AND MESSAGE_IX_version("minor") = %VERSION_MINOR% ),
    put_utility 'log' / '***';
    put_utility 'log' / '*** Abort "The MESSAGEix version and the MESSAGE-scheme definition in the installed ixmp package do not match!"';
    put_utility 'log' / '***';
    abort "Incompatible versions of MESSAGEix and ixmp";
) ;
