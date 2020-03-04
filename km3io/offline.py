import uproot
import numpy as np
import warnings
import km3io.definitions.trigger
import km3io.definitions.fitparameters
import km3io.definitions.reconstruction

MAIN_TREE_NAME = "E"
# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2


class cached_property:
    """A simple cache decorator for properties."""
    def __init__(self, function):
        self.function= function

    def __get__(self, obj, cls):
        if obj is None:
            return self
        prop = obj.__dict__[self.function.__name__] = self.function(obj)
        return prop


class OfflineKeys:
    """wrapper for offline keys"""
    def __init__(self, tree):
        """OfflineKeys is a class that reads all the available keys in an offline
        file and adapts the keys format to Python format.

        Parameters
        ----------
        tree : uproot.TTree
            The main ROOT tree.
        """
        self._tree = tree

    def __str__(self):
        return '\n'.join([
            "Events keys are:\n\t" + "\n\t".join(self.events_keys),
            "Hits keys are:\n\t" + '\n\t'.join(self.hits_keys),
            "Tracks keys are:\n\t" + '\n\t'.join(self.tracks_keys),
            "Mc hits keys are:\n\t" + '\n\t'.join(self.mc_hits_keys),
            "Mc tracks keys are:\n\t" + '\n\t'.join(self.mc_tracks_keys)
        ])

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def _get_keys(self, tree, fake_branches=None):
        """Get tree keys except those in fake_branches

        Parameters
        ----------
        tree : uproot.Tree
            The tree to look for keys
        fake_branches : list of str or None
            The fake branches to ignore

        Returns
        -------
        list of str
            The keys of the tree.
        """
        keys = []
        for key in tree.keys():
            key = key.decode('utf-8')
            if fake_branches is not None and key in fake_branches:
                continue
            keys.append(key)
        return keys

    @cached_property
    def events_keys(self):
        """reads events keys from an offline file.

        Returns
        -------
        list of str
            list of all events keys found in an offline file,
            except those found in fake branches.
        """
        fake_branches = ['Evt', 'AAObject', 'TObject', 't']
        t_baskets = ['t.fSec', 't.fNanoSec']
        tree = self._tree['Evt']
        return self._get_keys(self._tree['Evt'], fake_branches) + t_baskets

    @cached_property
    def hits_keys(self):
        """reads hits keys from an offline file.

        Returns
        -------
        list of str
            list of all hits keys found in an offline file,
            except those found in fake branches.
        """
        fake_branches = ['hits.usr', 'hits.usr_names']
        return self._get_keys(self._tree['hits'], fake_branches)

    @cached_property
    def tracks_keys(self):
        """reads tracks keys from an offline file.

        Returns
        -------
        list of str
            list of all tracks keys found in an offline file,
            except those found in fake branches.
        """
        # a solution can be tree['trks.usr_data'].array(
        # uproot.asdtype(">i4"))
        fake_branches = ['trks.usr_data', 'trks.usr', 'trks.usr_names']
        return self._get_keys(self._tree['Evt']['trks'], fake_branches)

    @cached_property
    def mc_hits_keys(self):
        """reads mc hits keys from an offline file.

        Returns
        -------
        list of str
            list of all mc hits keys found in an offline file,
            except those found in fake branches.
        """
        fake_branches = ['mc_hits.usr', 'mc_hits.usr_names']
        return self._get_keys(self._tree['Evt']['mc_hits'], fake_branches)

    @cached_property
    def mc_tracks_keys(self):
        """reads mc tracks keys from an offline file.

        Returns
        -------
        list of str
            list of all mc tracks keys found in an offline file,
            except those found in fake branches.
        """
        fake_branches = ['mc_trks.usr_data', 'mc_trks.usr', 'mc_trks.usr_names']
        return self._get_keys(self._tree['Evt']['mc_trks'], fake_branches)

    @cached_property
    def valid_keys(self):
        """constructs a list of all valid keys to be read from an offline event file.
        Returns
        -------
        list of str
            list of all valid keys.
        """
        return (self.events_keys + self.hits_keys + self.tracks_keys +
                self.mc_tracks_keys + self.mc_hits_keys)

    @cached_property
    def fit_keys(self):
        """constructs a list of fit parameters, not yet outsourced in an offline file.

        Returns
        -------
        list of str
            list of all "trks.fitinf" keys.
        """
        return sorted(km3io.definitions.fitparameters.data,
                      key=km3io.definitions.fitparameters.data.get,
                      reverse=False)

    @cached_property
    def cut_hits_keys(self):
        """adapts hits keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted hits keys.
        """
        return [k.split('hits.')[1].replace('.', '_') for k in self.hits_keys]

    @cached_property
    def cut_tracks_keys(self):
        """adapts tracks keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted tracks keys.
        """
        return [
            k.split('trks.')[1].replace('.', '_') for k in self.tracks_keys
        ]

    @cached_property
    def cut_events_keys(self):
        """adapts events keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted events keys.
        """
        return [k.replace('.', '_') for k in self.events_keys]


class OfflineReader:
    """reader for offline ROOT files"""
    def __init__(self, file_path=None, fobj=None, data=None):
        """ OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file.

        """
        self._file_path = file_path

        if file_path is not None:
            self._fobj = uproot.open(self._file_path)
            self._tree = self._fobj[MAIN_TREE_NAME]
            self._data = self._tree.lazyarrays(
                basketcache=uproot.cache.ThreadSafeArrayCache(
                    BASKET_CACHE_SIZE))
        else:
            self._fobj = fobj
            self._tree = self._fobj[MAIN_TREE_NAME]
            self._data = data

    @classmethod
    def from_index(cls, source, index):
        """Create an instance with a subtree of a given index

        Parameters
        ----------
        source: ROOTDirectory
            The source file.
        index: index or slice
            The index or slice to create the subtree.
        """
        instance = cls(fobj=source._fobj, data=source._data[index])
        return instance

    def __getitem__(self, index):
        return OfflineReader.from_index(source=self, index=index)

    def __len__(self):
        return len(self._data)

    @cached_property
    def header(self):
        if 'Head' in self._fobj:
            header = {}
            for n, x in self._fobj['Head']._map_3c_string_2c_string_3e_.items():
                header[n.decode("utf-8")] = x.decode("utf-8").strip()
            return header
        else:
            warnings.warn("Your file header has an unsupported format")

    @cached_property
    def keys(self):
        """wrapper for all keys in an offline file.

        Returns
        -------
        Class
            OfflineKeys.
        """
        return OfflineKeys(self._tree)

    @cached_property
    def events(self):
        """wrapper for offline events.

        Returns
        -------
        Class
            OfflineEvents.
        """
        return OfflineEvents(
            self.keys.cut_events_keys,
            [self._data[key] for key in self.keys.events_keys])

    @cached_property
    def hits(self):
        """wrapper for offline hits.

        Returns
        -------
        Class
            OfflineHits.
        """
        return OfflineHits(self.keys.cut_hits_keys,
                           [self._data[key] for key in self.keys.hits_keys])

    @cached_property
    def tracks(self):
        """wrapper for offline tracks.

        Returns
        -------
        Class
            OfflineTracks.
        """
        return OfflineTracks(
            self.keys.cut_tracks_keys,
            [self._data[key] for key in self.keys.tracks_keys]
            )

    @cached_property
    def mc_hits(self):
        """wrapper for offline mc hits.

        Returns
        -------
        Class
            OfflineHits.
        """
        return OfflineHits(self.keys.cut_hits_keys,
                           [self._data[key] for key in self.keys.mc_hits_keys])

    @cached_property
    def mc_tracks(self):
        """wrapper for offline mc tracks.

        Returns
        -------
        Class
            OfflineTracks.
        """
        return OfflineTracks(
            self.keys.cut_tracks_keys,
            [self._data[key] for key in self.keys.mc_tracks_keys])

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
                n.decode("utf-8")
                for n in tree['Evt']['usr_names'].array()[0]
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


class OfflineEvents:
    """wrapper for offline events"""
    def __init__(self, keys, values):
        """wrapper for offline events.

        Parameters
        ----------
        keys : list of str
            list of valid events keys.
        values : list of arrays
            list of arrays containting events data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __getitem__(self, item):
        return OfflineEvent(self._keys, [v[item] for v in self._values])

    def __len__(self):
        try:
            return len(self._values[0])
        except IndexError:
            return 0

    def __str__(self):
        return "Number of events: {}".format(len(self))

    def __repr__(self):
        return "<{}: {} parsed events>".format(self.__class__.__name__,
                                               len(self))


class OfflineEvent:
    """wrapper for an offline event"""
    def __init__(self, keys, values):
        """wrapper for one offline event.

        Parameters
        ----------
        keys : list of str
            list of valid events keys.
        values : list of arrays
            list of arrays containting event data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __str__(self):
        return "offline event:\n\t" + "\n\t".join([
            "{:15} {:^10} {:>10}".format(k, ':', str(v))
            for k, v in zip(self._keys, self._values)
        ])


class OfflineHits:
    """wrapper for offline hits"""
    def __init__(self, keys, values):
        """wrapper for offline hits.

        Parameters
        ----------
        keys : list of str
            list of cropped hits keys.
        values : list of arrays
            list of arrays containting hits data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __getitem__(self, item):
        return OfflineHit(self._keys, [v[item] for v in self._values])

    def __len__(self):
        try:
            return len(self._values[0])
        except IndexError:
            return 0

    def __str__(self):
        return "Number of hits: {}".format(len(self))

    def __repr__(self):
        return "<{}: {} parsed elements>".format(self.__class__.__name__,
                                                 len(self))


class OfflineHit:
    """wrapper for an offline hit"""
    def __init__(self, keys, values):
        """wrapper for one offline hit.

        Parameters
        ----------
        keys : list of str
            list of cropped hits keys.
        values : list of arrays
            list of arrays containting hit data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __str__(self):
        return "offline hit:\n\t" + "\n\t".join([
            "{:15} {:^10} {:>10}".format(k, ':', str(v))
            for k, v in zip(self._keys, self._values)
        ])

    def __getitem__(self, item):
        return self._values[item]


class OfflineTracks:
    """wrapper for offline tracks"""
    def __init__(self, keys, values):
        """wrapper for offline tracks

        Parameters
        ----------
        keys : list of str
            list of cropped tracks keys.
        values : list of arrays
            list of arrays containting tracks data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __getitem__(self, item):
        return OfflineTrack(self._keys, [v[item] for v in self._values])

    def __len__(self):
        try:
            return len(self._values[0])
        except IndexError:
            return 0

    def __str__(self):
        return "Number of tracks: {}".format(len(self))

    def __repr__(self):
        return "<{}: {} parsed elements>".format(self.__class__.__name__,
                                                 len(self))


class OfflineTrack:
    """wrapper for an offline track"""
    def __init__(self, keys, values):
        """wrapper for one offline track.

        Parameters
        ----------
        keys : list of str
            list of cropped tracks keys.
        values : list of arrays
            list of arrays containting track data.
        """
        self._keys = keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __str__(self):
        return "offline track:\n\t" + "\n\t".join([
            "{:30} {:^2} {:>26}".format(k, ':', str(v))
            for k, v in zip(self._keys, self._values) if k not in ['fitinf']
        ]) + "\n\t" + "\n\t".join([
            "{:30} {:^2} {:>26}".format(k, ':', str(
                getattr(self, 'fitinf')[v]))
            for k, v in km3io.definitions.fitparameters.data.items()
            if len(getattr(self, 'fitinf')) > v
        ])  # I don't like 18 being explicit here

    def __getitem__(self, item):
        return self._values[item]
