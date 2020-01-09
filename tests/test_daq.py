import os
import re
import unittest

from km3io.daq import DAQReader, get_rate

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


class TestDAQEvents(unittest.TestCase):
    def setUp(self):
        self.events = DAQReader(os.path.join(SAMPLES_DIR,
                                             "daq_v1.0.0.root")).events

    def test_index_lookup(self):
        assert 3 == len(self.events)

    def test_str(self):
        assert re.match(".*events.*3", str(self.events))

    def test_repr(self):
        assert re.match(".*events.*3", self.events.__repr__())


class TestDAQEvent(unittest.TestCase):
    def setUp(self):
        self.event = DAQReader(os.path.join(SAMPLES_DIR,
                                            "daq_v1.0.0.root")).events[0]

    def test_str(self):
        assert re.match(".*event.*96.*snapshot.*18.*triggered",
                        str(self.event))

    def test_repr(self):
        assert re.match(".*event.*96.*snapshot.*18.*triggered",
                        self.event.__repr__())


class TestDAQEventsSnapshotHits(unittest.TestCase):
    def setUp(self):
        self.events = DAQReader(os.path.join(SAMPLES_DIR,
                                             "daq_v1.0.0.root")).events
        self.lengths = {0: 96, 1: 124, -1: 78}
        self.total_item_count = 298

    def test_reading_snapshot_hits(self):
        hits = self.events.snapshot_hits

        for event_id, length in self.lengths.items():
            assert length == len(hits[event_id].dom_id)
            assert length == len(hits[event_id].channel_id)
            assert length == len(hits[event_id].time)

    def test_total_item_counts(self):
        hits = self.events.snapshot_hits

        assert self.total_item_count == sum(hits.dom_id.count())
        assert self.total_item_count == sum(hits.channel_id.count())
        assert self.total_item_count == sum(hits.time.count())

    def test_data_values(self):
        hits = self.events.snapshot_hits

        self.assertListEqual([806451572, 806451572, 806455814],
                             list(hits.dom_id[0][:3]))
        self.assertListEqual([10, 13, 0], list(hits.channel_id[0][:3]))
        self.assertListEqual([1593234433, 1559680001, 3371422721],
                             list(hits.time[0][:3]))

    def test_channel_ids_have_valid_values(self):
        hits = self.events.snapshot_hits

        # channel IDs are always between [0, 30]
        assert all(c >= 0 for c in hits.channel_id.min())
        assert all(c < 31 for c in hits.channel_id.max())


class TestDAQEventsTriggeredHits(unittest.TestCase):
    def setUp(self):
        self.events = DAQReader(os.path.join(SAMPLES_DIR,
                                             "daq_v1.0.0.root")).events
        self.lengths = {0: 18, 1: 53, -1: 9}
        self.total_item_count = 80

    def test_data_lengths(self):
        hits = self.events.triggered_hits

        for event_id, length in self.lengths.items():
            assert length == len(hits[event_id].dom_id)
            assert length == len(hits[event_id].channel_id)
            assert length == len(hits[event_id].time)
            assert length == len(hits[event_id].trigger_mask)

    def test_total_item_counts(self):
        hits = self.events.triggered_hits

        assert self.total_item_count == sum(hits.dom_id.count())
        assert self.total_item_count == sum(hits.channel_id.count())
        assert self.total_item_count == sum(hits.time.count())

    def test_data_values(self):
        hits = self.events.triggered_hits

        self.assertListEqual([806451572, 806451572, 808432835],
                             list(hits.dom_id[0][:3]))
        self.assertListEqual([10, 13, 1], list(hits.channel_id[0][:3]))
        self.assertListEqual([1593234433, 1559680001, 1978979329],
                             list(hits.time[0][:3]))
        self.assertListEqual([16, 16, 4], list(hits.trigger_mask[0][:3]))

    def test_channel_ids_have_valid_values(self):
        hits = self.events.triggered_hits

        # channel IDs are always between [0, 30]
        assert all(c >= 0 for c in hits.channel_id.min())
        assert all(c < 31 for c in hits.channel_id.max())


class TestDAQTimeslices(unittest.TestCase):
    def setUp(self):
        self.ts = DAQReader(os.path.join(SAMPLES_DIR,
                                         "daq_v1.0.0.root")).timeslices

    def test_data_lengths(self):
        assert 3 == len(self.ts._timeslices["L1"][0])
        assert 3 == len(self.ts._timeslices["SN"][0])
        with self.assertRaises(KeyError):
            assert 0 == len(self.ts._timeslices["L2"][0])
        with self.assertRaises(KeyError):
            assert 0 == len(self.ts._timeslices["L0"][0])

    def test_streams(self):
        self.ts.stream("L1", 0)
        self.ts.stream("SN", 0)

    def test_reading_frames(self):
        assert 8 == len(self.ts.stream("SN", 1).frames[808447186])

    def test_str(self):
        s = str(self.ts)
        assert "L1" in s
        assert "SN" in s


class TestDAQTimeslice(unittest.TestCase):
    def setUp(self):
        self.ts = DAQReader(os.path.join(SAMPLES_DIR,
                                         "daq_v1.0.0.root")).timeslices
        self.n_frames = {"L1": [69, 69, 69], "SN": [64, 66, 68]}

    def test_str(self):
        for stream, n_frames in self.n_frames.items():
            print(stream, n_frames)
            for i in range(len(n_frames)):
                s = str(self.ts.stream(stream, i))
                assert re.match("{}.*{}".format(stream, n_frames[i]), s)


class TestSummaryslices(unittest.TestCase):
    def setUp(self):
        self.ss = DAQReader(os.path.join(SAMPLES_DIR,
                                         "daq_v1.0.0.root")).summaryslices

    def test_headers(self):
        assert 3 == len(self.ss.headers)
        self.assertListEqual([44, 44, 44], list(self.ss.headers.detector_id))
        self.assertListEqual([6633, 6633, 6633], list(self.ss.headers.run))
        self.assertListEqual([126, 127, 128],
                             list(self.ss.headers.frame_index))
        assert 806451572 == self.ss.slices[0].dom_id[0]

    def test_slices(self):
        assert 3 == len(self.ss.slices)

    def test_rates(self):
        assert 3 == len(self.ss.rates)


class TestGetReate(unittest.TestCase):
    def test_zero(self):
        assert 0 == get_rate(0)

    def test_some_values(self):
        assert 2054 == get_rate(1)
        assert 55987 == get_rate(123)
        assert 1999999 == get_rate(255)

    def test_vectorized_input(self):
        self.assertListEqual([2054], list(get_rate([1])))
        self.assertListEqual([2054, 2111, 2169], list(get_rate([1,2,3])))
