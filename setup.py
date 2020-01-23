#!/usr/bin/env python
# Filename: setup.py
"""
The km3io setup script.

"""
from setuptools import setup

with open('requirements.txt') as fobj:
    requirements = [l.strip() for l in fobj.readlines()]

try:
    with open("README.rst") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    long_description = "km3io, a library to read KM3NeT files without ROOT"

setup(
    name='km3io',
    url='http://git.km3net.de/km3py/km3io',
    description='KM3NeT I/O without ROOT',
    long_description=long_description,
    author='Zineb Aly, Tamas Gal, Johannes Schumann',
    author_email='zaly@km3net.de, tgal@km3net.de, johannes.schumann@fau.de',
    packages=['km3io'],
    include_package_data=True,
    platforms='any',
    setup_requires=['setuptools_scm'],
    use_scm_version={
        'write_to': 'km3io/version.txt',
        'tag_regex': r'^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$',
    },
    install_requires=requirements,
    python_requires='>=3.5',
    entry_points={
        'console_scripts': ['KPrintTree=km3io.utils.kprinttree:main']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
    ],
)

__author__ = 'Zineb Aly, Tamas Gal and Johannes Schumann'
