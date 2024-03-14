#!/usr/bin/env python3

import unittest
import awkward as ak
import numpy as np
from pathlib import Path

from numpy.testing import assert_almost_equal, assert_allclose

from km3net_testdata import data_path
from km3io.definitions import fitparameters as kfit

from km3io import OfflineReader
from km3io.tools import (
    to_num,
    cached_property,
    unfold_indices,
    unique,
    uniquecount,
    fitinf,
    count_nested,
    mask,
    best_track,
    get_w2list_param,
    get_multiplicity,
    has_jmuon,
    has_jshower,
    has_aashower,
    has_dusjshower,
    best_jmuon,
    best_jshower,
    best_aashower,
    best_dusjshower,
    is_cc,
    usr,
    is_bit_set,
    is_3dshower,
    is_mxshower,
    is_3dmuon,
    is_nanobeacon,
    TimeConverter,
    phi,
    theta,
    zenith,
    azimuth,
    angle,
    angle_between,
    magnitude,
    unit_vector,
)


OFFLINE_FILE = OfflineReader(data_path("offline/km3net_offline.root"))
OFFLINE_USR = OfflineReader(data_path("offline/usr-sample.root"))
OFFLINE_MC_TRACK_USR = OfflineReader(
    data_path(
        "offline/mcv5.11r2.gsg_muonCChigherE-CC_50-5000GeV.km3_AAv1.jterbr00004695.jchain.aanet.498.root"
    )
)
OFFLINE_JMERGEFIT = OfflineReader(
    data_path(
        "offline/mcv5.0.gsg_elec-CC_10-100GeV.km3sim.JDK.jte.jmergefit.orca.aanet.909.evtsample.root"
    )
)
GENHEN_OFFLINE_FILE = OfflineReader(
    data_path("offline/mcv5.1.genhen_anumuNC.sirene.jte.jchain.aashower.sample.root")
)
GSEAGEN_OFFLINE_FILE = OfflineReader(data_path("offline/numucc.root"))


class TestFitinf(unittest.TestCase):
    def setUp(self):
        self.tracks = OFFLINE_FILE.events.tracks
        self.fit = self.tracks.fitinf
        self.best = self.tracks[:, 0]
        self.best_fit = self.best.fitinf

    def test_fitinf_from_all_events(self):
        beta = fitinf(kfit.JGANDALF_BETA0_RAD, self.tracks)

        assert beta[0][0] == self.fit[0][0][0]
        assert beta[0][1] == self.fit[0][1][0]
        assert beta[0][2] == self.fit[0][2][0]

        beta1 = fitinf(kfit.JGANDALF_BETA1_RAD, self.tracks)

        self.assertAlmostEqual(0.003417848024252858, beta1[0][1])
        self.assertAlmostEqual(0.0035514113196960105, beta1[3][2])

    def test_fitinf_from_one_event(self):
        beta = fitinf(kfit.JGANDALF_BETA0_RAD, self.best)

        assert beta[0] == self.best_fit[0][0]
        assert beta[1] == self.best_fit[1][0]
        assert beta[2] == self.best_fit[2][0]

        beta1 = fitinf(kfit.JGANDALF_BETA1_RAD, self.best)

        assert np.allclose(
            [
                0.003417848024252858,
                0.009401304503949024,
                0.0015619992272287897,
                0.0035514113196960105,
                0.014331655995648987,
                0.020507433510666175,
                0.019360118783263776,
                0.014202233969464604,
                0.0024146277135960043,
                0.006569492242345319,
            ],
            list(beta1),
        )


class TestBestTrackSelection(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events
        self.one_event = OFFLINE_FILE.events[0]

    def test_best_track_selection_from_multiple_events_with_explicit_stages_in_list(
        self,
    ):
        best = best_track(self.events.tracks, stages=[1, 3, 5, 4])

        assert len(best) == 10

        assert best.rec_stages[0].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[1].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[2].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[3].tolist() == [1, 3, 5, 4]

        # test with a shorter set of rec_stages
        best2 = best_track(self.events.tracks, stages=[1, 3])

        assert len(best2) == 10

        assert best2.rec_stages[0].tolist() == [1, 3]
        assert best2.rec_stages[1].tolist() == [1, 3]
        assert best2.rec_stages[2].tolist() == [1, 3]
        assert best2.rec_stages[3].tolist() == [1, 3]

        # test the importance of order in rec_stages in lists
        best3 = best_track(self.events.tracks, stages=[3, 1])

        assert len(best3) == 10

        assert best3.rec_stages[0] is None
        assert best3.rec_stages[1] is None
        assert best3.rec_stages[2] is None
        assert best3.rec_stages[3] is None

    def test_best_track_selection_from_multiple_events_with_a_set_of_stages(
        self,
    ):
        best = best_track(self.events.tracks, stages={1, 3, 4, 5})

        assert len(best) == 10

        assert best.rec_stages[0].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[1].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[2].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[3].tolist() == [1, 3, 5, 4]

        # test with a shorter set of rec_stages
        best2 = best_track(self.events.tracks, stages={1, 3})

        assert len(best2) == 10

        for rec_stages in best2.rec_stages:
            for stage in {1, 3}:
                assert stage in rec_stages

    def test_best_track_selection_from_multiple_events_with_start_end(self):
        best = best_track(self.events.tracks, startend=(1, 4))

        assert len(best) == 10

        assert best.rec_stages[0].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[1].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[2].tolist() == [1, 3, 5, 4]
        assert best.rec_stages[3].tolist() == [1, 3, 5, 4]

        # test with shorter stages
        best2 = best_track(self.events.tracks, startend=(1, 3))

        assert len(best2) == 10

        assert best2.rec_stages[0].tolist() == [1, 3]
        assert best2.rec_stages[1].tolist() == [1, 3]
        assert best2.rec_stages[2].tolist() == [1, 3]
        assert best2.rec_stages[3].tolist() == [1, 3]

        # test the importance of start as a real start of rec_stages
        best3 = best_track(self.events.tracks, startend=(0, 3))

        assert len(best3) == 10

        assert best3.rec_stages[0] is None
        assert best3.rec_stages[1] is None
        assert best3.rec_stages[2] is None
        assert best3.rec_stages[3] is None

        # test the importance of end as a real end of rec_stages
        best4 = best_track(self.events.tracks, startend=(1, 10))

        assert len(best4) == 10

        assert best4.rec_stages[0] is None
        assert best4.rec_stages[1] is None
        assert best4.rec_stages[2] is None
        assert best4.rec_stages[3] is None

    def test_best_track_from_a_single_event(self):
        # stages as a list
        best = best_track(self.one_event.tracks, stages=[1, 3, 5, 4])

        assert best.lik == ak.max(self.one_event.tracks.lik)
        assert np.allclose(best.rec_stages.tolist(), [1, 3, 5, 4])

        # stages as a set
        best2 = best_track(self.one_event.tracks, stages={1, 3, 4, 5})

        assert best2.lik == ak.max(self.one_event.tracks.lik)
        assert np.allclose(best2.rec_stages.tolist(), [1, 3, 5, 4])

        # stages with start and end
        best3 = best_track(self.one_event.tracks, startend=(1, 4))

        assert best3.lik == ak.max(self.one_event.tracks.lik)
        assert np.allclose(best3.rec_stages.tolist(), [1, 3, 5, 4])

    def test_best_track_on_slices_one_event(self):
        tracks_slice = self.one_event.tracks[self.one_event.tracks.rec_type == 4000]

        # test stages with list
        best = best_track(tracks_slice, stages=[1, 3, 5, 4])

        assert best.lik == ak.max(tracks_slice.lik)
        assert best.rec_stages.tolist() == [1, 3, 5, 4]

        # test stages with set
        best2 = best_track(tracks_slice, stages={1, 3, 4, 5})

        assert best2.lik == ak.max(tracks_slice.lik)
        assert best2.rec_stages.tolist() == [1, 3, 5, 4]

    def test_best_track_on_slices_with_start_end_one_event(self):
        tracks_slice = self.one_event.tracks[0:5]
        best = best_track(tracks_slice, startend=(1, 4))

        assert best.lik == ak.max(tracks_slice.lik)
        assert best.rec_stages[0] == 1
        assert best.rec_stages[-1] == 4

    def test_best_track_on_slices_with_explicit_rec_stages_one_event(self):
        tracks_slice = self.one_event.tracks[0:5]
        best = best_track(tracks_slice, stages=[1, 3, 5, 4])

        assert best.lik == ak.max(tracks_slice.lik)
        assert best.rec_stages[0] == 1
        assert best.rec_stages[-1] == 4

    def test_best_track_on_slices_multiple_events(self):
        tracks_slice = self.events[0:5].tracks

        # stages in list
        best = best_track(tracks_slice, stages=[1, 3, 5, 4])

        assert len(best) == 5

        assert np.allclose(
            best.lik.tolist(),
            [
                294.6407542676734,
                96.75133289411137,
                560.2775306614813,
                278.2872951665753,
                99.59098153341449,
            ],
        )
        for i in range(len(best)):
            assert best.rec_stages[i].tolist() == [1, 3, 5, 4]

        # stages in set
        best = best_track(tracks_slice, stages={3, 4, 5})

        assert len(best) == 5

        assert np.allclose(
            best.lik.tolist(),
            [
                294.6407542676734,
                96.75133289411137,
                560.2775306614813,
                278.2872951665753,
                99.59098153341449,
            ],
        )
        for i in range(len(best)):
            assert best.rec_stages[i].tolist() == [1, 3, 5, 4]

        # using start and end
        start, end = (1, 4)
        best = best_track(tracks_slice, startend=(start, end))

        assert len(best) == 5

        assert np.allclose(
            best.lik.tolist(),
            [
                294.6407542676734,
                96.75133289411137,
                560.2775306614813,
                278.2872951665753,
                99.59098153341449,
            ],
        )
        for i in range(len(best)):
            rs = best.rec_stages[i].tolist()
            assert rs[0] == start
            assert rs[-1] == end

    def test_best_track_raises_when_unknown_stages(self):
        with self.assertRaises(ValueError):
            best_track(self.events.tracks)

    def test_best_track_raises_when_too_many_inputs(self):
        with self.assertRaises(ValueError):
            best_track(self.events.tracks, startend=(1, 4), stages=[1, 3, 5, 4])


class TestHasJmuon(unittest.TestCase):
    def test_has_jmuon(self):
        assert ak.sum(has_jmuon(OFFLINE_JMERGEFIT.events.tracks)) == len(
            OFFLINE_JMERGEFIT.events.tracks
        )


class TestHasJshower(unittest.TestCase):
    def test_has_jshower(self):
        assert ak.sum(has_jshower(OFFLINE_JMERGEFIT.events.tracks)) == len(
            OFFLINE_JMERGEFIT.events.tracks
        )


class TestHasAashower(unittest.TestCase):
    def test_has_aashower(self):
        # there are no aashower events in this file
        assert ak.sum(has_aashower(OFFLINE_JMERGEFIT.events.tracks)) == 0


class TestHasDusjshower(unittest.TestCase):
    def test_has_dusjshower(self):
        # there are no dusj events in this file
        assert ak.sum(has_dusjshower(OFFLINE_JMERGEFIT.events.tracks)) == 0


class TestBestJmuon(unittest.TestCase):
    def test_best_jmuon(self):
        best = best_jmuon(OFFLINE_FILE.events.tracks)

        assert len(best) == 10

        jmuon_stages = [1, 3, 5, 4]

        assert best.rec_stages[0].tolist() == jmuon_stages
        assert best.rec_stages[1].tolist() == jmuon_stages
        assert best.rec_stages[2].tolist() == jmuon_stages
        assert best.rec_stages[3].tolist() == jmuon_stages

        assert best.lik[0] == ak.max(OFFLINE_FILE.events.tracks.lik[0])
        assert best.lik[1] == ak.max(OFFLINE_FILE.events.tracks.lik[1])
        assert best.lik[2] == ak.max(OFFLINE_FILE.events.tracks.lik[2])


class TestBestJshower(unittest.TestCase):
    def test_best_jshower(self):
        best = best_jshower(OFFLINE_JMERGEFIT.events.tracks)

        assert len(best) == 10

        jshower_stages = [101, 106, 102, 105, 107, 103]

        assert best.rec_stages[0].tolist() == jshower_stages
        assert best.rec_stages[1].tolist() == jshower_stages
        assert best.rec_stages[2].tolist() == jshower_stages
        assert best.rec_stages[3].tolist() == jshower_stages

        jshower_mask = mask(
            OFFLINE_JMERGEFIT.events.tracks.rec_stages, sequence=jshower_stages
        )
        jshower_tracks = OFFLINE_JMERGEFIT.events.tracks[jshower_mask]

        assert best.lik[0] == ak.max(jshower_tracks.lik[0])
        assert best.lik[1] == ak.max(jshower_tracks.lik[1])
        assert best.lik[2] == ak.max(jshower_tracks.lik[2])


class TestBestAashower(unittest.TestCase):
    def test_best_aashower(self):
        # there are no aashower events in this file
        best = best_aashower(OFFLINE_FILE.events.tracks)

        assert len(best) == 10

        assert best.rec_stages[0] is None
        assert best.rec_stages[1] is None
        assert best.rec_stages[2] is None
        assert best.rec_stages[3] is None

        assert best.lik[0] is None
        assert best.lik[1] is None
        assert best.lik[2] is None


class TestBestDusjshower(unittest.TestCase):
    def test_best_dusjshower(self):
        # there are no dusj events in this file
        best = best_dusjshower(OFFLINE_FILE.events.tracks)

        assert len(best) == 10

        assert best.rec_stages[0] is None
        assert best.rec_stages[1] is None
        assert best.rec_stages[2] is None
        assert best.rec_stages[3] is None

        assert best.lik[0] is None
        assert best.lik[1] is None
        assert best.lik[2] is None


class TestGetMultiplicity(unittest.TestCase):
    def test_get_multiplicity(self):
        multiplicity = get_multiplicity(OFFLINE_FILE.events.tracks, [1, 3, 5, 4])

        assert len(multiplicity) == 10
        assert multiplicity[0] == 1
        assert multiplicity[1] == 1
        assert multiplicity[2] == 1
        assert multiplicity[3] == 1

        # test with no nexisting rec_stages
        multiplicity2 = get_multiplicity(OFFLINE_FILE.events.tracks, [1, 2, 3, 4, 5])

        assert len(multiplicity2) == 10
        assert multiplicity2[0] == 0
        assert multiplicity2[1] == 0
        assert multiplicity2[2] == 0
        assert multiplicity2[3] == 0


class TestCountNested(unittest.TestCase):
    def test_count_nested(self):
        fit = OFFLINE_FILE.events.tracks.fitinf

        assert count_nested(fit, axis=0) == 10
        assert count_nested(fit, axis=1)[0:4].tolist() == [56, 55, 56, 56]
        assert count_nested(fit, axis=2)[0][0:4].tolist() == [17, 11, 8, 8]


class TestRecStagesMasks(unittest.TestCase):
    def setUp(self):
        self.nested = ak.Array(
            [
                [[1, 2, 3], [1, 2, 3], [1]],
                [[0], [1, 2, 3]],
                [[0], [0, 1, 3], [0], [1, 2, 3], [1, 2, 3]],
            ]
        )

        self.tracks = OFFLINE_FILE.events.tracks

    def test_mask_with_explicit_rec_stages_in_list_with_multiple_events(self):
        rec_stages = self.tracks.rec_stages
        stages = [1, 3, 5, 4]
        masks = mask(self.tracks.rec_stages, sequence=stages)

        assert masks[0][0] == all(rec_stages[0][0] == ak.Array(stages))
        assert masks[1][0] == all(rec_stages[1][0] == ak.Array(stages))
        assert masks[0][1] == False

    def test_mask_with_atleast_on_multiple_events(self):
        stages = [1, 3, 4, 5]
        masks = mask(self.tracks.rec_stages, atleast=stages)
        tracks = self.tracks[masks]

        assert 1 in tracks.rec_stages[0][0]
        assert 3 in tracks.rec_stages[0][0]
        assert 4 in tracks.rec_stages[0][0]
        assert 5 in tracks.rec_stages[0][0]

    def test_mask_with_start_and_end_of_rec_stages_with_multiple_events(self):
        rec_stages = self.tracks.rec_stages
        stages = [1, 3, 5, 4]
        masks = mask(self.tracks.rec_stages, startend=(1, 4))

        assert masks[0][0] == all(rec_stages[0][0] == ak.Array(stages))
        assert masks[1][0] == all(rec_stages[1][0] == ak.Array(stages))
        assert masks[0][1] == False

    def test_mask_with_start_and_end_of_rec_stages_signle_event(self):
        rec_stages = self.tracks.rec_stages[0][0]
        stages = [1, 3, 5, 4]
        track = self.tracks[0]
        masks = mask(track.rec_stages, startend=(1, 4))

        assert track[masks].rec_stages[0][0] == 1
        assert track[masks].rec_stages[0][-1] == 4

    def test_mask_with_explicit_rec_stages_with_single_event(self):
        rec_stages = self.tracks.rec_stages[0][0]
        stages = [1, 3]
        track = self.tracks[0]
        masks = mask(track.rec_stages, sequence=stages)

        assert track[masks].rec_stages[0][0] == stages[0]
        assert track[masks].rec_stages[0][1] == stages[1]

    def test_mask_raises_when_no_inputs(self):
        with self.assertRaises(ValueError):
            mask(self.tracks)


class TestMask(unittest.TestCase):
    def test_minmax_2dim_mask(self):
        arr = ak.Array([[1, 2, 3, 4], [3, 4, 5], [1, 2, 5]])
        m = mask(arr, minmax=(1, 4))
        self.assertListEqual(m.tolist(), [True, False, False])

    def test_minmax_3dim_mask(self):
        arr = ak.Array([[[1, 2, 3, 4], [3, 4, 5], [1, 2, 5]], [[1, 2, 3]]])
        m = mask(arr, minmax=(1, 4))
        self.assertListEqual(m.tolist(), [[True, False, False], [True]])

    def test_minmax_4dim_mask(self):
        arr = ak.Array(
            [[[[1, 2, 3, 4], [3, 4, 5], [1, 2, 5]], [[1, 2, 3]]], [[[1, 9], [3, 3]]]]
        )
        m = mask(arr, minmax=(1, 4))
        self.assertListEqual(
            m.tolist(), [[[True, False, False], [True]], [[False, True]]]
        )


class TestUnique(unittest.TestCase):
    def run_random_test_with_dtype(self, dtype):
        max_range = 100
        for i in range(23):
            low = np.random.randint(0, max_range)
            high = np.random.randint(low + 1, low + 2 + np.random.randint(max_range))
            n = np.random.randint(max_range)
            arr = np.random.randint(low, high, n).astype(dtype)
            np_reference = np.sort(np.unique(arr))
            result = np.sort(unique(arr, dtype=dtype))
            try:
                np.allclose(np_reference, result, atol=1e-1)
            except ValueError:
                print("low:", low)
                print("high:", high)
                print("n:", n)
                print("arr =", list(arr))
                print("np.unique(arr) =", np_reference)
                print("unique(arr) =", result)
                assert False

    def test_unique_with_dtype_int8(self):
        self.run_random_test_with_dtype(np.int8)

    def test_unique_with_dtype_int16(self):
        self.run_random_test_with_dtype(np.int16)

    def test_unique_with_dtype_int32(self):
        self.run_random_test_with_dtype(np.int32)

    def test_unique_with_dtype_int64(self):
        self.run_random_test_with_dtype(np.int64)

    def test_unique_with_dtype_uint8(self):
        self.run_random_test_with_dtype(np.uint8)

    def test_unique_with_dtype_uint16(self):
        self.run_random_test_with_dtype(np.uint16)

    def test_unique_with_dtype_uint32(self):
        self.run_random_test_with_dtype(np.uint32)

    def test_unique_with_dtype_uint64(self):
        self.run_random_test_with_dtype(np.uint64)


class TestUniqueCount(unittest.TestCase):
    def test_uniquecount(self):
        arr = ak.Array([[1, 2, 3], [2, 2, 2], [3, 4, 5, 6, 6], [4, 4, 3, 1]])
        assert np.allclose([3, 1, 4, 3], uniquecount(arr))

    def test_uniquecount_with_empty_subarrays(self):
        arr = ak.Array([[1, 2, 3], [2, 2, 2], [], [4, 4, 3, 1]])
        assert np.allclose([3, 1, 0, 3], uniquecount(arr))


class TestToNum(unittest.TestCase):
    def test_to_num(self):
        self.assertEqual(10, to_num("10"))
        self.assertEqual(10.5, to_num("10.5"))
        self.assertEqual("test", to_num("test"))
        self.assertIsNone(to_num(None))


class TestCachedProperty(unittest.TestCase):
    def test_cached_property(self):
        class Test:
            @cached_property
            def prop(self):
                pass

        self.assertTrue(isinstance(Test.prop, cached_property))


class TestUnfoldIndices(unittest.TestCase):
    def test_unfold_indices(self):
        data = range(10)

        indices = [slice(2, 5), 0]
        assert data[indices[0]][indices[1]] == unfold_indices(data, indices)

        indices = [slice(1, 9, 2), slice(1, 4), 2]
        assert data[indices[0]][indices[1]][indices[2]] == unfold_indices(data, indices)

    def test_unfold_indices_raises_index_error(self):
        data = range(10)
        indices = [slice(2, 5), 99]
        with self.assertRaises(IndexError):
            unfold_indices(data, indices)


class TestIsCC(unittest.TestCase):
    def test_is_cc(self):
        NC_file = is_cc(GENHEN_OFFLINE_FILE)
        CC_file = is_cc(GSEAGEN_OFFLINE_FILE)

        self.assertFalse(
            all(NC_file) == True
        )  # this test fails because the CC flags are not reliable in old files
        self.assertTrue(all(CC_file) == True)


class TestUsr(unittest.TestCase):
    def test_event_usr(self):
        assert np.allclose(
            [118.6302815337638, 44.33580521344907, 99.93916717621543],
            usr(OFFLINE_USR.events, "CoC").tolist(),
        )
        assert np.allclose(
            [37.51967774166617, -10.280346193553832, 13.67595659707355],
            usr(OFFLINE_USR.events, "DeltaPosZ").tolist(),
        )

    def test_mc_tracks_usr(self):
        assert np.allclose(
            [0.0487],
            usr(OFFLINE_MC_TRACK_USR.mc_tracks[0], "bx").tolist(),
            atol=0.0001,
        )


class TestIsBitSet(unittest.TestCase):
    def test_is_bit_set_for_single_values(self):
        value = 2  # 10
        assert not is_bit_set(value, 0)
        assert is_bit_set(value, 1)
        value = 42  # 101010
        assert not is_bit_set(value, 0)
        assert is_bit_set(value, 1)
        assert not is_bit_set(value, 2)
        assert is_bit_set(value, 3)
        assert not is_bit_set(value, 4)
        assert is_bit_set(value, 5)

    def test_is_bit_set_for_lists(self):
        values = [2, 42, 4]
        assert np.allclose([True, True, False], is_bit_set(values, 1))

    def test_is_bit_set_for_numpy_arrays(self):
        values = np.array([2, 42, 4])
        assert np.allclose([True, True, False], is_bit_set(values, 1))

    def test_is_bit_set_for_awkward_arrays(self):
        values = ak.Array([2, 42, 4])
        assert np.allclose([True, True, False], list(is_bit_set(values, 1)))


class TestTriggerMaskChecks(unittest.TestCase):
    def test_is_3dshower(self):
        assert np.allclose(
            [True, True, True, True, True, False, False, True, True, True],
            list(is_3dshower(OFFLINE_FILE.events.trigger_mask)),
        )
        assert np.allclose(
            [True, True, True, True, True, True, True, True, True, False],
            list(is_3dshower(GENHEN_OFFLINE_FILE.events.trigger_mask)),
        )

    def test_is_mxshower(self):
        assert np.allclose(
            [True, True, True, True, True, True, True, True, True, True],
            list(is_mxshower(OFFLINE_FILE.events.trigger_mask)),
        )
        assert np.allclose(
            [False, False, False, False, False, False, False, False, False, False],
            list(is_mxshower(GENHEN_OFFLINE_FILE.events.trigger_mask)),
        )

    def test_is_3dmuon(self):
        assert np.allclose(
            [True, True, True, True, True, False, False, True, True, True],
            list(is_3dmuon(OFFLINE_FILE.events.trigger_mask)),
        )
        assert np.allclose(
            [False, False, False, True, False, False, True, False, True, True],
            list(is_3dmuon(GENHEN_OFFLINE_FILE.events.trigger_mask)),
        )

    def test_is_nanobeacon(self):
        assert np.allclose(
            [False, False, False, False, False, False, False, False, False, False],
            list(is_nanobeacon(OFFLINE_FILE.events.trigger_mask)),
        )
        assert np.allclose(
            [False, False, False, False, False, False, False, False, False, False],
            list(is_nanobeacon(GENHEN_OFFLINE_FILE.events.trigger_mask)),
        )


class TestTimeConverter(unittest.TestCase):
    def setUp(self):
        self.one_event = GENHEN_OFFLINE_FILE.events[5]
        self.tconverter = TimeConverter(self.one_event)

    def test_get_time_of_frame(self):
        t_frame = self.tconverter.get_time_of_frame(self.one_event.frame_index)

        assert t_frame < self.one_event.mc_t
        assert t_frame % self.tconverter.FRAME_TIME_NS == 0

    def test_get_DAQ_time(self):
        t_DAQ = self.tconverter.get_DAQ_time(self.one_event.mc_hits.t)

        assert all(t_DAQ < self.tconverter.FRAME_TIME_NS)

    def test_get_MC_time(self):
        t_frame = self.tconverter.get_time_of_frame(self.one_event.frame_index)
        t_MC = self.tconverter.get_MC_time(self.one_event.hits.t)

        assert all(
            np.fabs(self.one_event.mc_t + t_MC - t_frame)
            < self.tconverter.FRAME_TIME_NS
        )


class TestMath(unittest.TestCase):
    def setUp(self):
        self.v = np.array([0.26726124, 0.53452248, 0.80178373])
        self.vecs = np.array(
            [
                [0.0, 0.19611614, 0.98058068],
                [0.23570226, 0.23570226, 0.94280904],
                [0.53452248, 0.26726124, 0.80178373],
                [0.80178373, 0.26726124, 0.53452248],
                [0.94280904, 0.23570226, 0.23570226],
            ]
        )

    def test_phi(self):
        print(phi((1, 0, 0)))
        assert_almost_equal(0, phi((1, 0, 0)))
        assert_almost_equal(np.pi, phi((-1, 0, 0)))
        assert_almost_equal(np.pi / 2, phi((0, 1, 0)))
        assert_almost_equal(np.pi / 2 * 3, phi((0, -1, 0)))
        assert_almost_equal(np.pi / 2 * 3, phi((0, -1, 0)))
        assert_almost_equal(0, phi((0, 0, 0)))
        assert_almost_equal(phi(self.v), 1.10714872)
        assert_almost_equal(
            phi(self.vecs),
            np.array([1.57079633, 0.78539816, 0.46364761, 0.32175055, 0.24497866]),
        )

    def test_zenith(self):
        assert_allclose(np.pi, zenith((0, 0, 1)))
        assert_allclose(0, zenith((0, 0, -1)))
        assert_allclose(np.pi / 2, zenith((0, 1, 0)))
        assert_allclose(np.pi / 2, zenith((0, -1, 0)))
        assert_allclose(np.pi / 4 * 3, zenith((0, 1, 1)))
        assert_allclose(np.pi / 4 * 3, zenith((0, -1, 1)))
        assert_almost_equal(zenith(self.v), 2.5010703409103687)
        assert_allclose(
            zenith(self.vecs),
            np.array([2.94419709, 2.80175574, 2.50107034, 2.13473897, 1.80873745]),
        )

    def test_azimuth(self):
        self.assertTrue(np.allclose(np.pi, azimuth((1, 0, 0))))
        self.assertTrue(np.allclose(0, azimuth((-1, 0, 0))))

        print(azimuth((0, 1, 0)))
        print(azimuth((0, -1, 0)))
        print(azimuth((0, 0, 0)))
        print(azimuth(self.v))
        print(azimuth(self.vecs))
        self.assertTrue(np.allclose(np.pi / 2 * 3, azimuth((0, 1, 0))))
        self.assertTrue(np.allclose(np.pi / 2, azimuth((0, -1, 0))))
        self.assertTrue(np.allclose(np.pi, azimuth((0, 0, 0))))
        self.assertTrue(np.allclose(azimuth(self.v), 4.24874137138))
        self.assertTrue(
            np.allclose(
                azimuth(self.vecs),
                np.array([4.71238898, 3.92699082, 3.60524026, 3.46334321, 3.38657132]),
            )
        )

    def test_theta(self):
        print(theta((0, 0, -1)))
        print(theta((0, 0, 1)))
        print(theta((0, 1, 0)))
        print(theta((0, -1, 0)))
        print(theta((0, 1, 1)))
        print(theta((0, -1, 1)))
        print(theta(self.v))
        print(theta(self.vecs))
        self.assertTrue(np.allclose(0, theta((0, 0, 1))))
        self.assertTrue(np.allclose(np.pi, theta((0, 0, -1))))
        self.assertTrue(np.allclose(np.pi / 2, theta((0, 1, 0))))
        self.assertTrue(np.allclose(np.pi / 2, theta((0, -1, 0))))
        self.assertTrue(np.allclose(0, theta((0, 1, 1))))
        self.assertTrue(np.allclose(0, theta((0, -1, 1))))
        self.assertTrue(np.allclose(theta(self.v), 0.64052231))
        self.assertTrue(
            np.allclose(
                theta(self.vecs),
                np.array([0.19739554, 0.33983691, 0.64052231, 1.00685369, 1.3328552]),
            )
        )

    def test_unit_vector(self):
        v1 = (1, 0, 0)
        v2 = (1, 1, 0)
        v3 = (-1, 2, 0)
        assert np.allclose(v1, unit_vector(v1))
        assert np.allclose(np.array(v2) / np.sqrt(2), unit_vector(v2))
        assert np.allclose(np.array(v3) / np.sqrt(5), unit_vector(v3))

    def test_magnitude(self):
        assert 1 == magnitude(np.array([1, 0, 0]))
        assert 2 == magnitude(np.array([0, 2, 0]))
        assert 3 == magnitude(np.array([0, 0, 3]))
        assert np.allclose(
            [3.74165739, 8.77496439, 13.92838828],
            magnitude(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
        )

    def test_angle(self):
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        v3 = np.array([-1, 0, 0])
        self.assertAlmostEqual(0, angle(v1, v1))
        self.assertAlmostEqual(np.pi / 2, angle(v1, v2))
        self.assertAlmostEqual(np.pi, angle(v1, v3))
        self.assertAlmostEqual(angle(self.v, v1), 1.3002465638163236)
        self.assertAlmostEqual(angle(self.v, v2), 1.0068536854342678)
        self.assertAlmostEqual(angle(self.v, v3), 1.8413460897734695)

        assert np.allclose(
            [1.300246563816323, 1.0068536854342678, 1.8413460897734695],
            angle(np.array([self.v, self.v, self.v]), np.array([v1, v2, v3])),
        )

    def test_angle_between(self):
        v1 = (1, 0, 0)
        v2 = (0, 1, 0)
        v3 = (-1, 0, 0)
        self.assertAlmostEqual(0, angle_between(v1, v1))
        self.assertAlmostEqual(np.pi / 2, angle_between(v1, v2))
        self.assertAlmostEqual(np.pi, angle_between(v1, v3))
        self.assertAlmostEqual(angle_between(self.v, v1), 1.3002465638163236)
        self.assertAlmostEqual(angle_between(self.v, v2), 1.0068536854342678)
        self.assertAlmostEqual(angle_between(self.v, v3), 1.8413460897734695)

        assert np.allclose(
            [0.0, 0.0, 0.0]
            - angle_between(np.array([v1, v2, v3]), np.array([v1, v2, v3]), axis=1),
            0,
        )
        assert np.allclose(
            [np.pi / 2, np.pi]
            - angle_between(np.array([v1, v1]), np.array([v2, v3]), axis=1),
            0,
        )

        self.assertTrue(
            np.allclose(
                angle_between(self.vecs, v1),
                np.array([1.57079633, 1.3328552, 1.0068537, 0.64052231, 0.33983691]),
            )
        )
        self.assertTrue(
            np.allclose(
                angle_between(self.vecs, v2),
                np.array([1.37340077, 1.3328552, 1.3002466, 1.30024656, 1.3328552]),
            )
        )
        self.assertTrue(
            np.allclose(
                angle_between(self.vecs, v3),
                np.array([1.57079633, 1.80873745, 2.13473897, 2.50107034, 2.80175574]),
            )
        )
