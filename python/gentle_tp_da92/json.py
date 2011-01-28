#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - JSON Module.

Provides loads (standard behaviour); dumps (compact behaviour); pretty and
pprint (pretty-printing behaviour).
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

import json

loads = json.loads
load = json.load

def dump(*a, **k):
    """
    Like json.dump(), but defaults to compact, sorted output.
    """
    knew = dict(separators=(',',':'), sort_keys=True)
    knew.update(k)
    return json.dump(*a, **knew)

def dumps(*a, **k):
    """
    Like json.dumps(), but defaults to compact, sorted output.
    """
    knew = dict(separators=(',',':'), sort_keys=True)
    knew.update(k)
    return json.dumps(*a, **knew)

def pretty(*a, **k):
    """
    Like json.dumps(), but defaults to pretty-printing.
    """
    knew = dict(indent=4, sort_keys=True)
    knew.update(k)
    return json.dumps(*a, **knew)

def pprint(*a, **k):
    print(pretty(*a, **k))
