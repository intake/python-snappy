import sys

py3k = False
if sys.hexversion > 0x02070000:
    unicode = str
    py3k = True

def test_snappy_cffi_enum():
    from snappy.snappy_cffi import lib

    assert 0 == lib.SNAPPY_OK
    assert 1 == lib.SNAPPY_INVALID_INPUT
    assert 2 == lib.SNAPPY_BUFFER_TOO_SMALL

def test_snappy_all_cffi():
    from snappy.snappy_cffi import ffi, lib

    import os
    data = 'string to be compressed'

    _input_data = ffi.new('char[]', data.encode('utf-8'))
    _input_size =  ffi.cast('size_t', len(_input_data))

    max_compressed = lib.snappy_max_compressed_length(_input_size)

    _out_data = ffi.new('char[]', max_compressed)
    _out_size = ffi.new('size_t*', max_compressed)

    rc = lib.snappy_compress(_input_data, _input_size, _out_data, _out_size)

    assert lib.SNAPPY_OK == rc

    rc = lib.snappy_validate_compressed_buffer(_out_data, _out_size[0])

    assert lib.SNAPPY_OK == rc

    result = ffi.new('size_t*', 0)
    rc = lib.snappy_uncompressed_length(_out_data,
                                      _out_size[0],
                                      result)

    assert lib.SNAPPY_OK == rc

    _uncompressed_data = ffi.new('char[]', result[0])

    rc = lib.snappy_uncompress(_out_data, _out_size[0], _uncompressed_data, result)

    assert lib.SNAPPY_OK == rc

    result = ffi.string(_uncompressed_data, result[0])
    if py3k:
        result = result.decode('utf-8')

    assert data == result
