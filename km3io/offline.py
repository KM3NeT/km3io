from collections import namedtuple
import logging
import warnings
import uproot
import numpy as np
import awkward as ak

from .definitions import mc_header
from .tools import cached_property, to_num, unfold_indices
from .rootio import EventReader

log = logging.getLogger("offline")


class OfflineReader(EventReader):
    """reader for offline ROOT files"""

    event_path = "E/Evt"
    item_name = "OfflineEvent"
    skip_keys = ["t", "AAObject"]
    aliases = {
        "t_sec": "t/t.fSec",
        "t_ns": "t/t.fNanoSec",
        "usr": "AAObject/usr",
        "usr_names": "AAObject/usr_names",
    }
    nested_branches = {
        "hits": {
            "id": "hits.id",
            "channel_id": "hits.channel_id",
            "dom_id": "hits.dom_id",
            "t": "hits.t",
            "tot": "hits.tot",
            "trig": "hits.trig",  # non-zero if the hit is a triggered hit
        },
        "mc_hits": {
            "id": "mc_hits.id",
            "pmt_id": "mc_hits.pmt_id",
            "t": "mc_hits.t",  # hit time (MC truth)
            "a": "mc_hits.a",  # hit amplitude (in p.e.)
            "origin": "mc_hits.origin",  # track id of the track that created this hit
            "pure_t": "mc_hits.pure_t",  # photon time before pmt simultion
            "pure_a": "mc_hits.pure_a",  # amplitude before pmt simution,
            "type": "mc_hits.type",  # particle type or parametrisation used for hit
        },
        "trks": {
            "id": "trks.id",
            "pos_x": "trks.pos.x",
            "pos_y": "trks.pos.y",
            "pos_z": "trks.pos.z",
            "dir_x": "trks.dir.x",
            "dir_y": "trks.dir.y",
            "dir_z": "trks.dir.z",
            "t": "trks.t",
            "E": "trks.E",
            "len": "trks.len",
            "lik": "trks.lik",
            "rec_type": "trks.rec_type",
            "rec_stages": "trks.rec_stages",
            "fitinf": "trks.fitinf",
        },
        "mc_trks": {
            "id": "mc_trks.id",
            "pos_x": "mc_trks.pos.x",
            "pos_y": "mc_trks.pos.y",
            "pos_z": "mc_trks.pos.z",
            "dir_x": "mc_trks.dir.x",
            "dir_y": "mc_trks.dir.y",
            "dir_z": "mc_trks.dir.z",
            "E": "mc_trks.E",
            "t": "mc_trks.t",
            "len": "mc_trks.len",
            # "status": "mc_trks.status",  # TODO: check this
            # "mother_id": "mc_trks.mother_id",  # TODO: check this
            "pdgid": "mc_trks.type",
            "hit_ids": "mc_trks.hit_ids",
            "usr": "mc_trks.usr",  # TODO: trouble with uproot4
            "usr_names": "mc_trks.usr_names",  # TODO: trouble with uproot4
        },
    }
    nested_aliases = {
        "tracks": "trks",
        "mc_tracks": "mc_trks",
    }

    @cached_property
    def header(self):
        """The file header"""
        if "Head" in self._fobj:
            return Header(self._fobj["Head"].tojson()["map<string,string>"])
        else:
            warnings.warn("Your file header has an unsupported format")


class Header:
    """The header"""

    def __init__(self, header):
        self._data = {}

        for attribute, fields in header.items():
            values = fields.split()
            fields = mc_header.get(attribute, [])

            n_values = len(values)
            n_fields = len(fields)

            if n_values == 1 and n_fields == 0:
                self._data[attribute] = to_num(values[0])
                continue

            n_max = max(n_values, n_fields)
            values += [None] * (n_max - n_values)
            fields += ["field_{}".format(i) for i in range(n_fields, n_max)]

            Constructor = namedtuple(attribute, fields)

            if not values:
                continue

            self._data[attribute] = Constructor(
                **{f: to_num(v) for (f, v) in zip(fields, values)}
            )

        for attribute, value in self._data.items():
            setattr(self, attribute, value)

    def __str__(self):
        lines = ["MC Header:"]
        keys = set(mc_header.keys())
        for key, value in self._data.items():
            if key in keys:
                lines.append("  {}".format(value))
            else:
                lines.append("  {}: {}".format(key, value))
        return "\n".join(lines)
