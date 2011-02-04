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
    timestamp, prev, tree = struct.unpack(SNAPSHOT_PACK_FORMAT, raw_snapshot)
    return (timestamp, prev.encode("hex"), tree.encode("hex"))


class _GentleDB(data_store_interfaces._GentleDB):
    """
    Base class for Gentle TP-DA92 journaling databases.
    """

    def __init__(self, data_store):
        super(_GentleDB, self).__init__()
        self.ds = data_store

    def _make_new_snapshot(self, raw_tree):
        timestamp = int(time.time())
        prev_snapshot_id = self.ds.snapshot_cid
        snapshot_tree_id = self.ds.content_db + raw_tree

        raw_snapshot = ss_pack(timestamp, prev_snapshot_id, snapshot_tree_id)
        self.ds.snapshot_cid = self.ds.content_db + raw_snapshot
        self.ds.pointer_db[SNAPSHOT_POINTER_ID] = self.ds.snapshot_cid
        self.ds.raw_snapshot_root_tree = raw_tree

    def __getitem__(self, identifier):
        raise NotImplementedError()

    def __delitem__(self, identifier):
        raise NotImplementedError()

    def find(self, partial_identifier=""):
        raise NotImplementedError()

    def __contains__(self, identifier):
        raise NotImplementedError()


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def __getitem__(self, identifier):
        raise NotImplementedError()

    def __add__(self, byte_string):
        hex_identifier = self.ds.content_db + byte_string
        raw_tree = self.ds.raw_snapshot_root_tree
        level = 0
        if len(raw_tree) == 16*32+1:  # 16 IDs + size
            raise NotImplementedError()
        # up to 15 (right-hand-partial) IDs
        tree_size = len(raw_tree) // 32
        raw_stored_ids = [raw_tree[i*32:(i+1)*32] for i in range(tree_size)]
        raw_identifier = hex_identifier.decode("hex")
        if raw_identifier in raw_stored_ids:
            return hex_identifier
        raw_stored_ids = sorted(raw_stored_ids + [raw_identifier])
        if len(raw_stored_ids) > 15:
            new_trees = [[] for i in range(16)]
            for raw_stored_id in raw_stored_ids:
                hex_stored_id = raw_stored_ids.encode("hex")
                index = IDENTIFIER_DIGITS.index(hex_stored_id[level])
                new_trees[index].append(raw_stored_id)
            new_tree_size = sum(len(t) for t in new_trees)
            new_tree_ids = [self.ds.content_db + "".join(t) for t in new_trees]
            nts = chr(min(255, new_tree_size))
            raw_tree = "".join(i.decode("hex") for i in new_tree_ids) + nts
        else:
            raw_tree = "".join(raw_stored_ids)
        self._make_new_snapshot(raw_tree)
        return hex_identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def __getitem__(self, identifier):
        raise NotImplementedError()

    def __setitem__(self, pointer_identifier, content_identifier):
        raise NotImplementedError()


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, data_store):
        super(GentleDataStore, self).__init__()

        self.ds = data_store

        if SNAPSHOT_POINTER_ID in self.ds.pointer_db:
            self.ds.snapshot_cid = self.ds.pointer_db[SNAPSHOT_POINTER_ID]
            raw_snapshot = self.ds.content_db[self.ds.snapshot_cid]
            timestamp, prev_snapshot_id, snapshot_tree_id = \
                ss_unpack(raw_snapshot)
            self.ds.raw_snapshot_root_tree = self.ds.content_db[snapshot_tree_id]
        else:
            # We are starting with an empty database:
            timestamp = int(time.time())
            prev_snapshot_id = NULL
            raw_tree = ""
            snapshot_tree_id = self.ds.content_db + raw_tree

            raw_snapshot = ss_pack(timestamp, prev_snapshot_id, snapshot_tree_id)
            self.ds.snapshot_cid = self.ds.content_db + raw_snapshot
            self.ds.pointer_db[SNAPSHOT_POINTER_ID] = self.ds.snapshot_cid
            self.ds.raw_snapshot_root_tree = raw_tree

        self.content_db = _GentleContentDB(self.ds)
        self.pointer_db = _GentlePointerDB(self.ds)
