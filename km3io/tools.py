#!/usr/bin/env python3
from collections import namedtuple
import numpy as np
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
    for depth, idx in enumerate(indices):
        try:
            obj = obj[idx]
        except IndexError:
            print("IndexError while accessing item '{}' at depth {} ({}) of "
                  "the index chain {}".format(repr(obj), depth, idx, indices))
            raise
    return obj


BranchMapper = namedtuple(
    "BranchMapper",
    ['name', 'key', 'extra', 'exclude', 'update', 'attrparser', 'flat'])


class Branch:
    """Branch accessor class"""
    def __init__(self,
                 tree,
                 mapper,
                 index=None,
                 subbranchmaps=None,
                 keymap=None):
        self._tree = tree
        self._mapper = mapper
        self._index = index
        self._keymap = None
        self._branch = tree[mapper.key]
        self._subbranches = []
        self._subbranchmaps = subbranchmaps

        if keymap is None:
            self._initialise_keys()  #
        else:
            self._keymap = keymap

        if subbranchmaps is not None:
            for mapper in subbranchmaps:
                subbranch = self.__class__(self._tree,
                                   mapper=mapper,
                                   index=self._index)
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
            basketcache=BASKET_CACHE)
        if self._index is not None:
            out = out[self._index]
        return out

    def __getitem__(self, item):
        """Slicing magic"""
        if isinstance(item, (int, slice)):
            return self.__class__(self._tree,
                                  self._mapper,
                                  index=item,
                                  keymap=self._keymap,
                                  subbranchmaps=self._subbranchmaps)

        if isinstance(item, tuple):
            return self[item[0]][item[1]]

        if isinstance(item, str):
            return self.__getkey__(item)

        return self.__class__(self._tree,
                              self._mapper,
                              index=np.array(item),
                              keymap=self._keymap,
                              subbranchmaps=self._subbranchmaps)

    def __len__(self):
        if self._index is None:
            return len(self._branch)
        elif isinstance(self._index, int):
            return 1
        else:
            return len(self._branch[self._keymap['id']].lazyarray(
                basketcache=BASKET_CACHE)[self._index])

    def __str__(self):
        return "Number of elements: {}".format(len(self._branch))

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
