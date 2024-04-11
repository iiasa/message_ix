$ontext
This program illustrates the use savepoint. It writes
the current model solution to a log or GDX file. The option
values are:
   0: do not write a point file (default)
   1: write the solution to <workdir><modelname>_p.gdx
   2: write the solution to <workdir><modelname>_p<solvenumber>.gdx
$offtext

$call =gams trnsport savepoint=2 lo=%GAMS.lo%
