import unittest
import numpy as np
from pathlib import Path
import uuid

import awkward as ak
from km3net_testdata import data_path

from km3io import OfflineReader
from km3io.offline import Header
from km3io.tools import usr

OFFLINE_FILE = OfflineReader(data_path("offline/km3net_offline.root"))
OFFLINE_USR = OfflineReader(data_path("offline/usr-sample.root"))
OFFLINE_MC_TRACK_USR = OfflineReader(
    data_path(
        "offline/mcv5.11r2.gsg_muonCChigherE-CC_50-5000GeV.km3_AAv1.jterbr00004695.jchain.aanet.498.root"
    )
)
OFFLINE_NUMUCC = OfflineReader(data_path("offline/numucc.root"))  # with mc data
OFFLINE_MC_TRACK = OfflineReader(
    data_path("gseagen/gseagen_v7.0.0_numuCC_diffuse.aa.root")
)


class TestOfflineReader(unittest.TestCase):
    def setUp(self):
        self.r = OFFLINE_FILE
        self.nu = OFFLINE_NUMUCC
        self.n_events = 10

    def test_context_manager(self):
        filename = OFFLINE_FILE
        with OfflineReader(data_path("offline/km3net_offline.root")) as r:
            assert r

    def test_number_events(self):
        assert self.n_events == len(self.r.events)

    def test_uuid(self):
        assert str(self.r.uuid) == "b192d888-fcc7-11e9-b430-6cf09e86beef"


class TestHeader(unittest.TestCase):
    def test_str_header(self):
        assert "MC Header" in str(OFFLINE_NUMUCC.header)

    def test_warning_if_unsupported_header(self):
        # test the warning for unsupported fheader format
        with self.assertWarns(UserWarning):
            OFFLINE_FILE.header

    def test_missing_key_definitions(self):
        head = {"a": "1 2 3", "b": "4", "c": "d"}

        header = Header(head)

        assert 1 == header.a.field_0
        assert 2 == header.a.field_1
        assert 3 == header.a.field_2
        assert 4 == header.b
        assert "d" == header.c

    def test_missing_values(self):
        head = {"can": "1"}

        header = Header(head)

        assert 1 == header.can.zmin
        assert header.can.zmax is None
        assert header.can.r is None

    def test_additional_values_compared_to_definition(self):
        head = {"can": "1 2 3 4"}

        header = Header(head)

        assert 1 == header.can.zmin
        assert 2 == header.can.zmax
        assert 3 == header.can.r
        assert 4 == header.can.field_3

    def test_header(self):
        head = {
            "DAQ": "394",
            "PDF": "4",
            "can": "0 1027 888.4",
            "undefined": "1 2 test 3.4",
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

    def test_header_with_invalid_field_or_attribute_names(self):
        head = {
            "a": "1 2 3",
            "b+c": "4 5 6",
            "c": "foo",
            "d": "7",
            "e+f": "bar",
        }

        header = Header(head)
        assert 1 == header["a"][0]
        assert 2 == header["a"][1]
        assert 3 == header["a"][2]
        assert 1 == header.a[0]
        assert 2 == header.a[1]
        assert 3 == header.a[2]
        assert 4 == header["b+c"][0]
        assert 5 == header["b+c"][1]
        assert 6 == header["b+c"][2]
        assert "foo" == header.c
        assert "foo" == header["c"]
        assert 7 == header.d
        assert 7 == header["d"]
        assert "bar" == header["e+f"]

    def test_header_behaves_like_a_dict(self):
        head = {
            "a": "1 2 3",
            "b+c": "4 5 6",
            "c": "foo",
            "d": "7",
            "e+f": "bar",
        }

        header = Header(head)
        self.assertListEqual(list(head.keys()), list(header.keys()))
        assert 5 == len(header.values())
        assert 5 == len(header.items())

    def test_reading_header_from_sample_file(self):
        head = OFFLINE_NUMUCC.header

        assert 394 == head.DAQ.livetime
        assert 4 == head.PDF.i1
        assert 58 == head.PDF.i2
        assert 0 == head.coord_origin.x
        assert 0 == head.coord_origin.y
        assert 0 == head.coord_origin.z
        assert 100 == head.cut_nu.Emin
        assert 100000000.0 == head.cut_nu.Emax
        assert -1 == head.cut_nu.cosTmin
        assert 1 == head.cut_nu.cosTmax
        assert "diffuse" == head.sourcemode
        assert 100000.0 == head.ngen


class TestOfflineEvents(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events
        self.n_events = 10
        self.det_id = [44] * self.n_events
        self.n_hits = [176, 125, 318, 157, 83, 60, 71, 84, 255, 105]
        self.n_tracks = [56, 55, 56, 56, 56, 56, 56, 56, 54, 56]
        self.t_sec = [
            1567036818,
            1567036818,
            1567036820,
            1567036816,
            1567036816,
            1567036816,
            1567036822,
            1567036818,
            1567036818,
            1567036820,
        ]
        self.t_ns = [
            200000000,
            300000000,
            200000000,
            500000000,
            500000000,
            500000000,
            200000000,
            500000000,
            500000000,
            400000000,
        ]

    def test_len(self):
        assert self.n_events == len(self.events)

    def test_attributes(self):
        assert self.n_events == len(self.events.det_id)
        self.assertListEqual(self.det_id, list(self.events.det_id))
        print(self.n_hits)
        print(self.events.hits)
        self.assertListEqual(self.n_hits, list(self.events.n_hits))
        self.assertListEqual(self.n_tracks, list(self.events.n_tracks))
        self.assertListEqual(self.t_sec, list(self.events.t_sec))
        self.assertListEqual(self.t_ns, list(self.events.t_ns))

    def test_keys(self):
        assert np.allclose(self.n_hits, self.events["n_hits"].tolist())
        assert np.allclose(self.n_tracks, self.events["n_tracks"].tolist())
        assert np.allclose(self.t_sec, self.events["t_sec"].tolist())
        assert np.allclose(self.t_ns, self.events["t_ns"].tolist())

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
            assert np.allclose(
                self.events[s].n_hits.tolist(), self.events.n_hits[s].tolist()
            )

    def test_index_consistency(self):
        for i in [0, 2, 5]:
            assert np.allclose(self.events[i].n_hits, self.events.n_hits[i])

    def test_index_chaining(self):
        assert np.allclose(
            self.events[3:5].n_hits.tolist(), self.events.n_hits[3:5].tolist()
        )
        assert np.allclose(self.events[3:5][0].n_hits, self.events.n_hits[3:5][0])

    def test_index_chaining_on_nested_branches_aka_records(self):
        assert np.allclose(
            self.events[3:5].hits[1].dom_id[4],
            self.events.hits[3:5][1].dom_id[4],
        )
        assert np.allclose(
            self.events.hits[3:5][1].dom_id[4],
            self.events[3:5][1].hits.dom_id[4],
        )

    def test_fancy_indexing(self):
        mask = self.events.n_tracks > 55
        tracks = self.events.tracks[mask]
        first_tracks = tracks[:, 0]
        assert 8 == len(first_tracks)
        assert 8 == len(first_tracks.rec_stages)
        assert 8 == len(first_tracks.lik)

    def test_iteration(self):
        i = 0
        for event in self.events:
            i += 1
        assert 10 == i

    def test_iteration_2(self):
        n_hits = [len(e.hits.id) for e in self.events]
        assert np.allclose(n_hits, ak.num(self.events.hits.id, axis=1).tolist())

    def test_iteration_over_slices(self):
        ids = [e.id for e in self.events[2:5]]
        self.assertListEqual([3, 4, 5], ids)

    def test_iteration_over_slices_raises_when_stepsize_not_supported(self):
        with self.assertRaises(NotImplementedError):
            [e.id for e in self.events[2:8:2]]

    def test_iteration_over_slices_raises_when_single_item(self):
        with self.assertRaises(NotImplementedError):
            [e.id for e in self.events[0]]

    def test_iteration_over_slices_raises_when_multiple_slices(self):
        with self.assertRaises(NotImplementedError):
            [e.id for e in self.events[2:8][2:4]]

    def test_iteration_over_subbranches_raises(self):
        with self.assertRaises(NotImplementedError):
            [t for t in self.events[0].tracks]

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
                806451572,
                806451572,
                806451572,
                806451572,
                806455814,
                806455814,
                806455814,
                806483369,
                806483369,
                806483369,
            ],
            5: [
                806455814,
                806487219,
                806487219,
                806487219,
                806487226,
                808432835,
                808432835,
                808432835,
                808432835,
                808432835,
            ],
        }
        self.t = {
            0: [
                70104010.0,
                70104016.0,
                70104192.0,
                70104123.0,
                70103096.0,
                70103797.0,
                70103796.0,
                70104191.0,
                70104223.0,
                70104181.0,
            ],
            5: [
                81861237.0,
                81859608.0,
                81860586.0,
                81861062.0,
                81860357.0,
                81860627.0,
                81860628.0,
                81860625.0,
                81860627.0,
                81860629.0,
            ],
        }

    def test_fields_work_as_keys_and_attributes(self):
        for key in self.hits.fields:
            getattr(self.hits, key)
            self.hits[key]

    def test_channel_ids(self):
        self.assertTrue(all(c >= 0 for c in ak.min(self.hits.channel_id, axis=1)))
        self.assertTrue(all(c < 31 for c in ak.max(self.hits.channel_id, axis=1)))

    def test_repr(self):
        assert str(self.n_hits) in repr(self.hits)

    def test_attributes(self):
        for idx, dom_id in self.dom_id.items():
            self.assertListEqual(dom_id, list(self.hits.dom_id[idx][: len(dom_id)]))
        for idx, t in self.t.items():
            assert np.allclose(t, self.hits.t[idx][: len(t)].tolist())

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
                assert np.allclose(
                    self.hits.dom_id[idx][s].tolist(), self.hits[idx].dom_id[s].tolist()
                )
                assert np.allclose(
                    OFFLINE_FILE.events[idx].hits.dom_id[s].tolist(),
                    self.hits.dom_id[idx][s].tolist(),
                )

    def test_index_consistency(self):
        for idx, dom_ids in self.dom_id.items():
            assert np.allclose(
                self.hits[idx].dom_id[: self.n_hits].tolist(), dom_ids[: self.n_hits]
            )
            assert np.allclose(
                OFFLINE_FILE.events[idx].hits.dom_id[: self.n_hits].tolist(),
                dom_ids[: self.n_hits],
            )
        for idx, ts in self.t.items():
            assert np.allclose(
                self.hits[idx].t[: self.n_hits].tolist(), ts[: self.n_hits]
            )
            assert np.allclose(
                OFFLINE_FILE.events[idx].hits.t[: self.n_hits].tolist(),
                ts[: self.n_hits],
            )

    def test_fields(self):
        assert "dom_id" in self.hits.fields
        assert "channel_id" in self.hits.fields
        assert "t" in self.hits.fields
        assert "tot" in self.hits.fields
        assert "a" in self.hits.fields
        assert "trig" in self.hits.fields
        assert "id" in self.hits.fields


class TestOfflineTracks(unittest.TestCase):
    def setUp(self):
        self.f = OFFLINE_FILE
        self.tracks = OFFLINE_FILE.events.tracks
        self.tracks_numucc = OFFLINE_NUMUCC
        self.mc_tracks = OFFLINE_MC_TRACK.mc_tracks
        self.mc_tracks_old = OFFLINE_MC_TRACK_USR.mc_tracks
        self.n_events = 10
        self.status = [100, 5, 11, 15, 1, 12, 12, 12, 12, 12]
        self.mother_id = [-1, -1, 1, 1, 0, 2, 5, 5, 6, 8]

    def test_fields(self):
        for field in [
            "id",
            "pos_x",
            "pos_y",
            "pos_z",
            "dir_x",
            "dir_y",
            "dir_z",
            "t",
            "E",
            "len",
            "lik",
            "rec_type",
            "rec_stages",
            "fitinf",
        ]:
            getattr(self.tracks, field)

    def test_status(self):
        assert np.allclose(self.status, self.mc_tracks[1].status[:10].tolist())

    def test_mother_id(self):
        assert np.allclose(self.mother_id, self.mc_tracks[1].mother_id[:10].tolist())

    def test_attribute_error_raised_for_older_files(self):
        with self.assertRaises(AttributeError):
            self.mc_tracks_old[1].mother_id
        with self.assertRaises(AttributeError):
            self.mc_tracks_old[1].status

    def test_item_selection(self):
        self.assertListEqual(
            list(self.tracks[0].dir_z[:2]), [-0.872885221293917, -0.872885221293917]
        )

    def test_repr(self):
        assert "10" in repr(self.tracks)

    def test_slicing(self):
        tracks = self.tracks
        self.assertEqual(10, len(tracks))  # 10 events
        self.assertEqual(56, len(tracks[0].id))  # number of tracks in first event
        track_selection = tracks[2:7]
        assert 5 == len(track_selection)
        track_selection_2 = tracks[1:3]
        assert 2 == len(track_selection_2)
        for _slice in [
            slice(0, 1),
            slice(0, 2),
            slice(1, 5),
            slice(3, -2),
        ]:
            print(f"checking {_slice}")
            self.assertListEqual(
                list(tracks.E[:, 0][_slice]), list(tracks[_slice].E[:, 0])
            )

    def test_nested_indexing(self):
        self.assertAlmostEqual(
            self.f.events.tracks.fitinf[3:5][1][9][2],
            self.f.events[3:5].tracks[1].fitinf[9][2],
        )
        self.assertAlmostEqual(
            self.f.events.tracks.fitinf[3:5][1][9][2],
            self.f.events[3:5][1].tracks.fitinf[9][2],
        )


class TestMisc(unittest.TestCase):
    def test_mc_tracks_counter(self):
        r = OfflineReader(data_path("gseagen/DAT000001.gSeaGen.1.aa.root"))
        np.testing.assert_allclose(
            [0, 0, 6, 7, 0, 0, 2, 53, 0, 0, 6, 57, 0], r.mc_tracks.counter[0][:13]
        )


class TestBranchIndexingMagic(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events

    def test_slicing_magic(self):
        self.assertEqual(318, self.events[2:4].n_hits[0])
        assert np.allclose(
            self.events[3].tracks.dir_z[10], self.events.tracks.dir_z[3, 10]
        )
        assert np.allclose(
            self.events[3:6].tracks.pos_y[:, 0].tolist(),
            self.events.tracks.pos_y[3:6, 0].tolist(),
        )

    def test_selecting_specific_items_via_a_list(self):
        # test selecting with a list
        self.assertEqual(3, len(self.events[[0, 2, 3]]))

    def test_selecting_specific_items_via_a_numpy_array(self):
        # test selecting with a list
        self.assertEqual(3, len(self.events[np.array([0, 2, 3])]))

    def test_selecting_specific_items_via_a_awkward_array(self):
        # test selecting with a list
        self.assertEqual(3, len(self.events[ak.Array([0, 2, 3])]))


class TestBranchHighLevelAccessor(unittest.TestCase):
    def test_tracks_arrays(self):
        pos_xy = OFFLINE_FILE.tracks.arrays(["pos_x", "pos_y"])
        n = len(pos_xy)
        for i in range(n):
            assert np.allclose(
                OFFLINE_FILE.tracks.pos_x.tolist()[i], pos_xy.pos_x.tolist()[i]
            )


class TestUsr(unittest.TestCase):
    def setUp(self):
        self.f = OFFLINE_USR

    def test_str_flat(self):
        print(self.f.events.usr)

    def test_keys_flat(self):
        self.assertListEqual(
            [
                "RecoQuality",
                "RecoNDF",
                "CoC",
                "ToT",
                "ChargeAbove",
                "ChargeBelow",
                "ChargeRatio",
                "DeltaPosZ",
                "FirstPartPosZ",
                "LastPartPosZ",
                "NSnapHits",
                "NTrigHits",
                "NTrigDOMs",
                "NTrigLines",
                "NSpeedVetoHits",
                "NGeometryVetoHits",
                "ClassficationScore",
            ],
            self.f.events.usr_names[0].tolist(),
        )


class TestMcTrackUsr(unittest.TestCase):
    def setUp(self):
        self.f = OFFLINE_MC_TRACK_USR

    def test_usr_names(self):
        n_tracks = len(self.f.events)
        for i in range(3):
            self.assertListEqual(
                ["bx", "by", "ichan", "cc"],
                self.f.events.mc_tracks.usr_names[i][0].tolist(),
            )
            self.assertListEqual(
                ["energy_lost_in_can"],
                self.f.events.mc_tracks.usr_names[i][1].tolist(),
            )

    def test_usr(self):
        assert np.allclose(
            [0.0487, 0.0588, 3, 2],
            self.f.events.mc_tracks.usr[0][0].tolist(),
            atol=0.0001,
        )
        assert np.allclose(
            [0.147, 0.4, 3, 2], self.f.events.mc_tracks.usr[1][0].tolist(), atol=0.001
        )
