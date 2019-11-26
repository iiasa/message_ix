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

   ixmp.config
   ixmp.model.MODELS
   ixmp.model.get_model
   ixmp.testing.make_dantzig


.. currentmodule:: message_ix

``message_ix`` package
----------------------

|MESSAGEix| models are created using the :py:class:`message_ix.Scenario` class. Several utility methods are also provided in the module :py:mod:`message_ix.utils`.

.. autoclass:: message_ix.Scenario
   :members:
   :show-inheritance:
   :inherited-members:

   This class extends :class:`ixmp.Scenario` and :class:`ixmp.TimeSeries` and
   inherits all their methods. Documentation of these inherited methods is
   included here for convenience. :class:`message_ix.Scenario` defines
   additional methods specific to |MESSAGEix|:

   .. autosummary::

      add_cat
      add_horizon
      add_spatial_sets
      cat
      cat_list
      equ
      firstmodelyear
      par
      read_excel
      rename
      to_excel
      var
      vintage_and_active_years
      years_active



Model classes
-------------

.. currentmodule:: message_ix.models

.. automodule:: message_ix.models
   :exclude-members: MESSAGE, MESSAGE_MACRO

.. autodata:: DEFAULT_CPLEX_OPTIONS

   These configure the GAMS CPLEX solver (or another solver, if selected); see `the solver documentation <https://www.gams.com/latest/docs/S_CPLEX.html>`_ for possible values.

.. autoclass:: MESSAGE
   :members:
   :exclude-members: defaults
   :show-inheritance:

   The MESSAGE Python class encapsulates the GAMS code for the core MESSAGE mathematical formulation.
   The *model_options* arguments are received from :meth:`.Scenario.solve`, and—except for *solve_options*—are passed on to the parent class :class:`~ixmp.model.gams.GAMSModel`; see there for a full list of options.

   .. autoattribute:: name

   .. autoattribute:: defaults
      :annotation: = dict(...)

      The paths to MESSAGE GAMS source files use the ``MODEL_PATH`` configuration setting.
      ``MODEL_PATH``, in turn, defaults to "message_ix/model" inside the directory where :mod:`message_ix` is installed.

      ================== ===
      Key                Value
      ================== ===
      MESSAGE defaults
      ----------------------
      **model_file**     ``'{MODEL_PATH}/{model_name}_run.gms'``
      **in_file**        ``'{MODEL_PATH}/data/MsgData_{case}.gdx'``
      **out_file**       ``'{MODEL_PATH}/output/MsgOutput_{case}.gdx'``
      **solve_args**     ``['--in="{in_file}"', '--out="{out_file}"', '--iter="{MODEL_PATH}/output/MsgIterationReport_{case}.gdx"']``
      ------------------ ---
      Inherited from :class:`~ixmp.model.gams.GAMSModel`
      ----------------------
      **case**           ``'{scenario.model}_{scenario.scenario}'``
      **gams_args**      ``['LogOption=4']``
      **check_solution** :obj:`True`
      **comment**        :obj:`None`
      **equ_list**       :obj:`None`
      **var_list**       :obj:`None`
      ================== ===

.. autoclass:: MESSAGE_MACRO
   :members:
   :show-inheritance:

   .. autoattribute:: name


.. _utils:

Utility methods
---------------

.. automodule:: message_ix.utils
   :members: make_df


Testing utilities
-----------------

.. automodule:: message_ix.testing
   :members: make_dantzig, make_westeros
