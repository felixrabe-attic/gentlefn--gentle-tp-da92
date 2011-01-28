#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Time Module.

This module provides a standard way to deal with timestamps, represented as
strings in the format "yyyy-mm-dd HH:MM:SS +OFST", which conform to ISO 8601.
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

from   datetime import datetime
import time

############################################################################

# Code based on bzr's osutils.py:

def local_time_offset(t):
    """Return offset of local zone from GMT at time t."""
    offset = datetime.fromtimestamp(t) - datetime.utcfromtimestamp(t)
    return offset.days * 86400 + offset.seconds

def get_utctime_with_offset(t):
    tt = time.gmtime(t)
    offset = 0
    return (tt, offset)

def get_localtime_with_offset(t):
    tt = time.localtime(t)
    offset = local_time_offset(t)
    return (tt, offset)

def format_time_with_offset(t, offset_arg=None):
    tt, offset = get_localtime_with_offset(t)
    if offset_arg is not None:
        offset = offset_arg
    # # TODO: this is wrong - file a bug for bzr:
    # offset_str = " %+03d%02d" % (offset / 3600, (offset / 60) % 60)
    offset_sign = "-" if offset < 0 else "+"
    offset_str = " %s%02d%02d" % (offset_sign, abs(offset) / 3600, (abs(offset) / 60) % 60)
    return time.strftime("%Y-%m-%d %H:%M:%S", tt) + offset_str

############################################################################

def parse_time_with_offset(timestamp):
    if len(timestamp) != 25:
        raise ValueError("timestamp has wrong format: '%s'" % timestamp)
    offset_str = timestamp[-6:]
    offset_sign = offset_str[1]
    offset = (int(offset_str[2:4]) * 60 + int(offset_str[4:6])) * 60
    if offset_sign == "-": offset *= -1
    tt = time.strptime(timestamp[:-6], "%Y-%m-%d %H:%M:%S")
    return (time.mktime(tt), offset)
