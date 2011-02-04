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

from hashlib import sha256

from gentle_tp_da92 import utilities


def test(data_store):
    """
    Test a data store (must be empty).

    Example:
    >>> from gentle_tp_da92 import test_data_store, memory_based
    >>> test_data_store.test(memory_based.GentleDataStore())
    'PASS'
    """
    cdb = data_store.content_db
    pdb = data_store.pointer_db

    assert cdb.find() == []
    assert pdb.find() == []

    p = "0b3bef2bde9575c8b3251c3c92a4f99f6b770cc8f6e73509a0276e08b2cb9573"
    assert p not in cdb
    assert p not in pdb

    string = "Hello YOU"
    c = cdb + string
    assert c == sha256(string).hexdigest()
    assert c in cdb
    assert c not in pdb

    pdb[p] = c
    assert p not in cdb
    assert p in pdb
    assert pdb[p] == c

    for db in (cdb, pdb):
        try:
            "" in db  # should raise an exception
        except:
            assert True
        else:
            assert False

    assert pdb.find(p[:2]) == [p]
    assert cdb.find(c[:2]) == [c]

    string = "Second content"
    old_c = c
    c = cdb + string
    assert c == sha256(string).hexdigest()
    assert c in cdb

    pdb[p] = c
    assert p in pdb
    assert pdb[p] == c
    assert sorted(cdb.find()) == sorted([old_c, c])
    assert pdb.find() == [p]

    del pdb[p]
    assert p not in pdb
    assert sorted(cdb.find()) == sorted([old_c, c])
    assert pdb.find() == []

    # Randomized testing
    import random, os
    random_data = []
    for i in range(800):
        random_data.append(os.urandom(random.randrange(5000)))
    for i, rnd in enumerate(random_data):
        assert len(cdb.find()) == i + 2
        c = cdb + rnd
        assert len(cdb.find()) == i + 3
        assert c in cdb
        assert c not in pdb
        assert c == sha256(rnd).hexdigest()
        assert cdb[c] == rnd
        assert cdb.find(c) == [c]

        try:
            c[:-1] in cdb  # should raise an exception
        except:
            assert True
        else:
            assert False

        p = os.urandom(32).encode("hex")
        pdb[p] = c
        assert p in pdb
        assert pdb[p] == c
        assert p not in cdb
        assert pdb.find(p) == [p]
        p = utilities.random()
        pdb[p] = c
        assert p in pdb
        assert pdb[p] == c
        assert p not in cdb
        assert pdb.find(p) == [p]

        try:
            p[:-1] in pdb  # should raise an exception
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
                                debugging_wrapper)

    nullwriter = type("", (), {})()
    nullwriter.write = lambda *a, **k: None

    data_stores = [
        (None, Gentle(memory_based)),
        ("Wrapped memory_based", Gentle(debugging_wrapper, Gentle(memory_based), nullwriter)),
        (None, Gentle(fs_based, tempfile.mkdtemp())),
        ("Wrapped fs_based", Gentle(debugging_wrapper, Gentle(fs_based, tempfile.mkdtemp()), nullwriter)),
        ]

    for name, data_store in data_stores:
        if name is None: name = data_store.ds
        print("Testing %s:" % name)
        try:
            print(test(data_store))
        finally:
            if isinstance(data_store.ds, fs_based.GentleDataStore):
                shutil.rmtree(data_store.ds.directory)
            elif isinstance(data_store.ds, debugging_wrapper.GentleDataStore):
                if isinstance(data_store.ds.data_store.ds, fs_based.GentleDataStore):
                    shutil.rmtree(data_store.ds.data_store.ds.directory)
        print()


if __name__ == "__main__":
    test_all()
