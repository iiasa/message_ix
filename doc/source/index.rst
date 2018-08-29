The |MESSAGEix| framework 
=========================

.. figure:: _static/ix_features.png
   :width: 320px
   :align: right
   
   The |ixmp| (source: :cite:`huppmann_messageix_2018`)

Overview and scope
------------------

|MESSAGEix| is a versatile, open-source, dynamic systems-optimization modelling framework.
It was developed for strategic energy planning and integrated assessment of
energy-engineering-economy-environment systems (E4).
The framework can be applied to analyse scenarios of the energy system transformation
under technical-engineering constraints and political-societal considerations.
The optimization model can be linked to the general-economy MACRO model
to incorporate feedback between prices and demand levels for energy and commodities.
The equations are implemented in the mathematical programming system `GAMS`_
for numerical solution of a model instance.

The |MESSAGEix| framework is fully integrated with IIASA's |ixmp| (ixmp),
a data warehouse for high-powered numerical scenario analysis.
The platform supports an efficient workflow between original input data sources,
the implementation of the mathematical model formulation, 
and the analysis of numerical results.
The platform can be accessed via a web-based user interface
and application programming interfaces (API)
to the scientific programming languages Python and R.
The platform also includes a generic data exchange API
to `GAMS`_ for numerical computation.

This documentation provides an introduction and the mathematical formulation 
of the |MESSAGEix| equations and auxiliary functions.
For the scientific reference of the framework, 
see Huppmann et al. (submitted) :cite:`huppmann_messageix_2018`.
The formulation of |MESSAGEix| is a re-implementation and extension of `'MESSAGE V'`
(Messner and Strubegger, 1995 :cite:`messner_users_1995`),
the Integrated Assessment model developed at IIASA since the 1980s.
For an overview of the |MESSAGEix| model used at the IIASA Energy Program
and a list of recent publications, please refer to the `MESSAGE-GLOBIOM documentation website`_.

.. _`GAMS` : http://www.gams.com

.. _`MESSAGE-GLOBIOM documentation website` : http://data.ene.iiasa.ac.at/message-globiom/

Frequently asked questions
--------------------------

Please refer to our `FAQ page`_ for more information.

.. _`FAQ page`: faq.html

License and user guidelines
---------------------------

|MESSAGEix| and the |ixmp| are licensed under an `APACHE 2.0 open-source license`_. 
See the `LICENSE`_ file for the full text.

.. _`APACHE 2.0 open-source license`: http://www.apache.org/licenses/LICENSE-2.0

.. _`LICENSE`: https://github.com/iiasa/message_ix/blob/master/LICENSE

Please read the `NOTICE`_ included in this repository and other documents referenced below
for the user guidelines and further information.

The community mailing list for questions and discussions on new features is hosted using Googlegroups.
Please join at `groups.google.com/d/forum/message_ix`_
and use <message_ix@googlegroups.com> to send an email to the |MESSAGEix| user community.

.. toctree::
   :maxdepth: 1

   faq
   notice
   contributing
   contributor_license

.. _`NOTICE`: notice.html

.. _`groups.google.com/d/forum/message_ix` : https://groups.google.com/d/forum/message_ix

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

Documentation
-------------

The `mathematical model description`_ and other documentation pages are built
from the documentation comments in the GAMS code and the Python and R interface bindings. 
The documentation available on `MESSAGEix.iiasa.ac.at`_ is synchronized with the latest release on the
public GitHub repository.

.. _`mathematical model description`: model/MESSAGE/model_core.html

.. _`MESSAGEix.iiasa.ac.at` : http://MESSAGEix.iiasa.ac.at

.. _`github.com/iiasa/message_ix` : https://github.com/iiasa/message_ix/tree/master

Getting started
---------------

Installation
^^^^^^^^^^^^

For new users, we recommend to install `Anaconda`_ (Python 3.6 or higher) and
`GAMS`_. Importantly, when installing GAMS, check the box labeled `Use advanced 
installation mode` select `Add GAMS directory to PATH environment variable` on
the Advanced Options page.
   
Then, open a command prompt and type

    ```
    conda install -c conda-forge message-ix
    ```

For expert users or to install from source, please follow the installation
instructions in the `README`_.

.. tutorials:

Tutorials
^^^^^^^^^

To get started with a stylized energy system model implemented in |MESSAGEix|,
look at the tutorials included in this repository:

.. toctree::
   :maxdepth: 1

   tutorials

.. _`Anaconda`: https://www.continuum.io/downloads

.. _`README`: https://github.com/iiasa/message_ix#install-from-source-advanced-users


Running the |MESSAGEix| model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Scientific programming API documentation
----------------------------------------

For a comprehensive documentation of the scientific programming APIs,
please see the documentation of the `ixmp` package at
`software.ene.iiasa.ac.at/ixmp`_.

.. _`software.ene.iiasa.ac.at/ixmp`: https://software.ene.iiasa.ac.at/ixmp

Bibliography
------------

.. toctree::
   :maxdepth: 2
   
   bibliography   
