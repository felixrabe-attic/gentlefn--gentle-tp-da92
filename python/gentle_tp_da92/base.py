#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Base Module.

Provides the basic, filesystem-based database classes, implemented in Python.
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

from hashlib import sha256

from .utilities import *


class GentleBaseDB(object):
    """
    Base class for the Gentle TP-DA92 databases.

    Classes inheriting from GentleBaseDB strive to emulate standard Python
    container types to the greatest extent possible.

    Usage summary:
    >>> gentle_db = GentleBaseDB(directory)
    >>> gentle_db[identifier]
    'Content.'
    >>> del gentle_db[identifier]
    """

    def __init__(self, directory):
        self.directory = directory

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.directory, identifier)
        result = open(filename, "rb").read()
        return result

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.directory, identifier)
        os.remove(filename)


class GentleContentDB(GentleBaseDB):
    """
    Represents the Gentle content database.
    """

    def append(self, byte_string):
        """
        Enter content into the content database and return its SHA-256 content
        identifier.
        """
        content_identifier = sha256(byte_string).hexdigest()
        filename = os.path.join(self.directory, content_identifier)
        if not os.path.exists(filename):  # Give priority to pre-existing content.
            create_file_with_mode(filename, 0400).write(byte_string)
        return content_identifier


class GentlePointerDB(GentleBaseDB):
    """
    Represents the Gentle pointer database.
    """

    def __setitem__(self, pointer_identifier, content_identifier):
        """
        Create or change a pointer in the pointer database.
        """
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        filename = os.path.join(self.directory, pointer_identifier)
        create_file_with_mode(filename, 0600).write(content_identifier)
        return pointer_identifier


class GentleDataStore(object):

    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        self.content_db = GentleContentDB(os.path.join(self.directory, "content_db"))
        self.pointer_db = GentlePointerDB(os.path.join(self.directory, "pointer_db"))
