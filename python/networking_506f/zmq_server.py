#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - ZeroMQ-based Server.
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

from   traceback import print_exc

import zmq

from   gentle_tp_da92 import data_store_interfaces
from   gentle_tp_da92.utilities import *


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, data_store_to_serve):
        super(GentleDataStore, self).__init__()
        self.data_store = data_store_to_serve
        self.content_db = self.data_store.content_db
        self.pointer_db = self.data_store.pointer_db

    def _command_get(self, db, payload):
        return db[payload]

    def _command_del(self, db, payload):
        del db[payload]
        return ""

    def _command_find(self, db, payload):
        return " ".join(db.find(payload))

    def _command_contains(self, db, payload):
        return "yes" if payload in db else "no"

    def _command_add(self, db, payload):
        return db + payload

    def _command_set(self, db, payload):
        pointer_identifier, content_identifier = payload.split()
        db[pointer_identifier] = content_identifier
        return ""

    def process_msg(self, msg):
        kind, command, payload = msg[:-1].split(" ", 2)
        db = {"c": self.content_db, "p": self.pointer_db}[kind]
        try:
            method = getattr(self, "_command_" + command)
            reply = "ok " + method(db, payload)
        except Exception as e:
            print_exc()
            reply = "error " + str(e)
        return reply + "\0"

    def serve(self, address):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(address)
        print "Serving on %r ..." % address
        while True:
            msg = socket.recv()
            print "Received %r" % msg
            reply = self.process_msg(msg)
            print "Replying with %r" % reply
            socket.send(reply)
            print
