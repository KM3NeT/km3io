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
            tree = uproot.open(self._file_path)['E']['Evt']['trks']
            self._tracks_keys = [key.decode('utf8') for key in tree.keys()]
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
            tree = uproot.open(self._file_path)['E']['Evt']['mc_trks']
            self._mc_tracks_keys = [key.decode('utf8') for key in tree.keys()]
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
            self._valid_keys = self.events_keys + self.hits_keys + self.tracks_keys + self.mc_tracks_keys + self.mc_hits_keys
        return self._valid_keys


class AanetReader(AanetKeys):
    """Reader for one Aanet ROOT file"""
    def __init__(self, file_path):
        """ AanetReader class is a Aanet ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        self._file_path = file_path
        self._lazy_data = uproot.open(self._file_path)['E'].lazyarrays()
        self._events_keys = None
        self._hits_keys = None
        self._tracks_keys = None
        self._mc_hits_keys = None
        self._mc_tracks_keys = None
        self._valid_keys = None

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


class AanetEvents():
    "wrapper for Aanet events"
    def __init__(self, run_id, det_id, frame_index, trigger_mask, trigger_counter, overlays):
        self.det_id = det_id
        self.run_id = run_id
        self.frame_index = frame_index
        self.trigger_mask = trigger_mask
        self.trigger_counter = trigger_counter
        self.overlays = overlays

    def __getitem__(self, item):
        return AanetEvent(self.run_id[item], self.det_id[item], self.frame_index[item], self.trigger_mask[item], self.trigger_counter[item], self.overlays[item])

    def __len__(self):
        return len(self.overlays)

    def __str__(self):
        return "Number of events: {}".format(len(self.overlays))

    def __repr__(self):
        return str(self)


class AanetEvent():
    "wrapper for an Aanet event"
    def __init__(self, run_id, det_id, frame_index, trigger_mask, trigger_counter, overlays):
        self.det_id = det_id
        self.run_id = run_id
        self.frame_index = frame_index
        self.trigger_mask = trigger_mask
        self.trigger_counter = trigger_counter
        self.overlays = overlays

    def __str__(self):
        return "\n\t".join([
            "Aanet event     :\n",
            "detector id     : {:>10}".format(self.det_id),
            "run id          : {:>10}".format(self.run_id),
            "frame index     : {:>10}".format(self.frame_index),
            "trigger mask    : {:>10}".format(self.trigger_mask),
            "trigger counter : {:>10}".format(self.trigger_counter),
            "overlays        : {:>10}".format(self.overlays)])

    def __repr__(self):
        return str(self)


class AanetHits:
    "wrapper for Aanet hits"
    def __init__(self, run_id, det_id, frame_index, trigger_mask, trigger_counter, overlays):
        self.det_id = det_id
        self.run_id = run_id
        self.frame_index = frame_index
        self.trigger_mask = trigger_mask
        self.trigger_counter = trigger_counter
        self.overlays = overlays

    def __getitem__(self, item):
        return AanetEvent(self.run_id[item], self.det_id[item], self.frame_index[item], self.trigger_mask[item], self.trigger_counter[item], self.overlays[item])

    def __len__(self):
        return len(self.overlays)

    def __str__(self):
        return "Number of events: {}".format(len(self.overlays))

    def __repr__(self):
        return str(self)


class AanetHit:
    "wrapper for an Aanet hit"
    def __init__(self):
        stm

    def __str__(self):
        return "\n\t".join([
            "Aanet event:\n",
            "detector id: {}".format(self.det_id),
            "run id: {}".format(self.run_id),
            "frame index: {}".format(self.frame_index),
            "trigger mask: {}".format(self.trigger_mask),
            "trigger counter: {}".format(self.trigger_counter),
            "overlays: {}".format(self.overlays)])

    def __repr__(self):
        return str(self)
# class AanetMcEvent:
#     "A simple wrapper for an Aanet Mc Event"
        # self.id = id
        # self.id = id
        # self.det_id = det_id
        # self.run_id = run_id
        # self.frame_index = frame_index
        # self.trigger_mask = trigger_mask
        # self.trigger_counter = trigger_counter
        # self.overlays = overlays
        # self.hits = hits
        # self.trks = trks
        # self.w = w
        # self.w2list = w2list
        # self.w3list = w3list
        # self.comment = comment
        # self.index = index
        # self.flags = flags
        # self.t_fSec = t_fSec
        # self.t_fNanoSec = t_fNanoSec