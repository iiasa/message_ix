.. include:: ../../INSTALL.rst


Configure model files
---------------------

By default, the GAMS files containing the mathematical model core are installed
with ``message_ix`` (e.g., in your Python ``site-packages`` directory). Many
users will simply want to run |MESSAGEix|, or use the Python or R APIs to
manipulate data, parameters and scenarios. For these uses, direct editing of the
GAMS files is not necessary.

To edit the files directly—to change the mathematical formulation, such as
adding new types of parameters, constraints, etc.—use the ``messageix-config``
utility to place the model files in a directory of your choice::

    $ messageix-config --model_path /path/to/model

.. note::

   If you installed from source on Windows using ``install.bat``, this
   command was run automatically, pointing to ``message_ix/model``.
