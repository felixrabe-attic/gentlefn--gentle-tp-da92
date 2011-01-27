package org.gentlefn.tp_da92.utilities;

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

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.gentlefn.tp_da92.base.GentleException;


public class Utilities {

    private Utilities() {
        // No instances please
    }

    private static final String HEXES = "0123456789abcdef";
    /**
     * @see http://rgagnon.com/javadetails/java-0596.html
     */
    private static String encodeBytesToHex(byte[] bytes) {
        if (bytes == null)
            return null;
        final StringBuilder hex = new StringBuilder(2 * bytes.length);
        for (final byte b : bytes) {
            hex.append(HEXES.charAt((b & 0xf0) >> 4))
                .append(HEXES.charAt((b & 0x0f)));
        }
        return hex.toString();
    }

    public static String sha256(String byteString) throws GentleException {
        MessageDigest digest = null;
        try {
            digest = MessageDigest.getInstance("SHA-256");
        }
        catch (NoSuchAlgorithmException e) {
            throw new GentleException("Could not compute SHA-256 digest", e);
        }
        digest.reset();
        byte[] result = null;
        try {
            result = digest.digest(byteString.getBytes("utf-8"));
        }
        catch (UnsupportedEncodingException e) {
            throw new GentleException("Encoding not supported", e);
        }
        return encodeBytesToHex(result);
    }

}
