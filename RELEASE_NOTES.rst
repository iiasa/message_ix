.. Next release
.. ============

.. All changes
.. -----------

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

- The :ref:`default reports <default-reports>` (tables in IAMC format) available in a :class:`~message_ix.reporting.Reporter` have changed keys to e.g. ``message::default`` with **two** colons.
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

All changes
-----------

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
- Adjust :mod:`message_ix.reporting` to use :mod:`genno` / :mod:`ixmp.reporting` changes in `ixmp PR #397 <https://github.com/iiasa/ixmp/pull/397>`_ (:pull:`441`).


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

- :pull:`407`: Use :mod:`.reporting` in tutorials; add :mod:`.util.tutorial` for shorthand code used to streamline tutorials.
- :pull:`407`: Make :class:`.Reporter` a top-level class.
- :pull:`415`: Improve :func:`.make_df` to generate empty, partially-, or fully-filled data frames with the correct columns for any MESSAGE or MACRO parameter.
- :pull:`415`: Make complete lists of :data:`.MESSAGE_ITEMS`, :data:`.MACRO_ITEMS` and their dimensions accessible through the Python API.
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
- :pull:`328`: Expand automatic reporting of emissions prices and mapping sets; improve robustness of :meth:`Reporter.convert_pyam`.
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
- :pull:`176`: Add :mod:`message_ix.reporting` module.
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
