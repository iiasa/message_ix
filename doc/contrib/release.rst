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
  - Accounts on both https://test.pypi.org and https://pypi.org.
  - "Maintainer" or "Owner" permissions for both projects on both sites; i.e. your account should appear in https://test.pypi.org/manage/project/ixmp/collaboration/.

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

1. Mark new deprecations.
   Explicitly state the version when the removal is targeted, so that users can adjust their code.
2. Remove items targeted for this release.

   .. note:: This can be done at any point, and should be done before the release prep begins.
      For instance, a feature marked as deprecated in v2.0 *should* be removed before 3.0 is released.
      But *may* also be removed from the ``master`` branch *immediately after* 2.0.0 is released.
      This is preferred, because it forces tutorials, user code, etc. to stay ahead of deprecations.

Releasing
=========

1. Create a "release candidate" (RC) branch named e.g. 'prepare-<version>' or 'release-<version>'.
2. Update the following files:

   1. :file:`setup.cfg` (message_ix only):
      Update the ``install_requires`` line for ixmp.
      Each version of message_ix depends on the corresponding version of ixmp.
      For instance, message_ix 3.1 depends on ixmp 3.1; not ixmp 3.0.

   2. :file:`RELEASE_NOTES.rst`:

      - Rename the section "Next Release" to "``v<version>`` (YYYY-MM-DD)".
      - Add a short text description summarizing the release.
      - Optionally, add a subsection "Migration notes" explaining to users how to adjust to changes in the release.

   3. :file:`tutorial/README.rst`: Adjust the links to the tutorials, replacing all instances of ``/blob/master/`` with ``blob/v<version>/``.
   4. :file:`rmessageix/DESCRIPTION` (message_ix only): Set the "Version:"" line to ``<version>``.

   Commit with a message like “Prepare ``v<version>``”.

3. Create a pull request to merge the RC branch into 'master'.

   1. Ensure all continuous integration checks pass.
   2. On `Read The Docs <https://readthedocs.com>`_, enable the build of the RC branch and ensure the docs build correctly.

4. Test publishing using TestPyPI.

   1. On your local machine, create a *temporary* tag for the release number, adding a 'rc' suffix::

        git tag v<version>rc1

      - This is **NOT** the commit we will distribute. The tag is only for testing.
      - **DO NOT** push this tag anywhere, e.g. to GitHub!

   2. Build and check::

        rm -rf build dist
        python3 setup.py bdist_wheel sdist
        twine check dist/*

      This should complete without any errors.
      If it does not: fix any issues, create new commit(s), retag (``git tag --delete v<version>rc1`` then ``git tag v<version>rc1``), and try again.

   3. Publish and check::

        twine upload -r testpypi dist/*

      View and download the package from TestPyPI to ensure the README and contents are complete and free of errors.
      If they are not, fix any issues, create new commit(s), and try again fro step (4)(1), using an incremented ``rc`` part, e.g. ``v<version>rc2``.

   4. Delete all test tags created::

        git tag --delete v<version>rc1
        git tag --delete v<version>rc2
        # etc.

5. On Github, merge the RC PR using the ‘rebase’ approach.
6. On your local machine, pull the now-updated 'master', tag and push:

    git checkout master
    git pull <upstream> master
    git tag v<version>
    git push <upstream> --tags

7. On `Read The Docs`_, set the privacy level for the docs built from the new ``v<version>`` tag to “Public.”
8. Publish on PyPI::

    rm -rf build dist
    python3 setup.py bdist_wheel sdist
    twine check dist/*
    twine upload dist/*

    # Also upload to testpypi, so the latest version is not the RC above
    twine upload -r testpypi dist/*

9. Create a new release on GitHub.

   - Choose the existing tag ``v<version>`` created/pushed earlier; *do not* create a new one.
   - For the description, provide a link to the section in the “What's New” page of the documentation that corresponds to the new release.
     For example:

     .. code-block:: markdown

        See the [“What's New” page](https://docs.messageix.org/projects/ixmp/en/stable/whatsnew.html#v3-1-0-2020-08-28) in the ixmp documentation for a list of all changes.


10. Update on conda-forge.
    A PR should automatically be opened by a bot after the GitHub release (sometimes this takes up to 30 minutes).

    1. Confirm that any new dependencies are added. The minimum versions in :file:`meta.yaml` should match the versions in :file:`setup.cfg`.
    2. Ensure that tests pass and complete any other checklist items.
    3. Merge the PR.
    4. Check that the new package version appears on conda-forge. This may take up to several hours.

11. Announce the release(s) on our mailing list/Google group and/or on Twitter.
    Copy the text from the What's New page of the built documentation.

After the release
=================

**Update the following files.** Make a single commit directly to 'master' with a message like “Reset to development state”.
The following changes essentially reverse the changes under step (2) in the release procedure, above.

- :file:`RELEASE_NOTES.rst`: Add new section "Next Release" and subsection "All changes" above the section for the release.
- :file:`tutorial/README.rst`: Replace all instances of ``/blob/v<version>/`` with ``blob/master/``.
- :file:`rmessageix/DESCRIPTION`: (message_ix only) Append ".9000" to the "Version: " line, e.g. "2.0.0.9000" to indicate a development version following v2.0.0.
