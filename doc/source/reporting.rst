Postprocessing and reporting
============================

.. warning::

   :mod:`message_ix.reporting` is **experimental** in message_ix 1.2 and only
   supports Python 3. The API and functionality may change without advance
   notice or a deprecation period in subsequent releases.

The |ixmp| provides powerful features to perform calculations and other postprocessing after a :class:`message_ix.Scenario` has been solved by the associated model. The |MESSAGEix| framework uses these features to provide zero-configuration reporting of models built on the framework.

These features are accessible through :class:`Reporter <message_ix.reporting.Reporter>`, which can produce multiple **reports** from one or more Scenarios. A report is identified by a **key** (usually a string), and may…

- perform arbitrarily complex calculations while intelligently handling units;
- read and make use of data that is ‘exogenous’ to (not included in) a
  Scenario;
- produce output as Python or R objects (in code), or to files or databases;
- calculate only a requested subset of quantities; and
- much, much more!


Terminology
-----------

:mod:`ixmp.reporting` handles numerical **quantities**, which are scalar (0-dimensional) or array (1 or more dimensions) data with optional associated units.
*ixmp* parameters, scalars, equations, and time-series data all become quantities for the purpose of reporting.

Every quantity and report is identified by a **key**, which is a :py:class:`str` or other :py:term:`hashable` object. Special keys are used for multidimensional quantities. For instance: the |MESSAGEix| parameter ``resource_cost``, defined with the dimensions (node `n`, commodity `c`, grade `g`, year `y`) is identified by the key ``'resource_cost:n-c-g-y'``. When summed across the grade/`g` dimension, it has dimensions `n`, `c`, `y` and is identified by the key ``'resource_cost:n-c-y'``.

Non-model [1]_ quantities and reports are produced by **computations**, which are atomic tasks that build on other computations. The most basic computations—for instance, ``resource_cost:n-c-g-y``—simply retrieve raw/unprocessed data from a :class:`message_ix.Scenario` and return it as a :class:`Quantity <ixmp.reporting.utils.Quantity>`. Advanced computations can depend on many quantities, and/or combine quantities together into a structure like a document or spreadsheet. Computations are defined in :mod:`ixmp.reporting.computations` and :mod:`message_ix.reporting.computations`, but most common computations can be added using the methods of :class:`Reporter <message_ix.reporting.Reporter>`.

.. [1] i.e. quantities that do not exist within the mathematical formulation of the model itself, and do not affect its solution.

Basic usage
-----------

A basic reporting workflow has the following steps:

1. Obtain a :class:`message_ix.Scenario` object from an :class:`ixmp.Platform`.
2. Use :meth:`from_scenario() <message_ix.reporting.Reporter.from_scenario>` to
   create a Reporter object.
3. (optionally) Use :class:`Reporter <message_ix.reporting.Reporter>` built-in
   methods or advanced features to add computations to the reporter.
4. Use :meth:`get() <ixmp.reporting.Reporter.get>` to retrieve the
   results (or trigger the effects) of one or more computations.

>>> from ixmp import Platform
>>> from message_ix import Scenario, Reporter
>>>
>>> mp = Platform()
>>> scen = Scenario(scen)
>>> rep = Reporter.from_scenario(scen)
>>> rep.get('all')

.. note:: :class:`Reporter <message_ix.reporting.Reporter>` stores defined
   computations, but these **are not executed** until :meth:`get()
   <ixmp.reporting.Reporter.get>` is called—or the results of one
   computation are required by another. This allows the Reporter to skip
   unneeded (and potentially slow) computations. A Reporter may contain computations for thousands of model quantities and derived quantities, but
   a call to :meth:`get() <ixmp.reporting.Reporter.get>` may only execute a
   few of these.


Customization
-------------

A Reporter prepared with :meth:`from_scenario()
<message_ix.reporting.Reporter.from_scenario>` always contains a key
``scenario``, referring to the Scenario to be reported.

The method :meth:`Reporter.add() <ixmp.reporting.Reporter.add>` can be used to
add *arbitrary* Python code that operates directly on the Scenario object:

>>> def my_custom_report(scenario):
>>>     """Function with custom code that manipulates the *scenario*."""
>>>     print('foo')
>>>
>>> rep.add('custom', (my_custom_report, 'scenario'))
>>> rep.get('custom')
foo

In this example, the function ``my_custom_report()`` *could* run to thousands
of lines; read to and write from multiple files; invoke other programs or
Python scripts; etc.

In order to take advantage of the performance-optimizing features of the
Reporter, however, such calculations can be instead composed from atomic (i.e.
small, indivisible) computations.


Reporters
---------

.. currentmodule:: message_ix.reporting

.. autoclass:: Reporter
   :show-inheritance:
   :members: write
   :exclude-members: as_pyam, from_scenario

   .. automethod:: from_scenario

      In addition to the keys automatically added by
      :meth:`ixmp.reporting.Reporter.from_scenario`, keys are added for
      derived quantities specific to the MESSAGEix framework, as defined in
      :obj:`PRODUCTS` and :obj:`DERIVED`.

      - ``out``: the product of ``output`` (output efficiency) and ``ACT``
        (activity).
      - ``out_hist``: ``output`` × ``ref_activity`` (historical reference
        activity),
      - ``in``:      ``input`` × ``ACT``,
      - ``in_hist``: ``input`` × ``ref_activity``,
      - ``emi``:      ``emission_factor`` × ``ACT``,
      - ``emi_hist``: ``emission_factor`` × ``ref_activity``,
      - ``inv``:      ``inv_cost`` × ``CAP_NEW``,
      - ``inv_hist``: ``inv_cost`` × ``ref_new_capacity``,
      - ``fom``:      ``fix_cost`` × ``CAP``,
      - ``fom_hist``: ``fix_cost`` × ``ref_capacity``,
      - ``vom``:      ``var_cost`` × ``ACT``, and
      - ``vom_hist``: ``var_cost`` × ``ref_activity``.
      - ``tom``: ``fom`` + ``vom``.

      .. tip:: Use :meth:`full_key` to retrieve the full-dimensionality
         :class:`Key` for these quantities.

      Other added keys include:

      - ``<name>:pyam`` for the above quantities, plus:

        - ``cap:pyam`` (from ``CAP``)
        - ``new_cap:pyam`` (from ``CAP_NEW``)

      ...according to :obj:`PYAM_CONVERT`.

      - Standard reports according to :obj:`REPORTS`.
      - The report ``message:default``, collecting all of the above reports.

   .. automethod:: message_ix.reporting.Reporter.as_pyam

      The :pyam:doc:`IAMC data format <data>` includes columns named 'Model',
      'Scenario', 'Region', 'Variable', 'Unit'; one of 'Year' or 'Time'; and
      'value'.

      Using :meth:`as_pyam` :

      - 'Model' and 'Scenario' are populated from the attributes of the
        Scenario identified by the key ``scenario``;
      - 'Variable' contains the name(s) of the `quantities`;
      - 'Unit' contains the units associated with the `quantities`; and
      - 'Year' or 'Time' is created according to `year_time_dim`.

      Additional dimensions of quantities pass through :meth:`as_pyam` and
      appear as additional columns in the resulting :class:`IamDataFrame`.
      While this is valid IAMC data, :meth:`as_pyam` also supports dropping
      additional columns (with `drop`), and a custom callback (`collapse`) that
      can be used to manipulate values along other dimensions.

      For example, here the values for the MESSAGEix ``technology`` and
      ``mode`` dimensions are appended to the 'Variable' column::

          def m_t(df):
              """Callback for collapsing ACT columns."""
              # .pop() removes the named column from the returned row
              df['variable'] = Activity + '|' + df['t'] + '|' + df['m']
              return df

          ACT = rep.full_key('ACT')
          keys = rep.as_pyam(ACT, 'ya', collapse=m_t, drop=['t', 'm'])

.. autodata:: PRODUCTS
.. autodata:: DERIVED
.. autodata:: PYAM_CONVERT
.. autodata:: REPORTS

.. automethod:: ixmp.reporting.configure

.. autoclass:: ixmp.reporting.Reporter
   :members:
   :exclude-members: graph, add

   A Reporter is used to postprocess data from from one or more
   :class:`ixmp.Scenario` objects. The :meth:`get` method can be used to:

   - Retrieve individual **quantities**. A quantity has zero or more
     dimensions and optional units. Quantities include the ‘parameters’,
     ‘variables’, ‘equations’, and ‘scalars’ available in an
     :class:`ixmp.Scenario`.

   - Generate an entire **report** composed of multiple quantities. A report
     may:

     - Read in non-model or exogenous data,
     - Trigger output to files(s) or a database, or
     - Execute user-defined methods.

   Every report and quantity (including the results of intermediate steps) is
   identified by a :class:`utils.Key`; all the keys in a Reporter can be
   listed with :meth:`keys`.

   Reporter uses a :doc:`graph <graphs>` data structure to keep track of
   **computations**, the atomic steps in postprocessing: for example, a single
   calculation that multiplies two quantities to create a third. The graph
   allows :meth:`get` to perform *only* the requested computations. Advanced
   users may manipulate the graph directly; but common reporting tasks can be
   handled by using Reporter methods:

   .. autosummary::
      add
      add_file
      aggregate
      apply
      configure
      describe
      disaggregate
      finalize
      full_key
      get
      read_config
      visualize
      write

   .. autoattribute:: graph

   .. automethod:: add

      :meth:`add` may be used to:

      - Provide an alias from one *key* to another:

        >>> r.add('aliased name', 'original name')

      - Define an arbitrarily complex computation in a Python function that
        operates directly on the :class:`ixmp.Scenario`:

        >>> def my_report(scenario):
        >>>     # many lines of code
        >>>     return 'foo'
        >>> r.add('my report', (my_report, 'scenario'))
        >>> r.finalize(scenario)
        >>> r.get('my report')
        foo

      .. note::
         Use care when adding literal :class:`str` values (2); these may
         conflict with keys that identify the results of other
         computations.


Computations
------------

.. currentmodule:: message_ix.reporting

.. automodule:: message_ix.reporting.computations
   :members: add, write_report


.. automodule:: message_ix.reporting.pyam
   :members: as_pyam, collapse_message_cols


Computations from ixmp
~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: ixmp.reporting

.. automodule:: ixmp.reporting.computations
   :members:

   .. autosummary::

      aggregate
      disaggregate_shares
      load_file
      make_dataframe
      write_report


Utilities
---------

.. autoclass:: ixmp.reporting.utils.Key
   :members:

   Quantities in a :class:`Scenario` can be indexed by one or more dimensions.
   For example, a parameter with three dimensions can be initialized with:

   >>> scenario.init_par('foo', ['a', 'b', 'c'], ['apple', 'bird', 'car'])

   Computations for this scenario might use the quantity ``foo`` in different
   ways:

   1. in its full resolution, i.e. indexed by a, b, and c;
   2. aggregated (e.g. summed) over any one dimension, e.g. aggregated over c
      and thus indexed by a and b;
   3. aggregated over any two dimensions; etc.

   A Key for (1) will hash, display, and evaluate as equal to ``'foo:a-b-c'``.
   A Key for (2) corresponds to ``'foo:a-b'``, and so forth.

   Keys may be generated concisely by defining a convenience method:

   >>> def foo(dims):
   >>>     return Key('foo', dims.split(''))
   >>> foo('a b')
   foo:a-b

.. autoclass:: ixmp.reporting.utils.AttrSeries

.. automodule:: ixmp.reporting.utils
   :members:
   :exclude-members: AttrSeries, Key, combo_partition
