package org.gentlefn.tp_da92;

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

import org.gentlefn.tp_da92.base.GentleDataStore;
import org.gentlefn.tp_da92.base.GentleException;
import org.gentlefn.tp_da92.utilities.Utilities;


public class CommandLine {

    public static final File DEFAULT_DATA_DIR = new File(System.getProperty("user.home"), ".gentle_da92de4118f6fa91");
    public static final String ENVIRON_DATA_DIR_KEY = "GENTLE_DA92DE41_DIR";

    private static void mkdirIfNotExists(File directory) {
        if (directory.mkdir()) {
            // Make readable / writable / executable by owner only:
            directory.setReadable(false, false);
            directory.setReadable(true, true);
            directory.setWritable(false, false);
            directory.setWritable(true, true);
            directory.setExecutable(false, false);
            directory.setExecutable(true, true);
        }
    }

    public static void main(String[] args) throws IOException {
        String directory = null;
        File topDirectory = null;
        if (args.length >= 1) {
            directory = args[0];
        }
        if (directory == null) {
            directory = System.getenv(ENVIRON_DATA_DIR_KEY);
            if (directory == null) {
                topDirectory = DEFAULT_DATA_DIR;
            } else {
                topDirectory = new File(directory);
            }
        }

        File contentDir = new File(topDirectory, "content_db");
        File pointerDir = new File(topDirectory, "pointer_db");

        mkdirIfNotExists(topDirectory);
        mkdirIfNotExists(contentDir);
        mkdirIfNotExists(pointerDir);

        if (!(topDirectory.isDirectory() && contentDir.isDirectory() && pointerDir.isDirectory())) {
            throw new IOException("Specified an existing path that is not a directory");
        }

        GentleDataStore gentle = null;
        try {
            gentle = new GentleDataStore(topDirectory);
            System.out.println("Hello " + gentle.getDirectory() + "!");
            System.out.println(Utilities.sha256("1234stuff"));
        }
        catch (GentleException e) {
            System.err.println(e);
            System.exit(1);
        }
    }

}
