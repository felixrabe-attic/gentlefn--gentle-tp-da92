#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The explicit goal of Gentle is to FUNDAMENTALLY SIMPLIFY COMPUTER PROGRAMMING
AND USER INTERFACES.

This Technology Preview implements the fundamental operations needed to store
and retrieve data on a computer, using two simple, filesystem-based, dictionary
data structures.

Provides the basic, filesystem-based database classes, implemented in Python.
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

from distutils.core import setup

setup(
        name = "gentle-tp-da92",
        version = "0.0.0",
        description = "Gentle Technology Preview DA92 (TP-DA92)",
        long_description = __doc__.strip(),
        author = "Felix Rabe",
        author_email = "public@felixrabe.net",
        url = "https://github.com/gentlefn/gentle-tp-da92/",
        packages = [
            "gentle_tp_da92",
            ],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Environment :: MacOS X",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Java",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Unix Shell",
            "Topic :: Database",
            "Topic :: Database :: Database Engine/Servers",
            # "Topic :: Desktop Environment",
            # "Topic :: Internet :: Name Service (DNS)",
            "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
            "Topic :: Other/Nonlisted Topic",
            # "Topic :: Software Development :: Build Tools",
            "Topic :: Software Development :: Libraries :: Java Libraries",
            "Topic :: Software Development :: Libraries :: Python Modules",
            # "Topic :: Software Development :: User Interfaces",
            # "Topic :: Software Development :: Version Control",
            # "Topic :: System :: Archiving",
            "Topic :: System :: Filesystems",
            "Topic :: Text Editors :: Integrated Development Environments (IDE)",
            ],
      )
