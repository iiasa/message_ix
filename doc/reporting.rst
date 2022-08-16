Postprocessing and reporting
****************************

The |MESSAGEix| framework provides zero-configuration **reporting** of models built on the framework.
The word “reporting” refers to calculations and other post-processing performed *after* a :class:`.Scenario` has been solved by the associated optimization model: first the model solution is obtained, and then things are “reported” based on that solution.

:mod:`message_ix.reporting` is developed on the basis of :mod:`ixmp.reporting` and :mod:`genno`.
It provides a basis for other code and packages—such as :mod:`message_ix_models`—that perform reporting calculations tailored to specific model structures.
Each layer of this “stack” builds on the features in the level below:

.. list-table::
   :header-rows: 1

   * - Package
     - Role
     - Core features
     - Reporting features
   * - ``message_ix_models``
     - MESSAGEix-GLOBIOM models
     - Specific model structure (``coal_ppl`` in ``t``)
     - Calculations for specific technologies
   * - ``message_ix``
     - Energy model framework
     - Common sets/parameters (``output``)
     - Derived quantities (``tom``)
   * - ``ixmp``
     - Optimization models & data
     - :class:`~ixmp.Scenario` with sets, parameters, variables
     - :class:`~ixmp.Reporter` auto-populated with sets etc.
   * - ``genno``
     - Structured calculations
     - :class:`~genno.Computer`,
       :class:`~genno.Key`,
       :class:`~genno.Quantity`
     - —

These features are accessible through :class:`.Reporter`, which can produce multiple **reports** from one or more Scenarios.
A report is identified by a **key** (usually a string), and may…

- perform arbitrarily complex calculations while intelligently handling units;
- read and make use of data that is ‘exogenous’ to (not included in) a
  Scenario;
- produce output as Python or R objects (in code), or to files or databases;
- calculate only a requested subset of quantities; and
- much, much more!

Contents:

.. contents::
   :local:
   :depth: 3


Concepts
========

See :doc:`genno:usage` in the genno documentation for an introduction to concepts including **quantity**, **key**, **computation**, **task**, and **graph**.
In :mod:`message_ix.reporting`:

- The :class:`.message_ix.Reporter` class is an extended version of the :class:`genno.Computer` class.
- :mod:`ixmp` parameters, scalars, equations, and time-series data all become quantities for the purpose of reporting.
- For example, the |MESSAGEix| parameter ``resource_cost``, defined with the dimensions (node `n`, commodity `c`, grade `g`, year `y`) is identified by the key ``resource_cost:n-c-g-y``.
  When summed across the grade/`g` dimension, it has dimensions `n`, `c`, `y` and is identified by the key ``resource_cost:n-c-y``.
- :meth:`.Reporter.from_scenario` automatically sets up keys and tasks (such as ``resource_cost:n-c-g-y``) that simply retrieve raw/unprocessed data from a :class:`~message_ix.Scenario` and return it as a :any:`genno.Quantity`.
- Computations are defined as functions in modules including:
  :mod:`message_ix.reporting.computations`,
  :mod:`ixmp.reporting.computations`, and
  :mod:`genno.computations`.
  These are documented below.

Usage
=====

A |MESSAGEix| reporting workflow has the following steps:

1. Obtain a :class:`.Scenario` object from an :class:`.Platform`.
2. Use :meth:`.Reporter.from_scenario` to prepare a Reporter object with many calculations automatically prepared.
3. (optionally) Use the built-in features of :class:`.Reporter` to describe additional calculations.
4. Use :meth:`.get` 1 or more times to execute tasks, including all the calculations on which they depend:

.. code-block:: python

    from ixmp import Platform
    from message_ix import Scenario, Reporter

    mp = Platform()
    scen = Scenario(scen)
    rep = Reporter.from_scenario(scen)
    rep.get("all")

Note that keys and tasks are **described** in steps (2–3), but they are not **executed** until :meth:`.get` is called—or the results of one task are required by another.
This design allows the Reporter to skip unneeded (and potentially slow) computations and deliver good performance.
The Reporter's :attr:`Computer.graph` may contain thousands of tasks for retrieving model quantities and calculating derived quantities, but a particular call to :meth:`.get` may only execute a few of these.


Customization
=============

A Reporter prepared with :meth:`.from_scenario` always contains a key
``scenario``, referring to the Scenario to be reported.

The method :meth:`.Reporter.add` can be used to add *arbitrary* Python code that operates directly on the Scenario object:

.. code-block:: python

    def my_custom_report(scenario):
        """Function with custom code that manipulates the `scenario`."""
        print("Model name:", scenario.model)

    # Add a task at the key "custom". The task executes my_custom_report().
    # The key "scenario" means that the Scenario object is retrieved and
    # passed as an argument to the function.
    rep.add("custom", (my_custom_report, "scenario"))
    rep.get("custom")

In this example, the function ``my_custom_report()`` *could* run to thousands of lines; read to and write from multiple files; invoke other programs or Python scripts; etc.
In order to take advantage of the performance-optimizing features of the Reporter, such calculations can instead be composed from atomic (i.e. small, indivisible) computations.
See the :mod:`genno` documentation for more.

API reference
=============

.. currentmodule:: message_ix.reporting

.. automodule:: message_ix.reporting

Top-level classes and functions
-------------------------------

:mod:`message_ix.reporting` provides:

.. autosummary::

   Reporter

The following objects from :mod:`genno` may also be imported from :mod:`message_ix.reporting`.
Their documentation is repeated below for convenience.

.. autosummary::

   ComputationError
   Key
   KeyExistsError
   MissingKeyError
   Quantity
   configure


:meth:`ixmp.Reporter.from_scenario <ixmp.reporting.Reporter.from_scenario>` automatically adds keys based on the contents of the :class:`.Scenario` argument.
:meth:`message_ix.Reporter.from_scenario <.Reporter.from_scenario>` extends this to add additional keys for derived quantities specific to the MESSAGEix model framework.
These include:

- ``out`` - ``output`` × ``ACT``; that is, the product of ``output`` (output efficiency) and ``ACT`` (activity)
- ``out_hist``     = ``output`` × ``ref_activity`` (historical reference activity)
- ``in``           = ``input`` × ``ACT``
- ``in_hist``      = ``input`` × ``ref_activity``
- ``emi``          = ``emission_factor`` × ``ACT``
- ``emi_hist``     = ``emission_factor`` × ``ref_activity``
- ``inv``          = ``inv_cost`` × ``CAP_NEW``
- ``inv_hist``     = ``inv_cost`` × ``ref_new_capacity``
- ``fom``          = ``fix_cost`` × ``CAP``
- ``fom_hist``     = ``fix_cost`` × ``ref_capacity``
- ``vom``          = ``var_cost`` × ``ACT``
- ``vom_hist``     = ``var_cost`` × ``ref_activity``
- ``tom``          = ``fom`` + ``vom``
- ``land_out``     = ``land_output`` × ``LAND``
- ``land_use_qty`` = ``land_use`` × ``LAND``
- ``land_emi``     = ``land_emission`` × ``LAND``
- ``addon conversion``, the model parameter ``addon_conversion`` (note space versus underscore), except broadcast across individual add-on technologies (`ta`) rather than add-on types (`type_addon`).
- ``addon up``, which is ``addon_up`` similarly broadcast.
- ``addon ACT``    = ``addon conversion`` × ``ACT``
- ``addon in``     = ``input`` × ``addon ACT``
- ``addon out``    = ``output`` × ``addon ACT``
- ``addon potential`` = ``addon up`` × ``addon ACT``, the maximum potential activity by add-on technology.
- ``price emission``, the model variable ``PRICE_EMISSION`` broadcast across emission species (`e`) *and* technologies (`t`) rather than types (`type_emission`, `type_tec`).

.. tip:: Use :meth:`~.Computer.full_key` to retrieve the full-dimensionality :class:`Key` for any of these quantities.

Other added keys include:

- :mod:`message_ix` adds the standard short symbols for |MESSAGEix| dimensions (sets) based on :data:`DIMS`.
  Each of these is also available in a Reporter: for example ``rep.get("n")`` returns a list with the elements of the |MESSAGEix| set named "node".
  These keys can be used as input

.. _default-reports:

- Computations to convert internal :func:`Quantity` data format to the IAMC data format, i.e. as :class:`pyam.IamDataFrame` objects.
  These include:

  - ``<name>::pyam`` for most of the above derived quantities.
  - ``CAP::pyam`` (from ``CAP``)
  - ``CAP_NEW::pyam`` (from ``CAP_NEW``)

- ``map_<name>`` as "one-hot" or indicator quantities for the respective |MESSAGEix| mapping sets ``cat_<name>``.
- Standard reports ``message::system``, ``message::costs``, and ``message::emissions`` per :data:`REPORTS`.
- The report ``message::default``, collecting all of the above reports.

These automatic contents are prepared using:

.. autosummary::

   DERIVED
   DIMS
   MAPPING_SETS
   PRODUCTS
   PYAM_CONVERT
   REPORTS

.. autoclass:: Reporter
   :show-inheritance:
   :members:
   :inherited-members:

   .. autosummary::
      add
      add_file
      add_product
      add_queue
      add_single
      aggregate
      apply
      check_keys
      configure
      convert_pyam
      describe
      disaggregate
      finalize
      from_scenario
      full_key
      get
      infer_keys
      keys
      set_filters
      visualize
      write


.. autodata:: DERIVED
.. autodata:: DIMS
.. autodata:: MAPPING_SETS
.. autodata:: PRODUCTS
.. autodata:: PYAM_CONVERT
.. autodata:: REPORTS

.. automodule:: message_ix.reporting
   :noindex:
   :members: ComputationError, Key, KeyExistsError, MissingKeyError, Quantity, configure


Computations
------------

.. automodule:: message_ix.reporting.computations
   :members:

   :mod:`message_ix.reporting` provides a small number of computations.
   Two of these (:func:`.plot_cumulative` and :func:`.stacked_bar`) are currently only used in the tutorials to produce simple plots; for more flexible plotting, :mod:`genno.compat.plotnine` is recommended instead.

   .. autosummary::
      as_message_df
      plot_cumulative
      stacked_bar

   Other computations are provided by :mod:`ixmp.reporting`:

   .. autosummary::
      ~ixmp.reporting.computations.data_for_quantity
      ~ixmp.reporting.computations.map_as_qty
      ~ixmp.reporting.computations.store_ts
      ~ixmp.reporting.computations.update_scenario

   …and by :mod:`genno.computation` and its compatibility modules. See the package documentation for details.

   .. autosummary::
      ~genno.compat.plotnine.Plot
      ~genno.computations.add
      ~genno.computations.aggregate
      ~genno.computations.apply_units
      ~genno.compat.pyam.computations.as_pyam
      ~genno.computations.broadcast_map
      ~genno.computations.combine
      ~genno.computations.concat
      ~genno.computations.disaggregate_shares
      ~genno.computations.div
      ~genno.computations.group_sum
      ~genno.computations.index_to
      ~genno.computations.interpolate
      ~genno.computations.load_file
      ~genno.computations.mul
      ~genno.computations.pow
      ~genno.computations.ratio
      ~genno.computations.relabel
      ~genno.computations.rename_dims
      ~genno.computations.select
      ~genno.computations.sum
      ~genno.computations.write_report


Utilities
---------

.. currentmodule:: message_ix.reporting.pyam

.. automodule:: message_ix.reporting.pyam
   :members: collapse_message_cols
