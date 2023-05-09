Auto-documentation of the MESSAGEix framework
=============================================

The documentation of the MESSAGEix framework is generated from rst files included in ``doc\source`` and from mark-up comments in the GAMS code written in restructured text.


Dependencies
------------

Install with the package. From the parent directory::

    $ pip install .[docs]


Writing in Restructured Text
----------------------------

There are a number of guides out there, e.g. on docutils_.


Building the docs on your local machine
---------------------------------------

From the command line, run in `doc/`::

    make html

You can then view the site by::

    cd build
    python -m http.server

and pointing your browser at http://0.0.0.0:8000/_build/html/


Read the Docs
-------------

On Read the Docs (RTD), the documentation is built using a command similar to:

    sphinx-build -T -E -d _build/doctrees-readthedocs -D language=en . \
      _build/html

This command is executed in the directory containing `conf.py`, i.e.
`doc/source/`. Note that this is different from `doc/`, where the above `make`
tools are invoked. Use this to test whether the documentation build works on
RTD.

.. _Sphinx: http://sphinx-doc.org/
.. _docutils: http://docutils.sourceforge.net/docs/user/rst/quickref.html
