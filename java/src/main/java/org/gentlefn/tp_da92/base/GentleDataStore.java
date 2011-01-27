package org.gentlefn.tp_da92.base;

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

import java.io.File;
import java.io.IOException;


public class GentleDataStore {

    private File topDirectory;
    private GentleContentDB contentDB;
    private GentlePointerDB pointerDB;

    public GentleDataStore(File directory) throws GentleException {
        topDirectory = directory;
        try {
            contentDB = new GentleContentDB(new File(topDirectory, "content_db"));
            pointerDB = new GentlePointerDB(new File(topDirectory, "pointer_db"));
        }
        catch (IOException e) {
            throw new GentleException("Could not instantiate database(s)", e);
        }
    }

    public File getDirectory() {
        return topDirectory;
    }

}
