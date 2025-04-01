Prerequisite knowledge & skills
*******************************

Modeling using |MESSAGEix| requires domain knowledge, understanding of certain research methods, and scientific computing skills.
This page lists these prerequisite items, grouped by different use cases.

.. contents::
   :local:

Where possible, suggested learning materials are linked.
In some cases, there are multiple options. Keep in mind that the right choice of learning materials and the time required depends on the context (e.g. formal classroom learning with an instructor vs. self-guided learning), level of prior knowledge, and learning goals.


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
     - Install the development version (source code).
   * - Use a laptop/desktop computer.
     - Use cloud computing/HPC servers.
   * - Store data on your local machine.
     - Store data in a shared database.
   * - Run/modify the :doc:`tutorial notebooks <tutorials>`.
     - Build large models from scratch.
   * -
     - Collaborate on MESSAGEix-GLOBIOM.
   * - Use the mathematical formulation as-is.
     - Modify the MESSAGE equations.
   * - Use the :mod:`message_ix` Python/R code.
     - :doc:`Contribute or request new features <contributing>`.

Basic usage
===========

Domain knowledge
----------------
You should be able to:

1. Understand mathematical optimization, linear programming, and/or the calculus underlying these.
2. Understand concepts including:

   - Energy systems, including their components: resources, supply-side technologies, demand and end-use.
   - Levels (such as primary or secondary energy) in an energy system.
   - Efficiency of energy use or transformation.
   - Costs, including the distinction between fixed costs, variable costs, and investment costs.

Scientific computing skills
---------------------------
You should be able to:

1. Install and uninstall software on your operating system (OS): one of Linux, Windows, or macOS.

2. Use a command line (terminal, command prompt) on your OS to navigate directories and files, run commands, and view their output.

3. Modify environment variables on your OS.

4. Write simple programs in Python or R, including:

   - Understand concepts including: variables, functions, and arguments.
   - Use control flow structures such as ``if`` statements and various types of loops.
   - Access and read the documentation for the core language.
   - Use a search engine to find code examples and to diagnose error messages.

   For Python, `Dive Into Python <https://diveinto.org/python3/table-of-contents.html>`_ is one beginner resource.
   Many free and paid online courses are available.

5. Understand the **concepts of a software package**, software release, version number (in particular the concept of `semantic versioning <https://semver.org>`_), and deprecation.
   See :ref:`releases` for specific practices used for :mod:`message_ix`.

.. _prereq-venv:

6. Understand the concept of **virtual environments** for Python, using either
   the built-in :mod:`venv` module (`docs <https://docs.python.org/3/library/venv.html>`__, `usage with pip`_), or `Anaconda environments`_ to create, activate, switch, and remove environments.

   The :ref:`install-quick` and :doc:`install-adv` give instructions for the above two systems, but several others are in common use including
   `virtualenv <https://virtualenv.pypa.io/en/latest/index.html>`__ and `virtualfish <https://virtualfish.readthedocs.io/en/latest/>`__.

7. **Manage Python packages**—that is, install, uninstall, upgrade, and check installed versions—using at least one of:

   - The `Anaconda Navigator <https://docs.anaconda.com/anaconda/navigator/>`_ graphical interface,
   - the :program:`conda` command-line interface (`documentation <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html#installing-packages>`__), or
   - :program:`pip`.

8. Understand or learn the basic concepts functionality of widely-used Python data science packages:

   - `Introductory tutorials <https://pandas.pydata.org/docs/getting_started/index.html#intro-to-pandas>`__ for pandas, including the concept of a **series** and **data frame**.

9. Use a **Jupyter notebook** to run Python or R code, including: start the notebook server; open, restart, and close notebooks; create and edit cells.

   - `Jupyter notebook <https://jupyter-notebook.readthedocs.io/en/stable/notebook.html>`_ official documentation.
   - Video introductions to the notebook.
     `Example 1 <https://www.youtube.com/watch?v=jZ952vChhuI>`_ by Michael Fudge (English, 7 minutes)
     `Example 2 <https://www.youtube.com/watch?v=HW29067qVWk>`_ by Corey Schafer (English, 30 minutes), both on YouTube.
     Many are available on other platforms.
   - An `in-depth tutorial <https://www.datacamp.com/community/tutorials/tutorial-jupyter-notebook>`_ by Karlijn Williams on DataCamp.

.. _prereq-rfc2119:

10. Know the :rfc:`2119` keywords **must**, **must not**, **required**, **shall**, **shall not**, **should**, **should not**, **recommended**,  **may**, and **optional**, and their meanings.

Advanced usage
==============
The following items may be more or less.

Domain knowledge
----------------
You should be able to:

1. Understand concepts including:

   - Capacity factor of a power-generating technology.
   - Deprecation.

Scientific computing skills
---------------------------
You should be able to:

1. Interact with a server or ‘headless’ computer, i.e. one without a graphical interface, over the command line, using SSH.

2. Use the ``pip`` command-line interface (`documentation <https://pip.pypa.io/en/stable/user_guide/#installing-packages>`__) to install, uninstall, upgrade, and check the versions of Python packages.

3. Use the **Git version control system** and the ``git`` command-line tool to clone repositories, pull, fetch, create branches, and push.
   For :doc:`contributing to development <contributing>`, you should know how to:

   - `git merge <https://git-scm.com/docs/git-merge>`_, i.e. bring all updates from the ``main`` branch into your PR branch, giving you a chance to fix conflicts and make a new commit.
   - `git rebase <https://git-scm.com/docs/git-rebase>`_, i.e. replay your PR branch commits one-by-one, starting from the tip of the ``main`` branch (rather than the original starting commit).

   Optionally, do these things via a graphical program such as GitHub Desktop.

   - The free `Pro Git book <https://git-scm.com/book/en/v2>`_.
   - Interactive learning tools on `try.github.io <http://try.github.io/>`_.

4. Understand and interact with repositories and issues on **GitHub**, including:

   - Find and read the list of issues for a repository.
   - Search within one repository or across all of GitHub.
   - Use GitHub's formatting to produce legible descriptions of code and code errors.
   - Understand concepts including: pull request, merge, merge conflict, assign, review.

   See:

   - `Documentation for the GitHub website <https://docs.github.com/en/github>`_
   - `Short introduction to the Github 'flow' <https://guides.github.com/introduction/flow/>`_, which describes a **pull request** and how it is used.
   - Interactive tools in the `Learning Lab <https://lab.github.com/>`_.

5. Provide a complete and explicit description of a software error message and how to reproduce it.

6. Read and understand GAMS code.

.. _`usage with pip`: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments
.. _`Anaconda environments`: https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html
