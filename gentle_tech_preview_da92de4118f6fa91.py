#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91)
"""
# Copyright (C) 2010  Felix Rabe
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
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

me = "da92de4118f6fa91"

import os

class FullyQualified(object):

    @staticmethod
    def generate_name_b0a08d9073e10594():
        name_length = 64 / 8  # 64 bits, 8 bytes
        new_name = os.urandom(name_length)
        return new_name.encode("hex")  # 8 -> 16 bytes

    @staticmethod
    def resolve_9b97d1198d8da30d(name):
        if name == me:
            import gentle_tech_preview_da92de4118f6fa91
            return gentle_tech_preview_da92de4118f6fa91
        for member_name in dir(FullyQualified):
            if member_name.endswith("_" + name):
                return getattr(FullyQualified, member_name)
        return None

gen = FullyQualified.generate_name_b0a08d9073e10594
ntl = FullyQualified.resolve_9b97d1198d8da30d
