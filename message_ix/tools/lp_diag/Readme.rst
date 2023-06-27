.. lpDiag documentation master file

``lpDiag``: basic diagnostics of the LP programming problems
============================================================

Description
-----------

``lpDiag`` provides basic information about the LP programming problems
defined by corresponding MPS-format files.
The diagnostics focuses on the implied numerical properties of the underlying
optimization problem.

In this context, the term `outlier` denotes the model entities having values
in either lower or upper tail of the corresponding value distribution.
The tails are defined by the corresponding orders of magnitudes.
The default values are (-6, 6), respectively; they can be redefined,
if desired.

Features
^^^^^^^^

The current version provides the following information:

- characteristics of the problem (including numbers of rows, columns, non-zero
  coefficients and distributions of their values),
- location (row and column) of each outlier,
- ranges of values of other coefficients in each such row and column, as well as
  the corresponding bounds (LHS, RHS for rows),

The functionality of ``lpDiag`` will be gradually enhanced to meet actual needs
of the ``message_ix`` modelers.

Usage
-----

The tool analyzes provided MPS-format files.
We provide several small MPSs for testing local installations, as well
as becoming familiar with ``lpDiag``.
Hints on generating MPS files are provided below.

Generation of the MPS file in the ``message_ix`` environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The MPS-format is the oldest, and still popular, representation of the LP problems.
Most modeling environments provide various ways of generation of the MPS file.
For instance, upon solving a :class:`message_ix scenario` one shall define
in `scenario.solve()` the `writemps` option together with the desired name of
the MPS file.
The MPS file will then be generated and deposited in the `message_ix/message_ix/model`
folder.
Details are available in the GAMS-Documentation:
https://www.gams.com/latest/docs/S_CPLEX.html#CPLEXwritemps

Example of specification of the corresponding option::

	`scenario.solve(solve_options={"writemps": "<file_name>.mps"})`


Running ``lpDiag`` within the ``message_ix`` environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Navigate to any folder you want to work; it is convenient to copy or link
to such a folder the MPS file(s) you want to explore.
If you want to use the provided MPS files, then you find them in
`message_ix/tools/lp_diag`.

One can run ``lpDiag`` from the command line::

	python main.py --path message_ix/tools/lp_diag --mps "<file_name>"

utility on the specified `.mps` file located in the the directory `message_ix/tools/lp_diag`. The
option `-s` will save the results in a text-file in the subdirectory (`repdir`) of the
current working directory.

Running ``lpDiag`` locally
^^^^^^^^^^^^^^^^^^^^^^^^^^

Exploring results
^^^^^^^^^^^^^^^^^

Running ``lpDiag``
^^^^^^^^^^^^^^^^^^


Please share your comments and report bugs in the in the Discussions and Issues
of this repo, respectively.

This tool adds new modeling years to an existing :class:`message_ix.Scenario` (hereafter "reference scenario"). For instance, in a scenario define with::

    history = [690]
    model_horizon = [700, 710, 720]
    sc_ref.add_horizon(
        year=history + model_horizon,
        firstmodelyear=model_horizon[0]
    )

.. additional years can be added after importing the add_year function::

    from message_ix.tools.add_year import add_year
    sc_new = message_ix.Scenario(mp, sc_ref.model, sc_ref.scenario,
                                 version='new')
    add_year(sc_ref, sc_new, [705, 712, 718, 725])

At this point, ``sc_new`` will have the years [700, 705, 710, 712, 718, 720, 725], and original or interpolated data for all these years in all parameters.


The tool operates by creating a new empty Scenario (hereafter "new scenario") and:

- Copying all **sets** from the reference scenario, adding new time steps to relevant sets (e.g., adding 2025 between 2020 and 2030 in the set ``year``)
- Copying all **parameters** from the reference scenario, adding new years to relevant parameters, and calculating missing values for the added years.

Features
~~~~~~~~

- It can be used for any MESSAGE scenario, from tutorials, country-level, and global models.
- The new years can be consecutive, between existing years, and/or after the model horizon.
- The user can define for what regions and parameters the new years should be added. This saves time when adding the new years to only one parameter of the reference scenario, when other parameters have previously been successfully added to the new scenario.

