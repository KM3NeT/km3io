from collections import namedtuple
import uproot
import numpy as np
import awkward as ak
import warnings
from .definitions import mc_header

MAIN_TREE_NAME = "E"
# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2

BranchMapper = namedtuple(
    "BranchMapper",
    ['name', 'key', 'extra', 'exclude', 'update', 'attrparser'])


def _nested_mapper(key):
    """Maps a key in the ROOT file to another key (e.g. trks.pos.x -> pos_x)"""
    return '_'.join(key.split('.')[1:])


EXCLUDE_KEYS = set(["AAObject", "t", "fBits", "fUniqueID"])
BRANCH_MAPS = [
    BranchMapper("tracks", "trks", {}, ['trks.usr_data', 'trks.usr'], {},
                 _nested_mapper),
    BranchMapper("mc_tracks", "mc_trks", {},
                 ['mc_trks.usr_data', 'mc_trks.usr'], {}, _nested_mapper),
    BranchMapper("hits", "hits", {}, ['hits.usr'], {}, _nested_mapper),
    BranchMapper("mc_hits", "mc_hits", {},
                 ['mc_hits.usr', 'mc_hits.dom_id', 'mc_hits.channel_id'], {},
                 _nested_mapper),
    BranchMapper("events", "Evt", {
        't_sec': 't.fSec',
        't_ns': 't.fNanoSec'
    }, [], {
        'n_hits': 'hits',
        'n_mc_hits': 'mc_hits',
        'n_tracks': 'trks',
        'n_mc_tracks': 'mc_trks'
    }, lambda a: a),
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
    def __init__(self,
                 file_path=None,
                 fobj=None,
                 data=None,
                 index=slice(None)):
        """ OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file.

        """
        self._index = index
        if file_path is not None:
            self._fobj = uproot.open(file_path)
            self._tree = self._fobj[MAIN_TREE_NAME]
            self._data = self._tree.lazyarrays(
                basketcache=uproot.cache.ThreadSafeArrayCache(
                    BASKET_CACHE_SIZE))
        else:
            self._fobj = fobj
            self._tree = self._fobj[MAIN_TREE_NAME]
            self._data = data

        for mapper in BRANCH_MAPS:
            setattr(self, mapper.name,
                    Branch(self._tree, mapper=mapper, index=self._index))

    @classmethod
    def from_index(cls, source, index):
        """Create an instance with a subtree of a given index

        Parameters
        ----------
        source: ROOTDirectory
            The source file object.
        index: index or slice
            The index or slice to create the subtree.
        """
        instance = cls(fobj=source._fobj,
                       data=source._data[index],
                       index=index)
        return instance

    def __getitem__(self, index):
        return OfflineReader.from_index(source=self, index=index)

    def __len__(self):
        tree = self._fobj[MAIN_TREE_NAME]
        if self._index == slice(None):
            return len(tree)
        else:
            return len(
                tree.lazyarrays(basketcache=uproot.cache.ThreadSafeArrayCache(
                    BASKET_CACHE_SIZE))[self.index])

    @cached_property
    def header(self):
        if 'Head' in self._fobj:
            header = {}
            for n, x in self._fobj['Head']._map_3c_string_2c_string_3e_.items(
            ):
                header[n.decode("utf-8")] = x.decode("utf-8").strip()
            return Header(header)
        else:
            warnings.warn("Your file header has an unsupported format")

    @cached_property
    def usr(self):
        return Usr(self._tree)

    def get_best_reco(self):
        """returns the best reconstructed track fit data. The best fit is defined
        as the track fit with the maximum reconstruction stages. When "nan" is
        returned, it means that the reconstruction parameter of interest is not
        found. for example, in the case of muon simulations: if [1, 2] are the
        reconstruction stages, then only the fit parameters corresponding to the
        stages [1, 2] are found in the Offline files, the remaining fit parameters
        corresponding to the stages 3, 4, 5 are all filled with nan. 

        Returns
        -------
        numpy recarray
            a recarray of the best track fit data (reconstruction data).
        """
        keys = ", ".join(self.keys.fit_keys[:-1])
        empty_fit_info = np.array(
            [match for match in self._find_empty(self.tracks.fitinf)])
        fit_info = [
            i for i, j in zip(self.tracks.fitinf, empty_fit_info[:, 1])
            if j is not None
        ]
        stages = self._get_max_reco_stages(self.tracks.rec_stages)
        fit_data = np.array([i[j] for i, j in zip(fit_info, stages[:, 2])])
        rows_size = len(max(fit_data, key=len))
        equal_size_data = np.vstack([
            np.hstack([i, np.zeros(rows_size - len(i)) + np.nan])
            for i in fit_data
        ])
        return np.core.records.fromarrays(equal_size_data.transpose(),
                                          names=keys)

    def _get_max_reco_stages(self, reco_stages):
        """find the longest reconstructed track based on the maximum size of 
        reconstructed stages. 

        Parameters
        ----------
        reco_stages : chunked array 
            chunked array of all the reconstruction stages of all tracks.
            In km3io, it is accessed with
            km3io.OfflineReader(my_file).tracks.rec_stages .

        Returns
        -------
        numpy array
            array with 3 columns: *list of the maximum reco_stages
                                  *lentgh of the maximum reco_stages
                                  *position of the maximum reco_stages
        """
        empty_reco_stages = np.array(
            [match for match in self._find_empty(reco_stages)])
        max_reco_stages = np.array(
            [[max(i, key=len),
              len(max(i, key=len)),
              i.index(max(i, key=len))]
             for i, j in zip(reco_stages, empty_reco_stages[:, 1])
             if j is not None])
        return max_reco_stages

    def get_reco_fit(self, stages, mc=False):
        """construct a numpy recarray of the fit information (reconstruction
        data) of the tracks reconstructed following the reconstruction stages
        of interest.

        Parameters
        ----------
        stages : list
            list of reconstruction stages of interest. for example
            [1, 2, 3, 4, 5].
        mc : bool, optional
            default is False to look for fit data in the tracks tree in offline files
            (not the mc tracks tree). mc=True to look for fit data from the mc tracks
            tree in offline files.

        Returns
        -------
        numpy recarray
            a recarray of the fit information (reconstruction data) of
            the tracks of interest.

        Raises
        ------
        ValueError
            ValueError raised when the reconstruction stages of interest
            are not found in the file.
        """
        keys = ", ".join(self.keys.fit_keys[:-1])

        if mc is False:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=False)])
            fitinf = self.tracks.fitinf

        if mc is True:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=True)])
            fitinf = self.mc_tracks.fitinf

        mask = rec_stages[:, 1] != None

        if np.all(rec_stages[:, 1] == None):
            raise ValueError(
                "The stages {} are not found in your file.".format(
                    str(stages)))
        else:
            fit_data = np.array(
                [i[k] for i, k in zip(fitinf[mask], rec_stages[:, 1][mask])])
            rec_array = np.core.records.fromarrays(fit_data.transpose(),
                                                   names=keys)
            return rec_array

    def get_reco_hits(self, stages, keys, mc=False):
        """construct a dictionary of hits class data based on the reconstruction
        stages of interest. For example, if the reconstruction stages of interest
        are [1, 2, 3, 4, 5], then get_reco_hits method will select the hits data 
        from the events that were reconstructed following these stages (i.e 
        [1, 2, 3, 4, 5]).

        Parameters
        ----------
        stages : list
            list of reconstruction stages of interest. for example
            [1, 2, 3, 4, 5].
        keys : list of str
            list of the hits class attributes.
        mc : bool, optional
            default is False to look for hits data in the hits tree in offline files
            (not the mc_hits tree). mc=True to look for mc hits data in the mc hits
            tree in offline files.

        Returns
        -------
        dict
            dictionary of lazyarrays containing data for each hits attribute requested.

        Raises
        ------
        ValueError
            ValueError raised when the reconstruction stages of interest
            are not found in the file.
        """
        lazy_d = {}

        if mc is False:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=False)])
            hits_data = self.hits

        if mc is True:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=True)])
            hits_data = self.mc_hits

        mask = rec_stages[:, 1] != None

        if np.all(rec_stages[:, 1] == None):
            raise ValueError(
                "The stages {} are not found in your file.".format(
                    str(stages)))
        else:
            for key in keys:
                lazy_d[key] = getattr(hits_data, key)[mask]
        return lazy_d

    def get_reco_events(self, stages, keys, mc=False):
        """construct a dictionary of events class data based on the reconstruction
        stages of interest. For example, if the reconstruction stages of interest
        are [1, 2, 3, 4, 5], then get_reco_events method will select the events data 
        that were reconstructed following these stages (i.e [1, 2, 3, 4, 5]).

        Parameters
        ----------
        stages : list
            list of reconstruction stages of interest. for example
            [1, 2, 3, 4, 5].
        keys : list of str
            list of the events class attributes.
        mc : bool, optional
            default is False to look for the reconstruction stages in the tracks tree
            in offline files (not the mc tracks tree). mc=True to look for the reconstruction
            data in the mc tracks tree in offline files.

        Returns
        -------
        dict
            dictionary of lazyarrays containing data for each events attribute requested.

        Raises
        ------
        ValueError
            ValueError raised when the reconstruction stages of interest
            are not found in the file.
        """
        lazy_d = {}

        if mc is False:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=False)])

        if mc is True:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=True)])

        mask = rec_stages[:, 1] != None

        if np.all(rec_stages[:, 1] == None):
            raise ValueError(
                "The stages {} are not found in your file.".format(
                    str(stages)))
        else:
            for key in keys:
                lazy_d[key] = getattr(self.events, key)[mask]
        return lazy_d

    def get_reco_tracks(self, stages, keys, mc=False):
        """construct a dictionary of tracks class data based on the reconstruction
        stages of interest. For example, if the reconstruction stages of interest
        are [1, 2, 3, 4, 5], then get_reco_tracks method will select tracks data 
        from the events that were reconstructed following these stages (i.e 
        [1, 2, 3, 4, 5]).

        Parameters
        ----------
        stages : list
            list of reconstruction stages of interest. for example
            [1, 2, 3, 4, 5].
        keys : list of str
            list of the tracks class attributes.
        mc : bool, optional
            default is False to look for tracks data in the tracks tree in offline files
            (not the mc tracks tree). mc=True to look for tracks data in the mc tracks
            tree in offline files.

        Returns
        -------
        dict
            dictionary of lazyarrays containing data for each tracks attribute requested.

        Raises
        ------
        ValueError
            ValueError raised when the reconstruction stages of interest
            are not found in the file.
        """
        lazy_d = {}

        if mc is False:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=False)])
            tracks_data = self.tracks

        if mc is True:
            rec_stages = np.array(
                [match for match in self._find_rec_stages(stages, mc=True)])
            tracks_data = self.mc_tracks

        mask = rec_stages[:, 1] != None

        if np.all(rec_stages[:, 1] == None):
            raise ValueError(
                "The stages {} are not found in your file.".format(
                    str(stages)))
        else:
            for key in keys:
                lazy_d[key] = np.array([
                    i[k] for i, k in zip(
                        getattr(tracks_data, key)[mask], rec_stages[:,
                                                                    1][mask])
                ])

        return lazy_d

    def _find_rec_stages(self, stages, mc=False):
        """find the index of reconstruction stages of interest in a
        list of multiple reconstruction stages.

        Parameters
        ----------
        stages : list
            list of reconstruction stages of interest. for example
            [1, 2, 3, 4, 5].
        mc : bool, optional
            default is False to look for reconstruction stages in the tracks tree in
            offline files (not the mc tracks tree). mc=True to look for reconstruction
            stages in the mc tracks tree in offline files.
        Yields
        ------
        generator
            the track id and the index of the reconstruction stages of
            interest if found. If the reconstruction stages of interest
            are not found, None is returned as the stages index.
        """
        if mc is False:
            stages_data = self.tracks.rec_stages

        if mc is True:
            stages_data = self.mc_tracks.rec_stages

        for trk_index, rec_stages in enumerate(stages_data):
            try:
                stages_index = rec_stages.index(stages)
            except ValueError:
                stages_index = None
                yield trk_index, stages_index
                continue

            yield trk_index, stages_index

    def _find_empty(self, array):
        """finds empty lists/arrays in an awkward array

        Parameters
        ----------
        array : awkward array
            Awkward array of data of interest. For example:
            km3io.OfflineReader(my_file).tracks.fitinf .

        Yields
        ------
        generator
            the empty list id and the index of the empty list. When
            data structure (list) is simply empty, None is written in the
            corresponding index. However, when data structure (list) is not
            empty and does not contain an empty list, then False is written in the
            corresponding index.
        """
        for i, rs in enumerate(array):
            try:
                if len(rs) == 0:
                    j = None
                if len(rs) != 0:
                    j = rs.index([])
            except ValueError:
                j = False  # rs not empty but [] not found
                yield i, j
                continue
            yield i, j


class Usr:
    """Helper class to access AAObject usr stuff"""
    def __init__(self, tree):
        # Here, we assume that every event has the same names in the same order
        # to massively increase the performance. This needs triple check if it's
        # always the case; the usr-format is simply a very bad design.
        try:
            self._usr_names = [
                n.decode("utf-8") for n in tree['Evt']['usr_names'].array()[0]
            ]
        except (KeyError, IndexError):  # e.g. old aanet files
            self._usr_names = []
        else:
            self._usr_idx_lookup = {
                name: index
                for index, name in enumerate(self._usr_names)
            }
            self._usr_data = tree['Evt']['usr'].lazyarray(
                basketcache=uproot.cache.ThreadSafeArrayCache(
                    BASKET_CACHE_SIZE))
            for name in self._usr_names:
                setattr(self, name, self[name])

    def __getitem__(self, item):
        return self._usr_data[:, self._usr_idx_lookup[item]]

    def keys(self):
        return self._usr_names

    def __str__(self):
        entries = []
        for name in self.keys():
            entries.append("{}: {}".format(name, self[name]))
        return '\n'.join(entries)


def _to_num(value):
    """Convert a value to a numerical one if possible"""
    if value is None:
        return
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            pass
    else:
        return value


class Header:
    """The online header"""
    def __init__(self, header):
        self._data = {}
        for attribute, fields in mc_header.items():
            values = header.get(attribute, '').split()
            if not values:
                continue
            Constructor = namedtuple(attribute, fields)
            if len(values) < len(fields):
                values += [None] * (len(fields) - len(values))
            self._data[attribute] = Constructor(
                **{f: _to_num(v)
                   for (f, v) in zip(fields, values)})

        for attribute, value in self._data.items():
            setattr(self, attribute, value)

    def __str__(self):
        lines = ["MC Header:"]
        for value in self._data.values():
            lines.append("  {}".format(value))
        return "\n".join(lines)


class Branch:
    """Branch accessor class"""
    def __init__(self, tree, mapper, index=slice(None)):
        self._tree = tree
        self._mapper = mapper
        self._index = index
        self._keymap = None
        self._branch = tree[mapper.key]

        self._initialise_keys()

    def _initialise_keys(self):
        """Create the keymap and instance attributes"""
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

        # self._EntryType = namedtuple(mapper.name[:-1], self.keys())

        for key in self.keys():
            # print("setting", self._mapper.name, key)
            setattr(self, key, self[key])

    def keys(self):
        return self._keymap.keys()

    def __getitem__(self, item):
        """Slicing magic a la numpy"""
        if isinstance(item, slice):
            return self.__class__(self._tree, self._mapper, index=item)
        if isinstance(item, int):
            return BranchElement(
                self._mapper.name, {
                    key: self._branch[self._keymap[key]].array()[self._index,
                                                                 item]
                    for key in self.keys()
                })
        if isinstance(item, tuple):
            return self[item[0]][item[1]]
        return self._branch[self._keymap[item]].lazyarray(
            basketcache=uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE))[
                self._index]

    def __len__(self):
        if self._index == slice(None):
            return len(self._branch)
        else:
            return len(
                self._branch[self._keymap['id']].lazyarray()[self._index])

    def __str__(self):
        return "Number of elements: {}".format(len(self._branch))

    def __repr__(self):
        return "<{}[{}]: {} parsed elements>".format(self.__class__.__name__,
                                                     self._mapper.name,
                                                     len(self))


class BranchElement:
    """Represents a single branch element

    Parameters
    ----------
    name: str
        The name of the branch
    dct: dict (keys=attributes, values=arrays of values)
        The data
    index: slice
        The slice mask to be applied to the sub-arrays
    """
    def __init__(self, name, dct, index=slice(None)):
        self._dct = dct
        self._name = name
        self._index = index
        self.ItemConstructor = namedtuple(self._name[:-1], dct.keys())
        for key, values in dct.items():
            setattr(self, key, values[index])

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self._name, self._dct, index=item)
        if isinstance(item, int):
            return self.ItemConstructor(
                **{k: v[self._index][item]
                   for k, v in self._dct.items()})

    def __repr__(self):
        return "<{}[{}]>".format(self.__class__.__name__, self._name)
