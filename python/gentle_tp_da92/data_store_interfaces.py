#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Data Store Interfaces Module.

Defines the interfaces used by the data store implementation module classes.
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


class _GentleDB(object):
    """
    Base class for Gentle TP-DA92 databases implemented in Python.

    Gentle TP-DA92 databases map identifiers to values.  The current
    implementations use 256-bit identifiers, represented as 64 lower-case
    hexadecimal digits (regex: '[0-9a-f]{64}').

    Classes inheriting from _GentleDB strive to emulate standard Python
    container types to the greatest extent possible.

    Usage example:
    >>> gentle_db = _GentleDB()
    >>> gentle_db[identifier]
    'Content.'
    >>> gentle_db.find(identifier[:10])
    ['<identifier>']
    """

    def __init__(self, *a, **k):
        super(_GentleDB, self).__init__(*a, **k)

    def __getitem__(self, identifier):
        """
        Get an item from the database.
        """
        return None

    def find(self, partial_identifier=""):
        """
        Find all the identifiers registered in this database that start with
        partial_identifier.  Return an unsorted list.  The list may be empty.

        If partial_identifier is not specified (default is ""), return the full
        list of all identifiers in the database.
        """
        return []

    def keys(self):
        """
        Alias for self.find("").

        Do not override this method in subclasses.
        """
        return self.find("")

    def __contains__(self, identifier):
        """
        Return True if the database contains content for the specified
        identifier, and False otherwise.
        """
        return False


class _GentleContentDB(_GentleDB):
    """
    A Gentle TP-DA92 content database.

    Usage example:
    >>> gentle_content_db = _GentleContentDB()
    >>> content_identifier = gentle_content_db + "Some content"
    >>> gentle_content_db[content_identifier]
    'Some content'
    >>> del gentle_content_db[content_identifier]
    """

    def __add__(self, byte_string):
        """
        Enter content into the content database and return its content
        identifier.

        The content identifier is a hash value of the content.  Current
        implementations use the SHA-256 value of the content as the content
        identifier.

        This method gives priority to pre-existing content.  This means that
        content will not be saved if its hash value already exists as a key in
        the database.

        Example:
        >>> identifier = content_db + "some content"
        """
        return None


class _GentlePointerDB(_GentleDB):
    """
    A Gentle TP-DA92 pointer database.

    Usage example:
    >>> gentle_pointer_db = _GentlePointerDB()
    >>> new_ptr_id = gentle_tp_da92.utilities.random()
    >>> gentle_pointer_db[new_ptr_id] = content_identifier      # __setitem__
    >>> gentle_pointer_db[new_ptr_id] == content_identifier     # __getitem__
    True
    >>> del gentle_pointer_db[new_ptr_id]
    """

    def __setitem__(self, pointer_identifier, content_identifier):
        """
        Create or change a pointer in the pointer database.
        """
        # Tries to return pointer_identifier - would be awesome if that worked
        # for self[x]=y!  If you need this return value, use
        # self.__setitem__(x,y) instead.
        return None

    def __delitem__(self, pointer_identifier):
        """
        Delete a pointer from the database.
        """
        pass


class GentleDataStore(object):
    """
    The Gentle TP-DA92 data store, consisting of one content database
    (attribute 'content_db') and one pointer database (attribute 'pointer_db').
    """

    def __init__(self, *a, **k):
        super(GentleDataStore, self).__init__(*a, **k)
        self.content_db = None
        self.pointer_db = None
