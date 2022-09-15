Calibrate and tune MESSAGE-MACRO
********************************

“MESSAGE-MACRO” refers to the combination of MESSAGE and MACRO, run iteratively in a multi-disciplinary optimization algorithm.
This combination is activated by calling :meth:`.solve` with the argument `model='MESSAGE-MACRO'`, or using the GAMS :file:`MESSAGE-MACRO_run.gms` script directly (see :ref:`running` for details about these two methods).

.. contents::
   :local:

Prior to solving MESSAGE in combination with MACRO, MACRO will need to be calibrated to MESSAGE.

The calibration process adjusts the AEEI improvement rates and labour productivity growth rates by comparing MACRO GDP with exogenous GDP growth rates.

This necessitates a scenario which has already been solved with standalone MESSAGE.
Ideally, this scenario will be a counterfactual scenario or a reference-scenario, meaning that this scenario will not include any long-term climate policy targets.
The calibration of the scenario is invoked using the :meth:`.add_macro`.

The calibration will be run for the entire optimization-time horizon i.e., for all time-periods after and including, the `firstmodelyear`.
It will be necessary to provide the calibration process with calibration data, which amongst other data, specifies data for the last historic time-period in the model i.e., the time-period prior to the `firstmodelyear`, later referred to as the "reference year".
This "reference year" represents the time-period for which commodity prices and energy system cost are known for a given demand of those commodities.
This is detailed in the :ref:`next section <macro-input-data>`.

The calibration itself is carried out by the :file:`message_ix/model/MACRO/macro_calibration.gms`.
In the file, `max_it` is used to specify the number of iterations carried out between MESSAGE and MACRO as part of the calibration process.
The default value is set to 100 iterations, which has proven to be sufficient for the calibration of MACRO to MESSAGE reference scenario.
Adjustment of labor productivity growth rates is carried out during even iterations.
Adjustment of AEEI improvement rates is carried out during odd iterations.

.. note:: Note, that no actual check is carried out to see if the calibration process has been successful.

The information from the calibration process is logged in :file:`message_ix/model/MACRO_run.lst`.
Successful calibration of MACRO to MESSAGE can be identified by looking at the reported values for the "PARAMETER growth_correction" for the last "even" iteration, which should be somewhere around 1e-14 to 1e-16 for positive adjustments or -1e-14 to -1e-16 for negative adjustments.
Likewise, the "PARAMETER aeei_correction" can be checked for the loss "odd" iteration.  
Once the calibration process has been completed, the scenario will be populated with :ref:`additional parameters <macro-core-formulation>`.
As part of the calibration process, final check will automatically be carried out, solving the freshly calibrated scenario in combination with MACRO, ensuring that the convergence criteria is met after the first iteration.

.. _macro-input-data:

Input data file
===============

The calibration process requires an input data file (Microsoft Excel format), largely built around :ref:`ixmp:excel-data-format`.
For an example of such input data files, see the files :file:`message_ix/tests/data/*_macro_input.xlsx` included as part of the :mod:`message_ix` test suite; either in your local installation, or `here on GitHub <https://github.com/iiasa/message_ix/tree/main/message_ix/tests/data>`_. The input data file includes the following sheets: 

General configuration sheet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``config``: This configuration sheet specifies MACRO-related nodes and years, and maps MACRO sectors to MESSAGE commodities and levels.
   The sheet has five columns, each of which is a list of labels/codes for a corresponding :ref:`ixmp set <ixmp:data-model-data>`:

   - "node", "year": these can each have any length, depending on the number of regions and years to be included in the MACRO calibration process.
   - "sector", "commodity", "level": these 3 columns must have equal lengths.
     They describe a one-to-one mapping between MACRO sectors (entries in the "sector" column) and MESSAGE commodities and levels (paired entries in the "commodity" and "level" columns).

MACRO parameter sheets
~~~~~~~~~~~~~~~~~~~~~~
   The remaining sheets each contain data for one MACRO parameter:

   - ``price_ref``: prices of MESSAGE commodities in a reference year. 
     These can be obtained from the variable `PRICE_COMMODITY`. 
   - ``cost_ref``: total cost of the energy system in the reference year.
     These can be obtained from the variable `COST_NODAL_NET` and should be divided by a factor of 1000. 
   - ``demand_ref``: demand for different commodities in the reference year.
   - ``lotol``: tolerance factor for lower bounds on MACRO variabales.
   - ``esub``: elasticity between capital-labor and energy.
   - ``drate``: social discount rate. 
   - ``depr``: annual percent depreciation.
   - ``kpvs``: capital value share parameter.
   - ``kgdp``: initial capital to GDP ratio in base year.
   - ``gdp_calibrate``: trajectory of GDP in optimization years calibrated to energy demand to MESSAGE.
     Values for atleast two periods prior to the `firstmodelyear` are required in order to compute the growth rates in historical years. 
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
Specifically, the algorithm checks for three patterns across the iterations.

1. Does the sign of the `max_adjustment` parameter change?
2. Are the maximum-positive and maximum-negative adjustments equal to each other?
3. Do the solutions jump between two objective functions?

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

Which of the three checks listed above has been invoked is logged in the iteration report in :file:`MsgIterationReport_<{model_name}>_<{scenario_name}>.gdx` under the header "oscillation check".

The algorithm then gradually reduces `max_adjustment` from the user-supplied value.
This has the effect of reducing the allowable relative change in demands, until the `convergence_criterion` is met.

If none of the checks have been invoked over the iterations, then MESSAGEix and MACRO converged *naturally*.
A log message as follows is printed::

    --- Reading solution for model MESSAGE_MACRO
    --- Executing after solve: elapsed 7:42:24.622
    --- MESSAGE-MACRO_run.gms(5176) 1116 Mb
        +++ Convergence criteria satisfied after 14 iterations +++
        +++ Natural convergence achieved +++

If in any of the iterations, any of the three oscillation checks were invoked, a log message is printed as follows::

    --- Reading solution for model MESSAGE_MACRO
    --- Executing after solve: elapsed 7:42:24.622
    --- MESSAGE-MACRO_run.gms(5176) 1116 Mb
        +++ Convergence criteria satisfied after 14 iterations +++
        +++ Convergence achieved via oscillation check mechanism; check iteration log for further details +++

Issue 1: Oscillations not detected
----------------------------------

Oscillation detection can fail, especially when the oscillation is very small.
When this occurs, MESSAGE-MACRO will iterate until `max_iteration` (default ``50``) and then print a message indicating that it has not converged.

For the MESSAGEix-GLOBIOM global model, this issue can be encountered with scenarios which have stringent carbon budgets (e.g. <1000 Gt CO₂ cumulative) and require more aggressive reductions of demands.

Identifying oscillation
~~~~~~~~~~~~~~~~~~~~~~~

In order to find out whether failure to converge is due to undetected oscillation, check the iteration report.
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

1. Adjust CPLEX's scaling parameter; specify `scaind = 1`.
   This will result in more "aggressive" scaling.

2. Adjust CPLEX's barrier crossover algorithm; specify `barcrossalg = 2`.
   By default, CPLEX will choose between either `Primal crossover` or `Dual crossover`.
   Unscaled infeasibilities will result only with `Primal crossover`, hence forcing CPLEX to use the latter will resolve the issue.
   This will result in longer solving times, but will guarantee overcoming the issue.

.. note:: This solution has been implemented as part of the MESSAGE-MACRO iterations process.
   During the iterations, a check is performed on the solution status (LP status (5)) of MESSAGE.
   If the solution status is found to show the solution is "optimal with unscaled infeasibilities", then a secondary CPLEX configuration file is used.
   The secondary CPLEX configuration file :file:`message_ix\model\cplex.op2` is a duplicate of :file:`message_ix\model\cplex.opt` with the addition of the argument `barcrossalg = 2`.
   This secondary CPLEX configuration file is generated together with the primary CPLEX configuration file in :file:`message_ix\models.py`.

3. Adjust CPLEX's convergence criterion, `epopt` (this is distinct from the `convergence_criterion` of the MESSAGE_MACRO algorithm).
   In :mod:`message_ix`, :data:`.DEFAULT_CPLEX_OPTIONS` sets this to ``1e-6`` by default.
   This approach is delicate, as changing the tolerance may also change the solution by a significant amount.
   This has not been tested in detail and should be handled with care.

4. Switch to other methods provided by CPLEX, using e.g. `lpmethod` = ``2``.
   A disadvantage of this approach is the longer runtime, as described above.

The arguments can be passed with the solve command, e.g. `scenario.solve(solve_options={"barcrossalg": "2"})`
Alternatively the arguments can be specified either in :file:`models.py`.


:mod:`message_ix.macro` internals
=================================

.. currentmodule:: message_ix.macro

.. automodule:: message_ix.macro
   :members:
   :exclude-members: MACRO_ITEMS
