.. _releases:

Versions and releases
*********************

- We use `semantic versioning <https://semver.org>`_.

  To paraphrase: a **major** version increment (e.g. from 3.5 to 4.0) means there are *backwards-incompatible* changes to the API or functionality (e.g. code written for version 3.5 may no longer work with 4.0).
  Major releases always include migration notes in :doc:`/whatsnew` to alert users to such changes and suggest how to adjust their code.
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

- New releases are made by ECE Program staff using the :doc:`release`, and appear on Github, PyPI, and conda-forge.

- There is no fixed **release schedule**, but new releases are generally made twice each year, sometimes more often.
