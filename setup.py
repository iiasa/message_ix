#!/usr/bin/env python
from __future__ import print_function

import os
import shutil

from setuptools import setup, find_packages
from setuptools.command.install import install

INFO = {
    'version': '1.0.0',
}


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


def all_files(path, strip=None):
    paths = [os.path.join(path, '*')]
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
        ],
    }
    cmdclass = {
        'install': Cmd,
    }
    pack_data = {
        'message_ix': all_files('message_ix/model', strip='message_ix'),
    }
    setup_kwargs = {
        "name": "message_ix",
        "version": INFO['version'],
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
