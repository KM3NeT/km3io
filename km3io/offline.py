from collections import namedtuple
import uproot
import warnings
from .definitions import mc_header
from .tools import Branch, BranchMapper, cached_property, _to_num, _unfold_indices

MAIN_TREE_NAME = "E"
EXCLUDE_KEYS = ["AAObject", "t", "fBits", "fUniqueID"]

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2
BASKET_CACHE = uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)


def _nested_mapper(key):
    """Maps a key in the ROOT file to another key (e.g. trks.pos.x -> pos_x)"""
    return '_'.join(key.split('.')[1:])


EVENTS_MAP = BranchMapper(name="events",
                          key="Evt",
                          extra={
                              't_sec': 't.fSec',
                              't_ns': 't.fNanoSec'
                          },
                          exclude=EXCLUDE_KEYS,
                          update={
                              'n_hits': 'hits',
                              'n_mc_hits': 'mc_hits',
                              'n_tracks': 'trks',
                              'n_mc_tracks': 'mc_trks'
                          },
                          attrparser=lambda a: a,
                          flat=True)

SUBBRANCH_MAPS = [
    BranchMapper(name="tracks",
                 key="trks",
                 extra={},
                 exclude=EXCLUDE_KEYS +
                 ['trks.usr_data', 'trks.usr', 'trks.fUniqueID', 'trks.fBits'],
                 update={},
                 attrparser=_nested_mapper,
                 flat=False),
    BranchMapper(name="mc_tracks",
                 key="mc_trks",
                 extra={},
                 exclude=EXCLUDE_KEYS + [
                     'mc_trks.usr_data', 'mc_trks.usr', 'mc_trks.rec_stages',
                     'mc_trks.fitinf', 'mc_trks.fUniqueID', 'mc_trks.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper,
                 flat=False),
    BranchMapper(name="hits",
                 key="hits",
                 extra={},
                 exclude=EXCLUDE_KEYS + [
                     'hits.usr', 'hits.pmt_id', 'hits.origin', 'hits.a',
                     'hits.pure_a', 'hits.fUniqueID', 'hits.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper,
                 flat=False),
    BranchMapper(name="mc_hits",
                 key="mc_hits",
                 extra={},
                 exclude=EXCLUDE_KEYS + [
                     'mc_hits.usr', 'mc_hits.dom_id', 'mc_hits.channel_id',
                     'mc_hits.tdc', 'mc_hits.tot', 'mc_hits.trig',
                     'mc_hits.fUniqueID', 'mc_hits.fBits'
                 ],
                 update={},
                 attrparser=_nested_mapper,
                 flat=False),
]


class OfflineBranch(Branch):
    @cached_property
    def usr(self):
        return Usr(self._mapper, self._branch, index_chain=self._index_chain)


class Usr:
    """Helper class to access AAObject `usr` stuff"""
    def __init__(self, mapper, branch, index_chain=None):
        self._mapper = mapper
        self._name = mapper.name
        self._index_chain = [] if index_chain is None else index_chain
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
            n.decode("utf-8")
            for n in self._branch[self._usr_key + '_names'].lazyarray()[0]
        ]
        self._usr_idx_lookup = {
            name: index
            for index, name in enumerate(self._usr_names)
        }

        data = self._branch[self._usr_key].lazyarray()

        if self._index_chain:
            data = _unfold_indices(data, self._index_chain)

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
        if self._index_chain:
            return _unfold_indices(
                self._usr_data, self._index_chain)[:,
                                                   self._usr_idx_lookup[item]]
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
        return _unfold_indices(data, self._index_chain)

    def keys(self):
        return self._usr_names

    def __str__(self):
        entries = []
        for name in self.keys():
            entries.append("{}: {}".format(name, self[name]))
        return '\n'.join(entries)

    def __repr__(self):
        return "<{}[{}]>".format(self.__class__.__name__, self._name)


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
        return OfflineBranch(self._tree,
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
                self._data[attribute] = _to_num(values[0])
                continue

            n_max = max(n_values, n_fields)
            values += [None] * (n_max - n_values)
            fields += ["field_{}".format(i) for i in range(n_fields, n_max)]

            Constructor = namedtuple(attribute, fields)

            if not values:
                continue

            self._data[attribute] = Constructor(
                **{f: _to_num(v)
                   for (f, v) in zip(fields, values)})

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
