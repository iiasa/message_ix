Sharing tools, projects and publications
****************************************

We invite you to share your tools, projects and/or publications wxhich are using the |MESSAGEi| framework.
This page contains guidelines for making your usage of the |MESSAGEix| visible.


Share your usage
================

1. Fork and branch
------------------

Register a Github account, if you do not already have one.
Fork the |MESSAGEix| repository to your own Github account.
Create a branch with an appropriate name:

- ``all-lower-case-with-hyphens`` —underscores (``_``) are slower to type; don't use them.
- Don't use the ``main`` branch in your fork for a PR.
  This makes it hard for others to check out and play with your code.

2. Add your tool, project or publications
-----------------------------------------

Tools
`````

Project
```````

Publications
````````````
1. Add a figure representing your paper into the directory *message_ix/doc/_static/publication_figures*.

   - As a naming convention we make use of the DOI of your paper. Use everything after https://doi.org/ and use "-" instead of "/".
     For example if your DOI is https://doi.org/10.1016/j.scs.2021.103257 the name of your figure would be *10.1016-j.scs.2021.103257.jpeg*.
     The ending .jpeg can also be .png or else.

2. Add your paper to the different categories.

   - In the *message_ix/doc/publications* directory you find, next to the files of the various papers, REsT files of the different categories where you can add your paper to.
   - Please add the name of your paper underlined by "-".
   - Then add your figure with the following::

        .. figure:: ../_static/publication_figures/The_name_of_your_figure.The_ending_of_your_figure
           :width: 250px
           :align: right
   - Add authors, year and Journal as following::

        **McCollum, D.L., Zhou, W., Bertram, C. et al. (2018), Nature Energy**
   - Add the first max. 311 characters of the abstract of your paper followed by::

        ... :doc:`Read more →<The_name_of_your_paper>`
   - You can add your paper to as many categories as you think fits to the topic.

4. (Optional) Add new category

   - If a category is not listed, which represents your paper best, feel free to add an additional REsT file under *message_ix/doc/publications* underlining the heading with "=".
   - Link then the *publications.rst* file under *Topic* or *Geographic* (or any heading) with the following::

        - :doc:`publications/Name_of_the_file_with_new_category`

3. Open a pull request on MESSAGEix
-----------------------------------

Open a PR (e.g. on `message_ix`__) to merge your code into the ``main`` branch.
The ``message_ix`` repositories each have a template for the text of the PR that is designed to help you write a clear description.
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


4. Ensure checks pass
---------------------

|MESSAGEix| has several kinds of automatic, or *continuous integration*, checks:

- The `CLA Assistant <https://github.com/cla-assistant/>`_ ensures you have signed the :doc:`contrib/cla` (follow link for text).
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
     Each scenario's outputs are compared to an expected value listed in :file:`message_ix/tests/data/scenarios.yaml`.
     PRs that touch the GAMS code may cause the these objective function values to change; the values **must** be updated as part of such PRs.
     See the comments in the file for how to temporarily enable these checks for every commit on a PR branch.

  anaconda, miniconda
     These workflows check that the package can be installed from conda-forge using Anaconda and Miniconda, respectively, on Windows only.

Resolve any non-passing checks—seeking help if needed.

If your PR updates the documentation, the ``lint`` check will confirm that it can be built.
However, you should also *manually* build and view the HTML documentation on your machine to confirm that the generated HTML is as expected, and address any warnings generated by Sphinx during the build phase.
See ``doc/README.rst``.


5. Review
---------

Using the GitHub sidebar on your PR, request a review from another |MESSAGEix| contributor.
GitHub suggests reviewers; optionally, contact the IIASA ECE Program to ask who should review your code.

- If you want them to follow along with progress, tag them in the PR description, like “FYI @Alice @Bob”.
- Only formally request review once the code is ready to review.
  Doing this sends e-mail and other notifications (e.g. in Slack, the “Pull Reminders” bot sends notices every day).
  If the code is not yet complete and ready for review, these notifications are noise.

Address any comments raised by the reviewer.


6. Merge
--------

GitHub provides `three ways to incorporate a pull request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-merges>`_: merge, rebase, and squash.
Current practice for the ``ixmp``, ``message_ix``, and ``message_data`` repositories is:

- Use **squash and merge**…

  - if the commit history for the PR is "messy", e.g. there are many merge commits from other branches, or the author did not write well-formatted commit messages (see “Code style”, below).
  - if the PR is very old, i.e. it starts at an old commit on ``main``. However, it is better to rebase the PR branch on the HEAD of ``main`` and then use a merge commit (below).

- Use **rebase and merge**…

  - if the PR is only one or a few commits that are obviously related.
  - if the PR does not involve user-facing changes, i.e. does not need to be linked from the release notes.

- Use **merge pull request** (also written “create a merge commit”) in all other cases.

  PR branches *should* be rebased on the HEAD of ``main`` before merging.
  This is because some git-based tools will display commits from ``main`` and the PR branch interleaved if their dates and times are mixed, which makes it harder to read the commit history.
  Rebasing avoids this problem by ensuring each PR's commits are displayed together & in sequence.

