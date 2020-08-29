#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016-2020 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

import trellowarrior as project

import os
from setuptools import find_packages
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = project.NAME,
    version = project.VERSION,
    author = project.AUTHOR_NAME,
    author_email = project.AUTHOR_EMAIL,
    description = project.DESCRIPTION,
    license = project.LICENSE,
    keywords = project.KEYWORDS,
    url = project.URL,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=read('requirements.txt'),
    entry_points={
        'console_scripts': [
            'trellowarrior = trellowarrior.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/ogarcia/trellowarrior/issues',
        'Source': 'https://github.com/ogarcia/trellowarrior',
    },
)
