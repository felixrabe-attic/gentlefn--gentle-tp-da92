#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - ZeroMQ-based Client.
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
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.#!/usr/bin/env python

import zmq

from   gentle_tp_da92 import data_store_interfaces
from   gentle_tp_da92.utilities import *


class NetworkException(Exception): pass


def send_command(db, command, payload):
    socket, kind = db.socket, db.kind
    socket.send("%s %s %s\0" % (kind, command, payload))
    reply = socket.recv()
    status, payload = reply[:-1].split(" ", 1)
    if status == "ok": return payload
    elif status == "error": raise NetworkException(payload)
    else: raise NetworkException("invalid reply: %r" % reply)


class _GentleDB(data_store_interfaces._GentleDB):

    def __init__(self, socket):
        super(_GentleDB, self).__init__()
        self.kind = "c" if self.__class__ is _GentleContentDB else "p"
        self.socket = socket

    _send_command = send_command

    def __getitem__(self, identifier):
        validate_identifier_format(identifier)
        content = self._send_command("get", identifier)
        return content

    def find(self, partial_identifier=""):
        reply = self._send_command("find", partial_identifier)
        identifiers = reply.split()
        return identifiers

    def __contains__(self, identifier):
        reply = self._send_command("contains", identifier)
        return reply == "yes"


class _GentleContentDB(data_store_interfaces._GentleContentDB, _GentleDB):

    def __add__(self, byte_string):
        content_identifier = self._send_command("add", byte_string)
        return content_identifier


class _GentlePointerDB(data_store_interfaces._GentlePointerDB, _GentleDB):

    def __setitem__(self, pointer_identifier, content_identifier):
        validate_identifier_format(pointer_identifier)
        validate_identifier_format(content_identifier)
        self._send_command("set", pointer_identifier + " " + content_identifier)
        return pointer_identifier

    def __delitem__(self, identifier):
        validate_identifier_format(identifier)
        self._send_command("del", identifier)


class GentleDataStore(data_store_interfaces.GentleDataStore):

    def __init__(self, socket_or_address):
        super(GentleDataStore, self).__init__()
        if isinstance(socket_or_address, basestring):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(socket_or_address)
        else:
            socket = socket_or_address
        self.content_db = _GentleContentDB(socket)
        self.pointer_db = _GentlePointerDB(socket)
