Contributing to |MESSAGEix| development
=======================================

We appreciate contributions to the code base and development of new features for the framework.
Please `open a new issue on Github <https://github.com/iiasa/message_ix/issues/new>`_ to raise questions concerning potential bugs or to propose new features.
`Existing open and resolved/closed issues <https://github.com/iiasa/message_ix/issues?q=is:issue>`_ may already contain a solution.

For contributions to the code base of the platform, please `open a GitHub “pull request,” <https://github.com/iiasa/message_ix/pulls>`_ including a detailed description of the new feature and unit tests to illustrate the intended functionality.
All pull requests will be reviewed by the message_ix maintainers and/or contributors.

Contributors are required to sign the `Contributor License Agreement`_ before any pull request can be reviewed.
This ensures that all future users can benefit from your contribution, and that your contributions do not infringe on anyone else's rights.
The electronic signature is collected via the `cla-assistant`_ when issuing the pull request.

Coding style
------------

Code submitted via pull requests must adhere to the following style:

- Python: follow `PEP 8`_.
- R: follow the style of the existing code base.
- Jupyter notebooks (``.ipynb``):

  - Commit 'bare' notebooks, with no cell output.
    Notebooks will be run and rendered when the documentation is generated.

- Documentation (``.rst``, ``.md``):

  - Do not hard-wrap lines. Start each sentence on a new line.

- Other (file names, CLI, etc.): follow the style of the existing code base.

.. _`Contributor License Agreement`: contributor_license.html
.. _`cla-assistant`: https://github.com/cla-assistant/
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
