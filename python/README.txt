Gentle Technology Preview DA92 (TP-DA92)
========================================

The explicit goal of Gentle is to FUNDAMENTALLY SIMPLIFY COMPUTER PROGRAMMING
AND USER INTERFACES.

This Technology Preview implements the fundamental operations needed to store
and retrieve data on a computer, using two simple, filesystem-based, dictionary
data structures.

One dictionary, called the content database, is a content-addressable store.
The value is the data content, and the key is the SHA-256 sum of that value.
The key-value entries in the content database are inherently immutable.

The second dictionary, called the pointer database, stores references to these
SHA-256 keys.  The value is the SHA-256 sum, and the key (usually) is a
generated 256-bit random number.  The values of pointer database entries are
mutable.

There is a third identifier namespace of a smiliar nature.  It actually does
not store any data, and the only meaningful method that operates on it is the
random number generator which is also used for the pointer database.
Identifiers in this namespace are not backed by data.  Rather, they can be used
to represent real objects, like buildings, people, computer equipment, and so
forth.  This very technology preview uses the identifier
    da92de4118f6fa915b6bdd73f090ad57dc153082600855e5c7a85e8fe054c5a1
in exactly this way (note the first four digits).  This identifier is unique and
long-lasting, more so than a project name or URL.


Scope of this technology preview
--------------------------------

This technology preview uses simple filesystem-based data structures for storing
data.  As soon as this backend proves insufficient, a new Gentle project (be it
a technology preview or something else) will be started.


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


Installation (optional)
-----------------------

You may want to copy or link the included Python modules somewhere on your
PYTHONPATH.


Dependencies
------------

* Python 2.6 or later (Python 3.x is not supported at the moment)


Command Line Tutorial: Setup
----------------------------

This tutorial assumes that you know and use Bash.

Change into the directory where those modules can be found:

    gentle_da92de4118f6fa91.py - Gentle Core Module
        This is the module which implements the very heart of Gentle.  This set
        of features is what distinguishes Gentle from all other systems out
        there.

    gentle_da92de4118f6fa91_next.py - Gentle Next Module
        You can think of this module as some kind of subclass of
        gentle_da92de4118f6fa91.  The Next Module extends the Core Module with
        features that are the next step, or the next level up, from the Core
        Module.

The modules have a convenient command-line interface if aliased:

    $ alias g='python -m gentle_da92de4118f6fa91_next'

(You can also use ". setenv.sh" to do that.)

Gentle (currently) simply uses a directory to store its two databases.  It is
very easy to find out where they are stored:

    $ g getdir
    /home/frog/.gentle_da92de4118f6fa91

The use of any Gentle programming interface (either from the shell or by
creating a Gentle instance in Python), even the 'getdir' command, causes the
data directory to be created if it does not already exist, silently and
automatically.

    $ ls -al /home/frog/.gentle_da92de4118f6fa91
    total 16
    drwx------  4 fr fr 4096 Jan  3 01:10 .
    drwxr-xr-x 55 fr fr 4096 Jan  4 23:19 ..
    drwx------  2 fr fr 4096 Jan  3 01:16 content_db
    drwx------  2 fr fr 4096 Jan  3 01:16 pointer_db


Command Line Tutorial: Content
------------------------------

Let's start using Gentle for real, by putting a "Hello World\n" into the
content database:

    $ echo "Hello World" | g put
    d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26
    $ g get d2a8
    Hello World

Content is identified by its SHA-256 hash value.  You will get the same result
if using sha256sum, and Gentle also makes the sha256 function public:

    $ echo "Hello World" | sha256sum
    d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26  -
    $ echo "Hello World" | g sha256
    d2a84f4b8b650937ec8f73cd8be2c74add5a911ba64df27458ed8229da804a26

As long as it is unique, the identifier can be abbreviated, like "d2a8" above.


Command Line Tutorial: Pointers
-------------------------------

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
can be done in a more straightforward way:

    $ g put $(g random) $(g put < content) > content.ptr

Saving the same data again, i.e. data with the same SHA-256 hash value, will do
no harm:

    $ echo "Another Hello World" | g put
    062043cad71efc24e5e0eeec1821621e9c5e7f1fff6ffefe63ce160e87f5d726

Content can also easily be removed:

    $ g rm d2a8 $PTR 0620

Please note that changing a pointer does *not* remove the content that it has
previously pointed to.  This is by design, as multiple pointers might refer to
the same content, and even some content might contain references to other
content.  There are several possible ways to clean up content that is no longer
needed, like: only keeping what is reachable by pointers; removal after some
expiration date; merging some of the contents with another database, then
removing the original one; and so forth.

To remove (or 'clear') the whole data directory of the tech preview:

    $ rm -rf "$(g getdir)"

The position of the tech preview data directory can be changed by setting the
environment variable 'GENTLE_DA92DE41_DIR':

    $ export GENTLE_DA92DE41_DIR=/tmp/some_gentle_experiment
    $ g getdir
    /tmp/some_gentle_experiment
    $ rm -rf "$(g getdir)"


Command Line Tutorial: The Next Module
--------------------------------------

(TODO)


Python Module Tutorial: The Core Module
---------------------------------------

All these commands are also conveniently available from within Python as
methods of the Gentle class:

    from gentle_da92de4118f6fa91 import Gentle
    g = Gentle()
    new_ptr = g.put(g.random(), g.put("This is some new content\n"))
    new_hash = g.get(new_ptr)
    print new_ptr, "->", new_hash


Ideas for future features
-------------------------

* Proper setup.py for installing the modules
* Public key encryption and signature
* Fine-grained web of trust
* Fine-grained software and data structure modularity and distribution
* Fine-grained commerce (Flattr? Bitcoin?)
* Facilities for merging (parts of) multiple repositories together
* A graphical user interface
* Smallest possible bootstrapping
    - Move most Python code into the Gentle data store
* Version control and global undo
* Indexed meta data (maybe employing map/reduce)
* Interfaces to legacy software:
    - virtual file system (FUSE)
    - mail server (SMTP + IMAP/POP3)
    - HTTP
* Programming language APIs for C, C#, Java, Javascript, Perl, PHP, Python 3
* Email
* Programming IDE
* The Web how it should have been
