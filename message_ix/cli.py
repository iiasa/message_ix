import argparse
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

import click
from ixmp import config
from ixmp.cli import main
from ixmp.utils import logger
import message_ix
from six.moves.urllib.request import urlretrieve


main.__doc__ == \
    """MESSAGEix command-line interface."""


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


def do_dl(tag=None, branch=None, repo_path=None, local_path='.'):
    if tag is not None and branch is not None:
        raise ValueError('Can only provide one of `tag` and `branch`')
    if tag is None and branch is None:
        tag = '{}'.format(message_ix.__version__)

    zipname = '{}.zip'.format(branch or 'v' + tag)
    url = 'https://github.com/iiasa/message_ix/archive/{}'.format(zipname)

    tmp = tempdir_name()
    os.makedirs(tmp)
    try:
        logger().info('Retrieving {}'.format(url))
        dst = os.path.join(tmp, zipname)
        urlretrieve(url, dst)

        archive = zipfile.ZipFile(dst)
        logger().info('Unzipping {} to {}'.format(dst, tmp))
        archive.extractall(tmp)

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        cpfrom = '{}/message_ix-{}/{}'.format(tmp, branch or tag, repo_path)
        cpto = '{}/{}'.format(local_path, repo_path)
        logger().info('Copying {} to {}'.format(cpfrom, cpto))
        recursive_copy(cpfrom, cpto, overwrite=True)

        shutil.rmtree(tmp)

    except Exception as e:
        logger().info("Could not delete {} because {}".format(tmp, e))


def dl():
    parser = argparse.ArgumentParser()
    repo_path = 'Path to files to download from repository (e.g., tutorial).'
    parser.add_argument('--repo_path', help=repo_path, default='tutorial')
    local_path = 'Path on place files on local machine.'
    parser.add_argument('--local_path', help=local_path, default='.')
    tag = 'Repository tag to download from (e.g., 1.0.0).'
    parser.add_argument('--tag', help=tag, default=None)
    branch = 'Repository branch to download from (e.g., master).'
    parser.add_argument('--branch', help=branch, default=None)
    args = parser.parse_args()
    do_dl(tag=args.tag, branch=args.branch, repo_path=args.repo_path,
          local_path=args.local_path)
