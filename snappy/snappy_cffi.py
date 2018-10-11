from __future__ import absolute_import

from ._snappy_cffi import ffi, lib

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3


class UncompressError(Exception):
    pass


class SnappyBufferSmallError(Exception):
    pass


def prepare(data):
    _out_data = None
    _out_size = None

    _out_data = ffi.from_buffer(data)
    _out_size = ffi.cast('size_t', len(data))

    return (_out_data, _out_size)


def compress(data):
    if isinstance(data, unicode):
        data = data.encode('utf-8')

    _input_data, _input_size = prepare(data)

    max_compressed = lib.snappy_max_compressed_length(_input_size)

    _out_data = ffi.new('char[]', max_compressed)
    _out_size = ffi.new('size_t*', max_compressed)

    rc = lib.snappy_compress(_input_data, _input_size, _out_data, _out_size)

    if rc != lib.SNAPPY_OK:
        raise SnappyBufferSmallError()

    value = ffi.buffer(ffi.cast('char*', _out_data), _out_size[0])

    return value[:]


def uncompress(data):
    _out_data, _out_size = prepare(data)

    result = ffi.new('size_t*', 0)

    rc = lib.snappy_validate_compressed_buffer(_out_data, _out_size)

    if not rc == lib.SNAPPY_OK:
        raise UncompressError()

    rc = lib.snappy_uncompressed_length(_out_data,
                                      _out_size,
                                      result)

    if not rc == lib.SNAPPY_OK:
        raise UncompressError()

    _uncompressed_data = ffi.new('char[]', result[0])

    rc = lib.snappy_uncompress(_out_data, _out_size, _uncompressed_data, result)

    if rc != lib.SNAPPY_OK:
        raise UncompressError()

    buf =  ffi.buffer(ffi.cast('char*', _uncompressed_data), result[0])

    return buf[:]


def isValidCompressed(data):
    if isinstance(data, unicode):
        data = data.encode('utf-8')

    _out_data, _out_size= prepare(data)

    rc = lib.snappy_validate_compressed_buffer(_out_data, _out_size)

    return rc == lib.SNAPPY_OK

decompress = uncompress

def _crc32c(data):
    c_data = ffi.from_buffer(data)
    size = ffi.cast('int', len(data))
    return int(lib._crc32c(c_data, size))
