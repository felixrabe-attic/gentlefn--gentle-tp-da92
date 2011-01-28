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

from   .utilities import random as rnd



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
    FS_DEFAULT_DIR = os.path.join(USER_HOME, ".gentle_tp_da92_default_data_store")
    FS_ENVIRON_KEY = "GENTLE_TP_DA92_DIR"

    @classmethod
    def simplify__gentle_tp_da92__fs_based(cls, fs_based,
                                           directory=None, *a, **k):
        if directory is None:
            directory = os.environ.get(cls.FS_ENVIRON_KEY, cls.FS_DEFAULT_DIR)
        k["mkdir"] = k.get("mkdir", True)  # default to True instead of to False
        return ((directory,) + a, k)


_init_simplifiers = _InitSimplifiers()


class GentleEasyDataStoreWrapper(object):
    """
    Simplifies usage of a GentleDataStore.
    """

    def __init__(self, gentle_data_store):
        self.gentle_data_store = gentle_data_store

        # Shortcuts for interactive usage:
        self.ds = self.gentle_data_store
        self.c  = self.ds._content_db
        self.cf = self.ds._content_db.find_identifiers_starting_with
        self.p  = self.ds._pointer_db
        self.pf = self.ds._pointer_db.find_identifiers_starting_with


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
