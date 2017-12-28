import io
import os
from unittest import TestCase

from snappy import snappy_formats as formats
from snappy.snappy import _CHUNK_MAX, UncompressError


class TestFormatBase(TestCase):
    compress_format = formats.FORMAT_AUTO
    decompress_format = formats.FORMAT_AUTO
    success = True

    def runTest(self):
        data = os.urandom(1024 * 256 * 2) + os.urandom(13245 * 2)
        compress_func = formats.get_compress_function(self.compress_format)
        instream = io.BytesIO(data)
        compressed_stream = io.BytesIO()
        compress_func(instream, compressed_stream)
        compressed_stream.seek(0)
        if not self.success:
            with self.assertRaises(UncompressError) as err:
                decompress_func, read_chunk = formats.get_decompress_function(
                    self.decompress_format, compressed_stream
                )
                decompressed_stream = io.BytesIO()
                decompress_func(
                    compressed_stream,
                    decompressed_stream,
                    start_chunk=read_chunk
                )
            return
        decompress_func, read_chunk = formats.get_decompress_function(
            self.decompress_format, compressed_stream
        )
        decompressed_stream = io.BytesIO()
        decompress_func(
            compressed_stream,
            decompressed_stream,
            start_chunk=read_chunk
        )
        decompressed_stream.seek(0)
        self.assertEqual(data, decompressed_stream.read())


class TestFormatFramingFraming(TestFormatBase):
    compress_format = formats.FRAMING_FORMAT
    decompress_format = formats.FRAMING_FORMAT
    success = True


class TestFormatFramingHadoop(TestFormatBase):
    compress_format = formats.FRAMING_FORMAT
    decompress_format = formats.HADOOP_FORMAT
    success = False


class TestFormatFramingAuto(TestFormatBase):
    compress_format = formats.FRAMING_FORMAT
    decompress_format = formats.FORMAT_AUTO
    success = True


class TestFormatHadoopHadoop(TestFormatBase):
    compress_format = formats.HADOOP_FORMAT
    decompress_format = formats.HADOOP_FORMAT
    success = True


class TestFormatHadoopFraming(TestFormatBase):
    compress_format = formats.HADOOP_FORMAT
    decompress_format = formats.FRAMING_FORMAT
    success = False


class TestFormatHadoopAuto(TestFormatBase):
    compress_format = formats.HADOOP_FORMAT
    decompress_format = formats.FORMAT_AUTO
    success = True


class TestFormatAutoFraming(TestFormatBase):
    compress_format = formats.FORMAT_AUTO
    decompress_format = formats.FRAMING_FORMAT
    success = True


class TestFormatAutoHadoop(TestFormatBase):
    compress_format = formats.FORMAT_AUTO
    decompress_format = formats.HADOOP_FORMAT
    success = False


if __name__ == "__main__":
    import unittest
    unittest.main()
