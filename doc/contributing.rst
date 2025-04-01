Contributing to development
***************************

We welcome contributions to the code base and development of new features for the |MESSAGEix| framework.
This page contains guidelines for making such contributions.
Each section requires some of the listed :doc:`prerequisite knowledge and skills <prereqs>`;
use the links there to external resources about git, GitHub, Python, etc. to ensure you are able to understand and complete the steps.

This page uses :ref:`RFC 2119 <prereq-rfc2119>` keywords to distinguish mandatory and optional actions.
Sentences written in the `imperative mood <https://en.wikipedia.org/wiki/Imperative_mood>`_ with a bold-face verb like "**Do** X, Y, and Z" imply the **must** / **required** keyword.

On this page:

.. contents::
  :local:

On separate pages:

.. toctree::
   :maxdepth: 1

   contrib/version
   contrib/release
   contrib/tutorial
   contrib/cla
   contrib/video

On GitHub:

- `Our community Code of Conduct <https://github.com/iiasa/message_ix?tab=coc-ov-file>`_
- `How we handle code safety <https://github.com/iiasa/message_ix?tab=security-ov-file>`_

File issues for bugs and enhancements
=====================================

We use Github **issues** for several purposes:

- Ask and answer *questions* about intended behaviour or issues running the framework or related models.
- Report *bugs*, i.e. unintended or undocumented behaviour.
- Request *changes* to exiting behaviour.
- Request specific *enhancements* and *new features*, both urgent and long-term/low-priority.
- Discuss and design of other improvements.

Please search through open *and* closed issues for *both* the `message_ix`__ and `ixmp <https://github.com/iiasa/ixmp/issues?q=is:issue>`_ repositories.
Review any related issues.
Then, if your issue is not found, `open a new one <https://github.com/iiasa/message_ix/issues/new>`_.

__ https://github.com/iiasa/message_ix/issues?q=is:issue

.. _contrib-pr:

Contribute code via pull requests
=================================

1. Choose a repository
----------------------

Decide which part of the |MESSAGEix| software stack is the appropriate location for your code:

:mod:`ixmp`
   Contributions not specific to |MESSAGEix| model framework, e.g. that could be used for other, non-MESSAGE models.

   Also:
   - `genno <https://github.com/khaeru/genno>`__ —for core features underlying :doc:`reporting`.
   - `ixmp_source <https://github.com/iiasa/ixmp_source>`__ (closed source) —Java / JDBC backend for ``ixmp``.

:mod:`message_ix`
   Contributions not specific to *any particular MESSAGEix* model instance.
   Additions to this package should be usable in *any* MESSAGE-scheme model.

:mod:`message_ix_models`
   Contributions to the MESSAGE-GLOBIOM family of models, including the global model, and its documentation.

**Register** a GitHub account, if you do not already have one.

**Choose** either a fork of the given repository (under your own GitHub account), or repository itself.

- IIASA staff and core contributors with ‘Write’ permissions on **may** use branches within the main repositories.
  In some cases, these simplify testing and continuous integration checks.
- All others, and core contributors in all other cases, **should** use forks.

2. Create a branch and add commits
----------------------------------

Create a branch with an appropriate name:

- **Use** `'kebab case' <https://en.wikipedia.org/wiki/Letter_case#Kebab_case>`__ ``all-lower-case-with-hyphens``.
  Underscores (``_``) and capital letters are slower to type; don't use them.
- **Use** prefixes as appropriate:

  - If you are addressing or closing a specific issue: ``issue/1234``.
  - If you are adding an entirely new feature: ``enh/do-something`` or ``feature/do-something``.
  - If you are developing for a particular :mod:`message_ix_models` project: ``project/abc``.
    For projects that have many PRs and branches over time, **use** a suffix as well, for instance with the year, month, or week: ``project/abc/2025-w14``.
- **Do not** use the ``main`` branch in your fork for a PR.
  This makes it difficult for others to check out, use, and contribute to your code.

**Push** the branch to the main repository or your fork.

3. Open a pull request
----------------------

- Open a pull request (e.g. on `message_ix`__) to merge your code into the ``main`` branch or other target branch.
- **Assign** yourself and/or anyone else who will actually commit changes to the PR branch,
  or be actively involved in discussing/designing the code.
- **Choose** the `'draft'`__ status if the code on the branch is not yet complete and ready for review.
  (Developing code in draft PRs is good development practice:
  it ensures the automatic checks pass as you add to the code on your branch.)
- **Apply** any appropriate labels.
  If a PR is to close or address an issue,
  these labels **should** match the ones on the issue.

__ https://github.com/iiasa/message_ix/pulls
__ https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests

.. _pr-template:

3a. Use the template to write the PR description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The repository contains a template for the pull request description that is designed to help you write a clear one.
You **should** write at least a tentative description at the moment you open a PR:
it is useful even before code is started/finished as an expression of the intended scope of the PR.
Failing this, **write** "TBA" ("To Be Added") or a similar placeholder where needed.
In any case, **complete** the description before requesting review or taking the PR out of draft state (step (5) below).

The template contains in-line comments (``<!-- like this -->``) with instructions that **should** be removed as you complete them.
The "PR checklist" section and its individual items **must not** be removed.
If an item is not relevant for your PR, **strike** it out partly or fully and **append** text to explain.
For example:

.. code-block:: rst

   - [ ] ~Add or expand tests;~ coverage checks both ✅

This indicates that there were no tests added or changed—perhaps because no code was changed—but the coverage checks still pass.

.. code-block:: rst

  - ~Add, expand, or update documentation.~ N/A, bug fix
  - [x] Update release notes.

This indicates that the documentation was not changed, because a bug fix changed the code to *match* the documented behaviour.
However, the bugfix PR itself was added to the release notes.

**Revise** the description if the scope or goals of the PR change,
so that it remains up-to-date and useful for understanding the branch contents.

.. _ci-workflows:

4. Ensure checks pass
---------------------

|MESSAGEix| has several kinds of automatic, or *continuous integration*, checks.
Other repositories may have fewer or more checks.

- The `CLA Assistant <https://github.com/cla-assistant/>`_ ensures you have signed the :doc:`contrib/cla` (follow link for text).
  All contributors are required to sign the CLA before any pull request can be reviewed.
  This ensures that all future users can benefit from your contribution,
  and that your contributions do not infringe on anyone else's rights.
- GitHub Actions is used to run several *workflows*.
  These are defined by YAML files in :file:`.github/workflows/`:

  pytest
     This workflow runs all Python and R tests; on Linux, macOS, and Windows; and for multiple versions of Python.
     It also checks that the `code style`_ is applied.

  publish
     This workflow checks that the Python package (for upload to PyPI) can be built cleanly and without errors.
     The package is not actually uploaded, unless this workflow is started from a release candidate tag or on the creation of a new release on GitHub.

  nightly
     These tests run daily at 05:00 UTC.
     They download a particular package of full-scale, MESSAGEix-GLOBIOM global model scenarios from IIASA servers.
     Each scenario's outputs are compared to an expected value listed in :file:`message_ix/tests/data/scenarios.yaml`.
     PRs that touch the GAMS code may cause the objective function values to change;
     the values **must** be updated as part of such PRs.
     See the comments in the file for how to temporarily enable these checks for every commit on a PR branch.

  anaconda, miniconda
     These workflows check that the package can be installed from conda-forge using Anaconda and Miniconda, respectively, on Windows only.
- Two checks from `Codecov <https://codecov.io>`_ ensure that coverage of the 'patch' (changed lines in the PR) is above a given threshold (the average of all other code in the package),
  and that coverage of the overall package does not decrease.
- ReadTheDocs automatically builds a preview version of the documentation, including any changes on the PR branch.
  You **may** also build and view the HTML documentation on your machine to confirm that the generated HTML is as intended and conforms to the :ref:`doc-style` style.

**Resolve** any non-passing checks.

**Ask for help** if needed.

5. Review
---------

Using the GitHub sidebar on your PR, **request** review from another |MESSAGEix| contributor.
GitHub suggests reviewers; optionally, contact the IIASA ECE Program to ask who should review your code.

- If you want them to follow along with progress, tag them in the PR description, like “FYI @Alice @Bob”.
- Per (3a) above, **complete** the "How to review" section of the PR template so that reviewers can understand what they should look at,
  tasks they should perform, etc.
- **Do not** request review until the code is ready to review.
  Doing this sends e-mail and other notifications (e.g. in Slack, the “Pull Reminders” bot sends notices every day).
  If the code is not yet complete and ready for review,
  these notifications are noise,
  and the colleague may be confused as to what they should do.

**Address** any comments raised by the reviewer(s).

6. Merge
--------

GitHub provides `three ways to incorporate a pull request`__: merge, rebase, and squash.
Current practice for the ``ixmp``, ``message_ix``, and ``message_data`` repositories is:

- Use **squash and merge**…

  - if the commit history for the PR is "messy", e.g. there are many merge commits from other branches,
    or the author did not write well-formatted commit messages (see “Code style”, below).
  - if the PR is very old, i.e. it starts at an old commit on ``main``.
    However, it is better to rebase the PR branch on the HEAD of ``main`` and then use a merge commit (below).

- Use **rebase and merge**…

  - if the PR is only one or a few commits that are obviously related.
  - if the PR does not involve user-facing changes, i.e. does not need to be linked from the release notes.

- Use **merge pull request** (also written “create a merge commit”) in all other cases.

  PR branches **must** be rebased on the HEAD of ``main`` before merging.
  This is because some git-based tools will display commits from ``main`` and the PR branch interleaved if their dates and times are mixed,
  which makes it harder to read the commit history.
  Rebasing avoids this problem by ensuring each PR's commits are displayed in sequence.

__ https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-merges

.. _code-style:

Code style
==========

- For both *commit messages* and *pull request (PR) titles*, **follow** the `“7 rules of a great Git commit message” <https://chris.beams.io/posts/git-commit/#seven-rules>`_.

- For *Python* code:

  - **Follow** the `PEP 8 naming conventions <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_.
  - **Use** `ruff <https://docs.astral.sh/ruff>`_ to check code formatting (:program:`ruff format`, which applies the "black" format) and quality (:program:`ruff check`).
    In particular, through :file:`pyproject.toml`, :mod:`message_ix` uses the following rule sets to ensure:

    - `"F" <https://docs.astral.sh/ruff/rules/#pyflakes-f>`_: code is free of basic errors, equivalent to Pyflakes or `flake8 <https://flake8.pycqa.org>`_.
    - `"E", "W" <https://docs.astral.sh/ruff/rules/#pycodestyle-e-w>`_: code conforms to `PEP 8 <https://www.python.org/dev/peps/pep-0008>`_,
      equivalent to using pycodestyle.
    - `"I" <https://docs.astral.sh/ruff/rules/#isort-i>`_: :py:`import` statements are sorted in a consistent way,
      equivalent to `isort <https://pypi.org/project/isort/>`_.
    - `"C90" <https://docs.astral.sh/ruff/rules/#mccabe-c90>`_: the McCabe complexity of code is below a fixed threshold,
      equivalent to using `mccabe <https://pypi.org/project/mccabe/>`_ via flake8.

  - **Add** type hints to new or changed functions, methods, and global variables.
    **Check** these using the `mypy <https://mypy.readthedocs.io>`_ static type checker.

  To simplify the use of ruff and mypy,
  it is **recommended** to:

  - Configure these to run automatically within your code editor using an extension, plugin, or script.
    See their respective documentation for links and details.
    These extensions help apply the code style every time a file is saved, or even as you type.
  - Configure `pre-commit <https://pre-commit.com>`_ to invoke these and other checks every time you do a :program:`git commit`.
    To use this tool, install :program:`pre-commit` and then install its `git hooks <https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks>`_ in your local checkout of the source repository:

    .. code-block::

       uv tool install --with=pre-commit-uv pre-commit
       pre-commit install -f

       # Run the tools on all files to confirm they are working
       pre-commit run --all-files

  - The "Code quality" job in the "pytest" workflow :ref:`described above <ci-workflows>` applies exactly the same checks for PR branches.
    PRs that fail the checks **must** be corrected before they can be merged.

- For *GAMS* code:

    - **Wrap** lines at 121 characters, except for inline documentation (see below).

- For *R* code: follow the style of the existing code base.
- Jupyter notebooks (:file:`.ipynb`): see :doc:`contrib/tutorial`.
- Other (file names, CLI, etc.): follow the style of the existing code base, e.g.:

  - Use lower-case file names and extensions.
  - Except for Python source files, prefer hyphens to underscores.

.. _doc-style:

Documentation
-------------

- **Write** documentation in :doc:`reStructuredText (reST) <sphinx:usage/restructuredtext/index>` format for:

  1. Python docstrings.
     **Wrap** these at the same 88 characters as :command:`ruff` enforces for code.
  2. Documentation pages, :file:`doc/*.rst`.
  3. Inline documentation in :file:`message_ix/model/*.gms` files.

  For (2) and (3), **use** `semantic line breaks <https://sembr.org>`_.

- Ensure Sphinx does not give warnings about reST syntax for new or modified documentation.

- Use :mod:`sphinx.ext.intersphinx` (click for docs) to create cross-links within one project's documentation, or across projects.

  - Understand the use of the ``~`` and ``.`` characters to resolve references across the project.
    See :ref:`sphinx:xref-syntax` in the Sphinx docs.
  - See example usage in existing code.
  - Check that intersphinx links are correctly resolved, by building the docs and attempting to click new or modified links.

- **Write** docstrings in the `numpydoc <https://numpydoc.readthedocs.io/en/latest/format.html>`_ style.
  This implies also `PEP 257 <https://peps.python.org/pep-0257/>`_;
  see in particular the format for `multi-line docstrings <https://peps.python.org/pep-0257/#multi-line-docstrings>`_.

  Use single backticks to refer to function arguments, and asterisks for italics:

  .. code-block:: python

      def func(foo: str, bar: str) -> float:
          """Perform some action.

          If `foo` and `bar` have the same value, ``42.1`` is returned. *Nice!*
          """

References:

- :doc:`sphinx:usage/restructuredtext/basics` in the Sphinx docs.
- https://docutils.sourceforge.io/docs/user/rst/quickref.html


Manage issues and pull requests
===============================

- Assign an issue or PRs to the person(s) who must take the next action towards completing it.
  For example:

  - Comment on the issue to provide information/decisions needed to move forward.
  - Implement the requested changes in code.

  This might be different from the person who opened the issue/PR.

- Use the GitHub auto-linking feature to make clear the connection between related issues and PRs.
- Look at the labels, milestones, and projects in the right sidebar.
  Associate the issue with the correct one(s).
- Follow-up on old issues (ones with no activity for a month or more):

  - Ask (in a new comment, on Slack, in person) the assignee or last commenter what the status is.
  - Close or re-assign, with a comment that describes your reasoning.
