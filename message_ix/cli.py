import argparse
import json
import message_ix
import os
import shutil
import tempfile
import zipfile


from six.moves.urllib.request import urlretrieve

from message_ix.default_path_constants import CONFIG_PATH, DEFAULT_MODEL_PATH
from message_ix.utils import logger


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


def do_config(model_path=None, overwrite=False):
    config = {}

    # make directory for config if doesn't exist
    dirname = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # update default path to model directory
    if model_path:
        model_path = os.path.abspath(os.path.expanduser(model_path))
        if not os.path.exists(model_path):
            logger().info('Creating model directory: {}'.format(model_path))
            os.makedirs(model_path)
        recursive_copy(DEFAULT_MODEL_PATH, model_path, overwrite=overwrite,
                       skip_ext=['gdx'])
        config['MODEL_PATH'] = model_path

    # overwrite config if already exists
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, mode='r') as f:
            data = json.load(f)
        data.update(config)
        config = data

    # write new config
    if config:
        with open(CONFIG_PATH, mode='w') as f:
            logger().info('Updating configuration file: {}'.format(CONFIG_PATH))
            json.dump(config, f)


def config():
    parser = argparse.ArgumentParser()
    model_path = 'Copy model files to a new path and configure MESSAGEix to use those files.'
    parser.add_argument('--model_path', help=model_path, default=None)
    overwrite = 'Overwrite existing files.'
    parser.add_argument('--overwrite', help=overwrite, action='store_true')
    args = parser.parse_args()
    do_config(model_path=args.model_path, overwrite=args.overwrite)


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
