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

from hashlib import sha1
import os


class FullyQualified(object):

    USER_HOME = os.path.expanduser("~")
    PARENT_DIR_1683b96af50b3bd9 = os.path.join(USER_HOME, ".gentle_data_1683b96af50b3bd9")
    CONTENT_DB_DIR_6ebc8ee8333c1f4c = os.path.join(PARENT_DIR_1683b96af50b3bd9, "content_db_6ebc8ee8333c1f4c")
    POINTER_DB_DIR_8b3675814942c0fe = os.path.join(PARENT_DIR_1683b96af50b3bd9, "pointer_db_8b3675814942c0fe")

    # Make sure those above directories exist
    for directory in (PARENT_DIR_1683b96af50b3bd9, CONTENT_DB_DIR_6ebc8ee8333c1f4c, POINTER_DB_DIR_8b3675814942c0fe):
        if not os.path.exists(directory):
            os.mkdir(directory)

    ## METHODS FOR GENTLE BOOTSTRAPPING

    @staticmethod
    def generate_identifier_b0a08d9073e10594():
        """
        Generates a new 64-bit bootstrap identifier.
        """
        name_length = 64 / 8  # 64 bits, 8 bytes
        new_name = os.urandom(name_length)
        return new_name.encode("hex")  # 8 -> 16 bytes

    @staticmethod
    def resolve_identifier_9b97d1198d8da30d(name):
        """
        Resolves a 64-bit bootstrap identifier to a Python object.
        """
        if name == me:
            return g
        for member_name in dir(FullyQualified):
            if member_name.endswith("_" + name):
                return getattr(FullyQualified, member_name)
        return None

    ## FUNDAMENTAL OPERATIONS IN A GENTLE SYSTEM

    @staticmethod
    def sha1_42f2ba4c350bc32a(byte_string):
        sha1_object = sha1()
        sha1_object.update(byte_string)
        return sha1_object.hexdigest()

    @staticmethod
    def store_data_b1b4129b91991705(byte_string):
        sha1fn = g.ntl("42f2ba4c350bc32a")
        content_db_dir = g.ntl("6ebc8ee8333c1f4c")

        sha1key = sha1fn(byte_string)
        filename = os.path.join(content_db_dir, sha1key)
        if not os.path.exists(filename):
            file(filename, "wb").write(byte_string)
        return sha1key

    @staticmethod
    def remove_data_88eea22244f81249(sha1key):
        content_db_dir = g.ntl("6ebc8ee8333c1f4c")

        filename = os.path.join(content_db_dir, sha1key)
        os.remove(filename)

    @staticmethod
    def get_data_056702875ab4e43b(sha1key):
        content_db_dir = g.ntl("6ebc8ee8333c1f4c")

        filename = os.path.join(content_db_dir, sha1key)
        byte_string = file(filename, "rb").read()
        return byte_string

    @staticmethod
    def generate_ptr_142e69d252889f3c():
        key_length = 128 / 8  # 128 bits, 16 bytes
        ptrkey = os.urandom(key_length)
        return ptrkey.encode("hex")  # 16 -> 32 bytes

    @staticmethod
    def store_ptr_2c98aaa88cfdc9fc(ptrkey, sha1key):
        pointer_db_dir = g.ntl("8b3675814942c0fe")

        filename = os.path.join(pointer_db_dir, ptrkey)
        file(filename, "wb").write(sha1key)

    @staticmethod
    def remove_ptr_5518ac3c5c6eb04d(ptrkey):
        pointer_db_dir = g.ntl("8b3675814942c0fe")

        filename = os.path.join(pointer_db_dir, ptrkey)
        os.remove(filename)

    @staticmethod
    def follow_ptr_711d9d3ba40a10ee(ptrkey):
        pointer_db_dir = g.ntl("8b3675814942c0fe")

        filename = os.path.join(pointer_db_dir, ptrkey)
        sha1key = file(filename, "rb").read()
        return sha1key


import gentle_tech_preview_da92de4118f6fa91 as g
FQ = FullyQualified
gen = FullyQualified.generate_identifier_b0a08d9073e10594
ntl = FullyQualified.resolve_identifier_9b97d1198d8da30d

store_data = g.ntl("b1b4129b91991705")
remove_data = g.ntl("88eea22244f81249")
get_data = g.ntl("056702875ab4e43b")
generate_ptr = g.ntl("142e69d252889f3c")
store_ptr = g.ntl("2c98aaa88cfdc9fc")
remove_ptr = g.ntl("5518ac3c5c6eb04d")
follow_ptr = g.ntl("711d9d3ba40a10ee")


## COMMAND LINE INTERFACE

# Usage:
# python -m gentle_tech_preview_da92de4118f6fa91 <identifier> <arguments>

if __name__ == "__main__":
    import sys
    identifier = sys.argv[1]
    args = sys.argv[2:]
    fn = g.ntl(identifier)
    if fn == store_data:
        byte_string = sys.stdin.read()
        print fn(byte_string)
    elif fn == get_data:
        byte_string = fn(*args)
        sys.stdout.write(byte_string)
    else:
        result = fn(*args)
        if result is not None:
            print result
