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

Development rule of thumb
-------------------------

Pull requests for new features

- Open a new PR as soon as you create a branch for a new feature. This lets you (and others) keep track of the changes, and automatically runs tests to ensure you don't break anything. Use "WIP:" at the beginning of the PR title to indicate work in progress.
- Write a short (one sentence) description of the PR, followed by a detailed description. This is like the abstract of a publication: it should help a developer/reviewer/user quickly learn what the PR is about.
- Learn how to `rebase <https://git-scm.com/docs/git-rebase>`_ your feature branch onto the tip of ``master``. Do this frequently to ensure your added code can still be merged.

Milestones

- We use `semantic versioning. <https://semver.org>`_
- We keep at least two active milestones on ``message_ix`` and ``ixmp``.

  - The next minor version. E.g. if the last release was 3.5, the next minor release/milestone is 3.6.
  - The next major version. E.g. 4.0.

- Choose a milestone for every issue and PR to indicate a desire/consensus to release it at a certain time.

.. _`Contributor License Agreement`: contributor_license.html
.. _`cla-assistant`: https://github.com/cla-assistant/
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
