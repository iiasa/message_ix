Postprocessing and reporting
============================

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

Non-model quantities and reports are produced by **computations**, which are atomic tasks that build on other computations. The most basic computations—for instance, ``resource_cost:n-c-g-y``—simply return raw/unprocessed quantities from a :class:`message_ix.Scenario`. Advanced computations can depend on many quantities, and combine them together into a structure like a document or spreadsheet. Computations are defined in :mod:`ixmp.reporting.computations` and [eventually…] ``message_ix.reporting.computations``, but most common computations can be added using the methods of :class:`Reporter <message_ix.reporting.Reporter>`.

Basic usage
-----------

>>> from ixmp import Platform
>>> from message_ix import Scenario, Reporter
>>>
>>> mp = Platform()
>>> scen = Scenario(scen)
>>> rep = Reporter.from_scenario(scen)
>>> rep.get('all')

Advanced usage
--------------

>>> def my_custom_report(scenario):
>>>     """Function with custom code that manipulates the *scenario*."""
>>>     print('foo')
>>>
>>> rep.add('custom', (my_custom_report, 'scenario'))
>>> rep.get('custom')
foo

Reporters
---------

.. autoclass:: message_ix.reporting.Reporter
   :show-inheritance:
   :members:

.. autoclass:: ixmp.reporting.Reporter
   :members:


Computations
------------

.. currentmodule:: ixmp.reporting.computations

.. autosummary::

   aggregate
   disaggregate_shares
   load_file
   make_dataframe
   write_report

.. automodule:: ixmp.reporting.computations
   :members:
