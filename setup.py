#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


setup(
    name = 'oxttools',
    version =0.6,
    description = 'Utility to make libreoffice language extensions',
    maintainer = 'SIL International',
    url = 'http://github.com/silnrsi/oxttools',
    packages = ["oxttools",
        ],
    package_dir = {'':'lib'},
    install_requires=[
        'lxml',
    ],
    package_data={
        'oxttools': [
             'data/*.xml',
    ]},
    scripts = ['scripts/makeoxt'],
    license = 'MIT',
    platforms = ['Linux','Win32','Mac OS X'],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Linguistic",
        ],
)

