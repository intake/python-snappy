import os
import snappy
from unittest import TestCase

class SnappyCompressionTest(TestCase):

    def test_simple_compress(self):
        text = "hello world!"
        compressed = snappy.compress(text)
        self.assertEquals(text, snappy.uncompress(compressed))

    def test_moredata_compress(self):
        text = "snappy +" * 1000 + " " + "by " * 1000 + " google"
        compressed = snappy.compress(text)
        self.assertEquals(text, snappy.uncompress(compressed))

    def test_randombytes_compress(self):
        _bytes = repr(os.urandom(1000))
        compressed = snappy.compress(_bytes)
        self.assertEquals(_bytes, snappy.uncompress(compressed))

    def test_randombytes2_compress(self):
        _bytes = str(os.urandom(10000))
        compressed = snappy.compress(_bytes)
        self.assertEquals(_bytes, snappy.uncompress(compressed))

    def test_uncompress_error(self):
        self.assertRaises(snappy.UncompressError, snappy.uncompress, "hoa")

    def test_unicode_compress(self):
        text = u"hello unicode world!"
        compressed = snappy.compress(text)
        self.assertEquals(text, snappy.uncompress(compressed))

class SnappyValidBufferTest(TestCase):

    def test_valid_compressed_buffer(self):
        text = "hello world!"
        compressed = snappy.compress(text)
        uncompressed = snappy.uncompress(compressed)
        self.assertEquals(text == uncompressed, snappy.isValidCompressed(compressed))

    def test_invalid_compressed_buffer(self):
        self.assertFalse(snappy.isValidCompressed("not compressed"))
