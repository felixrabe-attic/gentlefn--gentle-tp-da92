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
package org.gentlefn.tp_da92.utilities;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Random;


public class Utilities {

    private Utilities() {
        // No instances please
    }

    private static final int IDENTIFIER_LENGTH = 256 / 4;
    private static final String IDENTIFIER_DIGITS = "0123456789abcdef";
    /**
     * @see http://rgagnon.com/javadetails/java-0596.html
     */
    private static String encodeBytesToHex(byte[] bytes) {
        if (bytes == null)
            return null;
        final StringBuilder hex = new StringBuilder(2 * bytes.length);
        for (final byte b : bytes) {
            hex.append(IDENTIFIER_DIGITS.charAt((b & 0xf0) >> 4))
                .append(IDENTIFIER_DIGITS.charAt((b & 0x0f)));
        }
        return hex.toString();
    }

    public static byte[] toHex(byte[] bytes) throws GentleException {
        try {
            return encodeBytesToHex(bytes).getBytes("UTF-8");
        }
        catch (UnsupportedEncodingException e) {
            throw new GentleException("implementation error", e);
        }
    }

    private static Random rng = new SecureRandom();

    public static byte[] random() throws GentleException {
        byte[] binaryResult = new byte[IDENTIFIER_LENGTH / 2];
        rng.nextBytes(binaryResult);
        return binaryResult;
    }

    public static byte[] randomId() throws GentleException {
        return toHex(random());
    }

    public static byte[] sha256(byte[] bytes) throws GentleException {
        MessageDigest digest = null;
        try {
            digest = MessageDigest.getInstance("SHA-256");
        }
        catch (NoSuchAlgorithmException e) {
            throw new GentleException("Could not compute SHA-256 digest", e);
        }
        digest.reset();
        byte[] result = null;
        result = digest.digest(bytes);
        return result;
    }

    public static byte[] sha256Id(byte[] bytes) throws GentleException {
        return toHex(sha256(bytes));
    }

    public static boolean isIdentifierFormatValid(byte[] identifier) {
        if (identifier.length != IDENTIFIER_LENGTH)
            return false;
        for (final byte b : identifier) {
            if (IDENTIFIER_DIGITS.indexOf(b) == -1)
                return false;
        }
        return true;
    }

    public static void validateIdentifierFormat(byte[] identifier) throws InvalidIdentifierException {
        if (!isIdentifierFormatValid(identifier)) {
            throw new InvalidIdentifierException(identifier.toString());
        }
    }

}
