#!/usr/bin/env python
from __future__ import print_function

import os
import shutil
import sys
import glob

from setuptools import setup, Command, find_packages
from setuptools.command.install import install

INFO = {
    'version': '0.1.0',
}


_here = os.path.dirname(os.path.realpath(__file__))
_local_path = os.path.expanduser(os.path.join('~', '.local', 'message_ix'))
paths = """
import os

fullpath = lambda *x: os.path.abspath(os.path.join(*x))

ROOT_DIR = fullpath(r'{local_path}')
MODEL_DIR = fullpath(ROOT_DIR, 'model')
DATA_DIR = fullpath(ROOT_DIR, 'model', 'data')
OUTPUT_DIR = fullpath(ROOT_DIR, 'model', 'output')
MSG_TEST_DIR = fullpath(r'{here}', 'tests')

""".format(local_path=_local_path, here=_here)


class Cmd(install):
    """Custom clean command to tidy up the project root."""

    def initialize_options(self):
        install.initialize_options(self)

    def finalize_options(self):
        install.finalize_options(self)

    def _clean_dirs(self):
        dirs = [
            'message_ix.egg-info'
        ]
        for d in dirs:
            print('removing {}'.format(d))
            shutil.rmtree(d)

    def _copy_model(self):
        src = os.path.join(_here, 'model')
        dst = os.path.join(_local_path, 'model')
        shutil.copytree(src, dst)

    def run(self):
        install.run(self)
        self._clean_dirs()
        self._copy_model()


def main():
    packages = [
        'message_ix'
    ]
    pack_dir = {
        'message_ix': 'message_ix',
    }
    entry_points = {
        'console_scripts': [
        ],
    }
    cmdclass = {
        'install': Cmd,
    }
    pack_data = {}
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
    print('Writing default_paths.py')
    pth = os.path.join('message_ix', 'default_paths.py')
    with open(pth, 'w') as f:
        f.write(paths)
    rtn = setup(**setup_kwargs)
    print('removing default_paths.py')
    os.remove(pth)


if __name__ == "__main__":
    main()
