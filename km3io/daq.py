import uproot
import numpy as np
import numba as nb

TIMESLICE_FRAME_BASKET_CACHE_SIZE = 23 * 1024**2  # [byte]
SUMMARYSLICE_FRAME_BASKET_CACHE_SIZE = 523 * 1024**2  # [byte]

# Parameters for PMT rate conversions, since the rates in summary slices are
# stored as a single byte to save space. The values from 0-255 can be decoded
# using the `get_rate(value)` function, which will yield the actual rate
# in Hz.
MINIMAL_RATE_HZ = 2.0e3
MAXIMAL_RATE_HZ = 2.0e6
RATE_FACTOR = np.log(MAXIMAL_RATE_HZ / MINIMAL_RATE_HZ) / 255


@nb.vectorize([
    nb.int32(nb.int8),
    nb.int32(nb.int16),
    nb.int32(nb.int32),
    nb.int32(nb.int64)
])
def get_rate(value):
    """Return the rate in Hz from the short int value"""
    if value == 0:
        return 0
    else:
        return MINIMAL_RATE_HZ * np.exp(value * RATE_FACTOR)


class DAQReader:
    """Reader for DAQ ROOT files"""
    def __init__(self, filename):
        self.fobj = uproot.open(filename)
        self._events = None
        self._timeslices = None
        self._summaryslices = None

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
            self._events = DAQEvents(headers, snapshot_hits, triggered_hits)
        return self._events

    @property
    def timeslices(self):
        if self._timeslices is None:
            self._timeslices = DAQTimeslices(self.fobj)
        return self._timeslices

    @property
    def summaryslices(self):
        if self._summaryslices is None:
            self._summaryslices = SummmarySlices(self.fobj)
        return self._summaryslices


class SummmarySlices:
    """A wrapper for summary slices"""
    def __init__(self, fobj):
        self.fobj = fobj
        self._slices = None
        self._headers = None
        self._rates = None
        self._ch_selector = ["ch{}".format(c) for c in range(31)]

    @property
    def headers(self):
        if self._headers is None:
            self._headers = self._read_headers()
        return self._headers

    @property
    def slices(self):
        if self._slices is None:
            self._slices = self._read_summaryslices()
        return self._slices

    @property
    def rates(self):
        if self._rates is None:
            self._rates = self.slices[["dom_id"] + self._ch_selector]
        return self._rates

    def _read_summaryslices(self):
        """Reads a lazyarray of summary slices"""
        tree = self.fobj[b'KM3NET_SUMMARYSLICE'][b'KM3NET_SUMMARYSLICE']
        return tree[b'vector<KM3NETDAQ::JDAQSummaryFrame>'].lazyarray(
            uproot.asjagged(uproot.astable(
                uproot.asdtype([("dom_id", "i4"), ("dq_status", "u4"),
                                ("hrv", "u4"), ("fifo", "u4"),
                                ("status3", "u4"), ("status4", "u4")] +
                               [(c, "u1") for c in self._ch_selector])),
                            skipbytes=10),
            basketcache=uproot.cache.ThreadSafeArrayCache(
                SUMMARYSLICE_FRAME_BASKET_CACHE_SIZE))

    def _read_headers(self):
        """Reads a lazyarray of summary slice headers"""
        tree = self.fobj[b'KM3NET_SUMMARYSLICE'][b'KM3NET_SUMMARYSLICE']
        return tree[b'KM3NETDAQ::JDAQSummarysliceHeader'].lazyarray(
            uproot.interpret(tree[b'KM3NETDAQ::JDAQSummarysliceHeader'],
                             cntvers=True))


class DAQTimeslices:
    """A simple wrapper for DAQ timeslices"""
    def __init__(self, fobj):
        self.fobj = fobj
        self._timeslices = {}
        self._read_streams()

    def _read_streams(self):
        """Read the L0, L1, L2 and SN streams if available"""
        streams = set(
            s.split(b"KM3NET_TIMESLICE_")[1].split(b';')[0]
            for s in self.fobj.keys() if b"KM3NET_TIMESLICE_" in s)
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
        return DAQTimeslice(*ts, idx, stream)

    def __str__(self):
        return "Available timeslice streams: {}".format(', '.join(
            s for s in self._timeslices.keys()))

    def __repr__(self):
        return str(self)


class DAQTimeslice:
    """A wrapper for a DAQ timeslice"""
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


class DAQEvents:
    """A simple wrapper for DAQ events"""
    def __init__(self, headers, snapshot_hits, triggered_hits):
        self.headers = headers
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __getitem__(self, item):
        return DAQEvent(self.headers[item], self.snapshot_hits[item],
                        self.triggered_hits[item])

    def __len__(self):
        return len(self.headers)

    def __str__(self):
        return "Number of events: {}".format(len(self.headers))

    def __repr__(self):
        return str(self)


class DAQEvent:
    """A wrapper for a DAQ event"""
    def __init__(self, header, snapshot_hits, triggered_hits):
        self.header = header
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __str__(self):
        return "DAQ event with {} snapshot hits and {} triggered hits".format(
            len(self.snapshot_hits), len(self.triggered_hits))

    def __repr__(self):
        return str(self)
