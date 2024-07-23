* GDX scheme version
*
* !!! DO NOT CHANGE VALUES IN THIS FILE MANUALLY !!!
* Instead, update message_ix and ixmp as described in the documentation.
*
* Technical details:
*
* These numbers describe the contents of the GDX file written by the Java code
* in ixmp.jar. The Java code automatically generates some contents, e.g., set
* elements, in a way that cannot be controlled or overriden by Python ixmp or
* message_ix.
*
* Formerly, these numbers were incremented in ixmp_source, ixmp.jar, and this
* file, with every release. Currently, they will be incremented if (and *only*
* if) there are changes in the behaviour of the Java code that must be synced
* with corresponding changes in the GAMS source files in this directory.
*
* Eventually, all automatic behaviour will be moved from ixmp_source (Java) to
* ixmp (Python); see https://github.com/iiasa/message_ix/issues/254. At that
* point, both this file and MESSAGE/version_check.gms can be removed.

$SETGLOBAL VERSION_MAJOR "2"
$SETGLOBAL VERSION_MINOR "0"
