# -*- coding: utf-8 -*-
"""stillness.managers -- Can you manage the stillness?
"""
import sys
import copy

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from versioners import Versions

from path import path

__path__ = path(__file__).abspath().dirname()

__all__ = ['Assetmanager', 'FileMap']

_RECURSION_LIMIT = sys.getrecursionlimit() - 2  # Just to be safe...!

YUI_COMPRESSOR = __path__ / 'yuicompressor-2.4.2.jar'


class FileMap(dict):
    """A recursive dictionary. Watch out for infinite loops!
    """
    def __init__(self, manager, *args, **kwargs):
        self.manager = manager
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

    def combine_files(self):
        for file_key in self:
            file_path = self.managers.options['common_path'] / file_key
            to_combine = self[file_key]

    def _combine(self, *filepaths):
        """Combine the given files into one buffer, using the configured delimiter.
        """
        buffer = StringIO()
        delimiter = self.options['delimiter']
        for fp in filepaths:
            fp = path(fp)
            buffer.write(delimiter % {'name': fp.name})
            buffer.write(fp.text())
        return buffer.getvalue()


class AssetManager(object):
    defaults = dict(
        common_path = path('.'),
        delimiter = '\n/* BEGIN %(name)s */\n',

        css_map = dict(),
        css_asset_pattern = r'(?P<url>url(\([\'"]?(?P<filename>[^)]+\.[a-z]{3,4})(?P<fragment>#\w+)?[\'"]?\)))',
        js_map = dict(),
        asset_paths = {
            '.': {},
            },
        default_asset_options = dict(
            pattern = r'.+(?!\.[0-9a-z]{8})(\.(png|jpg|gif|swf|ico))',
            recurse = True,
            versioner = 'SHA1Sum',
            ),

        css_compress_cmd = 'java -jar %(YUICOMPRESSOR)s --type css',
        js_compress_cmd = 'java -jar %(YUICOMPRESSOR)s --type js',

        css_link = '<link rel="%(alt)sstylesheet" type="%(type)s" href="%(href)s" media="%(media)s" %(title)s%(class)s/>\n',
        css_link_defaults = {
            'alt': '',
            'type': 'text/css',
            'title': '',
            'class': '',
            },
        script_link = '<script type="%(type)s" charset="%(charset)s" src="%(src)s"></script>\n',
        script_defaults = {
            'type': 'text/javascript',
            'charset': 'utf-8',
            },
        )

    def __init__(self, **kwargs):
        self.options = copy.deepcopy(self.defaults)
        self.options.update(**kwargs)
        self.options['common_path'] = path(self.options['common_path'])
        self.options['css_map'] = FileMap(self, self.options['css_map'])
        self.options['js_map'] = FileMap(self, self.options['js_map'])
        self.versions = Versions()

    def find_assets(self):
        """Find assets matching the configured patterns.

        Yields two-tuples of (configured_asset_path, absolute_path_to_asset)
        """
        for asset_path, options in self.options['asset_paths'].iteritems():
            o = copy.deepcopy(self.options['default_asset_options'])
            o.update(options)
            if o['recurse']:
                for f in path(asset_path).walkfilesRE(o['pattern']):
                    yield f
            else:
                for f in path(asset_path).listdirRE(o['pattern']):
                    yield (asset_path, f)
