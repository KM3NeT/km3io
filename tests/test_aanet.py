import unittest
from pathlib import Path

from km3io import AanetReader

SAMPLES_DIR = Path(__file__).parent / 'samples'
AANET_FILE = SAMPLES_DIR / 'aanet_v2.0.0.root'


class TestAanetReader(unittest.TestCase):
    def setUp(self):
        self.r = AanetReader(AANET_FILE)
        self.lengths = {0: 176, 1: 125, -1: 105}
        self.total_item_count = 1434

    def test_reading_dom_id(self):
        dom_ids = self.r["hits.dom_id"]

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(dom_ids[event_id]))

        self.assertEqual(self.total_item_count, sum(dom_ids.count()))

        self.assertListEqual([806451572, 806451572, 806451572],
                             list(dom_ids[0][:3]))

    def test_reading_channel_id(self):
        channel_ids = self.r["hits.channel_id"]

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(channel_ids[event_id]))

        self.assertEqual(self.total_item_count, sum(channel_ids.count()))

        self.assertListEqual([8, 9, 14], list(channel_ids[0][:3]))

        # channel IDs are always between [0, 30]
        self.assertTrue(all(c >= 0 for c in channel_ids.min()))
        self.assertTrue(all(c < 31 for c in channel_ids.max()))

    def test_reading_times(self):
        ts = self.r["hits.t"]

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(ts[event_id]))

        self.assertEqual(self.total_item_count, sum(ts.count()))

        self.assertListEqual([70104010.0, 70104016.0, 70104192.0],
                             list(ts[0][:3]))

    def test_reading_keys(self):
        all_keys = self.r.keys()

        # there are 66 valid keys in Aanet file
        self.assertEqual(len(all_keys), 66)

    def test_raising_KeyError(self):
        # non valid keys must raise a KeyError
        with self.assertRaises(KeyError):
            self.r['whatever']

    def test_number_events(self):
        Nevents = len(self.r)
        reader_repr = repr(self.r)

        # check that there are 10 events
        self.assertEqual(Nevents, 10)
        # check that there are 66 keys + 4 extra str
        self.assertEqual(len(reader_repr.split('\n')), 70)
