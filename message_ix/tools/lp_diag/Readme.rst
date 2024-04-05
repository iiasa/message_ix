.. LPdiag documentation file

``LPdiag``: basic diagnostics of the LP programming problems
============================================================

Description
-----------

``LPdiag`` provides basic information about the LP programming problems
defined by corresponding MPS-format files.
The diagnostics focuses on the implied numerical properties of the underlying
optimization problem.

In this context, the term `outlier` denotes the model entities having values
in either lower or upper tail of the corresponding value distribution.
The tails are defined by the corresponding orders of magnitudes defined as
:math:`int(alog(abs(val)))`, where :math:`val` stands for the value of
the corresponding coefficient.
The default values of the tails are equal to (-6, 6), respectively;
they can be redefined, if desired.

The rule of thumb says: the maximum and minimum orders of magnitudes of
the LP matrix coefficients passed to optimization should differ by at most four.
``LPdiag`` helps to achieve such a goal by providing info on outliers.
Such info can be used e.g., for:

- reconsideration of measurement units of the corresponding variables
  and relations,
- consideration of replacing `small` (in relations to other coefficients in
  the same row or column) by zero,
- splitting the corresponding rows and/or columns,
- verification of the coefficients' values.

Features
^^^^^^^^

The current ``LPdiag`` version provides the following information:

- characteristics of the problem (including numbers of rows, columns, non-zero
  coefficients and distributions of their values),
- distributions of diverse values characterizing the LP matrix,
- location (row and column) of each outlier,
- ranges of values of other coefficients in each such row or column, as well as
  the corresponding bounds (LHS, RHS for rows, lower and upper bounds for
  columns).

The functionality of ``LPdiag`` will be gradually enhanced to meet actual needs
of the ``message_ix`` modelers.

Usage
-----

The tool analyzes provided MPS-format files.
We provide several small MPSs for testing local installations, as well
as becoming familiar with ``LPdiag``.
Hints on generating MPS files are provided below.

We suggest the following steps for becoming familiar with ``LPdiag`` and
then use it for analysis of actual MPS files:

- becoming familiar with ``LPdiag``,
- prepare MPS file,
- actual analysis.

We outline each of these steps below.

Becoming familiar with ``LPdiag``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that ``LPdiag`` should be run at the terminal prompt.

- Navigate to the folder `message_ix/tools/lp_diag`. 
- For initial testing run the following command, which will run analysis of
  the default (pre-specified) MPS provided in the test_mps folder.
  Other provided MPS example can be run by using the ``--mps`` option explained
  below. ::

	python lpdiag.py

- To display the available ``LPdiag`` options run: ::

	python lpdiag.py -h

The output of the above should read as follows (except of the work_dir line,
which differs for each local repository): ::

	work_dir: '/Users/marek/Documents/GitHub/marek_iiasa/message_ix/message_ix/tools/lp_diag'.
	usage: lpdiag.py [-h] [--wdir WDIR] [--mps MPS] [--outp OUTP]
	Diagnostics of basic properties of LP Problems represented by the MPS-format.
	Examples of usage:
	python lpdiag.py
	python lpdiag.py -h
	python lpdiag.py --mps test_mps/aez --outp foo.txt
	options:
	-h, --help   show this help message and exit
	--wdir WDIR  --wdir : string Working directory.
	--mps MPS    --mps : string Name of the MPS file (optionally with path).
	--outp OUTP  --outp : string Redirect output to the named file.

Comments on the arguments of the above three options:

- WDIR: specification of the desired work-directory (by default the work-directory
  is the same, in which ``LPdiag`` is located).
- MPS: name of the MPS file to be analysed; if the file is not located in the
  work-directory, then the name should include the path to the file (see
  the example above).
- OUTP: name of the file to which the output shall be redirected.
  By default the output is listed to the stdout, i.e., to the terminal window
  unless the redirection is included in the command.
  Optionally, the output can be redirected to a specified file.
  Such redirection can be specified by either using the ``--outp file_name``
  option, as illustrated by the second example shown above (in the output
  resulting from using the ``-h`` option),
  or by including the redirection in the corresponding command, e.g.,: ::

	python lpdiag.py -h > foo.txt


Generation of the MPS file in the ``message_ix`` environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The MPS-format is the oldest but still widely used for specification of
the LP problems.
Most modeling environments provide various ways of the MPS file generation.

In the ``message_ix`` environment one can generate the MPS file e.g.,
upon solving a :class:`message_ix scenario` by defining
in `scenario.solve()` the `writemps` option together with the desired name of
the MPS file.
The MPS file will then be generated and deposited in the `message_ix/message_ix/model`
folder.
Details are available in the GAMS-Documentation:
https://www.gams.com/latest/docs/S_CPLEX.html#CPLEXwritemps

Example of specification of the corresponding option::

	`scenario.solve(solve_options={"writemps": "<file_name>.mps"})`


Actual analysis
^^^^^^^^^^^^^^^

For actual analysis one needs to specify the corresponding MPS file in
a command run (still in the directory `message_ix/tools/lp_diag`): ::

	python lpdiag.py --mps loc/name

where `loc` and `name` stand for the path to the directory where the MPS-file is
located, and `name` stands for the corresponding file-name, respectively.
Other option(s) can be included in the command, as explained above.

If the output redirection is desired (e.g., for results to be shared or composed
of many lines), then run: ::

	python lpdiag.py --mps loc/name --outp outfile.txt

Extensions in the file names are optional.
An alternative way of output redirection is explained above.


Summary of the provided analysis results
----------------------------------------

The results are composed of the following elements:

- Info on the work-directory.
- Info during reading the MPS file:

	- Should a syntax error occur during reading the file, then the corresponding
	  exception is thrown with the corresponding details.
	- Basic info during processing of each MPS section.
- Basic attributes of the read MPS.
- Distribution of values of the objective (goal function) coefficients.
- Distribution of :math:`abs(val)` of the matrix elements.
- Distribution of values of :math:`int(log10(abs(values)))`.
- Distribution of values of :math:`int(log10(abs(values)))` sorted by
  magnitudes of values (magnitudes of zero-occurrences skipped).
- For each (lower and upper) tail of the matrix coefficient values of the
  corresponding sub-matrix:

  - Distributions of diverse values (:math:`value, abs(val), log10(abs(val))`)
    of the matrix elements.
  - For each order of magnitude: number of elements
  - Row-wise location of each outlier with:
    (1) info on other coefficients in the same row, (2) order of magnitude of the row's LHS and RHS.
  - Column-wise location of each outlier with:
    (1) info on other coefficients in the same column, and (2) order of magnitude of the column's lower and upper bounds.
- The processing start- and end-times.

