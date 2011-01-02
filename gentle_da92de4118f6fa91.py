#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91)

Full identifier: da92de4118f6fa915b6bdd73f090ad57dc153082600855e5c7a85e8fe054c5a1
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

import glob
import os

# Locations of the content and pointer databases:
USER_HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(USER_HOME, ".gentle_da92de4118f6fa91")
CONTENT_DIR = os.path.join(DATA_DIR, "content_db")
POINTER_DIR = os.path.join(DATA_DIR, "pointer_db")
    

def sha256(byte_string):
    """
    Return the SHA-256 hash value of the given byte_string in hexadecimal
    representation.
    
    Used for entering content into the content database.
    """
    from hashlib import sha256
    sha256_object = sha256()
    sha256_object.update(byte_string)
    return sha256_object.hexdigest()


def random():
    """
    Return a random-generated 256-bit number in hexadecimal representation.
    
    Useful for creating pointers in the pointer database.
    """
    return os.urandom(256 / 8).encode("hex")


def full(identifier):
    """
    Return the full version of a possibly abbreviated identifier.
    
    The identifier must match the beginning of the key of exactly one entry in
    either one database.
    """
    contents = glob.glob(os.path.join(CONTENT_DIR, identifier) + "*")
    pointers = glob.glob(os.path.join(POINTER_DIR, identifier) + "*")
    matches = contents + pointers
    if len(matches) == 0:
        raise Exception("neither content nor pointer found for identifier '%s'" % identifier)
    if len(matches) > 1:
        raise Exception("multiple identifiers found starting with '%s'" % identifier)
    directory, identifier = os.path.split(matches[0])
    return (directory, identifier)


def put(a, b=None):
    """
    Enter content into the content database, or change a pointer in the pointer
    database.
    
    Example:
    >>> put("content")
    'ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73'
    >>> random()
    '80834436d97b9327eb8138c907f57c205b3d7ba9a962d7cf72849993e909c299'
    >>> put("80834436d97b9327eb8138c907f57c205b3d7ba9a962d7cf72849993e909c299", "ed7002")
    
    In the first usage, return the SHA-256 hash value of the entered content.
    """
    if b is None:  # write new content
        byte_string = a
        hash_value = sha256(byte_string)
        filename = os.path.join(CONTENT_DIR, hash_value)
        if not os.path.exists(filename):
            with os.fdopen(os.open(filename, os.O_CREAT | os.O_WRONLY, 0400), "wb") as f:
                f.write(byte_string)
        return hash_value
    else:  # write new pointer or change it
        pointer_key, identifier = a, b
        directory, hash_value = full(identifier)
        if directory != CONTENT_DIR:
            raise TypeError("second argument must be a content hash value")
        filename = os.path.join(POINTER_DIR, pointer_key)
        with os.fdopen(os.open(filename, os.O_CREAT | os.O_WRONLY, 0600), "wb") as f:
            f.write(hash_value)


def get(identifier):
    """
    Get content from the content database, or follow a pointer from the
    pointer database.
    
    Example:
    >>> get("808344")
    'ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73'
    >>> get("ed7002")
    'content'
    
    The identifier must match the beginning of the key of exactly one entry in
    either one database.
    """
    directory, identifier = full(identifier)
    filename = os.path.join(directory, identifier)
    if directory == CONTENT_DIR:
        byte_string = open(filename, "rb").read()
        return byte_string
    else:
        hash_value = open(filename, "rb").read()
        return hash_value


def remove(identifier):
    """
    Remove content from the content database, or a pointer from the pointer
    database.
    
    The identifier must match the beginning of the key of exactly one entry in
    either one database.
    """
    directory, identifier = full(identifier)
    filename = os.path.join(directory, identifier)
    os.remove(filename)


def _gentle_init():
    """
    Make sure the database directories exist.
    """
    for directory in (DATA_DIR, CONTENT_DIR, POINTER_DIR):
        if not os.path.exists(directory):
            os.mkdir(directory, 0700)
    # TODO: Bootstrap the gentle object from the databases.
    return None

gentle = _gentle_init()


def main(argv):
    """
    Command line interface.
    """
    function_name, args = argv[1], argv[2:]
    fn = globals()[function_name]
    if fn in (sha256, put) and len(args) == 0:
        byte_string = sys.stdin.read()
        print fn(byte_string)
        return
    elif fn is get:
        directory, identifier = full(args[0])
        if directory == CONTENT_DIR:
            byte_string = get(*args)
            sys.stdout.write(byte_string)
            return
    result = fn(*args)
    if result is not None:
        print result

if __name__ == "__main__":
    import sys
    main(sys.argv)

