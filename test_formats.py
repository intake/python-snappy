import io
import os
import subprocess
import sys
import tempfile
from unittest import TestCase

from snappy import snappy_formats as formats


class TestFormatBase(TestCase):
    compress_format = "auto"
    decompress_format = "auto"
    success = True

    def runTest(self):
        data = os.urandom(1024 * 256 * 2) + os.urandom(13245 * 2)
        compress_func = formats.get_compress_function(self.compress_format)
        instream = io.BytesIO(data)
        compressed_stream = io.BytesIO()
        compress_func(instream, compressed_stream)
        compressed_stream.seek(0)
        decompress_func = formats.get_decompress_function(
            self.decompress_format, compressed_stream
        )
        compressed_stream.seek(0)
        decompressed_stream = io.BytesIO()
        decompress_func(
            compressed_stream,
            decompressed_stream,
        )
        decompressed_stream.seek(0)
        self.assertEqual(data, decompressed_stream.read())


class TestFormatFramingFraming(TestFormatBase):
    compress_format = "framing"
    decompress_format = "framing"
    success = True


class TestFormatFramingAuto(TestFormatBase):
    compress_format = "framing"
    decompress_format = "auto"
    success = True


class TestFormatAutoFraming(TestFormatBase):
    compress_format = "auto"
    decompress_format = "framing"
    success = True


class TestFormatHadoop(TestFormatBase):
    compress_format = "hadoop"
    decompress_format = "hadoop"
    success = True


class TestFormatRaw(TestFormatBase):
    compress_format = "raw"
    decompress_format = "raw"
    success = True


class TestFormatHadoopAuto(TestFormatBase):
    compress_format = "hadoop"
    decompress_format = "auto"
    success = True


class TestFormatRawAuto(TestFormatBase):
    compress_format = "raw"
    decompress_format = "auto"
    success = True


class TestCommandLine(TestCase):
    def test_compress_decompress_roundtrip(self):
        data = os.urandom(1024 * 256 * 2) + os.urandom(13245 * 2)
        with tempfile.TemporaryDirectory() as tmp_dir:
            plain = os.path.join(tmp_dir, "plain")
            compressed = os.path.join(tmp_dir, "compressed.snappy")
            with open(plain, "wb") as f:
                f.write(data)
            subprocess.run(
                [sys.executable, "-m", "snappy", "-c", plain, compressed],
                check=True,
            )
            for target_format in formats.ALL_SUPPORTED_FORMATS:
                with self.subTest(target_format=target_format):
                    decompressed = os.path.join(tmp_dir, target_format)
                    subprocess.run(
                        [sys.executable, "-m", "snappy", "-d",
                         "-t", target_format, compressed, decompressed],
                        check=True,
                    )
                    with open(decompressed, "rb") as f:
                        self.assertEqual(data, f.read())


if __name__ == "__main__":
    import unittest
    unittest.main()
