<!--

Delete each of these instruction comments as you complete it.

Title: use a short, declarative statement similar to a commit message,
e.g. “Change [thing X] to [fix solve bug|enable feature Y]”

-->

**Required:** write a single sentence that describes the changes made by this PR.

<!-- Optional: write a longer description to help a reviewer understand the PR in ~3 minutes. -->

## How to review

**Required:** describe specific things that reviewer(s) must do, in order to ensure that the PR achieves its goal.
If no review is required, write “No review:” and describe why.

<!--
For example, one or more of:

- Read the diff and note that the CI checks all pass.
- Run a specific code snippet or command and check the output.
- Build the documentation and look at a certain page.
- Ensure that changes/additions are self-documenting, i.e. that another
  developer (someone like the reviewer) will be able to understand what the code
  does in the future.
-->

## PR checklist

<!-- This item is always required. -->
- [ ] Continuous integration checks all ✅
<!--
The following items are all *required* if the PR results in changes to user-
facing behaviour, e.g. new features or fixes to existing behaviour. They are
*optional* if the changes are solely to documentation, CI configuration, etc.

In ambiguous cases, strike them out and add a short explanation, e.g.

- ~Add or expand tests.~ No change in behaviour, simply refactoring.
-->
- [ ] Add or expand tests; coverage checks both ✅
- [ ] Add, expand, or update documentation.
- [ ] Update release notes.
  <!--
  To do this, add a single line at the TOP of the “Next release” section of
  RELEASE_NOTES.rst, where '999' is the GitHub pull request number:

  - :pull:`999`: Title or single-sentence description from above.

  Commit with a message like “Add #999 to release notes”
  -->
