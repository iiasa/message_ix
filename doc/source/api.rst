Python & R API
==============

The application programming interface (API) for |MESSAGEix| model developers
is implemented in Python. Support for R usage of the core classes is provided
through the `reticulate`_ package. For instance::

    > library(reticulate)
    > message <- library("message_ix")
    > s <- messageix$Scenario(…)

.. _`reticulate`: https://rstudio.github.io/reticulate/

.. toctree::

   api/ixmp.rst
   api/message_ix.rst
