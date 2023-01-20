from collections import namedtuple
import logging
import warnings
import uproot
import numpy as np
import awkward as ak

from .definitions import mc_header
from ._definitions import dst
from .tools import cached_property, to_num, unfold_indices
from .rootio import EventReader
from .offline import OfflineReader

log = logging.getLogger("dst")


class DSTReader(EventReader):
    """reader for DST ROOT files"""

    event_path = "T"
    item_name = "DSTEvent"
    skip_keys = []
    aliases = {"id": "sum_hits/tmin"}
    nested_branches = {}#dst.parameters
    nested_aliases = {}

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
