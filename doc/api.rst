Python API
==========

The application programming interface (API) for |MESSAGEix| model developers is implemented in Python.
The full API is also available from R; see :doc:`rmessageix`.

.. contents::
   :local:


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

.. automodule:: message_ix

``message_ix`` package
----------------------

|MESSAGEix| models are created using the :py:class:`message_ix.Scenario` class. Several utility methods are also provided in the module :py:mod:`message_ix.util`.

.. autoclass:: message_ix.Scenario
   :members:
   :exclude-members: add_macro
   :show-inheritance:
   :inherited-members:

   This class extends :class:`ixmp.Scenario` and :class:`ixmp.TimeSeries` and inherits of the methods of those classes, shown below.
   :class:`message_ix.Scenario` adds or overrides the following methods specific to |MESSAGEix|:

   .. autosummary::

      add_cat
      add_horizon
      add_macro
      add_spatial_sets
      cat
      cat_list
      clone
      equ
      firstmodelyear
      par
      rename
      set
      solve
      var
      vintage_and_active_years
      y0
      years_active
      ya
      yv_ya

   Inherited from :class:`.ixmp.Scenario`:

   .. versionchanged:: 3.0

      :meth:`.read_excel` and :meth:`.to_excel` are now methods of :class:`ixmp.Scenario`, but continue to work with message_ix.Scenario.

   .. autosummary::

      add_par
      add_set
      change_scalar
      has_item
      has_solution
      idx_names
      idx_sets
      init_item
      init_scalar
      items
      list_items
      load_scenario_data
      read_excel
      remove_par
      remove_set
      remove_solution
      scalar
      to_excel

   Inherited from :class:`.ixmp.TimeSeries`:

   .. autosummary::

      add_geodata
      add_timeseries
      check_out
      commit
      discard_changes
      get_geodata
      get_meta
      is_default
      last_update
      preload_timeseries
      read_file
      remove_geodata
      remove_timeseries
      run_id
      set_as_default
      set_meta
      timeseries
      transact
      url

   .. automethod:: add_macro

      .. warning:: MACRO support via :meth:`add_macro` is **experimental** in message_ix 3.0 and may not function as expected on all possible |MESSAGEix| models.
         See `a list of known and pending issues <https://github.com/iiasa/message_ix/issues?q=is%3Aissue+is%3Aopen+label%3Amacro>`_ on GitHub.


Model classes
-------------

.. currentmodule:: message_ix.models

.. autosummary::

   MESSAGE
   MACRO
   MESSAGE_MACRO
   GAMSModel
   DEFAULT_CPLEX_OPTIONS
   Item
   ItemType

.. autodata:: DEFAULT_CPLEX_OPTIONS

   These configure the GAMS CPLEX solver (or another solver, if selected); see `the solver documentation <https://www.gams.com/latest/docs/S_CPLEX.html>`_ for possible values.

.. autoclass:: GAMSModel
   :members:
   :exclude-members: defaults

   The :class:`.MESSAGE`, :class:`MACRO`, and :class:`MESSAGE_MACRO` child classes encapsulate the GAMS code for the core MESSAGE (or MACRO) mathematical formulation.

   The class receives `model_options` via :meth:`.Scenario.solve`. Some of these are passed on to the parent class :class:`ixmp.model.gams.GAMSModel` (see there for a list); others are handled as described below.

   The “model_dir” option may be set in the user's :ref:`ixmp configuration file <ixmp:configuration>` using the key “message model dir”.
   If not set, it defaults to “message_ix/model” below the directory where :mod:`message_ix` is installed.

   The “solve_options” option may be set in the user's ixmp configuration file using the key “message solve options”.
   If not set, it defaults to :data:`.DEFAULT_CPLEX_OPTIONS`.

   For example, with the following configuration file:

   .. code-block:: yaml

      {
        "platform": {
          "default": "my-platform",
          "my-platform": {"backend": "jdbc", "etc": "etc"},
        },
        "message model dir": "/path/to/custom/gams/source/files",
        "message solve options": {"lpmethod": 4},
      }

   The following are equivalent:

   .. code-block:: python

      # Model options given explicitly
      scen.solve(
          model_dir="/path/to/custom/gams/source/files",
          solve_options=dict(lpmethod=4),
      )

      # Model options are read from configuration file
      scen.solve()

   GDX input and output files generated using this class will contain a 2-dimensional set named ``ixmp_version``, wherein the first element of each member is a package name from the :py:`record_version_packages` parameter, and the second is its version according to :func:`importlib.metadata.version`.
   If the package is not installed, the string "(not installed)" is stored.

   The following tables list all model options:

   .. list-table:: Options in :class:`message_ix.models.GAMSModel` or overridden from :mod:`ixmp`
      :widths: 20 40 40
      :header-rows: 1

      * - Option
        - Usage
        - Default value
      * - **model_dir**
        - Path to GAMS source files.
        - See above.
      * - **model_file**
        - Path to GAMS source file.
        - :py:`"{model_dir}/{model_name}_run.gms"`
      * - **in_file**
        - Path to write GDX input file.
        - :py:`"{model_dir}/data/MsgData_{case}.gdx"`
      * - **out_file**
        - Path to read GDX output file.
        - :py:`"{model_dir}/output/MsgOutput_{case}.gdx"`
      * - **solve_args**
        - Arguments passed directly to GAMS.
        - .. code-block:: python

             [
                 '--in="{in_file}"',
                 '--out="{out_file}"',
                 '--iter="{model_dir}/output/MsgIterationReport_{case}.gdx"'
             ]
      * - **solve_options**
        - Options for the GAMS LP solver.
        - :data:`.DEFAULT_CPLEX_OPTIONS`
      * - **record_version_packages**
        - Python package versions to record.
        - :py:`["message_ix", "ixmp"]`

   .. list-table:: Option defaults inherited from :class:`ixmp.model.gams.GAMSModel`
      :widths: 20 80
      :header-rows: 1

      * - Option
        - Default value
      * - **case**
        - :py:`"{scenario.model}_{scenario.scenario}"`
      * - **gams_args**
        - :py:`["LogOption=4"]`
      * - **check_solution**
        - :obj:`True`
      * - **comment**
        - :obj:`None`
      * - **equ_list**
        - :obj:`None`
      * - **var_list**
        - :obj:`None`

.. autoclass:: MESSAGE
   :members: initialize
   :exclude-members: defaults
   :show-inheritance:

   .. autoattribute:: items
      :no-value:

      Keys are the names of items (sets, parameters, variables, and equations); values are :class:`.Item` instances.
      These include all items listed in the MESSAGE mathematical specification, i.e. :ref:`sets_maps_def` and :ref:`parameter_def`.

.. autoclass:: MACRO
   :members:
   :exclude-members: items
   :show-inheritance:

   The MACRO class solves only the MACRO model in “standalone” mode—that is, without MESSAGE.
   It is also invoked from :class:`.MESSAGE_MACRO` to process *model_options* to control the behaviour of MACRO:

   - **concurrent** (:class:`int` or :class:`float`, either :py:`0` or :py:`1`).
     This corresponds to the GAMS compile-time variable ``MACRO_CONCURRENT``.
     If set to :py:`0` (the default), MACRO is solved in a loop, once for each node in the Scenario.
     If set to :py:`1`, MACRO is solved only once, for all nodes simultaneously.

   .. autoattribute:: items
      :no-value:

.. autoclass:: MESSAGE_MACRO
   :members:
   :exclude-members: items
   :show-inheritance:

   MESSAGE_MACRO solves the MESSAGE and MACRO models iteratively, connecting changes in technology activity and resource demands (from MESSAGE) to changes in final demands and prices (from MACRO).
   This iteration continues until the solution *converges*; i.e. the two models reach a stable point for the values of these parameters.

   MESSAGE_MACRO accepts three additional *model_options* that control the behaviour of this iteration algorithm:

   - **max_adjustment** (:class:`float`, default 0.2): the maximum absolute relative change in final demands between iterations.
     If MACRO returns demands that have changed by more than a factor outside the range (1 - `max_adjustment`, 1 + `max_adjustment`) since the previous iteration, then the change is confined to the limits of that range for the next run of MESSAGE.
   - **convergence_criterion** (:class:`float`, default 0.01): threshold for model convergence.
     This option applies to the same value as `max_adjustment`: the relative change in final demands between two iterations.
     If the absolute relative change is less than `convergence_criterion`, the linked model run is complete.
   - **max_iteration** (:class:`int`, default 50): the maximum number of iterations between the two models.
     If the solution does not converge after this many iterations, the linked model run fails and no valid result is produced.

   .. seealso:: :meth:`.Scenario.add_macro`

   .. autoattribute:: items
      :no-value:

.. autodata:: DIMS
.. autoclass:: Item
   :members:

.. currentmodule:: message_ix.macro

.. _utils:

Utility methods
---------------

.. automodule:: message_ix.util
   :members: expand_dims, copy_model, make_df

.. automodule:: message_ix.util.sankey
   :members: map_for_sankey

Testing utilities
-----------------

.. automodule:: message_ix.testing
   :members: make_austria, make_dantzig, make_westeros, tmp_model_dir

.. automodule:: message_ix.testing.nightly
   :members:
