import uproot

class DataReader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = uproot.open(self.file_path)['E']
        self.lazy_data = self.data.lazyarrays()

    def event_reader(self, key):
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
        evt_tree = self.data['Evt']
        evt_keys = self._event_keys(evt_tree)
        if key in evt_keys:
            evt_key_lazy = self.lazy_data[key]
            return evt_key_lazy
        else:
            raise NameError("The event key must be one of the following: 'id', 'det_id', 'mc_id', 'run_id', 'mc_run_id', 'frame_index', 'trigger_mask', 'trigger_counter', 'overlays', 'hits', 'trks', 'w', 'w2list', 'w3list', 'mc_t', 'mc_hits', 'mc_trks', 'comment', 'index', 'flags', 't.fSec', 't.fNanoSec' ")

    def _event_keys(self, evt_tree):
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
        fake_branches = ['Evt', 'AAObject', 'TObject','t']
        t_baskets = ['t.fSec', 't.fNanoSec']
        # 
        all_keys_evt = [key.decode('utf-8') for key in evt_tree.keys() if key.decode('utf-8') not in fake_branches] + t_baskets
        return all_keys_evt

    def hits_reader(self, hits_key):
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
        hits_tree = self.data['Evt']['hits']
        hits_keys = [key.decode('utf8') for key in hits_tree.keys()]
        if hits_key in hits_keys:
            hits_key_lazy = self.lazy_data[hits_key]
            return hits_key_lazy
        else:
            raise NameError("The hits key must be one of the following: 'hits.fUniqueID', 'hits.fBits', 'hits.usr', 'hits.usr_names', 'hits.id', 'hits.dom_id', 'hits.channel_id', 'hits.tdc', 'hits.tot', 'hits.trig', 'hits.pmt_id', 'hits.t', 'hits.a', 'hits.pos.x', 'hits.pos.y', 'hits.pos.z', 'hits.dir.x', 'hits.dir.y', 'hits.dir.z', 'hits.pure_t', 'hits.pure_a', 'hits.type', 'hits.origin', 'hits.pattern_flags'")

    def tracks_reader(self, tracks_key ):
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
        tracks_tree = self.data['Evt']['trks']
        tracks_keys = [key.decode('utf8') for key in tracks_tree.keys()]
        if tracks_key in tracks_keys:
            tracks_key_lazy = self.lazy_data[tracks_key]
            return tracks_key_lazy
        else:
            raise NameError("The tracks key must be one the following: 'trks.fUniqueID', 'trks.fBits', 'trks.usr', 'trks.usr_names', 'trks.id', 'trks.pos.x', 'trks.pos.y', 'trks.pos.z', 'trks.dir.x', 'trks.dir.y', 'trks.dir.z', 'trks.t', 'trks.E', 'trks.len', 'trks.lik', 'trks.type', 'trks.rec_type', 'trks.rec_stages', 'trks.fitinf', 'trks.hit_ids', 'trks.error_matrix', 'trks.comment'")

  

