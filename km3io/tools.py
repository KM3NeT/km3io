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
                subbranch = Branch(self._tree,
                                   mapper=mapper,
                                   index=self._index)
                self._subbranches.append(subbranch)
        for subbranch in self._subbranches:
            setattr(self, subbranch._mapper.name, subbranch)

    def _initialise_keys(self):
        """Create the keymap and instance attributes for branch keys"""
        # TODO: this could be a cached property
        keys = set(k.decode('utf-8') for k in self._branch.keys()) - set(
            self._mapper.exclude)
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

    @cached_property
    def usr(self):
        return Usr(self._mapper, self._branch, index=self._index)

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

class Usr:
    """Helper class to access AAObject `usr` stuff"""
    def __init__(self, mapper, branch, index=None):
        self._mapper = mapper
        self._name = mapper.name
        self._index = index
        self._branch = branch
        self._usr_names = []
        self._usr_idx_lookup = {}

        self._usr_key = 'usr' if mapper.flat else mapper.key + '.usr'

        self._initialise()

    def _initialise(self):
        try:
            self._branch[self._usr_key]
            # This will raise a KeyError in old aanet files
            # which has a different strucuter and key (usr_data)
            # We do not support those (yet)
        except (KeyError, IndexError):
            print("The `usr` fields could not be parsed for the '{}' branch.".
                  format(self._name))
            return

        if self._mapper.flat:
            self._initialise_flat()

    def _initialise_flat(self):
        # Here, we assume that every event has the same names in the same order
        # to massively increase the performance. This needs triple check if
        # it's always the case.
        self._usr_names = [
            n.decode("utf-8") for n in self._branch[self._usr_key + '_names'].lazyarray(
                basketcache=BASKET_CACHE)[0]
        ]
        self._usr_idx_lookup = {
            name: index
            for index, name in enumerate(self._usr_names)
        }

        data = self._branch[self._usr_key].lazyarray(basketcache=BASKET_CACHE)

        if self._index is not None:
            data = data[self._index]

        self._usr_data = data

        for name in self._usr_names:
            setattr(self, name, self[name])

    # def _initialise_nested(self):
    #     self._usr_names = [
    #         n.decode("utf-8") for n in self.branch['usr_names'].lazyarray(
    #             # TODO this will be fixed soon in uproot,
    #             # see https://github.com/scikit-hep/uproot/issues/465
    #             uproot.asgenobj(
    #                 uproot.SimpleArray(uproot.STLVector(uproot.STLString())),
    #                 self.branch['usr_names']._context, 6),
    #             basketcache=BASKET_CACHE)[0]
    #     ]

    def __getitem__(self, item):
        if self._mapper.flat:
            return self.__getitem_flat__(item)
        return self.__getitem_nested__(item)

    def __getitem_flat__(self, item):
        if self._index is not None:
            return self._usr_data[self._index][:, self._usr_idx_lookup[item]]
        else:
            return self._usr_data[:, self._usr_idx_lookup[item]]

    def __getitem_nested__(self, item):
        data = self._branch[self._usr_key + '_names'].lazyarray(
                # TODO this will be fixed soon in uproot,
                # see https://github.com/scikit-hep/uproot/issues/465
                uproot.asgenobj(
                    uproot.SimpleArray(uproot.STLVector(uproot.STLString())),
                    self._branch[self._usr_key + '_names']._context, 6),
                basketcache=BASKET_CACHE)
        if self._index is None:
            return data
        else:
            return data[self._index]

    def keys(self):
        return self._usr_names

    def __str__(self):
        entries = []
        for name in self.keys():
            entries.append("{}: {}".format(name, self[name]))
        return '\n'.join(entries)

    def __repr__(self):
        return "<{}[{}]>".format(self.__class__.__name__, self._name)


def _to_num(value):
    """Convert a value to a numerical one if possible"""
    for converter in (int, float):
        try:
            return converter(value)
        except (ValueError, TypeError):
            pass
    return value
