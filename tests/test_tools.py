#!/usr/bin/env python3

import unittest
import awkward1 as ak
import numpy as np
from km3io.tools import (to_num, cached_property, unfold_indices, unique,
                         uniquecount)


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
        assert data[indices[0]][indices[1]][indices[2]] == unfold_indices(
            data, indices)

    def test_unfold_indices_raises_index_error(self):
        data = range(10)
        indices = [slice(2, 5), 99]
        with self.assertRaises(IndexError):
            unfold_indices(data, indices)
