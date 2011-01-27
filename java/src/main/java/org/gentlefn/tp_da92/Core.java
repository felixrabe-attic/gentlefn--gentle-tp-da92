package org.gentlefn.tp_da92;

import java.io.File;
import java.io.IOException;

public class Core {

    public static final File DEFAULT_DATA_DIR = new File(System.getProperty("user.home"), ".gentle_da92de4118f6fa91");
    public static final String ENVIRON_DATA_DIR_KEY = "GENTLE_DA92DE41_DIR";

    private File contentDir;
    private File pointerDir;

    public Core(File directory) throws IOException {
        if (directory == null) {
            String envDataDir = System.getenv(ENVIRON_DATA_DIR_KEY);
            if (envDataDir == null) {
                directory = DEFAULT_DATA_DIR;
            } else {
                directory = new File(envDataDir);
            }
        }
        System.out.println(directory.getCanonicalPath());
        directory.mkdirs();  // TODO: make them only readable by owner

        contentDir = new File(directory, "content_db");
        pointerDir = new File(directory, "pointer_db");

        mkdirIfNotExists(directory);
        mkdirIfNotExists(contentDir);
        mkdirIfNotExists(pointerDir);

        if (!(directory.isDirectory() && contentDir.isDirectory() && pointerDir.isDirectory())) {
            throw new IOException("Specified an existing path that is not a directory");
        }
    }

    private void mkdirIfNotExists(File directory) {
        directory.mkdir();

        // Make readable / writable / executable by owner only:
        directory.setReadable(false, false);
        directory.setReadable(true, true);
        directory.setWritable(false, false);
        directory.setWritable(true, true);
        directory.setExecutable(false, false);
        directory.setExecutable(true, true);
    }

    public Core() throws IOException {
        this(null);
    }

}
