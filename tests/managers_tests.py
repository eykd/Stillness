# -*- coding: utf-8 -*-
"""managers_tests.py -- tests for the AssetManager and FileMap.
"""
import unittest

from stillness import managers


class FileMapTests(unittest.TestCase):
    def setUp(self):
        self.test_map = managers.FileMap({
            'foo': ['bar', 'baz', 'bizbar'],  # Includes baz
            'baz': ['phlegm', 'auto', 'biz'],  # Includes biz
            'biz': ['blah', 'blaz'],
            })

    def test_include_recursive_files(self):
        self.assertEqual(self.test_map['foo'],
                         ['bar', 'phlegm', 'auto', 'blah', 'blaz', 'bizbar'])
