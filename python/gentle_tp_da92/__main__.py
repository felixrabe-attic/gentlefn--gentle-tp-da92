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

import os.path
import sys

from   ._optparse import *
from   . import easy
from   . import json


_all_commands = {}


class _CommandMeta(type):

    def __init__(cls, name, bases, dict):
        super(_CommandMeta, cls).__init__(name, bases, dict)
        if not cls.__name__.startswith("_"):
            _all_commands[cls.get_name()] = cls


class _Command(object):
    __metaclass__ = _CommandMeta

    def __init__(self, common_options):
        super(_Command, self).__init__()
        self.common_options = common_options
        self.gentle = easy.Gentle(self.common_options.implementation)

    @classmethod
    def get_name(cls):
        return cls.__name__.lower()

    @staticmethod
    def get_description():
        return ""

    def parse_args(self, option_parser, args):
        self.option_parser = self.get_option_parser(option_parser)
        self.options, self.args = self.option_parser.parse_args(args)

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

    def run(self):
        pass


class Find(_Command):

    @staticmethod
    def get_description():
        return "Find identifiers starting with the argument in the data store"

    def run(self):
        lst = []
        for arg in self.args:
            lst += self.gentle.find(arg)
        for i in sorted(lst):
            print(i)


class FindC(_Command):

    @staticmethod
    def get_description():
        return "Find identifiers starting with the argument in the content database"

    def run(self):
        lst = []
        for arg in self.args:
            lst += self.gentle.c.find(arg)
        for i in sorted(lst):
            print(i)


class FindP(_Command):

    @staticmethod
    def get_description():
        return "Find identifiers starting with the argument in the pointer database"

    def run(self):
        lst = []
        for arg in self.args:
            lst += self.gentle.p.find(arg)
        for i in sorted(lst):
            print(i)


class GetC(_Command):

    @staticmethod
    def get_description():
        return "Get content for a content ID from the content database"

    def run(self):
        if len(self.args) != 1:
            self.option_parser.error("one argument expected")
        arg = self.args[0]
        result = self.gentle.c.find(arg)
        if len(result) == 1:
            print(self.gentle.c[result[0]], end='')
        else:
            self.option_parser.error("ambiguous identifier: %r" % arg)


class GetP(_Command):

    @staticmethod
    def get_description():
        return "Get a content ID for a pointer ID from the pointer database"

    def run(self):
        if len(self.args) != 1:
            self.option_parser.error("one argument expected")
        arg = self.args[0]
        result = self.gentle.p.find(arg)
        if len(result) == 1:
            print(self.gentle.p[result[0]])
        else:
            self.option_parser.error("ambiguous identifier: %r" % arg)


class JSON(_Command):

    @staticmethod
    def get_description():
        return "Evaluate a JSON expression"

    def _bad_expr(self, expr):
        raise Exception("bad expression: %r" % expr)

    def _resolve(self, context, context_type):
        g = self.gentle
        if context_type[-1:] == ["pointer"]:
            context = self.gentle.p[context]
            context_type[-1] = "content"
        if context_type[-1:] == ["content"]:
            context = self.gentle.c[context]
        if context_type[-2:] in (["json", "content"], ["metadata", "content"]):
            context = json.loads(context)
            context_type = []
        return context, context_type

    def run(self):
        g = self.gentle
        context = None
        context_type = []
        for arg in self.args:
            if arg == ":raw":
                context_type = ["raw"]
                continue
            if context is None:
                if os.path.exists(arg):
                    arg = open(arg).read().strip()
                result = g.find(arg)
                if len(result) != 1:
                    self._bad_expr(arg)
                result_other = result[0]
                result = g.c.find(arg)
                if result:
                    context = g.c[result[0]]
                else:
                    context = g.c[g.p[result_other]]
                if context_type != ["raw"]:
                    context = json.loads(context)
                continue
            if isinstance(context, list):
                if arg == ":len":
                    context = len(context)
                else:
                    arg = json.loads(arg)
                    if not isinstance(arg, int):
                        self._bad_expr(arg)
                    context = context[arg]
                    if context_type[-2:] == ["json", "content"]:
                        context = g.c[context]
                continue
            if isinstance(context, dict):
                if ":" in arg:  # contains the type, must match exactly
                    if arg == ":keys" or arg.startswith(":key:"):
                        _saved_context = context
                        context = sorted(context.keys())
                        if arg.startswith(":key:"):
                            key = context[json.loads(arg.split(":", 2)[-1])]
                            context = _saved_context[key]
                            arg = key
                        else:
                            context_type = []
                            arg = ""
                    else:
                        context = context[arg]
                    if context_type != ["raw"]:
                        context_type = arg.split(":")[1:]
                        if isinstance(context, basestring):
                            context, context_type = self._resolve(context, context_type)
                else:  # follow contents and pointers dynamically
                    found_keys = []
                    for key in context.keys():
                        if key == arg or key.startswith(arg + ":"):
                            found_keys.append(key)
                    if len(found_keys) != 1:
                        self._bad_expr(arg)
                    key = found_keys[0]
                    context = context[key]
                    if context_type != ["raw"]:
                        context_type = key.split(":")[1:]
                        if isinstance(context, basestring):
                            context, context_type = self._resolve(context, context_type)
                continue
            self._bad_expr(arg)

        if context_type == ["raw"]:
            print(context, end='')
        else:
            json.pprint(context)


class Put(_Command):

    @staticmethod
    def get_description():
        return "(NOOP) Put content or a pointer into the data store"

    def run(self):
        self.option_parser.error("not implemented")


class Type(_Command):

    @staticmethod
    def get_description():
        return "Get the type of an identifier, 'content' or 'pointer'"

    def run(self):
        if len(self.args) != 1:
            self.option_parser.error("one argument expected")
        arg = self.args[0]
        found_c = self.gentle.c.find(arg)
        found_p = self.gentle.p.find(arg)
        len_both = len(found_c) + len(found_p)
        if len_both > 1:
            self.option_parser.error("ambiguous identifier: %r" % arg)
        if len_both < 1:
            self.option_parser.error("identifier not found: %r" % arg)
        if found_c:
            print("content")
        else:
            print("pointer")


def main():
    option_parser = OptionParser(
        prog="gentle_tp_da92",
        usage="Usage: %prog [common options] <command> [command options]",
        description="Gentle TP-DA92 command line interface to the data store.",
        add_help_option=False
        )
    option_parser.disable_interspersed_args()

    common_option_group = OptionGroup(option_parser, "Common options")

    common_option_group.add_option(
        "-h", "--help", default=False, action="store_true",
        help="""Show this help message and exit; or, if <command> has been
                specified, show that command's help message"""
        )

    common_option_group.add_option(
        "--implementation", default="gentle_tp_da92.fs_based",
        help="""The module used as the implementation for data store access;
                default: '%default'"""
        )

    common_option_group.add_option(
        "--raw", default=False, action="store_true",
        help="""Do not process input/output, instead pass content unchanged
                to/from the data store"""
        )

    option_parser.add_option_group(common_option_group)

    common_options, args = option_parser.parse_args()
    command = None
    if len(args) > 0:
        command, args = _all_commands.get(args[0].lower()), args[1:]

    if common_options.help or command is None:
        if command is not None:
            option_parser = command.get_option_parser(option_parser)
        option_parser.print_help()
        if command is None:
            print()
            print("All available commands:")
            for name, command in sorted(_all_commands.items()):
                print("    %-7s %s" % (name, command.get_description()))
            print()
            # Shamelessly stolen from 'git --help':
            print(option_parser.expand_prog_name(
                "See '%prog --help <command>' for more information on a "
                "specific command"))
        sys.exit(0)

    command = command(common_options)
    command.parse_args(option_parser, args)
    command.run()


if __name__ == "__main__":
    main()
