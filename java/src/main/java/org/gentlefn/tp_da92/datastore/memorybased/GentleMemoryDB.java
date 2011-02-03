/*
 * Copyright (C) 2010, 2011  Felix Rabe
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.gentlefn.tp_da92.datastore.memorybased;

import static org.gentlefn.tp_da92.utilities.Utilities.validateIdentifierFormat;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.gentlefn.tp_da92.datastore.interfaces.GentleDB;
import org.gentlefn.tp_da92.utilities.InvalidIdentifierException;


/**
 * Base class for Gentle TP-DA92 memory-based databases.
 */
class GentleMemoryDB implements GentleDB {

    protected Map<byte[], byte[]> database;

    GentleMemoryDB() {
        super();
        database = new HashMap<byte[], byte[]>();
    }

    public byte[] get(byte[] identifier) throws InvalidIdentifierException {
        validateIdentifierFormat(identifier);
        return database.get(identifier);
    }

    public byte[] remove(byte[] identifier) {
        return database.remove(identifier);
    }

    public Set<byte[]> find(byte[] partialIdentifier) {
        Set<byte[]> result = new HashSet<byte[]>();
        for (byte[] identifier: database.keySet()) {
            if (new String(identifier).startsWith(new String(partialIdentifier))) {
                result.add(identifier);
            }
        }
        return result;
    }

    public boolean containsKey(byte[] identifier) {
        return database.containsKey(identifier);
    }

}
