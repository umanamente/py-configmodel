# -*- coding: utf-8 -*-
import unittest

from configmodel.MixinCachedValues import MixinCachedValues


class TestMixinCachedValues(unittest.TestCase):

    def test_set_not_dirty(self):
        """
        Test that _set_not_dirty() sets all cached values to not dirty
        """
        mixin1 = MixinCachedValues()
        mixin1._is_dirty = True
        mixin1._set_not_dirty()
        self.assertFalse(mixin1._is_dirty)
        mixin1.set_cached_value(["a", "b"], "value")
        self.assertTrue(mixin1._is_dirty)
        self.assertTrue(mixin1._cached_values["a.b"].is_dirty)
        mixin1._set_not_dirty()
        self.assertFalse(mixin1._is_dirty)

    def test_set_values_not_dirty(self):
        """
        Test that set_cached_value() sets cached value to not dirty
        """
        mixin1 = MixinCachedValues()
        self.assertFalse(mixin1._is_dirty)
        mixin1.set_cached_value(["a", "b"], "value", is_dirty=False)
        self.assertFalse(mixin1._is_dirty)
        self.assertFalse(mixin1._cached_values["a.b"].is_dirty)

    def test_get_set_values(self):
        """
        Test that get_cached_value() and set_cached_value() work
        """
        mixin1 = MixinCachedValues()
        self.assertIsNone(mixin1.get_cached_value(["a", "b"]))
        mixin1.set_cached_value(["a", "b"], "value")
        self.assertTrue(mixin1._is_dirty)
        self.assertEqual("value", mixin1.get_cached_value(["a", "b"]))
        self.assertIsNone(mixin1.get_cached_value(["z", "x"]))
        mixin1.set_cached_value(["z", "x"], "value2")
        self.assertEqual("value2", mixin1.get_cached_value(["z", "x"]))


if __name__ == '__main__':
    unittest.main()

