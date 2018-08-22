
An overview of the |MESSAGEix| framework
----------------------------------------

.. figure:: _static/ix_components.png 

   Components and their interlinkages in the |ixmp| (source :cite:`huppmann_messageix_2018`): 
   web-based user interface, scientific programming interface,  
   modeling platform, database backend, 
   implementation of the |MESSAGEix| mathematical model formulation

Features of the |MESSAGEix| model
---------------------------------

The |MESSAGEix| implementation includes:
 
- A comprehensive implementation of 'technologies' to represent a *reference energy system*
  (i.e., the fuel supply chain, conversion technologies from primary to secondary energy forms,
  transmissions and distribution, and final demand for energy services)
- Vintaging of capacity and explicit possibility for early retirement/decommissioning of technologies
- Explicit formulations for the system integration of variable renewable energy sources
  based on Sullivan et al., 2013 :cite:`sullivan_VRE_2013` and Johnson et al., 2016 :cite:`johnson_VRE_2016`. 
- A direct implementation of the 'soft' relaxations of dynamic constraints on new capacity and activity 
  (see Keppo and Strubegger, 2010 :cite:`keppo_short_2010`)
- Implementation of perfect-foresight and dynamic-recursive (myopic) solution approaches

Running the |MESSAGEix| model
-----------------------------

There are three methods to run the |MESSAGEix| model:

- Via the scientific programming APIs using the packages/libraries ``ixmp`` and ``message_ix``,
  calling the method ``solve()`` of the ``message_ix.Scenario`` class (see the `tutorials`_).

- Using the file ``MESSAGE_master.gms``, where the scenario name (i.e., the gdx input file), 
  the optimization horizon (perfect foresight or myopic/rolling-horizon version),
  and other options can be defined explicitly.
    
  *This approach is recommended for users who prefer to work via GAMS IDE or other text editors 
  to set the model specifications.*
   
- Directly from the command line calling the file ``MESSAGE_run.gms`` (see the `auto-doc page`_). 
  The scenario name and other arguments can be passed as command line parameters, 
  e.g. :literal:`gams MESSAGE_run.gms --in="<data-file>" --out="<output-file>"`.

.. _`auto-doc page`: model/MESSAGE_run.html
   
Overview of model structure and includes files
----------------------------------------------

The pages listed below provide a comprehensive documentation
of the equations and the workflow when solving a |MESSAGEix| model instance.
The documentation is generated to a large extent from mark-up comments
in the GAMS code.

.. toctree::
   :maxdepth: 2

   model/MESSAGE_run
   model/MESSAGE-MACRO_run
   model/MESSAGE/sets_maps_def
   model/MESSAGE/parameter_def
   model/MESSAGE/model_core
   model/MESSAGE/model_solve
   model/MESSAGE/reporting
   model/MESSAGE/scaling_investment_costs
   model/MACRO/macro_core
   efficiency_methodology
   debugging
