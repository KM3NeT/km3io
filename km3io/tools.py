#!/usr/bin/env python3
from collections import namedtuple
import numpy as np
import awkward1 as ak
import uproot
# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2
BASKET_CACHE = uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)


class cached_property:
    """A simple cache decorator for properties."""
    def __init__(self, function):
        self.function = function

    def __get__(self, obj, cls):
        if obj is None:
            return self
        prop = obj.__dict__[self.function.__name__] = self.function(obj)
        return prop


def _unfold_indices(obj, indices):
    """Unfolds an index chain and returns the corresponding item"""
    original_obj = obj
    for depth, idx in enumerate(indices):
        try:
            obj = obj[idx]
        except IndexError:
            print(
                "IndexError while accessing an item from '{}' at depth {} ({}) "
                "using the index chain {}".format(repr(original_obj), depth,
                                                  idx, indices))
            raise
    return obj


class BranchMapper:
    def __init__(
            self,
            name,
            key,
            extra=None,
            exclude=None,
            update=None,
            attrparser=None,
            flat=True,
            interpretations=None,
            toawkward=None):
        """
        Mapper helper for keys in a ROOT branch.

        Parameters
        ----------
        name: str
            The name of the mapper helper which is displayed to the user
        key: str
            The key of the branch in the ROOT tree.
        exclude: ``None``, ``list(str)``
            Keys to exclude from parsing.
        update: ``None``, ``dict(str: str)``
            An update map for keys which are to be presented with a different
            key to the user e.g. ``{"n_hits": "hits"}`` will rename the ``hits``
            key to ``n_hits``.
        extra: ``None``, ``dict(str: str)``
            An extra mapper for hidden object, primarily nested ones like
            ``t.fSec``, which can be revealed and mapped to e.g. ``t_sec``
            via ``{"t_sec", "t.fSec"}``.
        attrparser: ``None``, ``function(str) -> str``
            The function to be used to create attribute names. This is only
            needed if unsupported characters are present, like ``.``, which
            would prevent setting valid Python attribute names.
        toawkward: ``None``, ``list(str)``
            List of keys to convert to awkward arrays (recommended for
            doubly ragged arrays)
        """
        self.name = name
        self.key = key

        self.extra = {} if extra is None else extra
        self.exclude = [] if exclude is None else exclude
        self.update = {} if update is None else update
        self.attrparser = (lambda x: x) if attrparser is None else attrparser
        self.flat = flat
        self.interpretations = {} if interpretations is None else interpretations
        self.toawkward = [] if toawkward is None else toawkward


class Branch:
    """Branch accessor class"""
    def __init__(self,
                 tree,
                 mapper,
                 index_chain=None,
                 subbranchmaps=None,
                 keymap=None):
        self._tree = tree
        self._mapper = mapper
        self._index_chain = [] if index_chain is None else index_chain
        self._keymap = None
        self._branch = tree[mapper.key]
        self._subbranches = []
        self._subbranchmaps = subbranchmaps

        self._iterator_index = 0

        if keymap is None:
            self._initialise_keys()  #
        else:
            self._keymap = keymap

        if subbranchmaps is not None:
            for mapper in subbranchmaps:
                subbranch = self.__class__(self._tree,
                                           mapper=mapper,
                                           index_chain=self._index_chain)
                self._subbranches.append(subbranch)
        for subbranch in self._subbranches:
            setattr(self, subbranch._mapper.name, subbranch)

    def _initialise_keys(self):
        """Create the keymap and instance attributes for branch keys"""
        # TODO: this could be a cached property
        keys = set(k.decode('utf-8')
                   for k in self._branch.keys()) - set(self._mapper.exclude)
        self._keymap = {
            **{self._mapper.attrparser(k): k
               for k in keys},
            **self._mapper.extra
        }
        self._keymap.update(self._mapper.update)
        for k in self._mapper.update.values():
            del self._keymap[k]

        for key in self._keymap.keys():
            setattr(self, key, None)

    def keys(self):
        return self._keymap.keys()

    def __getattribute__(self, attr):
        if attr.startswith("_"):  # let all private and magic methods pass
            return object.__getattribute__(self, attr)

        if attr in self._keymap.keys():  # intercept branch key lookups
            return self.__getkey__(attr)

        return object.__getattribute__(self, attr)

    def __getkey__(self, key):
        out = self._branch[self._keymap[key]].lazyarray(
            interpretation=self._mapper.interpretations.get(key),
            basketcache=BASKET_CACHE)
        if self._index_chain is not None and key in self._mapper.toawkward:
            out = ak.from_iter(out)
        return _unfold_indices(out, self._index_chain)

    def __getitem__(self, item):
        """Slicing magic"""
        if isinstance(item, str):
            return self.__getkey__(item)

        return self.__class__(self._tree,
                              self._mapper,
                              index_chain=self._index_chain + [item],
                              keymap=self._keymap,
                              subbranchmaps=self._subbranchmaps)

    def __len__(self):
        if not self._index_chain:
            return len(self._branch)
        elif isinstance(self._index_chain[-1], int):
            return 1
        else:
            return len(
                _unfold_indices(
                    self._branch[self._keymap['id']].lazyarray(
                        basketcache=BASKET_CACHE), self._index_chain))

    def __iter__(self):
        self._iterator_index = 0
        return self

    def __next__(self):
        idx = self._iterator_index
        self._iterator_index += 1
        if idx >= len(self):
            raise StopIteration
        return self[idx]

    def __str__(self):
        length = len(self)
        return "{} ({}) with {} element{}".format(self.__class__.__name__,
                                               self._mapper.name, length,
                                               's' if length > 1 else '')

    def __repr__(self):
        length = len(self)
        return "<{}[{}]: {} element{}>".format(self.__class__.__name__,
                                               self._mapper.name, length,
                                               's' if length > 1 else '')


def _to_num(value):
    """Convert a value to a numerical one if possible"""
    for converter in (int, float):
        try:
            return converter(value)
        except (ValueError, TypeError):
            pass
    return value
