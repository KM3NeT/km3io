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
    skip_keys = []  # ignore these subbranches, even if they exist
    aliases = {}  # top level aliases -> {fromkey: tokey}
    nested_branches = {}
    nested_aliases = {}

    def __init__(
        self,
        f,
        index_chain=None,
        step_size=2000,
        keys=None,
        aliases=None,
        nested_branches=None,
        event_ctor=None,
    ):
        """EventReader base class

        Parameters
        ----------
        f : str or uproot4.reading.ReadOnlyDirectory (from uproot4.open)
            Path to the file of interest or uproot4 filedescriptor.
        step_size : int, optional
            Number of events to read into the cache when iterating.
            Choosing higher numbers may improve the speed but also increases
            the memory overhead.
        index_chain : list, optional
            Keeps track of index chaining.
        keys : list or set, optional
            Branch keys.
        aliases : dict, optional
            Branch key aliases.
        event_ctor : class or namedtuple, optional
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
        self._uuid = self._fobj.parent.uuid
        self._iterator_index = 0
        self._keys = keys
        self._event_ctor = event_ctor
        self._index_chain = [] if index_chain is None else index_chain

        if aliases is not None:
            self.aliases = aliases
        if nested_branches is not None:
            self.nested_branches = nested_branches

        if self._keys is None:
            self._initialise_keys()

        if self._event_ctor is None:
            self._event_ctor = namedtuple(
                self.item_name,
                set(
                    list(self.keys())
                    + list(self.aliases)
                    + list(self.nested_branches)
                    + list(self.nested_aliases)
                ),
            )

    def _initialise_keys(self):
        skip_keys = set(self.skip_keys)
        all_keys = set(self._fobj[self.event_path].keys())
        toplevel_keys = set(k.split("/")[0] for k in all_keys)
        valid_aliases = {}
        for fromkey, tokey in self.aliases.items():
            if tokey in all_keys:
                valid_aliases[fromkey] = tokey
        self.aliases = valid_aliases
        keys = (toplevel_keys - skip_keys).union(
            list(valid_aliases) + list(self.nested_aliases)
        )
        for key in list(self.nested_branches) + list(self.nested_aliases):
            keys.add("n_" + key)
        # self._grouped_branches = {k for k in toplevel_keys - skip_keys if isinstance(self._fobj[self.event_path][k].interpretation, uproot.AsGrouped)}
        valid_nested_branches = {}
        for nested_key, aliases in self.nested_branches.items():
            if nested_key in toplevel_keys:
                valid_nested_branches[nested_key] = {}
                subbranch_keys = self._fobj[self.event_path][nested_key].keys()
                for fromkey, tokey in aliases.items():
                    if tokey in subbranch_keys:
                        valid_nested_branches[nested_key][fromkey] = tokey
        self.nested_branches = valid_nested_branches
        self._keys = keys

    def __dir__(self):
        """Tab completion in IPython"""
        return list(self.keys()) + ["header"]

    def keys(self):
        """Returns all accessible branch keys, without the skipped ones."""
        return self._keys

    @property
    def events(self):
        # TODO: deprecate this, since `self` is already the container type
        return iter(self)

    def _keyfor(self, key):
        """Return the correct key for a given alias/key"""
        return self.nested_aliases.get(key, key)

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
                nested_branches=self.nested_branches,
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
        if key in self.nested_branches:
            fields = []
            # some fields are not always available, like `usr_names`
            for to_field, from_field in self.nested_branches[key].items():
                if from_field in branch[key].keys():
                    fields.append(to_field)
            log.debug(fields)
            return Branch(
                branch[key], fields, self.nested_branches[key], self._index_chain
            )
        else:
            return unfold_indices(
                branch[self.aliases.get(key, key)].array(), self._index_chain
            )

    def __iter__(self, chunkwise=False):
        self._events = self._event_generator(chunkwise=chunkwise)
        return self

    def _get_iterator_limits(self):
        """Determines start and stop, used for event iteration"""
        if len(self._index_chain) > 1:
            raise NotImplementedError(
                "iteration is currently not supported with nested slices"
            )
        if self._index_chain:
            s = self._index_chain[0]
            if not isinstance(s, slice):
                raise NotImplementedError("iteration is only supported with slices")
            if s.step is None or s.step == 1:
                start = s.start
                stop = s.stop
            else:
                raise NotImplementedError(
                    "iteration is only supported with single steps"
                )
        else:
            start = None
            stop = None
        return start, stop

    def _event_generator(self, chunkwise=False):
        start, stop = self._get_iterator_limits()

        if chunkwise:
            raise NotImplementedError("iterating over chunks is not implemented yet")

        events = self._fobj[self.event_path]
        group_count_keys = set(
            k for k in self.keys() if k.startswith("n_")
        )  # extra keys to make it easy to count subbranch lengths
        log.debug("group_count_keys: %s", group_count_keys)
        keys = set(
            list(
                set(self.keys())
                - set(self.nested_branches.keys())
                - set(self.nested_aliases)
                - group_count_keys
            )
            + list(self.aliases.keys())
        )  # all top-level keys for regular branches
        log.debug("keys: %s", keys)
        log.debug("aliases: %s", self.aliases)
        events_it = events.iterate(
            keys,
            aliases=self.aliases,
            step_size=self._step_size,
            entry_start=start,
            entry_stop=stop,
        )
        nested = []
        nested_keys = (
            self.nested_branches.keys()
        )  # dict-key ordering is an implementation detail
        log.debug("nested_keys: %s", nested_keys)
        for key in nested_keys:
            nested.append(
                events[key].iterate(
                    self.nested_branches[key].keys(),
                    aliases=self.nested_branches[key],
                    step_size=self._step_size,
                    entry_start=start,
                    entry_stop=stop,
                )
            )
        group_counts = {}
        for key in group_count_keys:
            group_counts[key] = iter(self[key])

        log.debug("group_counts: %s", group_counts)
        for event_set, *nested_sets in zip(events_it, *nested):
            for _event, *nested_items in zip(event_set, *nested_sets):
                data = {}
                for k in keys:
                    data[k] = _event[k]
                for k, i in zip(nested_keys, nested_items):
                    data[k] = i
                for tokey, fromkey in self.nested_aliases.items():
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
                # TODO: not sure why this is needed at all, it's too late...
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
        return (
            f"<{self.__class__.__name__} "
            f"[{length}{'/' + str(actual_length) if length < actual_length else ''}]"
            f" path='{self.event_path}'>"
        )

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

    def __dir__(self):
        """Tab completion in IPython"""
        return list(self.fields)

    def __getattr__(self, attr):
        if attr not in self._aliases:
            raise AttributeError(
                f"No field named {attr}. Available fields: {self.fields}"
            )
        key = self._aliases[attr]

        if self._index_chain:
            idx0 = self._index_chain[0]
            if isinstance(idx0, (int, np.int32, np.int64)):
                # optimise single-element and slice lookups
                start = idx0
                stop = idx0 + 1
                arr = ak.flatten(
                    self._branch[key].array(entry_start=start, entry_stop=stop)
                )
                return unfold_indices(arr, self._index_chain[1:])
            if isinstance(idx0, slice):
                if idx0.step is None or idx0.step == 1:
                    start = idx0.start
                    stop = idx0.stop
                    arr = self._branch[key].array(entry_start=start, entry_stop=stop)
                    return unfold_indices(arr, self._index_chain[1:])

        return unfold_indices(self._branch[key].array(), self._index_chain)

    def __iter__(self):
        raise NotImplementedError(
            "iterating over a nested branch is not supported nor recommended. "
            "If you really feel you need to do it, open an issue in "
            "https://git.km3net.de/km3py/km3io"
        )

    def __getitem__(self, key):
        return self.__class__(
            self._branch, self.fields, self._aliases, self._index_chain + [key]
        )

    def __len__(self):
        if not self._index_chain:
            return self._branch.num_entries
        elif isinstance(self._index_chain[-1], (int, np.int32, np.int64)):
            # we stick to the convention and return the 1 for a single subbranch
            # if len(self._index_chain) == 1:
            #     # single "event" is selected
            #     # return len(self.id)
            #     return 1
            return 1
        else:
            # ignore the usual index magic and access `id` directly
            return len(self.id)

    def arrays(self, *args, **kwargs):
        """High-level interface to uproots arrays call on branches"""
        return self._branch.arrays(*args, **kwargs, aliases=self._aliases)

    def __actual_len__(self):
        """The raw number of events without any indexing/slicing magic"""
        return len(self._branch[self._aliases["id"]].array())

    def __repr__(self):
        length = len(self)
        actual_length = self.__actual_len__()
        return (
            f"<{self.__class__.__name__} "
            f"[{length}{'/' + str(actual_length) if length < actual_length else ''}]"
            f" path='{self._branch.name}'>"
        )

    @property
    def ndim(self):
        if not self._index_chain:
            return 2
        elif any(isinstance(i, (int, np.int32, np.int64)) for i in self._index_chain):
            return 1
        return 2
