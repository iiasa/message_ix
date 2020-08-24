Prerequisite knowledge & skills
*******************************

Energy systems modeling using |MESSAGEix| requires domain knowledge, understanding of certain research methods, and scientific computing skills.
This page lists these *prerequisite* items, grouped by different uses cases; where possible, suggested learning materials are linked.


What is my use case?
====================

There are many different use cases for |MESSAGEix|.
This page currently distinguishes between “basic” and “advanced”:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Basic usage
     - Advanced usage
   * - Install the released version of :mod:`message_ix`.
     - Install the development version from source code.
   * - Use a laptop/desktop computer.
     - Use cloud computing/HPC servers.
   * - Store data on your local machine.
     - Store data in a shared database.
   * - Run/modify the Jupyter tutorial notebooks.
     - Build large models from scratch.
   * -
     - Collaborate on MESSAGEix-GLOBIOM.
   * - Use the existing mathematical formulation.
     - Modify the MESSAGE equations.
   * - Use :mod:`message_ix` as-is.
     - Contribute or request new features.

Basic usage
===========
You should be able to:

Domain knowledge
----------------

1. Understand mathematical optimization, linear programming, and/or the calculus underlying these.
2. Understand concepts including:

   - Energy system
   - Levels (such as primary or secondary energy) in an energy system.
   - Efficiency of energy use or transformation.
   - Costs, including the distinction between fixed costs, variable costs, and investment costs.

Scientific computing skills
---------------------------

1. Install and uninstall software on your operating system (OS): one of Linux, Windows, or macOS.
2. Use a command line on your OS.
3. Modify environment variables on your OS.
4. Write simple programs in Python or R, including:

   - Understand concepts including: variables, functions, and arguments.
   - Use control flow structures such as ``if`` statements and various types of loops.
   - Access and read the documentation for the core language.
   - Use a search engine to find code examples and to diagnose error messages.

5. Use the `Anaconda Navigator <https://docs.anaconda.com/anaconda/navigator/>`_ graphical interface or the ``conda`` command-line interface (`documentation <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#installing-packages>`__) to install, uninstall, upgrade, and check the versions of Python packages.
   Understand the concept of `conda environments <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_; create, activate, switch, and remove environments.
6. Understand or learn the basic functionality of Python data science packages, including pandas.
7. Use a Jupyter notebook to run Python or R code, including: start the notebook server; open, restart, and close notebooks; create and edit cells.

Resources:

- `Dive Into Python <https://diveinto.org/python3/table-of-contents.html>`_.


Advanced usage
==============
Depending on the specific use case, you should be able to:

Domain knowledge
----------------

1. Understand concepts including:

   - Capacity factor of a power-generating technology.
   - Deprecation.

Scientific computing skills
---------------------------

1. Use the ``pip`` command-line interface (`documentation <https://pip.pypa.io/en/stable/user_guide/#installing-packages>`__) to install, uninstall, upgrade, and check the versions of Python packages.
2. Use the Git version control system and the ``git`` command-line tool to clone repositories, pull, fetch, create branches, and push.
   Optionally, do these things via a graphical program such as GitHub Desktop.
3. Understand and interact with repositories and issues on GitHub, including:

   - Find and read the list of issues for a repository.
   - Search within one repository or across all of GitHub.
   - Use GitHub's formatting to produce legible descriptions of code and code errors.
4. Provide a complete and explicit description of a software error message and how to reproduce it.
5. Read and understand GAMS code.
