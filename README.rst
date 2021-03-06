.. image:: https://travis-ci.org/roskakori/vcdb.svg?branch=master
    :target: https://travis-ci.org/roskakori/vcdb
    :alt: Build Status

.. image:: https://coveralls.io/repos/roskakori/vcdb/badge.png?branch=master
    :target: https://coveralls.io/r/roskakori/vcdb?branch=master
    :alt: Test coverage

.. image:: https://landscape.io/github/roskakori/vcdb/master/landscape.svg
    :target: https://landscape.io/github/roskakori/vcdb/master
    :alt: Code Health


vcdb
====

Vcdb scans a version control repository and builds an SQL database that can
be queried. This simplifies monitoring version control activity and obtaining
numbers from it.


Installation
------------

Vcdb is available from https://pypi.python.org/pypi/vcdb and can be installed
running::

$ pip install vcdb

The minimum supported Python version is 3.4.

The Subversion command line client ``svn`` must be installed and located in
the command search path (``$PATH`` resp. ``%PATH%``).


Usage
-----

To build a database for vcdb's own repository run::

$ vcdb https://github.com/roskakori/vcdb/trunk sqlite:////tmp/vcdb.db

Currently vcdb only supports Subversion. Because Github provides a Subversion
interface for git repositories you can still analyze them using a call like
the one above.

You can then query the database using e.g. the sqlite command line client, for
example::

$ sqlite3 /tmp/vcdb.db "select count(1) from changes"

The data model is a work in progress, so their is no documentation yet. To
see the SQL code used to create all available tables, columns and their
relations, run::

$ sqlite3 /tmp/vcdb.db ".schema"

To see all available command line options, run::

$ vcdb --help

To see the current version number, run::

$ vcdb --version


License
-------

Copyright (C) 2016 Thomas Aglassinger. Distributed under the GNU Lesser
General Public License v3 or later (LGPLv3+).


History
-------

v0.1, 2016-07-01

* Initial public release.