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
    `conda-forge/message-ix-feedstock <https://github.com/conda-forge/message-ix-feedstock>`__
    repositories.
    This means your Github account is listed in the :file:`recipe/meta.yaml`, under the key ``recipe-maintainers:``.

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
      But *may* also be removed from the ``master`` branch *immediately after* 2.0.0 is released.
      This is preferred, because it forces tutorials, user code, etc. to stay ahead of deprecations.

3. Check https://github.com/iiasa/message-ix/actions?query=branch:master (or equivalent for ixmp) to ensure that the push and scheduled builds are passing.
4. Check https://readthedocs.com/projects/iiasa-energy-program-message-ix/builds/ (or equivalent for ixmp) to ensure that the docs build is passing.

Any failures in (3) or (4) must be corrected before releasing.
If necessary, make and merge ≥1 PR(s) to address (1–4).

Releasing
=========

1. Create a "release candidate" (RC) branch named e.g. 'prepare-<version>' or 'release-<version>'.
2. Update the following files:

   1. :file:`setup.cfg` (message_ix only):
      Update the ``install_requires`` line for ixmp.
      Each version of message_ix must depend on the corresponding version of ixmp.
      For instance, message_ix 3.1.0 depends on ixmp ≥ 3.1.0; not ixmp 3.0.0

   2. :file:`RELEASE_NOTES.rst`:

      - Comment the heading "Next release", then insert another heading below it, at the same level, with the version number and date, e.g.:

        .. code-block:: rest

           .. Next release
           .. ============

           v99.98.0 (2035-10-12)
           =====================

      - Add a short text description summarizing the release.
      - If necessary, add a subsection "Migration notes" explaining to users how to adjust to changes in the release.

      Build the docs locally to ensure any ReST markup in these additions renders correctly.

   3. :file:`rmessageix/DESCRIPTION` (message_ix only): Set the "Version:"" line to ``<version>``.

   Commit with a message like “Prepare ``v<version>``”.

3. Push the RC branch to GitHub.
   Create a pull request to merge the RC branch into 'master'.
   Ensure all continuous integration checks pass, then merge the PR.

4. On your local machine, pull the now-updated 'master' branch, tag the release candidate version, i.e. with a ``rcN`` suffix, and push::

    $ git checkout master
    $ git pull
    $ git tag v<version>rc1
    $ git push --tags origin master

5. Check:

   - at https://github.com/iiasa/message-ix/actions?query=workflow:publish that the workflow completes: the package builds successfully and is published to TestPyPI.
   - at https://test.pypi.org/project/message-ix/ that:

      - The package can be downloaded, installed and run.
      - The README is rendered correctly.

   Address any warnings or errors that appear.
   If needed, repeat steps (1–4), incrementing the rc number.

6. (optional) Tag the release itself and push::

    $ git tag v<version>
    $ git push --tags origin master

   This step (but *not* step (4)) can also be performed directly on GitHub; see (6), next.

7. Visit https://github.com/iiasa/message-ix/releases and mark the new release: either using the pushed tag from (6), or by creating the tag and release simultaneously.

   For the description, provide a link to the section in the “What's New” page of the documentation that corresponds to the new release.
   For example:

   .. code-block::

      See the [“What's New” page](https://docs.messageix.org/en/stable/whatsnew.html) in the documentation for a list of all changes.

8. Check at https://github.com/iiasa/message-ix/actions?query=workflow:publish and https://pypi.org/project/message-ix/ that the distributions are published.

9. Update on conda-forge.
   A PR should automatically be opened by a bot after the GitHub release (sometimes this takes up to 30 minutes).

   1. Confirm that any new dependencies are added.
      The minimum versions in :file:`meta.yaml` should match the versions in :file:`setup.cfg`.
   2. Ensure that tests pass and complete any other checklist items.
   3. Merge the PR.
   4. Check that the new package version appears on conda-forge. This may take up to several hours.

10. Announce the release(s) on our mailing list/Google group and/or on Twitter.
    Copy the text from the What's New page of the built documentation.

After the release
=================

**Update the following files.** Make a single commit directly to 'master' with a message like “Reset to development state”.
The following changes essentially reverse the changes under step (2) in the release procedure, above.

- :file:`rmessageix/DESCRIPTION`: (message_ix only) Append ".9000" to the "Version: " line, e.g. "2.0.0.9000" to indicate a development version following v2.0.0.
