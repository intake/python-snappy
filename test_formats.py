import io
import os
from unittest import TestCase
import subprocess
import sys
import tempfile
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

class TestAutoDecompress(TestCase):
    data = bytes(range(256))

    def compressed(self, name):
        stream = io.BytesIO()
        formats.get_compress_function(name)(io.BytesIO(self.data), stream)
        stream.seek(0)
        return stream

    def test_seekable_formats(self):
        for name in ("hadoop", "raw"):
            with self.subTest(format=name):
                compressed = self.compressed(name)
                decompress = formats.get_decompress_function("auto", compressed)
                output = io.BytesIO()
                decompress(compressed, output)
                self.assertEqual(output.getvalue(), self.data)

    def test_cli_seekable_formats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "input.snappy")
            target = os.path.join(tmpdir, "output.bin")
            for name in ("hadoop", "raw"):
                with self.subTest(format=name):
                    with open(source, "wb") as stream:
                        stream.write(self.compressed(name).getvalue())
                    result = subprocess.run(
                        [sys.executable, "-m", "snappy", "-d", source, target],
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    with open(target, "rb") as stream:
                        self.assertEqual(stream.read(), self.data)

    def test_cli_framed_stdin(self):
        result = subprocess.run(
            [sys.executable, "-m", "snappy", "-d"],
            input=self.compressed("framing").getvalue(),
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.data)


class TestDecompressFunction(TestCase):
    def test_auto_returns_function(self):
        data = b"hello world"

        compressed = io.BytesIO()
        formats.get_compress_function("auto")(
            io.BytesIO(data),
            compressed
        )
        compressed.seek(0)

        decompress_func = formats.get_decompress_function(
            "auto",
            compressed
        )

        decompressed = io.BytesIO()
        decompress_func(compressed, decompressed)

        self.assertEqual(data, decompressed.getvalue())

    def test_cli_decompress(self):
        data = b"hello world"

        with tempfile.TemporaryDirectory() as tmpdir:
            compressed = os.path.join(tmpdir, "input.snappy")
            output = os.path.join(tmpdir, "output.txt")

            with open(compressed, "wb") as f:
                formats.get_compress_function("auto")(
                    io.BytesIO(data),
                    f
                )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "snappy",
                    "-d",
                    compressed,
                    output,
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)

            with open(output, "rb") as f:
                self.assertEqual(data, f.read())


if __name__ == "__main__":
    import unittest
    unittest.main()
