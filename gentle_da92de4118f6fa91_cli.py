#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91) - Command Line Interface Module
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

from gentle_da92de4118f6fa91_next import *

def printw(string):
    "Print string without appending a newline."
    sys.stdout.write(string)

def read():
    "Read from stdin."
    return sys.stdin.read()


class GentleCLI(object):

    def __init__(self, *a, **k):
        self.gentle = GentleNext(*a, **k)

    def dig(self, identifier):
        "Find content, even if versioned and/or behind a pointer."
        g = self.gentle
        (directory, identifier) = g.full(identifier)
        if directory == g.pointer_dir:  # follow pointer
            identifier = g.get(identifier)
        content = g.get(identifier)
        json_document = ()
        try:    json_document = json.loads(content)
        except: pass
        if not isinstance(json_document, dict): return identifier
        if g.PREV_VERSION_KEY not in json_document: return identifier
        for key in json_document:
            p = key.split(":")
            if p[0] == "content" and p[-1] == "content":
                break
        else:
            raise TypeError("invalid version: %s" % identifier)
        identifier = json_document[key]
        return identifier

    def get(self, identifier):
        g = self.gentle
        identifier = self.dig(identifier)
        content = g.get(identifier)
        try:
            json_document = json.loads(content)
            print json.dumps(json_document, indent=4, sort_keys=True)
        except:
            printw(content)

    def follow(self, number):
        "Follow a pointer and get the content_hash."
        g = self.gentle
        (directory, identifier) = g.full(number)
        if directory != g.pointer_dir:
            raise TypeError("specified number is not a pointer")
        print g.get(number)

    def put(self, to_number=None, from_number_or_timestamp=None, timestamp=None):
        """
        Put some content into Gentle.

        g put <content-from-stdin>
        -> Same as gentle.put(<content>)
        -> Prints: "<content>"
        -> Verbose: "New content <content> created."

        g put <prev-version-or-new-pointer> <new-version>
        -> Changes pointer to point to new version if prev-version matches.
           (Non-matching new version raises exception.  New pointer version is '{}'.)
        -> Prints: "<pointer-to-prev-version>"
        -> Verbose: "Pointer <pointer-to-prev-version> points now to new version <new-version>.
                     Previous pointed-to version was: <prev-version>."

        g put <prev-version[-pointer]> <not-a-version> [<timestamp>]
        -> Same as gentle_next.mkversion(<prev-version>, <not-a-version>[, <timestamp>]).
        -> Or (for pointer) same as gentle.put(<pointer>, gentle_next.mkversion(...))
        -> Prints: "<new-version>" or "<pointer>"
        -> Verbose: "New version <new-version> has been created from the given inputs."

        g put <broken-pointer> <anything>  # or:
        g put <pointer> <not-a-version>
        -> Same as gentle.put(<new-pointer>, <not-a-version>).
        -> Prints: "<pointer>"
        -> Verbose: "Pointer <pointer> points now to content <not-a-version>.
                     Previous pointed-to content was <prev-content>."

        All other parameter combinations result in an exception.
        """
        g = self.gentle

        # interpret to_number:
        if to_number is None:
            content = read()
            try:
                content_json = json.loads(content)
            except:
                print g.put(content)
            else:
                print g.putj(content_json)
            return

        # interpret the latter arguments:
        from_number = None
        if timestamp is None:
            try:
                parse_time_with_offset(from_number_or_timestamp)
            except:
                from_number = from_number_or_timestamp
            else:
                timestamp = from_number_or_timestamp

        # interpret to_number more:
        to_pointer = None
        to_pointer_exists = None
        to_pointer_sane = True
        to_pointer_content = None
        to_content = None
        to_content_json = ()  # json.loads() won't return () on success
        try:
            (to_dir, to_pointer) = g.full(to_number)
        except:
            to_pointer_exists = False
            from string import hexdigits as hexd
            if len(to_number) != len(g.empty_version) or any(c not in hexd for c in to_number):
                raise ValueError("invalid pointer: %r" % to_number)
            to_pointer = to_number
        else:
            to_pointer_exists = True
            to_number = to_pointer
            if to_dir == g.pointer_dir:
                to_number = g.get(to_pointer)
            else:
                to_pointer = None
            to_pointer_content = to_number
            try:
                to_content = g.get(to_pointer_content)
            except:  # broken pointer
                to_pointer_sane = False
            try:    to_content_json = json.loads(to_content)
            except: pass

        # interpret from_number:
        from_content = None
        from_content_json = ()  # json.loads() won't return () on success
        if from_number is None:  # content will come from stdin
            from_content = read()  # either JSON or not is fine
            try:
                from_content_json = json.loads(from_content)
            except:
                from_number = g.put(from_content)
            else:
                from_number = g.putj(from_content_json)
        else:
            (from_dir, from_number) = g.full(from_number)
            if from_dir == g.pointer_dir:
                from_number = g.get(from_number)  # follow pointer to re-use its content
            from_content = g.get(from_number)
            try:    from_content_json = json.loads(from_content)
            except: pass

        # Try the case of the broken pointer:
        if not to_pointer_sane:
            print g.put(to_pointer, from_number)
            return

        # Try the case where from_content is a new version:
        if isinstance(from_content_json, dict) and g.PREV_VERSION_KEY in from_content_json:
            if to_pointer is None:
                raise TypeError("first data is not a pointer")
            to_pointer_version_number = g.empty_version
            if to_pointer_exists:
                to_pointer_version_number = to_number
            if to_pointer_version_number != g.empty_version:  # validate non-empty version
                if not isinstance(to_content_json, dict) or g.PREV_VERSION_KEY not in to_content_json:
                    raise TypeError("first data is not a version, while second data is a version")

            # Go back until we find the matching previous version number:
            version_number = from_number
            version = from_content_json
            while True:
                prev_version_number = version[g.PREV_VERSION_KEY]
                if not isinstance(prev_version_number, basestring):
                    raise TypeError("invalid version: %s" % version_number)
                if prev_version_number == to_pointer_version_number:
                    break
                if prev_version_number == g.empty_version:
                    print "WARNING: first version is not an ancestor of second version"
                    print "First version was: %s" % to_pointer_version_number
                    break
                version = json.loads(g.get(prev_version_number))

            # Change pointer to new version:
            print g.put(to_pointer, version_number)
            return

        # Try the case where to_number is or points to a version:
        if isinstance(to_content_json, dict) and (to_number == g.empty_version or g.PREV_VERSION_KEY in to_content_json):
            if to_number == g.empty_version and from_number == g.empty_version:
                number = to_number  # TODO
            else:
                number = g.mkversion(to_number, from_number)
                if to_pointer is not None:
                    number = g.put(to_pointer, number)
            print number
            return

        # Try the case where to_number is a pointer:
        if to_pointer is not None:
            print g.put(to_pointer, from_number)
            return

        # All other parameter combinations result in an exception:
        raise TypeError("invalid arguments")

    def json(self, identifier, python_snippet=None):
        g = self.gentle
        if python_snippet is None:
            python_snippet = read()
        identifier = self.dig(identifier)
        return g.json(identifier, python_snippet)

    def _cli_get_method(self, method_name):
        try:
            m = getattr(self, method_name)
        except:
            # e.g. function_name == "import" -> def import_(...): ...
            m = getattr(self, method_name + "_")
        return m, getattr(m, "__func__", m)

    def _cli(self, method_name, *args):
        """
        Command line interface.
        """
        try:
            m, f = self._cli_get_method(method_name)
            return m(*args)
        except Exception as e:
            # print "ERROR:", e
            raise


def main(argv):
    """
    Command line interface.
    """
    g = GentleCLI()
    return g._cli(*argv[1:])


if __name__ == "__main__":
    import sys
    main(sys.argv)
