import uproot


class AanetReader:
    """Reader for one Aanet ROOT file"""
    def __init__(self, file_path):
        """ AanetReader class is a Aanet ROOT file wrapper

        Parameters
        ----------
        file_path : path-like object
            Path to the file of interest. It can be a str or any python
            path-like object that points to the file of ineterst.
        """
        self.file_path = file_path
        self.data = uproot.open(self.file_path)['E']
        self.lazy_data = self.data.lazyarrays()
        self._events_keys = None
        self._hits_keys = None
        self._tracks_keys = None

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
        if key not in self.keys() and not isinstance(key, int):
            raise KeyError(
                "'{}' is not a valid key or is a fake branch.".format(key))
        return self.lazy_data[key]

    def __len__(self):
        return len(self.lazy_data)

    def __repr__(self):
        return '\n'.join([
            "Number of events: {}".format(self.__len__()),
            "Events keys are:\n\t" + '\n\t'.join(self.events_keys),
            "Hits keys are:\n\t" + '\n\t'.join(self.hits_keys),
            "Tracks keys are:\n\t" + '\n\t'.join(self.tracks_keys)
        ])

    def keys(self):
        """constructs a list of all valid keys to be read from an Aanet event file.

        Returns
        -------
        list
            list of all valid keys.
        """
        return self.events_keys + self.hits_keys + self.tracks_keys

    @property
    def events_keys(self):
        if self._events_keys is None:
            fake_branches = ['Evt', 'AAObject', 'TObject', 't']
            t_baskets = ['t.fSec', 't.fNanoSec']
            self._events_keys = [
                key.decode('utf-8') for key in self.data['Evt'].keys()
                if key.decode('utf-8') not in fake_branches
            ] + t_baskets
        return self._events_keys

    @property
    def hits_keys(self):
        if self._hits_keys is None:
            hits_tree = self.data['Evt']['hits']
            self._hits_keys = [key.decode('utf8') for key in hits_tree.keys()]
        return self._hits_keys

    @property
    def tracks_keys(self):
        if self._tracks_keys is None:
            tracks_tree = self.data['Evt']['trks']
            self._tracks_keys = [
                key.decode('utf8') for key in tracks_tree.keys()
            ]
        return self._tracks_keys
