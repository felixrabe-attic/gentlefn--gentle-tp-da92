#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Filesystem-Based Data Store Implementation Module.

Provides basic, filesystem-based data store classes, implemented in Python.
gentle_tp_da92.fs_based.GentleDataStore operates on the following directory
tree:

    .../<data store top directory>/
        content_db/
            1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd
            4567cdef4567cdef4567cdef4567cdef4567cdef4567cdef4567cdef4567cdef
            ... (files containing the real content; name = SHA-256(content))
        pointer_db/
            3456bcde3456bcde3456bcde3456bcde3456bcde3456bcde3456bcde3456bcde
            5678fedc5678fedc5678fedc5678fedc5678fedc5678fedc5678fedc5678fedc
            ... (files containing names of content; name = random)

It is recommended to use the gentle_tp_da92.easy module in applications, instead
of directly using the data store implementation modules.

For documentation on the interfaces of the classes provided by this module, see
the gentle_tp_da92.data_store_interfaces module.
"""
# Copyright (C) 2010, 2011  Felix Rabe
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

import glob
from   hashlib import sha256
import os

from   . import data_store_interfaces
from   .utilities import *


class _GentleDB(data_store_interfaces._GentleDB):
    """
    Base class for Gentle TP-DA92 filesystem-based databases.
    """

    def __init__(self, directory, mkdir=False):
        super(_GentleDB, self).__init__()
        self.directory = directory
        if mkdir and not os.path.exists(self.directory):
            os.mkdir(self.directory, 0700)

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.directory, identifier)
        content = open(filename, "rb").read()
        return content

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.directory, identifier)
        os.remove(filename)

    def find_identifiers_starting_with(self, partial_identifier):
        partial_filename = os.path.join(self.directory, partial_identifier)
        matches = glob.glob(partial_filename + "*")
        identifiers = sorted(os.path.basename(m) for m in matches)
        return identifiers


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def append(self, byte_string):
        content_identifier = sha256(byte_string).hexdigest()
        filename = os.path.join(self.directory, content_identifier)
        if not os.path.exists(filename):
            create_file_with_mode(filename, 0400).write(byte_string)
        return content_identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def __setitem__(self, pointer_identifier, content_identifier):
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        filename = os.path.join(self.directory, pointer_identifier)
        create_file_with_mode(filename, 0600).write(content_identifier)
        return pointer_identifier


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, directory, mkdir=False):
        super(GentleDataStore, self).__init__()
        self.directory = os.path.abspath(directory)
        if mkdir and not os.path.exists(self.directory):
            os.mkdir(self.directory, 0700)

        self._content_db = _GentleContentDB(
            os.path.join(self.directory, "content_db"), mkdir=mkdir)

        self._pointer_db = _GentlePointerDB(
            os.path.join(self.directory, "pointer_db"), mkdir=mkdir)
