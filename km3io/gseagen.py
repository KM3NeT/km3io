#!/usr/bin/env python
# coding=utf-8
# Filename: gseagen.py
# Author: Johannes Schumann <jschumann@km3net.de>

import warnings
from .rootio import EventReader
from .tools import cached_property


class GSGReader(EventReader):
    """reader for gSeaGen ROOT files"""

    event_path = "Events"
    skip_keys = ["Header"]

    @cached_property
    def header(self):
        header_key = "Header"
        if header_key in self._fobj:
            header = {}
            for k, v in self._fobj[header_key].items():
                v = v.array()[0]
                if isinstance(v, bytes):
                    try:
                        v = v.decode("utf-8")
                    except UnicodeDecodeError:
                        pass
                header[k] = v
            return header
        else:
            warnings.warn("Your file header has an unsupported format")
