***
* .. _sets_maps_def:
*
* Sets and mappings definition
* =============================
*
* This file contains the definition of all sets and mappings used in |MESSAGEix|.
***

* indices to mapping sets will always be in the following order:
* lvl_spatial, lvl_temporal,
* node_location, tec, year_vintage, year_actual, mode, commodity, level, grade,
* node_origin/destination, emission, time_actual), time_origin/destination, rating

* allows sets to be empty
$ONEMPTY

*----------------------------------------------------------------------------------------------------------------------*
* Set definitions                                                                                                      *
*----------------------------------------------------------------------------------------------------------------------*

***
* Sets in the |MESSAGEix| implementation
* --------------------------------------
*
* .. list-table::
*    :widths: 20 12 68
*    :header-rows: 1
*
*    * - Set name
*      - Notation
*      - Explanatory comments
*    * - node [#node]_
*      - :math:`n \in N`
*      - regions, countries, grid cells
*    * - commodity
*      - :math:`c \in C`
*      - resources, electricity, water, land availability, etc.
*    * - level
*      - :math:`l \in L`
*      - levels of the reference energy system or supply chain (primary, secondary, ... , useful)
*    * - grade
*      - :math:`g \in G`
*      - grades of resource quality in the extraction & mining sector
*    * - technology [tec]
*      - :math:`t \in T`
*      - | technologies that use input commodities to produce outputs;
*        | the short-hand notation "tec" is used in the GAMS implementation
*    * - mode [#mode]_
*      - :math:`m \in M`
*      - modes of operation for specific technologies
*    * - emission
*      - :math:`e \in E`
*      - greenhouse gases, pollutants, etc.
*    * - land_scenario
*      - :math:`s \in S`
*      - scenarios of land use (for land-use model emulator)
*    * - land_type
*      - :math:`u \in U`
*      - land-use types (e.g., field, forest, pasture)
*    * - year [year_all] [#year_all]_ [#period_year]_
*      - :math:`y \in Y`
*      - model horizon (including historical periods for vintage structure of installed capacity
*        and dynamic constraints)
*    * - time [#time]_
*      - :math:`h \in H`
*      - subannual time periods (seasons, days, hours)
*    * - relation [#relations]_
*      - :math:`r \in R`
*      - set of generic linear constraints
*    * - rating
*      - :math:`q \in Q`
*      - identifies the 'quality' of the renewable energy potential
*    * - lvl_spatial
*      -
*      - set of spatial hierarchy levels (global, region, country, grid cell)
*    * - lvl_temporal
*      -
*      - set of temporal hierarchy levels (year, season, day, hour)
*
* .. [#node] The set ``node`` includes spatial units across all levels of spatial disaggregation
*    (global, regions, countries, basins, grid cells).
*    The hierarchical mapping is implemented via the mapping set ``map_spatial_hierarchy``.
*    This set always includes an element 'World' when initializing a ``MESSAGE``-scheme ``message_ix.Scenario``.
*
* .. [#mode] For example, high electricity or high heat production modes of operation for combined heat and power plants.
*
* .. [#year_all] In the |MESSAGEix| implementation in GAMS, the set ``year_all`` denotes the "superset"
*    of the entire horizon (historical and model horizon), and the set ``year`` is a dynamic subset of ``year_all``.
*    This facilitates an efficient implementation of the historical capacity build-up and
*    the (optional) recursive-dynamic solution approach.
*    When working with a ``message_ix.Scenario`` via the scientific programming API, the set of all periods is
*    called ``year`` for a more concise notation.
*    The specification of the model horizon is implemented using the mapping set ``cat_year``
*    and the type "firstmodelyear".
*
* .. _period_year_footnote:
*
* .. [#period_year] In |MESSAGEix|, the key of an element in set ``year`` identifies *the last year* of the period,
*    i.e., in a set :math:`year = [2000, 2005, 2010, 2015]`,
*    the period '2010' comprises the years :math:`[2006, .. ,2010]`.
*
* .. [#time] The set ``time`` collects all sub-annual temporal units across all levels of temporal disaggregation.
*    In a ``MESSAGE``-scheme ``ixmp``.Scenario, this set always includes an element "year",
*    and the duration of that element is 1 (:math:`duration\_time_{'year'} = 1`).
*
* .. [#relations] A generic formulation of linear constraints is implemented in |MESSAGEix|,
*    see :ref:`section_of_generic_relations`. These constraints can be used for testing and development,
*    but specific new features should be implemented by specific equations and parameters.
***

Sets
    node            world - regions - countries - grid cells
    commodity       resources - electricity - water - land availability - etc.
    level           levels of the reference energy system or supply chain ( primary - secondary - ... - useful )
    sector          sectors (for integration with MACRO)
    grade           grades of extraction of raw materials
    tec             technologies
    mode            modes of operation
    emission        greenhouse gases - pollutants - etc.
    land_scenario   scenarios of land use (for land-use model emulator)
    land_type       types of land use
    year_all        years (over entire model horizon)
    year (year_all) years included in a model instance (for myopic or rolling-horizon optimization)
    time            subannual time periods (seasons - days - hours)
    shares          share constraint relations
    relation        generic linear relations
    lvl_spatial     hierarchical levels of spatial resolution
    lvl_temporal    hierarchical levels of temporal resolution
    rating          identifies the 'quality' of the renewable energy potential (bins acc. to Sullivan)
;

* definition of aliases
Alias(node,location);
Alias(node,node2);
Alias(node,node_share);
Alias(tec,tec2);
Alias(commodity,commodity2);
Alias(level,level2);
Alias(emission,emission2);
Alias(year_all,vintage);
Alias(year_all,year_all2);
Alias(year_all,year_all3);
Alias(year,year2);
Alias(year,year3);
Alias(time,time2);
Alias(time,time_act);
Alias(time,time_od);
Alias(mode, mode2);

*----------------------------------------------------------------------------------------------------------------------*
* Category types and mappings                                                                                                       *
*----------------------------------------------------------------------------------------------------------------------*

***
* Category types and mappings
* ---------------------------
*
* This feature is used to easily implement aggregation across groups of set elements.
* For example, by setting an upper bound over an emission type, the constraint enforces
* that the sum over all emission species mapped to that type via the mapping set ``cat_emission``
* satisfies that upper bound.
*
* .. list-table::
*    :widths: 25 15 60
*    :header-rows: 1
*
*    * - Set name
*      - Notation
*      - Explanatory comments
*    * - level_resource (level) [#level_res]_
*      - :math:`l \in L^{RES} \subseteq L`
*      - levels related to `fossil resources` representation
*    * - level_renewable (level) [#level_res]_
*      - :math:`l \in L^{REN} \subseteq L`
*      - levels related to `renewables` representation
*    * - type_node [#type_node]_
*      - :math:`\widehat{n} \in \widehat{N}`
*      - Category types for nodes
*    * - cat_node (type_node,node)
*      - :math:`n \in N(\widehat{n})`
*      - Category mapping between node types and nodes
*    * - type_tec [#type_tec]_
*      - :math:`\widehat{t} \in \widehat{T}`
*      - Category types for technologies
*    * - cat_tec (type_tec,tec)
*      - :math:`t \in T(\widehat{t})`
*      - Category mapping between tec types and technologies
*    * - inv_tec (tec) [#inv_tec]_
*      - :math:`t \in T^{INV} \subseteq T`
*      - Specific subset of investment technologies
*    * - renewable_tec (tec) [#renewable_tec]_
*      - :math:`t \in T^{REN} \subseteq T`
*      - Specific subset of renewable-energy technologies
*    * - type_emission
*      - :math:`\widehat{e} \in \widehat{E}`
*      - Category types for emissions (greenhouse gases, pollutants, etc.)
*    * - cat_emission (type_emission,emission)
*      - :math:`e \in E(\widehat{e})`
*      - Category mapping between emission types and emissions
*    * - type_tec_land (type_tec) [#type_tec_land]_
*      - :math:`\widehat{t} \in \widehat{T}^{LAND} \subseteq \widehat{T}`
*      - Mapping set of technology types and land use
*    * - balance_equality (commodity,level)
*      - :math:`c \in C^{FULL} \subseteq C`
*      - :math:`l \in L^{FULL} \subseteq L`
*      - Commodities and level related to `Equation COMMODITY_BALANCE_LT`_
*
* .. [#level_res] The constraint ``EXTRACTION_EQUIVALENCE`` is active only for the levels included in this set,
*    and the constraint ``COMMODITY_BALANCE`` is deactivated for these levels.
*
* .. [#type_node] The element "economy" is added by default as part of the ``MESSAGE``-scheme ``ixmp``.Scenario.
*
* .. [#type_tec] The element "all" in ``type_tec`` and the associated mapping to all technologies in the set ``cat_tec``
*    are added by default as part of the ``MESSAGE``-scheme ``message_ix``.Scenario.
*
* .. [#inv_tec] The auxiliary set ``inv_tec`` (subset of ``technology``) is a short-hand notation for all technologies
*    with defined investment costs. This activates the investment cost part in the objective function and the
*    constraints for all technologies where investment decisions are relevant.
*    It is added by default when exporting ``MESSAGE``-scheme ``message_ix``.Scenario to gdx.
*
* .. [#renewable_tec] The auxiliary set ``renewable_tec`` (subset of ``technology``) is a short-hand notation
*    for all technologies with defined parameters relevant for the equations in the "Renewable" section.
*    It is added by default when exporting ``MESSAGE``-scheme ``message_ix``.Scenario to gdx.
*
* .. [#type_tec_land] The mapping set ``type_tec_land`` is a dynamic subset of ``type_tec`` and specifies whether
*    emissions from the land-use model emulator module are included when aggregrating over a specific technology type.
*    The element "all" is added by default in a ``MESSAGE``-scheme ``message_ix``.Scenario.
***

* category types and mappings
Sets
    level_resource (level)                  subset of 'level' to mark all levels related to make hfossil resources
    level_renewable(level)                  subset of 'level' to mark all levels related to renewable resources
    type_node                               types of nodes
    cat_node(type_node,node)                mapping of nodes to respective categories
    type_tec                                types of technologies
    cat_tec(type_tec,tec)                   mapping of technologies to respective categories
    inv_tec(tec)                            technologies that have explicit investment and capacity decision variables
    renewable_tec(tec)                      technologies that use renewable energy potentials
    addon(tec)                              technologies that are an add-on to other (parent) technologies
    type_addon                              types of add-on technologies (that can be applied mutually exclusive)
    cat_addon(type_addon,addon)             mapping of add-on technologies to respective add-on technology types
    type_year                               types of year aggregations
    cat_year(type_year,year_all)            mapping of years to respective categories
    type_emission                           types of emission aggregations
    cat_emission(type_emission,emission)    mapping of emissions to respective categories
    type_tec_land(type_tec)                 dynamic set whether emissions from land use are included in type_tec
    balance_equality(commodity,level)       mapping of commodities-level where the supply-demand balance must be maintained with equality
;

Alias(type_tec,type_tec_share);
Alias(type_tec,type_tec_total);

*----------------------------------------------------------------------------------------------------------------------*
* Mapping sets                                                                                                         *
*----------------------------------------------------------------------------------------------------------------------*

***
* Mappings sets
* -------------
*
* These sets are generated automatically when exporting a ``MESSAGE``-scheme ``ixmp``.Scenario to gdx using the API.
* They are used in the GAMS model to reduce model size by excluding non-relevant variables and equations
* (e.g., actitivity of a technology outside of its technical lifetime).
*
* .. list-table::
*    :widths: 25 15 60
*    :header-rows: 1
*
*    * - Set name
*      - Notation
*      - Explanatory comments
*    * - map_node(node,location)
*      -
*      - mapping of nodes across hierarchy levels (location is in node)
***

Sets
    map_node(node,location)                     mapping of nodes across hierarchy levels (location is in node)
    map_time(time,time2)                        mapping of time periods across hierarchy levels (time2 is in time)

    map_resource(node,commodity,grade,year_all)  mapping of resources and grades to node over time
    map_ren_grade(node,commodity,grade,year_all) mapping of renewables and grades to node over time
    map_ren_com(node,tec,commodity,year_all)     mapping of technologies to renewable energy source as input
    map_rating(node,tec,commodity,level,rating,year_all) mapping of technologues to ratings bin assignment

    map_commodity(node,commodity,level,year_all,time)    mapping of commodity-level to node and time
    map_stocks(node,commodity,level,year_all)    mapping of commodity-level to node and time

    map_tec(node,tec,year_all)                   mapping of technology to node and years
    map_tec_time(node,tec,year_all,time)         mapping of technology to temporal dissagregation (time)
    map_tec_mode(node,tec,year_all,mode)         mapping of technology to modes
    map_tec_act(node,tec,year_all,mode,time)     mapping of technology to modes AND temporal dissagregation
    map_tec_addon(tec,type_addon)                mapping of types of add-on technologies to the underlying parent technology

    map_spatial_hierarchy(lvl_spatial,node,node)    mapping of spatial resolution to nodes (last index is 'parent')
    map_temporal_hierarchy(lvl_temporal,time,time)  mapping of temporal resolution to time (last index is 'parent')

    map_shares_commodity_share(shares,node,
        node,type_tec,mode,commodity,level)   mapping for commodity share constraints (numerator)
    map_shares_commodity_total(shares,node,
        node,type_tec,mode,commodity,level)   mapping for commodity share constraints (denominator)

    map_land(node,land_scenario,year_all)            mapping of land-use model emulator scenarios to nodes and years
    map_relation(relation,node,year_all)             mapping of generic (user-defined) relations to nodes and years
;

* additional sets created in GAMS to make notation more concise
Sets
    map_tec_lifetime(node,tec,vintage,year_all)  mapping of technologies to periods within technical lifetime
;

*----------------------------------------------------------------------------------------------------------------------*
* Mapping sets (flags) for bounds                                                                                             *
*----------------------------------------------------------------------------------------------------------------------*

***
* Mapping sets (flags) for bounds
* -------------------------------
*
* There are a number of mappings sets generated when exporting a ``message_ix.Scenario`` to gdx.
* They are used as 'flags' to indicate whether a constraint is active.
* The names of these sets follow the format ``is_<constraint>_<dir>``.
*
* Such mapping sets are necessary because GAMS does not distinguish between 0 and 'no value assigned',
* i.e., it cannot differentiate between a bound of 0 and 'no bound assigned'.
***

Sets
    is_bound_extraction_up(node,commodity,grade,year_all) flag whether upper bound exists for extraction of commodity
    is_bound_new_capacity_up(node,tec,year_all)      flag whether upper bound exists for new capacity
    is_bound_new_capacity_lo(node,tec,year_all)      flag whether lower bound exists for new capacity
    is_bound_total_capacity_up(node,tec,year_all)    flag whether upper bound exists for total installed capacity
    is_bound_total_capacity_lo(node,tec,year_all)    flag whether lower bound exists for total installed capacity
    is_bound_activity_up(node,tec,year_all,mode,time) flag whether upper bound exists for a technology activity
*   is_bound_activity_lo(node,tec,year_all,mode,time) flag whether lower bound exists for a technology activity
* this last flag is not required because the lower bound defaults to zero unless explicitly specified otherwise

    is_dynamic_new_capacity_up(node,tec,year_all)    flag whether upper dynamic constraint exists for new capacity (investment)
    is_dynamic_new_capacity_lo(node,tec,year_all)    flag whether lower dynamic constraint exists for new capacity (investment)
    is_dynamic_activity_up(node,tec,year_all,time)   flag whether upper dynamic constraint exists for a technology (activity)
    is_dynamic_activity_lo(node,tec,year_all,time)   flag whether lower dynamic constraint exists for a technology (activity)

    is_bound_emission(node,type_emission,type_tec,type_year) flag whether emissions bound exists

    is_dynamic_land_scen_up(node,land_scenario,year_all)   flag whether dynamic upper constraint on land-scenario change exists
    is_dynamic_land_scen_lo(node,land_scenario,year_all)   flag whether dynamic lower constraint on land-scenario change exists
    is_dynamic_land_up(node,year_all,land_type)   flag whether dynamic upper constraint on land-type use change exists
    is_dynamic_land_lo(node,year_all,land_type)   flag whether dynamic lower constraint on land-type use change exists

    is_relation_upper(relation,node,year_all)     flag whether upper bounds exists for generic relation
    is_relation_lower(relation,node,year_all)     flag whether lower bounds exists for generic relation
;

*----------------------------------------------------------------------------------------------------------------------*
* Mapping sets (flags) for fixed variables                                                                             *
*----------------------------------------------------------------------------------------------------------------------*

***
* Mapping sets (flags) for fixed variables
* ----------------------------------------
*
* Similar to the mapping sets for bounds, there are mapping sets to indicate whether decision variables
* are pre-defined to a specific value, usually taken from a solution of another model instance.
* This can be used to represent imperfect foresight where a policy shift or parameter change is introduced in later
* years. The names of these sets follow the format ``is_fixed_<variable>``.
***

Sets
    is_fixed_extraction(node,commodity,grade,year_all)     flag whether extraction variable is fixed
    is_fixed_stock(node,commodity,level,year_all)          flag whether stock variable is fixed
    is_fixed_new_capacity(node,tec,year_all)               flag whether new capacity variable is fixed
    is_fixed_capacity(node,tec,vintage,year_all)           flag whether maintained capacity variable is fixed
    is_fixed_activity(node,tec,vintage,year_all,mode,time) flag whether activity variable is fixed
    is_fixed_land(node,land_scenario,year_all)             flag whether land level is fixed
;
