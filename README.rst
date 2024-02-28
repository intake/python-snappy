python-snappy
=============

Python library for the snappy compression library from Google.
This library is distributed under the New BSD License
(http://www.opensource.org/licenses/bsd-license.php).

Dependencies
============

* cramjam

* Supports Python >=3.8

Install
=======

Install it from PyPi:

::

  pip install python-snappy

Run tests
=========

::

  # run python snappy tests
  nosetest test_snappy.py

  # support for cffi backend
  nosetest test_snappy_cffi.py

Benchmarks
==========

See ``cramjam`` for speed tests.

Commandline usage
=================

You can invoke Python Snappy to compress or decompress files or streams from
the commandline after installation as follows

Compressing and decompressing a file:

::

  $ python -m snappy -c uncompressed_file compressed_file.snappy
  $ python -m snappy -d compressed_file.snappy uncompressed_file

Compressing and decompressing a stream:

::

  $ cat uncompressed_data | python -m snappy -c > compressed_data.snappy
  $ cat compressed_data.snappy | python -m snappy -d > uncompressed_data

You can get help by running

::

  $ python -m snappy --help


Snappy - compression library from Google (c)
 http://google.github.io/snappy