Installation
************

.. contents::
   :local:

Ensure you have first read the :doc:`prerequisites <prereqs>` for understanding and using |MESSAGEix|.
These include specific points of knowledge that are necessary to understand these instructions and choose among different installation options.

.. _system-dependencies:

Install system dependencies
===========================

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

.. note::
   MESSAGE-MACRO and MACRO require GAMS 24.8.1 or later (see :attr:`.MACRO.GAMS_min_version`)
   The latest version is recommended.

   GAMS is proprietary software and requires a license to solve optimization problems.
   To run both the :mod:`message_ix` and :mod:`ixmp` tutorials and test suites, a “free demonstration” license is required; the free license is suitable for these small models.
   Versions of GAMS up to `version 29`_ include such a license with the installer; since version 30, the free demo license is no longer included, but may be requested via the GAMS website.

.. note::
   If you only have a license for an older version of GAMS, install both the older and the latest versions.


Graphviz (optional)
-------------------

:meth:`.Reporter.visualize` uses `Graphviz`_, a program for graph visualization.
Installing message_ix causes the `graphviz <https://graphviz.readthedocs.io>`__ Python package to be installed.
If you want to use :meth:`.visualize` or run the test suite, the Graphviz program itself must also be installed; otherwise it is **optional**.

If you install MESSAGEix `using conda <using-conda>`_, Graphviz is installed automatically via `its conda-forge package`_.
For other methods of installation, see the `Graphviz download page`_ for downloads and instructions for your system.


Install |MESSAGEix|
===================

After installing GAMS, we recommend that new users use ``pip`` to install |MESSAGEix|.
If you are more comfortable with that, you can also install |MESSAGEix| using ``conda``.
Advanced users may install from source code, too, to benefit from the latest features.
Whichever option you choose, please skip the other sections.

Using virtual environments
--------------------------

Python uses virtual environments to keep track of different sets of dependency versions. 
Each virtual environment (“venv”) contains one set of packages with specific versions, allowing your system to contain multiple versions of packages at the same time, that might be conflicting with one another.
Usually, one virtual environment is used per project, and if you want to switch from one project to another, you simply switch your active virtual environment, too.

There are many ways to manage venvs. Python includes a native `venv library <https://docs.python.org/3/library/venv.html>`__ and `conda`_ can manage them, too.
Some further favourites of ours include `virtualenv <https://virtualenv.pypa.io/en/latest/index.html>`__ and `virtualfish <https://virtualfish.readthedocs.io/en/latest/>`__, but there are many more.

Whichever tool you choose, we strongly recommend you use a venv for your |MESSAGEix| installation.


Using ``pip``
-------------

`pip`_ is Python's default package management system.
``pip`` can be used when Python is installed directly or as installed from ``conda``. [1]_

4. We strongly recommend creating and activating a virtual environment, e.g. using ``virtualenv``. Open a command prompt and run::

    virtualenv message_env

    # On Linux or Mac:
    source message_env/bin/activate

    # On Windows:
    .\message_env\Scripts\activate

5. Ensure ``pip`` is installed—from ``conda``, or according to the pip documentation.

6. Install |MESSAGEix|::

    pip install message_ix[docs,report,tests,tutorial]

   The ``[docs,report,tests,tutorial]`` extra requirements ensure additional dependencies are installed and can be adapted as desired. [2]_
   ``docs`` allows you to build this documentation locally, ``report`` enables you to use the built-in :doc:`reporting <reporting>` functionality, ``tests`` facilitates running our test suite locally, and ``tutorial`` contains everything required for running our :doc:`tutorials <tutorials>`.

.. [1] If you intend to use ``pip`` in a venv managed by ``conda``, please read `conda's guide to using pip in a venv <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`__. 
   In particular, please make sure you use ``conda`` only to install ``pip`` in your venv and then use that specific ``pip`` for all further install commands.
.. [2] If using ``zsh``, recall that ``[...]`` is a `glob operator <https://zsh.sourceforge.io/Doc/Release/Expansion.html#Glob-Operators>`__, so the argument to pip must be quoted appropriately: ``pip install -e '.[docs,tests,tutorial]'.


.. _using-conda:

Using ``conda``
--------------

.. note:: This section is also available as a narrated video on the `IIASA YouTube channel`_.
   If you are a beginner, you may want to watch the video before attempting the installation yourself.

   .. raw:: html

      <iframe width="690" height="360" src="https://www.youtube.com/embed/QZw-7rIqUJ0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

4. Install Python via either `Miniconda`_ or `Anaconda`_. [1]_
   We recommend the latest version; currently Python 3.12. [2]_

5. Open a command prompt.
   Windows users should use the “Anaconda Prompt” to avoid issues with permissions and environment variables when installing and using |MESSAGEix|.
   This program is available in the Windows Start menu after installing Anaconda.

6. Configure conda to install :mod:`message_ix` from the conda-forge channel [3]_::

    conda config --prepend channels conda-forge

7. Install and configure the `mamba solver`_, which is faster and more reliable than conda's default solver::

    conda install conda-libmamba-solver
    conda config --set solver libmamba

8. Create a new conda environment and activate it.
   This step is **required** if using Anaconda, but *optional* if using Miniconda.
   This example uses the name ``message_env``, but you can use any name of your choice::

    conda create --name message_env
    conda activate message_env

9. Install the ``message-ix`` package into the current environment (either e.g. ``message_env``, or another name from step 7) [4]_::

    conda install message-ix

Again: at this point, installation is complete.
You do not need to complete the steps in “Using ``pip``” or “From source”.
Go to the section `Check that installation was successful`_.

.. [1] See the `conda glossary`_ for the differences between Anaconda and Miniconda, and the definitions of the terms ‘channel’ and ‘environment’ here.
.. [2] On newer macOS systems with "Apple M1" processors: the Miniconda or Anaconda installers provided for M1 lead to errors in ixmp.
   Instead, we recommend to use the macOS installers for "x86_64" processors on these systems.
   See also `ixmp issue 473 <https://github.com/iiasa/ixmp/issues/473>`_ and `ixmp issue 531 <https://github.com/iiasa/ixmp/issues/531>`_.
.. [3] The ‘$’ character at the start of these lines indicates that the command text should be entered in the terminal or prompt, depending on the operating system.
   Do not retype the ‘$’ character itself.
.. [4] Notice that conda uses the hyphen (‘-’) in package names, different from the underscore (‘_’) used in Python when importing the package.
.. note:: When using Anaconda (not Miniconda), steps (5) through (9) can also be performed using the graphical Anaconda Navigator.
   See the `Anaconda Navigator documentation`_ for how to perform the various steps.


From source
-----------

.. note::
   If you want to install |MESSAGEix| from source, but already have an install from ``pip``, please make sure you run ``pip uninstall message-ix`` first.
   Otherwise, ``pip`` might not recognize your new install correctly, resulting in an error message along the lines of ``'message_ix' has not attribute 'Scenario'```.

4. We strongly recommend creating and activating a virtual environment, e.g. using ``virtualenv``. Open a command prompt and run::

    virtualenv message_env

    # On Linux or Mac:
    source message_env/bin/activate

    # On Windows:
    .\message_env\Scripts\activate

5. Install :doc:`ixmp <ixmp:install>` from source. If you prefer to install ``ixmp`` from ``pip``, please be sure to use the same combination of major and minor version, i.e. if ``message_ix`` has 3.9.x, ``ixmp`` should also have 3.9.x.

6. (Optional) If you intend to contribute changes to |MESSAGEix|, first register a Github account, and fork the `message_ix repository <https://github.com/iiasa/message_ix>`_.
   This will create a new repository ``<user>/message_ix``.
   (Please also see :doc:`contributing`.)

7. Clone either the main repository, or your fork; using the `Github Desktop`_ client, or the command line::

    git clone git@github.com:iiasa/message_ix.git

    # or:
    git clone git@github.com:USER/message_ix.git

8. (Conditional) If you cloned your fork, add the main repository as a remote git repository.
   This will allow keeping up to date with changes there and importing tags, which also needs to be done for the install tests to succeed::

    git remote add upstream git@github.com:iiasa/message_ix.git

    git fetch upstream --tags

9. Open a command prompt in the ``message_ix`` directory and type::

    pip install --editable .[docs,report,tests,tutorial]

   The ``--editable`` flag ensures that changes to the source code are picked up every time :code:`import message_ix` is used in Python code.
   The ``[docs,report,tests,tutorial]`` extra requirements ensure additional dependencies are installed are installed and can be adapted as desired. [1]_
   ``docs`` allows you to build this documentation locally, ``report`` enables you to use the built-in :doc:`reporting <reporting>` functionality, ``tests`` facilitates running our test suite locally, and ``tutorial`` contains everything required for running our :doc:`tutorials <tutorials>`.

10. (Optional) If you will be using :file:`MESSAGE_master.gms` outside of Python :mod:`message_ix` to run |MESSAGEix|, you will likely modify this file, but will not want to commit these changes to Git.
   Set the Git “assume unchanged” bit for this file::

    git update-index --assume-unchanged message_ix/model/MESSAGE_master.gms

   To unset the bit, use ``--no-assume-unchanged``.
   See the `Git documentation`_ for more details.

11. (Optional) If installed from source, run the built-in test suite to check that |MESSAGEix| functions correctly on your system::

    pytest

.. [1] If using ``zsh``, recall that ``[...]`` is a `glob operator <https://zsh.sourceforge.io/Doc/Release/Expansion.html#Glob-Operators>`__, so the argument to pip must be quoted appropriately: ``pip install -e '.[docs,tests,tutorial]'.


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

“No JVM shared library file (jvm.dll) found”
--------------------------------------------

Error messages like this when running ``message-ix --platform=default list`` or when creating a :class:`ixmp.Platform` object (for instance, :py:`ixmp.Platform()` in Python) indicate that :mod:`message_ix` (via :mod:`ixmp` and JPype) cannot find Java on your machine, in particular the Java Virtual Machine (JVM).
There are multiple ways to resolve this issue:

1. If you have installed Java manually, ensure that the ``JAVA_HOME`` environment variable is set system-wide; see for example `these instructions`_ for Windows users.
2. If using Anaconda, install the ``openjdk`` package in the same environment as the ``message-ix`` package.
   When the Windows Anaconda Prompt is opened, ``conda activate`` then ensures the ``JAVA_HOME`` variable is correctly set.

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

By default, the GAMS files containing the mathematical model core are installed
with ``message_ix`` (e.g., in your Python ``site-packages`` directory). Many
users will simply want to run |MESSAGEix|, or use the Python or R APIs to
manipulate data, parameters and scenarios. For these uses, direct editing of the
GAMS files is not necessary.

To edit the files directly—to change the mathematical formulation, such as adding new types of parameters, constraints, etc.—use the ``message-ix`` command-line program to copy the model files in a directory of your choice::

    message-ix copy-model /path/for/model/files

You can also set the ``message model dir`` configuration key so that this copy of the files is used by default::

    message-ix config set "message model dir" /path/for/model/files

…or do both in one step::

    message-ix copy-model --set-default /path/for/model/files

.. _`GAMS`: http://www.gams.com
.. _`latest version`: https://www.gams.com/download/
.. _`version 29`: https://www.gams.com/29/
.. _`Graphviz`: https://www.graphviz.org/
.. _`its conda-forge package`: https://anaconda.org/conda-forge/graphviz
.. _`Graphviz download page`: https://www.graphviz.org/download/
.. _`conda`: https://docs.conda.io/projects/conda/en/stable/
.. _pip: https://pip.pypa.io/en/stable/user_guide/
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
.. _`these instructions`: https://javatutorial.net/set-java-home-windows-10
