import uproot


class AanetKeys:
    "wrapper for aanet keys"

    def __init__(self, file_path):
        self._file_path = file_path
        self._events_keys = None
        self._hits_keys = None
        self._tracks_keys = None
        self._mc_hits_keys = None
        self._mc_tracks_keys = None
        self._valid_keys = None

    def __repr__(self):
        return '\n'.join([
            "Events keys are:\n\t" + '\n\t'.join(self.events_keys),
            "Hits keys are:\n\t" + '\n\t'.join(self.hits_keys),
            "Tracks keys are:\n\t" + '\n\t'.join(self.tracks_keys),
            "Mc hits keys are:\n\t" + '\n\t'.join(self.mc_hits_keys),
            "Mc tracks keys are:\n\t" + '\n\t'.join(self.mc_tracks_keys)
        ])

    def __str__(self):
        return repr(self)

    @property
    def events_keys(self):
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
        if self._hits_keys is None:
            tree = uproot.open(self._file_path)['E']['hits']
            self._hits_keys = [key.decode('utf8') for key in tree.keys()]
        return self._hits_keys

    @property
    def tracks_keys(self):
        if self._tracks_keys is None:
            fake_branches = ['trks.usr_data',
                             'trks.usr_names']  # uproot can't read these
            tree = uproot.open(self._file_path)['E']['Evt']['trks']
            self._tracks_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._tracks_keys

    @property
    def mc_hits_keys(self):
        if self._mc_hits_keys is None:
            tree = uproot.open(self._file_path)['E']['Evt']['mc_hits']
            self._mc_hits_keys = [key.decode('utf8') for key in tree.keys()]
        return self._mc_hits_keys

    @property
    def mc_tracks_keys(self):
        if self._mc_tracks_keys is None:
            fake_branches = ['mc_trks.usr_data',
                             'mc_trks.usr_names']  # uproot can't read these
            tree = uproot.open(self._file_path)['E']['Evt']['mc_trks']
            self._mc_tracks_keys = [
                key.decode('utf8') for key in tree.keys()
                if key.decode('utf8') not in fake_branches
            ]
        return self._mc_tracks_keys

    @property
    def valid_keys(self):
        """constructs a list of all valid keys to be read from an Aanet event file.
        Returns
        -------
        list
            list of all valid keys.
    """
        if self._valid_keys is None:
            self._valid_keys = (self.events_keys + self.hits_keys +
                                self.tracks_keys + self.mc_tracks_keys +
                                self.mc_hits_keys)
        return self._valid_keys


class Reader(AanetKeys):
    """Reader for one Aanet ROOT file"""
    def __init__(self, file_path):
        """ AanetReader class is a Aanet ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        super().__init__(file_path)
        self._lazy_data = uproot.open(self._file_path)['E'].lazyarrays()

    def __getitem__(self, key):
        """reads data stored in the branch of interest in an event tree.

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
        KeyEroor
            Some branches in an Aanet file structure are "fake branches" and do
            not contain data. Therefore, the keys corresponding to these fake
            branches are not read.
        """
        if key not in self.valid_keys and not isinstance(key, int):
            raise KeyError(
                "'{}' is not a valid key or is a fake branch.".format(key))
        return self._lazy_data[key]


class AanetReader(AanetKeys):
    def __init__(self, file_path, data=None):
        """ AanetReader class is a Aanet ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        super().__init__(file_path)
        if data is not None:
            self._lazy_data = data
        else:
            self._lazy_data = uproot.open(self._file_path)['E'].lazyarrays()
        self._events = None
        self._hits = None
        self._tracks = None
        self._mc_hits = None
        self._mc_tracks = None

    # def __getitem__(self, item):
    #     return AanetEvents(self._events_keys, [self._lazy_data[key] for key in self.events])

    def __getitem__(self, item):
        return AanetReader(file_path=self._file_path,
                           data=self._lazy_data[item])

    @property
    def events(self):
        if self._events is None:
            self._events = AanetEvents(
                self.events_keys,
                [self._lazy_data[key] for key in self.events_keys])
        return self._events

    @property
    def hits(self):
        if self._hits is None:
            self._hits = AanetHits(
                self.hits_keys,
                [self._lazy_data[key] for key in self.hits_keys])
        return self._hits

    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = AanetTracks(
                self.tracks_keys,
                [self._lazy_data[key] for key in self.tracks_keys])
        return self._tracks

    @property
    def mc_hits(self):
        if self._mc_hits is None:
            self._mc_hits = AanetHits(
                self.mc_hits_keys,
                [self._lazy_data[key] for key in self.mc_hits_keys])
        return self._mc_hits

    @property
    def mc_tracks(self):
        if self._mc_tracks is None:
            self._mc_tracks = AanetTracks(
                self.mc_tracks_keys,
                [self._lazy_data[key] for key in self.mc_tracks_keys])
        return self._mc_tracks


class AanetEvents:
    "wrapper for Aanet events"

    def __init__(self, keys, values):  # values is a list of lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __getitem__(self, item):
        return AanetEvent(self._keys, [v[item] for v in self._values])

    def __len__(self):
        return len(
            self._values[0]
        )  # I don't like this being explicit, what if values is empty ...

    def __str__(self):
        return "Number of events: {}".format(len(self))

    def __repr__(self):
        return str(self)


class AanetEvent:
    "wrapper for an Aanet event"

    def __init__(self, keys, values):  # both inputs are lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k, v)

    def __str__(self):
        return "Aanet event:\n\t" + "\n\t".join([
            "{:15} {:^10} {:>10}".format(k, ':', str(v))
            for k, v in zip(self._keys, self._values)
        ])

    def __repr__(self):
        return str(self)


class AanetHits:
    "wrapper for Aanet hits, manages the display of all hits in one event"

    def __init__(self, keys, values):  # values is a list of lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k.split('hits.')[1].replace('.', '_'), v)

    def __getitem__(self, item):
        # return self._values[item]
        return AanetHit(self._keys, [v[item] for v in self._values])

    def __len__(self):
        return len(
            self._values[0]
        )  # I don't like this being explicit, what if values is empty ...

    def __str__(self):
        # hits
        if all(key.startswith('hits.') for key in self._keys):
            return "Number of hits in the selected event: {}".format(len(self))
        # mc hits
        if all(key.startswith('mc_hits.') for key in self._keys):
            return "Number of mc hits in the selected event: {}".format(
                len(self))

    def __repr__(self):
        return str(self)


class AanetHit:
    "wrapper for an Aanet hit"

    def __init__(self, keys, values):  # both inputs are lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k.split('hits.')[1].replace('.', '_'), v)

    def __str__(self):
        # hits
        if all(key.startswith('hits.') for key in self._keys):
            return "Aanet hit:\n\t" + "\n\t".join([
                "{:15} {:^10} {:>10}".format(
                    k.split('hits.')[1].replace('.', '_'), ':', str(v))
                for k, v in zip(self._keys, self._values)
            ])

        # mc hits
        if all(key.startswith('mc_hits.') for key in self._keys):
            return "Aanet mc hit:\n\t" + "\n\t".join([
                "{:15} {:^10} {:>10}".format(
                    k.split('mc_hits.')[1].replace('.', '_'), ':', str(v))
                for k, v in zip(self._keys, self._values)
            ])

    def __getitem__(self, item):
        # return self._values[item]
        return self._values[item]

    def __repr__(self):
        return str(self)


class AanetTracks:
    "wrapper for Aanet tracks, manages the display of all tracks in one event"

    def __init__(self, keys, values):  # values is a list of lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k.split('trks.')[1].replace('.', '_'), v)

    def __getitem__(self, item):
        # return self._values[item]
        return AanetTrack(self._keys, [v[item] for v in self._values])

    def __len__(self):
        return len(
            self._values[0]
        )  # I don't like this being explicit, what if values is empty ...

    def __str__(self):
        # hits
        if all(key.startswith('trks.') for key in self._keys):
            return "Number of tracks in the selected event: {}".format(
                len(self))
        # mc hits
        if all(key.startswith('mc_trks.') for key in self._keys):
            return "Number of mc tracks in the selected event: {}".format(
                len(self))

    def __repr__(self):
        return str(self)


class AanetTrack:
    "wrapper for an Aanet track"

    def __init__(self, keys, values):  # both inputs are lists
        self._keys = keys  # list of keys
        self._values = values
        for k, v in zip(self._keys, self._values):
            setattr(self, k.split('trks.')[1].replace('.', '_'), v)

    def __str__(self):
        # hits
        if all(key.startswith('trks.') for key in self._keys):
            return "Aanet track:\n\t" + "\n\t".join([
                "{:15} {:^10} {:>10}".format(
                    k.split('trks.')[1].replace('.', '_'), ':', str(v))
                for k, v in zip(self._keys, self._values)
            ])

        # mc hits
        if all(key.startswith('mc_trks.') for key in self._keys):
            return "Aanet mc track:\n\t" + "\n\t".join([
                "{:15} {:^10} {:>10}".format(
                    k.split('trks.')[1].replace('.', '_'), ':', str(v))
                for k, v in zip(self._keys, self._values)
            ])

    def __getitem__(self, item):
        # return self._values[item]
        return self._values[item]

    def __repr__(self):
        return str(self)