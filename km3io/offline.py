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
BASKET_CACHE_SIZE = 110 * 1024**2
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

        self._usr_names = self._branch[self._usr_key + '_names'].array()[0] 
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
    skip_keys = ['mc_trks', 'trks', 't', 'AAObject']
    aliases = {"t_s": "t.fSec", "t_ns": "t.fNanoSec"}
    special_keys = {
        'hits': {
            'channel_id': 'hits.channel_id',
            'dom_id': 'hits.dom_id',
            'time': 'hits.t',
            'tot': 'hits.tot',
            'triggered': 'hits.trig'
        },
        'mc_hits': {
            'pmt_id': 'mc_hits.pmt_id',
            'time': 'mc_hits.t',
            'a': 'mc_hits.a',
        },
        'trks': {
            'dir_x': 'trks.dir.x',
            'dir_y': 'trks.dir.y',
            'dir_z': 'trks.dir.z',
            'rec_stages': 'trks.rec_stages',
            'fitinf': 'trks.fitinf'
        },
        'mc_trks': {
            'dir_x': 'mc_trks.dir.x',
            'dir_y': 'mc_trks.dir.y',
            'dir_z': 'mc_trks.dir.z',
        },

    }
    # TODO: this is fishy
    special_aliases = {'trks': 'tracks', 'hits': "hits", "mc_hits": "mc_hits", "mc_trks": "mc_tracks"}

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
        self._subbranches = None
        self._event_ctor = namedtuple("OfflineEvent", set(list(self.keys()) + list(self.aliases.keys()) + list(self.special_aliases[k] for k in self.special_keys)))

    def keys(self):
        if self._subbranches is None:
            subbranches = defaultdict(list)
            for key in self._fobj[self.event_path].keys():
                toplevel, *remaining = key.split("/")
                if remaining:
                    subbranches[toplevel].append("/".join(remaining))
                else:
                    subbranches[toplevel] = []
            for key in self.skip_keys:
                del subbranches[key]
            self._subbranches = subbranches
        return self._subbranches.keys()

    @property
    def events(self):
        return iter(self)

    def __getitem__(self, key):
        return self._fobj[self.event_path][key].array()

    def __iter__(self):
        self._iterator_index = 0
        self._events = self._event_generator()
        return self

    def _event_generator(self):
        events = self._fobj[self.event_path]
        keys = list(set(self.keys()) - set(self.special_keys.keys())) + list(self.aliases.keys())
        events_it = events.iterate(
            keys,
            aliases=self.aliases,
            step_size=self.step_size)
        specials = []
        special_keys = self.special_keys.keys()  # dict-key ordering is an implementation detail
        for key in special_keys:
            specials.append(
                events[key].iterate(
                    self.special_keys[key].keys(),
                    aliases=self.special_keys[key],
                    step_size=self.step_size
                )
            )
        for event_set, *special_sets in zip(events_it, *specials):
            for _event, *special_items in zip(event_set, *special_sets):
                yield self._event_ctor(**{k: _event[k] for k in keys},
                                       **{k: i for (k, i) in zip(special_keys, special_items)})

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
            return Header(self._fobj['Head'].tojson()['map<string,string>'])
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
