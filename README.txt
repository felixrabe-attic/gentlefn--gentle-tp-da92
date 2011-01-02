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


First steps
-----------

Put / install / link gentle_da92de4118f6fa91.py somewhere in your PYTHONPATH
(or do the following tutorial in the same directory as that Python module).

The module has a command-line interface which can be neatly aliased:

    $ alias g='python -m gentle_da92de4118f6fa91'

If you wonder where the following data ends up, you will find it in the
directory '~/.gentle_da92de4118f6fa91'.

You can put a Hello World into the content database:

    $ echo "Hello World" | g put
    d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26
    $ g get d2a8
    Hello World

Content is identified by its SHA-256 hash value.  As long as it is unique,
the identifier can be abbreviated.

To point to changing content, a pointer with a random-generated 256-bit
identifier can refer to a hash value:

    $ PTR=$(g random)
    $ echo $PTR
    de964224d0c4862024bf49462048d2d1a29738dbf3dfd3744e1832f6eff5e244
    $ g put $PTR d2a8
    de964224d0c4862024bf49462048d2d1a29738dbf3dfd3744e1832f6eff5e244
    $ g get $PTR
    d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26
    $ g get $(g get $PTR)
    Hello World
    $ echo "Another Hello World" | g put
    062043cad71efc24e5e0eeec1821621e9c5e7f1fff6ffefe63ce160e87f5d726
    $ g put $PTR 06204
    de964224d0c4862024bf49462048d2d1a29738dbf3dfd3744e1832f6eff5e244
    $ g get $PTR
    062043cad71efc24e5e0eeec1821621e9c5e7f1fff6ffefe63ce160e87f5d726
    $ g get $(g get $PTR)
    Another Hello World

As 'g put' with two arguments returns the pointer's key, creating a new pointer
for some content can be done in a more straightforward way:

    $ g put $(g random) $(g put < content) > content.ptr

Saving the same data (data with the same SHA-256 hash value) again will do no
harm:

    $ echo "Another Hello World" | g put
    062043cad71efc24e5e0eeec1821621e9c5e7f1fff6ffefe63ce160e87f5d726

Content can also easily be removed:

    $ for IDENTIFIER in d2a8 $PTR 0620 ; do g rm $IDENTIFIER ; done

All these commands are also readily available from within Python as methods of
the gentle object:

    from gentle_da92de4118f6fa91 import gentle as g
    new_ptr = g.random()
    new_hash = g.put("This is some new content\n")
    g.put(new_ptr, new_hash)
    print new_ptr, "->", new_hash


Copyright statement
-------------------

Copyright (C) 2010, 2011  Felix Rabe

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program.  If not, see <http://www.gnu.org/licenses/>.


The file lgpl-2.1.txt, included in the library's distribution, contains the
license text.


Dependencies
------------

* Python 2.6 or later (Python 3.x is not supported)


Ideas for future features
-------------------------

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

