from __future__ import absolute_import

from .snappy import (
    compress,
    decompress,
    uncompress,
    stream_compress,
    stream_decompress,
    StreamCompressor,
    StreamDecompressor,
    UncompressError,
    HadoopStreamCompressor,
    HadoopStreamDecompressor,
    isValidCompressed,
)

__version__ = '0.7.2'
