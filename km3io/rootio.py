#!/usr/bin/env python3
from collections import namedtuple
import numpy as np
import awkward as ak
import uproot

from .tools import unfold_indices

import logging

log = logging.getLogger("km3io.rootio")


class EventReader:
    """reader for offline ROOT files"""

    event_path = None
    item_name = "Event"
    skip_keys = []
    aliases = {}
    special_branches = {}
    special_aliases = {}

    def __init__(
        self,
        f,
        index_chain=None,
        step_size=2000,
        keys=None,
        aliases=None,
        event_ctor=None,
    ):
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

        # if aliases is not None:
        #     self.aliases = aliases
        # else:
        #     # Check for usr-awesomeness backward compatibility crap
        #     if "E/Evt/AAObject/usr" in self._fobj:
        #         print("Found usr data")
        #         if ak.count(f["E/Evt/AAObject/usr"].array()) > 0:
        #             self.aliases.update(
        #                 {
        #                     "usr": "AAObject/usr",
        #                     "usr_names": "AAObject/usr_names",
        #                 }
        #             )

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
        # TODO: deprecate this, since `self` is already the container type
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
        # TODO: maybe just propagate everything to awkward and let it deal
        # with the type?
        if isinstance(
            key, (slice, int, np.int32, np.int64, list, np.ndarray, ak.Array)
        ):
            if isinstance(key, (int, np.int32, np.int64)):
                key = int(key)
            return self.__class__(
                self._fobj,
                index_chain=self._index_chain + [key],
                step_size=self._step_size,
                aliases=self.aliases,
                keys=self.keys(),
                event_ctor=self._event_ctor,
            )
        # group counts, for e.g. n_events, n_hits etc.
        if isinstance(key, str) and key.startswith("n_"):
            key = self._keyfor(key.split("n_")[1])
            arr = self._fobj[self.event_path][key].array(uproot.AsDtype(">i4"))
            return unfold_indices(arr, self._index_chain)

        key = self._keyfor(key)
        branch = self._fobj[self.event_path]
        # These are special branches which are nested, like hits/trks/mc_trks
        # We are explicitly grabbing just a predefined set of subbranches
        # and also alias them to be backwards compatible (and attribute-accessible)
        if key in self.special_branches:
            fields = []
            # some fields are not always available, like `usr_names`
            for to_field, from_field in self.special_branches[key].items():
                if from_field in branch[key].keys():
                    fields.append(to_field)
            log.debug(fields)
            # out = branch[key].arrays(fields, aliases=self.special_branches[key])
            return Branch(branch[key], fields, self.special_branches[key], self._index_chain)
        else:
            return unfold_indices(branch[self.aliases.get(key, key)].array(), self._index_chain)

    def __iter__(self):
        self._events = self._event_generator()
        return self

    def _event_generator(self):
        events = self._fobj[self.event_path]
        group_count_keys = set(
            k for k in self.keys() if k.startswith("n_")
        )  # special keys to make it easy to count subbranch lengths
        log.debug("group_count_keys: %s", group_count_keys)
        keys = set(
            list(
                set(self.keys())
                - set(self.special_branches.keys())
                - set(self.special_aliases)
                - group_count_keys
            )
            + list(self.aliases.keys())
        )  # all top-level keys for regular branches
        log.debug("keys: %s", keys)
        log.debug("aliases: %s", self.aliases)
        events_it = events.iterate(
            keys, aliases=self.aliases, step_size=self._step_size
        )
        specials = []
        special_keys = (
            self.special_branches.keys()
        )  # dict-key ordering is an implementation detail
        log.debug("special_keys: %s", special_keys)
        for key in special_keys:
            # print(f"adding {key} with keys {self.special_branches[key].keys()} and aliases {self.special_branches[key]}")

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

        log.debug("group_counts: %s", group_counts)
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
            return len(
                unfold_indices(
                    self._fobj[self.event_path]["id"].array(), self._index_chain
                )
            )

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


class Branch:
    """Helper class for nested branches likes tracks/hits"""
    def __init__(self, branch, fields, aliases, index_chain):
        self._branch = branch
        self.fields = fields
        self._aliases = aliases
        self._index_chain = index_chain

    def __getattr__(self, attr):
        if attr not in self._aliases:
            raise AttributeError(f"No field named {attr}. Available fields: {self.fields}")
        return unfold_indices(self._branch[self._aliases[attr]].array(), self._index_chain)

    def __getitem__(self, key):
        return self.__class__(self._branch, self.fields, self._aliases, self._index_chain + [key])

    def __len__(self):
        if not self._index_chain:
            return self._branch.num_entries
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
            return len(self.id)

    def __actual_len__(self):
        """The raw number of events without any indexing/slicing magic"""
        return len(self._branch[self._aliases["id"]].array())

    def __repr__(self):
        length = len(self)
        actual_length = self.__actual_len__()
        return f"{self.__class__.__name__} ({length}{'/' + str(actual_length) if length < actual_length else ''} {self._branch.name})"

    @property
    def ndim(self):
        if not self._index_chain:
            return 2
        elif any(isinstance(i, (int, np.int32, np.int64)) for i in self._index_chain):
            return 1
        return 2
