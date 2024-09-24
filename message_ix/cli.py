import logging
from pathlib import Path

import click
import ixmp
from ixmp.cli import main

import message_ix
import message_ix.tools.add_year.cli
import message_ix.tools.lp_diag.cli

log = logging.getLogger(__name__)

# Override the docstring of the ixmp CLI so that it masquerades as the
# message_ix CLI
main.help == """MESSAGEix command-line interface

    To view/run the 'nightly' commands, you need the testing dependencies.
    Run `pip install [--editable] .[tests]`.
    """

# Override the class used by the ixmp CLI to load Scenario objects
ixmp.cli.ScenarioClass = message_ix.Scenario


@main.command("copy-model")
@click.option(
    "--set-default",
    is_flag=True,
    help="Set the copy to be the default used when running MESSAGE.",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing files.")
@click.option("--quiet", is_flag=True, help="Don't print paths of copied files.")
@click.option(
    "--source-dir",
    type=click.Path(file_okay=False),
    help="Optional directory to copy files from.",
)
@click.argument("path", type=click.Path(file_okay=False))
def copy_model_cmd(path, overwrite, set_default, quiet, source_dir):
    """Copy the MESSAGE GAMS files to a new PATH.

    To use an existing set of GAMS files, you can also call:

        $ message-ix config set "message model dir" PATH
    """
    from message_ix.util import copy_model

    copy_model(path, overwrite, set_default, quiet, source_dir=source_dir)


@main.command()
@click.option("--branch", help="Repository branch to download from (e.g., main).")
@click.option("--tag", help="Repository tag to download from (e.g., v1.0.0).")
@click.argument("path", type=click.Path())
def dl(branch, tag, path):
    """Download MESSAGEix tutorial notebooks and extract to PATH.

    PATH is a local directory where to store the tutorial notebooks.
    """
    import json
    import os
    import tempfile
    import zipfile
    from urllib.request import Request, urlopen

    if tag and branch:
        raise click.UsageError(message="Can only provide one of `tag` or `branch`")
    elif branch:
        # Construct URL and filename from branch
        zipname = f"{branch}.zip"
        url = f"https://github.com/iiasa/message_ix/archive/{zipname}"
    else:
        # Get tag information using GitHub API
        args = dict(
            url="https://api.github.com/repos/iiasa/message_ix/tags",
            headers=dict(),
        )

        # The API rate-limits unathenticated requests by IP address. In some CI
        # environments (including the macOS on GitHub Actions), the build worker/runner
        # re-uses an address, so the limit can be exceeded and the request fails.
        # This (unadvertised) code uses a GitHub API token to avoid the rate limit.
        try:
            args["headers"]["authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        except KeyError:
            pass  # Variables not set

        with urlopen(Request(**args)) as response:
            tags_info = json.load(response)

        if tag is None:
            tag = tags_info[0]["name"]
            print(f"Default: latest release {tag}")

        # Get the zipball URL for the matching tag
        url = None
        for info in tags_info:
            if info["name"] == tag:
                url = info["zipball_url"]
                break

        if url is None:
            raise ValueError(f"tag {repr(tag)} does not exist")

        zipname = f"{tag}.zip"

    # Context manager to remove the TemporaryDirectory when complete
    with tempfile.TemporaryDirectory() as td:
        # Path for zip file
        zippath = Path(td) / zipname

        print(f"Retrieving {url}")
        with urlopen(url) as response:  # Unauthenticated request
            zippath.write_bytes(response.read())

        # Context manager to close the ZipFile when done, so it can be removed
        print(f"Unzipping {zippath} to {path}")
        with zipfile.ZipFile(zippath) as archive:
            # Zip archive successfully opened; create the output path
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)

            # Extract only tutorial files
            archive.extractall(
                path, members=filter(lambda n: "/tutorial/" in n, archive.namelist())
            )


# Add subcommands
main.add_command(message_ix.tools.add_year.cli.main)
main.add_command(message_ix.tools.lp_diag.cli.main)

try:
    import message_ix.testing.nightly
except ImportError:
    # Dependencies of testing.nightly are missing; don't show the command
    pass
else:
    main.add_command(message_ix.testing.nightly.cli)
