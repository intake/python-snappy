#!/usr/bin/env python

import os
import random
import struct
from unittest import TestCase

import snappy.hadoop_snappy


class SnappyStreaming(TestCase):

    def test_random(self):
        for _ in range(100):
            compressor = snappy.hadoop_snappy.StreamCompressor()
            decompressor = snappy.hadoop_snappy.StreamDecompressor()
            data = b""
            compressed = b""
            for _ in range(random.randint(0, 3)):
                chunk = os.urandom(
                    random.randint(0, snappy.hadoop_snappy._CHUNK_MAX * 2)
                )
                data += chunk
                compressed += compressor.add_chunk(
                    chunk
                )

            upper_bound = random.choice(
                [256, snappy.hadoop_snappy._CHUNK_MAX * 2]
            )
            while compressed:
                size = random.randint(0, upper_bound)
                chunk, compressed = compressed[:size], compressed[size:]
                chunk = decompressor.decompress(chunk)
                self.assertEqual(data[:len(chunk)], chunk)
                data = data[len(chunk):]

            decompressor.flush()
            self.assertEqual(len(data), 0)

    def test_concatenation(self):
        data1 = os.urandom(snappy.hadoop_snappy._CHUNK_MAX * 2)
        data2 = os.urandom(4096)
        decompressor = snappy.hadoop_snappy.StreamDecompressor()
        self.assertEqual(
                decompressor.decompress(
                    snappy.hadoop_snappy.StreamCompressor().compress(data1) +
                    snappy.hadoop_snappy.StreamCompressor().compress(data2)),
                data1 + data2)


if __name__ == "__main__":
    import unittest
    unittest.main()
