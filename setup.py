#!/usr/bin/env python
# Filename: setup.py
"""
The km3io setup script.

"""
import os
from setuptools import setup
import sys


def read_requirements(kind):
    """Return a list of stripped lines from a file"""
    with open(os.path.join("requirements", kind + ".txt")) as fobj:
        return [l.strip() for l in fobj.readlines()]


try:
    with open("README.rst") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    long_description = "km3io, a library to read KM3NeT files without ROOT"

setup(
    name="km3io",
    url="http://git.km3net.de/km3py/km3io",
    description="KM3NeT I/O without ROOT",
    long_description=long_description,
    author="Zineb Aly, Tamas Gal, Johannes Schumann",
    author_email="zaly@km3net.de, tgal@km3net.de, johannes.schumann@fau.de",
    packages=["km3io"],
    include_package_data=True,
    platforms="any",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    install_requires=read_requirements("install"),
    extras_require={kind: read_requirements(kind) for kind in ["dev"]},
    python_requires=">=3.6",
    entry_points={"console_scripts": ["KPrintTree=km3io.utils.kprinttree:main"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
    ],
)

__author__ = "Zineb Aly, Tamas Gal and Johannes Schumann"
