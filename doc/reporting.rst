Postprocessing and reporting
****************************

The |ixmp| provides powerful features to perform calculations and other postprocessing after a :class:`message_ix.Scenario` has been solved by the associated model. The |MESSAGEix| framework uses these features to provide zero-configuration reporting of models built on the framework.

These features are accessible through :class:`Reporter <message_ix.reporting.Reporter>`, which can produce multiple **reports** from one or more Scenarios. A report is identified by a **key** (usually a string), and may…

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


Terminology
===========

:mod:`ixmp.reporting` handles numerical **quantities**, which are scalar (0-dimensional) or array (1 or more dimensions) data with optional associated units.
*ixmp* parameters, scalars, equations, and time-series data all become quantities for the purpose of reporting.

Every quantity and report is identified by a **key**, which is a :py:class:`str` or other :py:term:`hashable` object. Special keys are used for multidimensional quantities. For instance: the |MESSAGEix| parameter ``resource_cost``, defined with the dimensions (node `n`, commodity `c`, grade `g`, year `y`) is identified by the key ``'resource_cost:n-c-g-y'``. When summed across the grade/`g` dimension, it has dimensions `n`, `c`, `y` and is identified by the key ``'resource_cost:n-c-y'``.

Non-model [1]_ quantities and reports are produced by **computations**, which are atomic tasks that build on other computations. The most basic computations—for instance, ``resource_cost:n-c-g-y``—simply retrieve raw/unprocessed data from a :class:`message_ix.Scenario` and return it as a :class:`Quantity <ixmp.reporting.utils.Quantity>`. Advanced computations can depend on many quantities, and/or combine quantities together into a structure like a document or spreadsheet. Computations are defined in :mod:`ixmp.reporting.computations` and :mod:`message_ix.reporting.computations`, but most common computations can be added using the methods of :class:`Reporter <message_ix.reporting.Reporter>`.

.. [1] i.e. quantities that do not exist within the mathematical formulation of the model itself, and do not affect its solution.


Basic usage
===========

A reporting workflow has the following steps:

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
=============

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


Reporter, Key, and Quantity classes
===================================

.. currentmodule:: message_ix.reporting

.. automodule:: message_ix.reporting

.. autosummary::

   message_ix.reporting.Reporter
   ixmp.reporting.Reporter
   ixmp.reporting.Key
   ixmp.reporting.Quantity

The :meth:`ixmp.Reporter <ixmp.reporting.Reporter.from_scenario>` automatically adds keys based on the contents of the :class:`ixmp.Scenario` argument.
The :class:`message_ix.reporting.Reporter` adds additional keys for **derived quantities** specific to the MESSAGEix model framework.
These include:

- ``out``: the product of ``output`` (output efficiency) and ``ACT``
  (activity).
- ``out_hist``     = ``output`` × ``ref_activity`` (historical reference activity),
- ``in``           = ``input`` × ``ACT``,
- ``in_hist``      = ``input`` × ``ref_activity``,
- ``emi``          = ``emission_factor`` × ``ACT``,
- ``emi_hist``     = ``emission_factor`` × ``ref_activity``,
- ``inv``          = ``inv_cost`` × ``CAP_NEW``,
- ``inv_hist``     = ``inv_cost`` × ``ref_new_capacity``,
- ``fom``          = ``fix_cost`` × ``CAP``,
- ``fom_hist``     = ``fix_cost`` × ``ref_capacity``,
- ``vom``          = ``var_cost`` × ``ACT``, and
- ``vom_hist``     = ``var_cost`` × ``ref_activity``.
- ``tom``          = ``fom`` + ``vom``.
- ``land_out``     = ``land_output`` × ``LAND``,
- ``land_use_qty`` = ``land_use`` × ``LAND``,
- ``land_emi``     = ``land_emission`` × ``LAND``,
- ``addon conversion``, the model parameter ``addon_conversion`` (note space versus underscore), except broadcast across individual add-on technologies (``ta``) rather than add-on types (``type_addon``),
- ``addon up``, which is ``addon_up`` similarly broadcast.,
- ``addon ACT``    = ``addon conversion`` × ``ACT``,
- ``addon in``     = ``input`` × ``addon ACT``,
- ``addon out``    = ``output`` × ``addon ACT``, and
- ``addon potential`` = ``addon up`` × ``addon ACT``, the maximum potential activity by add-on technology.
- ``price emission``, the model variable ``PRICE_EMISSION`` broadcast across emission species (``e``) *and* technologies (``t``) rather than types (``type_emission``, ``type_tec``).

.. tip:: Use :meth:`~.full_key` to retrieve the full-dimensionality
   :class:`Key` for any of these quantities.

Other added keys include:

- ``<name>:pyam`` for the above quantities, plus:

  - ``CAP:pyam`` (from ``CAP``)
  - ``CAP_NEW:pyam`` (from ``CAP_NEW``)

  These keys return the values in the IAMC data format, as :mod:`pyam` objects.

- ``map_<name>`` as 'indicator' quantities for the mapping sets ``cat_<name>``.
- Standard reports ``message:system``, ``message_costs``, and
  ``message:emissions``.
- The report ``message:default``, collecting all of the above reports.

These automatic features of :class:`~message_ix.reporting.Reporter` are controlled by:

.. autosummary::

   PRODUCTS
   DERIVED
   MAPPING_SETS
   PYAM_CONVERT
   REPORTS

.. autoclass:: Reporter
   :show-inheritance:
   :members: write
   :exclude-members: add_as_pyam

   .. automethod:: convert_pyam

      The :pyam:doc:`IAMC data format <data>` includes columns named 'Model',
      'Scenario', 'Region', 'Variable', 'Unit'; one of 'Year' or 'Time'; and
      'value'.

      Using :meth:`convert_pyam`:

      - 'Model' and 'Scenario' are populated from the attributes of the
        Scenario returned by the Reporter key ``scenario``;
      - 'Variable' contains the name(s) of the `quantities`;
      - 'Unit' contains the units associated with the `quantities`; and
      - 'Year' or 'Time' is created according to `year_time_dim`.

      A callback function (`collapse`) can be supplied that modifies the data before it is converted to an :class:`~pyam.IamDataFrame`; for instance, to concatenate extra dimensions into the 'Variable' column.
      Other dimensions can simply be dropped (with `drop`).
      Dimensions that are not collapsed or dropped will appear as additional columns in the resulting :class:`~pyam.IamDataFrame`; this is valid, but non-standard IAMC data.

      For example, here the values for the MESSAGEix ``technology`` and ``mode`` dimensions are appended to the 'Variable' column::

          def m_t(df):
              """Callback for collapsing ACT columns."""
              # .pop() removes the named column from the returned row
              df['variable'] = 'Activity|' + df['t'] + '|' + df['m']
              return df

          ACT = rep.full_key('ACT')
          keys = rep.convert_pyam(ACT, 'ya', collapse=m_t, drop=['t', 'm'])

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
      add_product
      aggregate
      apply
      check_keys
      configure
      describe
      disaggregate
      finalize
      full_key
      get
      keys
      set_filters
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


.. autoclass:: ixmp.reporting.Key
   :members:

   Quantities in a :class:`Scenario` can be indexed by one or more dimensions.
   Keys **refer** to quantities, using three components:

   1. a string :attr:`name`,
   2. zero or more ordered dimensions :attr:`dims`, and
   3. an optional :attr:`tag`.

   For example, an ixmp parameter with three dimensions can be initialized
   with:

   >>> scenario.init_par('foo', ['a', 'b', 'c'], ['apple', 'bird', 'car'])

   Key allows a specific, explicit reference to various forms of “foo”:

   - in its full resolution, i.e. indexed by a, b, and c:

     >>> k1 = Key('foo', ['a', 'b', 'c'])
     >>> k1
     <foo:a-b-c>

   - in a partial sum over one dimension, e.g. summed across dimension c, with  remaining dimensions a and b:

     >>> k2 = k1.drop('c')
     >>> k2
     <foo:a-b>

   - in a partial sum over multiple dimensions, etc.:

     >>> k1.drop('a', 'c') == k2.drop('a') == 'foo:b'
     True

   - after it has been manipulated by different reporting computations, e.g.

     >>> k3 = k1.add_tag('normalized')
     >>> k3
     <foo:a-b-c:normalized>
     >>> k4 = k3.add_tag('rescaled')
     >>> k4
     <foo:a-b-c:normalized+rescaled>

   **Notes:**

   A Key has the same hash, and compares equal to its :class:`str` representation.
   ``repr(key)`` prints the Key in angle brackets ('<>') to signify that it is a Key object.

   >>> str(k1)
   'foo:a-b-c'
   >>> repr(k1)
   '<foo:a-b-c>'
   >>> hash(k1) == hash('foo:a-b-c')
   True

   Keys are **immutable**: the properties :attr:`name`, :attr:`dims`, and :attr:`tag` are *read-only*, and the methods :meth:`append`, :meth:`drop`, and :meth:`add_tag` return *new* Key objects.

   Keys may be generated concisely by defining a convenience method:

   >>> def foo(dims):
   >>>     return Key('foo', dims.split())
   >>> foo('a b c')
   <foo:a-b-c>


.. autodata:: ixmp.reporting.Quantity(data, *args, **kwargs)
   :annotation:

The :data:`.Quantity` constructor converts its arguments to an internal, :class:`xarray.DataArray`-like data format:

.. code-block:: python

   # Existing data
   data = pd.Series(...)

   # Convert to a Quantity for use in reporting calculations
   qty = Quantity(data, name="Quantity name", units="kg")
   rep.add("new_qty", qty)


Computations
============

Defined by :mod:`message_ix`
----------------------------

.. currentmodule:: message_ix.reporting

.. automodule:: message_ix.reporting.computations
   :members: as_pyam, broadcast_map, concat, map_as_qty, stacked_bar, write_report

Inherited from ixmp
-------------------

.. currentmodule:: ixmp.reporting

.. automodule:: ixmp.reporting.computations
   :members:

   Unless otherwise specified, these methods accept and return
   :class:`Quantity <ixmp.reporting.utils.Quantity>` objects for data
   arguments/return values.

   Calculations:

   .. autosummary::
      add
      aggregate
      apply_units
      disaggregate_shares
      product
      ratio
      select
      sum

   Input and output:

   .. autosummary::
      load_file
      write_report

   Data manipulation:

   .. autosummary::
      concat


Configuration
=============

.. autosummary::

   ixmp.reporting.configure
   ixmp.reporting.utils.RENAME_DIMS
   ixmp.reporting.utils.REPLACE_UNITS

.. automethod:: ixmp.reporting.configure

.. currentmodule:: message_ix.reporting

.. autodata:: PRODUCTS
.. autodata:: DERIVED
.. autodata:: PYAM_CONVERT
.. autodata:: REPORTS
.. autodata:: MAPPING_SETS

.. currentmodule:: ixmp.reporting.utils

.. autodata:: RENAME_DIMS

   :mod:`message_ix` adds the standard short symbols for MESSAGE sets to this
   variable.

.. autodata:: REPLACE_UNITS


Utilities
=========

.. currentmodule:: ixmp.reporting.quantity

.. automodule:: ixmp.reporting.quantity
   :members: assert_quantity


.. automodule:: ixmp.reporting.utils
   :members:
   :exclude-members: RENAME_DIMS, REPLACE_UNITS

.. automodule:: message_ix.reporting.pyam
   :members: collapse_message_cols
