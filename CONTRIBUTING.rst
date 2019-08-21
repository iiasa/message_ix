Contributing to |MESSAGEix| development
=======================================

We welcome contributions to the code base and development of new features for the |MESSAGEix| framework.
This page contains guidelines for making these contributions.

.. contents::
  :local:


Filing issues for bugs and enhancements
---------------------------------------

We use Github **issues** for several purposes:

- Ask and answer questions about intended behaviour or issues running the framework or related models.
- Report bugs, i.e. unintended or undocumented behaviour.
- Request changes to behaviour.
- Request specific enhancements and new features, both urgent and long-term/low-priority.
- Discuss and design of other improvements.

Please search through open *and* closed issues for *both* the `message_ix <https://github.com/iiasa/message_ix/issues?q=is:issue>`_ and `ixmp <https://github.com/iiasa/ixmp/issues?q=is:issue>`_ repositories.
Review any related issues.
Then, if your issue is not found, `open a new one <https://github.com/iiasa/message_ix/issues/new>`_.


Contributing code via Github PRs
--------------------------------

See the `short introduction to the Github flow <https://guides.github.com/introduction/flow/>`_, which describes a **pull request** and how it is used.
Use online documentation for git, Github, and Python to ensure you are able to complete the process below.
Register a Github account, if you do not already have one.

1. Choose a repository
~~~~~~~~~~~~~~~~~~~~~~

Decide: to which part of the |MESSAGEix| software stack should your code be added?

``ixmp``
   Contributions not specific to |MESSAGEix| model framework, e.g. that could be used for other, non-MESSAGE models.
``message_ix``
   Contributions not specific to *any particular MESSAGEix* model instance.
   Additions to ``message_ix`` should be usable in any MESSAGE-scheme model.
``message_data`` or ``message_doc``
   Contributions to the MESSAGE-GLOBIOM family of models, including the global
   model; and its documentation, respectively.
``ixmp_source``
   Java / JDBC backend for ``ixmp``.

2. Fork, branch, and open a pull request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fork the chosen repository to your own Github account.
Create a branch with an appropriate name:

- ``all-lower-case-with-hyphens``.
- ``issue/1234`` if you are addressing a specific issue.
- ``feature/do-something`` if you are adding a new feature.

Open a PR (e.g. on `message_ix <https://github.com/iiasa/message_ix/pulls>`_) to merge your code into the ``master`` branch.
The ``message_ix`` and ``ixmp`` repositories each have a template for the text of the PR, including the minimum requirements:

- A title and one-sentence summary of the change.
  This is like the abstract of a publication: it should help a developer/reviewer/user quickly learn what the PR is about.
- Confirm that unit or integration tests have been added or revised to cover the changed code, and that the tests pass (see below).
- Confirm that documentation of the API and its usage is added or revised as necessary.
- Add a line to the file ``RELEASE_NOTES.md`` describing the changes (use the same title or one-sentence summary as above) and linking to the PR.

Optionally:

- Include a longer description of the design, or any changes whose purpose is not clear by inspecting code.
- Put “WIP:” at the start of the PR title to indicate “work in progress” while you continue to add commits.
  This is good development practice: it ensures the automatic checks pass as you add to the code on your branch.

3. Ensure checks pass
~~~~~~~~~~~~~~~~~~~~~

|MESSAGEix| currently has three kinds of **automatic**, or “continuous integration” checks:

- The `CLA Assistant <https://github.com/cla-assistant/>`_ ensures you have signed the `Contributor License Agreement`_ (text below).
  All contributors are required to sign the CLA before any pull request can be reviewed.
  This ensures that all future users can benefit from your contribution, and that your contributions do not infringe on anyone else's rights.
- The `Stickler <https://stickler-ci.com/>`_ service reviews Python code style (see below).
- `Travis <https://travis-ci.org/iiasa/message_ix/>`_ (Linux, macOS) and `AppVeyor <https://ci.appveyor.com/project/danielhuppmann/message-ix>`_ (Windows) run the test suite in ``tests/``.

Resolve any non-passing checks—seeking help if needed.

If your PR updates the documentation, **manually** check that it can be built.
See ``doc/README.rst``.

4. Review
~~~~~~~~~

Using the GitHub sidebar on your PR, request a review from another |MESSAGEix| contributor.
GitHub suggests reviewers; optionally, contact the IIASA Energy Program to ask who should review your code.
Address any comments raised by the reviewer, who will also merge your PR when it is ready.


Other tips
~~~~~~~~~~

- If other PRs are merged before yours, a **merge conflict** may arise and must be addressed to complete the above steps.
  This means that your PR, and the other PR, both modify the same file(s) in the same location(s), and git cannot automatically determine which changes to use.
  Learn how to:

  - `git merge <https://git-scm.com/docs/git-merge>`_. This brings all updates from the ``master`` branch into your PR branch, giving you a chance to fix conflicts and make a new commit.
  - `git rebase <https://git-scm.com/docs/git-rebase>`_. This replays your PR branch commits one-by-one, starting from the tip of the ``master`` branch (rather than the original starting commit).


Code style
----------

- Python: follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.
- R: follow the style of the existing code base.
- Jupyter notebooks (``.ipynb``): see below, under `Contributing tutorials`_.
- Documentation (``.rst``, ``.md``):

  - Do not hard-wrap lines.
  - Start each sentence on a new line.

- Other (file names, CLI, etc.): follow the style of the existing code base.


Versions and releases
---------------------

- We use `semantic versioning <https://semver.org>`_.
- We keep at least two active milestones on each of the ``message_ix`` and ``ixmp`` repositories:

  - The next minor version. E.g. if the latest release was 3.5, the next minor release/milestone is 3.6.
  - The next major version. E.g. 4.0.

- The milestones are closed at the time a new version is released.
  If a major release (e.g. 4.0) is made without the preceding minor release (e.g. 3.6), both are closed together.

- Every issue and PR must be assigned to a milestone to record the decision/intent to release it at a certain time.

- New releases are made by Energy Program staff using the `Release procedure <https://github.com/iiasa/message_ix/wiki/Release-procedure>`_, and appear on Github, PyPI, and conda-forge.


Contributing tutorials
----------------------

Developers *and users* of the |MESSAGEix| framework are welcome to contribute **tutorials**, according to the following guidelines.
Per the license and CLA, tutorials will become part of the ``message_ix`` test suite and will be publicly available.

Developers **must** ensure new features (including ``message_ix.tools`` submodules) are fully documented.
This can be done via the API documentation (this site) and, optionally, a tutorial.
These have complementary purposes:

- The API documentation (built using Sphinx and ReadTheDocs) must completely, but succinctly, *describe the arguments and behaviour* of every class and method in the code.
- Tutorials serve as *structured learning exercises* for the classroom or self-study.
  The intended learning outcome for each tutorial is that students understand how the model framework API may be used for scientific research, and can begin to implement their own models or model changes.

Coding & writing style
~~~~~~~~~~~~~~~~~~~~~~

- Tutorials are formatted as Jupyter notebooks in Python or R.
- Commit 'bare' notebooks in git, i.e. without cell output.
  Notebooks will be run and rendered when the documentation is generated.
- Add a line to ``tests/test_tutorials.py``, so that the parametrized test function runs the tutorial (as noted at `#196 <https://github.com/iiasa/message_ix/pull/196>`_).
- Optionally, use Jupyter notebook slide-show features so that the tutorial can be viewed as a presentation.
- When relevant, provide links to publications or sources that provide greater detail for the methodology, data, or other packages used.
- Providing the mathematical formulation in the tutorial itself is optional.
- Framework specific variables and parameters or functions must be in italic.
- Relevant figures, tables, or diagrams should be added to the tutorial if these can help users to understand concepts.

  - Place rendered versions of graphics in a directory with the tutorial (see `Location`_ below).
    Use SVG, PNG, JPG, or other web-ready formats.

Structure
~~~~~~~~~

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
~~~~~~~~

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
