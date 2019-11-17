import uproot

class AanetReader:

    def __init__(self, file_path):
        """Summary
        
        Parameters
        ----------
        file_path : path-like object
            Description
        """
        self.file_path = file_path
        self.data = uproot.open(self.file_path)['E']
        self.lazy_data = self.data.lazyarrays()
        self._events_keys = None
        self._hits_keys = None
        self._tracks_keys = None

    def read_event(self, key):
        """event_reader function reads data stored in a branch of interest in an event tree.
        
        Parameters
        ----------
        key : str
            name of the branch of interest in event data.
        
        Returns
        -------
        lazyarray
            Lazyarray of all data stored in a branch of interest (in an event tree). A lazyarray is an array-like
            object that reads data on demand. Here, only the first and last chunks of data are 
            read in memory, and not all data in the array. The output of event_reader can be used
            with all `Numpy's universal functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`.
        
        Raises
        ------
        NameError
            Some branches in an Aanet file structure are "fake branches" and do not contain data. Therefore,
            the keys corresponding to these fake branches are not read.
        """
        if key not in self.events_keys:
            raise KeyError(f"'{key}' is not a valid events key or is a fake branch.")
        evt_key_lazy = self.lazy_data[key]
        return evt_key_lazy
            
            
    def read_hits(self, key):
        """hits_reader function reads data stored in a branch of interest in hits tree from an Aanet
        event file.
        
        Parameters
        ----------
        hits_key : str
            name of the branch of interest in hits tree.
        
        Returns
        -------
        lazyarray
            Lazyarray of all data stored in a branch of interest (in hits tree). A lazyarray is an array-like
            object that reads data on demand. Here, only the first and last chunks of data are 
            read in memory, and not all data in the array. The output of event_reader can be used
            with all `Numpy's universal functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`.
        
        Raises
        ------
        NameError
            the hits.key stored in an Aanet file must be used to access the branch of interest
            from hits tree data.
        """
        if key not in self.hits_keys:
            raise KeyError(f"'{key}' is not a valid hits key.")
        hits_key_lazy = self.lazy_data[key]
        return hits_key_lazy
            

    def read_tracks(self, key):
        """tracks_reader function reads data stored in a branch of interest in tracks tree
        from an Aanet event file.
        
        Parameters
        ----------
        tracks_key : str
            name of the branch of interest in tracks tree.
        
        Returns
        -------
        lazyarray
            Lazyarray of all data stored in a branch of interest (in tracks tree). A lazyarray is an array-like
            object that reads data on demand. Here, only the first and last chunks of data are 
            read in memory, and not all data in the array. The output of event_reader can be used
            with all `Numpy's universal functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`.
        
        Raises
        ------
        NameError
            the trks.key stored in an Aanet file must be used to access the branch of interest
            from tracks tree data.
        """
        if key not in self.tracks_keys:
            raise KeyError(f"'{key}' is not a valid tracks key.")
        tracks_key_lazy = self.lazy_data[key]
        return tracks_key_lazy

    @property
    def events_keys(self):
        """_event_keys function returns a list of all the keys of interest
            for data analysis, and removes the keys of empty "fake branches" 
            found in Aanet event files. 
        
        Parameters
        ----------
        evt_tree : aanet event (Evt) tree.
        
        Returns
        -------
        list of str
            list of all the event keys.
        """
        if self._events_keys is None:
            fake_branches = ['Evt', 'AAObject', 'TObject','t']
            t_baskets = ['t.fSec', 't.fNanoSec']
            self._events_keys = [key.decode('utf-8') for key in self.data['Evt'].keys() if key.decode('utf-8') not in fake_branches] + t_baskets
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
            self._tracks_keys = [key.decode('utf8') for key in tracks_tree.keys()]
        return self._tracks_keys
