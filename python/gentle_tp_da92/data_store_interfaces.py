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

    Gentle TP-DA92 databases map identifiers, consisting of 64 lower-case
    hexadecimal digits ([0-9a-f]), to values.

    Classes inheriting from GentleBaseDB strive to emulate standard Python
    container types to the greatest extent possible.

    Usage example:
    >>> gentle_db = _GentleDB()
    >>> gentle_db[identifier]
    'Content.'
    >>> gentle_db.find(identifier[:10])
    ['<identifier>']
    >>> del gentle_db[identifier]
    """

    def __init__(self, *a, **k):
        super(_GentleDB, self).__init__(*a, **k)

    def __getitem__(self, identifier):
        """
        Get an item from the database.
        """
        return None

    def __delitem__(self, identifier):
        """
        Delete an item from the database.
        """
        pass

    def find(self, partial_identifier=""):
        """
        Find all the identifiers registered in this database that start with
        partial_identifier.  Return an unsorted list.  The list may be empty.

        If partial_identifier is not specified (default is ""), return the full
        list of all identifiers.
        """
        return []

    def keys(self):
        """
        Alias for self.find("").
        """
        return self.find("")


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
        Enter content into the content database and return its SHA-256 sum as
        its content identifier.

        This method gives priority to pre-existing content.  This means that
        content will not be saved if its SHA-256 sum already exists as a key in
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
        # Would be awesome if that worked for self[x]=y!
        # If you need this return value, use self.__setitem__(x,y) instead.
        return None


class GentleDataStore(object):
    """
    The Gentle TP-DA92 data store, consisting of one content database
    (attribute 'content_db') and one pointer database (attribute 'pointer_db').
    """

    def __init__(self, *a, **k):
        super(GentleDataStore, self).__init__(*a, **k)
