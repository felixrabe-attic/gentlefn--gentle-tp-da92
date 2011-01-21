#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

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

import email.utils
import json
from   json.encoder import encode_basestring_ascii
import os
from   xml.sax.saxutils import escape as xml_escape

from gentle_da92de4118f6fa91_next import GentleNext


class HTMLChunk(object):

    def __init__(self, string_value):
        self.string_value = string_value


class HTMLJSONEncoder(json.JSONEncoder):

    # This code is 90% copied from the standard Python 'json' module.
    # Adapted by Felix Rabe for (raw) pretty-printed HTML output with some links.

    # Traversing works similar to GentleNext.__findall_in_object().

    def _iterencode_list(self, lst, markers=None, current_gentle_key=None):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        yield '['
        if self.indent is not None:
            self.current_indent_level += 1
            newline_indent = self._newline_indent()
            separator = self.item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            separator = self.item_separator
        first = True
        for value in lst:
            if first:
                first = False
            else:
                yield separator
            for chunk in self._iterencode(value, markers, current_gentle_key):
                yield chunk
        if newline_indent is not None:
            self.current_indent_level -= 1
            yield self._newline_indent()
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(self, dct, markers=None):
        if not dct:
            yield '{}'
            return
        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        key_separator = self.key_separator
        if self.indent is not None:
            self.current_indent_level += 1
            newline_indent = self._newline_indent()
            item_separator = self.item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = self.item_separator
        first = True
        if self.ensure_ascii:
            encoder = encode_basestring_ascii
        else:
            encoder = encode_basestring
        allow_nan = self.allow_nan
        if self.sort_keys:
            keys = dct.keys()
            keys.sort()
            items = [(k, dct[k]) for k in keys]
        else:
            items = dct.iteritems()
        _encoding = self.encoding
        _do_decode = (_encoding is not None
            and not (_encoding == 'utf-8'))
        for key, value in items:
            if isinstance(key, str):
                if _do_decode:
                    key = key.decode(_encoding)
            elif isinstance(key, basestring):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                key = floatstr(key, allow_nan)
            elif isinstance(key, (int, long)):
                key = str(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif key is None:
                key = 'null'
            elif self.skipkeys:
                continue
            else:
                raise TypeError("key {0!r} is not a string".format(key))
            if first:
                first = False
            else:
                yield item_separator
            yield encoder(key)
            yield key_separator
            for chunk in self._iterencode(value, markers, current_gentle_key=key.split(":")):
                yield chunk
        if newline_indent is not None:
            self.current_indent_level -= 1
            yield self._newline_indent()
        yield '}'
        if markers is not None:
            del markers[markerid]

    def _iterencode(self, o, markers=None, current_gentle_key=None):
        if isinstance(o, basestring):
            html_url = None
            if current_gentle_key is not None:
                if current_gentle_key[-1] in GentleNext.REFERENCE_KEYS:
                    html_url = "/%s/%s" % (current_gentle_key[-1], o)
                elif current_gentle_key[-1] == "url":
                    html_url = o
                elif current_gentle_key[-1] == "email":
                    realname, address = email.utils.parseaddr(o)
                    html_url = "mailto:" + address
                if html_url is not None:
                    html_url = xml_escape(html_url)
                    yield HTMLChunk('<a href="%s">' % html_url)
            if self.ensure_ascii:
                encoder = encode_basestring_ascii
            else:
                encoder = encode_basestring
            _encoding = self.encoding
            if (_encoding is not None and isinstance(o, str)
                    and not (_encoding == 'utf-8')):
                o = o.decode(_encoding)
            yield encoder(o)
            if html_url is not None:
                yield HTMLChunk('</a>')
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, (int, long)):
            yield str(o)
        elif isinstance(o, float):
            yield floatstr(o, self.allow_nan)
        elif isinstance(o, (list, tuple)):
            for chunk in self._iterencode_list(o, markers, current_gentle_key=current_gentle_key):
                yield chunk
        elif isinstance(o, dict):
            for chunk in self._iterencode_dict(o, markers):
                yield chunk
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            for chunk in self._iterencode_default(o, markers):
                yield chunk
            if markers is not None:
                del markers[markerid]

    def iterencode(self, o):
        """Encode the given object and yield each string representation as
        available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        yield '<pre style="clear: both; margin-top: 6px; margin-bottom: 6px;">'
        for i in self._iterencode(o, markers):
            if isinstance(i, HTMLChunk):
                yield i.string_value
            else:
                yield xml_escape(i, {'"': '&quot;'})
        yield "</pre>\n"


def main():
    inputs = [f for f in os.listdir("tests") if f.endswith(".input.json")]
    for input_fn in inputs:
        number = input_fn.split(".", 1)[0]
        output_fn = number + ".output.html"

        input_fn = os.path.join("tests", input_fn)
        output_fn = os.path.join("tests", output_fn)

        input = open(input_fn, "rb").read()
        input = json.loads(input)
        output = json.dumps(input, indent=4, sort_keys=True, cls=HTMLJSONEncoder)
        open(output_fn, "wb").write(output)


if __name__ == "__main__":
    main()
