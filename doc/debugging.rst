.. _debugging:

Debugging and data validation
=============================

Finding the cause for infeasibilities or counter-intuitive results in large-scale numerical models is not trivial.
For this reason, the |MESSAGEix| framework includes a number of features to simplify debugging and pre-processing data validation.

Pre-processing data validation
------------------------------

The data validation checks are included in the file ``model/MESSAGE/data_load.gms``.
If the data validation fails, an error message is written to the log file.

Identification of infeasibilities
---------------------------------

The |MESSAGEix| framework includes the option to "relax" the most common constraints, simultaneously adding a penalty term for the relaxation to the objective function.
Solving the relaxed version of the model can help to identify incompatible constraints or input data errors causing infeasible models.

The relaxations can be activated by blocks/types of equations by setting the respective global variables (``$SETGLOBAL`` in GAMS) in ``MESSAGE_master.gms`` or by calling ``MESSAGE_run.gms`` passing the global variables as command-line arguments.
