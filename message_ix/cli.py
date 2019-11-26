from pathlib import Path
from shutil import copyfile
from urllib.request import urlretrieve
import tempfile
import zipfile

import click
from ixmp import config
from ixmp.cli import main
import message_ix
import message_ix.tools.add_year.cli


# Override the docstring of the ixmp CLI so that it masquerades as the
# message_ix CLI
main.help == \
    """MESSAGEix command-line interface

    To view/run the 'nightly' commands, you need the testing dependencies.
    Run `pip install [--editable] .[tests]`.
    """


@main.command('copy-model')
@click.option('--set-default', is_flag=True,
              help='Set the copy to be the default used when running MESSAGE.')
@click.option('--overwrite', is_flag=True,
              help='Overwrite existing files.')
@click.argument('path', type=click.Path(file_okay=False))
def copy_model(path, overwrite, set_default):
    """Copy the MESSAGE GAMS files to a new PATH.

    To use an existing set of GAMS files, you can also call:

        $ message-ix config set "message model dir" PATH
    """
    path = Path(path).resolve()

    src_dir = Path(__file__).parent / 'model'
    for src in src_dir.rglob('*'):
        # Skip certain files
        if src.suffix in ('.gdx', '.log', '.lst'):
            continue

        # Destination path
        dst = path / src.relative_to(src_dir)

        # Create parent directory
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.is_dir():
            # No further action for directories
            continue

        # Display output
        if dst.exists:
            if not overwrite:
                print('{} exists, will not overwrite'.format(dst))

                # Skip copyfile() below
                continue
            else:
                print('Overwriting {}'.format(dst))
        else:
            print('Copying to {}'.format(dst))

        copyfile(src, dst)

    if set_default:
        config.set('message model dir', path)
        config.save()


@main.command()
@click.option('--branch',
              help='Repository branch to download from (e.g., master).')
@click.option('--tag',
              help='Repository tag to download from (e.g., 1.0.0).')
@click.argument('path', type=click.Path())
def dl(branch, tag, path):
    if tag and branch:
        raise click.BadOptionUsage('Can only provide one of `tag` or `branch`')
    elif tag is None and branch is None:
        tag = '{}'.format(message_ix.__version__)
        print(tag)

    zipname = '{}.zip'.format(branch or 'v' + tag)
    url = 'https://github.com/iiasa/message_ix/archive/{}'.format(zipname)
    path = Path(path)

    with tempfile.TemporaryDirectory() as td:
        print('Retrieving {}'.format(url))
        zippath = Path(td) / zipname
        urlretrieve(url, zippath)

        archive = zipfile.ZipFile(zippath)

        print('Unzipping {} to {}'.format(zippath, path))
        path.mkdir(parents=True, exist_ok=True)
        archive.extractall(path)

        # Close *zipfile* so it can be deleted with *td*
        archive.close()


# Add subcommands
main.add_command(message_ix.tools.add_year.cli.main)

try:
    import message_ix.testing.nightly
except ImportError:
    # Dependencies of testing.nightly are missing; don't show the command
    pass
else:
    main.add_command(message_ix.testing.nightly.cli)
