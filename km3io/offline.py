from collections import namedtuple
import warnings
import uproot4 as uproot
import numpy as np
import awkward1 as ak

from .definitions import mc_header
from .tools import cached_property, to_num, unfold_indices


class OfflineReader:
    """reader for offline ROOT files"""

    event_path = "E/Evt"
    item_name = "OfflineEvent"
    skip_keys = ["t", "AAObject"]
    aliases = {
        "t_sec": "t.fSec",
        "t_ns": "t.fNanoSec",
    }
    special_branches = {
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
            # "status": "mc_trks.status",  # TODO: check this
            # "mother_id": "mc_trks.mother_id",  # TODO: check this
            "type": "mc_trks.type",
            "hit_ids": "mc_trks.hit_ids",
        },
    }
    special_aliases = {
        "tracks": "trks",
        "mc_tracks": "mc_trks",
    }

    def __init__(self, f, index_chain=None, step_size=2000, keys=None, aliases=None, event_ctor=None):
        """OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        f: str or uproot4.reading.ReadOnlyDirectory (from uproot4.open)
            Path to the file of interest or uproot4 filedescriptor.
        step_size: int, optional
            Number of events to read into the cache when iterating.
            Choosing higher numbers may improve the speed but also increases
            the memory overhead.
        index_chain: list, optional
            Keeps track of index chaining.
        keys: list or set, optional
            Branch keys.
        aliases: dict, optional
            Branch key aliases.
        event_ctor: class or namedtuple, optional
            Event constructor.

        """
        if isinstance(f, str):
            self._fobj = uproot.open(f)
            self._filepath = f
        elif isinstance(f, uproot.reading.ReadOnlyDirectory):
            self._fobj = f
            self._filepath = f._file.file_path
        else:
            raise TypeError("Unsupported file descriptor.")
        self._step_size = step_size
        self._uuid = self._fobj._file.uuid
        self._iterator_index = 0
        self._keys = keys
        self._event_ctor = event_ctor
        self._index_chain = [] if index_chain is None else index_chain

        if aliases is not None:
            self.aliases = aliases
        else:
            # Check for usr-awesomeness backward compatibility crap
            print("Found usr data")
            if "E/Evt/AAObject/usr" in self._fobj:
                if ak.count(f["E/Evt/AAObject/usr"].array()) > 0:
                    self.aliases.update(
                        {
                            "usr": "AAObject/usr",
                            "usr_names": "AAObject/usr_names",
                        }
                    )

        if self._keys is None:
            self._initialise_keys()

        if self._event_ctor is None:
            self._event_ctor = namedtuple(
                self.item_name,
                set(
                    list(self.keys())
                    + list(self.aliases)
                    + list(self.special_branches)
                    + list(self.special_aliases)
                ),
            )

    def _initialise_keys(self):
        skip_keys = set(self.skip_keys)
        toplevel_keys = set(k.split("/")[0] for k in self._fobj[self.event_path].keys())
        keys = (toplevel_keys - skip_keys).union(
            list(self.aliases.keys()) + list(self.special_aliases)
        )
        for key in list(self.special_branches) + list(self.special_aliases):
            keys.add("n_" + key)
        # self._grouped_branches = {k for k in toplevel_keys - skip_keys if isinstance(self._fobj[self.event_path][k].interpretation, uproot.AsGrouped)}
        self._keys = keys

    def keys(self):
        """Returns all accessible branch keys, without the skipped ones."""
        return self._keys

    @property
    def events(self):
        return iter(self)

    def _keyfor(self, key):
        """Return the correct key for a given alias/key"""
        return self.special_aliases.get(key, key)

    def __getattr__(self, attr):
        attr = self._keyfor(attr)
        # if attr in self.keys() or (attr.startswith("n_") and self._keyfor(attr.split("n_")[1]) in self._grouped_branches):
        if attr in self.keys():
            return self.__getitem__(attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def __getitem__(self, key):
        # indexing
        if isinstance(key, (slice, int, np.int32, np.int64)):
            if not isinstance(key, slice):
                key = int(key)
            return self.__class__(
                self._fobj,
                index_chain=self._index_chain + [key],
                step_size=self._step_size,
                aliases=self.aliases,
                keys=self.keys(),
                event_ctor=self._event_ctor
            )

        if isinstance(key, str) and key.startswith("n_"):  # group counts, for e.g. n_events, n_hits etc.
            key = self._keyfor(key.split("n_")[1])
            arr = self._fobj[self.event_path][key].array(uproot.AsDtype(">i4"))
            return unfold_indices(arr, self._index_chain)

        key = self._keyfor(key)
        branch = self._fobj[self.event_path]
        # These are special branches which are nested, like hits/trks/mc_trks
        # We are explicitly grabbing just a predefined set of subbranches
        # and also alias them to be backwards compatible (and attribute-accessible)
        if key in self.special_branches:
            out = branch[key].arrays(
                self.special_branches[key].keys(), aliases=self.special_branches[key]
            )
        else:
            out = branch[self.aliases.get(key, key)].array()

        return unfold_indices(out, self._index_chain)

    def __iter__(self):
        self._iterator_index = 0
        self._events = self._event_generator()
        return self

    def _event_generator(self):
        events = self._fobj[self.event_path]
        group_count_keys = set(k for k in self.keys() if k.startswith("n_"))
        keys = set(
            list(
                set(self.keys())
                - set(self.special_branches.keys())
                - set(self.special_aliases)
                - group_count_keys
            )
            + list(self.aliases.keys())
        )
        events_it = events.iterate(
            keys, aliases=self.aliases, step_size=self._step_size
        )
        specials = []
        special_keys = (
            self.special_branches.keys()
        )  # dict-key ordering is an implementation detail
        for key in special_keys:
            specials.append(
                events[key].iterate(
                    self.special_branches[key].keys(),
                    aliases=self.special_branches[key],
                    step_size=self._step_size,
                )
            )
        group_counts = {}
        for key in group_count_keys:
            group_counts[key] = iter(self[key])
        for event_set, *special_sets in zip(events_it, *specials):
            for _event, *special_items in zip(event_set, *special_sets):
                data = {}
                for k in keys:
                    data[k] = _event[k]
                for (k, i) in zip(special_keys, special_items):
                    data[k] = i
                for tokey, fromkey in self.special_aliases.items():
                    data[tokey] = data[fromkey]
                for key in group_counts:
                    data[key] = next(group_counts[key])
                yield self._event_ctor(**data)

    def __next__(self):
        return next(self._events)

    def __len__(self):
        if not self._index_chain:
            return self._fobj[self.event_path].num_entries
        elif isinstance(self._index_chain[-1], (int, np.int32, np.int64)):
            if len(self._index_chain) == 1:
                return 1
                # try:
                #     return len(self[:])
                # except IndexError:
                #     return 1
            return 1
        else:
            # ignore the usual index magic and access `id` directly
            return len(self._fobj[self.event_path]["id"].array(), self._index_chain)

    def __actual_len__(self):
        """The raw number of events without any indexing/slicing magic"""
        return len(self._fobj[self.event_path]["id"].array())


    def __repr__(self):
        length = len(self)
        actual_length = self.__actual_len__()
        return f"{self.__class__.__name__} ({length}{'/' + str(actual_length) if length < actual_length else ''} events)"

    @property
    def uuid(self):
        return self._uuid

    def close(self):
        self._fobj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

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
