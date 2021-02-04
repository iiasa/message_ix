.. note:: This page is generated from inline documentation in ``MESSAGE\model_solve.gms``.

Solve statement workflow
========================

This part of the code includes the perfect-foresight, myopic and rolling-horizon model solve statements
including the required accounting of investment costs beyond the model horizon.

Perfect-foresight model
~~~~~~~~~~~~~~~~~~~~~~~
For the perfect foresight version of |MESSAGEix|, include all years in the model horizon and solve the entire model.
This is the standard option; the GAMS global variable ``%foresight%=0`` by default.

.. math::
   \min_x OBJ = \sum_{y \in Y} OBJ_y(x_y)

Recursive-dynamic and myopic model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the myopic and rolling-horizon models, loop over horizons and iteratively solve the model, keeping the decision
variables from prior periods fixed.
This option is selected by setting the GAMS global variable ``%foresight%`` to a value greater than 0,
where the value represents the number of years that the model instance is considering when iterating over the periods
of the optimization horizon.

Loop over :math:`\hat{y} \in Y`, solving

.. math::
    \min_x \ OBJ = \sum_{y \in \hat{Y}(\hat{y})} OBJ_y(x_y) \\
    \text{s.t. } x_{y'} = x_{y'}^* \quad \forall \ y' < y

where :math:`\hat{Y}(\hat{y}) = \{y \in Y | \ |\hat{y}| - |y| < optimization\_horizon \}` and
:math:`x_{y'}^*` is the optimal value of :math:`x_{y'}` in iteration :math:`|y'|` of the iterative loop.

The advantage of this implementation is that there is no need to 'store' the optimal values of all decision
variables in additional reporting parameters - the last model solve automatically includes the results over the
entire model horizon and can be imported via the ixmp interface.

