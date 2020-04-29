from collections import namedtuple
import uproot
import warnings
import awkward1 as ak1
import numba as nb

from .definitions import mc_header, fitparameters
from .tools import cached_property, to_num, unfold_indices
from .rootio import Branch, BranchMapper

MAIN_TREE_NAME = "E"
EXCLUDE_KEYS = ["AAObject", "t", "fBits", "fUniqueID"]

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2
BASKET_CACHE = uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)


def _nested_mapper(key):
    """Maps a key in the ROOT file to another key (e.g. trks.pos.x -> pos_x)"""
    return '_'.join(key.split('.')[1:])


def fitinf(fitparam, tracks):
    """Access fit parameters in tracks.fitinf.

    Parameters
    ----------
    fitparam : str
        the fit parameter name according to fitparameters defined in
        KM3NeT-Dataformat.
    tracks : class km3io.offline.OfflineBranch
        the tracks class. both full tracks branch or a slice of the
        tracks branch (example tracks[:, 0]) work.

    Returns
    -------
    awkward array
        awkward array of the values of the fit parameter requested.
    """
    fit = tracks.fitinf
    index = fitparameters[fitparam]
    try:
        params = fit[count_nested(fit, axis=2) > index]
        return ak1.Array([i[:, index] for i in params])
    except ValueError:
        # This is the case for tracks[:, 0] or any other selection.
        params = fit[count_nested(fit, axis=1) > index]
        return params[:, index]


def fitparams():
    """name of the fit parameters as defined in the official
    KM3NeT-Dataformat.

    Returns
    -------
    dict_keys
        fit parameters keys.
    """
    return fitparameters.keys()


def count_nested(Array, axis=0):
    """count elements in a nested awkward Array.

    Parameters
    ----------
    Array : Awkward1 Array
        Array of data. Example tracks.fitinf or tracks.rec_stages.
    axis : int, optional
        axis = 0: to count elements in the outmost level of nesting.
        axis = 1: to count elements in the first level of nesting.
        axis = 2: to count elements in the second level of nesting.

    Returns
    -------
    awkward1 Array or int
        counts of elements found in a nested awkward1 Array.
    """
    if axis == 0:
        return ak1.num(Array, axis=0)
    if axis == 1:
        return ak1.num(Array, axis=1)
    if axis == 2:
        return ak1.count(Array, axis=2)


@nb.jit(nopython=True)
def _find(rec_stages, stages, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are found, the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages .
    stages : awkward1 Array
        reconstruction stages of interest.
    builder : awkward1.highlevel.ArrayBuilder
        awkward1 Array builder.
    """
    for s in rec_stages:
        builder.begin_list()
        for i in s:
            num_stages = len(i)
            if num_stages == len(stages):
                found = 0
                for j in range(num_stages):
                    if i[j] == stages[j]:
                        found += 1
                if found == num_stages:
                    builder.append(1)
                else:
                    builder.append(0)
            else:
                builder.append(0)
        builder.end_list()


def mask(rec_stages, stages):
    """create a mask on tracks.rec_stages .

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages .
    stages : list
        reconstruction stages of interest.

    Returns
    -------
    awkward1 Array
        an awkward1 Array mask where True corresponds to the positions
        where stages were found. False otherwise.
    """
    builder = ak1.ArrayBuilder()
    _find(rec_stages, ak1.Array(stages), builder)
    return builder.snapshot() == 1


def best_track(tracks, strategy="first", rec_stages=None):
    """best track selection based on different strategies

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        the tracks branch.
    strategy : str
        the trategy desired to select the best tracks.
    """
    if strategy == "first":
        return tracks[:, 0]
    # if strategy == "rec_stages" and rec_stages is not None:
    #     mask = tracks.rec_stages[]


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
                          })

SUBBRANCH_MAPS = [
    BranchMapper(name="tracks",
                 key="trks",
                 extra={},
                 exclude=EXCLUDE_KEYS +
                 ['trks.usr_data', 'trks.usr', 'trks.fUniqueID', 'trks.fBits'],
                 attrparser=_nested_mapper,
                 flat=False,
                 toawkward=['usr', 'fitinf', 'rec_stages']),
    BranchMapper(name="mc_tracks",
                 key="mc_trks",
                 exclude=EXCLUDE_KEYS + [
                     'mc_trks.rec_stages',
                     'mc_trks.fitinf', 'mc_trks.fUniqueID', 'mc_trks.fBits'
                 ],
                 attrparser=_nested_mapper,
                 toawkward=['usr', 'usr_names'],
                 flat=False),
    BranchMapper(name="hits",
                 key="hits",
                 exclude=EXCLUDE_KEYS + [
                     'hits.usr', 'hits.pmt_id', 'hits.origin', 'hits.a',
                     'hits.pure_a', 'hits.fUniqueID', 'hits.fBits'
                 ],
                 attrparser=_nested_mapper,
                 flat=False),
    BranchMapper(name="mc_hits",
                 key="mc_hits",
                 exclude=EXCLUDE_KEYS + [
                     'mc_hits.usr', 'mc_hits.dom_id', 'mc_hits.channel_id',
                     'mc_hits.tdc', 'mc_hits.tot', 'mc_hits.trig',
                     'mc_hits.fUniqueID', 'mc_hits.fBits'
                 ],
                 attrparser=_nested_mapper,
                 flat=False),
]


class OfflineBranch(Branch):
    @cached_property
    def usr(self):
        return Usr(self._mapper, self._branch, index_chain=self._index_chain)


class Usr:
    """Helper class to access AAObject `usr` stuff (only for events.usr)"""
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
            data = unfold_indices(data, self._index_chain)

        self._usr_data = data

        for name in self._usr_names:
            setattr(self, name, self[name])

    def __getitem__(self, item):
        if self._index_chain:
            return unfold_indices(
                self._usr_data, self._index_chain)[:,
                                                   self._usr_idx_lookup[item]]
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
        self._filename = file_path
        self._tree = self._fobj[MAIN_TREE_NAME]

    def close(self):
        self._fobj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

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
                self._data[attribute] = to_num(values[0])
                continue

            n_max = max(n_values, n_fields)
            values += [None] * (n_max - n_values)
            fields += ["field_{}".format(i) for i in range(n_fields, n_max)]

            Constructor = namedtuple(attribute, fields)

            if not values:
                continue

            self._data[attribute] = Constructor(
                **{f: to_num(v)
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
