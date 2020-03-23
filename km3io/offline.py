from collections import namedtuple
import uproot
import numpy as np
import warnings
from .definitions import mc_header

MAIN_TREE_NAME = "E"
# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2
BASKET_CACHE = uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)
EXCLUDE_KEYS = set(["AAObject", "t", "fBits", "fUniqueID"])

BranchMapper = namedtuple(
    "BranchMapper",
    ['name', 'key', 'extra', 'exclude', 'update', 'attrparser'])


def _nested_mapper(key):
    """Maps a key in the ROOT file to another key (e.g. trks.pos.x -> pos_x)"""
    return '_'.join(key.split('.')[1:])


EVENTS_MAP = BranchMapper(name="events",
                          key="Evt",
                          extra={
                              't_sec': 't.fSec',
                              't_ns': 't.fNanoSec'
                          },
                          exclude=[],
                          update={
                              'n_hits': 'hits',
                              'n_mc_hits': 'mc_hits',
                              'n_tracks': 'trks',
                              'n_mc_tracks': 'mc_trks'
                          },
                          attrparser=lambda a: a)

SUBBRANCH_MAPS = [
    BranchMapper(
        name="tracks",
        key="trks",
        extra={},
        exclude=['trks.usr_data', 'trks.usr', 'trks.fUniqueID', 'trks.fBits'],
        update={},
        attrparser=_nested_mapper),
    BranchMapper(name="mc_tracks",
                 key="mc_trks",
                 extra={},
                 exclude=[
                     'mc_trks.usr_data', 'mc_trks.usr', 'mc_trks.rec_stages',
                     'mc_trks.fitinf', 'mc_trks.fUniqueID', 'mc_trks.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper),
    BranchMapper(name="hits",
                 key="hits",
                 extra={},
                 exclude=[
                     'hits.usr', 'hits.pmt_id', 'hits.origin', 'hits.a',
                     'hits.pure_a', 'hits.fUniqueID', 'hits.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper),
    BranchMapper(name="mc_hits",
                 key="mc_hits",
                 extra={},
                 exclude=[
                     'mc_hits.usr', 'mc_hits.dom_id', 'mc_hits.channel_id',
                     'mc_hits.tdc', 'mc_hits.tot', 'mc_hits.trig',
                     'mc_hits.fUniqueID', 'mc_hits.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper),
]


class cached_property:
    """A simple cache decorator for properties."""
    def __init__(self, function):
        self.function = function

    def __get__(self, obj, cls):
        if obj is None:
            return self
        prop = obj.__dict__[self.function.__name__] = self.function(obj)
        return prop


class OfflineReader:
    """reader for offline ROOT files"""
    def __init__(self, file_path=None):
        """ OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file.

        """
        self._fobj = uproot.open(file_path)
        self._tree = self._fobj[MAIN_TREE_NAME]

    @cached_property
    def events(self):
        """The `E` branch, containing all offline events."""
        return Branch(self._tree,
                      mapper=EVENTS_MAP,
                      subbranchmaps=SUBBRANCH_MAPS)

    @cached_property
    def header(self):
        """The file header"""
        if 'Head' in self._fobj:
            header = {}
            for n, x in self._fobj['Head']._map_3c_string_2c_string_3e_.items(
            ):
                header[n.decode("utf-8")] = x.decode("utf-8").strip()
            return Header(header)
        else:
            warnings.warn("Your file header has an unsupported format")


class Usr:
    """Helper class to access AAObject `usr`` stuff"""
    def __init__(self, mapper, tree, index=None):
        # Here, we assume that every event has the same names in the same order
        # to massively increase the performance. This needs triple check if
        # it's always the case; the usr-format is simply a very bad design.
        self._name = mapper.key
        self._index = index
        try:
            tree[mapper.key +
                 '.usr']  # This will raise a KeyError in old aanet files
            # which has a different strucuter and key (usr_data)
            # We do not support those...
            self._usr_names = [
                n.decode("utf-8")
                for n in tree[mapper.key + '.usr_names'].lazyarray(
                    basketcache=BASKET_CACHE)[0]
            ]
        except (KeyError, IndexError):  # e.g. old aanet files
            print("The `usr` fields could not be parsed for the '{}' branch.".
                  format(self._name))
            self._usr_names = []
        else:
            self._usr_idx_lookup = {
                name: index
                for index, name in enumerate(self._usr_names)
            }
            data = tree[mapper.key +
                        '.usr'].lazyarray(basketcache=BASKET_CACHE)
            if index is not None:
                data = data[index]
            self._usr_data = data
            for name in self._usr_names:
                setattr(self, name, self[name])

    def __getitem__(self, item):
        if self._index is not None:
            return self._usr_data[self._index][:, self._usr_idx_lookup[item]]
        else:
            return self._usr_data[:, self._usr_idx_lookup[item]]

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


class Header:
    """The header"""
    def __init__(self, header):
        self._data = {}
        self._missing_keys = list(set(header.keys()) - set(mc_header.keys()))

        for attribute, fields in mc_header.items():
            values = header.get(attribute, '').split()
            if not values:
                continue
            Constructor = namedtuple(attribute, fields)
            if len(values) < len(fields):
                values += [None] * (len(fields) - len(values))
            print(attribute, fields, values)
            self._data[attribute] = Constructor(
                **{f: _to_num(v)
                   for (f, v) in zip(fields, values)})

        # quick fix while waiting for additional definitions in mc_header
        for key in self._missing_keys:
            self._data[key] = _to_num(header[key])

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
            self._mapper.exclude) - EXCLUDE_KEYS
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
                                  subbranchmaps=SUBBRANCH_MAPS)

        if isinstance(item, tuple):
            return self[item[0]][item[1]]

        if isinstance(item, str):
            return self.__getkey__(item)

        return self.__class__(self._tree,
                              self._mapper,
                              index=np.array(item),
                              keymap=self._keymap,
                              subbranchmaps=SUBBRANCH_MAPS)

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
