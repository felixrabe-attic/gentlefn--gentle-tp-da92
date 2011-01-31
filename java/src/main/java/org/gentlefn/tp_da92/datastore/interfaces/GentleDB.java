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
package org.gentlefn.tp_da92.datastore.interfaces;

import java.util.RandomAccess;
import java.util.Set;

import org.gentlefn.tp_da92.utilities.InvalidIdentifierException;


/**
 * Base class for Gentle TP-DA92 databases implemented in Java.
 *
 * Gentle TP-DA92 databases map identifiers to values.
 *
 * Classes inheriting from GentleDB strive to emulate standard Java container
 * interfaces to the greatest extent possible.
 */
public interface GentleDB extends RandomAccess {

    /** Get an item from the database. */
    byte[] get(byte[] identifier) throws InvalidIdentifierException;

    /** Delete an item from the database. */
    byte[] remove(byte[] identifier) throws InvalidIdentifierException;

    /** Find all the identifiers registered in this database that start with
        partialIdentifier.

        @return a Set, which may be empty.

        If partialIdentifier is "", return the full list of all identifiers in
        the database.
    */
    Set<byte[]> find(byte[] partialIdentifier);

    boolean containsKey(byte[] identifier);

}
