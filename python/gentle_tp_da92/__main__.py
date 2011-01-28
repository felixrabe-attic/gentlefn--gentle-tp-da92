#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Command Line Interface.

Provides an accessible and well-documented interface to a Gentle TP-DA92 data
store.
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

from __future__ import print_function

import sys

from   ._optparse import *
from   . import easy


_all_commands = {}


class _CommandMeta(type):

    def __init__(cls, name, bases, dict):
        super(_CommandMeta, cls).__init__(name, bases, dict)
        if cls.__name__ != "Command":
            _all_commands[cls.get_name()] = cls


class Command(object):
    __metaclass__ = _CommandMeta

    @classmethod
    def get_name(cls):
        return cls.__name__.lower()

    @staticmethod
    def get_description():
        return ""

    @classmethod
    def get_option_parser(cls, parent_optparser):
        usage = parent_optparser.expand_prog_name(
            "Usage: %%prog [common options] %s [command options]" %
            cls.get_name())

        option_parser = OptionParser(
            usage=usage,
            description=cls.get_description() + "."
        )

        return option_parser


class Get(Command):

    @staticmethod
    def get_description():
        return "Get content or a pointer from the data store"

    @classmethod
    def get_option_parser(cls, parent_optparser):
        option_parser = super(Get, cls).get_option_parser(parent_optparser)
        return option_parser


class Put(Command):

    @staticmethod
    def get_description():
        return "Put content or a pointer into the data store"


def main():
    option_parser = OptionParser(
        prog="gentle_tp_da92",
        usage="Usage: %prog [common options] <command> [command options]",
        description="Gentle TP-DA92 command line interface to the data store.",
        add_help_option=False
        )
    option_parser.disable_interspersed_args()

    common_options = OptionGroup(option_parser, "Common options")

    common_options.add_option(
        "-h", "--help", default=False, action="store_true",
        help="""Show this help message and exit; or, if <command> has been
                specified, show that command's help message"""
        )

    common_options.add_option(
        "--implementation", default="gentle_tp_da92.fs_based",
        help="""The module used as the implementation for data store access;
                default: '%default'"""
        )

    common_options.add_option(
        "--raw", default=False, action="store_true",
        help="""Do not process input/output, instead pass content unchanged
                to/from the data store"""
        )

    option_parser.add_option_group(common_options)

    options, args = option_parser.parse_args()
    command = None
    if len(args) > 0:
        command, args = _all_commands.get(args[0]), args[1:]

    if options.help or command is None:
        if command is not None:
            option_parser = command.get_option_parser(option_parser)
        option_parser.print_help()
        if command is None:
            print()
            print("All available commands:")
            for name, command in _all_commands.iteritems():
                print("    %-7s %s" % (name, command.get_description()))
            print()
            # Shamelessly stolen from 'git --help':
            print(option_parser.expand_prog_name(
                "See '%prog --help <command>' for more information on a "
                "specific command"))
        sys.exit(0)

    cmd_options, cmd_args = \
        command.get_option_parser(option_parser).parse_args(args)


if __name__ == "__main__":
    main()
