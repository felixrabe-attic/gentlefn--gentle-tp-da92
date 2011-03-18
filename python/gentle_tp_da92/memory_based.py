#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Memory-Based Data Store Implementation Module.

Provides basic, memory-based data store classes, implemented in Python.

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

from   hashlib import sha256

from   . import data_store_interfaces
from   .utilities import *


class _GentleDB(data_store_interfaces._GentleDB):
    """
    Base class for Gentle TP-DA92 memory-based databases.
    """

    def __init__(self):
        super(_GentleDB, self).__init__()
        self.db = {}

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        content = self.db[identifier]
        return content

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        del self.db[identifier]

    def find(self, partial_identifier=""):
        validate_identifier_format(partial_identifier, partial=True)
        identifiers = [i for i in self.db if i.startswith(partial_identifier)]
        return identifiers

    def __contains__(self, identifier):
        validate_identifier_format(identifier)
        return identifier in self.db


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def __add__(self, byte_string):
        content_identifier = sha256(byte_string).hexdigest()
        if not content_identifier in self.db:
            self.db[content_identifier] = byte_string
        return content_identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def __setitem__(self, pointer_identifier, content_identifier):
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        self.db[pointer_identifier] = content_identifier
        return pointer_identifier


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self):
        super(GentleDataStore, self).__init__()
        self.content_db = _GentleContentDB()
        self.pointer_db = _GentlePointerDB()
