#!/usr/bin/env python
#
# Copyright (c) 2011, Andres Moreira <andres@andresmoreira.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the authors nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import platform
import sys
import random
import snappy
import struct
from unittest import TestCase


class SnappyModuleTest(TestCase):
    def test_version(self):
        assert tuple(map(int, snappy.__version__.split("."))) >= (0, 6, 1)
        # Make sure that __version__ is identical to the version defined in setup.py
        with open(os.path.join(os.path.dirname(__file__), "setup.py")) as f:
            version_line, = (l for l in f.read().splitlines() if l.startswith("version"))
        assert version_line.split("=")[1].strip(" '\"") == snappy.__version__


class SnappyCompressionTest(TestCase):
    def test_simple_compress(self):
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.uncompress(compressed))

    def test_moredata_compress(self):
        text = "snappy +" * 1000 + " " + "by " * 1000 + " google"
        text = text.encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.uncompress(compressed))

    def test_randombytes_compress(self):
        _bytes = repr(os.urandom(1000)).encode('utf-8')
        compressed = snappy.compress(_bytes)
        self.assertEqual(_bytes, snappy.uncompress(compressed))

    def test_randombytes2_compress(self):
        _bytes = bytes(os.urandom(10000))
        compressed = snappy.compress(_bytes)
        self.assertEqual(_bytes, snappy.uncompress(compressed))

    def test_uncompress_error(self):
        self.assertRaises(snappy.UncompressError, snappy.uncompress,
                          "hoa".encode('utf-8'))

    if sys.version_info[0] == 2:
        def test_unicode_compress(self):
            text = "hello unicode world!".decode('utf-8')
            compressed = snappy.compress(text)
            self.assertEqual(text, snappy.uncompress(compressed))

    def test_decompress(self):
        # decompress == uncompress, just to support compatibility with zlib
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.decompress(compressed))

    def test_big_string(self):
        text = ('a'*10000000).encode('utf-8')
        compressed = snappy.compress(text)
        self.assertEqual(text, snappy.decompress(compressed))

    if platform.python_implementation() == 'CPython':
        def test_compress_memoryview(self):
            data = b"hello world!"
            expected = snappy.compress(data)
            actual = snappy.compress(memoryview(data))
            self.assertEqual(actual, expected)

        def test_decompress_memoryview(self):
            data = b"hello world!"
            compressed = snappy.compress(data)
            expected = snappy.uncompress(compressed)
            actual = snappy.uncompress(memoryview(compressed))
            self.assertEqual(actual, expected)


class SnappyValidBufferTest(TestCase):

    def test_valid_compressed_buffer(self):
        text = "hello world!".encode('utf-8')
        compressed = snappy.compress(text)
        uncompressed = snappy.uncompress(compressed)
        self.assertEqual(text == uncompressed,
                         snappy.isValidCompressed(compressed))

    def test_invalid_compressed_buffer(self):
        self.assertFalse(snappy.isValidCompressed(
                "not compressed".encode('utf-8')))


class SnappyStreaming(TestCase):

    def test_random(self):
        for _ in range(100):
            compressor = snappy.StreamCompressor()
            decompressor = snappy.StreamDecompressor()
            data = b""
            compressed = b""
            for _ in range(random.randint(0, 3)):
                chunk = os.urandom(random.randint(0, snappy.snappy._CHUNK_MAX * 2))
                data += chunk
                compressed += compressor.add_chunk(
                        chunk, compress=random.choice([True, False, None]))

            upper_bound = random.choice([256, snappy.snappy._CHUNK_MAX * 2])
            while compressed:
                size = random.randint(0, upper_bound)
                chunk, compressed = compressed[:size], compressed[size:]
                chunk = decompressor.decompress(chunk)
                self.assertEqual(data[:len(chunk)], chunk)
                data = data[len(chunk):]

            decompressor.flush()
            self.assertEqual(len(data), 0)

    def test_concatenation(self):
        data1 = os.urandom(snappy.snappy._CHUNK_MAX * 2)
        data2 = os.urandom(4096)
        decompressor = snappy.StreamDecompressor()
        self.assertEqual(
                decompressor.decompress(
                    snappy.StreamCompressor().compress(data1) +
                    snappy.StreamCompressor().compress(data2)),
                data1 + data2)


if __name__ == "__main__":
    import unittest
    unittest.main()
