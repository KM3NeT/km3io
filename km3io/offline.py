import uproot

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2


class OfflineKeys:
    """wrapper for offline keys"""
    def __init__(self, file_path):
        """OfflineKeys is a class that reads all the available keys in an offline
        file and adapts the keys format to Python format.

        Parameters
        ----------
        file_path : path-like object
            Path to the offline file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        self._file_path = file_path
        self._events_keys = None
        self._hits_keys = None
        self._tracks_keys = None
        self._mc_hits_keys = None
        self._mc_tracks_keys = None
        self._valid_keys = None
        self._fit_keys = None
        self._cut_hits_keys = None
        self._cut_tracks_keys = None
        self._cut_events_keys = None

    def __str__(self):
        return '\n'.join([
            "Events keys are:\n\t" + "\n\t".join(self.events_keys),
            "Hits keys are:\n\t" + '\n\t'.join(self.hits_keys),
            "Tracks keys are:\n\t" + '\n\t'.join(self.tracks_keys),
            "Mc hits keys are:\n\t" + '\n\t'.join(self.mc_hits_keys),
            "Mc tracks keys are:\n\t" + '\n\t'.join(self.mc_tracks_keys)
        ])

    def __repr__(self):
        return str(self)
        # return f'{self.__class__.__name__}("{self._file_path}")'

    @property
    def events_keys(self):
        """reads events keys from an offline file.

        Returns
        -------
        list of str
            list of all events keys found in an offline file,
            except those found in fake branches.
        """
        if self._events_keys is None:
            fake_branches = ['Evt', 'AAObject', 'TObject', 't']
            t_baskets = ['t.fSec', 't.fNanoSec']
            tree = uproot.open(self._file_path)['E']['Evt']
            self._events_keys = [
                key.decode('utf-8') for key in tree.keys()
                if key.decode('utf-8') not in fake_branches
            ] + t_baskets
        return self._events_keys

    @property
    def hits_keys(self):
        """reads hits keys from an offline file.

        Returns
        -------
        list of str
            list of all hits keys found in an offline file,
            except those found in fake branches.
        """
        if self._hits_keys is None:
            fake_branches = [
                'hits.usr', 'hits.usr_names'
            ]  # to be treated like trks.usr and trks.usr_names
            tree = uproot.open(self._file_path)['E']['hits']
            self._hits_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._hits_keys

    @property
    def tracks_keys(self):
        """reads tracks keys from an offline file.

        Returns
        -------
        list of str
            list of all tracks keys found in an offline file,
            except those found in fake branches.
        """
        if self._tracks_keys is None:
            # a solution can be tree['trks.usr_data'].array(
            # uproot.asdtype(">i4"))
            fake_branches = [
                'trks.usr_data', 'trks.usr', 'trks.usr_names'
            ]  # can be accessed using tree['trks.usr_names'].array()
            tree = uproot.open(self._file_path)['E']['Evt']['trks']
            self._tracks_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._tracks_keys

    @property
    def mc_hits_keys(self):
        """reads mc hits keys from an offline file.

        Returns
        -------
        list of str
            list of all mc hits keys found in an offline file,
            except those found in fake branches.
        """
        if self._mc_hits_keys is None:
            fake_branches = ['mc_hits.usr', 'mc_hits.usr_names']
            tree = uproot.open(self._file_path)['E']['Evt']['mc_hits']
            self._mc_hits_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._mc_hits_keys

    @property
    def mc_tracks_keys(self):
        """reads mc tracks keys from an offline file.

        Returns
        -------
        list of str
            list of all mc tracks keys found in an offline file,
            except those found in fake branches.
        """
        if self._mc_tracks_keys is None:
            fake_branches = [
                'mc_trks.usr_data', 'mc_trks.usr', 'mc_trks.usr_names'
            ]  # same solution as above can be used
            tree = uproot.open(self._file_path)['E']['Evt']['mc_trks']
            self._mc_tracks_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._mc_tracks_keys

    @property
    def valid_keys(self):
        """constructs a list of all valid keys to be read from an offline event file.
        Returns
        -------
        list of str
            list of all valid keys.
    """
        if self._valid_keys is None:
            self._valid_keys = (self.events_keys + self.hits_keys +
                                self.tracks_keys + self.mc_tracks_keys +
                                self.mc_hits_keys)
        return self._valid_keys

    @property
    def fit_keys(self):
        """constructs a list of fit parameters, not yet outsourced in an offline file.

        Returns
        -------
        list of str
            list of all "trks.fitinf" keys.
        """
        if self._fit_keys is None:
            # these are hardcoded because they are not outsourced in offline
            # files
            self._fit_keys = [
                'JGANDALF_BETA0_RAD', 'JGANDALF_BETA1_RAD', 'JGANDALF_CHI2',
                'JGANDALF_NUMBER_OF_HITS', 'JENERGY_ENERGY', 'JENERGY_CHI2',
                'JGANDALF_LAMBDA', 'JGANDALF_NUMBER_OF_ITERATIONS',
                'JSTART_NPE_MIP', 'JSTART_NPE_MIP_TOTAL',
                'JSTART_LENGTH_METRES', 'JVETO_NPE', 'JVETO_NUMBER_OF_HITS',
                'JENERGY_MUON_RANGE_METRES', 'JENERGY_NOISE_LIKELIHOOD',
                'JENERGY_NDF', 'JENERGY_NUMBER_OF_HITS', 'JCOPY_Z_M'
            ]
        return self._fit_keys

    @property
    def cut_hits_keys(self):
        """adapts hits keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted hits keys.
        """
        if self._cut_hits_keys is None:
            self._cut_hits_keys = [
                k.split('hits.')[1].replace('.', '_') for k in self.hits_keys
            ]
        return self._cut_hits_keys

    @property
    def cut_tracks_keys(self):
        """adapts tracks keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted tracks keys.
        """
        if self._cut_tracks_keys is None:
            self._cut_tracks_keys = [
                k.split('trks.')[1].replace('.', '_') for k in self.tracks_keys
            ]
        return self._cut_tracks_keys

    @property
    def cut_events_keys(self):
        """adapts events keys for instance variables format in a Python class.

        Returns
        -------
        list of str
            list of adapted events keys.
        """
        if self._cut_events_keys is None:
            self._cut_events_keys = [
                k.replace('.', '_') for k in self.events_keys
            ]
        return self._cut_events_keys


class Reader:
    """Reader for one offline ROOT file"""
    def __init__(self, file_path):
        """ Reader class is an offline ROOT file reader. This class is a
        "very" low level I/O.

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        self._file_path = file_path
        self._data = uproot.open(self._file_path)['E'].lazyarrays(
            basketcache=uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE))
        self._keys = None

    def __getitem__(self, key):
        """reads data stored in the branch of interest in an Evt tree.

        Parameters
        ----------
        key : str
            name of the branch of interest in event data.

        Returns
        -------
        lazyarray
            Lazyarray of all data stored in the branch of interest. A lazyarray
            is an array-like object that reads data on demand. Here, only the
            first and last chunks of data are read in memory, and not all data
            in the array. The output can be used with all `Numpy's universal
            functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`
            .

        Raises
        ------
        KeyError
            Some branches in an offline file structure are "fake branches" and
            do not contain data. Therefore, the keys corresponding to these
            fake branches are not read.
        """
        if key not in self.keys.valid_keys and not isinstance(key, int):
            raise KeyError(
                "'{}' is not a valid key or is a fake branch.".format(key))
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "<{}: {} entries>".format(self.__class__.__name__, len(self))

    @property
    def keys(self):
        """wrapper for all keys in an offline file.

        Returns
        -------
        Class
            OfflineKeys.
        """
        if self._keys is None:
            self._keys = OfflineKeys(self._file_path)
        return self._keys


class OfflineReader:
    """reader for offline ROOT files"""
    def __init__(self, file_path, data=None):
        """ OfflineReader class is an offline ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        self._file_path = file_path
        if data is not None:
            self._data = data
        else:
            self._data = uproot.open(self._file_path)['E'].lazyarrays(
                basketcache=uproot.cache.ThreadSafeArrayCache(
                    BASKET_CACHE_SIZE))
        self._events = None
        self._hits = None
        self._tracks = None
        self._mc_hits = None
        self._mc_tracks = None
        self._keys = None

    def __getitem__(self, item):
        return OfflineReader(file_path=self._file_path, data=self._data[item])

    def __len__(self):
        return len(self._data)

    @property
    def keys(self):
        """wrapper for all keys in an offline file.

        Returns
        -------
        Class
            OfflineKeys.
        """
        if self._keys is None:
            self._keys = OfflineKeys(self._file_path)
        return self._keys

    @property
    def events(self):
        """wrapper for offline events.

        Returns
        -------
        Class
            OfflineEvents.
        """
        if self._events is None:
            self._events = OfflineEvents(
                self.keys.cut_events_keys,
                [self._data[key] for key in self.keys.events_keys])
        return self._events

    @property
    def hits(self):
        """wrapper for offline hits.

        Returns
        -------
        Class
            OfflineHits.
        """
        if self._hits is None:
            self._hits = OfflineHits(
                self.keys.cut_hits_keys,
                [self._data[key] for key in self.keys.hits_keys])
        return self._hits

    @property
    def tracks(self):
        """wrapper for offline tracks.

        Returns
        -------
        Class
            OfflineTracks.
        """
        if self._tracks is None:
            self._tracks = OfflineTracks(
                self.keys.cut_tracks_keys,
                [self._data[key] for key in self.keys.tracks_keys],
                fit_keys=self.keys.fit_keys)
        return self._tracks

    @property
    def mc_hits(self):
        """wrapper for offline mc hits.

        Returns
        -------
        Class
            OfflineHits.
        """
        if self._mc_hits is None:
            self._mc_hits = OfflineHits(
                self.keys.cut_hits_keys,
                [self._data[key] for key in self.keys.mc_hits_keys])
        return self._mc_hits

    @property
    def mc_tracks(self):
        """wrapper for offline mc tracks.

        Returns
        -------
        Class
            OfflineTracks.
        """
        if self._mc_tracks is None:
            self._mc_tracks = OfflineTracks(
                self.keys.cut_tracks_keys,
                [self._data[key] for key in self.keys.mc_tracks_keys])
        return self._mc_tracks


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

    def __repr__(self):
        return str(self)


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

    def __repr__(self):
        return str(self)

    # def _is_empty(array):
    #     if array.size:
    #         return False
    #     else:
    #         return True


class OfflineTracks:
    """wrapper for offline tracks"""
    def __init__(self, keys, values, fit_keys=None):
        """wrapper for offline tracks

        Parameters
        ----------
        keys : list of str
            list of cropped tracks keys.
        values : list of arrays
            list of arrays containting tracks data.
        fit_keys : None, optional
            list of tracks fit information (not yet outsourced in offline
            files).
        """
        self._keys = keys
        self._values = values
        if fit_keys is not None:
            self._fit_keys = fit_keys
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __getitem__(self, item):
        if isinstance(item, int):
            return OfflineTrack(self._keys, [v[item] for v in self._values],
                                fit_keys=self._fit_keys)
        else:
            return OfflineTracks(
                self._keys,
                [v[item] for v in self._values],
                fit_keys=self._fit_keys
            )

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
    def __init__(self, keys, values, fit_keys=None):
        """wrapper for one offline track.

        Parameters
        ----------
        keys : list of str
            list of cropped tracks keys.
        values : list of arrays
            list of arrays containting track data.
        fit_keys : None, optional
            list of tracks fit information (not yet outsourced in offline
            files).
        """
        self._keys = keys
        self._values = values
        if fit_keys is not None:
            self._fit_keys = fit_keys
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __str__(self):
        return "offline track:\n\t" + "\n\t".join([
            "{:30} {:^2} {:>26}".format(k, ':', str(v))
            for k, v in zip(self._keys, self._values) if k not in ['fitinf']
        ]) + "\n\t" + "\n\t".join([
            "{:30} {:^2} {:>26}".format(k, ':', str(v))
            for k, v in zip(self._fit_keys, self._values[18]
                            )  # I don't like 18 being explicit here
        ])

    def __getitem__(self, item):
        return self._values[item]

    def __repr__(self):
        return str(self)
