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

Getting Started
---------------

.. toctree::
   :maxdepth: 1

   getting_started


Have a Question?
----------------

First, check out our FAQ:

.. toctree::
   :maxdepth: 1
   
   faq


Next, try the community mailing list hosted using Google groups:
`groups.google.com/d/forum/message_ix`_ .

.. _`groups.google.com/d/forum/message_ix` : https://groups.google.com/d/forum/message_ix

The |MESSAGEix| Model
---------------------

.. toctree::
   :maxdepth: 1
   
   model

API Documentation
-----------------

.. toctree::
   :maxdepth: 1
   
   api

Using |MESSAGEix|
-----------------

|MESSAGEix| and the |ixmp| are licensed under an `APACHE 2.0 open-source license`_. 
See the `LICENSE`_ file for the full text.

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


Bibliography
------------

.. toctree::
   :maxdepth: 2
   
   bibliography   
