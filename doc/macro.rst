Calibrate and tune MESSAGE-MACRO
********************************

“MESSAGE-MACRO” refers to the combination of MESSAGE and MACRO, run iteratively in a multi-disciplinary optimization algorithm.
This combination is activated by calling :meth:`.solve` with the argument `model='MESSAGE-MACRO'`, or using the GAMS :file:`MESSAGE-MACRO_run.gms` script directly (see :ref:`running` for details about these two methods).

.. contents::
   :local:

.. _macro-input-data:

Input data file
===============

Using :meth:`.add_macro` requires an input data file in Microsoft Excel format.
The format of this file is largely the same as for ixmp :ref:`ixmp:excel-data-format`, and includes the following sheets.
For example input data files, see the files :file:`message_ix/tests/data/*_macro_input.xlsx` included as part of the :mod:`message_ix` test suite; either in your local installation, or `here on GitHub <https://github.com/iiasa/message_ix/tree/main/message_ix/tests/data>`_.

“``config``” sheet
   This configuration sheet specifies MACRO-related nodes and years, and mapps MACRO sectors to MESSAGE commodities and levels.
   The ``config`` sheet has five columns, each of which is a list of labels/codes for a corresponding :ref:`ixmp set <ixmp:data-model-data>`:

   - "node", "year": these can each have any length, depending on the number of regions and years to be included in the MACRO calibration process.
   - "sector", "commodity", "level": these 3 columns must have equal lengths.
     They describe a one-to-one mapping between MACRO sectors (entries in the "sector" column) and MESSAGE commodities and levels (paired entries in the "commodity" and "level" columns).

MACRO parameter sheets
   The remaining sheets each contain data for one MACRO parameter:

   - ``price_ref``: prices of MESSAGE commodities in a reference year.
     This reference year is a year for which commodity prices and energy system cost are known for a given demand of those commodities.
   - ``cost_ref``: total cost of the energy system in the reference year.
   - ``demand_ref``: demand for different commodities in the referenbce year.
   - ``lotol``: tolerance factor for lower bounds on MACRO variabales.
   - ``esub``: elasticity between capital-labor and energy.
   - ``drate``: social discount rate.
   - ``depr``: annual percent depreciation.
   - ``kpvs``: capital value share parameter.
   - ``kgdp``: initial capital to GDP ratio in base year.
   - ``gdp_calibrate``: trajectory of GDP in optimization years calibrated to energy demand to MESSAGE.
   - ``aeei``: annual potential decrease of energy intensity in sector sector.
   - ``MERtoPPP``: conversion factor of GDP from market exchange rates to purchasing power parity.

Numerical issues
================

This section describes how to solve two numerical issues that can occur in large |MESSAGEix| models.

Oscillation detection in the MESSAGE-MACRO algorithm
----------------------------------------------------
The documentation for the :class:`.MESSAGE_MACRO` class describes the algorithm and its three parameters:

- `convergence_criterion`,
- `max_adjustment`, and
- `max_iteration`.

The algorithm detects 'oscillation', which occurs when MESSAGE and MACRO each return slightly different solutions, but these two solutions are each stable.

If the difference between these points is greater than `convergence_criterion`, the algorithm might jump between these two points infinitely.
Instead, the algorithm detects oscillation by comparing model solutions on each iteration to previous values recorded in the iteration log.

If the algorithm picks up on the oscillation between iterations, then after MACRO has solved and before solving MESSAGE, a log message is printed as follows::

    --- Restarting execution
    --- MESSAGE-MACRO_run.gms(4986) 625 Mb
    --- Reading solution for model MESSAGE_MACRO
    --- MESSAGE-MACRO_run.gms(4691) 630 Mb
        +++ Indication of oscillation, increase the scaling parameter (4) +++
    --- GDX File c:\repo\message_ix\message_ix\model\output\MsgIterationReport_ENGAGE_SSP2_v4_EN_NPi2020_900.gdx
        Time since GAMS start: 1 hour, 10 minutes
        +++ Starting iteration 14 of MESSAGEix-MACRO... +++
        +++ Solve the perfect-foresight version of MESSAGEix +++
    --- Generating LP model MESSAGE_LP

.. note:: This example is from a particular model run, and the actual message may differ.

The algorithm then gradually reduces `max_adjustment` from the user-supplied value.
This has the effect of reducing the allowable relative change in demands, until the `convergence_criterion` is met.


Issue 1: Oscillations not detected
----------------------------------

Oscillation detection can fail, especially when the oscillation is very small.
When this occurs, MESSAGE-MACRO will iterate until `max_iteration` (default ``50``) and then print a message indicating that it has not converged.

For the MESSAGEix-GLOBIOM global model, this issue can be encountered with scenarios which have stringent carbon budgets (e.g. <1000 Gt CO₂ cumulative) and require more aggressive reductions of demands.

Identifying oscillation
~~~~~~~~~~~~~~~~~~~~~~~

In order to find out whether failure to converge is due to undetected oscillation, check the iteration report in :file:`MsgIterationReport_<{model_name}>_<{scenario_name}>.gdx`.
The initial iterations will show the objective function value either decreasing or increasing (depending on the model), but after a number of iterations, the objective function will flip-flop between two very similar values.

Preventing oscillation
~~~~~~~~~~~~~~~~~~~~~~

The issue can be resolved by tuning `max_adjustment` and `convergence_criterion` from their respective default values of ``0.2`` (20%) and ``0.01`` (1%).
The general approach is to **reduce max_adjustment**.
Reducing this parameter to half of its default value—i.e. ``0.1``, or 10%—can help, but it can be reduced further, as low as ``0.01`` (1%).

This may require further tuning of the other parameters: first, ensure that `convergence_criterion` is smaller than `max_adjustment`, e.g. set to ``0.009`` (0.9%) < ``0.01``.
Second, due to the small change allowed to the model solution each iteration, if the initial MESSAGE solution is not close to the convergence point, numerous iterations could be required.
Therefore `max_iteration` may also need an increase.

These changes can be made in two ways:

1. Pass the values to :class:`.MESSAGE_MACRO` via keyword arguments to :meth:`.Scenario.solve`.
2. Manually edit the default values in :file:`MESSAGE-MACRO_run.gms`.


Issue 2: MESSAGE solves optimally with unscaled infeasibilities
---------------------------------------------------------------

By default, :mod:`message_ix` is configured so that the CPLEX solver runs using the `lpmethod` option set to ``2``, selecting the dual simplex method.
Solving models the size of MESSAGEix-GLOBIOM takes very long with the dual simplex method—scenarios with stringent constraints can take >10 hours on common hardware.
With `lpmethod` set to ``4``, selecting the barrier method, the model can solve in under a minute.

The drawback of using the barrier method is that, after CPLEX has solved, it crosses over to a simplex optimizer for verification.
As part of this verification step, it may turn out that the CPLEX solution is "optimal with unscaled infeasibilities."

This issue arises when some parameters in the model are not well-scaled, resulting in numerical issues within the solver.
`This page <https://www.tu-chemnitz.de/mathematik/discrete/manuals/cplex/doc/userman/html/solveLPS33.html>`_ (from an earlier, 2002 version of the CPLEX user manual) offers some advice on how to overcome the issues.
The most direct solution is to rescale the parameters in the model itself.

When this is not possible, there are some workarounds:

1. Adjust CPLEX's convergence criterion, `epopt` (this is distinct from the `convergence_criterion` of the MESSAGE_MACRO algorithm).
   In :mod:`message_ix`, :data:`.DEFAULT_CPLEX_OPTIONS` sets this to ``1e-6`` by default.
   This approach is delicate, as changing the tolerance may also change the solution by a significant amount.
   This has not been tested in detail and should be handled with care.

2. Switch to other methods provided by CPLEX, using e.g. `lpmethod` = ``2``.
   A disadvantage of this approach is the longer runtime, as described above.

3. Start the MESSAGE-MACRO algorithm with `lpmethod` set to ``4``.
   Manually monitor its progress, and after approximately 10 iterations have passed, delete the file :file:`cplex.opt`.
   When CPLEX can not find its option file, it will revert to using a simplex method (and advanced basis) from thereon.


:mod:`message_ix.macro` internals
=================================

.. currentmodule:: message_ix.macro

.. automodule:: message_ix.macro
   :members:
   :exclude-members: MACRO_ITEMS
