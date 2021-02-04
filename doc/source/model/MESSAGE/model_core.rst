.. note:: This page is generated from inline documentation in ``MESSAGE\model_core.gms``.

Mathematical formulation (core model)
=====================================

The |MESSAGEix| systems-optimization model minimizes total costs
while satisfying given demand levels for commodities/services
and considering a broad range of technical/engineering constraints and societal restrictions
(e.g. bounds on greenhouse gas emissions, pollutants, system reliability).
Demand levels are static (i.e. non-elastic), but the demand response can be integrated by linking |MESSAGEix|
to the single sector general-economy MACRO model included in this framework.

For the complete list of sets, mappings and parameters,
refer to the auto-documentation pages :ref:`sets_maps_def` and :ref:`parameter_def`.

Notation declaration
--------------------
The following short notation is used in the mathematical description relative to the GAMS code:

Mathematical notation of sets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
================================== ===================================================================================
Math notation                      GAMS set & index notation
================================== ===================================================================================
:math:`n \in N`                    node (across spatial hierarchy levels)
:math:`y \in Y`                    year (all periods including historical and model horizon)
:math:`y \in Y^M \subset Y`        time periods included in model horizon
:math:`y \in Y^H \subset Y`        historical time periods (prior to first model period)
:math:`c \in C`                    commodity
:math:`l \in L`                    level
:math:`g \in G`                    grade
:math:`t \in T`                    technology (a.k.a tec)
:math:`h \in H`                    time (subannual time periods)
:math:`m \in M`                    mode
:math:`q \in Q`                    rating of non-dispatchable technologies relative to aggregate commodity use
:math:`e \in E`                    emission, pollutants
:math:`s \in S`                    scenarios of land use (for land-use model emulator)
:math:`u \in U`                    land-use types
:math:`r \in R`                    set of generic relations (linear constraints)
:math:`t \in T^{INV} \subseteq T`  all technologies with investment decisions and capacity constraints
:math:`t \in T^{REN} \subseteq T`  all technologies which draw their input from the renewable level
:math:`n \in N(\widehat{n})`       all nodes that are subnodes of node :math:`\widehat{n}`
:math:`y \in Y(\widehat{y})`       all years mapped to the category ``type_year`` :math:`\widehat{y}`
:math:`t \in T(\widehat{t})`       all technologies mapped to the category ``type_tec`` :math:`\widehat{t}`
:math:`e \in E(\widehat{e})`       all emissions mapped to the category ``type_emission`` :math:`\widehat{e}`
================================== ===================================================================================


Decision variables
^^^^^^^^^^^^^^^^^^
============================================= ========================================================================
Variable                                      Explanatory text
============================================= ========================================================================
:math:`OBJ \in \mathbb{R}`                    Objective value of the optimization program
:math:`EXT_{n,c,g,y} \in \mathbb{R}_+`        Extraction of non-renewable/exhaustible resources from reserves
:math:`STOCK_{n,c,l,y} \in \mathbb{R}_+`      Quantity in stock (storage) at start of period :math:`y`
:math:`STOCK\_CHG_{n,c,l,y,h} \in \mathbb{R}` Input or output quantity into intertemporal commodity stock (storage)
:math:`REN_{n,t,c,g,y,h}`                     Activity of renewable technologies per grade
:math:`CAP\_NEW_{n,t,y} \in \mathbb{R}_+`     Newly installed capacity (yearly average over period duration)
:math:`CAP_{n,t,y^V,y} \in \mathbb{R}_+`      Maintained capacity in year :math:`y` of vintage :math:`y^V`
:math:`CAP\_FIRM_{n,t,c,l,y,q}`               Capacity counting towards firm (dispatchable)
:math:`ACT_{n,t,y^V,y,m,h} \in \mathbb{R}`    Activity of a technology (by vintage, mode, subannual time)
:math:`ACT\_RATING_{n,t,y^V,y,c,l,h,q}`       Activity attributed to a particular rating bin [#ACT_RATING]_
:math:`CAP\_NEW\_UP_{n,t,y} \in \mathbb{R}_+` Relaxation of upper dynamic constraint on new capacity
:math:`CAP\_NEW\_LO_{n,t,y} \in \mathbb{R}_+` Relaxation of lower dynamic constraint on new capacity
:math:`ACT\_UP_{n,t,y,h} \in \mathbb{R}_+`    Relaxation of upper dynamic constraint on activity [#ACT_BD]_
:math:`ACT\_LO_{n,t,y,h} \in \mathbb{R}_+`    Relaxation of lower dynamic constraint on activity [#ACT_BD]_
:math:`LAND_{n,s,y} \in [0,1]`                Relative share of land-use scenario (for land-use model emulator)
:math:`EMISS_{n,e,\widehat{t},y}`             Auxiliary variable for aggregate emissions by technology type
:math:`REL_{r,n,y} \in \mathbb{R}`            Auxiliary variable for left-hand side of relations (linear constraints)
:math:`COMMODITY\_USE_{n,c,l,y}`              Auxiliary variable for amount of commodity used at specific level
============================================= ========================================================================

The index :math:`y^V` is the year of construction (vintage) wherever it is necessary to
clearly distinguish between year of construction and the year of operation.

All decision variables are by year, not by (multi-year) period, except :math:`STOCK_{n,c,l,y}`.
In particular, the new capacity variable :math:`CAP\_NEW_{n,t,y}` has to be multiplied by the number of years
in a period :math:`|y| = duration\_period_{y}` to determine the available capacity in subsequent periods.
This formulation gives more flexibility when it comes to using periods of different duration
(more intuitive comparison across different periods).

The current model framework allows both input or output normalized formulation.
This will affect the parametrization, see Section :ref:`efficiency_output` for more details.

.. [#ACT_RATING] The auxiliary variable :math:`ACT\_RATING_{n,t,y^V,y,c,l,h,q}` is defined in terms of input or
   output of the technology.

.. [#ACT_BD] The dynamic activity constraints are implemented as summed over all modes;
   therefore, the variables for the relaxation are not indexed over the set ``mode``.


Auxiliary variables
^^^^^^^^^^^^^^^^^^^
============================================= ========================================================================
Variable                                      Explanatory text
============================================= ========================================================================
:math:`DEMAND_{n,c,l,y,h} \in \mathbb{R}`     Demand level (in equilibrium with MACRO integration)
:math:`PRICE\_COMMODITY_{n,c,l,y,h}`          Commodity price (undiscounted marginals of the commodity balances)
:math:`PRICE\_EMISSION_{n,e,\widehat{t},y}`   Emission price (undiscounted marginals of EMISSION_BOUND constraint)
:math:`COST\_NODAL\_NET_{n,y} \in \mathbb{R}` System costs at the node level net of energy trade revenues/cost
:math:`GDP_{n,y} \in \mathbb{R}`              gross domestic product (GDP) in market exchange rates for MACRO reporting
============================================= ========================================================================


Objective function
------------------

The objective function of the |MESSAGEix| core model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation OBJECTIVE
""""""""""""""""""

The objective function (of the core model) minimizes total discounted systems costs including costs for emissions,
relaxations of dynamic constraints

.. math::
   OBJ = \sum_{n,y \in Y^{M}} df\_year_{y} \cdot COST\_NODAL_{n,y}


Regional system cost accounting function
----------------------------------------

Accounting of regional system costs over time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation COST_ACCOUNTING_NODAL
""""""""""""""""""""""""""""""

Accounting of regional systems costs over time as well as costs for emissions (taxes),
land use (from the model land-use model emulator), relaxations of dynamic constraints,
and linear relations.

.. math::
   COST\_NODAL_{n,y} & = \sum_{c,g} \ resource\_cost_{n,c,g,y} \cdot EXT_{n,c,g,y} \\
     & + \sum_{t} \
         \bigg( inv\_cost_{n,t,y} \cdot construction\_time\_factor_{n,t,y} \\
     & \quad \quad \quad \cdot end\_of\_horizon\_factor_{n,t,y} \cdot CAP\_NEW_{n,t,y} \\[4 pt]
     & \quad \quad + \sum_{y^V \leq y} \ fix\_cost_{n,t,y^V,y} \cdot CAP_{n,t,y^V,y} \\
     & \quad \quad + \sum_{\substack{y^V \leq y \\ m,h}} \ var\_cost_{n,t,y^V,y,m,h} \cdot ACT_{n,t,y^V,y,m,h} \\
     & \quad \quad + \Big( abs\_cost\_new\_capacity\_soft\_up_{n,t,y} \\
     & \quad \quad \quad
         + level\_cost\_new\_capacity\_soft\_up_{n,t,y} \cdot\ inv\_cost_{n,t,y}
         \Big) \cdot CAP\_NEW\_UP_{n,t,y} \\[4pt]
     & \quad \quad + \Big( abs\_cost\_new\_capacity\_soft\_lo_{n,t,y} \\
     & \quad \quad \quad
         + level\_cost\_new\_capacity\_soft\_lo_{n,t,y} \cdot\ inv\_cost_{n,t,y}
         \Big) \cdot CAP\_NEW\_LO_{n,t,y} \\[4pt]
     & \quad \quad + \sum_{m,h} \ \Big( abs\_cost\_activity\_soft\_up_{n,t,y,m,h} \\
     & \quad \quad \quad
         + level\_cost\_activity\_soft\_up_{n,t,y,m,h} \cdot\ levelized\_cost_{n,t,y,m,h}
         \Big) \cdot ACT\_UP_{n,t,y,h} \\
     & \quad \quad + \sum_{m,h} \ \Big( abs\_cost\_activity\_soft\_lo_{n,t,y,m,h} \\
     & \quad \quad \quad
         + level\_cost\_activity\_soft\_lo_{n,t,y,m,h} \cdot\ levelized\_cost_{n,t,y,m,h}
         \Big) \cdot ACT\_LO_{n,t,y,h} \bigg) \\
     & + \sum_{\substack{\widehat{e},\widehat{t} \\ e \in E(\widehat{e})}}
           emission\_scaling_{\widehat{e},e} \cdot \ emission\_tax_{n,\widehat{e},\widehat{t},y}
           \cdot EMISS_{n,e,\widehat{t},y} \\
     & + \sum_{s} land\_cost_{n,s,y} \cdot LAND_{n,s,y} \\
     & + \sum_{r} relation\_cost_{r,n,y} \cdot REL_{r,n,y}

Here, :math:`n^L \in N(n)` are all nodes :math:`n^L` that are sub-nodes of node :math:`n`.
The subset of technologies :math:`t \in T(\widehat{t})` are all tecs that belong to category :math:`\widehat{t}`,
and similar notation is used for emissions :math:`e \in E`.

Resource and commodity section
------------------------------

Constraints on resource extraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation EXTRACTION_EQUIVALENCE
"""""""""""""""""""""""""""""""

This constraint translates the quantity of resources extracted (summed over all grades) to the input used by
all technologies (drawing from that node). It is introduced to simplify subsequent notation in input/output relations
and nodal balance constraints.

 .. math::
    \sum_{g} EXT_{n,c,g,y} =
    \sum_{\substack{n^L,t,m,h,h^{OD} \\ y^V \leq y  \\ \ l \in L^{RES} \subseteq L }}
        input_{n^L,t,y^V,y,m,n,c,l,h,h^{OD}} \cdot ACT_{n^L,t,m,y,h}

The set :math:`L^{RES} \subseteq L` denotes all levels for which the detailed representation of resources applies.

Equation EXTRACTION_BOUND_UP
""""""""""""""""""""""""""""

This constraint specifies an upper bound on resource extraction by grade.

 .. math::
    EXT_{n,c,g,y} \leq bound\_extraction\_up_{n,c,g,y}


Equation RESOURCE_CONSTRAINT
""""""""""""""""""""""""""""

This constraint restricts that resource extraction in a year guarantees the "remaining resources" constraint,
i.e., only a given fraction of remaining resources can be extracted per year.

 .. math::
    EXT_{n,c,g,y} \leq
    resource\_remaining_{n,c,g,y} \cdot
        \Big( & resource\_volume_{n,c,g} \\
              & - \sum_{y' < y} duration\_period_{y'} \cdot EXT_{n,c,g,y'} \Big)


Equation RESOURCE_HORIZON
"""""""""""""""""""""""""
This constraint ensures that total resource extraction over the model horizon does not exceed the available resources.

 .. math::
    \sum_{y} duration\_period_{y} \cdot EXT_{n,c,g,y} \leq  resource\_volume_{n,c,g}


Constraints on commodities and stocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Auxiliary COMMODITY_BALANCE
"""""""""""""""""""""""""""
For the commodity balance constraints below, we introduce an auxiliary `COMMODITY_BALANCE`. This is implemented
as a GAMS `$macro` function.

 .. math::
    \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} output_{n^L,t,y^V,y,m,n,c,l,h^A,h}
        \cdot duration\_time\_rel_{h,h^A} \cdot & ACT_{n^L,t,y^V,y,m,h^A} \\
    - \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} input_{n^L,t,y^V,y,m,n,c,l,h^A,h}
        \cdot duration\_time\_rel_{h,h^A} \cdot & ACT_{n^L,t,m,y,h^A} \\
    + \ STOCK\_CHG_{n,c,l,y,h} & \\[4pt]
    + \ \sum_s \Big( land\_output_{n,s,y,c,l,h} - land\_input_{n,s,y,c,l,h} \Big) \cdot & LAND_{n,s,y} \\[4pt]
    - \ demand\_fixed_{n,c,l,y,h}
    & = COMMODITY\_BALANCE{n,c,l,y,h} \quad \forall \ l \notin (L^{RES}, l^{REN} \subseteq L

The commodity balance constraint at the resource level is included in the `Equation RESOURCE_CONSTRAINT`_,
while at the renewable level, it is included in the `Equation RENEWABLES_EQUIVALENCE`_.

Equation COMMODITY_BALANCE_GT
"""""""""""""""""""""""""""""
This constraint ensures that supply is greater or equal than demand for every commodity-level combination.

 .. math::
    COMMODITY\_BALANCE_{n,c,l,y,h} \geq 0


Equation COMMODITY_BALANCE_LT
"""""""""""""""""""""""""""""
This constraint ensures the supply is smaller than or equal to the demand for all commodity-level combinatio
given in the :math:`balance\_equality_{c,l}`. In combination withe constraint above, it ensures that supply
is (exactly) equal to demand.

 .. math::
    COMMODITY\_BALANCE_{n,c,l,y,h} \leq 0


Equation STOCKS_BALANCE
"""""""""""""""""""""""
This constraint ensures the inter-temporal balance of commodity stocks.
The parameter :math:`commodity\_stocks_{n,c,l}` can be used to model exogenous additions to the stock

 .. math::
    STOCK_{n,c,l,y} + commodity\_stock_{n,c,l,y} =
        duration\_period_{y} \cdot & \sum_{h} STOCK\_CHG_{n,c,l,y,h} \\
                                   & + STOCK_{n,c,l,y+1}


Technology section
------------------

Technical and engineering constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The first set of constraints concern technologies that have explicit investment decisions
and where installed/maintained capacity is relevant for operational decisions.
The set where :math:`T^{INV} \subseteq T` is the set of all these technologies.


Equation CAPACITY_CONSTRAINT
""""""""""""""""""""""""""""
This constraint ensures that the actual activity of a technology at a node cannot exceed available (maintained)
capacity summed over all vintages, including the technology capacity factor :math:`capacity\_factor_{n,t,y,t}`.

 .. math::
    \sum_{m} ACT_{n,t,y^V,y,m,h}
        \leq duration\_time_{h} \cdot capacity\_factor_{n,t,y^V,y,h} \cdot CAP_{n,t,y^V,y}
        \quad \forall \ t \ \in \ T^{INV}


Equation CAPACITY_MAINTENANCE_HIST
""""""""""""""""""""""""""""""""""
The following three constraints implement technology capacity maintenance over time to allow early retirment.
The optimization problem determines the optimal timing of retirement, when fixed operation-and-maintenance costs
exceed the benefit in the objective function.

The first constraint ensures that historical capacity (built prior to the model horizon) is available
as installed capacity in the first model period.

  .. math::
     CAP_{n,t,y^V,'first\_period'} & \leq
         remaining\_capacity_{n,t,y^V,'first\_period'} \cdot
         duration\_period_{y^V} \cdot
         historical\_new\_capacity_{n,t,y^V} \\
     & \text{if } y^V  < 'first\_period' \text{ and } |y| - |y^V| < technical\_lifetime_{n,t,y^V}
     \quad \forall \ t \in T^{INV}


Equation CAPACITY_MAINTENANCE_NEW
"""""""""""""""""""""""""""""""""
The second constraint ensures that capacity is fully maintained throughout the model period
in which it was constructed (no early retirement in the period of construction).

  .. math::
     CAP_{n,t,y^V,y^V} =
         remaining\_capacity_{n,t,y^V,y^V} \cdot
         duration\_period_{y^V} \cdot
         CAP\_NEW{n,t,y^V}
     \quad \forall \ t \in T^{INV}

The current formulation does not account for construction time in the constraints, but only adds a mark-up
to the investment costs in the objective function.

Equation CAPACITY_MAINTENANCE
"""""""""""""""""""""""""""""
The third constraint implements the dynamics of capacity maintenance throughout the model horizon.
Installed capacity can be maintained over time until decommissioning, which is irreversible.

  .. math::
     CAP_{n,t,y^V,y} & \leq
         remaining\_capacity_{n,t,y^V,y} \cdot
         CAP_{n,t,y^V,y-1} \\
     \quad & \text{if } y > y^V \text{ and } y^V  > 'first\_period' \text{ and } |y| - |y^V| < technical\_lifetime_{n,t,y^V}
     \quad \forall \ t \in T^{INV}


Equation OPERATION_CONSTRAINT
"""""""""""""""""""""""""""""
This constraint provides an upper bound on the total operation of installed capacity over a year.
It can be used to represent reuqired scheduled unavailability of installed capacity.

  .. math::
     \sum_{m,h} ACT_{n,t,y^V,y,m,h}
         \leq operation\_factor_{n,t,y^V,y} \cdot capacity\_factor_{n,t,y^V,y,m,\text{'year'}} \cdot CAP_{n,t,y^V,y}
     \quad \forall \ t \in T^{INV}

This constraint is only active if :math:`operation\_factor_{n,t,y^V,y} < 1`.

Equation MIN_UTILIZATION_CONSTRAINT
"""""""""""""""""""""""""""""""""""
This constraint provides a lower bound on the total utilization of installed capacity over a year.

  .. math::
     \sum_{m,h} ACT_{n,t,y^V,y,m,h} \geq min\_utilization\_factor_{n,t,y^V,y} \cdot CAP_{n,t,y^V,y}
     \quad \forall \ t \in T^{INV}

This constraint is only active if :math:`min\_utilization\_factor_{n,t,y^V,y}` is defined.

Constraints representing renewable integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation RENEWABLES_EQUIVALENCE
"""""""""""""""""""""""""""""""
This constraint defines the auxiliary variables :math:`REN`
to be equal to the output of renewable technologies (summed over grades).

 .. math::
    \sum_{g} REN_{n,t,c,g,y,h} \leq
    \sum_{\substack{n,t,m,l,h,h^{OD} \\ y^V \leq y  \\ \ l \in L^{REN} \subseteq L }}
        input_{n^L,t,y^V,y,m,n,c,l,h,h^{OD}} \cdot ACT_{n^L,t,m,y,h}

The set :math:`L^{REN} \subseteq L` denotes all levels for which the detailed representation of renewables applies.

Equation RENEWABLES_POTENTIAL_CONSTRAINT
""""""""""""""""""""""""""""""""""""""""
This constraint sets the potential potential by grade as the upper bound for the auxiliary variable :math:`REN`.

 .. math::
    \sum_{\substack{t,h \\ \ t \in T^{R} \subseteq t }} REN_{n,t,c,g,y,h}
        \leq \sum_{\substack{l \\ l \in L^{R} \subseteq L }} renewable\_potential_{n,c,g,l,y}


Equation RENEWABLES_CAPACITY_REQUIREMENT
""""""""""""""""""""""""""""""""""""""""
This constraint connects the capacity factor of a renewable grade to the
installed capacity of a technology. It sets the lower limit for the capacity
of a renewable technology to the summed activity over all grades (REN) devided
by the capactiy factor of this grade.
It represents the fact that different renewable grades require different installed
capacities to provide their full potential.

 .. math::
    \sum_{y^V, h} & CAP_{n,t,y^V,y} \cdot operation\_factor_{n,t,y^V,y} \cdot capacity\_factor_{n,t,y^V,y,h} \\
       & \quad \geq \sum_{g,h,l} \frac{1}{renewable\_capacity\_factor_{n,c,g,l,y}} \cdot REN_{n,t,c,g,y,h}

This constraint is only active if :math:`renewable\_capacity\_factor_{n,c,g,l,y}` is defined.

Constraints for addon technologies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation ADDON_ACTIVITY_UP
""""""""""""""""""""""""""
This constraint provides an upper bound on the activity of an addon technology that can only be operated
jointly with a parent technology (e.g., abatement option, SO2 scrubber, power plant cooling technology).

  .. math::
     \sum_{\substack{t' \sim t^A, y^V \leq y}} ACT_{n,t',y^V,y,m,h}
     \leq
     \sum_{\substack{t, y^V \leq y}}
         addon\_up_{n,t^a,y,m,h,t^A} \cdot
         addon\_conversion_{n,t',y^V,y,m,h} \cdot
         ACT_{n,t,y^V,y,m,h}


Equation ADDON_ACTIVITY_LO
""""""""""""""""""""""""""
This constraint provides a lower bound on the activity of an addon technology that has to be operated
jointly with a parent technology (e.g., power plant cooling technology). The parameter `addon_lo` allows to define
a minimum level of operation of addon technologies relative to the activity of the parent technology.
If `addon_minimum = 1`, this means that it is mandatory to operate the addon technology at the same level as the
parent technology (i.e., full mitigation).

  .. math::
     \sum_{\substack{t' \sim t^A, y^V \leq y}} ACT_{n,t',y^V,y,m,h}
     \geq
     \sum_{\substack{t, y^V \leq y}}
         addon\_lo_{n,t^a,y,m,h,t^A} \cdot
         addon\_conversion_{n,t',y^V,y,m,h} \cdot
         ACT_{n,t,y^V,y,m,h}


System reliability and flexibility requirements
-----------------------------------------------
This section followi allows to include system-wide reliability and flexility considerations.
The current formulation is based on Sullivan et al., 2013 :cite:`sullivan_VRE_2013`.

Aggregate use of a commodity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The system reliability and flexibility constraints are implemented using an auxiliary variable representing
the total use (i.e., input of each commodity per level).

Equation COMMODITY_USE_LEVEL
""""""""""""""""""""""""""""
This constraint defines the auxiliary variable :math:`COMMODITY\_USE_{n,c,l,y}`, which is used to define
the rating bins and the peak-load that needs to be offset with firm (dispatchable) capacity.

  .. math::
     COMMODITY\_USE_{n,c,l,y}
     = & \sum_{n^L,t,y^V,m,h} input_{n^L,t,y^V,y,m,n,c,l,h,h} \\
       & \quad    \cdot duration\_time\_rel_{h,h} \cdot ACT_{n^L,t,y^V,y,m,h}

This constraint and the auxiliary variable is only active if :math:`peak\_load\_factor_{n,c,l,y,h}` or
:math:`flexibility\_factor_{n,t,y^V,y,m,c,l,h,r}` is defined.

.. _rating_bin:

Auxilary variables for technology activity by "rating bins"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The capacity and activity of certain (usually non-dispatchable) technologies
can be assumed to only partially contribute to the system reliability and flexibility requirements.

Equation ACTIVITY_RATING_BIN
""""""""""""""""""""""""""""
The auxiliary variable for rating-specific activity of each technology cannot exceed
the share of the rating bin in relation to the total commodity use.

.. math::
   ACT\_RATING_{n,t,y^V,y,c,l,h,q}
   \leq rating\_bin_{n,t,y,c,l,h,q} \cdot COMMODITY\_USE_{n,c,l,y}


Equation ACTIVITY_SHARE_TOTAL
"""""""""""""""""""""""""""""
The sum of the auxiliary rating-specific activity variables need to equal the total input and/or output
of the technology.

.. math::
   \sum_q ACT\_RATING_{n,t,y^V,y,c,l,h,q}
   = \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
        ( input_{n^L,t,y^V,y,m,n,c,l,h^A,h} + output_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad    \cdot duration\_time\_rel_{h,h^A} \cdot ACT_{n^L,t,y^V,y,m,h^A} \\


.. _reliability_constraint:

Reliability of installed capacity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The "firm capacity" that a technology can contribute to system reliability depends on its dispatch characteristics.
For dispatchable technologies, the total installed capacity counts toward the firm capacity constraint.
This is active if the parameter is defined over :math:`reliability\_factor_{n,t,y,c,l,h,'firm'}`.
For non-dispatchable technologies, or those that do not have explicit investment decisions,
the contribution to system reliability is calculated
by using the auxiliary variable :math:`ACT\_RATING_{n,t,y^V,y,c,l,h,q}` as a proxy,
with the :math:`reliability\_factor_{n,t,y,c,l,h,q}` defined per rating bin :math:`q`.

Equation FIRM_CAPACITY_PROVISION
""""""""""""""""""""""""""""""""
Technologies where the reliability factor is defined with the rating `firm`
have an auxiliary variable :math:`CAP\_FIRM_{n,t,c,l,y,q}`, defined in terms of output.

  .. math::
     \sum_q CAP\_FIRM_{n,t,c,l,y,q}
     = \sum_{y^V \leq y} & output_{n^L,t,y^V,y,m,n,c,l,h^A,h} \cdot duration\_time_h \\
       & \quad    \cdot capacity\_factor_{n,t,y^V,y,h} \cdot CAP_{n,t,y^Y,y}
     \quad \forall \ t \in T^{INV}


Equation SYSTEM_RELIABILITY_CONSTRAINT
""""""""""""""""""""""""""""""""""""""
This constraint ensures that there is sufficient firm (dispatchable) capacity in each period.
The formulation is based on Sullivan et al., 2013 :cite:`sullivan_VRE_2013`.

  .. math::
     \sum_{t, q \substack{t \in T^{INV} \\ y^V \leq y} } &
         reliability\_factor_{n,t,y,c,l,h,'firm'}
         \cdot CAP\_FIRM_{n,t,c,l,y} \\
     + \sum_{t,q,y^V \leq y} &
         reliability\_factor_{n,t,y,c,l,h,q}
        \cdot ACT\_RATING_{n,t,y^V,y,c,l,h,q} \\
        & \quad \geq peak\_load\_factor_{n,c,l,y,h} \cdot COMMODITY\_USE_{n,c,l,y}

This constraint is only active if :math:`peak\_load\_factor_{n,c,l,y,h}` is defined.

.. _flexibility_constraint:

Equation SYSTEM_FLEXIBILITY_CONSTRAINT
""""""""""""""""""""""""""""""""""""""
This constraint ensures that, in each sub-annual time slice, there is a sufficient
contribution from flexible technologies to ensure smooth system operation.

  .. math::
     \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
         flexibility\_factor_{n^L,t,y^V,y,m,c,l,h,'unrated'} \\
     & \quad   \cdot ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad   \cdot duration\_time\_rel_{h,h^A}
               \cdot ACT_{n,t,y^V,y,m,h} \\
     + \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y}} &
        flexibility\_factor_{n^L,t,y^V,y,m,c,l,h,1} \\
     & \quad   \cdot ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad   \cdot duration\_time\_rel_{h,h^A}
               \cdot ACT\_RATING_{n,t,y^V,y,c,l,h,q}
     \geq 0


Bounds on capacity and activity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation NEW_CAPACITY_BOUND_UP
""""""""""""""""""""""""""""""
This constraint provides upper bounds on new capacity installation.

  .. math::
     CAP\_NEW_{n,t,y} \leq bound\_new\_capacity\_up_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


Equation NEW_CAPACITY_BOUND_LO
""""""""""""""""""""""""""""""
This constraint provides lower bounds on new capacity installation.

  .. math::
     CAP\_NEW_{n,t,y} \geq bound\_new\_capacity\_lo_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


Equation TOTAL_CAPACITY_BOUND_UP
""""""""""""""""""""""""""""""""
This constraint gives upper bounds on the total installed capacity of a technology in a specific year of operation
summed over all vintages.

  .. math::
     \sum_{y^V \leq y} CAP_{n,t,y,y^V} \leq bound\_total\_capacity\_up_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


Equation TOTAL_CAPACITY_BOUND_LO
""""""""""""""""""""""""""""""""
This constraint gives lower bounds on the total installed capacity of a technology.

  .. math::
     \sum_{y^V \leq y} CAP_{n,t,y,y^V} \geq bound\_total\_capacity\_lo_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


.. _activity_bound_up:

Equation ACTIVITY_BOUND_UP
""""""""""""""""""""""""""
This constraint provides upper bounds by mode of a technology activity, summed over all vintages.

  .. math::
     \sum_{y^V \leq y} ACT_{n,t,y^V,y,m,h} \leq bound\_activity\_up_{n,t,m,y,h}


Equation ACTIVITY_BOUND_ALL_MODES_UP
""""""""""""""""""""""""""""""""""""
This constraint provides upper bounds of a technology activity across all modes and vintages.

  .. math::
     \sum_{y^V \leq y, m} ACT_{n,t,y^V,y,m,h} \leq bound\_activity\_up_{n,t,y,'all',h}


.. _acitvity_bound_lo:

Equation ACTIVITY_BOUND_LO
""""""""""""""""""""""""""
This constraint provides lower bounds by mode of a technology activity, summed over
all vintages.

  .. math::
     \sum_{y^V \leq y} ACT_{n,t,y^V,y,m,h} \geq bound\_activity\_lo_{n,t,y,m,h}

We assume that :math:`bound\_activity\_lo_{n,t,y,m,h} = 0`
unless explicitly stated otherwise.

Equation ACTIVITY_BOUND_ALL_MODES_LO
""""""""""""""""""""""""""""""""""""
This constraint provides lower bounds of a technology activity across all modes and vintages.

  .. math::
     \sum_{y^V \leq y, m} ACT_{n,t,y^V,y,m,h} \geq bound\_activity\_lo_{n,t,y,'all',h}

We assume that :math:`bound\_activity\_lo_{n,t,y,'all',h} = 0`
unless explicitly stated otherwise.

.. _share_constraints:

Constraints on shares of technologies and commodities
-----------------------------------------------------
This section allows to include upper and lower bounds on the shares of modes used by a technology
or the shares of commodities produced or consumed by groups of technologies.

Share constraints on activity by mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Equation SHARES_MODE_UP
"""""""""""""""""""""""
This constraint provides upper bounds of the share of the activity of one mode
of a technology. For example, it could limit the share of heat that can be produced
in a combined heat and electricity power plant.

  .. math::
    ACT_{n^L,t,y^V,y,m,h^A}
    \leq share\_mode\_up_{s,n,y,m,h} \cdot
    \sum_{m\prime} ACT_{n^L,t,y^V,y,m\prime,h^A}


Equation SHARES_MODE_LO
"""""""""""""""""""""""
This constraint provides lower bounds of the share of the activity of one mode of a technology.

  .. math::
    ACT_{n^L,t,y^V,y,m,h^A}
    \geq share\_mode\_lo_{s,n,y,m,h} \cdot
    \sum_{m\prime} ACT_{n^L,t,y^V,y,m\prime,h^A}


Share constraints on commodities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
These constraints allow to set upper and lower bound on the quantity of commodities produced or consumed by a group
of technologies relative to the commodities produced or consumed by another group.

The implementation is generic and flexible, so that any combination of commodities, levels, technologies and nodes
can be put in relation to any other combination.

The notation :math:`S^{share}` represents the mapping set `map_shares_commodity_share` denoting all technology types,
nodes, commodities and levels to be included in the numerator, and :math:`S^{total}` is
the equivalent mapping set `map_shares_commodity_total` for the denominator.

Equation SHARE_CONSTRAINT_COMMODITY_UP
""""""""""""""""""""""""""""""""""""""
  .. math::
     & \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim S^{share}}}
        ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad \cdot duration\_time\_rel_{h,h^A} \cdot ACT_{n^L,t,y^V,y,m,h^A} \\
     & \geq
       share\_commodity\_up_{s,n,y,h} \cdot
       \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim S^{total}}}
           ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad \cdot duration\_time\_rel_{h,h^A} \cdot ACT_{n^L,t,y^V,y,m,h^A}

This constraint is only active if :math:`share\_commodity\_up_{s,n,y,h}` is defined.

Equation SHARE_CONSTRAINT_COMMODITY_LO
""""""""""""""""""""""""""""""""""""""
  .. math::
     & \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim S^{share}}}
        ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad \cdot duration\_time\_rel_{h,h^A} \cdot ACT_{n^L,t,y^V,y,m,h^A} \\
     & \leq
       share\_commodity\_lo_{s,n,y,h} \cdot
       \sum_{\substack{n^L,t,m,h^A \\ y^V \leq y, (n,\widehat{t},m,c,l) \sim S^{total}}}
           ( output_{n^L,t,y^V,y,m,n,c,l,h^A,h} + input_{n^L,t,y^V,y,m,n,c,l,h^A,h} ) \\
     & \quad \cdot duration\_time\_rel_{h,h^A} \cdot ACT_{n^L,t,y^V,y,m,h^A}

This constraint is only active if :math:`share\_commodity\_lo_{s,n,y,h}` is defined.

.. _dynamic_constraints:

Dynamic constraints on market penetration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The constraints in this section specify dynamic upper and lower bounds on new capacity and activity,
i.e., constraints on market penetration and rate of expansion or phase-out of a technology.

The formulation directly includes the option for 'soft' relaxations of dynamic constraints
(cf. Keppo and Strubegger, 2010 :cite:`keppo_short_2010`).

Equation NEW_CAPACITY_CONSTRAINT_UP
"""""""""""""""""""""""""""""""""""
The level of new capacity additions cannot be greater than an initial value (compounded over the period duration),
annual growth of the existing 'capital stock', and a "soft" relaxation of the upper bound.

 .. math::
    CAP\_NEW_{n,t,y}
        \leq & ~ initial\_new\_capacity\_up_{n,t,y}
            \cdot \frac{ \Big( 1 + growth\_new\_capacity\_up_{n,t,y} \Big)^{|y|} - 1 }
                       { growth\_new\_capacity\_up_{n,t,y} } \\
             & + \Big( CAP\_NEW_{n,t,y-1} + historical\_new\_capacity_{n,t,y-1} \Big) \\
             & \hspace{2 cm} \cdot \Big( 1 + growth\_new\_capacity\_up_{n,t,y} \Big)^{|y|} \\
             & + CAP\_NEW\_UP_{n,t,y} \cdot \Bigg( \Big( 1 + soft\_new\_capacity\_up_{n,t,y}\Big)^{|y|} - 1 \Bigg) \\
        & \quad \forall \ t \ \in \ T^{INV}

Here, :math:`|y|` is the number of years in period :math:`y`, i.e., :math:`duration\_period_{y}`.

Equation NEW_CAPACITY_SOFT_CONSTRAINT_UP
""""""""""""""""""""""""""""""""""""""""
This constraint ensures that the relaxation of the dynamic constraint on new capacity (investment) does not exceed
the level of the investment in the same period (cf. Keppo and Strubegger, 2010 :cite:`keppo_short_2010`).

 .. math::
    CAP\_NEW\_UP_{n,t,y} \leq CAP\_NEW_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


Equation NEW_CAPACITY_CONSTRAINT_LO
"""""""""""""""""""""""""""""""""""
This constraint gives dynamic lower bounds on new capacity.

 .. math::
    CAP\_NEW_{n,t,y}
        \geq & - initial\_new\_capacity\_lo_{n,t,y}
            \cdot \frac{ \Big( 1 + growth\_new\_capacity\_lo_{n,t,y} \Big)^{|y|} }
                       { growth\_new\_capacity\_lo_{n,t,y} } \\
             & + \Big( CAP\_NEW_{n,t,y-1} + historical\_new\_capacity_{n,t,y-1} \Big) \\
             & \hspace{2 cm} \cdot \Big( 1 + growth\_new\_capacity\_lo_{n,t,y} \Big)^{|y|} \\
             & - CAP\_NEW\_LO_{n,t,y} \cdot \Bigg( \Big( 1 + soft\_new\_capacity\_lo_{n,t,y}\Big)^{|y|} - 1 \Bigg) \\
        & \quad \forall \ t \ \in \ T^{INV}


Equation NEW_CAPACITY_SOFT_CONSTRAINT_LO
""""""""""""""""""""""""""""""""""""""""
This constraint ensures that the relaxation of the dynamic constraint on new capacity does not exceed
level of the investment in the same year.

  .. math::
     CAP\_NEW\_LO_{n,t,y} \leq CAP\_NEW_{n,t,y} \quad \forall \ t \ \in \ T^{INV}


Equation ACTIVITY_CONSTRAINT_UP
"""""""""""""""""""""""""""""""
This constraint gives dynamic upper bounds on the market penetration of a technology activity.

 .. math::
    \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}
        \leq & ~ initial\_activity\_up_{n,t,y,h}
            \cdot \frac{ \Big( 1 + growth\_activity\_up_{n,t,y,h} \Big)^{|y|} - 1 }
                       { growth\_activity\_up_{n,t,y,h} } \\
            & + \bigg( \sum_{y^V \leq y-1,m} ACT_{n,t,y^V,y-1,m,h}
                        + \sum_{m} historical\_activity_{n,t,y-1,m,h} \bigg) \\
            & \hspace{2 cm} \cdot \Big( 1 + growth\_activity\_up_{n,t,y,h} \Big)^{|y|} \\
            & + ACT\_UP_{n,t,y,h} \cdot \Bigg( \Big( 1 + soft\_activity\_up_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)


Equation ACTIVITY_SOFT_CONSTRAINT_UP
""""""""""""""""""""""""""""""""""""
This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
level of the activity.

  .. math::
     ACT\_UP_{n,t,y,h} \leq \sum_{y^V \leq y,m} ACT_{n^L,t,y^V,y,m,h}


Equation ACTIVITY_CONSTRAINT_LO
"""""""""""""""""""""""""""""""
This constraint gives dynamic lower bounds on the market penetration of a technology activity.

 .. math::
    \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}
        \geq & - initial\_activity\_lo_{n,t,y,h}
            \cdot \frac{ \Big( 1 + growth\_activity\_lo_{n,t,y,h} \Big)^{|y|} - 1 }
                       { growth\_activity\_lo_{n,t,y,h} } \\
            & + \bigg( \sum_{y^V \leq y-1,m} ACT_{n,t,y^V,y-1,m,h}
                        + \sum_{m} historical\_activity_{n,t,y-1,m,h} \bigg) \\
            & \hspace{2 cm} \cdot \Big( 1 + growth\_activity\_lo_{n,t,y,h} \Big)^{|y|} \\
            & - ACT\_LO_{n,t,y,h} \cdot \Bigg( \Big( 1 + soft\_activity\_lo_{n,t,y,h} \Big)^{|y|} - 1 \Bigg)


Equation ACTIVITY_SOFT_CONSTRAINT_LO
""""""""""""""""""""""""""""""""""""
This constraint ensures that the relaxation of the dynamic activity constraint does not exceed the
level of the activity.

  .. math::
     ACT\_LO_{n,t,y,h} \leq \sum_{y^V \leq y,m} ACT_{n,t,y^V,y,m,h}


Emission section
----------------

Auxiliary variable for aggregate emissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation EMISSION_EQUIVALENCE
"""""""""""""""""""""""""""""
This constraint simplifies the notation of emissions aggregated over different technology types
and the land-use model emulator. The formulation includes emissions from all sub-nodes :math:`n^L` of :math:`n`.

  .. math::
     EMISS_{n,e,\widehat{t},y} =
         \sum_{n^L \in N(n)} \Bigg(
             \sum_{t \in T(\widehat{t}),y^V \leq y,m,h }
                 emission\_factor_{n^L,t,y^V,y,m,e} \cdot ACT_{n^L,t,y^V,y,m,h} \\
             + \sum_{s} \ land\_emission_{n^L,s,y,e} \cdot LAND_{n^L,s,y}
                  \text{ if } \widehat{t} \in \widehat{T}^{LAND} \Bigg)


Bound on emissions
^^^^^^^^^^^^^^^^^^

Equation EMISSION_CONSTRAINT
""""""""""""""""""""""""""""
This constraint enforces upper bounds on emissions (by emission type). For all bounds that include multiple periods,
the parameter :math:`bound\_emission_{n,\widehat{e},\widehat{t},\widehat{y}}` is scaled to represent average annual
emissions over all years included in the year-set :math:`\widehat{y}`.

The formulation includes historical emissions and allows to model constraints ranging over both the model horizon
and historical periods.

  .. math::
     \frac{
         \sum_{y' \in Y(\widehat{y}), e \in E(\widehat{e})}
             \begin{array}{l}
                 duration\_period_{y'} \cdot emission\_scaling_{\widehat{e},e} \cdot \\
                 \Big( EMISS_{n,e,\widehat{t},y'} + \sum_{m} historical\_emission_{n,e,\widehat{t},y'} \Big)
             \end{array}
         }
       { \sum_{y' \in Y(\widehat{y})} duration\_period_{y'} }
     \leq bound\_emission_{n,\widehat{e},\widehat{t},\widehat{y}}


Land-use model emulator section
-------------------------------

Bounds on total land use
^^^^^^^^^^^^^^^^^^^^^^^^

Equation LAND_CONSTRAINT
""""""""""""""""""""""""
This constraint enforces a meaningful result of the land-use model emulator,
in particular a bound on the total land used in |MESSAGEix|.
The linear combination of land scenarios must be equal to 1.

 .. math::
    \sum_{s \in S} LAND_{n,s,y} = 1


Dynamic constraints on land use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
These constraints enforces upper and lower bounds on the change rate per land scenario.

Equation DYNAMIC_LAND_SCEN_CONSTRAINT_UP
""""""""""""""""""""""""""""""""""""""""

 .. math::
    LAND_{n,s,y}
        \leq & initial\_land\_scen\_up_{n,s,y}
            \cdot \frac{ \Big( 1 + growth\_land\_scen\_up_{n,s,y} \Big)^{|y|} - 1 }
                       { growth\_land\_scen\_up_{n,s,y} } \\
             & + \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big)
                 \cdot \Big( 1 + growth\_land\_scen\_up_{n,s,y} \Big)^{|y|}


Equation DYNAMIC_LAND_SCEN_CONSTRAINT_LO
""""""""""""""""""""""""""""""""""""""""

 .. math::
    LAND_{n,s,y}
        \geq & - initial\_land\_scen\_lo_{n,s,y}
            \cdot \frac{ \Big( 1 + growth\_land\_scen\_lo_{n,s,y} \Big)^{|y|} - 1 }
                       { growth\_land\_scen\_lo_{n,s,y} } \\
             & + \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big)
                 \cdot \Big( 1 + growth\_land\_scen\_lo_{n,s,y} \Big)^{|y|}


These constraints enforces upper and lower bounds on the change rate per land type
determined as a linear combination of land use scenarios.

Equation DYNAMIC_LAND_TYPE_CONSTRAINT_UP
""""""""""""""""""""""""""""""""""""""""

 .. math::
    \sum_{s \in S} land\_use_{n,s,y,u} &\cdot LAND_{n,s,y}
        \leq initial\_land\_up_{n,y,u}
            \cdot \frac{ \Big( 1 + growth\_land\_up_{n,y,u} \Big)^{|y|} - 1 }
                       { growth\_land\_up_{n,y,u} } \\
             & + \Big( \sum_{s \in S} \big( land\_use_{n,s,y-1,u}
                         + dynamic\_land\_up_{n,s,y-1,u} \big) \\
                           & \quad \quad \cdot \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big) \Big) \\
                           & \quad \cdot \Big( 1 + growth\_land\_up_{n,y,u} \Big)^{|y|}


Equation DYNAMIC_LAND_TYPE_CONSTRAINT_LO
""""""""""""""""""""""""""""""""""""""""

 .. math::
    \sum_{s \in S} land\_use_{n,s,y,u} &\cdot LAND_{n,s,y}
        \geq - initial\_land\_lo_{n,y,u}
            \cdot \frac{ \Big( 1 + growth\_land\_lo_{n,y,u} \Big)^{|y|} - 1 }
                       { growth\_land\_lo_{n,y,u} } \\
             & + \Big( \sum_{s \in S} \big( land\_use_{n,s,y-1,u}
                         + dynamic\_land\_lo_{n,s,y-1,u} \big) \\
                           & \quad \quad \cdot \big( LAND_{n,s,y-1} + historical\_land_{n,s,y-1} \big) \Big) \\
                           & \quad \cdot \Big( 1 + growth\_land\_lo_{n,y,u} \Big)^{|y|}


.. _section_of_generic_relations:

Section of generic relations (linear constraints)
-------------------------------------------------

This feature is intended for development and testing only - all new features should be implemented
as specific new mathematical formulations and associated sets & parameters!

Auxiliary variable for left-hand side
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation RELATION_EQUIVALENCE
"""""""""""""""""""""""""""""
  .. math::
     REL_{r,n,y} = \sum_{t} \Bigg(
         & \ relation\_new\_capacity_{r,n,y,t} \cdot CAP\_NEW_{n,t,y} \\[4 pt]
         & + relation\_total\_capacity_{r,n,y,t} \cdot \sum_{y^V \leq y} \ CAP_{n,t,y^V,y} \\
         & + \sum_{n^L,y',m,h} \ relation\_activity_{r,n,y,n^L,t,y',m} \\
         & \quad \quad \cdot \Big( \sum_{y^V \leq y'} ACT_{n^L,t,y^V,y',m,h}
                             + historical\_activity_{n^L,t,y',m,h} \Big) \Bigg)

The parameter :math:`historical\_new\_capacity_{r,n,y}` is not included here, because relations can only be active
in periods included in the model horizon and there is no "writing" of capacity relation factors across periods.

Upper and lower bounds on user-defined relations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Equation RELATION_CONSTRAINT_UP
"""""""""""""""""""""""""""""""
  .. math::
     REL_{r,n,y} \leq relation\_upper_{r,n,y}

Equation RELATION_CONSTRAINT_LO
"""""""""""""""""""""""""""""""
  .. math::
     REL_{r,n,y} \geq relation\_lower_{r,n,y}

