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
import org.gentlefn.tp_da92.datastore.memorybased.GentleMemoryDataStore;


public class CommandLine {

    public static void main(String[] args) {
        try {
            GentleDataStore gentle = new GentleMemoryDataStore();
            GentleContentDB contentDB = gentle.getContentDB();
            GentlePointerDB pointerDB = gentle.getPointerDB();
            System.out.println("" + gentle + " " + contentDB + " " + pointerDB);
            byte[] content = "This is some byte crap".getBytes("UTF-8");
            byte[] contentIdentifier = contentDB.add(content);
            System.out.println(new String(contentIdentifier));
        }
        catch (Exception e) {
            System.out.println(e);
            System.exit(1);
        }
    }

}
