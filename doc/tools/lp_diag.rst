.. currentmodule:: message_ix.tools.lp_diag

:mod:`.lp_diag`: basic diagnostics of linear program (LP) problems
******************************************************************

.. contents::
   :local:

Description
===========

``LPdiag`` provides basic information about the LP programming problems defined by corresponding MPS-format files.
The diagnostics focuses on the implied numerical properties of the underlying optimization problem.

In this context, the term ``outlier`` denotes the model entities having values in either lower or upper tail of the corresponding value distribution.
The tails are defined by the corresponding orders of magnitudes defined as :math:`int(alog(abs(val)))`, where ``val`` stands for the value of the corresponding coefficient.
The default values of the tails are equal to :math:`(-6, 6)`, respectively; they can be redefined, if desired.

The rule of thumb says: the maximum and minimum orders of magnitudes of the LP matrix coefficients passed to optimization should differ by at most four.
``LPdiag`` helps to achieve such a goal by providing info on outliers.
Such info can be used e.g., for:

- reconsideration of measurement units of the corresponding variables and relations,
- consideration of replacing `small` (in relations to other coefficients in the same row or column) elements by zero,
- splitting the corresponding rows and/or columns,
- verification of the coefficients' values.

Features
--------

The current ``LPdiag`` version provides the following information:

- characteristics of the problem (including numbers of rows, columns, non-zero coefficients and distributions of their values),
- distributions of diverse values characterizing the LP matrix,
- location (row and column) of each outlier,
- ranges of values of other coefficients in each such row or column, as well as the corresponding bounds (LHS, RHS for rows, lower and upper bounds for columns).

The functionality of ``LPdiag`` will be gradually enhanced to meet actual needs of the ``message_ix`` modelers.

Usage
=====

The tool analyzes provided MPS-format files.
We provide several small MPS files for testing local installations in :file:`message_ix/tests/data/lp_diag/`, as well as becoming familiar with ``LPdiag``.
The small MPS files are structured as follows:

- :file:`aez.mps`: agro-ecological zones, medium size.
- :file:`diet.mps`: classical small LP.
- :file:`jg_korh.mps`: tiny testing problem.
- :file:`lotfi.mps`: classical medium size.
- :file:`error_{*}.mps`: various MPS-specs testing error-handling logic in the code.

Hints on generating MPS files are provided below.
Feel free to store arbitrary large MPS files in :file:`message_ix/tools/lp_diag/data/mps/`, but note that these should not be committed to GitHub.

We suggest the following steps for becoming familiar with ``LPdiag`` and then use it for analysis of actual MPS files:

- becoming familiar with ``LPdiag``,
- prepare MPS file,
- actual analysis.

We outline each of these steps below.

Becoming familiar with ``LPdiag``
---------------------------------

Note that ``LPdiag`` should be run at the terminal prompt.

- Navigate to the folder ``message_ix/tools/lp_diag``.
- For initial testing run the following command, which will run analysis of the default (pre-specified) MPS provided in the test_mps folder.
  Other provided MPS example can be run by using the ``--mps`` option explained below.::

	message-ix lp-diag

- To display the available ``LPdiag`` options run::

    $ message-ix lp-diag --help
    Usage: message-ix lp-diag [OPTIONS]

      Diagnostics of basic properties of LP problems stored in the MPS format.

      Examples:
        message-ix lp-diag
        message-ix lp-diag --help
        message-ix lp-diag --mps aez.mps --outp foo.txt

    Options:
      --wdir PATH            Working directory.
      --mps PATH             MPS file name or path.
      -L, --lo-tail INTEGER  Magnitude order of the lower tail (default: -7).
      -U, --up-tail INTEGER  Magnitude order of the upper tail (default: 5).
      --outp PATH            Path for file output.
      --help                 Show this message and exit.

Further details about the optional parameters:

- :program:`--wdir`: specification of the desired work-directory (by default the work-directory is the same, in which ``LPdiag`` is located).
- :program:`--mps`: name of the MPS file to be analysed; if the file is not located in the work-directory, then the name should include the path to the file (see the example above).
- :program:`--outp`: name of the file to which the output shall be redirected.
  By default the output is listed to the stdout, i.e., to the terminal window unless the redirection is included in the command.
  Optionally, the output can be redirected to a specified file.
  Such redirection can be specified by either using the ``--outp file_name`` option, as illustrated by the second example shown above (in the output resulting from using the ``-h`` option), or by including the redirection in the corresponding command, e.g.,::

	message-ix lp-diag -h > foo.txt

- :program:`--lo-tail`, :program:`--up-tail`: These are passed to :meth:`.LPdiag.print_statistics`.
   To obtain the numbers of coefficients at every magnitude in the MPS file, specify equal or overlapping values::

    message-ix lp-diag -L 0 -U 0 --mps file.mps


Generation of the MPS file in the :mod:`message_ix` environment
---------------------------------------------------------------

The MPS-format is the oldest but still widely used for specification of the LP problems.
Most modeling environments provide various ways of the MPS file generation.

In the ``message_ix`` environment one can generate the MPS file e.g., upon solving a :class:`message_ix.Scenario` by defining in :meth:`message_ix.Scenario.solve` the ``writemps`` option together with the desired name of the MPS file.
The MPS file will then be generated and deposited in the :file:`message_ix/model/` directory.
Details are available in the `GAMS-Documentation <https://www.gams.com/latest/docs/S_CPLEX.html#CPLEXwritemps>`__

Example of specification of the corresponding option:

.. code-block:: python

	scenario.solve(solve_options={"writemps": "<file_name>.mps"})


Actual analysis
---------------

For actual analysis one needs to specify the corresponding MPS file in a command run (still in the directory ``message_ix/tools/lp_diag``)::

	message-ix lp-diag --mps loc/name

…where ``loc`` and ``name`` stand for the path to the directory where the MPS-file is located, and ``name`` stands for the corresponding file-name, respectively.
Other option(s) can be included in the command, as explained above.

If the output redirection is desired (e.g., for results to be shared or composed of many lines), then run::

	message-ix lp-diag --mps loc/name --outp outfile.txt

Extensions in the file names are optional.
An alternative way of output redirection is explained above.


Summary of the provided analysis results
========================================

The results are composed of the following elements:

- Info on the work-directory.
- Info during reading the MPS file:

	- Should a syntax error occur during reading the file, then the corresponding exception is thrown with the corresponding details.
	- Basic info during processing of each MPS section.
- Basic attributes of the read MPS.
- Distribution of values of the objective (goal function) coefficients.
- Distribution of :math:`abs(val)` of the matrix elements.
- Distribution of values of :math:`int(log10(abs(values)))`.
- Distribution of values of :math:`int(log10(abs(values)))` sorted by magnitudes of values (magnitudes of zero-occurrences skipped).
- For each (lower and upper) tail of the matrix coefficient values of the corresponding sub-matrix:

  - Distributions of diverse values (:math:`value, abs(val), log10(abs(val))`) of the matrix elements.
  - For each order of magnitude: number of elements
  - Row-wise location of each outlier with:

    1. info on other coefficients in the same row, and
    2. order of magnitude of the row's LHS and RHS.
  - Column-wise location of each outlier with:

    1. info on other coefficients in the same column, and
    2. order of magnitude of the column's lower and upper bounds.
- The processing start- and end-times.


API reference
=============

.. automodule:: message_ix.tools.lp_diag
   :members:
