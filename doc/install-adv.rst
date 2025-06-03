Advanced installation guide
***************************

This guide includes detailed instructions for a variety of ways of installing |MESSAGEix| in cases beyond the simple case covered by the :doc:`Quick install instructions <install>`.

Again, be sure that you have the :doc:`prerequisites skills and knowledge <prereqs>`; these include specific points of knowledge that are necessary to understand these instructions and choose among different installation options.

.. contents::
   :local:

.. _system-dependencies:

Install system dependencies
===========================

.. _install-python:

Python (required)
-----------------

|MESSAGEix| requires Python version 3.9 or greater.
We recommend the latest version; currently Python 3.13.
Common ways to install Python include:

- Use the official `Python releases <https://www.python.org/downloads/>`_.
- Use a third-party Python distribution, such as `Miniconda`_ or `Anaconda`_. [1]_ [2]_
- Use a version of Python bundled with your operating system (for example, Ubuntu and other Linux distributions).

Before making this choice, see :ref:`install-pip-or-conda`, below, for further considerations.

.. [1] See the `conda glossary`_ for the differences between Anaconda and Miniconda, and the definitions of the terms ‘channel’ and ‘environment’ here.
.. [2] On newer macOS systems with Apple M-series processors: the Miniconda or Anaconda installers provided for the ``arm64`` architecture lead to errors in :mod:`ixmp`.
   Currently, we recommend to instead use the macOS installers for ``x86_64`` architecture on these systems.
   See :mod:`ixmp` issues `473 <https://github.com/iiasa/ixmp/issues/473>`_ and `531 <https://github.com/iiasa/ixmp/issues/531>`_.

.. _install-java:

Java (required)
---------------

A `Java Runtime Environment (JRE) <https://en.wikipedia.org/wiki/Java_(software_platform)#Java_Runtime_Environment>`_ is required
to use :class:`ixmp.JDBCBackend <ixmp.backend.jdbc.JDBCBackend>`,
the current default in the :mod:`ixmp` package that handles data storage for :mod:`message_ix`.

There are many ways to install a JRE.
Most often this is done by installing a Java Development Kit (JDK),
of which the most popular is OpenJDK.

- Linux operating systems like Ubuntu often have specific packages containing OpenJDK/the JRE,
  with names like ``openjdk-25-jre``.
- OpenJDK is also `built and packaged by many providers <https://en.wikipedia.org/wiki/OpenJDK#OpenJDK_builds>`_;
  these packages are known by different names
  and are available for operating systems including Windows and macOS.
  Some of these known to work with JDBCBackend include:

  - `Temurin <https://adoptium.net/temurin/releases/>`_.
  - `Zulu <https://www.azul.com/downloads/?package=jre#zulu>`_.
  - `Corretto <https://aws.amazon.com/corretto/>`_.

.. caution::

   Oracle provides releases branded simply “Java” at https://www.java.com,
   as well as `Oracle OpenJDK builds <https://jdk.java.net/>`_.
   Not all of these are free to use;
   for instance, use by several people in the same organization may require a paid license.
   `This news article <https://www.theregister.com/2025/05/09/users_advised_to_review_oracle_java_use/>`__ and other coverage
   explain how license fee demands may come as a surprise to users.

   We recommend one of the above, non-Oracle alternatives, which do not use paid licensing.

If using Anaconda or Miniconda, installing a JDK/JRE manually is *not required*.
This is because the ``message-ix`` conda-forge package depends on the `openjdk <https://anaconda.org/conda-forge/openjdk>`_ package,
so the latter is automatically installed with the former.


.. _install-gams:

GAMS (required)
---------------

|MESSAGEix| requires `GAMS`_.

1. Download GAMS for your operating system; either the `latest version`_ or, for users not familiar with GAMS licenses, `version 29`_ (see note below).

2. Run the installer.

3. Ensure that the ``PATH`` environment variable on your system includes the path to the GAMS program:

   - on Windows, in the GAMS installer…

      - Check the box labeled “Use advanced installation mode.”
      - Check the box labeled “Add GAMS directory to PATH environment variable” on the Advanced Options page.

   - on macOS, in the GAMS installer…

      - When prompted to specify the "Installation Type" (step 3 of the installation process), select "Customise".
      - Check the box labeled "Add GAMS to PATH".

     If this option is not available see instructions below.

   - on other platforms (macOS or Linux), add the following line to a file such as :file:`~/.bash_profile` (macOS), :file:`~/.bashrc`, or :file:`~/.profile`::

       $ export PATH=$PATH:/path/to/gams-directory-with-gams-binary

   Run :program:`gams` in a terminal/command prompt to confirm this step has taken effect.

.. note::
   MESSAGE-MACRO and MACRO require GAMS 24.8.1 or later (see :attr:`.MACRO.GAMS_min_version`)
   The latest version is recommended.

   GAMS is proprietary software and requires a license to solve optimization problems.
   To run both the :mod:`message_ix` and :mod:`ixmp` tutorials and test suites, a “free demonstration” license is required; the free license is suitable for these small models.
   Versions of GAMS up to `version 29`_ include such a license with the installer; since version 30, the free demo license is no longer included, but may be requested via the GAMS website.

.. note::
   If you only have a license for an older version of GAMS, install both the older and the latest versions.

.. _install-graphviz:

Graphviz (optional)
-------------------

:meth:`.Reporter.visualize` uses `Graphviz`_, a program for graph visualization.
Installing :mod:`message_ix` causes the `graphviz <https://graphviz.readthedocs.io>`__ Python package to be installed.
If you want to use :meth:`.visualize` or run the test suite, the Graphviz program itself must also be installed; otherwise it is **optional**.

If you install MESSAGEix :ref:`using conda <using-conda>`, Graphviz is installed automatically via `its conda-forge package`_.
For other methods of installation (such as :program:`pip`) see the `Graphviz download page`_ for downloads and instructions for your system.

Install |MESSAGEix|
===================

4. Open a terminal/command prompt.

   Windows users who have installed Python using Anaconda/Miniconda should use the “Anaconda Prompt” to avoid issues with permissions and environment variables.
   This program is available in the Windows Start menu after installing Anaconda.

.. _install-pip-or-conda:

Choose :program:`pip` or :program:`conda`
-----------------------------------------

We recommend that new users install |MESSAGEix| using :program:`pip` (`user guide <https://pip.pypa.io/en/stable/user_guide/>`_), the package manager recommended by the Python Software Foundation.
:program:`pip` can be used when Python is installed directly, or it can be installed using :program:`conda`. [3]_

If you are more comfortable with Anaconda, you can also install |MESSAGEix| using :program:`conda`.

Advanced users may choose to install from source code, to benefit from the latest features or to test features that have not been merged.
For this purpose :program:`pip` *must* be used; while it is possible to do this within an initial install made using :program:`conda`, [3]_ it is usually simpler not to mix the two and instead use :program:`pip` from the start.

Whichever option you choose, please skip the other sections.

.. [3] If you intend to use :program:`pip` in a :program:`conda` environment, please read `conda's guide to using pip in an environment <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`__.
   In particular, please make sure to use :program:`conda` *only* to install :program:`pip` into an environment, and then use that environment-specific :program:`pip` for all further package installation.

.. _install-venv:

Create and activate a virtual environment
-----------------------------------------

See :ref:`Prerequisite knowledge and skills > Basic usage > Scientific computing skills > #6 <prereq-venv>`.
In particular, the two links given for :mod:`venv` module documentation explain the general concept of virtual environments.

For |MESSAGEix| usage, many users choose to create *one virtual environment for each project*, and switch between those environments in order to switch between project-specific versions of :mod:`message_ix`, :mod:`ixmp`, :mod:`message_ix_models`, and any other dependencies.

It is also possible to use |MESSAGEix| *without* a virtual environment, but we strongly recommend that you create and use one.
The way of doing so depends on whether you chose:

- :program:`pip` —then the steps further depend on which virtual environment tool you choose.
  This guide gives examples for the first-party :mod:`venv` and third-party `virtualenv <https://virtualenv.pypa.io/en/latest/user_guide.html#quick-start>`_; for others, see their documentation.
- :program:`conda` —this program handles *both* virtual environment *and* package management.

See the respective sections below.

Use :program:`pip`
------------------

5. Create a virtual environment.
   Using :mod:`venv`, per `the documentation <https://docs.python.org/3/library/venv.html#creating-virtual-environments>`_::

     python -m venv message_env

   or using :program:`virtualenv`::

    virtualenv message_env

   These examples store the environment files in a directory named :file:`message_env` under the current working directory, but you can also place these anywhere else on your system.

6. Activate the environment with::

    # On Linux or macOS
    source message_env/bin/activate

    # On Windows
    .\message_env\Scripts\activate

   These examples use the directory created in the previous step.
   If you stored your virtual environment elsewhere, use the appropriate path.

7. Ensure :program:`pip` is installed::

    pip --version

   If not, see the `installation instructions for pip <https://pip.pypa.io/en/stable/installation/>`_.

.. _install-extras:

Choose optional dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When installing using :program:`pip` (but not :program:`conda`),
there is a distinction between **required** and **optional dependencies**.
For example :mod:`ixmp` is a required dependency of :mod:`message_ix`.
Whenever the latter is installed,
a compatible version of the former will also be installed.

Optional dependencies (also called “extra requirements”) are gathered in groups.
The example commands below include a string like ``[tests]``.
This implies five of the six available groups of extra requirements:

- ``docs`` includes packages required to build this documentation locally,
  including ``message_ix[report]`` and all *its* requirements,
- ``ixmp4`` includes packages require to use :class:`ixmp.IXMP4Backend <.IXMP4Backend>`,
- ``report`` includes packages required to use the built-in :doc:`reporting <reporting>` features of :mod:`message_ix`,
- ``sankey`` includes packages required to use :meth:`.Reporter.add_sankey`,
- ``tests`` includes packages required to run the test suite,
  including ``message_ix[docs]``, ``message_ix[tutorial]``,
  and all the requirements in those groups, and
- ``tutorial`` includes packages required to run the :doc:`tutorials <tutorials>`,
  including ``message_ix[report]``, ``message_ix[sankey]``, etc.

The set of extras used can be freely adjusted according to your needs.

Install the latest release from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

8. Install |MESSAGEix| [4]_::

    pip install message_ix[tests]

.. [4] If using the (non-standard) :program:`zsh` shell, note or recall that ``[...]`` is a `glob operator <https://zsh.sourceforge.io/Doc/Release/Expansion.html#Glob-Operators>`__, so the argument to pip must be quoted appropriately: ``pip install -e '.[tests]'``.

At this point, installation is complete.
Next, you can `Check that installation was successful`_.

Install from GitHub
~~~~~~~~~~~~~~~~~~~

The above installs the latest release of |MESSAGEix|.
If you are instead interested in installing a specific version of the code such as a branch of the :mod:`message_ix` `GitHub repository <https://github.com/iiasa/message_ix>`_, instead:

8. Run the following.
   Replace ``<ref>`` with a specific Git reference such as a branch name (for instance, the ``main`` development branch, or a branch associated with a pull request), a tag, or a commit hash::

    pip install git+ssh://git@github.com:iiasa/message_ix.git@<ref>[tests]

   ``git+ssh://`` assumes that you `use SSH to authenticate to GitHub <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>`__, which we recommend.
   If you instead use personal access tokens, then run::

    pip install git+https://github.com/iiasa/message_ix.git@<ref>[tests]

At this point, installation is complete.
Next, you can `Check that installation was successful`_.

Install from a :program:`git` clone of the source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   If you want to install |MESSAGEix| from source, but already have an install from :program:`pip`, please make sure to first :program:`pip uninstall message-ix`.
   Otherwise, Python might not recognize your new install correctly.
   A symptom of this error is a message like “'message_ix' has no attribute 'Scenario'”.

8. Install :doc:`ixmp <ixmp:install>`, either *also* from source, or from PyPI.
   Use the same combination of major and minor versions: for instance, if installing :mod:`message_ix` version 3.9.x from source, install :mod:`ixmp` version 3.9.x.

9. (Optional) If you intend to contribute changes to |MESSAGEix|, first register a GitHub account, and fork the `message_ix repository <https://github.com/iiasa/message_ix>`_.
   This will create a new repository ``<user>/message_ix``.
   (Please also see :doc:`contributing`.)

10. Clone either the main repository, or your fork; using the `Github Desktop`_ client, or the command line::

     git clone git@github.com:iiasa/message_ix.git

     # or:
     git clone git@github.com:USER/message_ix.git

11. (Optional) If you cloned your fork, add the main repository as a remote git repository.
    This allows to stay up to date with changes there and to import tags, which also must be done for the install tests to succeed::

     git remote add upstream git@github.com:iiasa/message_ix.git
     git fetch upstream --tags

12. Navigate to the :file:`message_ix/` directory created by :program:`git clone`.
    Run [4]_::

     pip install --editable .[tests]

    The :program:`--editable` flag ensures that changes to the source code are picked up every time :py:`import message_ix` is used in Python code.

At this point, installation is complete.
Next, you can `Check that installation was successful`_.

.. _using-conda:

Use :program:`conda`
--------------------

.. note:: An earlier version of the instructions from this section are available as a narrated video on the `IIASA YouTube channel`_.
   If you are a beginner, you may want to watch the video before attempting the installation yourself.

   .. raw:: html

      <iframe width="690" height="360" src="https://www.youtube.com/embed/QZw-7rIqUJ0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

5. Configure conda to install :mod:`message_ix` from the conda-forge channel::

    conda config --prepend channels conda-forge

6. Install and configure the `mamba solver`_, which is faster and more reliable than conda's default solver::

    conda install conda-libmamba-solver
    conda config --set solver libmamba

7. Create a new conda environment and activate it.
   This step is **required** if using Anaconda, but *optional* if using Miniconda.
   This example uses the name ``message_env``, but you can use any name of your choice::

    conda create --name message_env
    conda activate message_env

8. Install the ``message-ix`` package into the current environment (either ``message_env``, or another name from the previous step) [5]_::

    conda install message-ix

At this point, installation is complete.
Next, you can `Check that installation was successful`_.

.. [5] Notice that conda uses the hyphen (‘-’) in package names, different from the underscore (‘_’) used in Python when importing the package.

.. note:: When using Anaconda (not Miniconda), steps (5) through (8) can also be performed using the graphical Anaconda Navigator.
   See the `Anaconda Navigator documentation`_ for how to perform the various steps.

.. _check-install:

Check that installation was successful
======================================

Verify that the version installed corresponds to the `latest release`_ by running the following commands on the command line::

    # Show versions of message_ix, ixmp, and key dependencies
    message-ix show-versions

    # Show the list of platforms (~databases) that have been configured
    # and the path to the ixmp config file. By default, only the "local"
    # platform, backed by a local database, should appear in the list
    message-ix platform list

The above commands will work as of :mod:`message_ix` 3.0 and in subsequent versions.
If an error occurs, this may mean that an older version has been installed unintentionally.
To check the installed version directly::

    # If installed using pip
    pip show message-ix

    # If installed using conda
    conda list message-ix

For an install from source, it is possible to run the built-in test suite to check that |MESSAGEix| functions correctly on your system.
This requires that the ``[tests]`` extra dependencies were installed.
In the directory created by :program:`git clone`, run::

    pytest

.. _install-r:

Install R and reticulate
========================

You only need to install R if you want to use :mod:`message_ix` and :mod:`ixmp` from R, rather than from Python.

First, install :mod:`message_ix` using one of the three methods above.
Then:

1. `Install R <https://www.r-project.org>`_.

   .. warning::
      Ensure the the R version installed is either 32- *or* 64-bit (and >= 3.5.0), consistent with GAMS and Java.
      Having both 32- and 64-bit versions of R, or mixed 32- and 64-bit versions of different packages, can cause errors.

2. `Install reticulate <https://rstudio.github.io/reticulate/#installation>`_.

3. (Optional) Install `IRkernel`_, which allows running R code in Jupyter notebooks (see the link for instructions).

Next:

- See :doc:`rmessageix` for further details.

- If you installed :mod:`message_ix` from source, check that the R interface works by using the built-in test suite to run the R tutorial notebooks::

    $ pytest -m rmessageix


.. _common-issues:

Common issues
=============

If you run into an issue during installation that is not listed below, check the |MESSAGEix| `issue tracker`_ for an existing report, workaround, and/or solution.

“No JVM shared library file (jvm.dll) found”
--------------------------------------------

Error messages like this when running :program:`message-ix --platform=default list` or when creating a :class:`ixmp.Platform` object (for instance, :py:`ixmp.Platform()` in Python) indicate that :mod:`message_ix` (via :mod:`ixmp` and JPype) cannot find Java on your machine, in particular the Java Virtual Machine (JVM).
There are multiple ways to resolve this issue:

1. If you have installed Java manually, ensure that the ``JAVA_HOME`` environment variable is set system-wide; see for example `these instructions`_ for Windows users.
2. If using Anaconda, install the ``openjdk`` package in the same environment as the ``message-ix`` package.
   When the Windows Anaconda Prompt is opened, :program:`conda activate` then ensures the ``JAVA_HOME`` variable is correctly set.

To check which JVM will be used by ixmp, run the following in any prompt or terminal::

    python -c "import jpype; print(jpype.getDefaultJVMPath())"


“No module named 'pyam'”
------------------------

The package `pyam-iamc <https://pypi.org/project/pyam-iamc/>`_ is one of the "report" extra dependencies of :mod:`message_ix`.
These extra dependencies are not installed automatically, but can be installed using::

    # If message_ix is installed using pip
    pip install message_ix[report]
    # or
    pip install pyam-iamc

    # If message_ix is installed using Anaconda (see note below)
    conda install pyam

Note that this package has the *different* name on conda-forge versus PyPI: `pyam <https://anaconda.org/conda-forge/pyam>`__.

The package listed as `pyam <https://pypi.org/project/pyam/>`__ on PyPI (and not available via Anaconda) is unrelated to :mod:`message_ix`, not compatible with it, and will produce other error messages.
If you installed this package accidentally, remove it using::

    # If installed using pip
    pip uninstall pyam


Copy GAMS model files for editing
---------------------------------

By default, the GAMS files containing the mathematical model core are installed with :mod:`message_ix` (e.g., in your Python :file:`site-packages` directory).
Many users will simply want to run |MESSAGEix|, or use the Python or R APIs to manipulate data, parameters and scenarios.
For these uses, direct editing of the GAMS files is not necessary.

To edit the files directly—to change the mathematical formulation, such as adding new types of parameters, constraints, etc.—use the :program:`message-ix` command-line program to copy the model files to a directory of your choice::

    message-ix copy-model /path/for/model/files

You can also set the ``message model dir`` configuration key so that this copy of the files is used by default::

    message-ix config set "message model dir" /path/for/model/files

…or do both in one step::

    message-ix copy-model --set-default /path/for/model/files

Ignore local changes to :file:`.gms` files
------------------------------------------

If you will be using :file:`MESSAGE_master.gms` outside of the :mod:`message_ix` Python API to run |MESSAGEix|, you will likely modify this file, but will not want to commit these changes to Git.
Set the Git “assume unchanged” bit for this file::

    git update-index --assume-unchanged message_ix/model/MESSAGE_master.gms

To unset the bit, use :program:`--no-assume-unchanged`.
See the `Git documentation`_ for more details.

.. _`GAMS`: http://www.gams.com
.. _`latest version`: https://www.gams.com/download/
.. _`version 29`: https://www.gams.com/29/
.. _`Graphviz`: https://www.graphviz.org/
.. _`its conda-forge package`: https://anaconda.org/conda-forge/graphviz
.. _`Graphviz download page`: https://www.graphviz.org/download/
.. _`conda`: https://docs.conda.io/projects/conda/en/stable/
.. _`IIASA YouTube channel`: https://www.youtube.com/user/IIASALive
.. _`Miniconda`: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _`Anaconda`: https://docs.continuum.io/anaconda/install/
.. _`mamba solver`: https://conda.github.io/conda-libmamba-solver/
.. _`conda glossary`: https://docs.conda.io/projects/conda/en/latest/glossary.html
.. _Anaconda Navigator documentation: https://docs.anaconda.com/anaconda/navigator/
.. _`Github Desktop`: https://desktop.github.com
.. _`Git documentation`: https://www.git-scm.com/docs/git-update-index#_using_assume_unchanged_bit
.. _`latest release`: https://github.com/iiasa/message_ix/releases
.. _`IRkernel`: https://irkernel.github.io/installation/
.. _`issue tracker`: https://github.com/iiasa/message_ix/issues
.. _`these instructions`: https://javatutorial.net/set-java-home-windows-10
