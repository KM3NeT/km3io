#!/usr/bin/env python3

import unittest
import awkward1 as ak
import numpy as np
from pathlib import Path

from km3net_testdata import data_path

from km3io import OfflineReader
from km3io.tools import (to_num, cached_property, unfold_indices, unique,
                         uniquecount, fitinf, fitparams, count_nested, _find,
                         mask, best_track, rec_types, get_w2list_param,
                         get_multiplicity)

OFFLINE_FILE = OfflineReader(data_path("offline/km3net_offline.root"))


class TestFitinf(unittest.TestCase):
    def setUp(self):
        self.tracks = OFFLINE_FILE.events.tracks
        self.fit = self.tracks.fitinf
        self.best = self.tracks[:, 0]
        self.best_fit = self.best.fitinf

    def test_fitinf(self):
        beta = fitinf('JGANDALF_BETA0_RAD', self.tracks)
        best_beta = fitinf('JGANDALF_BETA0_RAD', self.best)

        assert beta[0][0] == self.fit[0][0][0]
        assert beta[0][1] == self.fit[0][1][0]
        assert beta[0][2] == self.fit[0][2][0]

        assert best_beta[0] == self.best_fit[0][0]
        assert best_beta[1] == self.best_fit[1][0]
        assert best_beta[2] == self.best_fit[2][0]

    def test_fitparams(self):
        keys = set(fitparams())

        assert "JGANDALF_BETA0_RAD" in keys


class TestRecoTypes(unittest.TestCase):
    def test_reco_types(self):
        keys = set(rec_types())

        assert "JPP_RECONSTRUCTION_TYPE" in keys


class TestBestTrack(unittest.TestCase):
    def setUp(self):
        self.events = OFFLINE_FILE.events
        self.one_event = OFFLINE_FILE.events[0]

    def test_best_track_selection_from_multiple_events_with_no_stages(self):
        longest = best_track(self.events.tracks, "JMUON")

        assert len(longest) == 10

        assert longest.rec_stages[0] == [1, 3, 5, 4]
        assert longest.rec_stages[1] == [1, 3, 5, 4]
        assert longest.rec_stages[2] == [1, 3, 5, 4]
        assert longest.rec_stages[3] == [1, 3, 5, 4]

    def test_best_track_selection_from_multiple_events_with_explicit_stages(
            self):
        best = best_track(self.events.tracks, "JMUON", stages=[1, 3, 5, 4])

        assert len(best) == 10

        assert best.rec_stages[0] == [1, 3, 5, 4]
        assert best.rec_stages[1] == [1, 3, 5, 4]
        assert best.rec_stages[2] == [1, 3, 5, 4]
        assert best.rec_stages[3] == [1, 3, 5, 4]

    def test_best_track_selection_from_multiple_events_with_start_end(self):
        best = best_track(self.events.tracks, "JMUON", start=1, end=4)
        best2 = best_track(self.events.tracks, "JMUON", start=1, end=3)

        assert len(best) == 10
        assert len(best2) == 10

        assert best.rec_stages[0] == [1, 3, 5, 4]
        assert best.rec_stages[1] == [1, 3, 5, 4]
        assert best.rec_stages[2] == [1, 3, 5, 4]
        assert best.rec_stages[3] == [1, 3, 5, 4]

        assert best2.rec_stages[0] == [1, 3]
        assert best2.rec_stages[1] == [1, 3]
        assert best2.rec_stages[2] == [1, 3]
        assert best2.rec_stages[3] == [1, 3]

    def test_best_track_raises_when_unknown_reco(self):
        with self.assertRaises(KeyError):
            best_track(self.events.tracks, "Zineb")

    def test_best_track_raises_when_start_or_end_not_valid(self):
        with self.assertRaises(ValueError):
            best_track(self.events.tracks, "JMUON", start=100, end=103)

    def test_best_track_raises_when_wrong_reco_stages(self):
        with self.assertRaises(KeyError):
            best_track(self.events.tracks, "JMUON", stages=[233, 100, 500])


#     def test_best_track_from_a_single_event(self):
#         first_track = best_track(self.one_event.tracks, strategy="first")
#         best = best_track(self.one_event.tracks,
#                           strategy="default",
#                           rec_type="JPP_RECONSTRUCTION_TYPE")

#         assert first_track.dir_z == self.one_event.tracks.dir_z[0]
#         assert first_track.lik == self.one_event.tracks.lik[0]

#         assert best.lik == ak.max(self.one_event.tracks.lik)
#         assert best.rec_type == 4000

#     def test_best_track_raises_when_unknown_strategy(self):
#         with self.assertRaises(ValueError):
#             best_track(self.events.tracks, strategy="Zineb")

#     def test_best_track_raises_when_default_strategy_and_no_rectype(self):
#         with self.assertRaises(ValueError):
#             best_track(self.events.tracks)

#     def test_best_track_on_slices(self):
#         tracks_slice = self.one_event.tracks[self.one_event.tracks.rec_type ==
#                                              4000]
#         first_track = best_track(tracks_slice, strategy="first")
#         best = best_track(tracks_slice,
#                           strategy="default",
#                           rec_type="JPP_RECONSTRUCTION_TYPE")

#         assert first_track.dir_z == self.one_event.tracks.dir_z[0]
#         assert first_track.lik == self.one_event.tracks.lik[0]

#         assert best.lik == ak.max(self.one_event.tracks.lik)
#         assert best.rec_type == 4000


class TestGetMultiplicity(unittest.TestCase):
    def test_get_multiplicity(self):
        rec_stages_tracks = get_multiplicity(OFFLINE_FILE.events.tracks,
                                             [1, 3, 5, 4])

        assert rec_stages_tracks.rec_stages[0] == [1, 3, 5, 4]
        assert rec_stages_tracks.rec_stages[1] == [1, 3, 5, 4]


class TestCountNested(unittest.TestCase):
    def test_count_nested(self):
        fit = OFFLINE_FILE.events.tracks.fitinf

        assert count_nested(fit, axis=0) == 10
        assert count_nested(fit, axis=1)[0:4] == ak.Array([56, 55, 56, 56])
        assert count_nested(fit, axis=2)[0][0:4] == ak.Array([17, 11, 8, 8])


class TestRecStagesMasks(unittest.TestCase):
    def setUp(self):
        self.nested = ak.Array([[[1, 2, 3], [1, 2, 3], [1]], [[0], [1, 2, 3]],
                                [[0], [0, 1, 3], [0], [1, 2, 3], [1, 2, 3]]])

        self.tracks = OFFLINE_FILE.events.tracks

    def test_find(self):
        builder = ak.ArrayBuilder()
        _find(self.nested, ak.Array([1, 2, 3]), builder)
        labels = builder.snapshot()

        assert labels[0][0] == 1
        assert labels[0][1] == 1
        assert labels[0][2] == 0
        assert labels[1][0] == 0

    def test_mask_with_explicit_rec_stages_with_multiple_events(self):
        rec_stages = self.tracks.rec_stages
        stages = [1, 3, 5, 4]
        masks = mask(self.tracks, stages=stages)

        assert masks[0][0] == all(rec_stages[0][0] == ak.Array(stages))
        assert masks[1][0] == all(rec_stages[1][0] == ak.Array(stages))
        assert masks[0][1] == False

    def test_mask_with_start_and_end_of_rec_stages_with_multiple_events(self):
        rec_stages = self.tracks.rec_stages
        stages = [1, 3, 5, 4]
        masks = mask(self.tracks, start=1, end=4)

        assert masks[0][0] == all(rec_stages[0][0] == ak.Array(stages))
        assert masks[1][0] == all(rec_stages[1][0] == ak.Array(stages))
        assert masks[0][1] == False

    def test_mask_with_start_and_end_of_rec_stages_signle_event(self):
        rec_stages = self.tracks.rec_stages[0][0]
        stages = [1, 3, 5, 4]
        track = self.tracks[0]
        masks = mask(track, start=1, end=4)

        assert track[masks].rec_stages[0][0] == 1
        assert track[masks].rec_stages[0][-1] == 4

    def test_mask_with_explicit_rec_stages_with_single_event(self):
        rec_stages = self.tracks.rec_stages[0][0]
        stages = [1, 3]
        track = self.tracks[0]
        masks = mask(track, stages=stages)

        assert track[masks].rec_stages[0][0] == stages[0]
        assert track[masks].rec_stages[0][1] == stages[1]


class TestUnique(unittest.TestCase):
    def run_random_test_with_dtype(self, dtype):
        max_range = 100
        for i in range(23):
            low = np.random.randint(0, max_range)
            high = np.random.randint(low + 1,
                                     low + 2 + np.random.randint(max_range))
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
        assert data[indices[0]][indices[1]][indices[2]] == unfold_indices(
            data, indices)

    def test_unfold_indices_raises_index_error(self):
        data = range(10)
        indices = [slice(2, 5), 99]
        with self.assertRaises(IndexError):
            unfold_indices(data, indices)
