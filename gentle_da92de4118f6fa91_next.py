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

from gentle_da92de4118f6fa91_oldcore import *

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


class OtherGentle(InterfaceDef):

    def caller_to_fn(self, other_data_dir):
        other_gentle = GentleNext(other_data_dir)
        return other_gentle


class Identifier(InterfaceDef):

    def caller_to_fn(self, identifier):
        directory, full_identifier = self.gentle.full(identifier)
        return (directory, full_identifier)

    fn_to_caller = caller_to_fn


class ContentHash(Identifier):

    def caller_to_fn(self, identifier):
        directory, hash_value = super(ContentHash, self).caller_to_fn(identifier)
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

    # In JSON data, keys ending in one of ":<REFERENCE_KEY>" have identifier
    # string values:
    REFERENCE_KEYS = ("pointer", "content")

    # These content types denote valid JSON documents:
    JSON_CONTENT_KEYS = ("json:content".split(":"), "metadata:content".split(":"))

    # This key is found in version control JSON documents (other than in the
    # empty version document):
    PREV_VERSION_KEY = "prev_version:metadata:content"

    def __init__(self, *a, **k):
        super(GentleNext, self).__init__(*a, **k)
        self.empty_content = self.put("")
        self.empty_version = self.putj({"content:content": self.empty_content})

    @interface(PassThrough, JSONContent)
    def getj(self, json_document):
        """
        Pretty-print a JSON document.
        """
        print json.dumps(json_document, indent=4, sort_keys=True)

    @interface(JSONContent, PassThrough)
    def putj(self, json_document):
        if isinstance(json_document, basestring):
            # Automatically try to parse the passed-in JSON:
            try:
                json_document = json.loads(json_document)
            except:
                pass  # Not severe; we just keep the string as-is
        return json_document

    @interface(PassThrough, JSONContent, PassThrough)
    def json(self, json_document, python_snippet):
        """
        Manipulate JSON.
        """
        c = json_document
        g = self
        exec python_snippet
        return None

    @staticmethod
    def timestamp(t=None):
        if t is None:
            t = time.time()
        return format_time_with_offset(t)

    @interface(JSONContent, ContentHash, ContentHash)
    def mkversion(self, prev_version_hashv, new_content_hashv=None, timestamp=None):
        """
        Create new version metadata.

        The identifiers must name existing content.  If only one identifier is
        specified, the method will create a new version whose previous version
        is the empty_version version ({}).
        """
        if new_content_hashv is None:
            new_content_hashv = prev_version_hashv
            prev_version_hashv = self.empty_version
        new_content_key = "content:content"
        try:
            json.loads(self.get(new_content_hashv))
        except: pass
        else:
            new_content_key = "content:json:content"

        if timestamp is None: timestamp = self.timestamp()

        new_version = {
            new_content_key: new_content_hashv,
            self.PREV_VERSION_KEY: prev_version_hashv,
            "timestamp": timestamp,
            }
        return new_version

    def putv(self, pointer_identifier, content_identifier=None):
        pointer_identifier = self.full(pointer_identifier)[1]
        if not isinstance(content_identifier, basestring):  # a json object
            content_identifier = self.putj(content_identifier)
        else:
            content_identifier = self.full(content_identifier)[1]
        new_version = self.mkversion(self.get(pointer_identifier), content_identifier)
        return self.put(pointer_identifier, new_version)

    def __findall_in_object(self, obj, found_by_key, key=None):
        if isinstance(obj, dict):
            for key in obj:
                self.__findall_in_object(obj[key], found_by_key, key.split(":"))

        elif isinstance(obj, list):
            for item in obj:
                self.__findall_in_object(item, found_by_key, key)

        elif isinstance(obj, basestring):
            if key is None or key[-1] not in GentleNext.REFERENCE_KEYS:
                return  # ignore non-references
            self.__findall_in_content(obj, found_by_key, key)

        # else - not interested in other types, just return

    def __findall_in_content(self, identifier, found_by_key, key=None,
                             identifier_must_be_valid=True):
        if identifier_must_be_valid:
            if len(identifier) != 256 / 4:
                raise ValueError("invalid identifier: %r" % identifier)
        directory, identifier = self.full(identifier)
        if directory == self.pointer_dir:
            if key is None:
                key = ["json", "pointer"]
            if key[-1] != "pointer":
                raise ValueError("identifier of wrong type: %r" % identifier)
            if identifier in found_by_key["pointer"]: return  # prevent loop
            found_by_key["pointer"].append(identifier)
            identifier = self.get(identifier)  # dereference pointer
            key = key[:]
            key[-1] = "content"  # turn "*:pointer" key into "*:content" key
        if key is None:
            key = ["json", "content"]
        if key[-1] != "content":
            raise ValueError("identifier of wrong type: %r" % identifier)
        if (identifier in found_by_key["content"] or
            identifier in found_by_key["json:content"]):
            return  # prevent loop
        if key[-2:] in GentleNext.JSON_CONTENT_KEYS:
            found_by_key["json:content"].append(identifier)
            obj = json.loads(self.get(identifier))
            self.__findall_in_object(obj, found_by_key)
        else:
            found_by_key["content"].append(identifier)

    def _findall(self, *identifiers):
        """
        Find all identifiers reachable by some identifiers, including the given
        identifiers.  Or, find all identifiers.
        """
        found_by_key = collections.defaultdict(list)
        if len(identifiers) == 0:  # find really *everything*
            for identifier in os.listdir(self.pointer_dir):
                found_by_key["pointer"].append(identifier)
            for identifier in os.listdir(self.content_dir):
                key = "content"
                content = self.get(identifier)
                try:
                    json_content = json.loads(content)
                except:
                    pass
                else:
                    key = "json:content"
                found_by_key[key].append(identifier)
        else:
            for identifier in identifiers:
                self.__findall_in_content(identifier, found_by_key,
                                          identifier_must_be_valid=False)
        for found_list in found_by_key.itervalues():
            found_list.sort()
        return found_by_key

    def findall(self, *identifiers):
        """
        Find all identifiers reachable by some identifiers, including the given
        identifiers.  Or, find all identifiers.
        """
        found_by_key = self._findall(*identifiers)
        jsondef = JSONContent(self)
        identifier = jsondef.fn_to_caller(found_by_key)
        return identifier

    @staticmethod
    def __copy(from_gentle, (from_directory, from_identifier), to_gentle):
        found_by_key = from_gentle._findall(from_identifier)
        # from_gentle.rm(identifier)
        pointers, contents = [], []
        for key, sublist in found_by_key.iteritems():
            key = key.split(":")
            if key[-1] == "pointer":
                pointers.extend(sublist)
            elif key[-1] == "content":
                contents.extend(sublist)
            else:
                raise Exception, "FATAL: findall() returned invalid data"
        for c in contents:
            to_gentle.put(from_gentle.get(c))
        for p in pointers:
            to_gentle.put(p, from_gentle.get(p))

    @interface(PassThrough, Identifier, OtherGentle)
    def export(self, (directory, identifier), other_gentle):
        """
        Extract the data reachable from the identifier in our databases, and
        copy it to another Gentle data directory.  This can be used to split or
        export data.
        """
        return self.__copy(self, (directory, identifier), other_gentle)

    @interface(PassThrough, PassThrough, OtherGentle)
    def import_(self, identifier, other_gentle):
        """
        Extract the data reachable from the identifier in the other Gentle's
        databases, and copy it into our Gentle data directory.  This can be used
        to merge or import data.
        """
        identifier_def = Identifier(other_gentle)
        (directory, identifier) = identifier_def.caller_to_fn(identifier)
        return self.__copy(other_gentle, (directory, identifier), self)

    def help(self):
        import gentle_da92de4118f6fa91_next
        print "TODO: Provide help text.  In the meantime, find the source code here:"
        print gentle_da92de4118f6fa91_next.__file__

    def _cli(self, method_name, *args):
        """
        Command line interface.
        """
        m, f = self._cli_get_method(method_name)
        if f == GentleNext.putj.__func__ and len(args) == 0:
            byte_string = sys.stdin.read()
            print m(byte_string)
            return
        if f == GentleNext.json.__func__ and len(args) == 1:
            python_snippet = sys.stdin.read()
            args = args + (python_snippet,)
        return super(GentleNext, self)._cli(method_name, *args)


def main(argv):
    """
    Command line interface.
    """
    gentle_next = GentleNext()
    return gentle_next._cli(*argv[1:])


if __name__ == "__main__":
    import sys
    main(sys.argv)
