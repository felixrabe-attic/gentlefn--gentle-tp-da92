#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import os
import sys

from gentle_tp_da92 import *

url = sys.argv[1]

DEFAULT_ACTION = """import sys, webbrowser
if not url.startswith("%s:" % PROTOCOL):
    sys.exit(1)
url = url[len(PROTOCOL)+1:]
webbrowser.open_new_tab(urlprefix + url)
"""

# Load configuration, or write default configuration:
CONF_PID = "9b2597266690501debebfa18a797701b134571b71b44889d5c9835f1eb69d09c"
gntl = easy.Gentle(fs_based)  # default data store
if CONF_PID in gntl.p:
    content = gntl[gntl[CONF_PID]]
    configuration = json.loads(content)
else:
    from webserver_18a4 import __main__
    default_port = __main__.build_option_parser().get_option("--port").default
    configuration = {
        "action": DEFAULT_ACTION,
        "variables": {
            "PROTOCOL": "gentle-tp-da92",
            "url": None,
            "urlprefix": "http://localhost:%u/" % default_port,
        },
    }
    gntl.p[CONF_PID] = gntl.c + json.pretty(configuration)

# Render the URL according to configuration["action"]:
vars = configuration["variables"]
vars["url"] = url
exec configuration["action"] in vars
