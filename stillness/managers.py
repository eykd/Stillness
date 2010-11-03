# -*- coding: utf-8 -*-
"""stillness.managers -- Can you manage the stillness?
"""
import sys
import copy
import subprocess
import itertools
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from versioners import Versions

from path import path

__path__ = path(__file__).abspath().dirname()

__all__ = ['Assetmanager', 'FileMap']

_RECURSION_LIMIT = sys.getrecursionlimit() - 2  # Just to be safe...!

YUICOMPRESSOR = __path__ / 'yuicompressor-2.4.2.jar'


class FileMap(dict):
    """A recursive dictionary. Watch out for infinite loops!
    """
    def __init__(self, manager, kind, *args, **kwargs):
        self.manager = manager
        self.kind = kind
        super(FileMap, self).__init__(*args, **kwargs)

    def _recurse_included_filekeys(self, filekey, callcount=0):
        """Process the given file map recursively, expanding included files.
    
        @param to_file_key: The filename on the left of the map to combine to.
        """
        if callcount == _RECURSION_LIMIT:
            raise RuntimeError("Hit the recursion limit while trying to include recursively-mapped files. Perhaps your have a loop?")
        for inc_key in self.get(filekey, ()):
            if inc_key in self:
                for rfk in self._recurse_included_filekeys(inc_key, callcount+1):
                    yield rfk
            else:
                yield inc_key

    def __getitem__(self, key):
        return list(self._recurse_included_filekeys(key))

    def minify_command(self):
        if self.kind == 'js':
            return self.manager.options['js']['minify_cmd']
        elif self.kind == 'css':
            return self.manager.options['css']['minify_cmd']
        else:
            return 'cat'
    minify_command = property(minify_command)

    def minify(self):
        if self.kind == 'js':
            return self.manager.options['js']['minify']
        elif self.kind == 'css':
            return self.manager.options['css']['minify']
        else:
            return True
    minify = property(minify)

    def combine_files(self):
        """Combine the mapped files, minifying if specified.
        """
        common_path = self.manager.options['common_path']
        build_path = self.manager.options['build_path']
        for file_key in self:
            out_path = build_path / file_key
            to_combine = self[file_key]
            combined = self.combine(*(common_path / fk for fk in to_combine))
            if self.minify:
                combined = self._minify_text(combined)
            fo = out_path.open('w')
            try:
                fo.write(combined)
            finally:
                fo.close()

    def _minify_text(self, text):
        compressor = subprocess.Popen(self.minify_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        compressed = compressor.communicate(text)[0]
        return compressed

    def _combine(self, *filepaths):
        """Combine the given files into one buffer, using the configured delimiter.
        """
        buffer = StringIO()
        delimiter = self.manager.options['delimiter']
        for fp in filepaths:
            fp = path(fp)
            buffer.write(delimiter % {'name': fp.name})
            buffer.write(fp.text())
        return buffer.getvalue()


class AssetManager(object):
    defaults = dict(
        debug = True,

        common_path = path('media'),
        build_path = path('build'),
        base_urls = ['/media'],
        delimiter = '\n/* BEGIN %(name)s */\n',

        css = dict(
            map = dict(),

            minify = True,
            version = True,
            versioner = 'SHA1Sum',

            asset_pattern = r'(?P<url>url(\([\'"]?(?P<filename>[^)]+\.[a-z]{3,4})(?P<fragment>#\w+)?[\'"]?\)))',
            minify_cmd = 'java -jar %(YUICOMPRESSOR)s --type css' % {'YUICOMPRESSOR': YUICOMPRESSOR},
            html = '<link rel="%(alt)sstylesheet" type="%(type)s" href="%(href)s" media="%(media)s" %(title)s%(class)s/>\n',
            html_defaults = {
                'alt': '',
                'type': 'text/css',
                'title': '',
                'class': '',
                },
            ),

        js = dict(
            minify = True,
            version = True,
            versioner = 'SHA1Sum',

            map = dict(),
            minify_cmd = 'java -jar %(YUICOMPRESSOR)s --type js' % {'YUICOMPRESSOR': YUICOMPRESSOR},
            html = '<script type="%(type)s" charset="%(charset)s" src="%(src)s"></script>\n',
            html_defaults = {
                'type': 'text/javascript',
                'charset': 'utf-8',
                },
            ),

        assets = dict(
            paths = {
                '.': {},
                },
            default_options = dict(
                pattern = r'.+(?!\.[0-9a-z]{8})(\.(png|jpg|gif|swf|ico))',
                recurse = True,
                version = True,
                versioner = 'SHA1Sum',
                ),
            ),

        
        )

    def __init__(self, **kwargs):
        self.options = copy.deepcopy(self.defaults)
        merge_dictionary(self.options, kwargs)
        self.options['common_path'] = path(self.options['common_path'])
        self.options['css']['map'] = FileMap(self, 'css', self.options['css']['map'])
        self.options['js']['map'] = FileMap(self, 'js', self.options['js']['map'])
        self.base_url_iter = itertools.cycle(self.options['base_urls'])
        self.versions = Versions()

    def find_assets(self):
        """Find assets matching the configured patterns.

        Yields two-tuples of (configured_asset_path, absolute_path_to_asset)
        """
        common_path = path(self.options['common_path'])
        for asset_path, options in self.options['assets']['paths']:
            o = copy.deepcopy(self.options['assets']['default_options'])
            merge_dictionary(o, options)
            if o['recurse']:
                for f in (common_path /asset_path).walkfilesRE(o['pattern']):
                    yield f
            else:
                for f in (common_path / asset_path).listdirRE(o['pattern']):
                    yield (asset_path, f)

    def timestamp_url(self, url):
        return '%s?time=%s' % (url, time.time())

    def get_asset_url(self, file_key):
        """Return the URL for the given asset file key.

        If more than one base URL is specified, each call to this
        method will use the next base url.
        """
        if file_key.startswith('http'):
            url = file_key
        else:
            base_url = self.base_url_iter.next()
            url = "%(base_url)s/%(file_key)s" % locals()

        if self.options['debug']:
            url = self.timestamp_url(url)

        return url

    def get_css_urls(self, file_key):
        """Return the URLs for the given CSS asset file key.

        If more than one base URL is specified, each call to this
        method will use the next base url.
        """
        if self.options['debug']:
            return [self.get_asset_url(css) for css in self.options['css']['map'][file_key]]
        else:
            self.options['css']['map'][file_key]  # Make sure it's defined.
            return [self.get_asset_url(file_key)]

    def get_js_urls(self, file_key):
        """Return the URLs for the given JS asset file key.

        If more than one base URL is specified, each call to this
        method will use the next base url.
        """
        if self.options['debug']:
            return [self.get_asset_url(css) for css in self.options['js']['map'][file_key]]
        else:
            self.options['js']['map'][file_key]  # Make sure it's defined.
            return [self.get_asset_url(file_key)]


def merge_dictionary(dst, src):
    """Merge the src dictionary into the dst dictionary, recursively.

    This function recursively walks the items and values of two dict
    like objects. At each level when a key exists in both, and each
    value is a dict, then the destination dict is updated from the
    source dict usiing the builtin dict.update method. After the
    operation all keys and values from the source, at any level, will
    be referenced in the destination.

    Based on:
        http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/#c1
    """
    stack = [(dst, src)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if isinstance(current_src[key], dict) and isinstance(current_dst[key], dict) :
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst