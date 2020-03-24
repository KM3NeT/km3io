import unittest
import numpy as np
from pathlib import Path

from km3io import OfflineReader
from km3io.offline import _nested_mapper, cached_property, _to_num, Header

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


class TestHeader(unittest.TestCase):
    def test_reading_header(self):
        # head is the supported format
        head = OFFLINE_NUMUCC.header

        self.assertAlmostEqual(head.DAQ.livetime, 394)

    def test_str_header(self):
        assert "MC Header" in str(OFFLINE_NUMUCC.header)

    def test_warning_if_unsupported_header(self):
        # test the warning for unsupported fheader format
        with self.assertWarns(UserWarning):
            OFFLINE_FILE.header

    def test_header(self):
        head = {
            'DAQ': '394',
            'PDF': '4',
            'can': '0 1027 888.4',
            'undefined': '1 2 test 3.4'
        }

        header = Header(head)

        assert 394 == header.DAQ.livetime
        assert 4 == header.PDF.i1
        assert header.PDF.i2 is None
        assert 0 == header.can.zmin
        assert 1027 == header.can.zmax
        assert 888.4 == header.can.r
        assert 1 == header.undefined.field_0
        assert 2 == header.undefined.field_1
        assert "test" == header.undefined.field_2
        assert 3.4 == header.undefined.field_3

    def test_missing_key_definitions(self):
        head = {'a': '1 2 3', 'b': '4'}

        header = Header(head)

        assert 1 == header.a.field_0
        assert 2 == header.a.field_1
        assert 3 == header.a.field_2
        assert 4 == header.b

    def test_missing_values(self):
        head = {'can': '1'}

        header = Header(head)

        assert 1 == header.can.zmin
        assert header.can.zmax is None
        assert header.can.r is None

    def test_additional_values_compared_to_definition(self):
        head = {'can': '1 2 3 4'}

        header = Header(head)

        assert 1 == header.can.zmin
        assert 2 == header.can.zmax
        assert 3 == header.can.r
        assert 4 == header.can.field_3


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
        assert np.allclose(self.n_hits, self.events['n_hits'])
        assert np.allclose(self.n_tracks, self.events['n_tracks'])
        assert np.allclose(self.t_sec, self.events['t_sec'])
        assert np.allclose(self.t_ns, self.events['t_ns'])

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

    def test_keys(self):
        assert "dom_id" in self.hits.keys()


class TestOfflineTracks(unittest.TestCase):
    def setUp(self):
        self.tracks = OFFLINE_FILE.events.tracks
        self.tracks_numucc = OFFLINE_NUMUCC
        self.n_events = 10

    def test_attributes_available(self):
        for key in self.tracks._keymap.keys():
            getattr(self.tracks, key)

    def test_attributes(self):
        assert np.allclose([294.64075427, 294.64075427, 294.64075427],
                           self.tracks[0].lik[0:3])
        assert np.allclose([99.10458562, 0., 0.], self.tracks[0].E[0:3])
        assert np.allclose([-0.872885221293917, -0.872885221293917],
                           self.tracks[0].dir_z[:2])

    def test_repr(self):
        assert " 10 " in repr(self.tracks)

    def test_len(self):
        assert len(self.tracks) == self.n_events
        assert len(self.tracks[0]) == 1

    def test_keys(self):
        assert "pos_x" in self.tracks.keys()

    def test_slicing_consistency(self):
        for s in [slice(1, 3), slice(2, 7, 3)]:
            for idx in range(3):
                assert np.allclose(self.tracks.lik[idx][s],
                                   self.tracks[idx].lik[s])
                assert np.allclose(OFFLINE_FILE.events[idx].tracks.lik[s],
                                   self.tracks.lik[idx][s])


class GroupFailingTests(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events
        self.hits = OFFLINE_FILE.events.hits
        self.tracks = OFFLINE_FILE.events.tracks

    @unittest.skip
    def test_tracks_slicing(self):
        s = slice(0, 10, 3)
        s_tracks = self.tracks[s]
        assert 4 == len(s_tracks)

        for idx in range(len(s_tracks)):
            step = 3
            prev_idx = idx * step
            self.assertListEqual(list(s_tracks[idx].lik[0:3]),
                                 list(self.tracks[prev_idx].lik[0:3]))
            self.assertListEqual(list(s_tracks[idx].E[0:3]),
                                 list(self.tracks[prev_idx].E[0:3]))
            self.assertListEqual(list(s_tracks[idx].pos_z[0:3]),
                                 list(self.tracks[prev_idx].pos_z[0:3]))


class TestBranchIndexingMagic(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events

    def test_foo(self):
        self.assertEqual(318, self.events[2:4].n_hits[0])
        assert np.allclose(self.events[3].tracks.dir_z[10],
                           self.events.tracks.dir_z[3, 10])
        assert np.allclose(self.events[3:6].tracks.pos_y[:, 0],
                           self.events.tracks.pos_y[3:6, 0])

        # test slicing with a tuple
        assert np.allclose(self.events[0].hits[1].dom_id[0:10],
                           self.events.hits[(0, 1)].dom_id[0:10])

        # test selecting with a list
        self.assertEqual(3, len(self.events[[0, 2, 3]]))


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


class TestNestedMapper(unittest.TestCase):
    def test_nested_mapper(self):
        self.assertEqual('pos_x', _nested_mapper("trks.pos.x"))


class TestToNum(unittest.TestCase):
    def test_to_num(self):
        self.assertEqual(10, _to_num("10"))
        self.assertEqual(10.5, _to_num("10.5"))
        self.assertEqual("test", _to_num("test"))
        self.assertIsNone(_to_num(None))


class TestCachedProperty(unittest.TestCase):
    def test_cached_properties(self):
        class Test:
            @cached_property
            def prop(self):
                pass

        self.assertTrue(isinstance(Test.prop, cached_property))
