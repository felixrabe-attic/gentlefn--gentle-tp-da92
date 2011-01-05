#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91) - Next Module

This module contains the next level that extends the core of Gentle by these
features:

- Interface definitions for methods.
- JSON (metadata) input/output.
- A very simple version control system.

While the functionality of the Gentle Core Module is the result of years of
development and careful design, the design and features of Gentle Next are more
experimental in comparison.
"""
# Copyright (C) 2011  Felix Rabe
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

import collections
from datetime import datetime
import json
import time

from gentle_da92de4118f6fa91 import Gentle

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

def format_time_with_offset(tt, offset=None):
    if offset is None:
        tt, offset = get_localtime_with_offset(tt)
    offset_str = " %+03d%02d" % (offset / 3600, (offset / 60) % 60)
    return time.strftime("%Y-%m-%d %H:%M:%S", tt) + offset_str

############################################################################


def _format_date(t, offset, timezone, date_fmt, show_offset):
    if timezone == 'utc':
        tt = time.gmtime(t)
        offset = 0
    elif timezone == 'original':
        if offset is None:
            offset = 0
        tt = time.gmtime(t + offset)
    elif timezone == 'local':
        tt = time.localtime(t)
        offset = local_time_offset(t)
    else:
        raise errors.UnsupportedTimezoneFormat(timezone)
    if date_fmt is None:
        date_fmt = "%a %Y-%m-%d %H:%M:%S"
    if show_offset:
        offset_str = ' %+03d%02d' % (offset / 3600, (offset / 60) % 60)
    else:
        offset_str = ''
    return (date_fmt, tt, offset_str)



class InterfaceDef(object):

    def __init__(self, gentle):
        super(InterfaceDef, self).__init__()
        self.gentle = gentle

    def caller_to_fn(self, data):
        return data

    def fn_to_caller(self, data):
        return data


class PassThrough(InterfaceDef):
    pass


class ContentHash(InterfaceDef):

    def caller_to_fn(self, identifier):
        directory, hash_value = self.gentle.full(identifier)
        if directory != self.gentle.content_dir:
            raise TypeError("argument must be a content identifier")
        return hash_value

    fn_to_caller = caller_to_fn


class JSONContent(ContentHash):

    def caller_to_fn(self, identifier):
        hash_value = super(JSONContent, self).caller_to_fn(identifier)
        json_string = self.gentle.get(hash_value)
        obj = json.loads(json_string)
        try:
            obj = type("_Wrapped", (type(obj),), {})(obj)
            obj.original_gentle_hash = hash_value
        except:
            # bool and NoneType (at least) can't be wrapped - that's ok
            pass
        return obj

    def fn_to_caller(self, obj):
        json_string = json.dumps(obj, separators=(',',':'), sort_keys=True)
        hash_value = self.gentle.put(json_string)
        return hash_value


def interface(*interfacedef):
    """
    Decorator defining the interface of a function.

    The first argument defines the output, the following arguments define the
    input.
    """
    def decorator(fn):
        def wrapper(self, *caller_args):
            # Create interface definitions objects
            self_idef = [icls(self) for icls in interfacedef]
            outputdef, inputdefs = self_idef[0], self_idef[1:]
            len_inputdefs = len(inputdefs)

            # Convert the arguments
            if len(caller_args) < len_inputdefs:
                raise TypeError("%s() takes at least %u arguments (%u given)" %
                                (fn.__name__, len_inputdefs, len(caller_args)))
            fn_args = []
            for i, caller_arg in enumerate(caller_args):
                if i < len_inputdefs:
                    caller_arg = inputdefs[i].caller_to_fn(caller_arg)
                fn_args.append(caller_arg)

            # Call wrapped function and return converted value
            fn_retval = fn(self, *fn_args)
            caller_retval = outputdef.fn_to_caller(fn_retval)
            return caller_retval
        return wrapper
    return decorator


class GentleNext(Gentle):

    @interface(PassThrough, JSONContent)
    def getjson(self, json_document):
        """
        Pretty-print a JSON document.
        """
        print json.dumps(json_document, indent=4, sort_keys=True)


    @interface(JSONContent, PassThrough)
    def putjson(self, json_document):
        return json_document

    jsonget = getjson
    jsonput = putjson

    @staticmethod
    def timestamp(t=None):
        if t is None:
            t = time.time()
        return format_time_with_offset(t)

    @interface(JSONContent, ContentHash, ContentHash)
    def mkversion(self, prev_version_hashv, new_content_hashv):
        """
        Create new version metadata.

        The identifiers must name existing content.
        """
        new_version = {
            "content": new_content_hashv,
            "prev_version:metadata:content": prev_version_hashv,
            "timestamp": self.timestamp(),
            }
        return new_version

    def __inner_findall(self, obj, dict_so_far, key=None):
        # import pdb; pdb.set_trace()

        if isinstance(obj, dict):
            for key in obj:
                p = key.split(":")
                if p[-1] != "content": continue
                self.__inner_findall(obj[key], dict_so_far, key)
            return

        if isinstance(obj, list):
            for item in obj:
                self.findall(item, dict_so_far, key)
            return

        if isinstance(obj, basestring):
            if key is None: return
            p = key.split(":")
            if p[-1] != "content": return  # ignore non-references
            content_hash = obj
            if content_hash in dict_so_far: return  # prevent loop
            dict_so_far[content_hash] = "content"
            if len(p) >= 2 and p[-2] == "metadata":
                dict_so_far[content_hash] = "metadata:content"
                self.findall(content_hash, dict_so_far)
            return

        return  # not interested in other types

    @interface(JSONContent, JSONContent)
    def findall(self, metadata, dict_so_far=None):
        """
        Find all identifiers reachable by some metadata.
        """
        outer_findall = dict_so_far is None
        if outer_findall:
            dict_so_far = {}
            if hasattr(metadata, "original_gentle_hash"):
                dict_so_far[metadata.original_gentle_hash] = "metadata:content"
        self.__inner_findall(metadata, dict_so_far)
        if outer_findall:
            lists = collections.defaultdict(list)
            for key, value in dict_so_far.iteritems():
                lists[value].append(key)
            for value in lists.itervalues():
                value.sort()
            return lists

    def _cli(self, function_name, *args):
        """
        Command line interface.
        """
        return super(GentleNext, self)._cli(function_name, *args)


def main(argv):
    """
    Command line interface.
    """
    gentle_next = GentleNext()
    return gentle_next._cli(*argv[1:])


if __name__ == "__main__":
    import sys
    main(sys.argv)
