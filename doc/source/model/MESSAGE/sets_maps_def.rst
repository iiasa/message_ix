.. note:: This page is generated from inline documentation in ``MESSAGE\sets_maps_def.gms``.

.. _sets_maps_def:

Sets and mappings definition
=============================

This file contains the definition of all sets and mappings used in |MESSAGEix|.

Sets in the |MESSAGEix| implementation
--------------------------------------

.. list-table::
   :widths: 20 12 68
   :header-rows: 1

   * - Set name
     - Notation
     - Explanatory comments
   * - node [#node]_
     - :math:`n \in N`
     - regions, countries, grid cells
   * - commodity
     - :math:`c \in C`
     - resources, electricity, water, land availability, etc.
   * - level
     - :math:`l \in L`
     - levels of the reference energy system or supply chain (primary, secondary, ... , useful)
   * - grade
     - :math:`g \in G`
     - grades of resource quality in the extraction & mining sector
   * - technology [tec]
     - :math:`t \in T`
     - | technologies that use input commodities to produce outputs;
       | the short-hand notation "tec" is used in the GAMS implementation
   * - mode [#mode]_
     - :math:`m \in M`
     - modes of operation for specific technologies
   * - emission
     - :math:`e \in E`
     - greenhouse gases, pollutants, etc.
   * - land_scenario
     - :math:`s \in S`
     - scenarios of land use (for land-use model emulator)
   * - land_type
     - :math:`u \in U`
     - land-use types (e.g., field, forest, pasture)
   * - year [year_all] [#year_all]_ [#period_year]_
     - :math:`y \in Y`
     - model horizon (including historical periods for vintage structure of installed capacity
       and dynamic constraints)
   * - time [#time]_
     - :math:`h \in H`
     - subannual time periods (seasons, days, hours)
   * - relation [#relations]_
     - :math:`r \in R`
     - set of generic linear constraints
   * - rating
     - :math:`q \in Q`
     - identifies the 'quality' of the renewable energy potential
   * - lvl_spatial
     -
     - set of spatial hierarchy levels (global, region, country, grid cell)
   * - lvl_temporal
     -
     - set of temporal hierarchy levels (year, season, day, hour)

.. [#node] The set ``node`` includes spatial units across all levels of spatial disaggregation
   (global, regions, countries, basins, grid cells).
   The hierarchical mapping is implemented via the mapping set ``map_spatial_hierarchy``.
   This set always includes an element 'World' when initializing a ``MESSAGE``-scheme ``message_ix.Scenario``.

.. [#mode] For example, high electricity or high heat production modes of operation for combined heat and power plants.

.. [#year_all] In the |MESSAGEix| implementation in GAMS, the set ``year_all`` denotes the "superset"
   of the entire horizon (historical and model horizon), and the set ``year`` is a dynamic subset of ``year_all``.
   This facilitates an efficient implementation of the historical capacity build-up and
   the (optional) recursive-dynamic solution approach.
   When working with a ``message_ix.Scenario`` via the scientific programming API, the set of all periods is
   called ``year`` for a more concise notation.
   The specification of the model horizon is implemented using the mapping set ``cat_year``
   and the type "firstmodelyear".

.. _period_year_footnote:

.. [#period_year] In |MESSAGEix|, the key of an element in set ``year`` identifies *the last year* of the period,
   i.e., in a set :math:`year = [2000, 2005, 2010, 2015]`,
   the period '2010' comprises the years :math:`[2006, .. ,2010]`.

.. [#time] The set ``time`` collects all sub-annual temporal units across all levels of temporal disaggregation.
   In a ``MESSAGE``-scheme ``ixmp``.Scenario, this set always includes an element "year",
   and the duration of that element is 1 (:math:`duration\_time_{'year'} = 1`).

.. [#relations] A generic formulation of linear constraints is implemented in |MESSAGEix|,
   see :ref:`section_of_generic_relations`. These constraints can be used for testing and development,
   but specific new features should be implemented by specific equations and parameters.


.. _mapping-sets:

Category types and mappings
---------------------------

This feature is used to easily implement aggregation across groups of set elements.
For example, by setting an upper bound over an emission type, the constraint enforces
that the sum over all emission species mapped to that type via the mapping set ``cat_emission``
satisfies that upper bound.

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Set name
     - Notation
     - Explanatory comments
   * - level_resource (level) [#level_res]_
     - :math:`l \in L^{RES} \subseteq L`
     - levels related to `fossil resources` representation
   * - level_renewable (level) [#level_res]_
     - :math:`l \in L^{REN} \subseteq L`
     - levels related to `renewables` representation
   * - type_node [#type_node]_
     - :math:`\widehat{n} \in \widehat{N}`
     - Category types for nodes
   * - cat_node (type_node,node)
     - :math:`n \in N(\widehat{n})`
     - Category mapping between node types and nodes
   * - type_tec [#type_tec]_
     - :math:`\widehat{t} \in \widehat{T}`
     - Category types for technologies
   * - cat_tec (type_tec,tec)
     - :math:`t \in T(\widehat{t})`
     - Category mapping between tec types and technologies
   * - inv_tec (tec) [#inv_tec]_
     - :math:`t \in T^{INV} \subseteq T`
     - Specific subset of investment technologies
   * - renewable_tec (tec) [#renewable_tec]_
     - :math:`t \in T^{REN} \subseteq T`
     - Specific subset of renewable-energy technologies
   * - type_emission
     - :math:`\widehat{e} \in \widehat{E}`
     - Category types for emissions (greenhouse gases, pollutants, etc.)
   * - cat_emission (type_emission,emission)
     - :math:`e \in E(\widehat{e})`
     - Category mapping between emission types and emissions
   * - type_tec_land (type_tec) [#type_tec_land]_
     - :math:`\widehat{t} \in \widehat{T}^{LAND} \subseteq \widehat{T}`
     - Mapping set of technology types and land use
   * - balance_equality (commodity,level)
     - :math:`c \in C, l \in L`
     - Commodities and level related to :doc:`Equation COMMODITY_BALANCE_LT
       <model_core>`

.. [#level_res] The constraint ``EXTRACTION_EQUIVALENCE`` is active only for the levels included in this set,
   and the constraint ``COMMODITY_BALANCE`` is deactivated for these levels.

.. [#type_node] The element "economy" is added by default as part of the ``MESSAGE``-scheme ``ixmp``.Scenario.

.. [#type_tec] The element "all" in ``type_tec`` and the associated mapping to all technologies in the set ``cat_tec``
   are added by default as part of the ``MESSAGE``-scheme ``message_ix``.Scenario.

.. [#inv_tec] The auxiliary set ``inv_tec`` (subset of ``technology``) is a short-hand notation for all technologies
   with defined investment costs. This activates the investment cost part in the objective function and the
   constraints for all technologies where investment decisions are relevant.
   It is added by default when exporting ``MESSAGE``-scheme ``message_ix``.Scenario to gdx.

.. [#renewable_tec] The auxiliary set ``renewable_tec`` (subset of ``technology``) is a short-hand notation
   for all technologies with defined parameters relevant for the equations in the "Renewable" section.
   It is added by default when exporting ``MESSAGE``-scheme ``message_ix``.Scenario to gdx.

.. [#type_tec_land] The mapping set ``type_tec_land`` is a dynamic subset of ``type_tec`` and specifies whether
   emissions from the land-use model emulator module are included when aggregrating over a specific technology type.
   The element "all" is added by default in a ``MESSAGE``-scheme ``message_ix``.Scenario.

Mappings sets
-------------

These sets are generated automatically when exporting a ``MESSAGE``-scheme ``ixmp``.Scenario to gdx using the API.
They are used in the GAMS model to reduce model size by excluding non-relevant variables and equations
(e.g., actitivity of a technology outside of its technical lifetime).

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Set name
     - Notation
     - Explanatory comments
   * - map_node(node,location)
     -
     - mapping of nodes across hierarchy levels (location is in node)

Mapping sets (flags) for bounds
-------------------------------

There are a number of mappings sets generated when exporting a ``message_ix.Scenario`` to gdx.
They are used as 'flags' to indicate whether a constraint is active.
The names of these sets follow the format ``is_<constraint>_<dir>``.

Such mapping sets are necessary because GAMS does not distinguish between 0 and 'no value assigned',
i.e., it cannot differentiate between a bound of 0 and 'no bound assigned'.

Mapping sets (flags) for fixed variables
----------------------------------------

Similar to the mapping sets for bounds, there are mapping sets to indicate whether decision variables
are pre-defined to a specific value, usually taken from a solution of another model instance.
This can be used to represent imperfect foresight where a policy shift or parameter change is introduced in later
years. The names of these sets follow the format ``is_fixed_<variable>``.

