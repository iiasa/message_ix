.. note:: This page is generated from inline documentation in ``MESSAGE\scaling_investment_costs.gms``.

Auxiliary investment parameters
===============================


Levelized capital costs
-----------------------
For the 'soft' relaxations of the dynamic constraints and the associated penalty factor in the objective function,
we need to compute the parameter :math:`levelized\_cost_{n,t,y}`.

.. math::
   levelized\_cost_{n,t,m,y,h} := \
       & inv\_cost_{n,t,y} \cdot \frac{ interestrate_{y} \cdot \left( 1 + interestrate_{y} \right)^{|y|} }
                                     { \left( 1 + interestrate_{y} \right)^{|y|} - 1 } \\
       & + fix\_cost_{n,t,y,y} \cdot \frac{ 1 }{ \sum_{h'} duration\_time_{h'} \cdot capacity\_factor_{n,t,y,y,h'} } \\
       & + var\_cost_{n,t,y,y,m,h}

where :math:`|y| = technical\_lifetime_{n,t,y}`. This formulation implicitly assumes constant fixed
and variable costs over time.

**Warning:** All soft relaxations of the dynamic activity constraint are
disabled if the levelized costs are negative!

Construction time accounting
----------------------------
If the construction of new capacity takes a significant amount of time,
investment costs have to be scaled up accordingly to account for the higher capital costs.

.. math::
   construction\_time\_factor_{n,t,y} = \left( 1 + interestrate_y \right)^{|y|}

where :math:`|y| = construction\_time_{n,t,y}`. If no construction time is specified, the default value of the
investment cost scaling factor defaults to 1. The model assumes that the construction time only plays a role
for the investment costs, i.e., each unit of new-built capacity is available instantaneously.

**Comment:** This formulation applies the discount rate of the vintage year
(i.e., the year in which the new capacity becomes operational).

Investment costs beyond the model horizon
-----------------------------------------
If the technical lifetime of a technology exceeds the model horizon :math:`Y^{model}`, the model has to add
a scaling factor to the investment costs (:math:`end\_of\_horizon\_factor_{n,t,y}`). Assuming a constant
stream of revenue (marginal value of the capacity constraint), this can be computed by annualizing investment costs
from the condition that in an optimal solution, the investment costs must equal the discounted future revenues,
if the investment variable :math:`CAP\_NEW_{n,t,y} > 0`:

.. math::
   inv\_cost_{n,t,y^V} = \sum_{y \in Y^{lifetime}_{n,t,y^V}} df\_year_{y} \cdot \beta_{n,t},

Here, :math:`\beta_{n,t} > 0` is the dual variable to the capacity constraint (assumed constant over future periods)
and :math:`Y^{lifetime}_{n,t,y^V}` is the set of periods in the lifetime of a plant built in period :math:`y^V`.
Then, the scaling factor :math:`end\_of\_horizon\_factor_{n,t,y^V}` can be derived as follows:

.. math::
   end\_of\_horizon\_factor_{n,t,y^V} :=
   \frac{\sum_{y \in Y^{lifetime}_{n,t,y^V} \cap Y^{model}} df\_year_{y} }
       {\sum_{y' \in Y^{lifetime}_{n,t,y^V}} df\_year_{y'} + beyond\_horizon\_factor_{n,t,y^V} }
   \in (0,1],

where the parameter :math:`beyond\_horizon\_factor_{n,t,y^V}` accounts for the discount factor beyond the
overall model horizon (the set :math:`Y` in contrast to the set :math:`Y^{model} \subseteq Y` of the periods
included in the current model iteration (see the page on the recursive-dynamic model solution approach).

.. math::
   beyond\_horizon\_lifetime_{n,t,y^V} :=  \max \Big\{ 0,
       economic\_lifetime_{n,t,y^V} - \sum_{y' \geq y^V} duration\_period_{y'} \Big\}

.. math::
   beyond\_horizon\_factor_{n,t,y^V} :=
       df\_year_{\widehat{y}} \cdot \frac{1}{ \left( 1 + interestrate_{\widehat{y}} \right)^{|\widehat{y}|} }
       \cdot \frac{ 1 - \left( \frac{1}{1 + interestrate_{\widehat{y}}} \right)^{|\widetilde{y}|}}
                  { 1 - \frac{1}{1 + interestrate_{\widehat{y}}}}

where :math:`\widehat{y}` is the last period included in the overall model horizon,
:math:`|\widehat{y}| = period\_duration\_period_{\widehat{y}}`
and :math:`|\widetilde{y}| = beyond\_horizon\_lifetime_{n,t,y^V}`.

If the interest rate is zero, i.e., :math:`interestrate_{\widehat{y}} = 0`,
the parameter :math:`beyond\_horizon\_factor_{n,t,y^V}` equals the remaining technical lifetime
beyond the model horizon and the parameter :math:`end\_of\_horizon\_factor_{n,t,y^V}` equals
the share of technical lifetime within the model horizon.

**Possible extension:** Instead of assuming :math:`\beta_{n,t}` to be constant over time, one could include
a simple (linear) projection of :math:`\beta_{n,t,y}` beyond the end of the model horizon. However, this would likely
require to include the computation of dual variables endogenously, and thus a mixed-complementarity formulation of
the model.

Remaining installed capacity
----------------------------
The model has to take into account that the technical lifetime of a technology may not coincide with the cumulative
period duration. Therefore, the model introduces the parameter :math:`remaining\_capacity_{n,t,y^V,y}`
as a factor of remaining technical lifetime in the last period of operation divided by the duration of that period.


