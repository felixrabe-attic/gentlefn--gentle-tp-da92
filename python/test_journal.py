#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from gentle_tp_da92 import *
from gentle_tp_da92 import journaled_data_store

rnd = utilities.random

def mkg():
    memory_ds = Gentle(memory_based)
    debug_ds = Gentle(debugging_wrapper, memory_ds, show_content=True)
    g = Gentle(journaled_data_store, debug_ds)
    return g

def main():
    mk_ds()

if __name__ == "__main__":
    main()
