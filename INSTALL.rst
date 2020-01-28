Installation
============

Install GAMS
------------

|MESSAGEix| requires `GAMS`_.

1. Download the latest version of `GAMS`_ for your operating system; run the
   installer.

   .. note:: MESSAGE-MACRO requires GAMS 24.8.1 or later (see
      :attr:`.MESSAGE_MACRO.GAMS_min_version`).

2. Add GAMS to the ``PATH`` environment variable. This is **required** in order
   for |MESSAGEix| to run the mathematical model core.

   - on Windows, in the GAMS installer…

     - Check the box labeled “Use advanced installation mode.”
     - Check the box labeled “Add GAMS directory to PATH environment variable”
       on the Advanced Options page.

   - on macOS or Linux, add the following line to your ``.bash_profile`` (macOS)
     or ``.bashrc`` (Linux)::

          export PATH=$PATH:/path/to/gams-directory-with-gams-binary

Install |MESSAGEix| via Anaconda
--------------------------------

After installing GAMS, we recommend that new users install Anaconda, and then
use it to install |MESSAGEix|. Advanced users may choose to install |MESSAGEix|
from source code (next section).

3. Install Python via `Anaconda`_. We recommend the latest version, i.e.,
   Python 3.6+.

4. Open a command prompt. We recommend Windows users use the “Anaconda Prompt”
   to avoid permissions issues when installing and using |MESSAGEix|. This
   program is available in the Windows Start menu after installing Anaconda.

5. Install the ``message-ix`` package::

    $ conda install -c conda-forge message-ix

Install |MESSAGEix| from source
-------------------------------

3. Install :doc:`ixmp <ixmp:install>` from source.

4. (Optional) If you intend to contribute changes to |MESSAGEix|, first register
   a Github account, and fork the `message_ix repository <https://github.com/iiasa/message_ix>`_. This will create a new repository ``<user>/message_ix``.
   (Please also see :doc:`contributing`.)

5. Clone either the main repository, or your fork; using the `Github Desktop`_
   client, or the command line::

    $ git clone git@github.com:iiasa/message_ix.git

    # or:
    $ git clone git@github.com:USER/message_ix.git

6. Open a command prompt in the ``message_ix`` directory and type::

    $ pip install --editable .

7. (Optional) Run the built-in test suite to check that |MESSAGEix| functions
   correctly on your system::

    $ pip install --editable .[tests]
    $ py.test tests

Common issues
-------------

No JVM shared library file (jvm.dll) found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you get an error containing “No JVM shared library file (jvm.dll) found” when creating a :class:`Platform` object (e.g. ``mp = ix.Platform(driver='HSQLDB')``), it is likely that you need to set the ``JAVA_HOME`` environment variable (see for example `these instructions`_).

.. _`GAMS`: http://www.gams.com
.. _`Anaconda`: https://www.anaconda.com/distribution/#download-section
.. _`ixmp`: https://github.com/iiasa/ixmp
.. _`Github Desktop`: https://desktop.github.com
.. _`README`: https://github.com/iiasa/message_ix#install-from-source-advanced-users
.. _`these instructions`: https://javatutorial.net/set-java-home-windows-10
