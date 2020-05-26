#!/usr/bin/env python3

from .mc_header import data as mc_header

from .trigger import data as trigger
from .fitparameters import data as fitparameters
from .reconstruction import data as reconstruction

trigger_idx = {v: k for k, v in trigger.items()}
fitparameters_idx = {v: k for k, v in fitparameters.items()}
reconstruction_idx = {v: k for k, v in reconstruction.items()}
