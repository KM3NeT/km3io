import uproot


class JppReader:
    """Reader for Jpp ROOT files"""
    def __init__(self, filename):
        self.fobj = uproot.open(filename)
        self._events = None

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
