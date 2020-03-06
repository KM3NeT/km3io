import unittest
import numpy as np
from pathlib import Path

from km3io import OfflineReader

SAMPLES_DIR = Path(__file__).parent / 'samples'
OFFLINE_FILE = OfflineReader(SAMPLES_DIR / 'aanet_v2.0.0.root')
OFFLINE_USR = OfflineReader(SAMPLES_DIR / 'usr-sample.root')
OFFLINE_NUMUCC = OfflineReader(SAMPLES_DIR / "numucc.root")  # with mc data


class TestOfflineReader(unittest.TestCase):
    def setUp(self):
        self.r = OFFLINE_FILE
        self.nu = OFFLINE_NUMUCC
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

    @unittest.skip
    def test_get_reco_fit(self):
        JGANDALF_BETA0_RAD = [
            0.0020367251782607574, 0.003306725805622178, 0.0057877124222254885,
            0.015581698352185896
        ]
        reco_fit = self.nu.get_reco_fit([1, 2, 3, 4, 5])['JGANDALF_BETA0_RAD']

        self.assertListEqual(JGANDALF_BETA0_RAD, reco_fit[:4].tolist())
        with self.assertRaises(ValueError):
            self.nu.get_reco_fit([1000, 4512, 5625], mc=True)

    @unittest.skip
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

    @unittest.skip
    def test_get_reco_tracks(self):

        pos = self.nu.get_reco_tracks([1, 2, 3, 4, 5], ["pos_x"])["pos_x"]
        mc_pos = self.nu.get_reco_tracks([], ["pos_x"], mc=True)["pos_x"]

        self.assertEqual(pos.size, 9)
        self.assertEqual(mc_pos.size, 10)

        self.assertEqual(pos[0], self.nu.tracks[0].pos_x[0])
        self.assertEqual(mc_pos[0], self.nu.mc_tracks[0].pos_x[0])

        with self.assertRaises(ValueError):
            self.nu.get_reco_tracks([1000, 4512, 5625], ["pos_x"])

    @unittest.skip
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

    @unittest.skip
    def test_get_max_reco_stages(self):
        rec_stages = self.nu.tracks.rec_stages
        max_reco = self.nu._get_max_reco_stages(rec_stages)

        self.assertEqual(len(max_reco.tolist()), 9)
        self.assertListEqual(max_reco[0].tolist(), [[1, 2, 3, 4, 5], 5, 0])

    @unittest.skip
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
        head = OFFLINE_NUMUCC.header

        self.assertAlmostEqual(head.DAQ.livetime, 394)

    def test_warning_if_unsupported_header(self):
        # test the warning for unsupported fheader format
        with self.assertWarns(UserWarning):
            self.r.header


class TestOfflineEvents(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events
        self.n_events = 10
        self.det_id = [44] * self.n_events
        self.n_hits = [176, 125, 318, 157, 83, 60, 71, 84, 255, 105]
        self.n_tracks = [56, 55, 56, 56, 56, 56, 56, 56, 54, 56]
        self.t_sec = [
            1567036818, 1567036818, 1567036820, 1567036816, 1567036816,
            1567036816, 1567036822, 1567036818, 1567036818, 1567036820
        ]
        self.t_ns = [
            200000000, 300000000, 200000000, 500000000, 500000000, 500000000,
            200000000, 500000000, 500000000, 400000000
        ]

    def test_len(self):
        assert self.n_events == len(self.events)

    def test_attributes_available(self):
        for key in self.events._keymap.keys():
            getattr(self.events, key)

    def test_attributes(self):
        assert self.n_events == len(self.events.det_id)
        self.assertListEqual(self.det_id, list(self.events.det_id))
        self.assertListEqual(self.n_hits, list(self.events.n_hits))
        self.assertListEqual(self.n_tracks, list(self.events.n_tracks))
        self.assertListEqual(self.t_sec, list(self.events.t_sec))
        self.assertListEqual(self.t_ns, list(self.events.t_ns))

    def test_keys(self):
        self.assertListEqual(self.n_hits, list(self.events['n_hits']))
        self.assertListEqual(self.n_tracks, list(self.events['n_tracks']))
        self.assertListEqual(self.t_sec, list(self.events['t_sec']))
        self.assertListEqual(self.t_ns, list(self.events['t_ns']))

    def test_slicing(self):
        s = slice(2, 8, 2)
        s_events = self.events[s]
        assert 3 == len(s_events)
        self.assertListEqual(self.n_hits[s], list(s_events.n_hits))
        self.assertListEqual(self.n_tracks[s], list(s_events.n_tracks))
        self.assertListEqual(self.t_sec[s], list(s_events.t_sec))
        self.assertListEqual(self.t_ns[s], list(s_events.t_ns))

    def test_slicing_consistency(self):
        for s in [slice(1, 3), slice(2, 7, 3)]:
            assert np.allclose(OFFLINE_FILE[s].events.n_hits,
                               self.events.n_hits[s])
            assert np.allclose(self.events[s].n_hits, self.events.n_hits[s])

    def test_index_consistency(self):
        for i in range(self.n_events):
            assert np.allclose(self.events[i].n_hits, self.events.n_hits[i])
            assert np.allclose(OFFLINE_FILE[i].events.n_hits,
                               self.events.n_hits[i])

    def test_str(self):
        assert str(self.n_events) in str(self.events)

    def test_repr(self):
        assert str(self.n_events) in repr(self.events)


class TestOfflineHits(unittest.TestCase):
    def setUp(self):
        self.hits = OFFLINE_FILE.hits
        self.n_hits = 10
        self.dom_id = {
            0: [
                806451572, 806451572, 806451572, 806451572, 806455814,
                806455814, 806455814, 806483369, 806483369, 806483369
            ],
            5: [
                806455814, 806487219, 806487219, 806487219, 806487226,
                808432835, 808432835, 808432835, 808432835, 808432835
            ]
        }
        self.t = {
            0: [
                70104010., 70104016., 70104192., 70104123., 70103096.,
                70103797., 70103796., 70104191., 70104223., 70104181.
            ],
            5: [
                81861237., 81859608., 81860586., 81861062., 81860357.,
                81860627., 81860628., 81860625., 81860627., 81860629.
            ]
        }

    def test_attributes_available(self):
        for key in self.hits._keymap.keys():
            getattr(self.hits, key)

    def test_channel_ids(self):
        self.assertTrue(all(c >= 0 for c in self.hits.channel_id.min()))
        self.assertTrue(all(c < 31 for c in self.hits.channel_id.max()))

    def test_str(self):
        assert str(self.n_hits) in str(self.hits)

    def test_repr(self):
        assert str(self.n_hits) in repr(self.hits)

    def test_attributes(self):
        for idx, dom_id in self.dom_id.items():
            self.assertListEqual(dom_id,
                                 list(self.hits.dom_id[idx][:len(dom_id)]))
        for idx, t in self.t.items():
            assert np.allclose(t, self.hits.t[idx][:len(t)])

    def test_slicing(self):
        s = slice(2, 8, 2)
        s_hits = self.hits[s]
        assert 3 == len(s_hits)
        for idx, dom_id in self.dom_id.items():
            self.assertListEqual(dom_id[s], list(self.hits.dom_id[idx][s]))
        for idx, t in self.t.items():
            self.assertListEqual(t[s], list(self.hits.t[idx][s]))

    def test_slicing_consistency(self):
        for s in [slice(1, 3), slice(2, 7, 3)]:
            for idx in range(3):
                assert np.allclose(self.hits.dom_id[idx][s],
                                   self.hits[idx].dom_id[s])
                assert np.allclose(OFFLINE_FILE[idx].hits.dom_id[s],
                                   self.hits.dom_id[idx][s])

    @unittest.skip
    def test_index_consistency(self):
        for i in range(self.n_events):
            assert np.allclose(self.events[i].n_hits, self.events.n_hits[i])
            assert np.allclose(OFFLINE_FILE[i].events.n_hits,
                               self.events.n_hits[i])


class TestOfflineTracks(unittest.TestCase):
    def setUp(self):
        self.tracks = OFFLINE_FILE.tracks
        self.r_mc = OFFLINE_NUMUCC
        self.Nevents = 10

    @unittest.skip
    def test_item_selection(self):
        self.assertListEqual(list(self.tracks[0].dir_z[:2]),
                             [-0.872885221293917, -0.872885221293917])

    @unittest.skip
    def test_IndexError(self):
        # test handling IndexError with empty lists/arrays
        self.assertEqual(len(OfflineTracks(['whatever'], [])), 0)

    @unittest.skip
    def test_repr(self):
        assert " 10 " in repr(self.tracks)

    @unittest.skip
    def test_str(self):
        assert str(self.tracks).endswith(" 10")

    @unittest.skip
    def test_reading_tracks_dir_z(self):
        dir_z = self.tracks.dir_z
        tracks_dir_z = {0: 56, 1: 55, 8: 54}

        for track_id, n_dir in tracks_dir_z.items():
            self.assertEqual(n_dir, len(dir_z[track_id]))

        # check that there are 10 arrays of tracks.dir_z info
        self.assertEqual(len(dir_z), self.Nevents)

    @unittest.skip
    def test_reading_mc_tracks_dir_z(self):
        dir_z = self.r_mc.mc_tracks.dir_z
        tracks_dir_z = {0: 11, 1: 25, 8: 13}

        for track_id, n_dir in tracks_dir_z.items():
            self.assertEqual(n_dir, len(dir_z[track_id]))

        # check that there are 10 arrays of tracks.dir_z info
        self.assertEqual(len(dir_z), self.Nevents)

        self.assertListEqual([0.230189, 0.230189, 0.218663],
                             list(dir_z[0][:3]))

    @unittest.skip
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
        self.f = OFFLINE_USR

    def test_str(self):
        print(self.f.events.usr)

    def test_nonexistent_usr(self):
        f = OfflineReader(SAMPLES_DIR / "daq_v1.0.0.root")
        assert not hasattr(self.f, "usr")

    def test_keys(self):
        self.assertListEqual([
            'RecoQuality', 'RecoNDF', 'CoC', 'ToT', 'ChargeAbove',
            'ChargeBelow', 'ChargeRatio', 'DeltaPosZ', 'FirstPartPosZ',
            'LastPartPosZ', 'NSnapHits', 'NTrigHits', 'NTrigDOMs',
            'NTrigLines', 'NSpeedVetoHits', 'NGeometryVetoHits',
            'ClassficationScore'
        ], self.f.events.usr.keys())

    def test_getitem(self):
        assert np.allclose(
            [118.6302815337638, 44.33580521344907, 99.93916717621543],
            self.f.events.usr['CoC'])
        assert np.allclose(
            [37.51967774166617, -10.280346193553832, 13.67595659707355],
            self.f.events.usr['DeltaPosZ'])

    def test_attributes(self):
        assert np.allclose(
            [118.6302815337638, 44.33580521344907, 99.93916717621543],
            self.f.events.usr.CoC)
        assert np.allclose(
            [37.51967774166617, -10.280346193553832, 13.67595659707355],
            self.f.events.usr.DeltaPosZ)
