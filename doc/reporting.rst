Postprocessing and reporting
****************************

The |ixmp| provides powerful features to perform calculations and other postprocessing after a :class:`message_ix.Scenario` has been solved by the associated model.
The |MESSAGEix| framework uses these features to provide zero-configuration reporting of models built on the framework.

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

API reference
=============

Top-level classes and functions
-------------------------------

:mod:`message_ix.reporting` is built on the :mod:`ixmp.reporting` and :mod:`genno` packages.
The following top-level objects from those packages may also be imported from
:mod:`message_ix.reporting`:

.. currentmodule:: message_ix.reporting

.. automodule:: message_ix.reporting

.. autosummary::

   ~ixmp.reporting.reporter.Reporter
   ~genno.config.configure
   ~genno.core.key.Key
   ~genno.core.quantity.Quantity

The :meth:`ixmp.Reporter <ixmp.reporting.Reporter.from_scenario>` automatically adds keys based on the contents of the :class:`ixmp.Scenario` argument.
The :class:`message_ix.reporting.Reporter` adds additional keys for **derived quantities** specific to the MESSAGEix model framework.
These include:

- ``out``: the product of ``output`` (output efficiency) and ``ACT`` (activity).
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

.. tip:: Use :meth:`~.full_key` to retrieve the full-dimensionality :class:`Key` for any of these quantities.

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
   :members:

.. autodata:: PRODUCTS
.. autodata:: DERIVED
.. autodata:: PYAM_CONVERT
.. autodata:: REPORTS
.. autodata:: MAPPING_SETS

Configuration
-------------

:mod:`message_ix` adds the standard short symbols for MESSAGE sets to :obj:`RENAME_DIMS`.


Computations
------------

.. automodule:: message_ix.reporting.computations
   :members:

   :mod:`message_ix.reporting` only provides two computations, which are currently only used in the tutorials to produce simple plots.
   For custom plotting, :mod:`genno.compat.plotnine` is recommended.

   .. autosummary::
      plot_cumulative
      stacked_bar

   Other computations are provided by :mod:`ixmp.reporting`:

   .. autosummary::
      ~ixmp.reporting.computations.data_for_quantity
      ~ixmp.reporting.computations.map_as_qty
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
      ~genno.computations.group_sum
      ~genno.computations.load_file
      ~genno.computations.product
      ~genno.computations.ratio
      ~genno.computations.select
      ~genno.computations.sum
      ~genno.computations.write_report


Utilities
---------

.. currentmodule:: message_ix.reporting.pyam

.. automodule:: message_ix.reporting.pyam
   :members: collapse_message_cols
