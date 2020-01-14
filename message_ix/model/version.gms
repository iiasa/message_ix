* This file specifies the release version number of MESSAGEix.
* The version number must match the MESSAGEix-scheme version number
* in the compiled `ixmp.jar`.

* !!! DO NOT CHANGE VALUES IN THIS FILE MANUALLY !!!

* Changes have to be done by pulling the respective version
* from the Github repository at https://github.com/iiasa/message_ix,
* or by updating the `message_ix` package
* using `conda update -c conda-forge message-ix`.

$SETGLOBAL VERSION_MAJOR "2"
$SETGLOBAL VERSION_MINOR "0"
$SETGLOBAL VERSION_PATCH "0"

* This file is imported by `message_ix/__init__.py`.
* In the documentation rst files, the tag ``|version|`` in any mark-up docstring
* is replaced by '%VERSION_MAJOR%.%VERSION_MINOR%'.
