.. Next release
.. ============

.. All changes
.. -----------

.. _v3.11.1:

v3.11.1 (2025-06-03)
====================

- Filter log noise generated when loading scenarios created with :mod:`message_ix`/:mod:`ixmp` v3.10 and earlier (:pull:`946`).

.. _v3.11.0:

v3.11.0 (2025-05-26)
====================

Migration notes
---------------

Users **should**:

- (:pull:`930`) identify any ``type_tec`` entries
  that are used both (a) for commodity share constraints
  (in the ``map_shares_commodity_share`` or ``map_shares_commodity_total`` :ref:`mapping sets <section_maps_def>`),
  *and* (b) for emissions accounting
  (for instance in the ``tax_emission`` or ``bound_emission`` :ref:`parameters <section_parameter_emissions>`).

  For any such entries,
  users **should** reformulate to use distinct ``type_tec`` entries for these two purposes,
  and then confirm that model behaviour relative to v3.10.0 is as expected/not different.
- (:pull:`924`) check that ``ACT`` of technologies within the model horizon is consistent with |historical_new_capacity| and ``technical_lifetime`` values for historical periods.

  If ``input`` or ``output`` parameter values within the model horizon were used as a work-around for :issue:`923`,
  these **may** be safely removed.
- (:pull:`924`, :issue:`932`) check values of ``CAP_NEW``,
  particularly in model periods that have a different duration than the preceding period,
  and adjust |growth_new_capacity_up| or |initial_new_capacity_up| values as necessary.
  For the latter, :func:`.initial_new_capacity_up_v311` may be used.

All changes
-----------

- Some MESSAGEix :doc:`tutorials <tutorials>` are runnable with the :class:`.IXMP4Backend` introduced in :mod:`ixmp` version 3.11 (:pull:`894`, :pull:`941`).
  See `Support roadmap for ixmp4 <https://github.com/iiasa/message_ix/discussions/939>`__ for details.
- Add the :py:`concurrent=...` model option to :class:`.MACRO` (:pull:`808`).
- Adjust use of :ref:`type_tec <mapping-sets>` in :ref:`equation_emission_equivalence` (:pull:`930`, :issue:`929`, :pull:`935`).

  This change reduces the size of the ``EMISS`` variable,
  which can improve memory use performance for large scenarios
  that make extensive use of commodity share constraints.
- Bug fix for construction of |map_tec_lifetime| (:pull:`924`, :issue:`923`).
  Previously, entries in |historical_new_capacity| did not correctly result in historical technology vintages
  that could be active in periods within the model horizon.
  The fix removes the need to use certain work-arounds for the bug; see the issue for details.
  Add documentation for this set.
- Bug fix for the application of |growth_new_capacity_up| in :ref:`equation_new_capacity_constraint_up` (:pull:`924`, :issue:`932`, :pull:`936`).
  In :mod:`message_ix` v3.7.0 to v3.10.0, changes in |duration_period| between subsequent periods
  would result in upper bounds applied to ``CAP_NEW``
  that were artificially low (if period duration increased) or high (if period duration decreased).
- Improve documentation of |duration_period_sum| (:pull:`926`, :issue:`925`).

.. _v3.10.0:

v3.10.0 (2025-02-19)
====================

Migration note
--------------

.. _v3.10.0-migrate-1:

1. For scenarios with :doc:`periods </time>` that have 2 or more different ``duration_period``, users should expect that values for the solution variable ``PRICE_EMISSION`` will change compared to version 3.9.0 and earlier.

   **Only** such scenarios are affected.
   For example, if ``duration_period`` is 5 years for some periods in the ``year`` set, and 10 years for others, then ``PRICE_EMISSION`` values will change.
   On the other hand, if ``duration_period`` values are *all* 5 years, or 10 years, there should be no change.

   This is a result of :pull:`912`, which adjusts the calculation of ``PRICE_EMISSION`` to give correct outcomes in the mixed-duration case.
   Please refer to :pull:`726` and :pull:`723` for more extensive discussion of the issue and fix.

GitHub-recommended community guidelines
---------------------------------------

Add community guidelines for interaction on GitHub (:pull:`871`, :pull:`911`).
Please familiarize yourself with these to foster an open and welcoming community!

All changes
-----------

- :mod:`message_ix` is tested and compatible with `Python 3.13 <https://www.python.org/downloads/release/python-3130/>`__ (:pull:`881`).
- Support for Python 3.8 is dropped (:pull:`881`), as it has reached end-of-life.
- Add :meth:`.Reporter.add_sankey` and :mod:`.tools.sankey` to create Sankey diagrams from solved scenarios (:pull:`770`).
  The :file:`westeros_sankey.ipynb` :ref:`tutorial <tutorial-westeros>` shows how to use this feature.
- Add option to :func:`.util.copy_model` from a non-default location of model files (:pull:`877`).
- Bug fix for calculation of ``PRICE_EMISSION`` (:pull:`912`, :issue:`723`).
  See the :ref:`migration note <v3.10.0-migrate-1>` above.

.. _v3.9.0:

v3.9.0 (2024-06-04)
===================

- Split installation instructions to a basic :ref:`install-quick` and detailed :doc:`install-adv` (:pull:`843`).
- Ensure compatibility with pandas upcoming 3.0 Copy-on-Write behaviour (:pull:`842`).
- Improve tutorial Westeros baseline for correct lifetime, units, and vintage-activity years (:pull:`815`).
- Update tutorial Westeros multinode to include code-based hints for in-depth questions (:pull:`798`).
- :func:`.make_df` can now create partly-filled :class:`DataFrames <pandas.DataFrame>` for indexed sets; not only parameters (:pull:`784`).
- New function :func:`.util.copy_model` that exposes the behaviour of the :program:`message-ix copy-model` CLI command to other Python code (:pull:`784`).
- New test fixture :func:`.tmp_model_dir` (:pull:`784`).
- Bug fix: :meth:`.Scenario.rename` would not rename keys where the index set and index name differed (:issue:`601`, :pull:`791`).
- Increase minimum requirement for genno dependency to 1.20 (:pull:`783`).

.. _v3.8.0:

v3.8.0 (2024-01-12)
===================

Migration notes
---------------

Update code that imports from the following modules:

- :py:`message_ix.reporting` → use :mod:`message_ix.report`.
- :py:`message_ix.reporting.computations` → use :mod:`message_ix.report.operator`.

Code that imports from the old locations will continue to work, but will raise :class:`DeprecationWarning`.

All changes
-----------

- :mod:`message_ix` is tested and compatible with `Python 3.12 <https://www.python.org/downloads/release/python-3120/>`__ (:pull:`767`).
  Support for Python 3.7, which `reached end-of-life on 2023-06-27 <https://peps.python.org/pep-0537/#lifespan>`__, is dropped (:pull:`738`).
  :mod:`message_ix` now requires Python version 3.8 or greater.
- Rename :mod:`message_ix.report` (:pull:`761`).
- Add the :doc:`LPdiag tool <tools/lp_diag>` to diagnose and analyze numerical issues in linear programming (LP) problems stored in MPS-format files (:pull:`704`).
- GDX files generated by :class:`.GAMSModel` (thus :class:`.MESSAGE`, :class:`.MACRO`, and :class:`.MESSAGE_MACRO`) will contain an ``ixmp_version`` set with information on the versions of :mod:`ixmp` and :mod:`message_ix` that generated the file (:issue:`747`, :pull:`767`).
- New reporting operator :func:`.model_periods` and automatic keys ``y::model`` and ``y0`` (:pull:`738`).
- Improve readability of LaTeX equations in docs (:pull:`721`).
- Replace :py:`MESSAGE_ITEMS` and :py:`MACRO_ITEMS` with :attr:`.MESSAGE.items` and :attr:`.MACRO.items`, respectively (:pull:`761`).
- Bugfix: :meth:`.Scenario.add_macro` would not correctly handle configuration that mapped a MESSAGE (commodity, level) to MACRO sector when the commodity and sector names were different (:pull:`719`).
- Expand :doc:`macro` documentation, particularly code documentation (:issue:`315`, :pull:`719`).
- Bugfix: :func:`.operator.as_message_df` would error if a particular dimension was supplied via the `common` argument but not present in `qty` (:pull:`719`).

.. _v3.7.0:

v3.7.0 (2023-05-16)
===================

Migration notes
---------------

- The default `lpmethod` has been changed from "Dual Simplex" (`lpmethod=2`) to "Barrier" (`lpmethod=4`).
  NOTE: this may result in changes to the solution.
  In order to use the previous default `lpmethod`, the user-specific default setting can be set through the user's ixmp configuration file.
  Alternatively, the `lpmethod` can be specified directly as an argument when solving a scenario.
  Both of these configuration methods are further explained :meth:`here <message_ix.models.GAMSModel>`.

- The dimensionality of one set and two parameters (``map_tec_storage``, ``storage_initial``, and ``storage_self_discharge``) are extended to allow repesentation of the mode of operation of storage technologies and the temporal level of storage containers.
  If these items are already populated with data in a Scenario, this data will be incompatible with the MESSAGE GAMS implementation in this release; a :class:`UserWarning` will be emitted when the :class:`.Scenario` is instantiated, and :meth:`~.message_ix.Scenario.solve` will raise a :class:`ValueError`.
  (If these items are empty, their dimensions will be updated automatically.
  New Scenarios are unaffected.)

  Users must update data for these items, specifically:

  ==========================  ============================================
  Existing parameter or set   Dimension(s) to add
  ==========================  ============================================
  ``map_tec_storage``         ``mode``, ``storage_mode``, ``lvl_temporal``
  ``storage_initial``         ``mode``
  ``storage_self_discharge``  ``mode``
  ==========================  ============================================

  For the set ``map_tec_storage``, values for the new dimensions represent, respectively, the ``mode`` of operation for charge/discharge technologies, and the ``storage_mode`` and ``lvl_temporal`` for the corresponding storage device.
  For the two parameters, :func:`.expand_dims` is provided to help:

  .. code-block:: python

      from message_ix import Scenario
      from message_ix.util import expand_dims

      scen, platform = Scenario.from_url("…")

      # Re-use the existing data in `scen`, adding the `mode` dimension
      expand_dims(scen, "storage_initial", mode="an existing mode")

All changes
-----------

- Add a tutorial for Westeros multi-node and different trade possibilities (:pull:`683`).
- Add additional oscillation detection mechanism for macro iterations (:pull:`645`, :pull:`676`)
- Adjust default `lpmethod` from "Dual Simplex" (2) to "Barrier" (4); do NOT remove `cplex.opt` file(s) after solving workflow completes (:pull:`657`).
- Adjust :meth:`.Scenario.add_macro` calculations for pandas 1.5.0 (:pull:`656`).
- Ensure `levelized_cost` are also calculated for technologies with only variable costs (:pull:`653`).
- Correct calculation of `COST_NODAL_NET` for standalone MESSAGE (:pull:`648`)
- Account for difference in period-length in equations `NEW_CAPACITY_CONSTRAINT_LO` and `NEW_CAPACITY_CONSTRAINT_UP` (:pull:`654`)
- Extend functionality of storage solutions to include "mode" and temporal level (:pull:`633`)
- Introduce a citation file :file:`CITATION.cff` with citation information (:pull:`695`).
- Correct GAMS for the assignment of "capacity_factor" at "year" (:pull:`705`).

.. _v3.6.0:

v3.6.0 (2022-08-17)
===================

Migration notes
---------------

- The `in_horizon` argument to :meth:`.vintage_and_active_years` is deprecated, and will be removed in :mod:`message_ix` 4.0 or later.
  At the same time, the behaviour will change to be the equivalent of providing `in_horizon` = :obj:`False`, i.e. the method will no longer filter to the scenario time horizon by default.
  To prepare for this change, user code that expects values confined to the time horizon can be altered to use :meth:`.pandas.DataFrame.query`:

  .. code-block:: python

     df = scen.vintage_and_active_years().query(f"{scen.y0} <= year_vtg")

- The :ref:`default reports <default-reports>` (tables in IAMC format) available in a :class:`.Reporter` have changed keys to e.g. ``message::default`` with **two** colons.
  Code using e.g. ``message:default`` (one colon) should be updated to use the current keys.

  This matches fixed behaviour upstream in :mod:`genno` version 1.12 to avoid unintended confusion with keys like ``A:i``: ``i`` (after the first colon) is the name for the sole dimension of a 1-dimensional quantity, whereas ``default`` in ``message::default`` is a tag.

All changes
-----------

- Adjust keys for IAMC-format reporting nodes (:pull:`628`, :pull:`641`)
- New reporting computation :func:`.as_message_df` (:pull:`628`).
- Extend functionality of :meth:`.vintage_and_active_years`; add aliases :meth:`.yv_ya`, :meth:`.ya`, and :attr:`.y0` (:pull:`572`, :pull:`623`).
- Add scripts and HOWTO for documentation videos (:pull:`396`).

.. _v3.5.0:

v3.5.0 (2022-05-06)
===================

Migration notes
---------------

The format of input data files for MACRO calibration has been changed in :pull:`327`.
Files compatible with v3.4.0 and earlier will not work with this version and should be updated; see details of the current data file format in the :doc:`documentation <macro>`.

:pull:`561` corrected the model internal logic for handling zero values in the :ref:`capacity_factor <params-tech>` parameter.
Before this change, the GAMS code inserted a ``capacity_factor`` value of 1.0 where such zero values appeared; now, zeros are preserved, so the technologies may be created (``CAP``) but none of their capacity will be usable at the
:math:`(n, t, y^V, y, h)` where zero values appear.
This is consistent with the general concept of a “capacity factor”: for instance, a solar photovoltaic technology for electricity generation may have a non-zero *capacity* with a *capacity factor* of 0 at :math:`h=\text{night}`.
This may cause changes in model output for scenarios where such zero values appear; see :issue:`591` for discussion, including methods to check for and adjust/remove such values.

All changes
-----------

- Extend documentation on historical capacity and activity values (:pull:`496`)
- Extend documentation on decision variables "CAP_NEW" and "CAP" (:pull:`595`)
- Extend documentation to guide users through the Westeros tutorials (:pull:`594`).
- Add new logo and diagram to the documentation (:pull:`597`).
- Correct typo in GAMS formulation, :ref:`equation_renewables_equivalence` (:pull:`581`).
- Handle zero values in ``capacity_factor`` in models with sub-annual time resolution; expand tests (:issue:`515`, :pull:`561`).
- Extend explanations, update :func:`.make_df` signature in tutorials (:pull:`524`).
- Improve configurability of :mod:`.macro`; see the :doc:`documentation <macro>` (:pull:`327`).
- Split :meth:`.Reporter.add_tasks` for use without an underlying :class:.`Scenario` (:pull:`567`).
- Allow setting the “model_dir” and “solve_options” options for :class:`.GAMSModel` (and subclasses :class:`.MESSAGE`, :class:`.MACRO`, and :class:`.MESSAGE_MACRO`) through the user's ixmp configuration file; expand documentation (:pull:`557`).

.. _v3.4.0:

v3.4.0 (2022-01-27)
===================

- Expand the documentation with an outlook of the MESSAGEix usage (:pull:`520`).
- Adjust test suite for pyam v1.1.0 compatibility (:pull:`499`).
- Add Westeros :doc:`tutorial <tutorials>` on historical parameters (:pull:`478`).
- Update reference for activity and capacity soft constraints (:pull:`474`).
- Update :meth:`.years_active` to use sorted results (:pull:`491`).
- Adjust the Westeros reporting tutorial to pyam 1.0 deprecations (:pull:`492`).
- Change precision of GAMS check for parameter "duration_time" (:pull:`513`).
- Update light and historic demand in Westeros baseline tutorial (:pull:`523`).
- Enhance mathematical formulation to represent sub-annual time slices consistently (:pull:`509`).

.. _v3.3.0:

v3.3.0 (2021-05-28)
===================

Migration notes
---------------

``rmessageix`` (and ``rixmp``) are deprecated and removed, as newer versions of the R `reticulate <https://rstudio.github.io/reticulate/>`_ package allow direct import and use of the Python modules with full functionality.
See the updated page for :doc:`rmessageix`, and the updated instructions on how to :ref:`install-r`.

All changes
-----------

- Update the Westeros :doc:`tutorial <tutorials>` on flexible generation (:pull:`369`).
- Add a Westeros :doc:`tutorial <tutorials>` on modeling renewable resource supply curves (:pull:`370`).
- Update the Westeros :doc:`tutorial <tutorials>` on firm capacity (:pull:`368`).
- Remove ``rmessageix`` (:pull:`473`).
- Expand documentation of :ref:`commodity storage <gams-storage>` sets, parameters, and equations (:pull:`473`).
- Add two new Westeros :doc:`tutorial <tutorials>` on creating scenarios from Excel files (:pull:`450`).
- Fix bug in :meth:`.years_active` to use the lifetime corresponding to the vintage year for which the active years are being retrieved (:pull:`456`).
- Add a PowerPoint document usable to generate the RES diagrams for the Westeros tutorials (:pull:`408`).
- Expand documentation :doc:`install` for installing GAMS under macOS (:pull:`460`).
- Add new Westeros :doc:`tutorial <tutorials>` on add-on technologies (:pull:`365`).
- Expand documentation of :ref:`dynamic constraint parameters <section_parameter_dynamic_constraints>` (:pull:`454`).
- Adjust :mod:`message_ix.report` to use :mod:`genno` / :mod:`ixmp.report` changes in `ixmp PR #397 <https://github.com/iiasa/ixmp/pull/397>`_ (:pull:`441`).

v3.2.0 (2021-01-24)
===================

Migration notes
---------------

- Code that uses :func:`.make_df` can be adjusted in one of two ways.
  See the function documentation for details.
  The function should be imported from the top level:

  .. code-block:: python

     from message_ix import make_df

All changes
-----------

- :pull:`407`: Use :mod:`.report` in tutorials; add :mod:`.util.tutorial` for shorthand code used to streamline tutorials.
- :pull:`407`: Make :class:`.Reporter` a top-level class.
- :pull:`415`: Improve :func:`.make_df` to generate empty, partially-, or fully-filled data frames with the correct columns for any MESSAGE or MACRO parameter.
- :pull:`415`: Make complete lists of :attr:`.MESSAGE_ITEMS <.MESSAGE.items>`, :attr:`.MACRO_ITEMS <.MACRO.items>` and their dimensions accessible through the Python API.
- :pull:`421`: Fix discounting from forward-looking to backward-looking and provide an explanation of the period structure and discounting in documentation of :doc:`time`.

v3.1.0 (2020-08-28)
===================

:mod:`message_ix` v3.1.0 coincides with :mod:`ixmp` v3.1.0.

For citing :mod:`message_ix`, distinct digital object identifiers (DOIs) are available for every release from v3.1.0 onwards; see the :ref:`user guidelines and notice <notice-cite>` for more information and how to cite.

All changes
-----------

- :pull:`367`: Add new westeros tutorial on share constraints.
- :pull:`366`: Add new Westeros tutorial on modeling fossil resource supply curves.
- :pull:`391`, :pull:`392`: Add a documentation page on :doc:`pre-requisite knowledge & skills <prereqs>`; expand guidelines on :doc:`contributing`.
- :pull:`389`: Fix a bug in :func:`.pyam.concat` using *non*-pyam objects.
- :pull:`286`, :pull:`381`, :pull:`389`: Improve :meth:`.add_horizon` to also set ``duration_period``; add documentation of :doc:`time`.
- :pull:`377`: Improve the :doc:`rmessageix <rmessageix>` R package, tutorials, and expand documentation and installation instructions.
- :pull:`382`: Update discount factor from ``df_year`` to ``df_period`` in documentation of the objective function to match the GAMS formulation.


v3.0.0 (2020-06-07)
===================

:mod:`message_ix` v3.0.0 coincides with :mod:`ixmp` v3.0.0.

Migration notes
---------------

The :ref:`generic storage formulation <gams-storage>` introduces **new ixmp items** (sets, parameters, variables, and equations) to the MESSAGE model scheme.
When loading a Scenario created with a version of `message_ix` older than 3.0.0, :meth:`.MESSAGE.initialize` will initialized these items (and leave them empty), using at most one call to :meth:`~message_ix.Scenario.commit`.

See also the `migration notes for ixmp 3.0.0`_.

.. _migration notes for ixmp 3.0.0: https://docs.messageix.org/projects/ixmp/en/latest/whatsnew.html#v3-0-0-2020-06-05

All changes
-----------

- :pull:`190`: Add generic mathematical formulation of :ref:`technologies that store commodities <gams-storage>`, such as water and energy.
- :pull:`343`, :pull:`345`: Accept :class:`.MESSAGE_MACRO` iteration control parameters through :meth:`.solve`; document how to tune these to avoid numerical issues.
- :pull:`340`: Allow cplex.opt to be used by `message_ix` from multiple processes.
- :pull:`328`: Expand automatic reporting of emissions prices and mapping sets; improve robustness of :func:`.Reporter.convert_pyam <genno.compat.pyam.operator.add_as_pyam>`.
- :pull:`321`: Move :meth:`.Scenario.to_excel`, :meth:`.read_excel` to :class:`ixmp.Scenario`; they continue to work with :class:`message_ix.Scenario`.
- :pull:`323`: Add `units`, `replace_vars` arguments to :meth:`.Reporter.convert_pyam`.
- :pull:`308`: Expand automatic reporting of add-on technologies.
- :pull:`313`: Include all tests in the `message_ix` package.
- :pull:`307`: Adjust to deprecations in ixmp 2.0.
- :pull:`223`: Add methods for parametrization and calibration of MACRO based on an existing MESSAGE Scenario.


v2.0.0 (2020-01-14)
===================

:mod:`message_ix` v2.0.0 coincides with :mod:`ixmp` v2.0.0.

Migration notes
---------------

Support for **Python 2.7 is dropped** as it has reached end-of-life, meaning no further releases will be made even to fix bugs.
See `PEP-0373 <https://www.python.org/dev/peps/pep-0373/>`_ and https://python3statement.org.
`message_ix` users must upgrade to Python 3.

**Command-line interface (CLI).** Use ``message-ix`` as the program for all command-line operations:

- ``message-ix copy-model`` replaces ``messageix-config``.
- ``message-ix dl`` replaces ``messageix-dl``.
- ``message-ix`` also provides all the features of the :mod:`ixmp` CLI.

**Configuration.** ixmp adds a streamlined system for storing information about different platforms, backends, and databases that store Scenario data.
See the :doc:`ixmp release notes <ixmp:whatsnew>` for migration notes.

All changes
-----------

- :pull:`285`: Drop support for Python 2.
- :pull:`284`: Add a suggested sequence/structure to how to run the Westeros tutorials.
- :pull:`281`: Test and improve logic of :meth:`.years_active` and :meth:`.vintage_and_active_years`.
- :pull:`269`: Enforce ``year``-indexed columns as integers.
- :pull:`256`: Update to use :obj:`ixmp.config` and improve CLI.
- :pull:`255`: Add :mod:`message_ix.testing.nightly` and ``message-ix nightly`` CLI command group for slow-running tests.
- :pull:`249`, :pull:`259`: Build MESSAGE and MESSAGE_MACRO classes on ixmp model API; adjust Scenario.
- :pull:`235`: Add a reporting tutorial.
- :pull:`236`, :pull:`242`, :pull:`263`: Enhance reporting.
- :pull:`232`: Add Westeros tutorial for modelling seasonality, update existing tutorials.
- :pull:`276`: Improve add_year for bounds and code cleanup


v1.2.0 (2019-06-25)
===================

MESSAGEix 1.2.0 adds an option to set the commodity balance to strict equality,
rather than a supply > demand inequality. It also improves the support for
models with non-equidistant years.

Other improvements include an experimental reporting module, support for CPLEX
solver options via :meth:`~.Scenario.solve`, and a reusable :mod:`message_ix.testing`
module.

Release 1.2.0 coincides with ixmp
`release 0.2.0 <https://github.com/iiasa/ixmp/releases/tag/v0.2.0>`_, which
provides full support for :meth:`~.Scenario.clone` across platforms (database
instances), e.g. from a remote database to a local HSQL database; as well as
other improvements. See the ixmp release notes for further details.

All changes
-----------

- :pull:`161`: A feature for adding new periods to a scenario.
- :pull:`205`: Implement required changes related to timeseries-support and cloning across platforms (see `ixmp#142 <https://github.com/iiasa/ixmp/pull/142>`_).
- :pull:`196`: Improve testing by re-using :mod:`ixmp` apparatus.
- :pull:`187`: Test for cumulative bound on emissions.
- :pull:`182`: Fix cross-platform cloning.
- :pull:`178`: Bugfix of the ``PRICE_EMISSION`` variable in models with non-equidistant period durations.
- :pull:`176`: Add :mod:`message_ix.report` module.
- :pull:`173`: The meth:`~.Scenario.solve` command now takes additional arguments when solving with CPLEX. The cplex.opt file is now generated on the fly during the solve command and removed after successfully solving.
- :pull:`172`: Add option to set ``COMMODITY_BALANCE`` to equality.
- :pull:`154`: Enable documentation build on ReadTheDocs.
- :pull:`138`: Update documentation and tutorials.
- :pull:`131`: Update clone function argument `scen` to `scenario` with planned deprecation of the former.


v1.1.0 (2018-11-21)
===================

Migration notes
---------------

This patch introduces a few backwards-incompatible changes to database management.

Database Migration
~~~~~~~~~~~~~~~~~~

If you see an error message like::

    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    usr/local/lib/python2.7/site-packages/ixmp/core.py:81: in __init__
        self._jobj = java.ixmp.Platform("Python", dbprops)
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    self = <jpype._jclass.at.ac.iiasa.ixmp.Platform object at 0x7ff1a8e98410>
    args = ('Python', '/tmp/kH07wz/test.properties')

        def _javaInit(self, *args):
            object.__init__(self)

            if len(args) == 1 and isinstance(args[0], tuple) \
               and args[0][0] is _SPECIAL_CONSTRUCTOR_KEY:
                self.__javaobject__ = args[0][1]
            else:
                self.__javaobject__ = self.__class__.__javaclass__.newClassInstance(
    >               *args)
    E           org.flywaydb.core.api.FlywayExceptionPyRaisable: org.flywaydb.core.api.FlywayException: Validate failed: Migration checksum mismatch for migration 1
    E           -> Applied to database : 1588531206
    E           -> Resolved locally    : 822227094

Then you need to update your local database. There are two methods to do so:

1. Delete it (you will lose all data and need to regenerate it). The default
   location is ~/.local/ixmp/localdb/.
2. Manually apply the underlying migrations. This is not particularly easy, but
   allows you to save all your data. If you want help, feel free to get in
   contact on the
   `listserv <https://groups.google.com/forum/#!forum/message_ix>`_.

New Property File Layout
~~~~~~~~~~~~~~~~~~~~~~~~

If you see an error message like::

    usr/local/lib/python2.7/site-packages/jpype/_jclass.py:111: at.ac.iiasa.ixmp.exceptions.IxExceptionPyRaisable
    ---------------------------- Captured stdout setup -----------------------------
    2018-11-13 08:15:17,410 ERROR at.ac.iiasa.ixmp.database.DbConfig:357 - missing property 'config.server.config' in /tmp/hhvE1o/test.properties
    2018-11-13 08:15:17,412 ERROR at.ac.iiasa.ixmp.database.DbConfig:357 - missing property 'config.server.password' in /tmp/hhvE1o/test.properties
    2018-11-13 08:15:17,412 ERROR at.ac.iiasa.ixmp.database.DbConfig:357 - missing property 'config.server.username' in /tmp/hhvE1o/test.properties
    2018-11-13 08:15:17,413 ERROR at.ac.iiasa.ixmp.database.DbConfig:357 - missing property 'config.server.url' in /tmp/hhvE1o/test.properties
    ------------------------------ Captured log setup ------------------------------
    core.py                     80 INFO     launching ixmp.Platform using config file at '/tmp/hhvE1o/test.properties'
    _________________ ERROR at setup of test_add_spatial_multiple __________________

        @pytest.fixture(scope="session")
        def test_mp():
            test_props = create_local_testdb()

            # start jvm
            ixmp.start_jvm()

            # launch Platform and connect to testdb (reconnect if closed)
    >       mp = ixmp.Platform(test_props)

Then you need to update your property configuration file. The old file looks like::

    config.name = message_ix_test_db@local
    jdbc.driver.1 = org.hsqldb.jdbcDriver
    jdbc.url.1 = jdbc:hsqldb:file:/path/to/database
    jdbc.user.1 = ixmp
    jdbc.pwd.1 = ixmp
    jdbc.driver.2 = org.hsqldb.jdbcDriver
    jdbc.url.2 = jdbc:hsqldb:file:/path/to/database
    jdbc.user.2 = ixmp
    jdbc.pwd.2 = ixmp

The new file should look like::

    config.name = message_ix_test_db@local
    jdbc.driver = org.hsqldb.jdbcDriver
    jdbc.url = jdbc:hsqldb:file:/path/to/database
    jdbc.user = ixmp
    jdbc.pwd = ixmp

All changes
-----------

- :pull:`202`: Added the "Development rule of thumb" section from the wiki and the Tutorial style guide to the Contributor guidelines. Tweaked some formatting to improve readibility.
- :pull:`113`: Upgrading to MESSAGEix 1.1: improved representation of renewables, share constraints, etc.
- :pull:`109`: MACRO module added for initializing models to be solved with MACRO. Added scenario-based CI on circleci.
- :pull:`99`: Fixing an error in the compuation of the auxiliary GAMS reporting variable ``PRICE_EMISSION``.
- :pull:`89`: Fully implementing system reliability and flexibity considerations (cf. Sullivan).
- :pull:`88`: Reformulated capacity maintainance constraint to ensure that newly installed capacity cannot be decommissioned within the same model period as it is built in.
- :pull:`84`: ``message_ix.Scenario.vintage_active_years()`` now limits active years to those after the first model year or the years of a certain technology vintage.
- :pull:`82`: Introducing "add-on technologies" for mitigation options, etc.
- :pull:`81`: Share constraints by mode added.
- :pull:`80`: Share constraints by commodity/level added.
- :pull:`78`: Bugfix: ``message_ix.Scenario.solve()`` uses 'MESSAGE' by default, but can be provided other model names.
- :pull:`77`: ``rename()`` function can optionally keep old values in the model (i.e., copy vs. copy-with-replace).
- :pull:`74`: Activity upper and lower bounds can now be applied to all modes of a technology.
- :pull:`67`: Use of advanced basis in cplex.opt turned off by default to avoid conflicts with barrier method.
- :pull:`65`: Bugfix for downloading tutorials. Now downloads current installed version by default.
- :pull:`60`: Add basic ability to write and read model input to/from Excel.
- :pull:`59`: Added MacOSX CI support.
