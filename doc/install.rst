.. include:: ../INSTALL.rst


Copy GAMS model files for editing
---------------------------------

By default, the GAMS files containing the mathematical model core are installed
with ``message_ix`` (e.g., in your Python ``site-packages`` directory). Many
users will simply want to run |MESSAGEix|, or use the Python or R APIs to
manipulate data, parameters and scenarios. For these uses, direct editing of the
GAMS files is not necessary.

To edit the files directly—to change the mathematical formulation, such as adding new types of parameters, constraints, etc.—use the ``message-ix`` command-line program to copy the model files in a directory of your choice::

    $ message-ix copy-model /path/for/model/files

You can also set the ``message model dir`` configuration key so that this copy of the files is used by default::

    $ message-ix config set "message model dir" /path/for/model/files

…or do both in one step::

    $ message-ix copy-model --set-default /path/for/model/files
