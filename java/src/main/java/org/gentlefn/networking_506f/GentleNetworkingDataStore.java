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
package org.gentlefn.networking_506f;

import org.gentlefn.tp_da92.datastore.interfaces.GentleContentDB;
import org.gentlefn.tp_da92.datastore.interfaces.GentleDataStore;
import org.gentlefn.tp_da92.datastore.interfaces.GentlePointerDB;


public class GentleNetworkingDataStore implements org.gentlefn.tp_da92.datastore.interfaces.GentleDataStore {

    private GentleDataStore wrappedDataStore;

    public GentleNetworkingDataStore(GentleDataStore wrappedDataStore) {
        super();
        this.wrappedDataStore = wrappedDataStore;
    }

    public void serve(String address) {
    }

    public GentleContentDB getContentDB() {
        return wrappedDataStore.getContentDB();
    }

    public GentlePointerDB getPointerDB() {
        return wrappedDataStore.getPointerDB();
    }

}
