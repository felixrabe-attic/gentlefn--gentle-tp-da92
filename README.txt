Gentle Technology Preview (da92de4118f6fa91)
============================================

This Technology Preview implements the fundamental operations needed to store
and retrieve data on a computer, using two simple dictionary data structures.

One dictionary, called the content database, is a content-addressable store.
The value is the data content, and the key is the SHA1 sum of that value.  By
their nature, the key-value entries in the content database are immutable.

The second dictionary, called the pointer database, stores references to these
SHA1 keys.  The value is the SHA1 sum, and the key is a generated 128-bit
random number.  The value is mutable.

For the bootstrapping mechanism that surrounds the data store, generated random
64-bit numbers are used as the definitive keys, if for no other reason than to
help to stop thinking in terms of (more often than not) poorly-chosen
identifiers.  So the bootstrap process is actually twofold, with both a
technical as well as a philosophical component.


License: LGPL 2.1+
------------------

Copyright (C) 2010  Felix Rabe

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


Future features
---------------

* Smallest possible bootstrapping
    - Move most Python code into the Gentle data store
* Version control and global undo
* Indexed meta data (maybe employing map/reduce)
* Interfaces to legacy software:
    - virtual file system
    - mail server (SMTP + IMAP/POP3)
    - HTTP
    - command line
    - programming language APIs

