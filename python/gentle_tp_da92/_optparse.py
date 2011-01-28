#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - optparse classes.
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

import optparse


class Options(object):

    def __init__(self, option_parser, options):
        super(Options, self).__init__()
        for option_name in option_parser.get_all_option_names():
            # Do the equivalent of:
            # self.<option_name> = options.<option_name>
            setattr(self, option_name, getattr(options, option_name))

    def copy(self):
        import copy
        return copy.copy(self)


class OptionParser(optparse.OptionParser):

    def __init__(self, *a, **k):
        if k.get("formatter") is None:
            # Make help formatting provide more space for help text by
            # decreasing max_help_position from the default 24 to 16:
            k["formatter"] = optparse.IndentedHelpFormatter(max_help_position=16)
        if isinstance(k.get("description"), basestring):
            k["description"] = " ".join(k["description"].split())
        optparse.OptionParser.__init__(self, *a, **k)

    def add_option(self, *a, **k):
        if "help" in k:
            k["help"] = " ".join(k["help"].split())
        return optparse.OptionParser.add_option(self, *a, **k)

    def check_values(self, options, args):
        # Make sure required options are specified:
        if hasattr(self, "required_option_group"):
            for required_option in self.required_option_group.option_list:
                if getattr(options, required_option.dest) is None:
                    self.error("required option %r is missing" %
                               required_option._long_opts[0])
        return options, args

    def parse_args(self, *a, **k):
        options, args = optparse.OptionParser.parse_args(self, *a, **k)
        return Options(self, options), args

    def get_all_option_names(self):
        all_option_names = set(o.dest for o in self.option_list) - set((None,))
        for opt_group in self.option_groups:
            newset = set(o.dest for o in opt_group.option_list)
            all_option_names = all_option_names.union(newset)
        all_option_names = sorted(all_option_names)
        return all_option_names

    def print_description(self):
        print self.formatter.format_description(self.get_description())


class OptionGroup(optparse.OptionGroup):

    def add_option(self, *a, **k):
        if "help" in k:
            k["help"] = " ".join(k["help"].split())
        return optparse.OptionGroup.add_option(self, *a, **k)


class HiddenOptionGroup(OptionGroup):

    def __init__(self, parser, title="", *a, **k):
        OptionGroup.__init__(self, parser, title, *a, **k)

    def format_help(self, *a, **k):
        return ""  # It's a hidden option group after all :)
