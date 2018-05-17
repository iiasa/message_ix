#!/usr/bin/env python
from __future__ import print_function

import os
import shutil
import sys
import glob

from setuptools import setup, Command, find_packages
from setuptools.command.install import install

INFO = {
    'version': '1.0.0',
}


_here = os.path.dirname(os.path.realpath(__file__))
_local_path = os.path.expanduser(os.path.join('~', '.local', 'message_ix'))
_default_paths_py_path = os.path.join(_here, 'message_ix', 'default_paths.py')
_default_paths_py = """
import os

fullpath = lambda *x: os.path.abspath(os.path.join(*x))

ROOT_DIR = fullpath(r'{local_path}')
MODEL_DIR = fullpath(ROOT_DIR, 'model')
DATA_DIR = fullpath(ROOT_DIR, 'model', 'data')
OUTPUT_DIR = fullpath(ROOT_DIR, 'model', 'output')
MSG_TEST_DIR = fullpath(r'{here}', 'tests')

""".format(local_path=_local_path, here=_here)


def copy_with_replace(src, dst):
    """Copy src to dst overwriting existing files"""
    for root, dirs, files in os.walk(src):
        for f in files:
            rel_path = root.replace(src, '').lstrip(os.sep)
            dst_path = os.path.join(dst, rel_path)

            if not os.path.isdir(dst_path):
                os.makedirs(dst_path)

            shutil.copyfile(os.path.join(root, f),
                            os.path.join(dst_path, f))


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
        print('Copying model files to: {}'.format(dst))
        copy_with_replace(src, dst)

    def _write_default_paths(self):
        print('Writing default_paths.py')
        with open(_default_paths_py_path, 'w') as f:
            f.write(_default_paths_py)

    def _clean_default_paths(self):
        print('removing default_paths.py')
        os.remove(_default_paths_py_path)

    def run(self):
        self._write_default_paths()
        install.run(self)
        self._clean_default_paths()
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
    rtn = setup(**setup_kwargs)


if __name__ == "__main__":
    main()
