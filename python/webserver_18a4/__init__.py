#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91) - Experimental Webserver

Unique Gentle identifier for this webserver:
    18a44d6590c1bb018a4bdacf31ea80ce090d12e1db4c6bc2c21e52cea5cd72ec
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

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import os
import sys

from webserver_18a4.jsonhtml import *

__gentle_da92_identifier__ = \
    "18a44d6590c1bb018a4bdacf31ea80ce090d12e1db4c6bc2c21e52cea5cd72ec"

PNG_SIGNATURE = "89504e470d0a1a0a".decode("hex")


class HTTPRequestHandler(BaseHTTPRequestHandler):

    server_version = "gentle_da92/%s" % __gentle_da92_identifier__[:6]

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.gentle = self.server.gentle
        self.public = self.server.public

    def do_GET(self):  # TODO: this is all too complex and should be refactored into smaller steps
        if not self.public and self.client_address[0] != "127.0.0.1":
            return  # do not serve
        path = self.path[1:].split("/")
        if path == [""]:  # default document
            path = ["0000000000"]
        if len(path) == 1:
            identifier = path[0]
            try:
                directory, identifier = self.gentle.full(identifier)
            except:
                self.send_error(404, "Item not found or invalid number: %r" % identifier)
                return
            if directory == self.gentle.pointer_dir:
                type = "pointer"
            elif directory == self.gentle.content_dir:
                type = "content"
            else:
                self.send_error(500, "Unsupported content database directory: %r" % directory)
                return
            self.send_response(302)
            location = "/%s/%s" % (type, identifier)
            self.send_header("Location", location)
            self.end_headers()
            return
        if len(path) == 2:
            type, identifier = path[0], path[1]
            try:
                content = self.gentle.get(identifier)
            except:
                self.send_error(404, "Item not found or invalid number: %r" % identifier)
                return
            header = []
            if type == "pointer":
                if False:
                    self.send_response(302)
                    location = "/%s/%s" % ("content", content)
                    self.send_header("Location", location)
                    self.end_headers()
                    return
                # Just serve the respective content:
                header.append('<div style="font-style: italic; color: #999; font-size: smaller;">')
                gnt = "gentle-tp-da92:%s" % identifier
                header.append('<div style="float: right;"><a href="%s" title="%s">%s</a></div>' % (gnt, self.gentle.getdir(), gnt))
                header.append('<a href="/">Home</a> ; Pointer to ')
                header.append('<a href="/content/%(c)s">content</a>: %(c)s</div>' % dict(c=content))
                content = self.gentle.get(content)
            self.send_response(200)
            header = "".join(header)
            try:
                json_content = json.loads(content)
            except:
                if type == "pointer":
                    self.send_header("Content-type", "text/html")
                    content = header
                    content += "<p><i>To see the non-JSON content, click 'content' above.</i></p>"
                else:
                    if content[:8] == PNG_SIGNATURE:
                        self.send_header("Content-type", "image/png")
                    else:
                        self.send_header("Content-type", "text/plain")
            else:
                self.send_header("Content-type", "text/html")
                content = header
                content += '<pre style="clear: both; margin-top: 6px; margin-bottom: 6px;">'
                content += json.dumps(json_content, indent=4, sort_keys=True, cls=HTMLJSONEncoder)
                content += "</pre>\n"
            self.end_headers()
            self.wfile.write(content)


def webserver(port=49876, directory=None, public=False):
    if directory is not None:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            raise Exception("No such directory: %r" % directory)
    server_address = ("", port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    httpd.gentle = GentleNext(directory)
    httpd.public = public
    try:
        print "Serving directory %r on port %u" % (httpd.gentle.getdir(), port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print  # or we get a '^C' immediately followed by the prompt
    httpd.server_close()
