Release procedure
*****************

.. contents::
   :local:
   :backlinks: none

Preliminaries
=============

- The procedure applies to both ixmp and message_ix.
- The ixmp release must be processed *before* message_ix.
- The person (or persons) processing the release needs the following authorizations:

  - Maintainer or Owner on both Github repositories.
  - Maintainer on the
    `conda-forge/ixmp-feedstock <https://github.com/conda-forge/ixmp-feedstock>`__
    and
    `message-ix-feedstock <https://github.com/conda-forge/message-ix-feedstock>`__
    repositories.
    This means your Github account is listed in each of them in the :file:`recipe/meta.yaml`, under the key ``recipe-maintainers:``. For an easy way of achieving that, see `the conda-forge docs <https://conda-forge.org/docs/maintainer/updating_pkgs.html#updating-the-maintainer-list>`__.

- In the below:

  - ``<version>`` stands for the full version number, e.g. ``1.2.0``.
    Always include all three parts: major, minor, and patch, i.e. ``1.2.0`` and never ``1.2``.
    Look very carefully to see when ``v<version>`` versus ``<version>`` should be used.
  - ``<upstream>`` stands for your local name for the Git remote that is the IIASA Github repository.

Before releasing
================

**Update these instructions.** Keep them current with actual practice.

**Handle deprecations.** You can find these by searching the code base for "deprecat".

A deprecation always involves *two* versions: (1) the version in which the item "is [marked as] deprecated", and (2) the version in which the item is removed.
These must always be separated by at least one major version.
For instance, an item marked as deprecated in v2.1 can be removed as of v3.0; an item marked as deprecated in v3.0 can be removed in v4.0, or later, e.g. in v5.0.

1. Mark any new deprecations.
   Explicitly state the version when the removal is targeted, so that users can adjust their code.

2. Remove any items targeted for removal in this release.

   .. note:: This can be done at any point, and should be done before the release prep begins.
      For instance, a feature marked as deprecated in v2.0 *should* be removed before 3.0 is released.
      But *may* also be removed from the ``main`` branch *immediately after* 2.0.0 is released.
      This is preferred, because it forces tutorials, user code, etc. to stay ahead of deprecations.

3. (message_ix only) Edit :file:`pyproject.toml`, updating the list ``dependencies`` in the ``project`` section for ixmp as necessary.

   Each version of message_ix depends on a minimum version of ixmp.
   message_ix **must not** depend on or use deprecated features of ixmp; it **should** remain compatible with earlier versions of ixmp, where possible.

**Check continuous integration.**
Any failures in (4) or (5) must be corrected before releasing.

4. Check https://github.com/iiasa/message_ix/actions/ (or `equivalent for ixmp <https://github.com/iiasa/ixmp/actions/>`__) to ensure that the push and scheduled builds are passing.
5. Check https://readthedocs.com/projects/iiasa-energy-program-message-ix/builds/ (or `ixmp <https://readthedocs.com/projects/iiasa-energy-program-ixmp/builds/>`_) to ensure that the docs build is passing.

If necessary, make and merge ≥1 PR(s) to address (1–5).

Releasing
=========

1. Create a new branch::

    $ git checkout -b release/X.Y.Z

2. Edit :file:`RELEASE_NOTES.rst`:

   - Comment the heading "Next release", and insert below it:

     - A commented "All changes" sub-heading (``---``)
     - A ReST anchor with the version number
     - Another heading (``===``) below it, with the version number and date

   - Add a short text description summarizing the release
   - If necessary, add a subsection "Migration notes" explaining to users how to adjust to changes in the release

   For example, the top of the file should look like:

   .. code-block:: rest
      :caption: Before editing

      Next release
      ============

      All changes
      -----------

      - Description of a change (:pull:`9999`).

   .. code-block:: rest
      :caption: After editing

      .. Next release
      .. ============

      .. All changes
      .. -----------

      .. _v99.98.0:

      v99.98.0 (2035-10-12)
      =====================

      Here is a description of the release.

      Migration notes
      ---------------

      Here is guidance on how to adjust to the release.

      All changes
      -----------

      - Description of a change (:pull:`9999`).

   Build the docs locally to ensure any ReST markup in these additions renders correctly.
3. Make a commit with a message like “Mark v<version> in release notes”.
4. (Only for message_ix) Update ``version`` and ``date-released`` in :file:`CITATION.cff`.
5. Tag the release candidate version, i.e. with a ``rcN`` suffix where ``N`` is a natural number, and push::

   $ git tag vX.Y.ZrcN
   $ git push --tags <upstream> release/X.Y.Z

6. Open a PR with the title “Release vX.Y.Z” using this branch.
   Check:

   - at https://github.com/iiasa/message_ix/actions/workflows/publish.yaml (or `ixmp <https://github.com/iiasa/ixmp/actions/workflows/publish.yaml>`__) that the workflow completes: the package builds successfully and is published to PyPI.
   - at https://pypi.org/project/message-ix/ (or `ixmp <https://pypi.org/project/ixmp/>`__) that:

     - The package can be downloaded, installed and run.
     - The README is rendered correctly.

   Address any warnings or errors that appear, if necessary through ≥1 new commit(s).
   Then continue from step (5), incrementing the release candidate number, e.g. from ``rc1`` to ``rc2``.

7. Merge the PR using the ‘rebase and merge’ method.
8. (optional) Tag the release itself and push::

    $ git tag v<version>
    $ git push --tags <upstream> main

   This step (but *not* step (5)) can be performed directly on GitHub; see (9), next.
9. Visit https://github.com/iiasa/message_ix/releases (or `ixmp <https://github.com/iiasa/ixmp/releases>`__) and mark the new release: either using the pushed tag from (8), or by creating the tag and release simultaneously.

   For the description, provide a link to the section in the “What's New” page of the documentation that corresponds to the new release, using the anchor added in (2), above.
   For example:

   .. code-block::

      See [“What's New”](https://docs.messageix.org/en/stable/whatsnew.html#v99-98-0) in the documentation for a list of all changes.

10. Check at https://github.com/iiasa/message_ix/actions/workflows/publish.yaml (or `ixmp <https://github.com/iiasa/ixmp/actions/workflows/publish.yaml>`__) and https://pypi.org/project/message-ix/ (or `ixmp <https://pypi.org/project/ixmp/>`__) that the distributions are published.
11. Update on conda-forge.
    A PR should automatically be opened by a bot after the GitHub release (sometimes this takes from 30 minutes to several hours).

    1. Confirm that any new dependencies are added.
       The minimum versions in :file:`meta.yaml` should match the versions in :file:`pyproject.toml`.
    2. Ensure that tests pass and complete any other checklist items.
    3. Merge the PR.
    4. Check that the new package version appears on conda-forge. This may take up to several hours.

12. Announce the release(s) on the GitHub Discussions pages and/or on Twitter.
    Copy the text from the What's New page of the built documentation.
