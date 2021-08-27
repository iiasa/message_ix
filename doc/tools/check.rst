Pre-solve checks
****************

.. currentmodule:: message_ix.tools

.. autofunction:: check

.. currentmodule:: message_ix.tools._check

.. _checks-summary:

.. automodule::  message_ix.tools._check
   :members: gaps_input, gaps_tl, tl_integer

   .. autoclass:: Result

   Individual checks
   =================

   Gaps in certain parameters (:func:`gaps_*` check functions) can cause the GAMS implementation to treat that specific technology to be disabled in one period, between other periods where it *is* enabled.
   This may prevent solution of the model.

   .. autosummary::

      gaps_input
      gaps_tl
      tl_integer
