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
    skip_keys = ["t", "AAObject", "mc_event_time", "header_uuid[16]"]
    aliases = {
        "mc_event_time_sec": "mc_event_time/mc_event_time.fSec",
        "mc_event_time_ns": "mc_event_time/mc_event_time.fNanoSec",
        "t_sec": "t/t.fSec",
        "t_ns": "t/t.fNanoSec",
        "usr": "AAObject/usr",
        "usr_names": "AAObject/usr_names",
        "header_uuid": "header_uuid[16]",
    }
    nested_branches = {
        "hits": {
            "id": "hits.id",
            "channel_id": "hits.channel_id",
            "dom_id": "hits.dom_id",
            "t": "hits.t",
            "tdc": "hits.tdc",
            "pos_x": "hits.pos.x",
            "pos_y": "hits.pos.y",
            "pos_z": "hits.pos.z",
            "dir_x": "hits.dir.x",
            "dir_y": "hits.dir.y",
            "dir_z": "hits.dir.z",
            "tot": "hits.tot",
            "a": "hits.a",  # hit amplitude (in p.e.)
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
            "status": "mc_trks.status",
            "mother_id": "mc_trks.mother_id",
            "counter": "mc_trks.counter",
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
                entry = to_num(values[0])
                self._data[attribute] = entry
                if attribute.isidentifier():
                    setattr(self, attribute, entry)
                continue

            n_max = max(n_values, n_fields)
            values += [None] * (n_max - n_values)
            fields += ["field_{}".format(i) for i in range(n_fields, n_max)]

            if not values:
                continue

            cls_name = attribute if attribute.isidentifier() else "HeaderEntry"
            entry = namedtuple(cls_name, fields)(*[to_num(v) for v in values])

            self._data[attribute] = entry

            if attribute.isidentifier():
                setattr(self, attribute, entry)
            else:
                log.warning(
                    f"Invalid attribute name for header entry '{attribute}'"
                    ", access only as dictionary key."
                )

    def __dir__(self):
        return list(self.keys())

    def __str__(self):
        lines = ["MC Header:"]
        keys = set(mc_header.keys())
        for key, value in self._data.items():
            if key in keys:
                lines.append("  {}".format(value))
            else:
                lines.append("  {}: {}".format(key, value))
        return "\n".join(lines)

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()
