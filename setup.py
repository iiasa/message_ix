#!/usr/bin/env python
import os
import re

from setuptools import find_packages, setup


fname = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     'message_ix', 'model', 'version.gms')
with open(fname) as f:
    s = str(f.readlines())

VERSION = '{}.{}.{}'.format(
    re.search('VERSION_MAJOR "(.+?)"', s).group(1),
    re.search('VERSION_MINOR "(.+?)"', s).group(1),
    re.search('VERSION_PATCH "(.+?)"', s).group(1),
)

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

INSTALL_REQUIRES = [
    'click',
    'ixmp>=0.2.0',
    'pandas',
    'xlrd',
    'XlsxWriter',
]

EXTRAS_REQUIRE = {
    'tests': ['asyncssh', 'pytest>=4.0'],
    'docs': ['numpydoc', 'sphinx', 'sphinx_rtd_theme',
             'sphinxcontrib-bibtex'],
    'reporting': ['pyam-iamc'],
    'tutorial': ['jupyter', 'matplotlib', 'plotnine'],
}


def all_gams_files(path, strip=None):
    paths = []
    for root, dirnames, files in os.walk(path):
        for f in [_f for _f in files
                  if os.path.splitext(_f)[1] in ['.gms', '.opt', '.md']]:
            paths.append(os.path.join(root, f))
    if strip:
        n = len(strip) if strip.endswith(os.sep) else len(strip + os.sep)
        paths = [x[n:] for x in paths]
    return paths


setup(
    name='message_ix',
    version=VERSION,
    description='The MESSAGEix Integrated Assessment Model',
    author='IIASA Energy Program',
    author_email='message_ix@iiasa.ac.at',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='http://github.com/iiasa/message_ix',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    packages=find_packages(),
    package_dir={'message_ix': 'message_ix'},
    package_data={
        'message_ix': all_gams_files('message_ix/model', strip='message_ix')
    },
    entry_points={
        'console_scripts': [
            'message-ix=message_ix.cli:main'
        ],
    }
)
