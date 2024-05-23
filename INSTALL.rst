Installation
************

.. contents::
   :local:

.. toctree::
   :hidden:
   :caption: Full install
   
   install_full

Thank you for using |MESSAGEix|! We hope this documentation can help you with your modelling journey.

.. note::
   The instructions on installing |MESSAGEix| are split into two parts: a quick install and a :doc:`full install <install_full>`. 
   The quick install is based on several assumptions, see below. If you do not meet these assumptions for whatever reason, please consult the full install.

   Should you run into any issues, please consult `our issue tracker`_ to see if a solution has already been established.


Quick installation
==================

This quick install guide assumes you have read the :doc:`prerequisites <prereqs>` for understanding and using |MESSAGEix|. 
It further assumes that you have a working installation of `GAMS`_ 24.8.1 or later and that you use the default terminal on your OS.
Finally, this guide assumes that you use Python to interact with |MESSAGEix|. See :ref:`install-r` for notes on using |MESSAGEix| with R.
We strongly recommend that you are familiar with `Python's virtual environments`_ and use them for your |MESSAGEix| projects.
Depending on your choice  of installation method below, you should have either `pip`_ or `conda`_ installed on your system. If in doubt, we recommend ``pip`` for ease of usage.


Using ``pip``
-------------

This method is quick to use and relatively easy to troubleshoot.

1. Open a command prompt, activate your virtual environment, and run::

    pip install message_ix[docs,report,tests,tutorial]

This will install the latest release of |MESSAGEix|. 
The ``[docs,report,tests,tutorial]`` extra requirements ensure additional dependencies are installed and can be adapted as desired.
``docs`` allows you to build this documentation locally, ``report`` enables you to use the built-in :doc:`reporting <reporting>` functionality, ``tests`` facilitates running our test suite locally, and ``tutorial`` contains everything required for running our :doc:`tutorials <tutorials>`.

.. note::
   :meth:`.Reporter.visualize` uses `Graphviz`_, a program for graph visualization.
   Installing |MESSAGEix| causes the `graphviz <https://graphviz.readthedocs.io>`__ Python package to be installed.
   If you want to use :meth:`.visualize` or run the test suite, see the `Graphviz download page`_ for downloads and instructions for your system.
   Otherwise, it is **optional**.


Installing from GitHub
^^^^^^^^^^^^^^^^^^^^^^

The above installs the latest release of |MESSAGEix|. 
If you are instead interested in installing a specific version of the code such as a branch of our `GitHub repository`_ (e.g. the latest version of our ``main`` development branch), you can instead

1. Open a command prompt, activate your virtual environment, and run::

    pip install git+ssh://git@github.com:iiasa/message_ix.git@<branch name>[docs,report,tests,tutorial]

   This command assumes that you `use SSH to authenticate to GitHub <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#adding-your-ssh-key-to-the-ssh-agent>`__, which we recommend.
   If you use personal access tokens, please use ``... git+https://github.com/iiasa/message_ix.git@...`` instead.


Using ``conda``
---------------

This method can seem easy since ``conda`` can both manage virtual environments and install packages, but it does not always mix well with ``pip``, which advanced users will want to use.
Thus, we recommend considering ``pip`` instead.

1. Open a command prompt, activate your virtual environment, and configure ``conda`` to install :mod:`message_ix` from the conda-forge channel::

    conda config --prepend channels conda-forge

2. Install and configure the `mamba solver`_, which is faster and more reliable than conda's default solver::

    conda install conda-libmamba-solver
    conda config --set solver libmamba

3. Install the ``message-ix`` package into the current environment::

    conda install message-ix

.. note::
   If you install |MESSAGEix| using ``conda``, Graphviz is installed automatically via `its conda-forge package`_


Check that installation was successful
======================================

Verify that the version installed corresponds to the `latest release`_ by running the following commands on the command line::

    # Show versions of message_ix, ixmp, and key dependencies
    message-ix show-versions

    # Show the list of modelling platforms that have been installed and the path to the database config file
    # By default, just the local database should appear in the list
    message-ix platform list

The above commands will work as of :mod:`message_ix` 3.0 and in subsequent versions.
If an error occurs, this may mean that an older version has been installed and should be updated.
To check the current version::

    # If installed using conda
    conda list message-ix

    # If installed using pip
    pip show message-ix

.. _`our issue tracker`: https://github.com/iiasa/message_ix/issues
.. _`GAMS`: http://www.gams.com
.. _`Python's virtual environments`: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments
.. _pip: https://pip.pypa.io/en/stable/user_guide/
.. _`conda`: https://docs.conda.io/projects/conda/en/stable/
.. _`Graphviz`: https://www.graphviz.org/
.. _`Graphviz download page`: https://www.graphviz.org/download/
.. _`GitHub repository`: https://github.com/iiasa/message_ix
.. _`IIASA YouTube channel`: https://www.youtube.com/user/IIASALive
.. _`mamba solver`: https://conda.github.io/conda-libmamba-solver/
.. _`its conda-forge package`: https://anaconda.org/conda-forge/graphviz
.. _`latest release`: https://github.com/iiasa/message_ix/releases
