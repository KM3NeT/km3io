import uproot

TIMESLICE_FRAME_BASKET_CACHE_SIZE = 23 * 1024**2  # [byte]


class JppReader:
    """Reader for Jpp ROOT files"""
    def __init__(self, filename):
        self.fobj = uproot.open(filename)
        self._events = None
        self._timeslices = None

    @property
    def events(self):
        if self._events is None:
            tree = self.fobj["KM3NET_EVENT"]

            headers = tree["KM3NETDAQ::JDAQEventHeader"].array(
                uproot.interpret(tree["KM3NETDAQ::JDAQEventHeader"],
                                 cntvers=True))
            snapshot_hits = tree["snapshotHits"].array(
                uproot.asjagged(uproot.astable(
                    uproot.asdtype([("dom_id", "i4"), ("channel_id", "u1"),
                                    ("time", "u4"), ("tot", "u1")])),
                                skipbytes=10))
            triggered_hits = tree["triggeredHits"].array(
                uproot.asjagged(uproot.astable(
                    uproot.asdtype([("dom_id", "i4"), ("channel_id", "u1"),
                                    ("time", "u4"), ("tot", "u1"),
                                    (" cnt", "u4"), (" vers", "u2"),
                                    ("trigger_mask", "u8")])),
                                skipbytes=10))
            self._events = JppEvents(headers, snapshot_hits, triggered_hits)
        return self._events

    @property
    def timeslices(self):
        if self._timeslices is None:
            self._timeslices = JppTimeslices(self.fobj)
        return self._timeslices


class JppTimeslices:
    """A simple wrapper for Jpp timeslices"""
    def __init__(self, fobj):
        self.fobj = fobj
        self._timeslices = {}
        self._read_default_stream()
        self._read_streams()

    def _read_default_stream(self):
        """Read the default KM3NET_TIMESLICE stream"""
        tree = self.fobj[b'KM3NET_TIMESLICE'][b'KM3NET_TIMESLICE']
        headers = tree[b'KM3NETDAQ::JDAQTimesliceHeader']
        superframes = tree[b'vector<KM3NETDAQ::JDAQSuperFrame>']
        self._timeslices['default'] = (headers, superframes)

    def _read_streams(self):
        """Read the L0, L1, L2 and SN streams if available"""
        streams = [
            s.split(b"KM3NET_TIMESLICE_")[1].split(b';')[0]
            for s in self.fobj.keys() if b"KM3NET_TIMESLICE_" in s
        ]
        for stream in streams:
            tree = self.fobj[b'KM3NET_TIMESLICE_' +
                             stream][b'KM3NETDAQ::JDAQTimeslice']
            headers = tree[b'KM3NETDAQ::JDAQTimesliceHeader'][
                b'KM3NETDAQ::JDAQHeader'][b'KM3NETDAQ::JDAQChronometer']
            if len(headers) == 0:
                continue
            superframes = tree[b'vector<KM3NETDAQ::JDAQSuperFrame>']
            hits_buffer = superframes[
                b'vector<KM3NETDAQ::JDAQSuperFrame>.buffer'].lazyarray(
                    uproot.asjagged(uproot.astable(
                        uproot.asdtype([("pmt", "u1"), ("tdc", "u4"),
                                        ("tot", "u1")])),
                                    skipbytes=6),
                    basketcache=uproot.cache.ThreadSafeArrayCache(
                        TIMESLICE_FRAME_BASKET_CACHE_SIZE))
            self._timeslices[stream.decode("ascii")] = (headers, superframes,
                                                        hits_buffer)

    def stream(self, stream, idx):
        ts = self._timeslices[stream]
        return JppTimeslice(*ts, idx, stream)

    def __str__(self):
        return "Available timeslice streams: {}".format(', '.join(
            s for s in self._timeslices.keys()))

    def __repr__(self):
        return str(self)


class JppTimeslice:
    """A wrapper for a Jpp timeslice"""
    def __init__(self, header, superframe, hits_buffer, idx, stream):
        self.header = header
        self._frames = {}
        self._superframe = superframe
        self._hits_buffer = hits_buffer
        self._idx = idx
        self._stream = stream
        self._n_frames = None

    @property
    def frames(self):
        if not self._frames:
            self._read_frames()
        return self._frames

    def _read_frames(self):
        """Populate a dictionary of frames with the module ID as key"""
        hits_buffer = self._hits_buffer[self._idx]
        n_hits = self._superframe[
            b'vector<KM3NETDAQ::JDAQSuperFrame>.numberOfHits'].lazyarray()[
                self._idx]
        module_ids = self._superframe[
            b'vector<KM3NETDAQ::JDAQSuperFrame>.id'].lazyarray()[self._idx]
        idx = 0
        for module_id, n_hits in zip(module_ids, n_hits):
            self._frames[module_id] = hits_buffer[idx:idx + n_hits]
            idx += n_hits

    def __len__(self):
        if self._n_frames is None:
            self._n_frames = len(
                self._superframe[b'vector<KM3NETDAQ::JDAQSuperFrame>.id'].
                lazyarray()[self._idx])
        return self._n_frames

    def __str__(self):
        return "{} timeslice with {} frames.".format(self._stream, len(self))

    def __repr__(self):
        return "<{}: {} entries>".format(self.__class__.__name__,
                                         len(self.header))


class JppEvents:
    """A simple wrapper for Jpp events"""
    def __init__(self, headers, snapshot_hits, triggered_hits):
        self.headers = headers
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __getitem__(self, item):
        return JppEvent(self.headers[item], self.snapshot_hits[item],
                        self.triggered_hits[item])

    def __len__(self):
        return len(self.headers)

    def __str__(self):
        return "Number of events: {}".format(len(self.headers))

    def __repr__(self):
        return str(self)


class JppEvent:
    """A wrapper for a Jpp event"""
    def __init__(self, header, snapshot_hits, triggered_hits):
        self.header = header
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __str__(self):
        return "Jpp event with {} snapshot hits and {} triggered hits".format(
            len(self.snapshot_hits), len(self.triggered_hits))

    def __repr__(self):
        return str(self)
