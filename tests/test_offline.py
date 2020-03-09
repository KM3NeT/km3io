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
        self.n_events = 10

    def test_number_events(self):
        assert self.n_events == len(self.r.events)

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

    @unittest.skip
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
            assert np.allclose(self.events[s].n_hits, self.events.n_hits[s])

    def test_index_consistency(self):
        for i in [0, 2, 5]:
            assert np.allclose(self.events[i].n_hits, self.events.n_hits[i])

    def test_str(self):
        assert str(self.n_events) in str(self.events)

    def test_repr(self):
        assert str(self.n_events) in repr(self.events)


class TestOfflineHits(unittest.TestCase):
    def setUp(self):
        self.hits = OFFLINE_FILE.events.hits
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
                assert np.allclose(OFFLINE_FILE.events[idx].hits.dom_id[s],
                                   self.hits.dom_id[idx][s])

    def test_index_consistency(self):
        for idx, dom_ids in self.dom_id.items():
            assert np.allclose(self.hits[idx].dom_id[:self.n_hits],
                               dom_ids[:self.n_hits])
            assert np.allclose(
                OFFLINE_FILE.events[idx].hits.dom_id[:self.n_hits],
                dom_ids[:self.n_hits])
        for idx, ts in self.t.items():
            assert np.allclose(self.hits[idx].t[:self.n_hits],
                               ts[:self.n_hits])
            assert np.allclose(OFFLINE_FILE.events[idx].hits.t[:self.n_hits],
                               ts[:self.n_hits])


class TestOfflineTracks(unittest.TestCase):
    def setUp(self):
        self.tracks = OFFLINE_FILE.events.tracks
        self.tracks_numucc = OFFLINE_NUMUCC
        self.n_events = 10

    def test_attributes_available(self):
        for key in self.tracks._keymap.keys():
            getattr(self.tracks, key)

    def test_item_selection(self):
        self.assertListEqual(list(self.tracks[0].dir_z[:2]),
                             [-0.872885221293917, -0.872885221293917])

    def test_repr(self):
        assert " 10 " in repr(self.tracks)

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
