Python & R API
==============

The application programming interface (API) for |MESSAGEix| model developers is implemented in Python:

.. contents::
   :local:

Support for R usage of the core classes is provided through the `reticulate`_ package. For instance::

    > library(reticulate)
    > ixmp <- import('ixmp')
    > message_ix <- import('message_ix')
    > mp <- ixmp$Platform(...)
    > scen <- message_ix$Scenario(mp, ...)

.. _`reticulate`: https://rstudio.github.io/reticulate/


``ixmp`` package
----------------

:mod:`ixmp` provides three classes. These are fully described by the :doc:`ixmp documentation <ixmp:index>`, which is cross-linked from many places in the |MESSAGEix| documentation.

.. autosummary::

   ~ixmp.Platform
   ~ixmp.TimeSeries
   ~ixmp.Scenario

:mod:`ixmp` also provides some utility classes and methods:

.. autosummary::

   ixmp.config.Config
   ixmp.model.MODELS
   ixmp.model.get_model
   ixmp.testing.make_dantzig


.. currentmodule:: message_ix

``message_ix`` package
----------------------

|MESSAGEix| models are created using the :py:class:`message_ix.Scenario` class. Several utility methods are also provided in the module :py:mod:`message_ix.utils`.

.. automodule:: message_ix
   :members: Scenario


Model classes
-------------

.. currentmodule:: message_ix.models

.. automodule:: message_ix.models
   :exclude-members: MESSAGE, MESSAGE_MACRO

.. autodata:: DEFAULT_CPLEX_OPTIONS

   These configure the GAMS CPLEX solver (or another solver, if selected); see `the solver documentation <https://www.gams.com/latest/docs/S_CPLEX.html>`_ for possible values.

.. autoclass:: MESSAGE
   :members:
   :show-inheritance:

   The MESSAGE Python class encapsulates the GAMS code for the core MESSAGE mathematical formulation.
   The *model_options* arguments are received from :meth:`.Scenario.solve`, and—except for *solve_options*—are passed on to the parent class :class:`~ixmp.model.gams.GAMSModel`; see there for a full list of options.

.. autoclass:: MESSAGE_MACRO
   :members:
   :show-inheritance:


.. _utils:

Utility methods
---------------

.. automodule:: message_ix.utils
   :members: make_df, make_ts, matching_rows, multiply_df


Testing utilities
-----------------

.. automodule:: message_ix.testing
   :members: make_dantzig, make_westeros
