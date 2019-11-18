import uproot


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
        header = tree[b'KM3NETDAQ::JDAQTimesliceHeader']
        self._timeslices['default'] = JppTimeslice(header)

    def _read_streams(self):
        """Read the L0, L1, L2 and SN streams if available"""
        streams = [
            s.split(b"KM3NET_TIMESLICE_")[1].split(b';')[0]
            for s in self.fobj.keys() if b"KM3NET_TIMESLICE_" in s
        ]
        for stream in streams:
            tree = self.fobj[b'KM3NET_TIMESLICE_' +
                             stream][b'KM3NETDAQ::JDAQTimeslice']
            header = tree[b'KM3NETDAQ::JDAQTimesliceHeader'][
                b'KM3NETDAQ::JDAQHeader'][b'KM3NETDAQ::JDAQChronometer']
            self._timeslices[stream.decode("ascii")] = JppTimeslice(header)

    def __str__(self):
        return "Available timeslice streams: {}".format(','.join(
            s.decode("ascii") for s in self._timeslices.keys()))

    def __repr__(self):
        return str(self)


class JppTimeslice:
    """A wrapper for a Jpp timeslice"""
    def __init__(self, header):
        self.header = header

    def __str__(self):
        return "Jpp timeslice"

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
