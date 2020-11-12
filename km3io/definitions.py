#!/usr/bin/env python3

from km3io._definitions.mc_header import data as mc_header

from km3io._definitions.trigger import data as trigger
from km3io._definitions.fitparameters import data as fitparameters
from km3io._definitions.reconstruction import data as reconstruction
from km3io._definitions.w2list_genhen import data as w2list_genhen
from km3io._definitions.w2list_gseagen import data as w2list_gseagen


class AttrDict(dict):
    """A dictionary which allows access to its key through attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


trigger = AttrDict(trigger)
fitparameters = AttrDict(fitparameters)
reconstruction = AttrDict(reconstruction)
w2list_genhen = AttrDict(w2list_genhen)
w2list_gseagen = AttrDict(w2list_gseagen)

trigger_idx = {v: k for k, v in trigger.items()}
fitparameters_idx = {v: k for k, v in fitparameters.items()}
reconstruction_idx = {v: k for k, v in reconstruction.items()}
w2list_genhen_idx = {v: k for k, v in w2list_genhen.items()}
w2list_gseagen_idx = {v: k for k, v in w2list_gseagen.items()}
