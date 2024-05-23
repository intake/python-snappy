"""Consts and function to handle target format.
ALL_SUPPORTED_FORMATS - list of supported formats
get_decompress_function - returns stream decompress function for a current
    format (specified or autodetected)
get_compress_function - returns compress function for a current format
    (specified or default)
"""
from __future__ import absolute_import

from .snappy import (
    HadoopStreamDecompressor, StreamDecompressor,
    hadoop_stream_compress, hadoop_stream_decompress, raw_stream_compress,
    raw_stream_decompress, stream_compress, stream_decompress,
    UncompressError
)


# Means format auto detection.
# For compression will be used framing format.
# In case of decompression will try to detect a format from the input stream
# header.
DEFAULT_FORMAT = "auto"

ALL_SUPPORTED_FORMATS = ["framing", "auto"]

_COMPRESS_METHODS = {
    "framing": stream_compress,
    "hadoop": hadoop_stream_compress,
    "raw": raw_stream_compress
}

_DECOMPRESS_METHODS = {
    "framing": stream_decompress,
    "hadoop": hadoop_stream_decompress,
    "raw": raw_stream_decompress
}

# We will use framing format as the default to compression.
# And for decompression, if it's not defined explicitly, we will try to
# guess the format from the file header.
_DEFAULT_COMPRESS_FORMAT = "framing"


def uvarint(fin):
    """Read uint64 nbumber from varint encoding in a stream"""
    result = 0
    shift = 0
    while True:
        byte = fin.read(1)[0]
        result |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result


def check_unframed_format(fin, reset=False):
    """Can this be read using the raw codec

    This function wil return True for all snappy raw streams, but
    True does not mean that we can necessarily decode the stream.
    """
    if reset:
        fin.seek(0)
    try:
        size = uvarint(fin)
        assert size < 2**32 - 1
        next_byte = fin.read(1)[0]
        end = fin.seek(0, 2)
        assert size < end
        assert next_byte & 0b11 == 0 # must start with literal block
        return True
    except:
        return False


# The tuple contains an ordered sequence of a format checking function and
# a format-specific decompression function.
# Framing format has it's header, that may be recognized.
_DECOMPRESS_FORMAT_FUNCS = {
    "framed": stream_decompress,
    "hadoop": hadoop_stream_decompress,
    "raw": raw_stream_decompress
}


def guess_format_by_header(fin):
    """Tries to guess a compression format for the given input file by it's
    header.

    :return: format name (str), stream decompress function (callable)
    """
    if StreamDecompressor.check_format(fin):
        form = "framed"
    elif HadoopStreamDecompressor.check_format(fin):
        form = "hadoop"
    elif check_unframed_format(fin, reset=True):
        form = "raw"
    else:
        raise UncompressError("Can't detect format")
    return form, _DECOMPRESS_FORMAT_FUNCS[form]


def get_decompress_function(specified_format, fin):
    if specified_format == "auto":
        format, decompress_func = guess_format_by_header(fin)
        return decompress_func
    return _DECOMPRESS_METHODS[specified_format]


def get_compress_function(specified_format):
    if specified_format == "auto":
        return _COMPRESS_METHODS[_DEFAULT_COMPRESS_FORMAT]
    return _COMPRESS_METHODS[specified_format]
