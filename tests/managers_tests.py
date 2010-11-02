# -*- coding: utf-8 -*-
"""managers_tests.py -- tests for the AssetManager and FileMap.
"""
import unittest

from stillness import managers
from stillness.path import path

__path__ = path(__file__).abspath().dirname()


class FileMapTests(unittest.TestCase):
    def setUp(self):
        manager = managers.AssetManager()
        self.test_map = managers.FileMap(manager, 'foo', {
                'foo': ['bar', 'baz', 'bizbar'],  # Includes baz
                'baz': ['phlegm', 'auto', 'biz'],  # Includes biz
                'biz': ['blah', 'blaz'],
                })

    def test_include_recursive_files(self):
        self.assertEqual(self.test_map['foo'],
                         ['bar', 'phlegm', 'auto', 'blah', 'blaz', 'bizbar'])


class AssetManagerTests(unittest.TestCase):
    def setUp(self):
        self.assets = managers.AssetManager(**self.options)

    def test_find_assets(self):
        assets = set(self.assets.find_assets())
        expected_assets = set((self.options['common_path'] / 'images').listdir())
        self.assertEqual(assets, expected_assets)

    options = dict(
        debug = True,

        common_path = __path__ / 'media',
        build_path = __path__ / 'build',
        urls = ['/media'],
        delimiter = '\n/* BEGIN %(name)s */\n',

        css = dict(
            map = {
                'css/main.min.css' : [
                    'css/_baseline/baseline.min.css',
                    'css/_less/less.min.css',
                    'css/grid.css',
                    'css/core.css',
                    'css/helpers.css',
                    'css/storylets.css',
                    'css/logos.css',

                    # Include print, inside `@media print` query.
                    'css/print.min.css',

                    # IE 5 hack patch.
                    'css/_patches/patch.css',
                    ],
                'css/_baseline/baseline.min.css' : [
                    'css/_baseline/baseline.reset.css',
                    'css/_baseline/baseline.base.css',
                    'css/_baseline/baseline.type.css',
                    'css/_baseline/baseline.table.css',
                    'css/_baseline/baseline.form.css',
                    #'css/_baseline/baseline.grid.css',
                    ],
                'css/_less/less.min.css' : [
                    'css/_less/_768px-default.css',
                    'css/_less/_767px.css',
                    'css/_less/1224px.css',
                    'css/_less/1824px.css',
                    'css/_less/overrides.css',
                    ],
                'css/print.min.css' : [
                    'css/_print/core.css',
                    ],
                'css/patch.win-ie-all.min.css' : [
                    'css/_patches/win-ie-all.css',
                    ],
                "css/patch.win-ie7.min.css" : [
                    "css/_patches/win-ie7.css",
                    ],

                "css/patch.win-ie-old.min.css" : [
                    "css/_patches/win-ie-old.css",
                    ],
                },

            minify = True,
            version = True,

            html = '<link rel="%(alt)sstylesheet" type="%(type)s" href="%(href)s" media="%(media)s" %(title)s%(class)s/>\n',
            ),

        js = dict(
            minify = True,
            version = True,

            map = {
                'js/main.min.js' : [
                    'js/_jquery/jquery.min.js',
                    'js/core.js',
                    'js/_hyphenator/hyphenator.min.js',
                    ],
                'js/_jquery/jquery.min.js' : [
                    'js/_jquery/jquery.1.4.2.js',
                    'js/_jquery/jquery.debug.js',
                    'js/_jquery/jquery.templates.js',
                    'js/_jquery/json2.js',
                    ],
                'js/modernizr.min.js' : [
                    'js/modernizr-1.5.js',
                    ],
                'js/_hyphenator/hyphenator.min.js' : [
                    'js/_hyphenator/Hyphenator.js',
                    'js/_hyphenator/patterns/en-us.js',
                    'js/_hyphenator/init.js',
                    ],
                'js/_patches/ie9.min.js' : [
                    'js/_patches/IE9.js',
                    ],
                'js/_patches/ie7.min.js' : [
                    'js/_patches/ie7-squish.js',
                    ],
                'js/_dev/dev.min.js' : [
                    'js/_dev/960.gridder.js',
                    ],
                'js/_dev/profiling/profiling.min.js' : [
                    'js/_dev/profiling/yahoo-profiling.js',
                    'js/_dev/profiling/config.js',
                    ],
                },
            html = '<script type="%(type)s" charset="%(charset)s" src="%(src)s"></script>\n',
            ),

        assets = dict(
            paths = (
                ('images', {}),
                ),
            ),
        )
