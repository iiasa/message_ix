Installation
************

Thank you for using |MESSAGEix|!
We hope this documentation can help you with your modelling journey.

First, **choose which install process to use**.
Use the :ref:`install-quick` steps on this page if *all* of the following apply:

- You plan to use:

  - …the latest releases of :mod:`message_ix` and :mod:`ixmp`.
  - …Python (not R) to interact with :mod:`message_ix`.
  - …the default terminal for an operating system (OS) like Ubuntu Linux, macOS, or Windows.
  - …a virtual environment to contain your |MESSAGEix| installation, as we :ref:`strongly recommend <install-venv>`.

- You have already installed on your system:

  - :ref:`Python <install-python>` (version 3.9 or later) installed, along with either :program:`pip` or :program:`conda`;
  - a :ref:`Java Runtime Environment (JRE) <install-java>` (if *not* using :program:`conda`; see :ref:`here <install-java>`); and
  - :ref:`GAMS <install-gams>` (version 24.8.1 or later).

If *any* of the above does not apply, instead consult the :doc:`install-adv`.
If the terms above are unfamiliar, you may need to review the :doc:`prereqs` for using |MESSAGEix| before you proceed.
For issues encountered during installation, see “:ref:`common-issues`” in the guide, and further resources linked there.

.. contents::
   :local:

.. toctree::
   :hidden:

   install-adv

.. _install-quick:

Quick install
=============

Choose one of the install methods below.
Depending on your choice, you should have either :program:`pip` or :program:`conda` installed on your system.
If in doubt, we recommend :program:`pip` because it is quick, easy to use and to troubleshoot.
(For more considerations, see “:ref:`install-pip-or-conda`” in the advanced guide.)

Install the latest release using :program:`pip`
-----------------------------------------------

1. Open a terminal/command prompt.

2. Activate your virtual environment.

3. Run [1]_::

    pip install message_ix[docs,report,tests,tutorial]

This will install the latest release of |MESSAGEix| from the `Python Package Index (PyPI) <https://pypi.org/project/message-ix/>`_.

.. [1] See “:ref:`install-extras`” in the advanced guide for an explanation of the ``[docs,report,tests,tutorial]`` extra requirements.
   See “:ref:`Graphviz <install-graphviz>`” if you want to use :meth:`.visualize` or run the test suite.


Install the latest release using :program:`conda`
-------------------------------------------------

1. Open a terminal/command prompt.

2. Activate your virtual environment.

3. Configure :program:`conda` to install :mod:`message_ix` from the conda-forge channel::

    conda config --prepend channels conda-forge

4. Install and configure the `mamba solver`_, which is faster and more reliable than conda's default solver::

    conda install conda-libmamba-solver
    conda config --set solver libmamba

5. Install the ``message-ix`` package into the current environment::

    conda install message-ix

This will install the latest release of |MESSAGEix| from `conda-forge <https://anaconda.org/conda-forge/message-ix>`_.

Check that installation was successful
======================================

Verify that the version installed corresponds to the latest release by running the following commands on the command line.
Show versions of :mod:`message_ix`, :mod:`ixmp`, and key dependencies::

    message-ix show-versions

The versions should correspond to the latest version shown on the :doc:`whatsnew` page.

Show the list of platforms (~databases) that have been configured and the path to the :mod:`ixmp` config file::

    message-ix platform list

See the :ref:`advanced guide <check-install>` for further details.

.. _pip: https://pip.pypa.io/en/stable/user_guide/
.. _conda: https://docs.conda.io/projects/conda/en/stable/
.. _`mamba solver`: https://conda.github.io/conda-libmamba-solver/
