import binascii
from collections import namedtuple
import uproot
import numpy as np

import numba as nb

# Parameters for PMT rate conversions, since the rates in summary slices are
# stored as a single byte to save space. The values from 0-255 can be decoded
# using the `get_rate(value)` function, which will yield the actual rate
# in Hz.
MINIMAL_RATE_HZ = 2.0e3
MAXIMAL_RATE_HZ = 2.0e6
RATE_FACTOR = np.log(MAXIMAL_RATE_HZ / MINIMAL_RATE_HZ) / 255

CHANNEL_BITS_TEMPLATE = np.zeros(31, dtype=bool)


BranchConfiguration = namedtuple(
    field_names=["branch_address", "interpretation"], typename="BranchConfiguration"
)


class SummarysliceReader:
    """
    A reader for summaryslices which are loaded as chunks given by step_size.

    To be used as an iterator (`for chunks in SummarysliceReader(...): ...`)
    """

    TREE_ADDR = "KM3NET_SUMMARYSLICE/KM3NET_SUMMARYSLICE"
    _subbranches = [
        BranchConfiguration(
            "KM3NETDAQ::JDAQSummarysliceHeader",
            uproot.interpretation.numerical.AsDtype(
                [
                    (" cnt", "u4"),
                    (" vers", "u2"),
                    (" cnt2", "u4"),
                    (" vers2", "u2"),
                    (" cnt3", "u4"),
                    (" vers3", "u2"),
                    ("detector_id", ">i4"),
                    ("run", ">i4"),
                    ("frame_index", ">i4"),
                    (" cnt4", "u4"),
                    (" vers4", "u2"),
                    ("UTC_seconds", ">u4"),
                    ("UTC_16nanosecondcycles", ">u4"),
                ]
            ),
        ),
        BranchConfiguration(
            "vector<KM3NETDAQ::JDAQSummaryFrame>",
            uproot.interpretation.jagged.AsJagged(
                uproot.interpretation.numerical.AsDtype(
                    [
                        ("dom_id", ">i4"),
                        ("dq_status", ">u4"),
                        ("hrv", ">u4"),
                        ("fifo", ">u4"),
                        ("status3", ">u4"),
                        ("status4", ">u4"),
                    ]
                    + [(f"ch{c}", "u1") for c in range(31)]
                ),
                header_bytes=10,
            ),
        ),
    ]

    def __init__(self, fobj, step_size=1000):
        if isinstance(fobj, str):
            self._fobj = uproot.open(fobj)
        else:
            self._fobj = fobj
        self._step_size = step_size
        self._branch = self._fobj[self.TREE_ADDR]

        self.ChunksConstructor = namedtuple(
            field_names=["headers", "slices"], typename="SummarysliceChunk"
        )

    def _chunks_generator(self):
        for chunk in self._branch.iterate(
            dict(self._subbranches), step_size=self._step_size
        ):
            yield self.ChunksConstructor(
                *[getattr(chunk, bc.branch_address) for bc in self._subbranches]
            )

    def __getitem__(self, idx):
        if idx >= len(self) or idx < -len(self):
            raise IndexError("Chunk index out of range")

        s = self._step_size

        if idx < 0:
            idx = len(self) + idx

        chunk = self._branch.arrays(
            dict(self._subbranches), entry_start=idx * s, entry_stop=(idx + 1) * s
        )
        return self.ChunksConstructor(
            *[getattr(chunk, bc.branch_address) for bc in self._subbranches]
        )

    def __iter__(self):
        self._chunks = self._chunks_generator()
        return self

    def __next__(self):
        return next(self._chunks)

    def __len__(self):
        return int(np.ceil(self._branch.num_entries / self._step_size))

    def __repr__(self):
        step_size = self._step_size
        n_items = self._branch.num_entries
        cls_name = self.__class__.__name__
        n_chunks = len(self)
        return (
            f"<{cls_name} {n_items} items, step_size={step_size} "
            f"({n_chunks} chunk{'' if n_chunks == 1 else 's'})>"
        )


@nb.vectorize(
    [nb.int32(nb.int8), nb.int32(nb.int16), nb.int32(nb.int32), nb.int32(nb.int64)]
)
def get_rate(value):  # pragma: no cover
    """Return the rate in Hz from the short int value"""
    if value == 0:
        return 0
    else:
        return MINIMAL_RATE_HZ * np.exp(value * RATE_FACTOR)


@nb.guvectorize(
    "void(i8, b1[:], b1[:])", "(), (n) -> (n)", target="parallel", nopython=True
)
def unpack_bits(value, bits_template, out):  # pragma: no cover
    """Return a boolean array for a value's bit representation.

    This function also accepts arrays as input, the output shape will be
    NxM where N is the number of input values and M the length of the
    ``bits_template`` array, which is just a dummy array, due to the weird
    signature system of numba.

    Parameters
    ----------
    value: int or np.array(int) with shape (N,)
        The binary value of containing the bit information
    bits_template: np.array() with shape (M,)
        The template for the output array, the only important is its shape

    Returns
    -------
    np.array(bool) either with shape (M,) or (N, M)
    """
    for i in range(bits_template.shape[0]):
        out[30 - i] = value & (1 << i) > 0


def get_channel_flags(value):
    """Returns the hrv/fifo flags for the PMT channels (hrv/fifo)

    Parameters
    ----------
    value : int32
        The integer value to be parsed.
    """
    channel_bits = np.bitwise_and(value, 0x7FFFFFFF)
    flags = unpack_bits(channel_bits, CHANNEL_BITS_TEMPLATE)
    return np.flip(flags, axis=-1)


def get_number_udp_packets(value):
    """Returns the number of received UDP packets (dq_status)

    Parameters
    ----------
    value : int32
        The integer value to be parsed.
    """
    return np.bitwise_and(value, 0x7FFF)


def get_udp_max_sequence_number(value):
    """Returns the maximum sequence number of the received UDP packets (dq_status)

    Parameters
    ----------
    value : int32
        The integer value to be parsed.
    """
    return np.right_shift(value, 16)


def has_udp_trailer(value):
    """Returns the UDP Trailer flag (fifo)

    Parameters
    ----------
    value : int32
        The integer value to be parsed.
    """
    return np.any(np.bitwise_and(value, np.left_shift(1, 31)))


class OnlineReader:
    """Reader for online ROOT files"""

    def __init__(self, filename):
        self._fobj = uproot.open(filename)
        self._filename = filename
        self._events = None
        self._timeslices = None
        self._summaryslices = None
        self._uuid = self._fobj.parent.uuid.hex

    @property
    def uuid(self):
        return self._uuid

    def close(self):
        self._fobj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def events(self):
        if self._events is None:
            tree = self._fobj["KM3NET_EVENT"]

            headers = tree["KM3NETDAQ::JDAQEventHeader"].array(
                uproot3.interpret(tree["KM3NETDAQ::JDAQEventHeader"], cntvers=True)
            )
            snapshot_hits = tree["snapshotHits"].array(
                uproot3.asjagged(
                    uproot3.astable(
                        uproot3.asdtype(
                            [
                                ("dom_id", ">i4"),
                                ("channel_id", "u1"),
                                ("time", "<u4"),
                                ("tot", "u1"),
                            ]
                        )
                    ),
                    skipbytes=10,
                )
            )
            triggered_hits = tree["triggeredHits"].array(
                uproot3.asjagged(
                    uproot3.astable(
                        uproot3.asdtype(
                            [
                                ("dom_id", ">i4"),
                                ("channel_id", "u1"),
                                ("time", "<u4"),
                                ("tot", "u1"),
                                (" cnt", "u4"),
                                (" vers", "u2"),
                                ("trigger_mask", ">u8"),
                            ]
                        )
                    ),
                    skipbytes=10,
                )
            )
            self._events = OnlineEvents(headers, snapshot_hits, triggered_hits)
        return self._events

    @property
    def summaryslices(self):
        if self._summaryslices is None:
            self._summaryslices = SummarysliceReader(
                uproot.open(self._filename)
            )  # TODO: remove when using uproot4
        return self._summaryslices


class OnlineEvents:
    """A simple wrapper for online events"""

    def __init__(self, headers, snapshot_hits, triggered_hits):
        self.headers = headers
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __getitem__(self, item):
        return OnlineEvent(
            self.headers[item], self.snapshot_hits[item], self.triggered_hits[item]
        )

    def __len__(self):
        return len(self.headers)

    def __str__(self):
        return "Number of events: {}".format(len(self.headers))

    def __repr__(self):
        return str(self)


class OnlineEvent:
    """A wrapper for a online event"""

    def __init__(self, header, snapshot_hits, triggered_hits):
        self.header = header
        self.snapshot_hits = snapshot_hits
        self.triggered_hits = triggered_hits

    def __str__(self):
        return "Online event with {} snapshot hits and {} triggered hits".format(
            len(self.snapshot_hits), len(self.triggered_hits)
        )

    def __repr__(self):
        return str(self)
