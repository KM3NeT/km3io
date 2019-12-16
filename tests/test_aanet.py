import unittest
from pathlib import Path

from km3io.aanet import Reader, AanetEvents, AanetHits, AanetTracks
from km3io import AanetReader

SAMPLES_DIR = Path(__file__).parent / 'samples'
AANET_FILE = SAMPLES_DIR / 'aanet_v2.0.0.root'
AANET_NUMUCC = SAMPLES_DIR / "numucc.root"  # with mc data


class TestAanetKeys(unittest.TestCase):
    def setUp(self):
        self.keys = AanetReader(AANET_FILE).keys

    def test_repr(self):
        reader_repr = repr(self.keys)

        # check that there are 106 keys + 5 extra str
        self.assertEqual(len(reader_repr.split('\n')), 111)

    def test_events_keys(self):
        # there are 22 "valid" events keys
        self.assertEqual(len(self.keys.events_keys), 22)
        self.assertEqual(len(self.keys.cut_events_keys), 22)

    def test_hits_keys(self):
        # there are 20 "valid" hits keys
        self.assertEqual(len(self.keys.hits_keys), 20)
        self.assertEqual(len(self.keys.mc_hits_keys), 20)
        self.assertEqual(len(self.keys.cut_hits_keys), 20)

    def test_tracks_keys(self):
        # there are 22 "valid" tracks keys
        self.assertEqual(len(self.keys.tracks_keys), 22)
        self.assertEqual(len(self.keys.mc_tracks_keys), 22)
        self.assertEqual(len(self.keys.cut_tracks_keys), 22)

    def test_valid_keys(self):
        # there are 106 valid keys: 22*2 + 22 + 20*2
        # (fit keys are excluded)
        self.assertEqual(len(self.keys.valid_keys), 106)

    def test_fit_keys(self):
        # there are 18 fit keys
        self.assertEqual(len(self.keys.fit_keys), 18)


class TestReader(unittest.TestCase):
    def setUp(self):
        self.r = Reader(AANET_FILE)
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
        # there are 106 "valid" keys in Aanet file
        self.assertEqual(len(self.r.keys.valid_keys), 106)

        # there are 20 hits keys
        self.assertEqual(len(self.r.keys.hits_keys), 20)
        self.assertEqual(len(self.r.keys.mc_hits_keys), 20)

        # there are 22 tracks keys
        self.assertEqual(len(self.r.keys.tracks_keys), 22)
        self.assertEqual(len(self.r.keys.mc_tracks_keys), 22)

    def test_raising_KeyError(self):
        # non valid keys must raise a KeyError
        with self.assertRaises(KeyError):
            self.r['whatever']

    def test_number_events(self):
        Nevents = len(self.r)

        # check that there are 10 events
        self.assertEqual(Nevents, 10)


class TestAanetReader(unittest.TestCase):
    def setUp(self):
        self.r = AanetReader(AANET_FILE)
        self.Nevents = 10
        self.selected_data = AanetReader(AANET_FILE,
                                         data=self.r._data[0])._data

    def test_item_selection(self):
        # test class instance with data=None option
        self.assertEqual(len(self.selected_data), len(self.r._data[0]))

        # test item selection (here we test with hits=176)
        self.assertEqual(self.r[0].events.hits, self.selected_data['hits'])

    def test_number_events(self):
        Nevents = len(self.r)

        # check that there are 10 events
        self.assertEqual(Nevents, self.Nevents)


class TestAanetEvents(unittest.TestCase):
    def setUp(self):
        self.events = AanetReader(AANET_FILE).events
        self.hits = {0: 176, 1: 125, -1: 105}
        self.Nevents = 10

    def test_reading_hits(self):
        # test item selection
        for event_id, hit in self.hits.items():
            self.assertEqual(hit, self.events.hits[event_id])

    def reading_tracks(self):
        self.assertListEqual(list(self.events.trks[:3]), [56, 55, 56])

    def test_item_selection(self):
        for event_id, hit in self.hits.items():
            self.assertEqual(hit, self.events[event_id].hits)

    def test_len(self):
        self.assertEqual(len(self.events), self.Nevents)

    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(AanetEvents(['whatever'], [])), 0)

    def test_str(self):
        self.assertEqual(str(self.events), 'Number of events: 10')

    def test_repr(self):
        self.assertEqual(repr(self.events), '<AanetEvents: 10 parsed events>')


class TestAanetEvent(unittest.TestCase):
    def setUp(self):
        self.event = AanetReader(AANET_FILE).events[0]

    def test_str(self):
        self.assertEqual(repr(self.event).split('\n\t')[0], 'Aanet event:')
        self.assertEqual(
            repr(self.event).split('\n\t')[2],
            'det_id              :              44')


class TestAanetHits(unittest.TestCase):
    def setUp(self):
        self.hits = AanetReader(AANET_FILE).hits
        self.lengths = {0: 176, 1: 125, -1: 105}
        self.total_item_count = 1434
        self.r_mc = AanetReader(AANET_NUMUCC)
        self.Nevents = 10

    def test_item_selection(self):
        self.assertListEqual(list(self.hits[0].dom_id[:3]),
                             [806451572, 806451572, 806451572])

    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(AanetHits(['whatever'], [])), 0)

    def test_repr(self):
        self.assertEqual(repr(self.hits), '<AanetHits: 10 parsed elements>')

    def test_str(self):
        self.assertEqual(str(self.hits), 'Number of hits: 10')

    def test_reading_dom_id(self):
        dom_ids = self.hits.dom_id

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(dom_ids[event_id]))

        self.assertEqual(self.total_item_count, sum(dom_ids.count()))

        self.assertListEqual([806451572, 806451572, 806451572],
                             list(dom_ids[0][:3]))

    def test_reading_channel_id(self):
        channel_ids = self.hits.channel_id

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(channel_ids[event_id]))

        self.assertEqual(self.total_item_count, sum(channel_ids.count()))

        self.assertListEqual([8, 9, 14], list(channel_ids[0][:3]))

        # channel IDs are always between [0, 30]
        self.assertTrue(all(c >= 0 for c in channel_ids.min()))
        self.assertTrue(all(c < 31 for c in channel_ids.max()))

    def test_reading_times(self):
        ts = self.hits.t

        for event_id, length in self.lengths.items():
            self.assertEqual(length, len(ts[event_id]))

        self.assertEqual(self.total_item_count, sum(ts.count()))

        self.assertListEqual([70104010.0, 70104016.0, 70104192.0],
                             list(ts[0][:3]))

    def test_reading_mc_pmt_id(self):
        pmt_ids = self.r_mc.mc_hits.pmt_id
        lengths = {0: 58, 2: 28, -1: 48}

        for hit_id, length in lengths.items():
            self.assertEqual(length, len(pmt_ids[hit_id]))

        self.assertEqual(self.Nevents, len(pmt_ids))

        self.assertListEqual([677, 687, 689], list(pmt_ids[0][:3]))


class TestAanetHit(unittest.TestCase):
    def setUp(self):
        self.hit = AanetReader(AANET_FILE)[0].hits[0]

    def test_item_selection(self):
        self.assertEqual(self.hit[0], self.hit.id)
        self.assertEqual(self.hit[1], self.hit.dom_id)

    def test_str(self):
        self.assertEqual(repr(self.hit).split('\n\t')[0], 'Aanet hit:')
        self.assertEqual(
            repr(self.hit).split('\n\t')[2],
            'dom_id              :       806451572')


class TestAanetTracks(unittest.TestCase):
    def setUp(self):
        self.tracks = AanetReader(AANET_FILE).tracks
        self.r_mc = AanetReader(AANET_NUMUCC)
        self.Nevents = 10

    def test_item_selection(self):
        self.assertListEqual(list(self.tracks[0].dir_z[:2]),
                             [-0.872885221293917, -0.872885221293917])

    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(AanetTracks(['whatever'], [])), 0)

    def test_repr(self):
        self.assertEqual(repr(self.tracks),
                         '<AanetTracks: 10 parsed elements>')

    def test_str(self):
        self.assertEqual(str(self.tracks), 'Number of tracks: 10')

    def test_reading_tracks_dir_z(self):
        dir_z = self.tracks.dir_z
        tracks_dir_z = {0: 56, 1: 55, 8: 54}

        for track_id, n_dir in tracks_dir_z.items():
            self.assertEqual(n_dir, len(dir_z[track_id]))

        # check that there are 10 arrays of tracks.dir_z info
        self.assertEqual(len(dir_z), self.Nevents)

    def test_reading_mc_tracks_dir_z(self):
        dir_z = self.r_mc.mc_tracks.dir_z
        tracks_dir_z = {0: 11, 1: 25, 8: 13}

        for track_id, n_dir in tracks_dir_z.items():
            self.assertEqual(n_dir, len(dir_z[track_id]))

        # check that there are 10 arrays of tracks.dir_z info
        self.assertEqual(len(dir_z), self.Nevents)

        self.assertListEqual([0.230189, 0.230189, 0.218663],
                             list(dir_z[0][:3]))


class TestAanetTrack(unittest.TestCase):
    def setUp(self):
        self.track = AanetReader(AANET_FILE)[0].tracks[0]

    def test_item_selection(self):
        self.assertEqual(self.track[0], self.track.fUniqueID)
        self.assertEqual(self.track[10], self.track.E)

    def test_str(self):
        self.assertEqual(repr(self.track).split('\n\t')[0], 'Aanet track:')
        self.assertEqual(
            repr(self.track).split('\n\t')[28],
            'JGANDALF_LAMBDA                :      4.2409761837248484e-12')
