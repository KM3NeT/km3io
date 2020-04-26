#!/usr/bin/env python
# coding=utf-8
# Filename: gseagen.py
# Author: Johannes Schumann <jschumann@km3net.de>

import uproot
import numpy as np
import warnings
from .rootio import Branch, BranchMapper
from .tools import cached_property
MAIN_TREE_NAME = "Events"


class GSGReader:
    """reader for gSeaGen ROOT files"""
    def __init__(self, file_path=None, fobj=None):
        """ GSGReader class is a gSeaGen ROOT file wrapper

        Parameters
        ----------
        file_path : file path or file-like object
            The file handler. It can be a str or any python path-like object
            that points to the file.
        """
        self._fobj = uproot.open(file_path)

    @cached_property
    def header(self):
        header_key = 'Header'
        if header_key in self._fobj:
            header = {}
            for k, v in self._fobj[header_key].items():
                v = v.array()[0]
                if isinstance(v, bytes):
                    try:
                        v = v.decode('utf-8')
                    except UnicodeDecodeError:
                        pass
                header[k.decode("utf-8")] = v
            return header
        else:
            warnings.warn("Your file header has an unsupported format")

    @cached_property
    def events(self):
        return Branch(self._fobj, BranchMapper(name="Events", key="Events"))
