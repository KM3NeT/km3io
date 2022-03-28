#!/usr/bin/env python3

from km3io._definitions.mc_header import data as mc_header

from km3io._definitions.daqdatatypes import data as daqdatatypes
from km3io._definitions.fitparameters import data as fitparameters
from km3io._definitions.reconstruction import data as reconstruction
from km3io._definitions.root import data as root
from km3io._definitions.trigger import data as trigger
from km3io._definitions.w2list_genhen import data as w2list_genhen
from km3io._definitions.w2list_gseagen import data as w2list_gseagen
from km3io._definitions.w2list_km3buu import data as w2list_km3buu
from km3io._definitions.trkmembers import data as trkmembers
from km3io._definitions.applications import data as applications
from km3io._definitions.pmt_status import data as pmt_status
from km3io._definitions.weightlist import data as weightlist
from km3io._definitions.module_status import data as module_status


class AttrDict(dict):
    """A dictionary which allows access to its key through attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


daqdatatypes = AttrDict(daqdatatypes)
root = AttrDict(root)
trigger = AttrDict(trigger)
fitparameters = AttrDict(fitparameters)
reconstruction = AttrDict(reconstruction)
w2list_genhen = AttrDict(w2list_genhen)
w2list_gseagen = AttrDict(w2list_gseagen)
w2list_km3buu = AttrDict(w2list_km3buu)
weightlist = AttrDict(weightlist)
module_status = AttrDict(module_status)

trigger_idx = {v: k for k, v in trigger.items()}
fitparameters_idx = {v: k for k, v in fitparameters.items()}
reconstruction_idx = {v: k for k, v in reconstruction.items()}
w2list_genhen_idx = {v: k for k, v in w2list_genhen.items()}
w2list_gseagen_idx = {v: k for k, v in w2list_gseagen.items()}
w2list_km3buu_idx = {v: k for k, v in w2list_km3buu.items()}
pmt_status_idx = {v: k for k, v in pmt_status.items()}
trkmembers_idx = {v: k for k, v in trkmembers.items()}
module_status_idx = {v: k for k, v in module_status.items()}
weightlist_idx = {v: k for k, v in weightlist.items()}
