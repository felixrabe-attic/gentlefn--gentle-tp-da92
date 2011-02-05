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
from   . import json
from   .utilities import *

SNAPSHOT_POINTER_ID = \
    "30daa8eb0352eee06dbae0affe4594208590356fcd05062995323bc43ff98f92"


def load_snapshot(ds, snapshot_cid=None):
    if snapshot_cid is None:
        snapshot_cid = ds.pointer_db[SNAPSHOT_POINTER_ID]
    snapshot = json.loads(ds.content_db[snapshot_cid])
    sn_ctree_cid, sn_ptree_cid, timestamp, sn_prev_cid = snapshot
    sn_ctree = json.loads(ds.content_db[sn_ctree_cid])
    sn_ptree = json.loads(ds.content_db[sn_ptree_cid])
    return snapshot_cid, sn_ctree, sn_ptree, timestamp, sn_prev_cid

def dump_snapshot(ds, sn_ctree, sn_ptree, timestamp, sn_prev_cid):
    sn_ctree_cid = ds.content_db + json.dumps(sn_ctree)
    sn_ptree_cid = ds.content_db + json.dumps(sn_ptree)
    snapshot = [sn_ctree_cid, sn_ptree_cid, timestamp, sn_prev_cid]
    snapshot_cid = ds.content_db + json.dumps(snapshot)
    ds.pointer_db[SNAPSHOT_POINTER_ID] = snapshot_cid
    return snapshot_cid


class _GentleDB(data_store_interfaces._GentleDB):
    """
    Base class for Gentle TP-DA92 journaling databases.
    """

    def __init__(self, data_store):
        super(_GentleDB, self).__init__()
        self.ds = data_store

    def _dump_snapshot(self):
        self.ds.sn_prev_cid = dump_snapshot(self.ds,
                                            self.ds.sn_ctree,
                                            self.ds.sn_ptree,
                                            int(time.time()),
                                            self.ds.sn_prev_cid)

    def _walk_tree(self, tree, identifier):
        traversed_trees = []
        while len(identifier) > len(traversed_trees):
            if len(tree) < 16:  # up to 15 leaves
                break
            else:  # 16 subtrees plus 1 size field
                index = IDENTIFIER_DIGITS.index(identifier[len(traversed_trees)])
                traversed_trees.append(tree)
                tree_cid = tree[index]
                tree = json.loads(self.ds.content_db[tree_cid])
        return traversed_trees, tree

    def _reorder_tree(self, new_tree, level):
        new_tree_size = len(new_tree)
        if len(new_tree) > 15:  # split up
            tree = new_tree
            new_trees = [[] for i in range(16)]
            for tree_data in tree:
                identifier = self._get_identifier_from_tree_data(tree_data)
                index = IDENTIFIER_DIGITS.index(identifier[level])
                new_trees[index].append(tree_data)
            new_tree_cids = []
            for new_tree in new_trees:
                new_tree, _ignore = self._reorder_tree(new_tree, level+1)
                new_tree_cid = self.ds.content_db + json.dumps(new_tree)
                new_tree_cids.append(new_tree_cid)
            return new_tree_cids + [len(tree)], new_tree_size
        # return
        return new_tree, new_tree_size

    def _propagate_tree_change_upwards(self, traversed_trees, new_tree, identifier):
        new_tree, new_tree_size = self._reorder_tree(new_tree, len(traversed_trees))
        # Propagate change upwards
        while traversed_trees:
            new_tree_cid = self.ds.content_db + json.dumps(new_tree)
            new_tree = traversed_trees.pop()
            index = IDENTIFIER_DIGITS.index(identifier[len(traversed_trees)])
            old_tree = json.loads(self.ds.content_db[new_tree[index]])
            if len(old_tree) < 16:
                old_tree_size = len(old_tree)
            else:
                old_tree_size = old_tree[16]
            new_tree[index] = new_tree_cid
            new_tree_size = new_tree[16] - old_tree_size + new_tree_size
            new_tree[16] = new_tree_size
        self._set_tree(new_tree)

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        traversed_trees, tree = self._walk_tree(self._get_tree(), identifier)
        for tree_data in tree:
            leaf = self._get_identifier_from_tree_data(tree_data)
            if leaf == identifier:
                return self._get_content_from_tree_data(tree_data)
        # Content not found
        raise KeyError(identifier)

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        traversed_trees, tree = self._walk_tree(self._get_tree(), identifier)
        for tree_data in tree:
            leaf = self._get_identifier_from_tree_data(tree_data)
            if leaf == identifier:  # found
                break
        else:  # content not found in snapshot
            raise KeyError(identifier)
        # Remove content
        tree.remove(tree_data)
        self._propagate_tree_change_upwards(traversed_trees, tree, identifier)
        self._dump_snapshot()

    def _find_traversal(self, tree):
        found = []
        expected_len = tree[16]
        for subtree_cid in tree[:16]:
            subtree = json.loads(self.ds.content_db[subtree_cid])
            if len(subtree) < 16:
                for tree_data in subtree:
                    leaf = self._get_identifier_from_tree_data(tree_data)
                    found.append(leaf)
            else:
                found.extend(self._find_traversal(subtree))
        if len(found) != expected_len:
            sys.stderr("Unexpected length of subtree")
            import pdb; pdb.set_trace()
        return found

    def find(self, partial_identifier=""):
        validate_identifier_format(partial_identifier, partial=True)
        traversed_trees, tree = self._walk_tree(self._get_tree(), partial_identifier)
        if len(tree) < 16:  # leaves
            found = []
            for tree_data in tree:
                leaf = self._get_identifier_from_tree_data(tree_data)
                if leaf.startswith(partial_identifier):
                    found.append(leaf)
        else:  # subtrees, of which all identifiers match
            found = self._find_traversal(tree)
        return found

    def __contains__(self, identifier):
        validate_identifier_format(identifier)
        traversed_trees, tree = self._walk_tree(self._get_tree(), identifier)
        for tree_data in tree:
            leaf = self._get_identifier_from_tree_data(tree_data)
            if leaf == identifier:  # Content already in snapshot
                return True
        return False


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def _get_tree(self):
        return self.ds.sn_ctree

    def _set_tree(self, tree):
        self.ds.sn_ctree = tree

    def _get_identifier_from_tree_data(self, tree_data):
        return tree_data

    def _get_content_from_tree_data(self, tree_data):
        return self.ds.content_db[tree_data]

    def __add__(self, byte_string):
        identifier = self.ds.content_db + byte_string
        traversed_trees, tree = self._walk_tree(self._get_tree(), identifier)
        for tree_data in tree:
            leaf = self._get_identifier_from_tree_data(tree_data)
            if leaf == identifier:  # Content already in snapshot
                return identifier
        # Content not found in current snapshot
        new_tree = sorted(tree + [identifier])
        self._propagate_tree_change_upwards(traversed_trees, new_tree, identifier)
        self._dump_snapshot()
        return identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def _get_tree(self):
        return self.ds.sn_ptree

    def _set_tree(self, tree):
        self.ds.sn_ptree = tree

    def _get_identifier_from_tree_data(self, tree_data):
        return tree_data[0]

    def _get_content_from_tree_data(self, tree_data):
        return tree_data[1]

    def __setitem__(self, identifier, content_identifier):
        validate_identifier_format(identifier)
        validate_identifier_format(content_identifier)
        traversed_trees, tree = self._walk_tree(self._get_tree(), identifier)
        for tree_data in tree:
            leaf = self._get_identifier_from_tree_data(tree_data)
            if leaf == identifier:  # Pointer already in snapshot - overwrite
                tree_data[1] = content_identifier
                new_tree = tree
                break
        else:
            # Pointer not found in current snapshot
            new_tree = sorted(tree + [[identifier, content_identifier]])
        self._propagate_tree_change_upwards(traversed_trees, new_tree, identifier)
        self._dump_snapshot()
        return identifier


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, data_store):
        super(GentleDataStore, self).__init__()

        self.ds = data_store

        if SNAPSHOT_POINTER_ID in self.ds.pointer_db:
            ( self.ds.sn_prev_cid,
              self.ds.sn_ctree,
              self.ds.sn_ptree,
              timestamp,
              sn_prev_cid ) = load_snapshot(self.ds)
        else:
            # We are starting with an empty database:
            self.ds.sn_ctree = []
            self.ds.sn_ptree = []
            sn_prev_cid = None
            self.ds.sn_prev_cid = dump_snapshot(self.ds,
                                                self.ds.sn_ctree,
                                                self.ds.sn_ptree,
                                                int(time.time()),
                                                sn_prev_cid)

        self.content_db = _GentleContentDB(self.ds)
        self.pointer_db = _GentlePointerDB(self.ds)
