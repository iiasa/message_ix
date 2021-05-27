.. TODO this page should eventually be renamed from rmessageix to discontinue usage of that name.

Usage in R via ``reticulate``
*****************************

:mod:`message_ix` and :mod:`ixmp` are fully usable in R via `reticulate`_, a package that allows nearly seamless access to the Python API.
See :doc:`install` for instructions on installing R and reticulate.
No additional R packages are needed. [1]_

Once installed, use reticulate to import the Python packages:

.. code-block:: R

   library(reticulate)
   ixmp <- import("ixmp")
   message_ix <- import("message_ix")

This creates two global variables, ``ixmp`` and ``message_ix``, that can be used much like the Python modules:

.. code-block:: R

   mp <- ixmp$Platform(name = "default")
   scen <- message_ix$Scenario(mp, "model name", "scenario name")
   # etc.

See the R versions of the :ref:`Austria tutorials <austria-tutorials>` for full examples of building models.

Some tips:

- If using Anaconda, you may need to direct reticulate to use the Python executable from the same conda environment where :mod:`message_ix` and :mod:`ixmp` are installed.
  See the reticulate documentation for usage of commands like:

  .. code-block:: R

    # Specify python binaries and environment under which messageix is installed
    use_condaenv("message_env")
    # or
    use_python("C:/.../anaconda3/envs/message_env/")

- As shown above, R uses the ``$`` character instead of ``.`` to access methods and properties of objects.
  Where Python code examples show, for instance, ``scen.add_par(...)``, R code should instead use ``scen$add_par(...)``.
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



.. _`reticulate`: https://rstudio.github.io/reticulate/
.. [1] The former ``rmessageix`` and ``rixmp`` packages were removed in :mod:`message_ix`/:mod:`ixmp` :ref:`v3.3.0`.
