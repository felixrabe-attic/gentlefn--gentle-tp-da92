#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides a read-only virtual filesystem that can be used by Gentle as its data
store.

Useful primarily for exporting directory structures into JSON structures.

Requires (Mac)FUSE, and fuse.py from http://code.google.com/p/fusepy/.  Should
run, with those components installed, (at least) on Linux 2.6 and Mac OS X 10.6.

Example:
$ alias gg='python -m gentle_da92de4118f6fa91_cli'
$ python -m gentle_da92.experimental.reversefs directory mountpoint
$ export GENTLE_DA92DE41_DIR=mountpoint
$ gg get 00000000

CAUTION: The implementation is very naive, so don't have too much data in the
directory that you use as the data source for mounting the file system, as all
of it will be loaded into memory at once.  This is not by design and can be
improved relatively easily; I just wanted to see quick results.
"""
# Copyright (C) 2011  Felix Rabe
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

__gentle_tp_da92_id__ = \
    "ef5d3e1949c2f663b21c5e78c0974f138fc25585817a85fbd70d46046b68b07d"

DEBUG = False

import errno
from   hashlib import sha256
import json
import os
import platform
import stat
import sys
import time

from fuse import FUSE, FuseOSError, Operations

from gentle_tp_da92.utilities import random

ROOT_POINTER = \
    "0000000000000000f8dc5728545c9273de850a6f25f259e28ce37a7f9048d4f4"
POINTER_GENERATION_NAMESPACE = \
    "9313eddcd7634162186b2c9b9c820ddd52ee45bf4ef7af732aa45dcef166cdde"
UPDATE_INTERVAL_IN_SECS = 5.0

_system = platform.system()

def _json_dumps(obj):
    json_string = json.dumps(obj, separators=(',',':'), sort_keys=True)
    return json_string

def interesting(method):
    "Decorator for debugging interesting methods."
    if not DEBUG: return method
    def wrapper(*a, **k):
        k_repr = ""
        if k:
            k_repr = ", **%r" % k
        a_repr = repr(a[1:])[1:-1]
        if a_repr.endswith(","): a_repr = a_repr[:-1]  # chop trailing ','
        print("CALL %s (%s%s)  " % (method.__name__, a_repr, k_repr), end="")
        try:
            r = method(*a, **k)
        except Exception as e:
            print(" =>   EXCEPTION %r" % e)
            raise
        else:
            print(" =>   %r" % (r,))
            return r
    return wrapper

class VirtualFile(object):
    def __init__(self, rootdir, content, *a, **k):
        super(VirtualFile, self).__init__(*a, **k)
        self._rootdir = rootdir
        self._content = content
    def get_content(self):
        return self._content
    def get_size(self):
        return len(self._content)
    def get_stat(self):
        stat_dict = dict(st_mode=stat.S_IFREG|0400, st_size=self.get_size())
        t = self._rootdir._last_reset_t
        for time_stat in "st_ctime st_mtime st_atime".split():
            stat_dict[time_stat] = t
        return stat_dict

class VirtualDirectory(dict):
    def __init__(self, rootdir, *a, **k):
        super(VirtualDirectory, self).__init__(*a, **k)
        self._rootdir = rootdir
    def get_stat(self):
        if _system == "Darwin":
            nlink = len(self) + 2
        else:
            nlink = len([x for x in self if isinstance(x, VirtualDirectory)]) + 2
        stat_dict = dict(st_mode=stat.S_IFDIR|0500, st_size=0, st_nlink=nlink)
        t = self._rootdir._last_reset_t
        for time_stat in "st_ctime st_mtime st_atime".split():
            stat_dict[time_stat] = t
        return stat_dict

class GentleRootDir(VirtualDirectory):

    def __init__(self, represented_directory, *a, **k):
        super(GentleRootDir, self).__init__(self, *a, **k)
        self._represented_dir = os.path.abspath(represented_directory)
        self._pointer_generation_namespace = random()
        self._last_reset_t = time.time() - 3600
        self.gentle_reset()

    def _gentle_reset_traversal(self, tree, path):
        for key, value in tree.items():
            del tree[key]
            new_path = "%s%s%s" % (path, os.path.sep, key)
            pointer_content = self._pointer_generation_namespace + new_path
            pointer = sha256(pointer_content).hexdigest()
            if isinstance(value, dict):  # value is a subtree
                key_suffix = ":json:pointer"
                content_hash = self._gentle_reset_traversal(value, new_path)
            else:  # value is content
                key_suffix = ":pointer"
                if key.endswith(".json"):
                    try:
                        # Compress the JSON string:
                        loaded_value = json.loads(value)
                        value = _json_dumps(loaded_value)
                    except:
                        pass
                    else:
                        key = key[:-5]
                        key_suffix = ":json:pointer"
                content_hash = self._cdbdir.add_content(value)
            self._pdbdir[pointer] = GentlePointer(self, content_hash)
            tree[key + key_suffix] = pointer
        json_string = json.dumps(tree, separators=(',',':'), sort_keys=True)
        content_hash = self._cdbdir.add_content(json_string)
        return content_hash

    # @interesting
    def gentle_reset(self):
        t = time.time()
        if t - self._last_reset_t < UPDATE_INTERVAL_IN_SECS: return
        self._last_reset_t = t
        self["content_db"] = self._cdbdir = GentleContentDir(self)
        self["pointer_db"] = self._pdbdir = GentlePointerDir(self)
        tree = {}
        for dirpath, dirnames, filenames in os.walk(self._represented_dir):
            dirparts = os.path.relpath(dirpath, self._represented_dir)
            dirparts = dirparts.split(os.path.sep)
            if dirparts == ["."]: dirparts = []
            current_tree = tree
            for part in dirparts:
                current_tree = current_tree[part]
            for fn in filenames:
                filepath = os.path.join(dirpath, fn)
                current_tree[fn] = open(filepath, "rb").read()
            for dn in dirnames:
                current_tree[dn] = {}
        content_hash = self._gentle_reset_traversal(tree, "")
        self._pdbdir[ROOT_POINTER] = GentlePointer(self, content_hash)

class GentleContentDir(VirtualDirectory):
    def __init__(self, *a, **k):
        super(GentleContentDir, self).__init__(*a, **k)
        self.add_content("{}")
        self.add_content('{"content:content":"%s"}' % self.add_content(""))
    def add_content(self, content):
        content_hash = sha256(content).hexdigest()
        self[content_hash] = GentleContent(self._rootdir, content)
        return content_hash

class GentlePointerDir(VirtualDirectory):
    def __init__(self, *a, **k):
        super(GentlePointerDir, self).__init__(*a, **k)

class GentlePointer(VirtualFile):
    pass

class GentleContent(VirtualFile):
    pass

class GentleReverseFS(Operations):

    def __init__(self, represented_directory):
        self._represented_directory = represented_directory
        self._virtual_root = GentleRootDir(self._represented_directory)
        self._fd = 0

    def _follow_path(self, path):
        path_parts = path.lstrip("/").split("/")
        virtual_directory = self._virtual_root
        if path_parts == [""]: return virtual_directory
        for ppart in path_parts:
            virtual_directory = virtual_directory.get(ppart)
            if virtual_directory is None: return None
        return virtual_directory  # leaf may also be VirtualFile

    def _get_fd(self):
        self._fd += 1
        return self._fd

    def readdir(self, path, fh):
        self._virtual_root.gentle_reset()
        virtual_dir = self._follow_path(path)
        content = [".", ".."]
        if virtual_dir is not None:
            content.extend(virtual_dir.keys())
        return content

    # @interesting
    def getattr(self, path, fh=None):
        self._virtual_root.gentle_reset()
        virtual_file = self._follow_path(path)
        if virtual_file is None:
            raise FuseOSError(errno.ENOENT)
        return virtual_file.get_stat()

    # @interesting
    def open(self, path, flags):
        self._virtual_root.gentle_reset()
        return self._get_fd()

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    # @interesting
    def read(self, path, size, offset, fh):
        virtual_file = self._follow_path(path)
        if not isinstance(virtual_file, VirtualFile):
            raise FuseOSError(errno.EIO)
        return virtual_file.get_content()[offset:offset + size]

def main():
    if len(sys.argv) != 3:
        print("Usage: %s <directory> <mountpoint>" % sys.argv[0])
        sys.exit(1)
    directory, mountpoint = sys.argv[1:3]
    if not DEBUG:
        foreground = False
    else:
        foreground = True
        ops = GentleReverseFS(directory)
        print(ops.readdir("/", 12345))
        print()
        print("#### FILESYSTEM LIVE FROM HERE ####")
        print()
    options = {}
    if _system == "Darwin":
        options.update(local=True, auto_cache=True)
    fuse = FUSE(GentleReverseFS(directory), mountpoint, foreground=foreground,
                **options)

if __name__ == "__main__":
    main()
