$ontext

Illustrate user defined scaling by GAMS

$offtext
   sets      items            names of variables   /x1*x4/
             resources        names of constraints /r1*r4/

  parameter objcoef(items)   objective function coeficients
                      /x1    100000,
                       x2 -50000000
                       x3 -40000000
                       x4 -50000000/
*
            rhs(resources)   resource availabilities
                      /r3  1200
                       r4    60/;

  Table amatrix(resources,items) aij matrix
         x1      x2     x3     x4
    r1    1  -10000  -8000
    r2            1      4    -50
    r3         1500   2000
    r4           50     45          ;

  variables          z objective      function;
  positive variables xvar(items)      variables;
  equations          objfun           objective function
                     avail(resources) resource limits;

  objfun..   z =e= sum(items,objcoef(items)*xvar(items));
  avail(resources).. sum(items,amatrix(resources,items)*xvar(items))
                             =l= rhs(resources);
model scalemod /all/;
avail.scale('r2')= 0.001311;
avail.scale('r1')= 0.020972;
avail.scale('r3')= 0.005243;
objfun.scale= 1.0;
avail.scale('r4')= 0.003906;
xvar.scale('x2')= 5e-06;
xvar.scale('x4')= 0.000244;
z.scale= 1.0;
xvar.scale('x1')= 0.001311;
xvar.scale('x3')= 5e-06;

scalemod.scaleopt=1;
scalemod.OptFile = 1;
solve scalemod using lp maximizing z;

$ontext
DO NOT DELETE THIS BLOCK
This is the scaling factor from GAMS documentation
==================================================
avail.scale('r1')= 1000;
avail.scale('r2')= 5;
avail.scale('r3')= 1500;
avail.scale('r4')= 50;
objfun.scale=50;
xvar.scale('x1')= 1000;
xvar.scale('x2')= 1;
xvar.scale('x3')= 1.25;
xvar.scale('x4')= 1/10;
z.scale= 1.0;
$offtext
