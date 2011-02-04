#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from gentle_tp_da92 import *
from gentle_tp_da92 import journaled_data_store

def mk_ds():
    memory_ds = memory_based.GentleDataStore()
    debug_ds = debugging_wrapper.GentleDataStore(memory_ds, sys.stdout)
    ds = journaled_data_store.GentleDataStore(debug_ds)
    return ds

def main():
    mk_ds()

if __name__ == "__main__":
    main()
