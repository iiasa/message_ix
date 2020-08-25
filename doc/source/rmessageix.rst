R API (``rmessageix``)
**********************

Support for :mod:`message_ix` and :mod:`ixmp` in R are provided through `reticulate`_, a package that allows nearly seamless access to the Python API.

.. _`reticulate`: https://rstudio.github.io/reticulate/

See :doc:`install` for instructions on installing the ``rmessageix`` R package.
Once installed, load the package:

.. code-block:: R

   library(rmessageix)

This creates two global variables, ``ixmp`` and ``message_ix``, that can be used much like the Python modules:

.. code-block:: R

   mp <- ixmp$Platform(name = "default")
   scen <- message_ix$Scenario(mp, "model name", "scenario name")
   # etc.

See the R versions of the :ref:`Austria tutorials <austria-tutorials>` for full model examples using ``rmessageix``.

Some tips:

- As shown above, R uses the ``$`` character instead of ``.`` to access methods and properties of objects.
  Where Python code examples show, for instance, ``scen.add_par(...)``, R code should use ``scen$add_par(...)``.
- |MESSAGEix| model parameters with dimensions indexed by the ``year`` set (e.g. dimensions named ``year_act`` or ``year_vtg``) must be indexed by integers; but R treats numeric literals as floating point values.
  Therefore, instead of:

  .. code-block:: R

     ya1 = 2010
     ya2 = c(2020, 2030, 2040)
     ya3 = seq(2050, 2100, 10)

     # ...store parameter data using year_act = ya1, ya2, or ya3

  …use ``as.integer()`` to convert:

  .. code-block:: R

     ya1 = as.integer(2010)
     ya2 = sapply(c(2020, 2030, 2040), as.integer)
     ya3 = as.integer(seq(2050, 2100, 10))
