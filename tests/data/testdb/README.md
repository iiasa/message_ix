# test database folder

This folder contains two local database instances for unit tests.

The `ixmp_test` database contains a number of scenarios for executing tests.
Run `tests\testdb_setup.py` to get a clean version of the db based on the
installed version of `ixmp`.

The db `message_ix_legacy` contains a scenario built from MESSAGEix release 1.1
(and `ixmp` release 0.1) to make sure that the migration in Java works as
expected and legacy scenarios can be loaded and solved in future releases.
