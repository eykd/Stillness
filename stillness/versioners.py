# -*- coding: utf-8 -*-
"""stillness.versioners -- File content versioners for Stillness.
"""
import hashlib

import ConfigParser

try:
    import json
except ImportError:
    json = None

try:
    import yaml
except ImportError:
    yaml = None

from path import path

__all__ = ['Versions']


class Versions(dict):
    def mapVersions(self, method, common_path, *file_keys):
        """Build a version map, using the given method, from the given files.

        @param method: the versioning method to use. One of ( Sha1Sum | MD5Sum | FileTimestamp ).
        
        @common_path: the common filesystem path that should be prepended to each file key.

        @file_keys: the relative file paths for each filename to version, based off the common path.
        """
        versioner = getattr(self, method)
        for fn in file_keys:
            self[fn] = versioner(path(common_path) / fn)

    ### Versioners
    def SHA1Sum(klass, filename):
        return hashlib.sha1(path(filename).text()).hexdigest()[:8]

    def MD5Sum(klass, filename):
        return hashlib.md5(path(filename).text()).hexdigest()[:8]

    def FileTimestamp(klass, filename):
        return str(int(path(filename).st_mtime))

    ### Readers and writers
    def writeJSON(self, filename):
        """Write the version map to a JSON file.
        """
        if json is None:
            raise RuntimeError('json is not available.')
        
        fo = open(filename, mode='w')
        try:
            json.dump(dict(**self), stream=fo)
        finally:
            fo.close()

    def readJSON(self, filename):
        """Read the version map from a JSON file.
        """
        if json is None:
            raise RuntimeError('json is not available.')
        
        fi = open(filename, mode='r')
        try:
            self.update(json.load(stream=fi))
        finally:
            fi.close()

        return self

    def writeYAML(self, filename):
        """Write the version map to a YAML file.
        """
        if yaml is None:
            raise RuntimeError('yaml is not available.')
        
        fo = open(filename, mode='w')
        try:
            yaml.dump(dict(**self), stream=fo)
        finally:
            fo.close()

    def readYAML(self, filename):
        """Read the version map from a YAML file.
        """
        if yaml is None:
            raise RuntimeError('yaml is not available.')
        
        fi = open(filename, mode='r')
        try:
            self.update(yaml.load(stream=fi))
        finally:
            fi.close()

        return self
        
    def writeINI(self, filename):
        """Write the version map to an INI file.
        """
        cp = ConfigParser()
        for key, value in self.iteritems():
            cp.set('versions', key, value)
        fo = open(filename, 'wb')
        try:
            cp.write(fo)
        finally:
            fo.close()

    def readINI(self, filename):
        """Read the version map from an INI file.
        """
        cp = ConfigParser()
        fi = open(filename, 'rb')
        try:
            cp.read(fi)
        finally:
            fi.close()

        self.update(cp.items('versions'))
