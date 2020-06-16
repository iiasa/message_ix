Getting Started
***************

.. contents::
   :local:

Install system dependencies
===========================

GAMS (required)
---------------

|MESSAGEix| requires `GAMS`_.

1. Download GAMS for your operating system; we encourage new users not familiar with GAMS licensing to install `version 29`_ and **not** the latest one (see note below).

2. Run the installer.

3. Ensure that the ``PATH`` environment variable on your system includes the path to the GAMS program:

   - on Windows, in the GAMS installer…

      - Check the box labeled “Use advanced installation mode.”
      - Check the box labeled “Add GAMS directory to PATH environment variable” on the Advanced Options page.

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

:meth:`.reporting.Reporter.visualize` uses `Graphviz`_, a program for graph visualization.
Installing message_ix causes the python :mod:`graphviz` package to be installed.
If you want to use :meth:`.visualize` or run the test suite, the Graphviz program itself must also be installed; otherwise it is **optional**.

If you `Install MESSAGEix via Anaconda`_, Graphviz is installed automatically via `its conda-forge package`_.
For other methods of installation, see the `Graphviz download page`_ for downloads and instructions for your system.


Install |MESSAGEix| via Anaconda
================================

After installing GAMS, we recommend that new users install Anaconda, and then use it to install |MESSAGEix|.
Advanced users may choose to install |MESSAGEix| from source code (next section).

4. Install Python via either `Miniconda`_ or `Anaconda`_. [1]_
   We recommend the latest version; currently Python 3.8.

5. Open a command prompt.
   **Windows users should use the “Anaconda Prompt”** to avoid issues with permissions and environment variables when installing and using |MESSAGEix|.
   This program is available in the Windows Start menu after installing Anaconda.

6. Configure conda to install :mod:`message_ix` from the conda-forge channel [2]_::

    $ conda config --prepend channels conda-forge

Alternatively to *Steps 5. and 6.*, :mod:`message_ix` can also be installed using the **“Anaconda Navigator”** (see instructions `here`_)

7. Create a new conda environment.
   This step is **required** if using Anaconda, and *optional* if using Miniconda.
   This example uses the name ``message``, but you can use any name of your choice::

    $ conda create --name message
    $ conda activate message

8. Install the ``message-ix`` package into the current environment (either ``base``, or another name from step 7, e.g. ``message``) [3]_::

    $ conda install message-ix

Install |MESSAGEix| via pip
===========================

6. As an alternative to *Steps 6., 7. and 8.* above, ``message-ix`` and its dependencies can also be installed using `pip`_::

    $ pip install message-ix


Check if the installation was successful
========================================

Verify that the version installed corresponds to |MESSAGEix| `latest release`_ by running::

    # Show versions of message_ix, ixmp, and key dependencies
    $ message-ix show-versions

    # Show the contents of the default local Platform (empty on install)
    $ message-ix --platform=default list

The above commands will work **as of** ``message-ix`` 3.0 and in subsequent versions. If an error prompts, it means that an *older* version has been installed and that ``message-ix`` should be updated. To check the current version::

    # If installation was through conda:
    $ conda list message-ix

    # or if you used pip for installing:
    $ pip show message-ix

.. [1] See the `conda glossary`_ for the differences between Anaconda and Miniconda, and the definitions of the terms ‘channel’ and ‘environment’ here.
.. [2] The ‘$’ character at the start of these lines indicates that the command text should be entered in the terminal or prompt, depending on the operating system.
       Do not retype the ‘$’ character itself.
.. [3] Notice that conda uses the hyphen (‘-’) in package names, different from the underscore (‘_’) used in Python when importing the package.

.. note:: If further errors appear, please check the section `Common issues`_ below.


Install |MESSAGEix| from source (advanced users)
================================================

4. Install :doc:`ixmp <ixmp:install>` from source.

5. (Optional) If you intend to contribute changes to |MESSAGEix|, first register a Github account, and fork the `message_ix repository <https://github.com/iiasa/message_ix>`_.
   This will create a new repository ``<user>/message_ix``.
   (Please also see :doc:`contributing`.)

6. Clone either the main repository, or your fork; using the `Github Desktop`_ client, or the command line::

    $ git clone git@github.com:iiasa/message_ix.git

    # or:
    $ git clone git@github.com:USER/message_ix.git

7. Open a command prompt in the ``message_ix`` directory and type::

    $ pip install --editable .[docs,reporting,tests,tutorial]

   The ``--editable`` flag ensures that changes to the source code are picked up every time :code:`import message_ix` is used in Python code.
   The ``[docs,reporting,tests,tutorial]`` extra requirements ensure additional dependencies are installed.

8. (Optional) If you will be using :file:`MESSAGE_master.gms` outside of Python :mod:`message_ix` to run |MESSAGEix|, you will likely modify this file, but will not want to commit these changes to Git.
   Set the Git “assume unchanged” bit for this file::

    $ git update-index --assume-unchanged message_ix/model/MESSAGE_master.gms

   To unset the bit, use ``--no-assume-unchanged``.
   See the `Git documentation <https://www.git-scm.com/docs/git-update-index#_using_assume_unchanged_bit>`_ for more details.

9. (Optional) Run the built-in test suite to check that |MESSAGEix| functions correctly on your system::

    $ pytest


Common issues
=============

“No JVM shared library file (jvm.dll) found”
--------------------------------------------

Error messages like this when running ``message-ix --platform=default list`` or when creating a :class:`Platform` object (e.g. :code:`ixmp.Platform()` in Python) indicate that :mod:`message_ix` (via :mod:`ixmp` and JPype) cannot find Java on your machine, in particular the Java Virtual Machine (JVM).
There are multiple ways to resolve this issue:

1. If you have installed Java manually, ensure that the ``JAVA_HOME`` environment variable is set system-wide; see for example `these instructions`_ for Windows users.
2. If using Anaconda, install the ``openjdk`` package in the same environment as the ``message-ix`` package.
   When the Windows Anaconda Prompt is opened, ``conda activate`` then ensures the ``JAVA_HOME`` variable is correctly set.

To check which JVM will be used by ixmp, run the following in any prompt or terminal::

    $ python -c "import jpype; print(jpype.getDefaultJVMPath())"


.. _`here`: https://docs.anaconda.com/anaconda/navigator/
.. _`pip`: https://pip.pypa.io/en/stable/user_guide/#installing-packages
.. _`latest release`: https://docs.messageix.org/en/master/whatsnew.html#what-s-new
.. _`GAMS`: http://www.gams.com
.. _`version 29`: https://www.gams.com/29/
.. _`Graphviz`: https://www.graphviz.org/
.. _`its conda-forge package`: https://anaconda.org/conda-forge/graphviz
.. _`Graphviz download page`: https://www.graphviz.org/download/
.. _`Miniconda`: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _`Anaconda`: https://docs.continuum.io/anaconda/install/
.. _`conda glossary`: https://docs.conda.io/projects/conda/en/latest/glossary.html
.. _`ixmp`: https://github.com/iiasa/ixmp
.. _`Github Desktop`: https://desktop.github.com
.. _`README`: https://github.com/iiasa/message_ix#install-from-source-advanced-users
.. _`these instructions`: https://javatutorial.net/set-java-home-windows-10

JPype1 segfautls
----------------
The symptom: crashes or segfaults when the JVM is started:

.. code-block:: RST

    >           self.jindex[ts].readSolutionFromGDX(*args)
    E           TypeError: Ambiguous overloads found for at.ac.iiasa.ixmp.objects.MsgScenario.readSolutionFromGDX(str,str,str,java.util.LinkedList,java.util.LinkedList,bool) between:
    E           	public void at.ac.iiasa.ixmp.objects.MsgScenario.readSolutionFromGDX(java.lang.String,java.lang.String,java.lang.String,java.util.List,java.util.List,boolean) throws at.ac.iiasa.ixmp.exceptions.IxException
    E           	public void at.ac.iiasa.ixmp.objects.Scenario.readSolutionFromGDX(java.lang.String,java.lang.String,java.lang.String,java.util.LinkedList,java.util.LinkedList,boolean) throws at.ac.iiasa.ixmp.exceptions.IxException

    ../../../miniconda/envs/testing/lib/python3.8/site-packages/ixmp/backend/jdbc.py:346: TypeError

There are two ways of checking this error:

a. Run a Python script (.py) containing::

    $ import ixmp
    $ ixmp.Platform()

b. Run in the command line of the “Anaconda Prompt”::

    $ ixmp --platform default list

If the error in the code block above appears, user should run these two extra commands::

    # To see (a) whether conda openjdk is installed, and (b) whether it comes from conda-forge:
    $ conda list openjdk

    # To force installation of the version from conda-forge:
    $ conda install -c conda-forge --override-channels openjdk

