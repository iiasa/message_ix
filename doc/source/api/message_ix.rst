.. currentmodule:: message_ix

``message_ix`` package
======================

|MESSAGEix| models are created using the :py:class:`message_ix.Scenario` class. Several utility methods are also provided in the module :py:mod:`message_ix.utils`.

.. autoattribute:: message_ix.core.DEFAULT_SOLVE_OPTIONS

   Solver options used by :meth:`message_ix.Scenario.solve`. These configure
   the GAMS CPLEX solver (or another solver, if selected); see `the solver
   documentation <https://www.gams.com/latest/docs/S_CPLEX.html>`_ for possible
   values.

.. automodule:: message_ix
   :members: Scenario

.. _utils:

Utility methods
---------------

.. automodule:: message_ix.utils
   :members: make_df, make_ts, matching_rows, multiply_df

.. automodule:: message_ix.testing
   :members: make_dantzig, make_westeros
