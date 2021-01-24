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
