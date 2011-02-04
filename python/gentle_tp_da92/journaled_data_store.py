#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Journaled Data Store.
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

from __future__ import print_function, absolute_import

from   functools import partial
from   hashlib import sha256
import struct
import sys
import time

from   . import data_store_interfaces
from   . import debugging_wrapper
from   .utilities import *

SNAPSHOT_POINTER_ID = \
    "30daa8eb0352eee06dbae0affe4594208590356fcd05062995323bc43ff98f92"

NULL = \
    "0000000000000000000000000000000000000000000000000000000000000000"

SNAPSHOT_PACK_FORMAT = (
    "!" +       # Network byte order
    "Q" +       # UTC timestamp ( int(time.time()) )
    "32s" +     # Previous snapshot content identifier
    "32s"       # Snapshot tree content identifier
    )

def ss_pack(timestamp, prev_snapshot_id, snapshot_tree_id):
    return struct.pack(SNAPSHOT_PACK_FORMAT, timestamp,
                       prev_snapshot_id.decode("hex"),
                       snapshot_tree_id.decode("hex"))

def ss_unpack(raw_snapshot):
    timestamp, prev, tree = struct.unpack(SNAPSHOT_PACK_FORMAT)
    return (timestamp, prev.encode("hex"), tree.encode("hex"))


class _GentleDB(data_store_interfaces._GentleDB):
    """
    Base class for Gentle TP-DA92 journaling databases.
    """

    def __init__(self, data_store):
        super(_GentleDB, self).__init__()
        self.ds = data_store

        if SNAPSHOT_POINTER_ID in self.ds.pointer_db:
            self.snapshot_cid = self.ds.pointer_db[SNAPSHOT_POINTER_ID]
            raw_snapshot = self.ds.content_db[self.snapshot_cid]
            timestamp, prev_snapshot_id, snapshot_tree_id = \
                ss_unpack(raw_snapshot)
            self.raw_snapshot_root_tree = self.ds.content_db[snapshot_tree_id]
        else:
            # We are starting with an empty database:
            timestamp = int(time.time())
            prev_snapshot_id = NULL
            self.raw_snapshot_root_tree = ""
            snapshot_tree_id = self.ds.content_db + self.raw_snapshot_root_tree

            raw_snapshot = ss_pack(timestamp, prev_snapshot_id, snapshot_tree_id)
            self.snapshot_cid = self.ds.content_db + raw_snapshot
            self.ds.pointer_db[SNAPSHOT_POINTER_ID] = self.snapshot_cid

    def _walk_tree(self, raw_tree, identifier):
        raise NotImplementedError()

    def __getitem__(self, identifier):
        raise NotImplementedError()

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        return None  # TODO!!!
        validate_identifier_format(identifier)
        del self.db[identifier]

    def find(self, partial_identifier=""):
        return None  # TODO!!!
        identifiers = [i for i in self.db if i.startswith(partial_identifier)]
        return identifiers

    def __contains__(self, identifier):
        return bool(self._walk_tree(self.raw_snapshot_root_tree, identifier))


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def _walk_tree(self, raw_tree, identifier, level=0):
        """Find out whether some content exists in the snapshot tree."""
        self._walk_tree_last = raw_tree
        if len(identifier) == 0:
            if len(raw_tree) > 0:  # tree of trees or tree with leaves
                return True
            else:
                return False  # bad luck
        # identifier may be right-hand remainder of original identifier
        if len(raw_tree) == 16 * 32 + 1:  # tree of trees (size appended)
            if len(identifier) == 1:
                identifier = identifier + "0"
            index, identifier = identifier[:2].decode("hex") // 16, identifier[1:]
            tree_id = raw_tree[index*32 : (index+1)*32].encode("hex")
            raw_tree = self.ds.content_db[tree_id]
            return self._walk_tree(raw_tree, identifier, level+1)
        # tree of at most 15 leaf nodes
        if len(identifier) % 2:
            identifier = "0" + identifier
        raw_identifier = identifier.decode("hex")
        ln = 32 - level // 2
        for i in range((len(raw_tree) - 1) // ln):
            if raw_tree[i*ln : (i+1)*ln].startswith(raw_identifier):
                return True
        return False

    def __getitem__(self, identifier):
        exists = self._walk_tree(self.raw_snapshot_root_tree, identifier)
        if not exists:
            raise KeyError(identifier)
        return self.db[identifier]

    def __add__(self, byte_string):
        return None  # TODO!!!
        content_identifier = sha256(byte_string).hexdigest()
        if not content_identifier in self.db:
            self.db[content_identifier] = byte_string
        return content_identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def _walk_tree(self, raw_tree, identifier, level=0):
        """Find a pointer in the snapshot tree."""
        self._walk_tree_last = raw_tree
        if len(identifier) == 0:
            if len(raw_tree) > 0:  # tree of trees or tree with leaves
                return True
            else:
                return None  # bad luck
        # identifier may be right-hand remainder of original identifier
        if len(raw_tree) == 16 * 32 + 1:  # tree of trees (size appended)
            if len(identifier) == 1:
                identifier = identifier + "0"
            index, identifier = identifier[:2].decode("hex") // 16, identifier[1:]
            tree_id = raw_tree[index*32 : (index+1)*32].encode("hex")
            raw_tree = self.ds.content_db[tree_id]
            return self._walk_tree(raw_tree, identifier, level+1)
        # tree of at most 15 leaf nodes
        if len(identifier) % 2:
            identifier = "0" + identifier
        raw_identifier = identifier.decode("hex")
        ln = 32 - level // 2
        lnpv = ln + 32  # ln plus size of pointer value
        for i in range((len(raw_tree) - 1) // lnpv):
            if raw_tree[i*lnpv : i*lnpv+ln].startswith(raw_identifier):
                pv = raw_tree[i*lnpv+ln : (i+1)*lnpv]
                return pv.encode("hex")
        return None

    def __getitem__(self, identifier):
        content_id = self._walk_tree(self.raw_snapshot_root_tree, identifier)
        if content_id is None:
            raise KeyError(identifier)
        return content_id

    def __setitem__(self, pointer_identifier, content_identifier):
        return None  # TODO!!!
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        self.db[pointer_identifier] = content_identifier
        return pointer_identifier


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, data_store):
        super(GentleDataStore, self).__init__()
        self.content_db = _GentleContentDB(data_store)
        self.pointer_db = _GentlePointerDB(data_store)
