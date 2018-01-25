The |MESSAGEix| framework 
=========================

.. figure:: _static/ix_components.png
   :width: 320px
   :align: right
   
   The components of the |ixmp|

|MESSAGEix| is a versatile, open-source dynamic systems-optimization model.
It can be applied to analyse scenarios of the energy system transformation
under technical-engineering constraints and political-societal considerations.
The optimization model can be linked to the general-economy MACRO model
to incorporate feedback between prices and demand levels for energy and commodities.
The equations are implemented in the mathematical programming system `GAMS`_
for numerical solution of a model instance.

|MESSAGEix| is fully integrated with IIASA's |ixmp| (ixmp),
a data warehouse for high-powered numerical scenario analysis.
The framework allows an efficient workflow between original input data sources,
the implementation of the mathematical model formulation, 
and the analysis of numerical results.
The platform can be accessed via a web-based user interface 
and application programming interfaces (API)
to the scientific programming languages Python and R.
The platform also includes an API to `GAMS`_ for numerical computation.

This documentation provides an introduction and the mathematical formulation 
of the |MESSAGEix| equations and auxiliary functions.
It also includes the documentation of the ixmp APIs 
to the scientific programming languages Python and R.

For the scientific reference of the framework, 
see Huppmann et al., in preparation :cite:`huppmann_messageix_2018`.
The formulation of |MESSAGEix| is a re-implementation and extension of `'MESSAGE V'`
(Messner and Strubegger, 1995 :cite:`messner_users_1995`).
For an overview of the |MESSAGEix| model used at the IIASA Energy Program
and a list of recent publications, please refer to the `MESSAGE-GLOBIOM documentation website`_.

.. _`GAMS` : http://www.gams.com

.. _`MESSAGE-GLOBIOM documentation website` : http://data.ene.iiasa.ac.at/message-globiom/

License and user guidelines
---------------------------

| |MESSAGEix| and the |ixmp| are licensed under an `APACHE 2.0 open-source license`_. 
| See the `LICENSE`_ file included in this repository for the full text.

.. _`APACHE 2.0 open-source license`: http://www.apache.org/licenses/LICENSE-2.0

.. _`LICENSE`: https://github.com/iiasa/message_ix/blob/master/LICENSE

Please read the `NOTICE`_ included in this repository and other documents referenced below
for the user guidelines and further information.

.. toctree::
   :maxdepth: 1

   notice
   contributing
   contributor_license

.. _`NOTICE`: notice.html

An overview of the |MESSAGEix| framework
----------------------------------------

.. figure:: _static/ix_overview.png 

   Component features and their interlinkages in the |ixmp|: 
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
- A direct implementation of the 'soft' relaxations of dynamic constraints on new capacity and activity 
  (see Keppo and Strubegger, 2010 :cite:`keppo_short_2010`)
- Implementation of perfect-foresight and dynamic-recursive (myopic) solution approaches
- A flexible formulation of dynamic constraints (market penetration of new capacity an activity) 
  allowing for endogenuous learning spillovers across technologies, regions and model periods

Documentation pages
-------------------

The `mathematical model description`_ and other documentation pages are built from the documentation comments 
in the GAMS code, the Python and R interface bindings, as well as the Java source code for the database backend. 
The documentation available on `www.iiasa.ac.at/message_ix`_ is synchronized with the github repository
and automatically built from the current master branch upon every update.

.. _`mathematical model description`: model/MESSAGE_framework/model_core.html

.. _`www.iiasa.ac.at/message_ix` : https://www.iiasa.ac.at/message_ix

Getting started
---------------

Refer to the page on `technical requirements`_ for a list of dependencies,
installation instructions, and other information on getting started.

For an introduction to the |ixmp|, look at the tutorials of the ixmp package
(included as a submodule to this repository) at `ixmp/tutorial/README`_.

To get started with a stylized energy system model implemented in |MESSAGEix|,
look at the tutorials included in this repository at `tutorial/README`_.

Further information:

.. toctree::
   :maxdepth: 1

   technical_requirements
   tutorials

.. _`technical requirements`: technical_requirements.html

.. _`ixmp/tutorial/README` : https://github.com/iiasa/message_ix/blob/master/ixmp/tutorial/README.md

.. _`tutorial/README` : https://github.com/iiasa/message_ix/blob/master/tutorial/README.md


Running the |MESSAGEix| model
-----------------------------

There are three methods to run the |MESSAGEix| model:

- Via the scientific programming API's using the packages/libraries ``ixmp`` and ``message_ix``,
  calling the method ``solve()`` of the ``ixmp``.Scenario class (see the tutorials).

- Using the file ``MESSAGE_master.gms``, where the scenario name (i.e., the gdx input file), the optimization horizon 
  (perfect foresight or myopic/rolling-horizon version), and other options can be defined explicitly.
    
  *This approach is recommended for users who prefer to work via GAMS IDE or other text editors 
  to set the model specifications.*
   
- Directly from the command line calling the file ``MESSAGE_run.gms`` (see the `auto-doc page`_). 
  The scenario name and other options can be passed as command line parameters, 
  e.g. :literal:`gams MESSAGE_run.gms --in="<data-file>" --out="<output-file>"`.

.. _`Scientific Programming APIs` : scientific_programming_api.html
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
   model/MESSAGE_framework/sets_maps_def
   model/MESSAGE_framework/parameter_def
   model/MESSAGE_framework/model_core
   model/MESSAGE_framework/model_solve
   model/MESSAGE_framework/reporting
   model/MESSAGE_framework/scaling_investment_costs
   model/MACRO/macro_core
   efficiency_methodology

Scientific programming API documentation
----------------------------------------

The documentation of the scientific programming APIs
are included directly from the ``ixmp`` repository.

.. toctree::
   :maxdepth: 2

   scientific_programming_api

Bibliography
------------

.. toctree::
   :maxdepth: 2
   
   bibliography   
