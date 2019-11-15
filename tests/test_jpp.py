import os
import unittest

from km3io import JppReader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


class TestJppEventsSnapshotHits(unittest.TestCase):
    def setUp(self):
        self.events = JppReader(os.path.join(SAMPLES_DIR,
                                             "jpp_v12.0.0.root")).events
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


class TestJppEventsTriggeredHits(unittest.TestCase):
    def setUp(self):
        self.events = JppReader(os.path.join(SAMPLES_DIR,
                                             "jpp_v12.0.0.root")).events
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
