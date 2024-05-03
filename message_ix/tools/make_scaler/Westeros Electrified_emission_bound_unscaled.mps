* ENCODING=ISO-8859-1
NAME          gamsmodel
ROWS
 N  _obj                                                         
 E  COST_ACCOUNTING_NODAL(World,700)                             
 E  COST_ACCOUNTING_NODAL(World,710)                             
 E  COST_ACCOUNTING_NODAL(World,720)                             
 E  COST_ACCOUNTING_NODAL(Westeros,700)                          
 E  COST_ACCOUNTING_NODAL(Westeros,710)                          
 E  COST_ACCOUNTING_NODAL(Westeros,720)                          
 G  COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)
 G  COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)
 G  COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)
 G  COMMODITY_BALANCE_GT(Westeros,electricity,final,700,year)    
 G  COMMODITY_BALANCE_GT(Westeros,electricity,final,710,year)    
 G  COMMODITY_BALANCE_GT(Westeros,electricity,final,720,year)    
 G  COMMODITY_BALANCE_GT(Westeros,light,useful,700,year)         
 G  COMMODITY_BALANCE_GT(Westeros,light,useful,710,year)         
 G  COMMODITY_BALANCE_GT(Westeros,light,useful,720,year)         
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,690,700,year)          
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,700,year)          
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,710,year)          
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,710,year)          
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,720,year)          
 L  CAPACITY_CONSTRAINT(Westeros,coal_ppl,720,720,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,690,700,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,700,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,710,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,710,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,720,year)          
 L  CAPACITY_CONSTRAINT(Westeros,wind_ppl,720,720,year)          
 L  CAPACITY_CONSTRAINT(Westeros,bulb,700,700,year)              
 L  CAPACITY_CONSTRAINT(Westeros,bulb,710,710,year)              
 L  CAPACITY_CONSTRAINT(Westeros,bulb,720,720,year)              
 L  CAPACITY_MAINTENANCE_HIST(Westeros,coal_ppl,690,700)         
 L  CAPACITY_MAINTENANCE_HIST(Westeros,wind_ppl,690,700)         
 E  CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,700,700)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,710,710)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,720,720)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,700,700)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,710,710)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,720,720)          
 E  CAPACITY_MAINTENANCE_NEW(Westeros,bulb,700,700)              
 E  CAPACITY_MAINTENANCE_NEW(Westeros,bulb,710,710)              
 E  CAPACITY_MAINTENANCE_NEW(Westeros,bulb,720,720)              
 L  CAPACITY_MAINTENANCE(Westeros,coal_ppl,700,710)              
 L  CAPACITY_MAINTENANCE(Westeros,coal_ppl,710,720)              
 L  CAPACITY_MAINTENANCE(Westeros,wind_ppl,700,710)              
 L  CAPACITY_MAINTENANCE(Westeros,wind_ppl,710,720)              
 G  ACTIVITY_BOUND_LO(Westeros,coal_ppl,700,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,coal_ppl,710,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,coal_ppl,720,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,wind_ppl,700,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,wind_ppl,710,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,wind_ppl,720,standard,year)       
 G  ACTIVITY_BOUND_LO(Westeros,grid,700,standard,year)           
 G  ACTIVITY_BOUND_LO(Westeros,grid,710,standard,year)           
 G  ACTIVITY_BOUND_LO(Westeros,grid,720,standard,year)           
 G  ACTIVITY_BOUND_LO(Westeros,bulb,700,standard,year)           
 G  ACTIVITY_BOUND_LO(Westeros,bulb,710,standard,year)           
 G  ACTIVITY_BOUND_LO(Westeros,bulb,720,standard,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,700,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,710,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,720,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,700,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,710,year)           
 L  ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,720,year)           
 E  EMISSION_EQUIVALENCE(World,CO2,all,700)                      
 E  EMISSION_EQUIVALENCE(World,CO2,all,710)                      
 E  EMISSION_EQUIVALENCE(World,CO2,all,720)                      
 E  EMISSION_EQUIVALENCE(Westeros,CO2,all,700)                   
 E  EMISSION_EQUIVALENCE(Westeros,CO2,all,710)                   
 E  EMISSION_EQUIVALENCE(Westeros,CO2,all,720)                   
 L  EMISSION_CONSTRAINT(Westeros,GHG,all,cumulative)             
COLUMNS
    CAP_NEW(Westeros,coal_ppl,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                               -500
    CAP_NEW(Westeros,coal_ppl,700)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,700,700)                                -10
    CAP_NEW(Westeros,coal_ppl,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                               -500
    CAP_NEW(Westeros,coal_ppl,710)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,710,710)                                -10
    CAP_NEW(Westeros,coal_ppl,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                  -304.023646636842
    CAP_NEW(Westeros,coal_ppl,720)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,720,720)                                -10
    CAP_NEW(Westeros,wind_ppl,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                              -1500
    CAP_NEW(Westeros,wind_ppl,700)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,700,700)                                -10
    CAP_NEW(Westeros,wind_ppl,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                              -1500
    CAP_NEW(Westeros,wind_ppl,710)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,710,710)                                -10
    CAP_NEW(Westeros,wind_ppl,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                  -912.070939910527
    CAP_NEW(Westeros,wind_ppl,720)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,720,720)                                -10
    CAP_NEW(Westeros,bulb,700)                                     COST_ACCOUNTING_NODAL(Westeros,700)                                                 -5
    CAP_NEW(Westeros,bulb,700)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,700,700)                                     -1
    CAP_NEW(Westeros,bulb,710)                                     COST_ACCOUNTING_NODAL(Westeros,710)                                                 -5
    CAP_NEW(Westeros,bulb,710)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,710,710)                                     -1
    CAP_NEW(Westeros,bulb,720)                                     COST_ACCOUNTING_NODAL(Westeros,720)                                                 -5
    CAP_NEW(Westeros,bulb,720)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,720,720)                                     -1
    CAP(Westeros,coal_ppl,690,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                                -30
    CAP(Westeros,coal_ppl,690,700)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,690,700,year)                                 -1
    CAP(Westeros,coal_ppl,690,700)                                 CAPACITY_MAINTENANCE_HIST(Westeros,coal_ppl,690,700)                                 1
    CAP(Westeros,coal_ppl,700,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                                -30
    CAP(Westeros,coal_ppl,700,700)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,700,year)                                 -1
    CAP(Westeros,coal_ppl,700,700)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,700,700)                                  1
    CAP(Westeros,coal_ppl,700,700)                                 CAPACITY_MAINTENANCE(Westeros,coal_ppl,700,710)                                     -1
    CAP(Westeros,coal_ppl,700,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                                -30
    CAP(Westeros,coal_ppl,700,710)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,710,year)                                 -1
    CAP(Westeros,coal_ppl,700,710)                                 CAPACITY_MAINTENANCE(Westeros,coal_ppl,700,710)                                      1
    CAP(Westeros,coal_ppl,710,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                                -30
    CAP(Westeros,coal_ppl,710,710)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,710,year)                                 -1
    CAP(Westeros,coal_ppl,710,710)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,710,710)                                  1
    CAP(Westeros,coal_ppl,710,710)                                 CAPACITY_MAINTENANCE(Westeros,coal_ppl,710,720)                                     -1
    CAP(Westeros,coal_ppl,710,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                                -30
    CAP(Westeros,coal_ppl,710,720)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,720,year)                                 -1
    CAP(Westeros,coal_ppl,710,720)                                 CAPACITY_MAINTENANCE(Westeros,coal_ppl,710,720)                                      1
    CAP(Westeros,coal_ppl,720,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                                -30
    CAP(Westeros,coal_ppl,720,720)                                 CAPACITY_CONSTRAINT(Westeros,coal_ppl,720,720,year)                                 -1
    CAP(Westeros,coal_ppl,720,720)                                 CAPACITY_MAINTENANCE_NEW(Westeros,coal_ppl,720,720)                                  1
    CAP(Westeros,wind_ppl,690,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                                -10
    CAP(Westeros,wind_ppl,690,700)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,690,700,year)                              -0.36
    CAP(Westeros,wind_ppl,690,700)                                 CAPACITY_MAINTENANCE_HIST(Westeros,wind_ppl,690,700)                                 1
    CAP(Westeros,wind_ppl,700,700)                                 COST_ACCOUNTING_NODAL(Westeros,700)                                                -10
    CAP(Westeros,wind_ppl,700,700)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,700,year)                              -0.36
    CAP(Westeros,wind_ppl,700,700)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,700,700)                                  1
    CAP(Westeros,wind_ppl,700,700)                                 CAPACITY_MAINTENANCE(Westeros,wind_ppl,700,710)                                     -1
    CAP(Westeros,wind_ppl,700,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                                -10
    CAP(Westeros,wind_ppl,700,710)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,710,year)                              -0.36
    CAP(Westeros,wind_ppl,700,710)                                 CAPACITY_MAINTENANCE(Westeros,wind_ppl,700,710)                                      1
    CAP(Westeros,wind_ppl,710,710)                                 COST_ACCOUNTING_NODAL(Westeros,710)                                                -10
    CAP(Westeros,wind_ppl,710,710)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,710,year)                              -0.36
    CAP(Westeros,wind_ppl,710,710)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,710,710)                                  1
    CAP(Westeros,wind_ppl,710,710)                                 CAPACITY_MAINTENANCE(Westeros,wind_ppl,710,720)                                     -1
    CAP(Westeros,wind_ppl,710,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                                -10
    CAP(Westeros,wind_ppl,710,720)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,720,year)                              -0.36
    CAP(Westeros,wind_ppl,710,720)                                 CAPACITY_MAINTENANCE(Westeros,wind_ppl,710,720)                                      1
    CAP(Westeros,wind_ppl,720,720)                                 COST_ACCOUNTING_NODAL(Westeros,720)                                                -10
    CAP(Westeros,wind_ppl,720,720)                                 CAPACITY_CONSTRAINT(Westeros,wind_ppl,720,720,year)                              -0.36
    CAP(Westeros,wind_ppl,720,720)                                 CAPACITY_MAINTENANCE_NEW(Westeros,wind_ppl,720,720)                                  1
    CAP(Westeros,bulb,700,700)                                     CAPACITY_CONSTRAINT(Westeros,bulb,700,700,year)                                     -1
    CAP(Westeros,bulb,700,700)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,700,700)                                      1
    CAP(Westeros,bulb,710,710)                                     CAPACITY_CONSTRAINT(Westeros,bulb,710,710,year)                                     -1
    CAP(Westeros,bulb,710,710)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,710,710)                                      1
    CAP(Westeros,bulb,720,720)                                     CAPACITY_CONSTRAINT(Westeros,bulb,720,720,year)                                     -1
    CAP(Westeros,bulb,720,720)                                     CAPACITY_MAINTENANCE_NEW(Westeros,bulb,720,720)                                      1
    ACT(Westeros,coal_ppl,690,700,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,700)                                                -30
    ACT(Westeros,coal_ppl,690,700,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)                        1
    ACT(Westeros,coal_ppl,690,700,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,690,700,year)                                  1
    ACT(Westeros,coal_ppl,690,700,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,700,standard,year)                               1
    ACT(Westeros,coal_ppl,690,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,700,year)                                   1
    ACT(Westeros,coal_ppl,690,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,710,year)                       -2.5937424601
    ACT(Westeros,coal_ppl,690,700,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,700)                                           -7.4
    ACT(Westeros,coal_ppl,690,700,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,700)                                        -7.4
    ACT(Westeros,coal_ppl,700,700,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,700)                                                -30
    ACT(Westeros,coal_ppl,700,700,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)                        1
    ACT(Westeros,coal_ppl,700,700,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,700,year)                                  1
    ACT(Westeros,coal_ppl,700,700,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,700,standard,year)                               1
    ACT(Westeros,coal_ppl,700,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,700,year)                                   1
    ACT(Westeros,coal_ppl,700,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,710,year)                       -2.5937424601
    ACT(Westeros,coal_ppl,700,700,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,700)                                           -7.4
    ACT(Westeros,coal_ppl,700,700,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,700)                                        -7.4
    ACT(Westeros,coal_ppl,700,710,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,710)                                                -30
    ACT(Westeros,coal_ppl,700,710,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)                        1
    ACT(Westeros,coal_ppl,700,710,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,700,710,year)                                  1
    ACT(Westeros,coal_ppl,700,710,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,710,standard,year)                               1
    ACT(Westeros,coal_ppl,700,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,710,year)                                   1
    ACT(Westeros,coal_ppl,700,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,720,year)                       -2.5937424601
    ACT(Westeros,coal_ppl,700,710,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,710)                                           -7.4
    ACT(Westeros,coal_ppl,700,710,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,710)                                        -7.4
    ACT(Westeros,coal_ppl,710,710,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,710)                                                -30
    ACT(Westeros,coal_ppl,710,710,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)                        1
    ACT(Westeros,coal_ppl,710,710,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,710,year)                                  1
    ACT(Westeros,coal_ppl,710,710,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,710,standard,year)                               1
    ACT(Westeros,coal_ppl,710,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,710,year)                                   1
    ACT(Westeros,coal_ppl,710,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,720,year)                       -2.5937424601
    ACT(Westeros,coal_ppl,710,710,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,710)                                           -7.4
    ACT(Westeros,coal_ppl,710,710,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,710)                                        -7.4
    ACT(Westeros,coal_ppl,710,720,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,720)                                                -30
    ACT(Westeros,coal_ppl,710,720,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)                        1
    ACT(Westeros,coal_ppl,710,720,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,710,720,year)                                  1
    ACT(Westeros,coal_ppl,710,720,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,720,standard,year)                               1
    ACT(Westeros,coal_ppl,710,720,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,720,year)                                   1
    ACT(Westeros,coal_ppl,710,720,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,720)                                           -7.4
    ACT(Westeros,coal_ppl,710,720,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,720)                                        -7.4
    ACT(Westeros,coal_ppl,720,720,standard,year)                   COST_ACCOUNTING_NODAL(Westeros,720)                                                -30
    ACT(Westeros,coal_ppl,720,720,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)                        1
    ACT(Westeros,coal_ppl,720,720,standard,year)                   CAPACITY_CONSTRAINT(Westeros,coal_ppl,720,720,year)                                  1
    ACT(Westeros,coal_ppl,720,720,standard,year)                   ACTIVITY_BOUND_LO(Westeros,coal_ppl,720,standard,year)                               1
    ACT(Westeros,coal_ppl,720,720,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,720,year)                                   1
    ACT(Westeros,coal_ppl,720,720,standard,year)                   EMISSION_EQUIVALENCE(World,CO2,all,720)                                           -7.4
    ACT(Westeros,coal_ppl,720,720,standard,year)                   EMISSION_EQUIVALENCE(Westeros,CO2,all,720)                                        -7.4
    ACT(Westeros,wind_ppl,690,700,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)                        1
    ACT(Westeros,wind_ppl,690,700,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,690,700,year)                                  1
    ACT(Westeros,wind_ppl,690,700,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,700,standard,year)                               1
    ACT(Westeros,wind_ppl,690,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,700,year)                                   1
    ACT(Westeros,wind_ppl,690,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,710,year)                       -2.5937424601
    ACT(Westeros,wind_ppl,700,700,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)                        1
    ACT(Westeros,wind_ppl,700,700,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,700,year)                                  1
    ACT(Westeros,wind_ppl,700,700,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,700,standard,year)                               1
    ACT(Westeros,wind_ppl,700,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,700,year)                                   1
    ACT(Westeros,wind_ppl,700,700,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,710,year)                       -2.5937424601
    ACT(Westeros,wind_ppl,700,710,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)                        1
    ACT(Westeros,wind_ppl,700,710,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,700,710,year)                                  1
    ACT(Westeros,wind_ppl,700,710,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,710,standard,year)                               1
    ACT(Westeros,wind_ppl,700,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,710,year)                                   1
    ACT(Westeros,wind_ppl,700,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,720,year)                       -2.5937424601
    ACT(Westeros,wind_ppl,710,710,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)                        1
    ACT(Westeros,wind_ppl,710,710,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,710,year)                                  1
    ACT(Westeros,wind_ppl,710,710,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,710,standard,year)                               1
    ACT(Westeros,wind_ppl,710,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,710,year)                                   1
    ACT(Westeros,wind_ppl,710,710,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,720,year)                       -2.5937424601
    ACT(Westeros,wind_ppl,710,720,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)                        1
    ACT(Westeros,wind_ppl,710,720,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,710,720,year)                                  1
    ACT(Westeros,wind_ppl,710,720,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,720,standard,year)                               1
    ACT(Westeros,wind_ppl,710,720,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,720,year)                                   1
    ACT(Westeros,wind_ppl,720,720,standard,year)                   COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)                        1
    ACT(Westeros,wind_ppl,720,720,standard,year)                   CAPACITY_CONSTRAINT(Westeros,wind_ppl,720,720,year)                                  1
    ACT(Westeros,wind_ppl,720,720,standard,year)                   ACTIVITY_BOUND_LO(Westeros,wind_ppl,720,standard,year)                               1
    ACT(Westeros,wind_ppl,720,720,standard,year)                   ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,720,year)                                   1
    ACT(Westeros,grid,700,700,standard,year)                       COST_ACCOUNTING_NODAL(Westeros,700)                                                -50
    ACT(Westeros,grid,700,700,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,secondary,700,year)                       -1
    ACT(Westeros,grid,700,700,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,700,year)                          0.9
    ACT(Westeros,grid,700,700,standard,year)                       ACTIVITY_BOUND_LO(Westeros,grid,700,standard,year)                                   1
    ACT(Westeros,grid,710,710,standard,year)                       COST_ACCOUNTING_NODAL(Westeros,710)                                                -50
    ACT(Westeros,grid,710,710,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,secondary,710,year)                       -1
    ACT(Westeros,grid,710,710,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,710,year)                          0.9
    ACT(Westeros,grid,710,710,standard,year)                       ACTIVITY_BOUND_LO(Westeros,grid,710,standard,year)                                   1
    ACT(Westeros,grid,720,720,standard,year)                       COST_ACCOUNTING_NODAL(Westeros,720)                                                -50
    ACT(Westeros,grid,720,720,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,secondary,720,year)                       -1
    ACT(Westeros,grid,720,720,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,720,year)                          0.9
    ACT(Westeros,grid,720,720,standard,year)                       ACTIVITY_BOUND_LO(Westeros,grid,720,standard,year)                                   1
    ACT(Westeros,bulb,700,700,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,700,year)                           -1
    ACT(Westeros,bulb,700,700,standard,year)                       COMMODITY_BALANCE_GT(Westeros,light,useful,700,year)                                 1
    ACT(Westeros,bulb,700,700,standard,year)                       CAPACITY_CONSTRAINT(Westeros,bulb,700,700,year)                                      1
    ACT(Westeros,bulb,700,700,standard,year)                       ACTIVITY_BOUND_LO(Westeros,bulb,700,standard,year)                                   1
    ACT(Westeros,bulb,710,710,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,710,year)                           -1
    ACT(Westeros,bulb,710,710,standard,year)                       COMMODITY_BALANCE_GT(Westeros,light,useful,710,year)                                 1
    ACT(Westeros,bulb,710,710,standard,year)                       CAPACITY_CONSTRAINT(Westeros,bulb,710,710,year)                                      1
    ACT(Westeros,bulb,710,710,standard,year)                       ACTIVITY_BOUND_LO(Westeros,bulb,710,standard,year)                                   1
    ACT(Westeros,bulb,720,720,standard,year)                       COMMODITY_BALANCE_GT(Westeros,electricity,final,720,year)                           -1
    ACT(Westeros,bulb,720,720,standard,year)                       COMMODITY_BALANCE_GT(Westeros,light,useful,720,year)                                 1
    ACT(Westeros,bulb,720,720,standard,year)                       CAPACITY_CONSTRAINT(Westeros,bulb,720,720,year)                                      1
    ACT(Westeros,bulb,720,720,standard,year)                       ACTIVITY_BOUND_LO(Westeros,bulb,720,standard,year)                                   1
    COST_NODAL(World,700)                                          _obj                                                                  7.72173492918481
    COST_NODAL(World,700)                                          COST_ACCOUNTING_NODAL(World,700)                                                     1
    COST_NODAL(World,710)                                          _obj                                                                  4.74047541335517
    COST_NODAL(World,710)                                          COST_ACCOUNTING_NODAL(World,710)                                                     1
    COST_NODAL(World,720)                                          _obj                                                                  2.91024068434285
    COST_NODAL(World,720)                                          COST_ACCOUNTING_NODAL(World,720)                                                     1
    COST_NODAL(Westeros,700)                                       _obj                                                                  7.72173492918481
    COST_NODAL(Westeros,700)                                       COST_ACCOUNTING_NODAL(Westeros,700)                                                  1
    COST_NODAL(Westeros,710)                                       _obj                                                                  4.74047541335517
    COST_NODAL(Westeros,710)                                       COST_ACCOUNTING_NODAL(Westeros,710)                                                  1
    COST_NODAL(Westeros,720)                                       _obj                                                                  2.91024068434285
    COST_NODAL(Westeros,720)                                       COST_ACCOUNTING_NODAL(Westeros,720)                                                  1
    EMISS(World,CO2,all,700)                                       EMISSION_EQUIVALENCE(World,CO2,all,700)                                              1
    EMISS(World,CO2,all,710)                                       EMISSION_EQUIVALENCE(World,CO2,all,710)                                              1
    EMISS(World,CO2,all,720)                                       EMISSION_EQUIVALENCE(World,CO2,all,720)                                              1
    EMISS(Westeros,CO2,all,700)                                    EMISSION_EQUIVALENCE(Westeros,CO2,all,700)                                           1
    EMISS(Westeros,CO2,all,700)                                    EMISSION_CONSTRAINT(Westeros,GHG,all,cumulative)                     0.333333333333333
    EMISS(Westeros,CO2,all,710)                                    EMISSION_EQUIVALENCE(Westeros,CO2,all,710)                                           1
    EMISS(Westeros,CO2,all,710)                                    EMISSION_CONSTRAINT(Westeros,GHG,all,cumulative)                     0.333333333333333
    EMISS(Westeros,CO2,all,720)                                    EMISSION_EQUIVALENCE(Westeros,CO2,all,720)                                           1
    EMISS(Westeros,CO2,all,720)                                    EMISSION_CONSTRAINT(Westeros,GHG,all,cumulative)                     0.333333333333333
    constobj                                                       _obj                                                                                 1
RHS
    rhs                                                            COMMODITY_BALANCE_GT(Westeros,light,useful,700,year)                                55
    rhs                                                            COMMODITY_BALANCE_GT(Westeros,light,useful,710,year)                                82
    rhs                                                            COMMODITY_BALANCE_GT(Westeros,light,useful,720,year)                               104
    rhs                                                            CAPACITY_MAINTENANCE_HIST(Westeros,coal_ppl,690,700)                  18.2648401826484
    rhs                                                            CAPACITY_MAINTENANCE_HIST(Westeros,wind_ppl,690,700)                  33.8237781160156
    rhs                                                            ACTIVITY_CONSTRAINT_UP(Westeros,coal_ppl,700,year)                    47.3742915086758
    rhs                                                            ACTIVITY_CONSTRAINT_UP(Westeros,wind_ppl,700,year)                    31.5828610057839
    rhs                                                            EMISSION_CONSTRAINT(Westeros,GHG,all,cumulative)                                   500
BOUNDS
 FR bnd                                                            COST_NODAL(World,700)                                        
 FR bnd                                                            COST_NODAL(World,710)                                        
 FR bnd                                                            COST_NODAL(World,720)                                        
 FR bnd                                                            COST_NODAL(Westeros,700)                                     
 FR bnd                                                            COST_NODAL(Westeros,710)                                     
 FR bnd                                                            COST_NODAL(Westeros,720)                                     
 FR bnd                                                            EMISS(World,CO2,all,700)                                     
 FR bnd                                                            EMISS(World,CO2,all,710)                                     
 FR bnd                                                            EMISS(World,CO2,all,720)                                     
 FR bnd                                                            EMISS(Westeros,CO2,all,700)                                  
 FR bnd                                                            EMISS(Westeros,CO2,all,710)                                  
 FR bnd                                                            EMISS(Westeros,CO2,all,720)                                  
 FX bnd                                                            constobj                                                                             0
ENDATA
