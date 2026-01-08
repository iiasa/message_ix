***
* .. _macro-core:
*
* MACRO core formulation
* ======================
*
* MACRO is a macroeconomic model maximizing the intertemporal utility function of a single representative producer-consumer
* in each node (or macro-economic region). The optimization result is a sequence of optimal savings, investment, and consumption decisions.
* The main variables of the model are the capital stock, available labor, and commodity inputs, which together determine the
* total output of an economy according to a nested constant elasticity of substitution (CES) production function. End-use service
* demands in the (commercial) demand categories of MESSAGE is determined within the model, and is consistent with commodity
* supply curves, which are inputs to the model.
*
***

*----------------------------------------------------------------------------------------------------------------------*
* Notation declaration                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* Notation declaration
* ~~~~~~~~~~~~~~~~~~~~
* The following short notation is used in the mathematical description relative to the GAMS code:
*
* ============== =============================== ===================================================================
* Math Notation  GAMS set & index notation       Description
* ============== =============================== ===================================================================
* :math:`n`      node (or node_active in loops)  spatial node corresponding to the macro-economic MESSAGE regions
* :math:`y`      year                            year (2005, 2010, 2020, ..., 2100)
* :math:`s`      sector                          sector corresponding to the (commercial) end-use demands of MESSAGE
* ============== =============================== ===================================================================
*
* A listing of all parameters used in MACRO together with a decription can be found in the table below.
*
* ================================== ================================================================================================================================
* Parameter                          Description
* ================================== ================================================================================================================================
* :math:`\text{period}_t`            Number of years in time period :math:`t` (forward diff)
* :math:`\text{total_cost}_{n,t}`    Total system costs in region :math:`n` and period :math:`t` from MESSAGE model run
* :math:`\text{enestart}_{n,s,t}`    Consumption level of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`t` from MESSAGE model run
* :math:`\text{p}_{n,s,t}`           Shadow prices of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`t` from MESSAGE model run
* :math:`\text{E}_{min,n,s,t}`       Subsistence level of direct energy consumption (end-use service) in region :math:`n`, sector :math:`s` and period :math:`t`
* :math:`\text{h}_{n,s,t}`           Share of the direct energy consumption of the total energy production in region :math:`n`, sector :math:`s` and period :math:`t`

* :math:`\epsilon_n`                 Elasticity of substitution between capital-labor and total energy in region :math:`n`
* :math:`\rho_n`                     :math:`\epsilon - 1 / \epsilon` where :math:`\epsilon` is the elasticity of substitution in region :math:`n`
* :math:`\beta_n`                    Consumption value share parameter in region :math:`n`
* :math:`\sigma_{n,s}`               Direct energy consumption value share parameter in region :math:`n` and of sector :math:`s`
* :math:`\delta_n`                   Annual depreciation rate in region :math:`n`
* :math:`\alpha_n`                   Capital value share parameter in region :math:`n`
* :math:`a_n`                        Production function coefficient of capital and labor in region :math:`n`
* :math:`b_{n,s}`                    Production function coefficients of the different end-use sectors in region :math:`n`, sector :math:`s` and period :math:`t`
* :math:`\text{udf}_{n,t}`           Utility discount factor in period year in region :math:`n` and period :math:`t`
* :math:`\text{L}_{n,t}`             Labor force in region :math:`n` and period :math:`t`
* :math:`\text{w}_{n,t}`             Wage rate in region :math:`n` and period :math:`t`
* :math:`\text{grow}_{n,t}`          Annual growth rates of potential GDP in region :math:`n` and period :math:`t`
* :math:`\text{aeei}_{n,s,t}`        Autonomous energy efficiency improvement (AEEI) in region :math:`n`, sector :math:`s` and period :math:`t`
* :math:`\text{fin_time}_{n,t}`      Finite time horizon correction factor in utility function in region :math:`n` and period :math:`t`
* ================================== ================================================================================================================================
***

*----------------------------------------------------------------------------------------------------------------------*
* Variable definitions                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* Decision variables
* ~~~~~~~~~~~~~~~~~~~~
*
* =============================== =========================================================== ==============================================================================================================
* Variable                        Definition                                                  Description
* =============================== =========================================================== ==============================================================================================================
* :math:`\text{K}_{n,y}`          :math:`\text{K}_{n, y}\geq 0 ~ \forall n, y`                Capital stock in region :math:`n` and period :math:`y`
* :math:`\text{Y}_{n,y}`          :math:`\text{Y}_{n, y}\geq 0 ~ \forall n, y`                Total production in region :math:`n` and period :math:`y`
* :math:`\text{C}_{n,y}`          :math:`\text{C}_{n, y}\geq 0 ~ \forall n, y`                Consumption in region :math:`n` and period :math:`y`
* :math:`\text{PHYSENE}_{n,s,y}`  :math:`\text{PHYSENE}_{n, s, y}\geq 0 ~ \forall n, s, y`    Physical end-use service use in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`\text{TE}_{n,s,y}`       :math:`\text{TE}_{n, s, y}\geq 0 ~ \forall n, s, y`         Value of total end-use service in the production function and utility function in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`\text{E}_{n,s,y}`        :math:`\text{E}_{n, s, y}\geq 0 ~ \forall n, s, y`          Value of direct energy consumption of end-use service of households in the utility function in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`\text{YE}_{n,s,y}`       :math:`\text{YE}_{n, s, y}\geq 0 ~ \forall n, s, y`         Value of end-use service energy consumption in the production function in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`\text{UTILITY}`          :math:`\text{UTILITY} \in \left[-\infty..\infty\right]`     Utility function (discounted log of consumption)
* =============================== =========================================================== ==============================================================================================================
*
***

* ------------------------------------------------------------------------------
* model variable declaration
* ------------------------------------------------------------------------------

POSITIVE VARIABLES
    K(node, year_all)                Capital stock in period year
    Y(node, year_all)                Total GDP

    PHYSENE(node, sector, year_all)
    TE(node, sector, year_all)  Value of end-use services or commodities in the production function
    E(node, sector, year_all)
    YE(node, sector, year_all)

    C(node, year_all)                Consumption (Trillion $)
;

VARIABLES
    UTILITY                          Utility function (discounted log of consumption)
;

Variables
* auxiliary variables for demand, prices, costs and GDP (for reporting when MESSAGE is run with MACRO)
    GDP(node,year_all)               gross domestic product (GDP) in market exchange rates for MACRO reporting
;

* ------------------------------------------------------------------------------
* model equations declaration
* ------------------------------------------------------------------------------

EQUATIONS
    UTILITY_FUNCTION                      Utility function (discounted log of consumption summed over all projection periods)
    
    CAPITAL(node, year_all)               Capital (wealth) formation

    PRODUCTION(node, year_all)            Total production across all vintages

    ENERGY_ACCOUNTING(node, sector, *)    New Energy Accounting Equations: Splitting TE into E and YE
    ENERGY_ACCOUNTING2(node, sector, *)   New Energy Accounting Equations: Defining E as share of the total energy TE
    TE_EQUATION(node, sector, *)          New Energy Accounting Equations: Determining TE based on optimal direct energy consumption of the households

    ENERGY_SUPPLY(node, sector, year_all) New Energy Accounting Equations: PHYSENE - TE relation with aeei

    TERMINAL_CONDITION(node, year_all)    New terminal condition
;

* ------------------------------------------------------------------------------
* model equations definition
* ------------------------------------------------------------------------------

***
* Equation UTILITY_FUNCTION
* ---------------------------------
* The utility function, which is maximized, sums the discounted logarithm of consumption :math:`\text{C}_{n,y}` and direct energy consumption 
* of end-use services :math:`\text{E}_{n,s,y}` of a single representative household over the entire time horizon of the model.
*
* The utility function and the capital formulation of the optimization problem are derived in previously (See equations 10 and 13 of the model documentation). 
*
* .. math:: \text{UTILITY} = \sum_{n} \bigg( &  \sum_{y |  (  (  {ord}( y )   >  1 )  \wedge  (  {ord}( y )   <   | y |  )  )} \text{udf}_{n, y} \cdot \bigg( (\beta_n + \sum_{s=1}^{3} \sigma_{s,n}) \log(\text{C}_{n, y}) - \sum_{s=1}^{3} \sigma_{s,n} \log(\text{p}_{n,s,y}) + \sum_{s=1}^{3} \sigma_{s,n} \log\left(\frac{\sigma_{s,n}}{\beta_n}\right) \bigg) \cdot \text{duration_period}_{y} \\
*                                 + &\sum_{y |  (  {ord}( y ) =  | y | ) } \text{udf}_{n, y} \cdot \bigg( (\beta_n + \sum_{s=1}^{3} \sigma_{s,n}) \log(\text{C}_{n, y}) - \sum_{s=1}^{3} \sigma_{s,n} \log(\text{p}_{n,s,y}) + \sum_{s=1}^{3} \sigma_{s,n} \log\left(\frac{\sigma_{s,n}}{\beta_n}\right) \bigg) \cdot \big( \text{duration_period}_{y-1} + \frac{1}{\text{fin_time}_{n, y}} \big) \bigg)
*
*
***

UTILITY_FUNCTION..
UTILITY =E=
SUM(node_active,
    1000 * (SUM(year $ (NOT macro_base_period(year) AND NOT last_period(year)),
            udf(node_active, year) * ( (alpha(node_active) + beta_rc_spec(node_active) + beta_rc_therm(node_active) + beta_transport(node_active)) * LOG(C(node_active, year)) 
            - beta_rc_spec(node_active) * LOG(eneprice(node_active, 'rc_spec', year)/1000) + beta_rc_spec(node_active) * LOG(beta_rc_spec(node_active)/alpha(node_active)) 
            - beta_rc_therm(node_active) * LOG(eneprice(node_active, 'rc_therm', year)/1000) + beta_rc_therm(node_active) * LOG(beta_rc_therm(node_active)/alpha(node_active))
            - beta_transport(node_active) * LOG(eneprice(node_active, 'transport', year)/1000) + beta_transport(node_active) * LOG(beta_transport(node_active)/alpha(node_active)) ) * duration_period(year) )
        + SUM(year $ last_period(year),
            udf(node_active, year) * ( (alpha(node_active) + beta_rc_spec(node_active) + beta_rc_therm(node_active) + beta_transport(node_active)) * LOG(C(node_active, year)) 
            - beta_rc_spec(node_active) * LOG(eneprice(node_active, 'rc_spec', year)/1000) + beta_rc_spec(node_active) * LOG(beta_rc_spec(node_active)/alpha(node_active)) 
            - beta_rc_therm(node_active) * LOG(eneprice(node_active, 'rc_therm', year)/1000) + beta_rc_therm(node_active) * LOG(beta_rc_therm(node_active)/alpha(node_active))
            - beta_transport(node_active) * LOG(eneprice(node_active, 'transport', year)/1000) + beta_transport(node_active) * LOG(beta_transport(node_active)/alpha(node_active)) ) * (duration_period(year) ) + 1/finite_time_corr(node_active, year)) )
)
;

***
* Equation CAPITAL
* ---------------------------------
*
* The household maximizes its utility subject to the constraint on wealth accumulation of capital in the sectors not represented in the energy model MESSAGE.
* The net capital (or wealth) formation :math:`\text{K}_{n,t}` is derived from the existing capital stock, returns on capital, labor income, minus the expenses
* for direct energy consumption and all other consumption goods, as well as depreciation of the previous capital stock.
*
* .. math:: \text{K}_{t+1,n} = (1 - \delta_{n})^{\text{period}_{t}} \text{K}_{t,n} + ((1 + r_{t,n})^{\text{period}_{t}} - 1) \text{K}_{t,n} + \text{period}_{t} \left( w_{t,n} L_{t,n} - \sum_{s=1}^{3} p_{t,s,n} L_{n,t} E_{min,t,s,n} - \frac{\beta + \sum_{s=1}^{3} \sigma_{s,n}}{\beta} C_{t,n} \right) \qquad (15)
*
***

CAPITAL(node_active, year) $ (NOT macro_base_period(year))..
K(node_active, year) =E=
SUM(year2$( seq_period(year2,year) ), K(node_active, year2) * (1 - depr(node_active))**duration_period(year2) + K(node_active, year2) * ((1 + interestrate(year2))**duration_period(year2) - 1) 
+ duration_period(year2) * labor(node_active, year2) * wage(node_active, year2) 
- duration_period(year2) * eneprice(node_active, 'rc_spec', year2)/1000 * labor(node_active, year2) * EMIN(node_active)
- duration_period(year2) * eneprice(node_active, 'rc_therm', year2)/1000 * labor(node_active, year2) * EMIN(node_active) 
- duration_period(year2) * eneprice(node_active, 'transport', year2)/1000 * labor(node_active, year2) * EMIN(node_active) 
- duration_period(year2) * (((alpha(node_active) + beta_rc_spec(node_active) + beta_rc_therm(node_active) + beta_transport(node_active))/alpha(node_active))) * C(node_active, year2)
) 
;

***
* Equation PRODUCTION
* ---------------------------------
*
* We implement a nested constant elasticity of substitution (CES) production function with capital, labor, and the (commercial) end-use services 
* represented in MESSAGE as inputs. :math:`\text{Y}_{n,t}` should correspond to gross domestic product (GDP).
*
* .. math:: \text{Y}_{n,t} = \left( a_{n} \cdot \text{K}_{n, t}^{ ( \rho_{n} \cdot \alpha_{n} ) } \cdot \text{L}_{n, t}^{ ( \rho_{n} \cdot ( 1 - \alpha_{n} ) ) } + \sum_{s} ( b_{n, s} \cdot \text{YE}_{n, s, t}^{\rho_{n}} ) \right)^{ \frac{1}{\rho_{n}} } \qquad \forall n, t > 1 \qquad (16)
*
***

NEW_PRODUCTION(node_active, year) $ (NOT macro_base_period(year))..
YN(node_active, year) =E=
( LAKL(node_active) * KN(node_active, year)**(rho(node_active) * kpvs(node_active)) * newlab(node_active, year)**(RHO(node_active) * (1 - kpvs(node_active)))
+ SUM(sector, PRFCONST(node_active, sector) * NEWENE(node_active, sector, year)**rho(node_active)) )**(1/rho(node_active))
;

***
* Equation TOTAL_CAPITAL
* ---------------------------------
* Equivalent to the total production equation above, the total capital stock, again excluding those sectors which are modeled in MESSAGE, is then simply a summation
* of capital stock in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`\text{depr}_{n}`, and the capital stock added in the current period :math:`y`.
*
* .. math:: \text{K}_{n, y} = \text{K}_{n, y-1} \cdot { \left( 1 - \text{depr}_n \right) }^{\text{duration_period}_{y}} + \text{KN}_{n, y} \qquad \forall{ n, y > 1}
*
***

TOTAL_CAPITAL(node_active, year) $ (NOT macro_base_period(year))..
K(node_active, year) =E=
SUM(year2$( seq_period(year2,year) ), K(node_active, year2)) * (1 - depr(node_active))**duration_period(year) + KN(node_active, year)
;

***
* Equation TOTAL_PRODUCTION
* ---------------------------------
* Total production in the economy (excluding energy sectors) is the sum of production from  assets that were already existing in the previous period :math:`y-1`,
* depreciated with the depreciation rate :math:`\text{depr}_{n}`, and the new vintage of production from period :math:`y`.
*
* .. math:: \text{Y}_{n, y} = \text{Y}_{n, y-1} \cdot { \left( 1 - \text{depr}_n \right) }^{\text{duration_period}_{y}} + \text{YN}_{n, y} \qquad \forall{ n, y > 1}
*
***

TOTAL_PRODUCTION(node_active, year) $ (NOT macro_base_period(year))..
Y(node_active, year) =E=
SUM(year2$( seq_period(year2,year) ), Y(node_active, year2)) * (1 - depr(node_active))**duration_period(year) + YN(node_active, year)
;

***
* Equation NEW_ENERGY
* ---------------------------------
* Total energy production (across the six commerical energy demands :math:`s`) is the sum of production from all assets that were already existing
* in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`\text{depr}_{n}`, and the the new vintage of energy production from
* period :math:`y`.
*
* .. math:: \text{PRODENE}_{n, s, y} = \text{PRODENE}_{n, s, y-1} \cdot { \left( 1 - \text{depr}_n \right) }^{\text{duration_period}_{y}} + \text{NEWENE}_{n, s, y} \qquad \forall{ n, s, y > 1}
*
***

NEW_ENERGY(node_active, sector, year) $ (NOT macro_base_period(year))..
PRODENE(node_active, sector, year) =E=
SUM(year2$( seq_period(year2,year) ), PRODENE(node_active, sector, year2)) * (1 - depr(node_active))**duration_period(year) + NEWENE(node_active, sector, year)
;

***
* Equation ENERGY_SUPPLY
* ---------------------------------
* The relationship below establishes the link between physical energy :math:`\text{PHYSENE}_{r, s, y}` as accounted in MESSAGE for the six commerical energy demands :math:`s` and
* energy in terms of monetary value :math:`\text{PRODENE}_{n, s, y}` as specified in the production function of MACRO.
*
* .. math:: \text{PHYSENE}_{n, s, y} \geq \text{PRODENE}_{n, s, y} \cdot \text{aeei_factor}_{n, s, y} \qquad \forall{ n, s, y > 1}
*
* The cumulative effect of autonomous energy efficiency improvements (AEEI) is captured in
* :math:`\text{aeei_factor}_{n,s,y} = \text{aeei_factor}_{n, s, y-1} \cdot (1 - \text{aeei}_{n,s,y})^{\text{duration_period}_{y}}`
* with :math:`\text{aeei_factor}_{n,s,y=1} = 1`. Therefore, choosing the :math:`\text{aeei}_{n,s,y}` coefficients appropriately offers the possibility to calibrate MACRO to a certain energy demand trajectory
* from MESSAGE.
*
***

ENERGY_SUPPLY(node_active, sector, year) $ (NOT macro_base_period(year))..
PHYSENE(node_active, sector, year) =G=
PRODENE(node_active, sector, year) * aeei_factor(node_active, sector, year)
;

***
* Equation COST_ENERGY
* ---------------------------------
* Energy system costs are based on a previous MESSAGE model run. The approximation of energy system costs in vicinity of the MESSAGE solution are approximated by a Taylor expansion with the
* first order term using shadow prices :math:`\text{eneprice}_{s, y, n}` of the MESSAGE model's solution and a quadratic second-order term.
*
* .. math:: \text{EC}_{n, y} =  & \text{total_cost}_{n, r} \\
*                        + & \displaystyle \sum_{s} \text{eneprice}_{s, y, n} \cdot \left( \text{PHYSENE}_{n, s, y} - \text{enestart}_{s, y, n} \right) \\
*                        + & \displaystyle \sum_{s} \frac{\text{eneprice}_{s, y, n}}{\text{enestart}_{s, y, n}} \cdot \left( \text{PHYSENE}_{n, s, y} - \text{enestart}_{s, y, n} \right)^2 \qquad \forall{ n, y > 1}
*
***

COST_ENERGY(node_active, year) $ (NOT macro_base_period(year))..
EC(node_active, year) =E=
(total_cost(node_active, year)/1000
+ SUM(sector, eneprice(node_active, sector, year) * 1E-3 * (PHYSENE(node_active, sector, year) - enestart(node_active, sector, year)))
+ SUM(sector, eneprice(node_active, sector, year) * 1E-3 / enestart(node_active, sector, year) * (PHYSENE(node_active, sector, year) - enestart(node_active, sector, year)) * (PHYSENE(node_active, sector, year) - enestart(node_active, sector, year))))
;

***
* Equation TERMINAL_CONDITION
* ---------------------------------
* Given the finite time horizon of MACRO, a terminal constraint needs to be applied to ensure that investments are chosen at an appropriate level, i.e. to replace depriciated capital and
* provide net growth of capital stock beyond MACRO's time horizon :cite:`Manne-Richels-1992`. The goal is to avoid to the extend possible model artifacts resulting from this finite time horizon
* cutoff.
*
* .. math:: \text{K}_{n, y} \cdot  \left( \text{grow}_{n, y} + \text{depr}_n \right) \leq \text{I}_{n, y} \qquad \forall{ n, y = \text{last year}}
***

TERMINAL_CONDITION(node_active, last_period)..
I(node_active, last_period) =G= K(node_active, last_period) * (grow(node_active, last_period) + depr(node_active))
;

* ------------------------------------------------------------------------------
* model definition
* ------------------------------------------------------------------------------

MODEL MESSAGE_MACRO /
    UTILITY_FUNCTION
    CAPITAL_CONSTRAINT
    NEW_CAPITAL
    NEW_PRODUCTION
    TOTAL_CAPITAL
    TOTAL_PRODUCTION
    NEW_ENERGY
    ENERGY_SUPPLY
    COST_ENERGY
    TERMINAL_CONDITION
/ ;

MESSAGE_MACRO.optfile = 1;
