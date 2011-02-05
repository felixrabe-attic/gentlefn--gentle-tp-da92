#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gentle TP-DA92 - Data Store Testing Module.
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

from __future__ import print_function

import cProfile
from   hashlib import sha256
import pdb
import traceback

from   gentle_tp_da92 import utilities


def test(data_store):
    """
    Test a data store (must be empty).

    Example:
    >>> from gentle_tp_da92 import test_data_store, memory_based
    >>> test_data_store.test(memory_based.GentleDataStore())
    'PASS'
    """
    c_db = data_store.content_db
    p_db = data_store.pointer_db

    assert c_db.find() == []
    assert p_db.find() == []

    p = "0b3bef2bde9575c8b3251c3c92a4f99f6b770cc8f6e73509a0276e08b2cb9573"
    assert p not in c_db
    assert p not in p_db

    string = "Hello YOU"
    c = c_db + string
    assert c == sha256(string).hexdigest()
    assert c in c_db
    assert c not in p_db

    p_db[p] = c
    assert p not in c_db
    assert p in p_db
    assert p_db[p] == c

    for db in (c_db, p_db):
        try:
            "" in db  # should raise an exception
        except:
            assert True
        else:
            assert False

    assert p_db.find(p[:2]) == [p]
    assert c_db.find(c[:2]) == [c]

    string = "Second content"
    old_c = c
    c = c_db + string
    assert c == sha256(string).hexdigest()
    assert c in c_db

    p_db[p] = c
    assert p in p_db
    assert p_db[p] == c
    assert sorted(c_db.find()) == sorted([old_c, c])
    assert p_db.find() == [p]

    del p_db[p]
    assert p not in p_db
    assert sorted(c_db.find()) == sorted([old_c, c])
    assert p_db.find() == []

    # Randomized testing
    import random, os
    random_data = []
    for i in range(300):
        random_data.append(os.urandom(random.randrange(3000)))
    for i, rnd in enumerate(random_data):
        assert len(c_db.find()) == i + 2
        c = c_db + rnd
        assert len(c_db.find()) == i + 3
        assert c in c_db
        assert c not in p_db
        assert c == sha256(rnd).hexdigest()
        assert c_db[c] == rnd
        assert c_db.find(c) == [c]

        try:
            c[:-1] in c_db  # should raise an exception
        except:
            assert True
        else:
            assert False

        p = os.urandom(32).encode("hex")
        p_db[p] = c
        assert p in p_db
        assert p_db[p] == c
        assert p not in c_db
        assert p_db.find(p) == [p]
        p = utilities.random()
        p_db[p] = c
        assert p in p_db
        assert p_db[p] == c
        assert p not in c_db
        assert p_db.find(p) == [p]

        try:
            p[:-1] in p_db  # should raise an exception
        except:
            assert True
        else:
            assert False

    return "PASS"


def test_all():
    import shutil
    import tempfile
    from gentle_tp_da92 import (Gentle,
                                fs_based,
                                memory_based,
                                debugging_wrapper,
                                journaled_data_store)

    nullwriter = type("", (), {})()
    nullwriter.write = lambda *a, **k: None

    data_stores = [
        (None, Gentle(journaled_data_store, Gentle(memory_based))),
        (None, Gentle(memory_based)),
        # ("Wrapped memory_based", Gentle(debugging_wrapper, Gentle(memory_based), nullwriter)),
        # (None, Gentle(fs_based, tempfile.mkdtemp())),
        # ("Wrapped fs_based", Gentle(debugging_wrapper, Gentle(fs_based, tempfile.mkdtemp()), nullwriter)),
        ]

    for name, data_store in data_stores:
        if name is None: name = data_store.ds
        print("Testing %s:" % name)
        try:
            print(test(data_store))
        except:
            traceback.print_exc()
            pdb.post_mortem()
        finally:
            if isinstance(data_store.ds, fs_based.GentleDataStore):
                shutil.rmtree(data_store.ds.directory)
            elif isinstance(data_store.ds, debugging_wrapper.GentleDataStore):
                if isinstance(data_store.ds.data_store.ds, fs_based.GentleDataStore):
                    shutil.rmtree(data_store.ds.data_store.ds.directory)
        print()


if __name__ == "__main__":
    cProfile.run("test_all()", "test-profile")
    # test_all()
