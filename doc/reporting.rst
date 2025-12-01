Postprocessing and reporting
****************************

The |MESSAGEix| framework provides zero-configuration **reporting** of models built on the framework.
The word “reporting” refers to calculations and other post-processing performed *after* a :class:`.Scenario` has been solved by the associated optimization model: first the model solution is obtained, and then things are “reported” based on that solution.

:mod:`message_ix.report` is developed on the basis of :mod:`ixmp.report` and :mod:`genno`.
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
     - MESSAGE-specific sets/parameters (``output``)
     - Derived quantities (``tom``)
   * - ``ixmp``
     - Optimization models & data
     - :class:`~ixmp.Scenario` with sets, parameters, variables
     - :class:`~ixmp.report.Reporter` auto-populated with sets etc.
   * - ``genno``
     - Structured calculations
     - :class:`~genno.Computer`,
       :class:`~genno.Key`,
       :class:`~genno.Quantity`
     - —

These features are accessible through :class:`.Reporter`, which can produce multiple **reports** from one or more Scenarios.
A report and the quantities that enter it is identified by a **key**, and may…

- perform arbitrarily complex calculations, handling dimensionality and units;
- read and make use of data that is ‘exogenous’ to (not included in) a Scenario;
- produce output as Python or R objects (in code), or write to files or databases;
- calculate only a requested subset of quantities; and
- much, much more!

Contents:

.. contents::
   :local:
   :depth: 3


Concepts
========

See :doc:`genno:usage` in the genno documentation for an introduction to concepts including **quantity**, **key**, **computation**, **task**, **graph**, and **operator**.
In :mod:`message_ix.report`:

- The :class:`.Reporter` class is an extended version of the :class:`genno.Computer` class.
- :mod:`ixmp` parameters, scalars, equations, and time-series data
  all become ‘quantities’ for the purpose of reporting.
- For example, the |MESSAGEix| parameter ``resource_cost``
  defined with the dimensions (node `n`, commodity `c`, grade `g`, year `y`)
  is identified by the key ``resource_cost:n-c-g-y``.
  When summed across the grade/`g` dimension, it has dimensions `n`, `c`, `y`
  and is identified by the key ``resource_cost:n-c-y``.
- :meth:`.Reporter.from_scenario` automatically sets up keys and tasks
  (such as ``resource_cost:n-c-g-y``) that simply retrieve raw/unprocessed data from a :class:`~message_ix.Scenario`
  and return it as a :any:`genno.Quantity`.
- Operators are defined as functions in modules including:
  :mod:`message_ix.report.operator`,
  :mod:`ixmp.report.operator`, and
  :mod:`genno.operator`.
  These are documented below.

Usage
=====

A |MESSAGEix| reporting workflow has the following steps:

1. Obtain a :class:`.Scenario` object from a :class:`~ixmp.Platform`.
2. Use :meth:`.Reporter.from_scenario` to prepare a Reporter object
   with many calculations automatically prepared.
   See below.
3. (optionally) Use the built-in features of :class:`.Reporter`
   to describe additional calculations.
4. Use :meth:`.get` 1 or more times to execute tasks,
   including all the calculations on which they depend:

.. code-block:: python

    from ixmp import Platform
    from message_ix import Scenario, Reporter

    mp = Platform()
    scen = Scenario(scen)
    rep = Reporter.from_scenario(scen)
    rep.get("all")

Note that keys and tasks are **described** in steps (2–3), but they are not **executed** until :meth:`.get` is called—or the results of one task are required by another.
This design allows the Reporter to skip unneeded (and potentially slow)
tasks and re-use intermediate results to deliver good performance.
The Reporter's :attr:`~genno.Computer.graph` may contain thousands of tasks for retrieving model quantities and calculating derived quantities, but a particular call to :meth:`.get` may only execute a few of these.

.. _reporter-default:

Default reporter contents
-------------------------

:meth:`message_ix.Reporter.from_scenario <.Reporter.from_scenario>`
returns a new Reporter instance pre-filled with many keys and tasks
based on the contents of the :class:`.Scenario` argument.

These include the contents added by 
:meth:`ixmp.Reporter.from_scenario <ixmp.report.Reporter.from_scenario>`
—that is, every :mod:`ixmp` set, parameter, variable, and equation available
in the Scenario—
plus additional keys for derived quantities specific to the MESSAGE model structure.
These automatic contents are prepared using:

.. autosummary::

   ~message_ix.report.TASKS0
   ~message_ix.report.PYAM_CONVERT
   ~message_ix.report.TASKS1
   ~message_ix.report.get_tasks

…and include the following:

Sets
   - Keys matching the standard short symbols for |MESSAGEix| sets/dimensions,
     according to  :data:`.common.DIMS`.
     Thus for instance:

     .. code-block:: python

        rep.get("n")

     …returns a Python :class:`list`
     with the elements of the |MESSAGEix| set named "node".
     These lists can be used as input to other tasks,
     or to construct data structures for indexing, aggregation, and other operators.
   - ``y0``: the ``firstmodelyear`` or :math:`y_0` (:class:`int`).
   - ``y::model``, :class:`list` of :class:`int`:
     only the periods in the `year` set (``y``/:math:`Y`)
     that are equal to or greater than ``y0``.
   - ``map_<name>``: "one-hot" or indicator quantities
     for the respective |MESSAGEix| mapping sets ``cat_<name>``.

Model solution data
   The following quantities combine |MESSAGEix| parameter data (exogenous)
   and variable data (endogenous; the optimal solution to the MESSAGE linear program)
   in commonly-used ways.

   Each is available in its full dimensionality
   (the union of the dimensions of its operands)
   and as partial sums over all combinations of 1 or more dimensions.
   Use :meth:`~genno.Computer.full_key` to retrieve the full-dimensionality
   :class:`~genno.Key` for any of these quantities.

   - ``in``              = ``input`` × ``ACT``;
     that is, the product of ``input`` (input intensity) and ``ACT`` (activity).
   - ``out``             = ``output`` × ``ACT``
   - ``emi``             = ``emission_factor`` × ``ACT``
   - ``inv``             = ``inv_cost`` × ``CAP_NEW``
   - ``fom``             = ``fix_cost`` × ``CAP``.
     The name is an abbreviation for "Fixed Operation and Maintenance costs".
   - ``vom``             = ``var_cost`` × ``ACT``,
     "Variable Operation and Maintenance costs".
   - ``tom``             = ``fom`` + ``vom``,
     "Total Operation and Maintenance costs".
   - ``land_out``        = ``land_output`` × ``LAND``
   - ``land_use_qty``    = ``land_use`` × ``LAND``
   - ``land_emi``        = ``land_emission`` × ``LAND``
   - ``addon conversion``,
     the model parameter ``addon_conversion`` (note space versus underscore),
     except broadcast across individual add-on technologies (`ta`)
     rather than add-on types (`type_addon`).
   - ``addon up``, which is ``addon_up`` similarly broadcast.
   - ``addon ACT``       = ``addon conversion`` × ``ACT``
   - ``addon in``        = ``input`` × ``addon ACT``
   - ``addon out``       = ``output`` × ``addon ACT``
   - ``addon potential`` = ``addon up`` × ``addon ACT``,
     the maximum potential activity by add-on technology.
   - ``price emission``,
     the model variable ``PRICE_EMISSION``
     broadcast across emission species (`e`) *and* technologies (`t`)
     rather than types (`type_emission`, `type_tec`).

.. _reporter-historical:

Historical and reference values
   The following quantities combine |MESSAGEix| parameter data.
   Because they do not include variable data,
   they are entirely exogenous and do not depend on the model solution.
   Their names correspond to the keys above:
   for example, ``in:*:historical+current`` and ``in:*:historical+weighted``
   correspond to ``in:*``: the latter is *within* the model time horizon,
   and the former are *before* the first model period.

   - ``in:*:historical+full``  = ``input`` × ``historical_activity``.
     This is an intermediate quantity,
     and in most cases should not be used directly.
     It is used to calculate ``{…}:*:historical+current``
     and ``{…}:*:historical+weighted``. [#key-notation]_

     Similar quantities exist for ``out``, ``emi``, and ``inv``,
     with keys like ``out:*:historical+full`` etc.
   - ``in:*:historical+current``:
     The subset of ``in:*:historical+full`` where :math:`y^V = y^A`.
     Use this quantity to represent an assumption that
     *all activity in each historical period* :math:`y^A < y_0` *is attributable to
     the technology vintage constructed in the same ('current') period*.
     In other words, this uses ``input`` intensity values for :math:`(y^V=y^A, y^A)`,
     and omits/ignores values for earlier vintages  :math:`(y^V < y^A, y^A)`,
     even if the |technical_lifetime| and |historical_new_capacity| of those earlier vintages
     implies they could be active in the period |yA|.

     Similar quantities exist for ``out``, ``emi``, and ``inv``.
   - ``in:*:historical+weighted``:
     a sum of ``in:*:historical+full`` across the ``yv`` dimension,
     weighted by ``share:*:in+historical``.
     The latter quantity **must** be supplied exogenously by the user.
     This can be done by overriding the placeholder task created by
     :meth:`.from_scenario`:

     .. code-block:: python

        k = rep.full_key("share:*:in+historical")
        rep.add(k, ...)  # Some task that returns share values, e.g. from file

     ``share:*:{…}+historical`` values give the fractional contribution
     of each technology vintage :math:`y^V`
     to the ``historical_activity`` in each :math:`y^A`.
     Therefore they **should** sum to 1.0 across the ``yv`` dimension
     for each combination of other indices.

     Similar quantities exist for ``out``, ``emi``, and ``inv``.
   - ``in:*:ref+current``, ``in:*:ref+weighted``, and ``in:*:ref+full``:
     Same as above, but computed using ``ref_activity`` instead of ``historical_activity``.

     Similar quantities exist for ``out``, ``emi``, and ``inv``.

.. [#key-notation] These string representations of :class:`genno.Key` use
   an asterisk for the dimensions (such as ``name:*:tag``)
   to indicate “all dimensions for this ``name`` and ``tag``”;
   and ``{…}`` to indicate “any string”.

.. _default-reports:

Time series data (:data:`.PYAM_CONVERT`, :data:`.TASKS1`)
   Tasks that transform :class:`~genno.Quantity` with varying number of dimensions
   to the :mod:`ixmp` :ref:`structure for time-series data <ixmp:data-tsdata>`
   (also called the “IAMC data structure”),
   specifically as instances of :class:`pyam.IamDataFrame`.

   These include:

   - ``<name>::pyam`` for most of the above derived quantities.
   - ``CAP::pyam`` (from ``CAP``)
   - ``CAP_NEW::pyam`` (from ``CAP_NEW``)
   - ``message::system``, ``message::costs``, and ``message::emissions``:
     concatenation of subsets of the above time series data.
   - ``message::default``: concatenation of all of the above time series data.

Customization
-------------

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

In this example, the function ``my_custom_report()`` **may** run to thousands of lines;
read to and write from multiple files;
invoke other programs or Python scripts; etc.
In order to take advantage of the performance-optimizing features of the Reporter,
such calculations **should** instead be composed from atomic (small, indivisible) operators
or functions.
See the :mod:`genno` documentation for more.

API reference
=============

.. currentmodule:: message_ix.report

.. automodule:: message_ix.report

Top-level classes and functions
-------------------------------

:mod:`message_ix.report` provides:

.. autosummary::

   Reporter

The following objects from :mod:`genno` may also be imported from :mod:`message_ix.report`.
Their documentation is repeated below for convenience.

.. currentmodule:: genno
.. autosummary::

   ComputationError
   Key
   KeyExistsError
   MissingKeyError
   Quantity
   configure
.. currentmodule:: message_ix.report


.. autoclass:: Reporter
   :show-inheritance:
   :members:
   :inherited-members:

   .. autosummary::
      add
      add_queue
      add_sankey
      add_single
      apply
      check_keys
      configure
      describe
      eval
      finalize
      from_scenario
      full_key
      get
      infer_keys
      keys
      set_filters
      visualize
      write

   .. autosummary::
      add_file
      add_product
      aggregate
      convert_pyam
      disaggregate


.. autodata:: TASKS0
.. autodata:: PYAM_CONVERT
.. autodata:: TASKS1

.. automodule:: message_ix.report
   :noindex:
   :members: ComputationError, Key, KeyExistsError, MissingKeyError, Quantity, configure


Operators
---------

.. automodule:: message_ix.report.operator
   :members:

   :mod:`message_ix.report` provides a small number of operators.
   Two of these (:func:`.plot_cumulative` and :func:`.stacked_bar`) are currently only used in the tutorials to produce simple plots; for more flexible plotting, :mod:`genno.compat.plotnine` is recommended instead.

   .. autosummary::

      as_message_df
      model_periods
      plot_cumulative
      stacked_bar

   Other operators are provided by :mod:`ixmp.report`:

   .. autosummary::
      ~ixmp.report.operator.data_for_quantity
      ~ixmp.report.operator.from_url
      ~ixmp.report.operator.get_ts
      ~ixmp.report.operator.map_as_qty
      ~ixmp.report.operator.remove_ts
      ~ixmp.report.operator.store_ts
      ~ixmp.report.operator.update_scenario

   …and by :mod:`genno.operator` and its compatibility modules.
   See the package documentation for details.

   .. autosummary::
      ~genno.compat.plotnine.Plot
      ~genno.operator.add
      ~genno.operator.aggregate
      ~genno.operator.apply_units
      ~genno.compat.pyam.operator.as_pyam
      ~genno.operator.broadcast_map
      ~genno.operator.combine
      ~genno.operator.concat
      ~genno.operator.div
      ~genno.operator.drop_vars
      ~genno.operator.group_sum
      ~genno.operator.index_to
      ~genno.operator.interpolate
      ~genno.operator.load_file
      ~genno.operator.mul
      ~genno.operator.pow
      ~genno.operator.relabel
      ~genno.operator.rename_dims
      ~genno.operator.round
      ~genno.operator.select
      ~genno.operator.sub
      ~genno.operator.sum
      ~genno.operator.write_report

   .. autosummary::
      ~genno.operator.disaggregate_shares
      ~genno.operator.product
      ~genno.operator.ratio

Utilities
---------

.. currentmodule:: message_ix.report.pyam

.. automodule:: message_ix.report.pyam
   :members: collapse_message_cols
