import os
import unittest

from km3io import reader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


class TestAanetReaderHits(unittest.TestCase):
    def setUp(self):
        self.r = reader.AanetReader(
            os.path.join(SAMPLES_DIR, "aanet_v2.0.0.root"))
        self.lengths = {0: 176, 1: 125, -1: 105}
        self.total_item_count = 1434

    def test_reading_dom_id(self):
        dom_ids = self.r.read_hits("hits.dom_id")

        for event_id, length in self.lengths.items():
            assert length == len(dom_ids[event_id])

        assert self.total_item_count == sum(dom_ids.count())

        self.assertListEqual([806451572, 806451572, 806451572],
                             list(dom_ids[0][:3]))

    def test_reading_channel_id(self):
        channel_ids = self.r.read_hits("hits.channel_id")

        for event_id, length in self.lengths.items():
            assert length == len(channel_ids[event_id])

        assert self.total_item_count == sum(channel_ids.count())

        self.assertListEqual([8, 9, 14], list(channel_ids[0][:3]))

        # channel IDs are always between [0, 30]
        assert all(c >= 0 for c in channel_ids.min())
        assert all(c < 31 for c in channel_ids.max())

    def test_reading_times(self):
        ts = self.r.read_hits("hits.t")

        for event_id, length in self.lengths.items():
            assert length == len(ts[event_id])

        assert self.total_item_count == sum(ts.count())

        self.assertListEqual([70104010.0, 70104016.0, 70104192.0],
                             list(ts[0][:3]))
