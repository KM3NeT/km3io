#!/usr/bin/env python3

from .mc_header import data as mc_header

from .trigger import data as trigger
from .fitparameters import data as fitparameters
from .reconstruction import data as reconstruction
from .w2list_genhen import data as w2list_genhen
from .w2list_gseagen import data as w2list_gseagen

trigger_idx = {v: k for k, v in trigger.items()}
fitparameters_idx = {v: k for k, v in fitparameters.items()}
reconstruction_idx = {v: k for k, v in reconstruction.items()}
w2list_genhen_idx = {v: k for k, v in w2list_genhen.items()}
w2list_gseagen_idx = {v: k for k, v in w2list_gseagen.items()}
