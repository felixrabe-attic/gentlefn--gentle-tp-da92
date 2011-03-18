#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Utility Module.

This module provides some utility functions to the Gentle Core Module.
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

import os


## CONSTANTS

IDENTIFIER_LENGTH = 256 / 4
IDENTIFIER_DIGITS = "0123456789abcdef"


## EXCEPTIONS

class GentleException(Exception):
    """
    Base class for all exceptions originating in Gentle.
    """

class InvalidIdentifierException(GentleException, LookupError):
    """
    Invalid Gentle identifier.
    """
    pass


## UTILITY FUNCTIONS IN ALPHABETICAL ORDER

def create_file_with_mode(filename, mode):
    return os.fdopen(os.open(filename, os.O_CREAT | os.O_WRONLY, mode), "wb")

def random():
    """
    Return a random-generated 256-bit number in hexadecimal representation.

    These numbers are suitable as identifiers in a pointer database.
    """
    return os.urandom(256 / 8).encode("hex")

def is_identifier_format_valid(identifier, partial=False):
    if not isinstance(identifier, basestring): return False
    if not (len(identifier) <= IDENTIFIER_LENGTH and
            all(c in IDENTIFIER_DIGITS for c in identifier)):
        return False
    if partial or len(identifier) == IDENTIFIER_LENGTH: return True
    return False

def validate_identifier_format(identifier, partial=False):
    if not is_identifier_format_valid(identifier, partial):
        raise InvalidIdentifierException(identifier)
