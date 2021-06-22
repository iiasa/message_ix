***
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
* =========================== ================================================================================================================================
* Parameter                   Description
* =========================== ================================================================================================================================
* :math:`duration\_period_y`  Number of years in time period :math:`y` (forward diff)
* :math:`total\_cost_{n,y}`   Total system costs in region :math:`n` and period :math:`y` from MESSAGE model run
* :math:`enestart_{n,s,y}`    Consumption level of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`y` from MESSAGE model run
* :math:`eneprice_{n,s,y}`    Shadow prices of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`y` from MESSAGE model run
* :math:`\epsilon_n`          Elasticity of substitution between capital-labor and total energy in region :math:`n`
* :math:`\rho_n`              :math:`\epsilon - 1 / \epsilon` where :math:`\epsilon` is the elasticity of subsitution in region :math:`n`
* :math:`depr_n`              Annual depreciation rate in region :math:`n`
* :math:`\alpha_n`            Capital value share parameter in region :math:`n`
* :math:`a_n`                 Production function coefficient of capital and labor in region :math:`n`
* :math:`b_{n,s}`             Production function coefficients of the different end-use sectors in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`udf_{n,y}`           Utility discount factor in period year in region :math:`n` and period :math:`y`
* :math:`newlab_{n,y}`        New vintage of labor force in region :math:`n` and period :math:`y`
* :math:`grow_{n,y}`          Annual growth rates of potential GDP in region :math:`n` and period :math:`y`
* :math:`aeei_{n,s,y}`        Autonomous energy efficiency improvement (AEEI) in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`fin\_time_{n,y}`     finite time horizon correction factor in utility function in region :math:`n` and period :math:`y`
* =========================== ================================================================================================================================
***

*----------------------------------------------------------------------------------------------------------------------*
* Variable definitions                                                                                                 *
*----------------------------------------------------------------------------------------------------------------------*

***
* Decision variables
* ~~~~~~~~~~~~~~~~~~~~
*
* ======================== ==================================================== ======================================================================================================
* Variable                 Definition                                           Description
* ======================== ==================================================== ======================================================================================================
* :math:`K_{n,y}`          :math:`{K}_{n, y}\geq 0 ~ \forall n, y`              Capital stock in region :math:`n` and period :math:`y`
* :math:`KN_{n,y}`         :math:`{KN}_{n, y}\geq 0 ~ \forall n, y`             New Capital vintage in region :math:`n` and period :math:`y`
* :math:`Y_{n,y}`          :math:`{Y}_{n, y}\geq 0 ~ \forall n, y`              Total production in region :math:`n` and period :math:`y`
* :math:`YN_{n,y}`         :math:`{YN}_{n, y}\geq 0 ~ \forall n, y`             New production vintage in region :math:`n` and period :math:`y`
* :math:`C_{n,y}`          :math:`{C}_{n, y}\geq 0 ~ \forall n, y`              Consumption in region :math:`n` and period :math:`y`
* :math:`I_{n,y}`          :math:`{I}_{n, y}\geq 0 ~ \forall n, y`              Investment in region :math:`n` and period :math:`y`
* :math:`PHYSENE_{n,s,y}`  :math:`{PHYSENE}_{n, s, y}\geq 0 ~ \forall n, s, y`  Physical end-use service use in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`PRODENE_{n,s,y}`  :math:`{PRODENE}_{n, s, y}\geq 0 ~ \forall n, s, y`  Value of end-use service in the production function in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`NEWENE_{n,s,y}`   :math:`{NEWENE}_{n, s, y}\geq 0 ~ \forall n, s, y`   New end-use service in the production function in region :math:`n`, sector :math:`s` and period :math:`y`
* :math:`EC_{n,y}`         :math:`EC \in \left[-\infty..\infty\right]`          Approximation of system costs based on MESSAGE results
* :math:`UTILITY`          :math:`UTILITY \in \left[-\infty..\infty\right]`     Utility function (discounted log of consumption)
* ======================== ==================================================== ======================================================================================================
*
***

* ------------------------------------------------------------------------------
* model variable declaration
* ------------------------------------------------------------------------------

POSITIVE VARIABLES
    K(node, year_all)                Capital stock in period year
    KN(node, year_all)               New Capital vintage in period year
    Y(node, year_all)                Production in period year
    YN(node, year_all)               New production vintage in period year

    PHYSENE(node, sector, year_all)  Physical end-use service or commodity use
    PRODENE(node, sector, year_all)  Value of end-use services or commodities in the production function
    NEWENE(node, sector, year_all)   New end-use service or commodity (production function value)

    C(node, year_all)                Consumption (Trillion $)
    I(node, year_all)                Investment (Trillion $)
;

VARIABLES
    UTILITY                          Utility function (discounted log of consumption)
    EC(node, year_all)               System costs (Trillion $) based on MESSAGE model run
;

Variables
* auxiliary variables for demand, prices, costs and GDP (for reporting when MESSAGE is run with MACRO)
    GDP(node,year_all)               gross domestic product (GDP) in market exchange rates for MACRO reporting
;

* ------------------------------------------------------------------------------
* model equations declaration
* ------------------------------------------------------------------------------

EQUATIONS
    UTILITY_FUNCTION                      Utility funciton (discounted log of consumpiton summed over all projection periods)
    CAPITAL_CONSTRAINT(node, year_all)    Capital constraint

    NEW_CAPITAL(node, year_all)           New capital
    NEW_PRODUCTION(node, year_all)        New production

    TOTAL_CAPITAL(node, year_all)         Total capital stock across all vintages
    TOTAL_PRODUCTION(node, year_all)      Total production across all vintages

    NEW_ENERGY(node, sector, year_all)    New end-use services or commodities (production function)
    ENERGY_SUPPLY(node, sector, *)        Supply of end-use services or commodities

    COST_ENERGY(node, year_all)           system costs approximation based on MESSAGE input
    TERMINAL_CONDITION(node, year_all)    Terminal condition
;

* ------------------------------------------------------------------------------
* model equations definition
* ------------------------------------------------------------------------------

***
* Equation UTILITY_FUNCTION
* ---------------------------------
* The utility function which is maximized sums up the discounted logarithm of consumption of a single representative producer-consumer over the entire time horizon
* of the model.
*
* .. math:: {UTILITY} = \sum_{n} \bigg( &  \sum_{y |  (  (  {ord}( y )   >  1 )  \wedge  (  {ord}( y )   <   | y |  )  )} {udf}_{n, y} \cdot {\log}( C_{n, y} ) \cdot {duration\_period}_{y} \\
*                                 + &\sum_{y |  (  {ord}( y ) =  | y | ) } {udf}_{n, y} \cdot {\log}( C_{n, y} ) \cdot \big( {duration\_period}_{y-1} + \frac{1}{{FIN\_TIME}_{n, y}} \big) \bigg)
*
* The utility discount rate for period :math:`y` is set to :math:`drate_{n} - grow_{n,y}`, where :math:`drate_{n}` is the discount rate used in MESSAGE, typically set to 5%,
* and :math:`grow` is the potential GDP growth rate. This choice ensures that in the steady state, the optimal growth rate is identical to the potential GDP growth rates :math:`grow`.
* The values for the utility discount rates are chosen for descriptive rather than normative reasons. The term :math:`\frac{{duration\_period}_{y} + {duration\_period}_{y-1}}{2}` mutliples the
* discounted logarithm of consumption with the period length. The final period is treated separately to include a correction factor :math:`\frac{1}{{FIN\_TIME}_{n, y}}` reflecting
* the finite time horizon of the model. Note that the sum over nodes :math:`node\_active` is artificial, because :math:`node\_active` only contains one element.
*
***

UTILITY_FUNCTION..
UTILITY =E=
SUM(node_active,
    1000 * (SUM(year $ (NOT macro_base_period(year) AND NOT last_period(year)),
                udf(node_active, year) * LOG(C(node_active, year)) * duration_period(year))
          + SUM(year $ last_period(year),
                udf(node_active, year) * LOG(C(node_active, year)) * (duration_period(year) + 1/finite_time_corr(node_active, year))))
)
;

***
* Equation CAPITAL_CONSTRAINT
* ---------------------------------
* The following equation specifies the allocation of total production among current consumption :math:`{C}_{n, y}`, investment into building up capital stock excluding
* the sectors represented in MESSAGE :math:`{I}_{n, y}` and the MESSAGE system costs :math:`{EC}_{n, y}` which are derived from a previous MESSAGE model run. MESSAGE system
* costs are all the energy system costs for a certain region including the trade balance from fuel and emissions certificate trade. Therefore, the constraint assures that the net
* expenditures and savings cannot exceed the total income in a region. As described in :cite:`manne_buying_1992`, the first-order optimality conditions lead to the Ramsey rule for
* the optimal allocation of investment and consumption over time. Positive contribution of EC to GDP would be counter balanced by the decrease of consumption :math:`{C}_{n, y}` and
* investment :math:`{I}_{n, y}` in the certain year as well as by the reduction in capacity to invest and grow the economy for later years. 

* The NEW PRODUCTION equation in MACRO only accounts for non-energy producing part of the economy and the energy system is modeled seperately in MESSAGE. In addition, MACRO does not include
* the trade of normal goods, therefore there is not an explicit component in the equation which takes the trade revenues into account. However, the revenues from energy goods and emission allowances
* would increase the domestic income and therefore should be accounted in the GDP definition. This is done via deducting the trade costs of MESSAGE in GDP reporting. This component is not added
* to capital constraint as trade is not represented in MACRO. 
*
* .. math:: Y_{n, y} = C_{n, y} + I_{r, y} + {EC}_{n, y} \qquad \forall{n, y}
*
***

CAPITAL_CONSTRAINT(node_active, year)..
Y(node_active, year) =E=
C(node_active, year) + I(node_active, year) + EC(node_active, year)
;

***
* Equation NEW_CAPITAL
* ---------------------------------
* The accumulation of capital in the sectors not represented in MESSAGE is governed by new capital stock equation. Net capital formation :math:`{KN}_{n,y}` is derived from gross
* investments :math:`{I}_{n,y}` minus depreciation of previsouly existing capital stock.
*
* .. math:: {KN}_{n,y} = {duration\_period}_{y} \cdot I_{n,y} \qquad \forall{n, y > 1}
*
* Here, the initial boundary condition for the base year :math:`y_0` implies for the investments that :math:`I_{n,y_0} = (grow_{n,y_0} + depr_{n}) \cdot kgdp_{n} \cdot gdp_{n,y_0}`.
***

NEW_CAPITAL(node_active, year) $ (NOT macro_base_period(year))..
KN(node_active, year) =E= duration_period(year) * I(node_active, year)
;

***
* Equation NEW_PRODUCTION
* ---------------------------------
* MACRO employs a nested constant elasticity of substitution (CES) production function with capital, labor and the (commercial) end-use services
* represented in MESSAGE as inputs. This version of the production function is equaivalent to that in MARKAL-MACRO.
*
* .. math:: {YN}_{n,y} =  { \left( {a}_{n} \cdot {{KN}_{n, y}}^{ ( {\rho}_{n} \cdot {\alpha}_{n} ) } \cdot {{newlab}_{n, y}}^{ ( {\rho}_{n} \cdot ( 1 - {\alpha}_{n} ) ) } + \displaystyle \sum_{s} ( {b}_{n, s} \cdot {{NEWENE}_{n, s, y}}^{{\rho}_{n}} )  \right) }^{ \frac{1}{{\rho}_{n}} } \qquad \forall{ n, y > 1}
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
* of capital stock in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`depr_{n}`, and the capital stock added in the current period :math:`y`.
*
* .. math:: K_{n, y} = K_{n, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {KN}_{n, y} \qquad \forall{ n, y > 1}
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
* depreciated with the depreciation rate :math:`depr_{n}`, and the new vintage of production from period :math:`y`.
*
* .. math:: Y_{n, y} = Y_{n, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {YN}_{n, y} \qquad \forall{ n, y > 1}
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
* in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`depr_{n}`, and the the new vintage of energy production from
* period :math:`y`.
*
* .. math:: {PRODENE}_{n, s, y} = {PRODENE}_{n, s, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {NEWENE}_{n, s, y} \qquad \forall{ n, s, y > 1}
*
***

NEW_ENERGY(node_active, sector, year) $ (NOT macro_base_period(year))..
PRODENE(node_active, sector, year) =E=
SUM(year2$( seq_period(year2,year) ), PRODENE(node_active, sector, year2)) * (1 - depr(node_active))**duration_period(year) + NEWENE(node_active, sector, year)
;

***
* Equation ENERGY_SUPPLY
* ---------------------------------
* The relationship below establishes the link between physical energy :math:`{PHYSENE}_{r, s, y}` as accounted in MESSAGE for the six commerical energy demands :math:`s` and
* energy in terms of monetary value :math:`{PRODENE}_{n, s, y}` as specified in the production function of MACRO.
*
* .. math:: {PHYSENE}_{n, s, y} \geq {PRODENE}_{n, s, y} \cdot {aeei\_factor}_{n, s, y} \qquad \forall{ n, s, y > 1}
*
* The cumulative effect of autonomous energy efficiency improvements (AEEI) is captured in
* :math:`{aeei\_factor}_{n,s,y} = {aeei\_factor}_{n, s, y-1} \cdot (1 - {aeei}_{n,s,y})^{duration\_period}_{y}`
* with :math:`{aeei\_factor}_{n,s,y=1} = 1`. Therefore, choosing the :math:`{aeei}_{n,s,y}` coefficients appropriately offers the possibility to calibrate MACRO to a certain energy demand trajectory
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
* first order term using shadow prices :math:`eneprice_{s, y, n}` of the MESSAGE model's solution and a quadratic second-order term.
*
* .. math:: {EC}_{n, y} =  & {total\_cost}_{n, r} \\
*                        + & \displaystyle \sum_{s} {eneprice}_{s, y, n} \cdot \left( {PHYSENE}_{n, s, y} - {enestart}_{s, y, n} \right) \\
*                        + & \displaystyle \sum_{s} \frac{{eneprice}_{s, y, n}}{{enestart}_{s, y, n}} \cdot \left( {PHYSENE}_{n, s, y} - {enestart}_{s, y, n} \right)^2 \qquad \forall{ n, y > 1}
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
* provide net growth of capital stock beyond MACRO's time horizon :cite:`manne_buying_1992`. The goal is to avoid to the extend possible model artifacts resulting from this finite time horizon
* cutoff.
*
* .. math:: K_{n, y} \cdot  \left( grow_{n, y} + {depr}_n \right) \leq I_{n, y} \qquad \forall{ n, y = last year}
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
