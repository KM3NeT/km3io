#!/usr/bin/env python3

import unittest
from km3io.tools import _to_num, cached_property, _unfold_indices


class TestToNum(unittest.TestCase):
    def test_to_num(self):
        self.assertEqual(10, _to_num("10"))
        self.assertEqual(10.5, _to_num("10.5"))
        self.assertEqual("test", _to_num("test"))
        self.assertIsNone(_to_num(None))


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
        assert data[indices[0]][indices[1]] == _unfold_indices(data, indices)

        indices = [slice(1, 9, 2), slice(1, 4), 2]
        assert data[indices[0]][indices[1]][indices[2]] == _unfold_indices(
            data, indices)

    def test_unfold_indices_raises_index_error(self):
        data = range(10)
        indices = [slice(2, 5), 99]
        with self.assertRaises(IndexError):
            _unfold_indices(data, indices)
