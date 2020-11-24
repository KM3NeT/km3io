import binascii
from collections import namedtuple, defaultdict
import uproot4 as uproot
import warnings
import numba as nb
import awkward1 as ak1

from .definitions import mc_header, fitparameters, reconstruction
from .tools import cached_property, to_num, unfold_indices
from .rootio import Branch, BranchMapper

MAIN_TREE_NAME = "E"
EXCLUDE_KEYS = ["AAObject", "t", "fBits", "fUniqueID"]

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024 ** 2
BASKET_CACHE = uproot.cache.LRUArrayCache(BASKET_CACHE_SIZE)


class Usr:
    """Helper class to access AAObject `usr` stuff (only for events.usr)"""

    def __init__(self, mapper, branch, index_chain=None):
        self._mapper = mapper
        self._name = mapper.name
        self._index_chain = [] if index_chain is None else index_chain
        self._branch = branch
        self._usr_names = []
        self._usr_idx_lookup = {}

        self._usr_key = "usr" if mapper.flat else mapper.key + ".usr"

        self._initialise()

    def _initialise(self):
        try:
            self._branch[self._usr_key]
            # This will raise a KeyError in old aanet files
            # which has a different strucuter and key (usr_data)
            # We do not support those (yet)
        except (KeyError, IndexError):
            print(
                "The `usr` fields could not be parsed for the '{}' branch.".format(
                    self._name
                )
            )
            return

        self._usr_names = self._branch[self._usr_key + "_names"].array()[0]
        self._usr_idx_lookup = {
            name: index for index, name in enumerate(self._usr_names)
        }

        data = self._branch[self._usr_key].array()

        if self._index_chain:
            data = unfold_indices(data, self._index_chain)

        self._usr_data = data

        for name in self._usr_names:
            setattr(self, name, self[name])

    def __getitem__(self, item):
        if self._index_chain:
            return unfold_indices(self._usr_data, self._index_chain)[
                :, self._usr_idx_lookup[item]
            ]
        else:
            return self._usr_data[:, self._usr_idx_lookup[item]]

    def keys(self):
        return self._usr_names

    def __str__(self):
        entries = []
        for name in self.keys():
            entries.append("{}: {}".format(name, self[name]))
        return "\n".join(entries)

    def __repr__(self):
        return "<{}[{}]>".format(self.__class__.__name__, self._name)


class OfflineReader:
    """reader for offline ROOT files"""

    event_path = "E/Evt"
    item_name = "OfflineEvent"
    skip_keys = ["t", "AAObject"]
    aliases = {"t_s": "t.fSec", "t_ns": "t.fNanoSec"}
    special_branches = {
        "hits": {
            "channel_id": "hits.channel_id",
            "dom_id": "hits.dom_id",
            "time": "hits.t",
            "tot": "hits.tot",
            "triggered": "hits.trig",  # non-zero if the hit is a triggered hit
        },
        "mc_hits": {
            "pmt_id": "mc_hits.pmt_id",
            "time": "mc_hits.t",  # hit time (MC truth)
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

    def __init__(self, file_path, step_size=2000):
        """OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file.
        step_size: int, optional
            Number of events to read into the cache when iterating.
            Choosing higher numbers may improve the speed but also increases
            the memory overhead.

        """
        self._fobj = uproot.open(file_path)
        self.step_size = step_size
        self._filename = file_path
        self._uuid = self._fobj._file.uuid
        self._iterator_index = 0
        self._keys = None

        self._initialise_keys()

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
        toplevel_keys = set(k.split("/")[0] for k in self._fobj[self.event_path].keys())
        keys = (toplevel_keys - set(self.skip_keys)).union(
            list(self.aliases.keys()) + list(self.special_aliases)
        )
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
        if attr in self.keys():
            return self.__getitem__(attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def __getitem__(self, key):
        key = self._keyfor(key)
        branch = self._fobj[self.event_path]
        # These are special branches which are nested, like hits/trks/mc_trks
        # We are explicitly grabbing just a predefined set of subbranches
        # and also alias them to be backwards compatible (and attribute-accessible)
        if key in self.special_branches:
            return branch[key].arrays(
                self.special_branches[key].keys(), aliases=self.special_branches[key]
            )
        return branch[self.aliases.get(key, key)].array()

    def __iter__(self):
        self._iterator_index = 0
        self._events = self._event_generator()
        return self

    def _event_generator(self):
        events = self._fobj[self.event_path]
        keys = list(
            set(self.keys())
            - set(self.special_branches.keys())
            - set(self.special_aliases)
        ) + list(self.aliases.keys())
        events_it = events.iterate(keys, aliases=self.aliases, step_size=self.step_size)
        specials = []
        special_keys = (
            self.special_branches.keys()
        )  # dict-key ordering is an implementation detail
        for key in special_keys:
            specials.append(
                events[key].iterate(
                    self.special_branches[key].keys(),
                    aliases=self.special_branches[key],
                    step_size=self.step_size,
                )
            )
        for event_set, *special_sets in zip(events_it, *specials):
            for _event, *special_items in zip(event_set, *special_sets):
                data = {
                    **{k: _event[k] for k in keys},
                    **{k: i for (k, i) in zip(special_keys, special_items)},
                }
                for tokey, fromkey in self.special_aliases.items():
                    data[tokey] = data[fromkey]
                yield self._event_ctor(**data)

    def __next__(self):
        return next(self._events)

    def __len__(self):
        return self._fobj[self.event_path].num_entries

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
