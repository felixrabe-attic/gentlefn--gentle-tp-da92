#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle Technology Preview (da92de4118f6fa91) - Webserver main() (CLI)

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

import optparse
import os
import sys

from webserver_18a4 import webserver


def build_option_parser():
    option_parser = optparse.OptionParser()

    option_parser.add_option(
        "-p", "--port", type="int", default=49876
        )

    option_parser.add_option(
        "-d", "--gentle-dir", "--directory"
        )

    option_parser.add_option(
        "--public", default=False, action="store_true",
        help="Serve to other clients than just 127.0.0.1 as well"
        )

    return option_parser


def parse_options():
    option_parser = build_option_parser()
    options, args = option_parser.parse_args()
    return options


def main():
    directory = None
    options = parse_options()
    port = options.port
    directory = options.gentle_dir
    webserver(port, directory, public=options.public)


if __name__ == "__main__":
    main()
