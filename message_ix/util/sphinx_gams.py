"""Sphinx extension for extracting inline documentation from GAMS source files."""

from os import PathLike
from pathlib import Path

try:
    from sphinx.util.display import status_iterator
except ImportError:  # Sphinx < 6.1
    # TODO remove this clause once message_ix requires Sphinx >= 6.1
    from sphinx.util import status_iterator  # type: ignore


def files(src_dir, target_dir, match="*.gms", ext=".rst"):
    """Return files in *src_dir* matching *match*.

    Two lists are returned; the second contains file names in *target_dir* with
    the replacement *ext*.

    """
    ins = list(src_dir.glob("**/" + match))
    outs = [target_dir / Path(inf).relative_to(src_dir).with_suffix(ext) for inf in ins]
    return ins, outs


def transcribe_docs(infp, outfp, source_filename):
    """Transcribe documentation lines from *infp* to *outfp*.

    Only lines between matched pairs of triple-star comments ('***') are
    copied.

    Returns True if any lines were encountered; otherwise False.

    """
    # State: None = no blocks encountered; True = in a block; False = outside
    on = None

    note = (
        ".. note:: This page is generated from inline documentation in ``{}``.\n\n"
    ).format(source_filename)

    for line in infp:
        if line.lstrip().startswith("***"):
            # Located a block divider
            if on:
                # Just finished a block, add a new line to the output
                outfp.write("\n")
            # Toggle between inside/outside of doc block
            on = not on
            # Write the header notice
            if note:
                outfp.write(note)
                note = None
        elif on:
            # Strip leftmost '* ' from the line
            base = "*".join(line.split("*")[1:])[1:]
            # Get rid of windows carriage return
            base = base.rstrip()
            outfp.write("{}\n".format(base))

    return on is not None


def main(app, config):  # pragma: no cover
    """Generate a mirrored tree of extracted documentation.

    Read all GAMS source files in *gams_source_dir*, and generate a mirrored
    tree of ReST documentation files in *gams_target_dir* containing any
    documentation blocks (appearing between triple-quoted comments; see
    transcribe_docs). Files without such blocks are omitted.
    """

    def docname(item):
        """Helper for status_iterator()."""
        return str(
            Path(item[0]).relative_to(app.config.gams_source_dir).with_suffix("")
        )

    # Locate GAMS source files and targets
    ins, outs = files(
        app.config.gams_source_dir, Path(app.srcdir) / app.config.gams_target_dir
    )

    # Iterator for logging
    it = status_iterator(
        zip(ins, outs),
        "generating GAMS sources... ",
        color="purple",
        length=len(ins),
        stringify_func=docname,
    )
    for inf, outf in it:
        # Make any parent directory(ies) of outf
        outf.parent.mkdir(parents=True, exist_ok=True)

        # Transcribe lines from the source file to the output file
        with open(inf, "r") as infp, open(outf, "w") as outfp:
            any_docs = transcribe_docs(
                infp, outfp, inf.relative_to(app.config.gams_source_dir)
            )

        if not any_docs:
            # No output was created; delete the file
            outf.unlink()


def setup(app):  # pragma: no cover
    """Sphinx extension configuration."""
    # Identify a variable to be set in the Sphinx conf.py
    app.add_config_value("gams_source_dir", Path("."), "env", (PathLike, str))
    app.add_config_value("gams_target_dir", Path("."), "env", (PathLike, str))

    # Hook into an early signal in the Sphinx build process
    app.connect("config-inited", main)
