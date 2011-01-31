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

import org.gentlefn.tp_da92.datastore.interfaces.GentlePointerDB;
import org.gentlefn.tp_da92.utilities.InvalidIdentifierException;


class GentleMemoryPointerDB extends GentleMemoryDB implements GentlePointerDB {

    public byte[] put(byte[] pointerIdentifier, byte[] contentIdentifier) throws InvalidIdentifierException {
        validateIdentifierFormat(pointerIdentifier);
        validateIdentifierFormat(contentIdentifier);
        return database.put(pointerIdentifier, contentIdentifier);
    }

}
