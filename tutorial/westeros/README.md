Westeros Tutorials
==================

The Westeros tutorials provide users with a step-by-step guide on how to use `MESSAGEix`
to build an energy model.  The tutorials have been built around a fictional regional
'Westeros'.  The tutorials start of by introducing the central components of `MESSAGEix`
by means of building a simple energy model, `Westeros Electrified`. 

Subsequent tutorials will add further details and complexity, building on the inital
energy model, thereby providing guidance on the application of the the numerous features
of `MESSAGEix`. 

Contents
========

westeros_baseline: Building a Simple Energy Model
-------------------------------------------------
The first Westeros tutorial presents the smallest possible energy system to illustrate
a range of framework features.

westeros_emissions_bound: Introducing emissions
-----------------------------------------------
How to introduce emissions and constraints on these to investigate impact of climate
policy.
Keywords: `emission_factor`, 'bound_emission`

westeros_emissions_taxes: Introducing emission taxes
----------------------------------------------------
How to introduce a carbon tax.
Keywords: `price_emission`

westeros_firm_capacity: Adding representation of renewables - Part 1
--------------------------------------------------------------------
For a model which does not use sub-annual timesteps and therefore does not depict peak
load, `firm capacity`, i.e. sufficient backup capacity from electricity generation plants
to maintain reliability through reasonable load and contingency events, needs to be
accounted for.
Keywords: `peak_load_factor`, `rating_bin`, `reliability_factor`
