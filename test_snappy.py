import os
import snappy
from unittest import TestCase

class SnappyTest(TestCase):

    def test_compress_uncompress(self):
        text = "hello world!"
        compressed = snappy.compress(text)
        self.assertEquals(text, snappy.uncompress(compressed))

        text = "snappy +" * 1000 + " " + "by " * 1000 + " google"
        compressed = snappy.compress(text)
        self.assertEquals(text, snappy.uncompress(compressed))

        _bytes = repr(os.urandom(1000))
        compressed = snappy.compress(_bytes)
        self.assertEquals(_bytes, snappy.uncompress(compressed))

    def test_uncompress_error(self):
        self.assertRaises(snappy.error, snappy.uncompress, "hoa")
