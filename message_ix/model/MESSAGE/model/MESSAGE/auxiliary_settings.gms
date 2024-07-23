*----------------------------------------------------------------------------------------------------------------------*
* auxiliary settings and defintions                                                                                    *
*----------------------------------------------------------------------------------------------------------------------*

* initialise logfile settings - this allows to write status messages to the logfile
file logfile / '' / ;
put logfile ;

* get yourself a short listing file
option limrow = 0 ;     # number of rows (equations) reported in lst file
option limcol = 0 ;     # number of columns reported in lst file
option solprint = off ; # solver's solution output printed
option savepoint = 0 ;  # creates a result gdx file after every solve
* this is done manually in this code to have the database name in the gdx file name and to save the file in a sub-folder

option ITERLIM = 1e8 ;  # iteration limit
option RESLIM = 1e6 ;   # resource limit (in seconds; 1e6 is approximately 11 days)
* solver comments for QCP and PATH:
* - GUROBI, CPLEX and MINOS are fast
* - CONOPT is slower, but (in non-linear problems) usually more helpful to identify the feasibility problems
* general comment: sometimes, first using one solver and then another (using the previous solution as starting point)
* helps even if the previous run did not solve to optimality
option LP = CPLEX ;
option NLP = CONOPT ;
option MCP = PATH ;

*option solveopt=clear ;# remove results of previous runs in memory
option solveopt=merge ; # keep results of previous runs in memory
$SETENV GdxCompress 1   # reduces the size of the gdx export file

%calibration%$ONTEXT
$ONLISTING
option limrow = 1e6 ;   # number of rows (equations) reported in lst file
option limcol = 1e6 ;   # number of columns reported in lst file
option solprint = on ;  # solver's solution output printed
$ONTEXT
$OFFTEXT
