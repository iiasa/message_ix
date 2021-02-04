.. note:: This page is generated from inline documentation in ``MACRO\macro_core.gms``.

MACRO - Mathematical formulation
================================

MACRO is a macroeconomic model maximizing the intertemporal utility function of a single representative producer-consumer
in each node (or macro-economic region). The optimization result is a sequence of optimal savings, investment, and consumption decisions.
The main variables of the model are the capital stock, available labor, and commodity inputs, which together determine the
total output of an economy according to a nested constant elasticity of substitution (CES) production function. End-use service
demands in the (commercial) demand categories of MESSAGE is determined within the model, and is consistent with commodity
supply curves, which are inputs to the model.


Notation declaration
~~~~~~~~~~~~~~~~~~~~
The following short notation is used in the mathematical description relative to the GAMS code:

============== =============================== ===================================================================
Math Notation  GAMS set & index notation       Description
============== =============================== ===================================================================
:math:`n`      node (or node_active in loops)  spatial node corresponding to the macro-economic MESSAGE regions
:math:`y`      year                            year (2005, 2010, 2020, ..., 2100)
:math:`s`      sector                          sector corresponding to the (commercial) end-use demands of MESSAGE
============== =============================== ===================================================================

A listing of all parameters used in MACRO together with a decription can be found in the table below.

=========================== ================================================================================================================================
Parameter                   Description
=========================== ================================================================================================================================
:math:`duration\_period_y`  Number of years in time period :math:`y` (forward diff)
:math:`total\_cost_{n,y}`   Total system costs in region :math:`n` and period :math:`y` from MESSAGE model run
:math:`enestart_{n,s,y}`    Consumption level of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`y` from MESSAGE model run
:math:`eneprice_{n,s,y}`    Shadow prices of (commercial) end-use services :math:`s` in region :math:`n` and period :math:`y` from MESSAGE model run
:math:`\epsilon_n`          Elasticity of substitution between capital-labor and total energy in region :math:`n`
:math:`\rho_n`              :math:`\epsilon - 1 / \epsilon` where :math:`\epsilon` is the elasticity of subsitution in region :math:`n`
:math:`depr_n`              Annual depreciation rate in region :math:`n`
:math:`\alpha_n`            Capital value share parameter in region :math:`n`
:math:`a_n`                 Production function coefficient of capital and labor in region :math:`n`
:math:`b_{n,s}`             Production function coefficients of the different end-use sectors in region :math:`n`, sector :math:`s` and period :math:`y`
:math:`udf_{n,y}`           Utility discount factor in period year in region :math:`n` and period :math:`y`
:math:`newlab_{n,y}`        New vintage of labor force in region :math:`n` and period :math:`y`
:math:`grow_{n,y}`          Annual growth rates of potential GDP in region :math:`n` and period :math:`y`
:math:`aeei_{n,s,y}`        Autonomous energy efficiency improvement (AEEI) in region :math:`n`, sector :math:`s` and period :math:`y`
:math:`fin\_time_{n,y}`     finite time horizon correction factor in utility function in region :math:`n` and period :math:`y`
=========================== ================================================================================================================================

Decision variables
~~~~~~~~~~~~~~~~~~~~

======================== ==================================================== ======================================================================================================
Variable                 Definition                                           Description
======================== ==================================================== ======================================================================================================
:math:`K_{n,y}`          :math:`{K}_{n, y}\geq 0 ~ \forall n, y`              Capital stock in region :math:`n` and period :math:`y`
:math:`KN_{n,y}`         :math:`{KN}_{n, y}\geq 0 ~ \forall n, y`             New Capital vintage in region :math:`n` and period :math:`y`
:math:`Y_{n,y}`          :math:`{Y}_{n, y}\geq 0 ~ \forall n, y`              Total production in region :math:`n` and period :math:`y`
:math:`YN_{n,y}`         :math:`{YN}_{n, y}\geq 0 ~ \forall n, y`             New production vintage in region :math:`n` and period :math:`y`
:math:`C_{n,y}`          :math:`{C}_{n, y}\geq 0 ~ \forall n, y`              Consumption in region :math:`n` and period :math:`y`
:math:`I_{n,y}`          :math:`{I}_{n, y}\geq 0 ~ \forall n, y`              Investment in region :math:`n` and period :math:`y`
:math:`PHYSENE_{n,s,y}`  :math:`{PHYSENE}_{n, s, y}\geq 0 ~ \forall n, s, y`  Physical end-use service use in region :math:`n`, sector :math:`s` and period :math:`y`
:math:`PRODENE_{n,s,y}`  :math:`{PRODENE}_{n, s, y}\geq 0 ~ \forall n, s, y`  Value of end-use service in the production function in region :math:`n`, sector :math:`s` and period :math:`y`
:math:`NEWENE_{n,s,y}`   :math:`{NEWENE}_{n, s, y}\geq 0 ~ \forall n, s, y`   New end-use service in the production function in region :math:`n`, sector :math:`s` and period :math:`y`
:math:`EC_{n,y}`         :math:`EC \in \left[-\infty..\infty\right]`          Approximation of system costs based on MESSAGE results
:math:`UTILITY`          :math:`UTILITY \in \left[-\infty..\infty\right]`     Utility function (discounted log of consumption)
======================== ==================================================== ======================================================================================================


Equation UTILITY_FUNCTION
---------------------------------
The utility function which is maximized sums up the discounted logarithm of consumption of a single representative producer-consumer over the entire time horizon
of the model.

.. math:: {UTILITY} = \sum_{n} \bigg( &  \sum_{y |  (  (  {ord}( y )   >  1 )  \wedge  (  {ord}( y )   <   | y |  )  )} {udf}_{n, y} \cdot {\log}( C_{n, y} ) \cdot {duration\_period}_{y} \\
                                + &\sum_{y |  (  {ord}( y ) =  | y | ) } {udf}_{n, y} \cdot {\log}( C_{n, y} ) \cdot \big( {duration\_period}_{y-1} + \frac{1}{{FIN\_TIME}_{n, y}} \big) \bigg)

The utility discount rate for period :math:`y` is set to :math:`drate_{n} - grow_{n,y}`, where :math:`drate_{n}` is the discount rate used in MESSAGE, typically set to 5%,
and :math:`grow` is the potential GDP growth rate. This choice ensures that in the steady state, the optimal growth rate is identical to the potential GDP growth rates :math:`grow`.
The values for the utility discount rates are chosen for descriptive rather than normative reasons. The term :math:`\frac{{duration\_period}_{y} + {duration\_period}_{y-1}}{2}` mutliples the
discounted logarithm of consumption with the period length. The final period is treated separately to include a correction factor :math:`\frac{1}{{FIN\_TIME}_{n, y}}` reflecting
the finite time horizon of the model. Note that the sum over nodes :math:`node\_active` is artificial, because :math:`node\_active` only contains one element.


Equation CAPITAL_CONSTRAINT
---------------------------------
The following equation specifies the allocation of total production among current consumption :math:`{C}_{n, y}`, investment into building up capital stock excluding
the sectors represented in MESSAGE :math:`{I}_{n, y}` and the MESSAGE system costs :math:`{EC}_{n, y}` which are derived from a previous MESSAGE model run. As described in :cite:`manne_buying_1992`, the first-order
optimality conditions lead to the Ramsey rule for the optimal allocation of savings, investment and consumption over time.

.. math:: Y_{n, y} = C_{n, y} + I_{r, y} + {EC}_{n, y} \qquad \forall{n, y}


Equation NEW_CAPITAL
---------------------------------
The accumulation of capital in the sectors not represented in MESSAGE is governed by new capital stock equation. Net capital formation :math:`{KN}_{n,y}` is derived from gross
investments :math:`{I}_{n,y}` minus depreciation of previsouly existing capital stock.

.. math:: {KN}_{n,y} = {duration\_period}_{y} \cdot I_{n,y} \qquad \forall{n, y > 1}

Here, the initial boundary condition for the base year :math:`y_0` implies for the investments that :math:`I_{n,y_0} = (grow_{n,y_0} + depr_{n}) \cdot kgdp_{n} \cdot gdp_{n,y_0}`.

Equation NEW_PRODUCTION
---------------------------------
MACRO employs a nested constant elasticity of substitution (CES) production function with capital, labor and the (commercial) end-use services
represented in MESSAGE as inputs. This version of the production function is equaivalent to that in MARKAL-MACRO.

.. math:: {YN}_{n,y} =  { \left( {a}_{n} \cdot {{KN}_{n, y}}^{ ( {\rho}_{n} \cdot {\alpha}_{n} ) } \cdot {{newlab}_{n, y}}^{ ( {\rho}_{n} \cdot ( 1 - {\alpha}_{n} ) ) } + \displaystyle \sum_{s} ( {b}_{n, s} \cdot {{NEWENE}_{n, s, y}}^{{\rho}_{n}} )  \right) }^{ \frac{1}{{\rho}_{n}} } \qquad \forall{ n, y > 1}


Equation TOTAL_CAPITAL
---------------------------------
Equivalent to the total production equation above, the total capital stock, again excluding those sectors which are modeled in MESSAGE, is then simply a summation
of capital stock in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`depr_{n}`, and the capital stock added in the current period :math:`y`.

.. math:: K_{n, y} = K_{n, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {KN}_{n, y} \qquad \forall{ n, y > 1}


Equation TOTAL_PRODUCTION
---------------------------------
Total production in the economy (excluding energy sectors) is the sum of production from  assets that were already existing in the previous period :math:`y-1`,
depreciated with the depreciation rate :math:`depr_{n}`, and the new vintage of production from period :math:`y`.

.. math:: Y_{n, y} = Y_{n, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {YN}_{n, y} \qquad \forall{ n, y > 1}


Equation NEW_ENERGY
---------------------------------
Total energy production (across the six commerical energy demands :math:`s`) is the sum of production from all assets that were already existing
in the previous period :math:`y-1`, depreciated with the depreciation rate :math:`depr_{n}`, and the the new vintage of energy production from
period :math:`y`.

.. math:: {PRODENE}_{n, s, y} = {PRODENE}_{n, s, y-1} \cdot { \left( 1 - {depr}_n \right) }^{duration\_period_{y}} + {NEWENE}_{n, s, y} \qquad \forall{ n, s, y > 1}


Equation ENERGY_SUPPLY
---------------------------------
The relationship below establishes the link between physical energy :math:`{PHYSENE}_{r, s, y}` as accounted in MESSAGE for the six commerical energy demands :math:`s` and
energy in terms of monetary value :math:`{PRODENE}_{n, s, y}` as specified in the production function of MACRO.

.. math:: {PHYSENE}_{n, s, y} \geq {PRODENE}_{n, s, y} \cdot {aeei\_factor}_{n, s, y} \qquad \forall{ n, s, y > 1}

The cumulative effect of autonomous energy efficiency improvements (AEEI) is captured in
:math:`{aeei\_factor}_{n,s,y} = {aeei\_factor}_{n, s, y-1} \cdot (1 - {aeei}_{n,s,y})^{duration\_period}_{y}`
with :math:`{aeei\_factor}_{n,s,y=1} = 1`. Therefore, choosing the :math:`{aeei}_{n,s,y}` coefficients appropriately offers the possibility to calibrate MACRO to a certain energy demand trajectory
from MESSAGE.


Equation COST_ENERGY
---------------------------------
Energy system costs are based on a previous MESSAGE model run. The approximation of energy system costs in vicinity of the MESSAGE solution are approximated by a Taylor expansion with the
first order term using shadow prices :math:`eneprice_{s, y, n}` of the MESSAGE model's solution and a quadratic second-order term.

.. math:: {EC}_{n, y} =  & {total\_cost}_{n, r} \\
                       + & \displaystyle \sum_{s} {eneprice}_{s, y, n} \cdot \left( {PHYSENE}_{n, s, y} - {enestart}_{s, y, n} \right) \\
                       + & \displaystyle \sum_{s} \frac{{eneprice}_{s, y, n}}{{enestart}_{s, y, n}} \cdot \left( {PHYSENE}_{n, s, y} - {enestart}_{s, y, n} \right)^2 \qquad \forall{ n, y > 1}


Equation TERMINAL_CONDITION
---------------------------------
Given the finite time horizon of MACRO, a terminal constraint needs to be applied to ensure that investments are chosen at an appropriate level, i.e. to replace depriciated capital and
provide net growth of capital stock beyond MACRO's time horizon :cite:`manne_buying_1992`. The goal is to avoid to the extend possible model artifacts resulting from this finite time horizon
cutoff.

.. math:: K_{n, y} \cdot  \left( grow_{n, y} + {depr}_n \right) \leq I_{n, y} \qquad \forall{ n, y = last year}

