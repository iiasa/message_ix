Contributing to development
***************************

We welcome contributions to the code base and development of new features for the |MESSAGEix| framework.
This page contains guidelines for making such contributions.
Each section requires some of the listed :doc:`prerequisite knowledge and skills <prereqs>`; use the links there to external resources about git, Github, Python, etc. to ensure you are able to understand and complete the steps.

.. contents::
  :local:


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


Contribute code via Github PRs
==============================

1. Choose a repository
----------------------

Decide which part of the |MESSAGEix| software stack is the appropriate location for your code:

:mod:`ixmp`
   Contributions not specific to |MESSAGEix| model framework, e.g. that could be used for other, non-MESSAGE models.

   :mod:`ixmp_source`
      Java / JDBC backend for ``ixmp``.

:mod:`message_ix`
   Contributions not specific to *any particular MESSAGEix* model instance.
   Additions to ``message_ix`` should be usable in any MESSAGE-scheme model.

:mod:`message_data` or :mod:`message_doc`
   Contributions to the MESSAGE-GLOBIOM family of models, including the global model; and its documentation, respectively.


2. Fork, branch, and open a pull request
----------------------------------------

Register a Github account, if you do not already have one.
Fork the chosen repository to your own Github account.
Create a branch with an appropriate name:

- ``all-lower-case-with-hyphens`` —underscores (``_``) are slower to type; don't use them.
- ``issue/1234`` if you are addressing a specific issue.
- ``feature/do-something`` if you are adding a new feature.
- Don't use the ``master`` branch  in your fork for a PR.
  This makes it hard for others to check out and play with your code.

Open a PR (e.g. on `message_ix`__) to merge your code into the ``master`` branch.
The ``message_ix`` and ``ixmp`` repositories each have a template for the text of the PR that is designed to help you write a clear description.
It includes:

__ https://github.com/iiasa/message_ix/pulls

- A title and one-sentence summary of the change.
  This is like the abstract of a publication: it should help a developer/reviewer/user quickly learn what the PR is about.
- Confirm that unit or integration tests have been added or revised to cover the changed code, and that the tests pass (see below).
- Confirm that documentation of the API and its usage is added or revised as necessary.
- Add a line to :file:`RELEASE_NOTES.rst` describing the changes (use the same title or one-sentence summary as above) and linking to the PR.

Optionally:

- Assign yourself and anyone else who will actually commit changes to the PR branch, or be actively involved in discussing/designing the code.
- Include a longer description of the design, or any changes whose purpose is not clear by inspecting code.
- Put “WIP:” or the construction sign Unicode character (🚧) at the start of the PR title to indicate “work in progress” while you continue to add commits; or use GitHub's `'draft' pull requests`__ feature.
  This is good development practice: it ensures the automatic checks pass as you add to the code on your branch.

__ https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests


3. Ensure checks pass
---------------------

|MESSAGEix| has several kinds of automatic, or *continuous integration*, checks:

- The `CLA Assistant <https://github.com/cla-assistant/>`_ ensures you have signed the `Contributor License Agreement`_ (text below).
  All contributors are required to sign the CLA before any pull request can be reviewed.
  This ensures that all future users can benefit from your contribution, and that your contributions do not infringe on anyone else's rights.
- GitHub Actions is used to run several *workflows*.
  These are defined by YAML files in :file:`.github/workflows/`:

  pytest
     This workflow runs all Python and R tests; on Linux, macOS, and Windows; and for multiple versions of Python.

  lint
     This workflow checks for code style and other details:

     - “Lint with flake8”: checks that `Code style`_ is met.
     - “Test package build”: checks that the Python package for upload to PyPI, can be built cleanly and without errors.
     - “Test documentation build”: checks that the documentation can be built without fatal errors.

  nightly
     These tests run daily at 05:00 UTC.
     They download a particular package of full-scale, MESSAGEix-GLOBIOM global model scenarios from IIASA servers.
     Each scenario's outputs are compared to an expected value.

  anaconda, miniconda
     These workflows check that the package can be installed from conda-forge using Anaconda and Miniconda, respectively, on Windows only.

Resolve any non-passing checks—seeking help if needed.

If your PR updates the documentation, the ``lint`` check will confirm that it can be built.
However, you should also *manually* build and view the HTML documentation on your machine to confirm that the generated HTML is as expected, and address any warnings generated by Sphinx during the build phase.
See ``doc/README.rst``.


4. Review
---------

Using the GitHub sidebar on your PR, request a review from another |MESSAGEix| contributor.
GitHub suggests reviewers; optionally, contact the IIASA Energy Program to ask who should review your code.

- If you want them to follow along with progress, tag them in the PR description, like “FYI @Alice @Bob”.
- Only formally request review once the code is ready to review.
  Doing this sends e-mail and other notifications (e.g. in Slack, the “Pull Reminders” bot sends notices every day).
  If the code is not yet complete and ready for review, these notifications are noise.

Address any comments raised by the reviewer.


5. Merge
--------

GitHub provides `three ways to incorporate a pull request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-merges>`_: merge, rebase, and squash.
Current practice for the ``ixmp``, ``message_ix``, and ``message_data`` repositories is:

- Use **squash and merge**…

  - if the commit history for the PR is "messy", e.g. there are many merge commits from other branches, or the author did not write well-formatted commit messages (see “Code style”, below).
  - if the PR is very old, i.e. it starts at an old commit on ``master``. However, it is better to rebase the PR branch on the HEAD of ``master`` and then use a merge commit (below).

- Use **rebase and merge**…

  - if the PR is only one or a few commits that are obviously related.
  - if the PR does not involve user-facing changes, i.e. does not need to be linked from the release notes.

- Use **merge pull request** (also written “create a merge commit”) in all other cases.

  PR branches *should* be rebased on the HEAD of ``master`` before merging.
  This is because some git-based tools will display commits from ``master`` and the PR branch interleaved if their dates and times are mixed, which makes it harder to read the commit history.
  Rebasing avoids this problem by ensuring each PR's commits are displayed together & in sequence.


Code style
==========

- Follow the `seven rules of a great Git commit message <https://chris.beams.io/posts/git-commit/#seven-rules>`_ for commit messages and PR titles.
- **Python:**

   - Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.
   - Docstrings are in the `numpydoc format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

- **R:** follow the style of the existing code base.
- Jupyter notebooks (:file:`.ipynb`): see below, under `Contribute tutorials`_.
- **Documentation** for ReStructuredText in :file:`.rst` files, and inline in :file:`.gms` files:

  - Do not hard-wrap lines.
  - Start each sentence on a new line.
  - Ensure Sphinx does not give warnings about ReST syntax for new or modified documentation.

- GAMS:

  - Wrap lines at 121 characters, except for inline documentation (see above).

- Other (file names, CLI, etc.): follow the style of the existing code base.


.. _releases:

Versions and releases
=====================

- We use `semantic versioning <https://semver.org>`_.

  To paraphrase: a **major** version increment (e.g. from 3.5 to 4.0) means there are *backwards-incompatible* changes to the API or functionality (e.g. code written for version 3.5 may no longer work with 4.0).
  Major releases always include migration notes in :doc:`whatsnew` to alert users to such changes and suggest how to adjust their code.
  A **minor** version increment may fix bugs or add new features, but does not change existing functionality.
  Code written for e.g. version 3.5 will continue to work with 3.6.

- Releases of :mod:`ixmp` and :mod:`message_ix` are generally made at the same time, and the version numbers kept synchronized.

- Each version of :mod:`message_ix` has a minimum required version of :mod:`ixmp`.

- We keep at least two active milestones on each of the message_ix and ixmp repositories:

  - The next minor version. e.g. if the latest release was 3.5, the next minor release/milestone is 3.6.
  - The next major version. e.g. 4.0.

- The milestones are closed at the time a new version is released.
  If a major release (e.g. 4.0) is made without the preceding minor release (e.g. 3.6), both are closed together.

- Every issue and PR should be assigned to a milestone to record the decision/intent to release it at a certain time.

- New releases are made by Energy Program staff using the `Release procedure <https://github.com/iiasa/message_ix/wiki/Release-procedure>`_, and appear on Github, PyPI, and conda-forge.

- There is no fixed **release schedule**, but new releases are generally made twice each year, sometimes more often.


Contribute tutorials
====================

Developers *and users* of the |MESSAGEix| framework are welcome to contribute **tutorials**, according to the following guidelines.
Per the license and CLA, tutorials will become part of the message_ix test suite and will be publicly available.

Developers **must** ensure new features (including :mod:`message_ix.tools` submodules) are fully documented.
This can be done via the API documentation (this site) and, optionally, a tutorial.
These have complementary purposes:

- The API documentation (built using Sphinx and ReadTheDocs) must completely, but succinctly, *describe the arguments and behaviour* of every class and method in the code.
- Tutorials serve as *structured learning exercises* for the classroom or self-study.
  The intended learning outcome for each tutorial is that students understand how the model framework API may be used for scientific research, and can begin to implement their own models or model changes.


Code and writing style
----------------------

- Format tutorials as Jupyter notebooks in Python or R.
- Only commit 'bare' notebooks to git, i.e. without cell output.
  Notebooks will be run and rendered when the documentation is generated.
- Add a line to ``tests/test_tutorials.py``, so that the parametrized test function runs the tutorial (as noted at :pull:`196`).
- Optionally, use Jupyter notebook slide-show features so that the tutorial can be viewed as a presentation.
- When relevant, provide links to publications or sources that provide greater detail for the methodology, data, or other packages used.
- Providing the mathematical formulation in the tutorial itself is optional.
- Framework specific variables and parameters or functions must be in italic.
- Relevant figures, tables, or diagrams should be added to the tutorial if these can help users to understand concepts.

  - Place rendered versions of graphics in a directory with the tutorial (see `Location`_ below).
    Use SVG, PNG, JPG, or other web-ready formats.


Structure
---------

Generally, a tutorial should have the following elements or sections.

- Tutorial introduction:

  - The general overview of tutorial.
  - The intended learning outcome.
  - An explanation of which features are covered.
  - Reference and provide links to any tutorials that are interlinked or part of a series.

- Description of individual steps:

  - A brief explanation of the step.
  - A link to any relevant mathematical documentation.

- Modeling results and visualizations:

  - Model outputs and post-processing calculations in tutorials should demonstrate usage of the :doc:`message_ix.reporting module <reporting>`.
  - Plots to depict results should use `pyam <https://github.com/IAMconsortium/pyam/>`_.
  - Include a brief discussion of insights from the results, in line with the learning objectives.

- Exercises: include self-test questions, small activities, and exercises at the end of a tutorial so that users (and instructors, if any) can check their learning.


Location
--------

Place notebooks in an appropriate location:

``tutorial/name.ipynb``:
   Stand-alone tutorial.

``tutorial/example/example_baseline.ipynb``:
   Group of tutorials named “example.”
   Each notebook's file name begins with the group name, followed by a name
   beginning with underscores.
   The group name can refer to a specific RES shared across multiple tutorials.
   Some example names include::

       <group>_baseline.ipynb

       <group>_basic.ipynb  # Basic modeling features, e.g.:
       <group>_emmission_bounds.ipynb
       <group>_emission_taxes.ipynb
       <group>_fossil_resources.ipynb

       <group>_adv.ipynb  # Advanced modeling features, e.g.:
       <group>_addon_technologies.ipynb
       <group>_share_constraints.ipynb

       <group>_renewables.ipynb  # Features related to renewable energy, e.g.:
       <group>_firm_capacity.ipynb
       <group>_flexible_generation.ipynb
       <group>_renewable_resources.ipynb


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

----

Included from :file:`CONTRIBUTOR_LICENSE.rst`:

.. include:: ../../CONTRIBUTOR_LICENSE.rst
