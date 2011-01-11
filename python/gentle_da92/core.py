#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91) - Core Module

Unique Gentle identifier for this Gentle Technology Preview:
    da92de4118f6fa915b6bdd73f090ad57dc153082600855e5c7a85e8fe054c5a1

The functionality of the Gentle Core is the result of years of development and
careful design.  The explicit goal of Gentle is to drastically simplify
computer programming and user interfaces.
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

from gentle_da92.core_utils import *


class _GentleDB(object):
    """
    Base class for the Gentle databases.

    Classes inheriting from _GentleDB strive to emulate standard Python
    container types to the greatest extent possible.

    Usage summary:
    >>> gentle_db = _GentleDB(location)
    >>> gentle_db[identifier]
    'Content.'
    >>> del gentle_db[identifier]
    """

    def __init__(self, location):
        self.location = location

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.location, identifier)
        result = open(filename, "rb").read()
        return result

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        filename = os.path.join(self.location, identifier)
        os.remove(filename)


class GentleContentDB(_GentleDB):
    """
    Represents the Gentle content database.
    """

    def append(self, byte_string):
        """
        Enter content into the content database and return its SHA-256 content
        identifier.
        """
        content_identifier = sha256(byte_string)
        filename = os.path.join(self.location, content_identifier)
        if not os.path.exists(filename):  # Give priority to pre-existing content.
            create_file_with_mode(filename, 0400).write(byte_string)
        return content_identifier


class GentlePointerDB(_GentleDB):
    """
    Represents the Gentle pointer database.
    """

    def __setitem__(self, pointer_identifier, content_identifier):
        """
        Create or change a pointer in the pointer database.
        """
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        filename = os.path.join(self.location, pointer_identifier)
        create_file_with_mode(filename, 0600).write(content_identifier)
        return pointer_identifier


class GentleData(object):

    def __init__(self, location):
        self.location = os.path.abspath(location)
        self.content_db = GentleContentDB(os.path.join(self.location, "content_db"))
        self.pointer_db = GentlePointerDB(os.path.join(self.location, "pointer_db"))
