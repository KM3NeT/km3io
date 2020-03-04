import unittest
import numpy as np
from pathlib import Path

from km3io import OfflineReader

SAMPLES_DIR = Path(__file__).parent / 'samples'
OFFLINE_FILE = SAMPLES_DIR / 'aanet_v2.0.0.root'
OFFLINE_USR = SAMPLES_DIR / 'usr-sample.root'
OFFLINE_NUMUCC = SAMPLES_DIR / "numucc.root"  # with mc data


class TestOfflineReader(unittest.TestCase):
    def setUp(self):
        self.r = OfflineReader(OFFLINE_FILE)
        self.nu = OfflineReader(OFFLINE_NUMUCC)
        self.Nevents = 10

    def test_number_events(self):
        Nevents = len(self.r)

        # check that there are 10 events
        self.assertEqual(Nevents, self.Nevents)

    def test_find_empty(self):
        fitinf = self.nu.tracks.fitinf
        rec_stages = self.nu.tracks.rec_stages

        empty_fitinf = np.array(
            [match for match in self.nu._find_empty(fitinf)])
        empty_stages = np.array(
            [match for match in self.nu._find_empty(rec_stages)])

        self.assertListEqual(empty_fitinf[:5, 1].tolist(),
                             [23, 14, 14, 4, None])
        self.assertListEqual(empty_stages[:5, 1].tolist(),
                             [False, False, False, False, None])

    def test_find_rec_stages(self):
        stages = np.array(
            [match for match in self.nu._find_rec_stages([1, 2, 3, 4, 5])])

        self.assertListEqual(stages[:5, 1].tolist(), [0, 0, 0, 0, None])

    def test_get_reco_fit(self):
        JGANDALF_BETA0_RAD = [
            0.0020367251782607574, 0.003306725805622178, 0.0057877124222254885,
            0.015581698352185896
        ]
        reco_fit = self.nu.get_reco_fit([1, 2, 3, 4, 5])['JGANDALF_BETA0_RAD']

        self.assertListEqual(JGANDALF_BETA0_RAD, reco_fit[:4].tolist())
        with self.assertRaises(ValueError):
            self.nu.get_reco_fit([1000, 4512, 5625], mc=True)

    def test_get_reco_hits(self):

        doms = self.nu.get_reco_hits([1, 2, 3, 4, 5], ["dom_id"])["dom_id"]

        mc_doms = self.nu.get_reco_hits([], ["dom_id"], mc=True)["dom_id"]

        self.assertEqual(doms.size, 9)
        self.assertEqual(mc_doms.size, 10)

        self.assertListEqual(doms[0][0:4].tolist(),
                             self.nu.hits[0].dom_id[0:4].tolist())
        self.assertListEqual(mc_doms[0][0:4].tolist(),
                             self.nu.mc_hits[0].dom_id[0:4].tolist())

        with self.assertRaises(ValueError):
            self.nu.get_reco_hits([1000, 4512, 5625], ["dom_id"])

    def test_get_reco_tracks(self):

        pos = self.nu.get_reco_tracks([1, 2, 3, 4, 5], ["pos_x"])["pos_x"]
        mc_pos = self.nu.get_reco_tracks([], ["pos_x"], mc=True)["pos_x"]

        self.assertEqual(pos.size, 9)
        self.assertEqual(mc_pos.size, 10)

        self.assertEqual(pos[0], self.nu.tracks[0].pos_x[0])
        self.assertEqual(mc_pos[0], self.nu.mc_tracks[0].pos_x[0])

        with self.assertRaises(ValueError):
            self.nu.get_reco_tracks([1000, 4512, 5625], ["pos_x"])

    def test_get_reco_events(self):

        hits = self.nu.get_reco_events([1, 2, 3, 4, 5], ["hits"])["hits"]
        mc_hits = self.nu.get_reco_events([], ["mc_hits"], mc=True)["mc_hits"]

        self.assertEqual(hits.size, 9)
        self.assertEqual(mc_hits.size, 10)

        self.assertListEqual(hits[0:4].tolist(),
                             self.nu.events.hits[0:4].tolist())
        self.assertListEqual(mc_hits[0:4].tolist(),
                             self.nu.events.mc_hits[0:4].tolist())

        with self.assertRaises(ValueError):
            self.nu.get_reco_events([1000, 4512, 5625], ["hits"])

    def test_get_max_reco_stages(self):
        rec_stages = self.nu.tracks.rec_stages
        max_reco = self.nu._get_max_reco_stages(rec_stages)

        self.assertEqual(len(max_reco.tolist()), 9)
        self.assertListEqual(max_reco[0].tolist(), [[1, 2, 3, 4, 5], 5, 0])

    def test_best_reco(self):
        JGANDALF_BETA1_RAD = [
            0.0014177681261476852, 0.002094094517471032, 0.003923368624980349,
            0.009491461076780453
        ]
        best = self.nu.get_best_reco()

        self.assertEqual(best.size, 9)
        self.assertEqual(best['JGANDALF_BETA1_RAD'][:4].tolist(),
                         JGANDALF_BETA1_RAD)

    def test_reading_header(self):
        # head is the supported format
        head = OfflineReader(OFFLINE_NUMUCC).header

        self.assertEqual(float(head['DAQ']), 394)
        self.assertEqual(float(head['kcut']), 2)

        # test the warning for unsupported fheader format
        with self.assertWarns(UserWarning):
            self.r.header


class TestOfflineEvents(unittest.TestCase):
    def setUp(self):
        self.events = OfflineReader(OFFLINE_FILE).events
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
        self.assertEqual(len(OfflineEvents(['whatever'], [])), 0)

    def test_str(self):
        self.assertEqual(str(self.events), 'Number of events: 10')

    def test_repr(self):
        self.assertEqual(repr(self.events),
                         '<OfflineEvents: 10 parsed events>')


class TestOfflineHits(unittest.TestCase):
    def setUp(self):
        self.hits = OfflineReader(OFFLINE_FILE).hits
        self.lengths = {0: 176, 1: 125, -1: 105}
        self.total_item_count = 1434
        self.r_mc = OfflineReader(OFFLINE_NUMUCC)
        self.Nevents = 10

    def test_item_selection(self):
        self.assertListEqual(list(self.hits[0].dom_id[:3]),
                             [806451572, 806451572, 806451572])

    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(OfflineHits(['whatever'], [])), 0)

    def test_repr(self):
        self.assertEqual(repr(self.hits), '<OfflineHits: 10 parsed elements>')

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


class TestOfflineTracks(unittest.TestCase):
    def setUp(self):
        self.tracks = OfflineReader(OFFLINE_FILE).tracks
        self.r_mc = OfflineReader(OFFLINE_NUMUCC)
        self.Nevents = 10

    def test_item_selection(self):
        self.assertListEqual(list(self.tracks[0].dir_z[:2]),
                             [-0.872885221293917, -0.872885221293917])

    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(OfflineTracks(['whatever'], [])), 0)

    def test_repr(self):
        assert " 10 " in repr(self.tracks)

    def test_str(self):
        assert str(self.tracks).endswith(" 10")

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

    def test_slicing(self):
        tracks = self.tracks
        assert 10 == len(tracks)
        # track_selection = tracks[2:7]
        # assert 5 == len(track_selection)
        # track_selection_2 = tracks[1:3]
        # assert 2 == len(track_selection_2)
        # for _slice in [
        #         slice(0, 0),
        #         slice(0, 1),
        #         slice(0, 2),
        #         slice(1, 5),
        #         slice(3, -2)
        # ]:
        #     self.assertListEqual(list(tracks.E[:, 0][_slice]),
        #                          list(tracks[_slice].E[:, 0]))


class TestUsr(unittest.TestCase):
    def setUp(self):
        self.f = OfflineReader(OFFLINE_USR)

    def test_str(self):
        print(self.f.usr)

    def test_nonexistent_usr(self):
        f = OfflineReader(SAMPLES_DIR / "daq_v1.0.0.root")
        self.assertListEqual([], f.usr.keys())

    def test_keys(self):
        self.assertListEqual([
            'RecoQuality', 'RecoNDF', 'CoC', 'ToT', 'ChargeAbove',
            'ChargeBelow', 'ChargeRatio', 'DeltaPosZ', 'FirstPartPosZ',
            'LastPartPosZ', 'NSnapHits', 'NTrigHits', 'NTrigDOMs',
            'NTrigLines', 'NSpeedVetoHits', 'NGeometryVetoHits',
            'ClassficationScore'
        ], self.f.usr.keys())

    def test_getitem(self):
        assert np.allclose(
            [118.6302815337638, 44.33580521344907, 99.93916717621543],
            self.f.usr['CoC'])
        assert np.allclose(
            [37.51967774166617, -10.280346193553832, 13.67595659707355],
            self.f.usr['DeltaPosZ'])

    def test_attributes(self):
        assert np.allclose(
            [118.6302815337638, 44.33580521344907, 99.93916717621543],
            self.f.usr.CoC)
        assert np.allclose(
            [37.51967774166617, -10.280346193553832, 13.67595659707355],
            self.f.usr.DeltaPosZ)
