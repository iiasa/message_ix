import argparse
import json
import logging
import os
import shutil

from message_ix.default_paths import CONFIG_PATH, DEFAULT_MODEL_PATH
from message_ix.utils import logger


def recursive_copy(src, dst, overwrite=False):
    """Copy src to dst recursively"""
    for root, dirs, files in os.walk(src):
        for f in files:
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


def config(model_path=None, overwrite=False):
    config = {}

    if model_path:
        model_path = os.path.abspath(os.path.expanduser(model_path))
        if not os.path.exists(model_path):
            logger().info('Creating model directory: {}'.format(model_path))
            os.makedirs(model_path)
        recursive_copy(DEFAULT_MODEL_PATH, model_path, overwrite=overwrite)
        config['MODEL_PATH'] = model_path

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, mode='r') as f:
            data = json.load(f)
        data.update(config)
        config = data

    if config:
        with open(CONFIG_PATH, mode='w') as f:
            logger().info('Updating configuration file: {}'.format(CONFIG_PATH))
            json.dump(config, f)
