#!/usr/bin/env python3

import unittest
from km3io.tools import _to_num, cached_property


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
