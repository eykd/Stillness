# -*- coding: utf-8 -*-
"""managers_tests.py -- tests for the AssetManager and FileMap.
"""
import unittest
import itertools
import time

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

        # Mock time.time to return deterministic results.
        self.oldtime = time.time
        time.time = lambda: 42

        #self.rmBuildPath()

    def tearDown(self):
        time.time = self.oldtime

        #self.rmBuildPath()

    def rmBuildPath(self):
        # Remove the build_path, if it exists.
        if self.options['build_path'].exists():
            self.options['build_path'].rmtree()

    def test_find_assets(self):
        assets = set(self.assets.find_assets())
        expected_assets = set((self.options['common_path'] / 'images').listdir())
        self.assertEqual(assets, expected_assets)

    def test_get_asset_url_debug_is_true(self):
        self.assets.options['debug'] = True
        for x in 'abcabc':
            url = self.assets.get_asset_url(x)
            self.assertEqual(url, "http://%(x)s.mycdn.org/media/%(x)s?time=42" % {'x': x})

    def test_get_asset_url_debug_is_false(self):
        self.assets.options['debug'] = False
        for x in 'abcabc':
            url = self.assets.get_asset_url(x)
            self.assertEqual(url, "http://%(x)s.mycdn.org/media/%(x)s" % {'x': x})

    def test_get_css_asset_urls_debug_is_true(self):
        self.assets.options['debug'] = True
        main_file_key = 'css/main.min.css'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_css_files = ["%s/%s?time=42" % (base_url_iter.next(), c)
                              for c in self.assets.options['css']['map'][main_file_key]]
        css_files = self.assets.get_css_urls(main_file_key)
        self.assertEqual(css_files, expected_css_files)

    def test_get_css_asset_urls_debug_is_false(self):
        self.assets.options['debug'] = False
        main_file_key = 'css/main.min.css'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_css_files = ["%s/%s" % (base_url_iter.next(), main_file_key)]
        css_files = self.assets.get_css_urls(main_file_key)
        self.assertEqual(css_files, expected_css_files)

    def test_get_js_asset_urls_debug_is_true(self):
        self.assets.options['debug'] = True
        main_file_key = 'js/main.min.js'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_js_files = ["%s/%s?time=42" % (base_url_iter.next(), c)
                              for c in self.assets.options['js']['map'][main_file_key]]
        js_files = self.assets.get_js_urls(main_file_key)
        self.assertEqual(js_files, expected_js_files)

    def test_get_js_asset_urls_debug_is_false(self):
        self.assets.options['debug'] = False
        main_file_key = 'js/main.min.js'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_js_files = ["%s/%s" % (base_url_iter.next(), main_file_key)]
        js_files = self.assets.get_js_urls(main_file_key)
        self.assertEqual(js_files, expected_js_files)

    def test_combine_files(self):
        self.rmBuildPath()
        self.assets.options['debug'] = False
        self.assets.options['css']['map'].combine_files()
        self.assets.options['js']['map'].combine_files()
        for file_key in (self.assets.options['css']['map'].keys() + self.assets.options['js']['map'].keys()):
            fp = (self.assets.options['build_path'] / file_key)
            self.assert_(fp.exists())

    def test_derive_absolute_url_from_relative(self):
        base_url = '/media'
        common_path = self.options['build_path']
        rel_fk_abs = [
            ('../images/foo.png', 'css/styles.css', '/media/images/foo.png?time=42'),
            ('/media/images/foo.png', 'css/styles.css', '/media/images/foo.png?time=42'),
            ]
        for rel_path, file_key, expected_abs_path in rel_fk_abs:
            abs_path = self.assets.options['css']['map']._derive_absolute_url_from_relative(
                base_url, file_key, rel_path
                )
            self.assertEqual(abs_path, expected_abs_path)
        
    def test_get_css_asset_html_debug_is_true(self):
        return
        self.assets.options['debug'] = True
        main_file_key = 'css/main.min.css'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_css_html = '\n'.join(
            '<link rel="stylesheet" type="text/css" href="%s/%s?time=42" media="all" />\n' % (base_url_iter.next(), c)
            for c in self.assets.options['css']['map'][main_file_key])
        css_html = self.assets.get_css_html(main_file_key)
        self.assertEqual(css_html, expected_css_html)

    def test_get_css_asset_html_debug_is_false(self):
        return
        self.assets.options['debug'] = False
        main_file_key = 'css/main.min.css'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_css_html = '<link rel="stylesheet" type="text/css" href="%s/%s?time=42" media="all" />\n\n' % (base_url_iter.next(), main_file_key)
        css_html = self.assets.get_css_html(main_file_key)
        self.assertEqual(css_html, expected_css_html)

    def test_get_js_asset_html_debug_is_true(self):
        return
        self.assets.options['debug'] = True
        main_file_key = 'js/main.min.js'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_js_html = '\n'.join(
            '<link rel="stylesheet" type="text/css" href="%s/%s?time=42" media="all" />\n\n' % (base_url_iter.next(), c)
            for c in self.assets.options['js']['map'][main_file_key]
            )
        js_html = self.assets.get_js_html(main_file_key)
        self.assertEqual(js_html, expected_js_html)

    def test_get_js_html_html_debug_is_false(self):
        return
        self.assets.options['debug'] = False
        main_file_key = 'js/main.min.js'
        base_url_iter = itertools.cycle(self.assets.options['base_urls'])
        expected_js_html = ["%s/%s" % (base_url_iter.next(), main_file_key)]
        js_html = self.assets.get_js_html(main_file_key)
        self.assertEqual(js_html, expected_js_html)

    options = dict(
        debug = True,

        common_path = __path__ / 'media',
        build_path = __path__ / 'build',
        base_urls = ['http://a.mycdn.org/media', 
                     'http://b.mycdn.org/media', 
                     'http://c.mycdn.org/media'],
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
                },
            html = '<script type="%(type)s" charset="%(charset)s" src="%(src)s"></script>\n',
            ),

        assets = dict(
            paths = (
                ('images', {}),
                ),
            ),
        )
