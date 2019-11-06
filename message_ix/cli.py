import os
from pathlib import Path
import shutil
from urllib.request import urlretrieve
import tempfile
import zipfile

import click
from ixmp import config
from ixmp.cli import main
from ixmp.utils import logger
import message_ix


# Override the docstring of the ixmp CLI so that it masquerades as the
# message_ix CLI
main.help == \
    """MESSAGEix command-line interface

    To view/run the 'nightly' commands, you need the testing dependencies.
    Run `pip install [--editable] .[tests]`.
    """


def recursive_copy(src, dst, overwrite=False, skip_ext=[]):
    """Copy src to dst recursively"""
    for root, dirs, files in os.walk(src):
        for f in [f for f in files if os.path.splitext(f)[1] not in skip_ext]:
            rel_path = root.replace(src, '').lstrip(os.sep)
            dst_path = os.path.join(dst, rel_path)

            if not os.path.isdir(dst_path):
                os.makedirs(dst_path)

            fromf = os.path.join(root, f)
            tof = os.path.join(dst_path, f)
            exists = os.path.exists(tof)
            if exists and not overwrite:
                logger().info('{} exists, will not overwrite'.format(tof))
            else:
                logger().info('Writing to {} (overwrite is {})'.format(
                    tof, 'ON' if overwrite else 'OFF'))
                shutil.copyfile(fromf, tof)


@main.command('copy-model')
@click.option('--set-default', is_flag=True,
              help='Set the copy to be the default used when running MESSAGE.')
@click.option('--overwrite', is_flag=True,
              help='Overwrite existing files.')
@click.argument('path', type=click.Path(file_okay=False))
def copy_model(path, overwrite, set_default):
    """Copy the MESSAGE GAMS files to a new PATH.

    To use an existing set of GAMS files, use instead:

    message-ix config set "message model dir" PATH
    """
    path = Path(path).resolve()

    if not path.exists():
        print('Creating model directory: {}'.format(path))
        path.mkdir()
        recursive_copy(Path(__file__).parent / 'model', path,
                       overwrite=overwrite, skip_ext=['gdx'])

    if set_default:
        config.set('message model dir', path)
        config.save()


def tempdir_name():
    return os.path.join(tempfile._get_default_tempdir(),
                        next(tempfile._get_candidate_names()))


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
        dst = Path(td) / zipname
        urlretrieve(url, dst)

        archive = zipfile.ZipFile(dst)

        print('Unzipping {} to {}'.format(dst, path))
        path.mkdir(parents=True, exist_ok=True)
        archive.extractall(path)


try:
    import message_ix.testing.nightly
except ImportError:
    # Dependencies of testing.nightly are missing; don't show the command
    pass
else:
    main.add_command(message_ix.testing.nightly.cli)
