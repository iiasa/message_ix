.. currentmodule:: message_ix.tools.migrate

Migrations
**********

This module contains tools for migrating :class:`.Scenario` data across versions of :mod:`message_ix`.
These are applicable when there are changes to the GAMS implementation of MESSAGE:

- Improvements that allow more efficient or tailored representation of certain phenomena.
- Fixes to bugs in the implementation that lead to incorrect model solution data,
  under certain conditions.
- Changes in the meaning or interpretation of sets or parameters.

Users **should** call functions like, for instance, :func:`v311`
that apply migrations appropriate for the MESSAGE GAMS implementation in version v3.11.0
(in other words, changes new since v3.10.x).

These functions call 1 or more atomic migration functions:
for example, :func:`v311` calls :func:`initial_new_capacity_up_v311`.
The atomic migration functions use :func:`migration_applied`
to ensure that the same adjustments are not performed more than once on the same Scenario.

API reference
=============

.. automodule:: message_ix.tools.migrate
   :members:
