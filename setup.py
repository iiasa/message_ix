#!/usr/bin/env python
from __future__ import print_function

import os
import re
import shutil

from setuptools import setup, find_packages
from setuptools.command.install import install

fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     'message_ix', 'model', 'version.gms')
with open(fname) as f:
    s = str(f.readlines())

VERSION = '{}.{}.{}'.format(
    re.search('VERSION_MAJOR "(.+?)"', s).group(1),
    re.search('VERSION_MINOR "(.+?)"', s).group(1),
    re.search('VERSION_PATCH "(.+?)"', s).group(1),
)


class Cmd(install):
    """Custom clean command to tidy up the project root."""

    def initialize_options(self):
        install.initialize_options(self)

    def finalize_options(self):
        install.finalize_options(self)

    def _clean_dirs(self):
        dirs = [
            'message_ix.egg-info',
            'build',
        ]
        for d in dirs:
            print('removing {}'.format(d))
            shutil.rmtree(d)

    def run(self):
        install.run(self)
        self._clean_dirs()


def all_subdirs(path, strip=None):
    paths = []
    for root, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            paths.append(os.path.join(root, dirname, '*'))
    if strip:
        n = len(strip) if strip.endswith(os.sep) else len(strip + os.sep)
        paths = [x[n:] for x in paths]
    return paths


def main():
    packages = [
        'message_ix'
    ]
    pack_dir = {
        'message_ix': 'message_ix',
    }
    entry_points = {
        'console_scripts': [
            'messageix-config=message_ix.cli:config',
            'messageix-dl=message_ix.cli:dl',
        ],
    }
    cmdclass = {
        'install': Cmd,
    }
    pack_data = {
        # for some reason the model/ directory had to be added separately
        # it worked locally but not on CI:
        # https://circleci.com/gh/iiasa/message_ix/29
        'message_ix': all_subdirs('message_ix/model', strip='message_ix') +
        ['model/*gms', 'model/*opt'],
    }
    setup_kwargs = {
        "name": "message_ix",
        "version": VERSION,
        "description": 'The MESSAGEix Integrated Assessment Model',
        "author": 'Daniel Huppmann, Matthew Gidden, Volker Krey,  '
                  'Oliver Fricko, Peter Kolp',
        "author_email": 'message_ix@iiasa.ac.at',
        "url": 'http://github.com/iiasa/message_ix',
        "packages": packages,
        "package_dir": pack_dir,
        "package_data": pack_data,
        "entry_points": entry_points,
        "cmdclass": cmdclass,
    }
    rtn = setup(**setup_kwargs)


if __name__ == "__main__":
    main()
