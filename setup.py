#!/usr/bin/env python
from __future__ import print_function

import os
import re
import shutil

from setuptools import setup
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

INSTALL_REQUIRES = [
    'ixmp>=0.1.3',
    'pandas',
    'xlrd',
    'XlsxWriter',
]

EXTRAS_REQUIRE = {
    'tests': ['pytest>=3.0.6'],
    'docs': ['numpydoc', 'sphinx>=1.8', 'sphinx_rtd_theme',
             'sphinxcontrib-bibtex'],
    'tutorial': ['jupyter', 'matplotlib'],
}

GMS_EXT = ['.gms', '.opt', '.md']


def all_subdirs(path, strip=None):
    paths = []
    for root, dirnames, files in os.walk(path):
        for f in [_f for _f in files if os.path.splitext(_f)[1] in GMS_EXT]:
            paths.append(os.path.join(root, f))
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
    }
    pack_data = {
        # for some reason the model/ directory had to be added separately
        # it worked locally but not on CI:
        # https://circleci.com/gh/iiasa/message_ix/29
        'message_ix': all_subdirs('message_ix/model', strip='message_ix')
    }
    setup_kwargs = {
        "name": "message_ix",
        "version": VERSION,
        "description": 'The MESSAGEix Integrated Assessment Model',
        "author": 'Daniel Huppmann, Matthew Gidden, Volker Krey,  '
                  'Oliver Fricko, Peter Kolp',
        "author_email": 'message_ix@iiasa.ac.at',
        "url": 'http://github.com/iiasa/message_ix',
        "install_requires": INSTALL_REQUIRES,
        "extras_require": EXTRAS_REQUIRE,
        "packages": packages,
        "package_dir": pack_dir,
        "package_data": pack_data,
        "entry_points": entry_points,
        "cmdclass": cmdclass,
    }
    rtn = setup(**setup_kwargs)


if __name__ == "__main__":
    main()
