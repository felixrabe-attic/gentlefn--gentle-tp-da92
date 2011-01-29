#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - The Easy Module.

Provides simplified access to a Gentle TP-DA92 data store from Python.  This
module is suitable for interactive usage.  Examples:

    >>> from gentle_tp_da92 import *
    >>> g = easy.Gentle()
    >>> g.getdir()
    '/home/user/.gentle_tp_da92_default_data_store'

It is recommended to use this module in applications, instead of directly using
the data store implementation modules.
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

from __future__ import print_function

from   functools import partial
import os
import sys

from   .utilities import *

isvalid = is_identifier_format_valid
rnd = random


class _InitSimplifiers(object):
    """
    Simplifies initialization arguments of the GentleDataStore class based on
    the data store module in question.  Do not use this class in application
    code.

    Usage:
    >>> _init_simplifiers = _InitSimplifiers()
    >>> from gentle_tp_da92 import fs_based
    >>> (a, k) = _init_simplifiers[fs_based]()
    >>> g = fs_based
    """

    def __getitem__(self, module):
        # Get the module's name:
        name = module.__name__

        # Get the corresponding method name:
        name = "simplify__" + name.replace(".", "__")

        # If such a method exists, return it, or else return _passthrough:
        if hasattr(self, name):
            return partial(getattr(self, name), module)
        else:
            return self._passthrough

    @staticmethod
    def _passthrough(*a, **k):
        return (a, k)

    ## SIMPLIFICATION FOR gentle_tp_da92.fs_based ##

    USER_HOME = os.path.expanduser("~")
    FS_DEFAULT_DIR = os.path.join(USER_HOME, ".gentle_tp_da92_default_datastore")
    FS_ENVIRON_KEY = "GENTLE_TP_DA92_DIR"

    @classmethod
    def simplify__gentle_tp_da92__fs_based(cls, fs_based,
                                           directory=None, *a, **k):
        if directory is None:
            directory = os.environ.get(cls.FS_ENVIRON_KEY, cls.FS_DEFAULT_DIR)
        directory = os.path.abspath(directory)
        k["mkdir"] = k.get("mkdir", True)  # default to True instead of to False
        return ((directory,) + a, k)


_init_simplifiers = _InitSimplifiers()


class GentleEasyDataStoreWrapper(object):
    """
    Simplifies usage of a GentleDataStore.
    """

    def __init__(self, gentle_data_store):
        self.ds = gentle_data_store
        self.c  = self.ds.content_db
        self.p  = self.ds.pointer_db
    
    def find(self, partial_identifier=""):
        content_identifiers = self.c.find(partial_identifier)
        pointer_identifiers = self.p.find(partial_identifier)
        return sorted(content_identifiers + pointer_identifiers)

    def __getitem__(self, partial_identifier):
        content_identifers = self.c.find(partial_identifier)
        pointer_identifers = self.p.find(partial_identifier)
        identifiers = content_identifers + pointer_identifers
        if len(identifiers) > 1:
            return sorted(identifiers)
        if content_identifers:
            return self.c[content_identifers[0]]
        else:
            return self.p[pointer_identifers[0]]

    def __setitem__(self, pointer_identifier, content_identifier):
        if not is_identifier_format_valid(pointer_identifier):
            identifiers = self.p.find(pointer_identifier)
            if len(identifiers) != 1:
                raise InvalidIdentifierException(pointer_identifier)
            pointer_identifier = identifiers[0]

        if not is_identifier_format_valid(content_identifier):
            identifiers = self.c.find(content_identifier)
            if len(identifiers) != 1:
                raise InvalidIdentifierException(content_identifier)
            content_identifier = identifiers[0]

        self.p[partial_pointer_identifier] = content_identifier

    def __add__(self, content):
        return self.c + content


def Gentle(implementation_module="gentle_tp_da92.fs_based", *a, **k):
    """
    Factory function that returns a Gentle TP-DA92 data store object.

    The user may provide an implementation module as the first argument, either
    a string or a module.  It defaults to gentle_tp_da92.fs_based.
    """
    if isinstance(implementation_module, basestring):
        __import__(implementation_module)
        implementation_module = sys.modules[implementation_module]

    # Simplify arguments based on the implementation_module:
    a, k = _init_simplifiers[implementation_module](*a, **k)
    gentle_data_store = implementation_module.GentleDataStore(*a, **k)
    gentle = GentleEasyDataStoreWrapper(gentle_data_store)
    return gentle
