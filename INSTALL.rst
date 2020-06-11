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

       export PATH=$PATH:/path/to/gams-directory-with-gams-binary

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

4. Install Python via `Anaconda`_.

   - We recommend the latest version; currently Python 3.8.

5. Open a command prompt.

   - We recommend **Windows users to use the “Anaconda Prompt”** to avoid permissions issues when installing and using |MESSAGEix|. This program is available in the Windows Start menu after installing Anaconda.

6. Install the ``message-ix`` package::

    $ conda install -c conda-forge message-ix

Alternatively to *Steps 5. and 6.*, ``message-ix`` can also be installed using the **“Anaconda Navigator”** (see instructions `here`_)


Install |MESSAGEix| via pip
===========================

6. As an alternative to *Step 6.* above, ``message-ix`` and its dependencies can also be installed using `pip`_::

    $ pip install message-ix


Check if the installation was successful
========================================

7. Run the command and verify that the version shown corresponds to |MESSAGEix| `latest release`_::

    $ message-ix show-versions

8. The above command will work **as of** ``message-ix`` 3.0 and in all subsequent versions. If an error prompts, it means that an older versions has been installed and that ``message-ix`` should be updated. To check the current version::

    # If installation was through conda:
    $ conda list message-ix

    # or if you used pip for installing:
    $ pip show message-ix

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

   The ``--editable`` flag ensures that changes to the source code are picked up every time ``import message_ix`` is used in Python code.
   The ``[docs,reporting,tests,tutorial]`` extra dependencies ensure additional dependencies are installed.

8. (Optional) If you will be using :file:`MESSAGE_master.gms` outside of Python :mod:`message_ix` to run |MESSAGEix|, you will likely modify this file, but will not want to commit these changes to Git.
   Set the Git “assume unchanged” bit for this file::

    $ git update-index --assume-unchanged message_ix/model/MESSAGE_master.gms

   To unset the bit, use ``--no-assume-unchanged``.
   See the `Git documentation <https://www.git-scm.com/docs/git-update-index#_using_assume_unchanged_bit>`_ for more details.

9. (Optional) Run the built-in test suite to check that |MESSAGEix| functions correctly on your system::

    $ pytest


Common issues
=============

No JVM shared library file (jvm.dll) found
------------------------------------------

If you get an error containing “No JVM shared library file (jvm.dll) found” when creating a :class:`Platform` object (e.g. ``mp = ix.Platform(driver='HSQLDB')``), it is likely that you need to set the ``JAVA_HOME`` environment variable (see for example `these instructions`_).

.. _`here`: https://docs.anaconda.com/anaconda/navigator/
.. _`pip`: https://pip.pypa.io/en/stable/user_guide/#installing-packages
.. _`latest release`: https://docs.messageix.org/en/master/whatsnew.html#what-s-new
.. _`GAMS`: http://www.gams.com
.. _`version 29`: https://www.gams.com/29/
.. _`Graphviz`: https://www.graphviz.org/
.. _`its conda-forge package`: https://anaconda.org/conda-forge/graphviz
.. _`Graphviz download page`: https://www.graphviz.org/download/
.. _`Anaconda`: https://www.anaconda.com/distribution/#download-section
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

