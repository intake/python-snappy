from cffi import FFI

ffi = FFI()

ffi.cdef('''
typedef enum {
  SNAPPY_OK = 0,
  SNAPPY_INVALID_INPUT = 1,
  SNAPPY_BUFFER_TOO_SMALL = 2
} snappy_status;

int snappy_compress(const char* input,
                    size_t input_length,
                    char* compressed,
                    size_t* compressed_length);

int snappy_uncompress(const char* compressed,
                      size_t compressed_length,
                      char* uncompressed,
                      size_t* uncompressed_length);

size_t snappy_max_compressed_length(size_t source_length);

int snappy_uncompressed_length(const char* compressed,
                               size_t compressed_length,
                               size_t* result);

int snappy_validate_compressed_buffer(const char* compressed,
                                      size_t compressed_length);


void* malloc(size_t size);
''')

C = ffi.verify('''
#include <stdlib.h>
#include <snappy-c.h>
''', libraries=["snappy"])


class UncompressError(Exception):
    pass

class SnappyBufferSmallError(Exception):
    pass

class DataWrapper(object):
    def __init__(self, void_p, size, unicode=False):
        self.void_p = void_p
        self.size = size
        self._unicode = unicode

    def __str__(self):
        import pytest; pytest.set_trace()
        return ffi.string(ffi.cast('char*', self.void_p), size)[:]

    def __eq__(self, other):
        import pytest; pytest.set_trace()
        return other.void_p == self.void_p

    def __len__(self):
        import pytest; pytest.set_trace()
        return self.size

def _check_data(data):
    _out_data = None
    _out_size = None
    unicode = False

    if isinstance(data, DataWrapper):
        _out_data = data.void_p
        _out_size = data.size
        unicode = data._unicode
    else:
        _out_data = ffi.new('char[]', data)
        _out_size = ffi.cast('size_t', len(_out_data))

    return (_out_data, _out_size, unicode)

def compress(data):
    uni = False
    if isinstance(data, unicode):
        data = data.encode('utf-8')
        uni = True

    _input_data = ffi.new('char[]', data)
    _input_size =  ffi.cast('size_t', len(data))

    max_compressed = C.snappy_max_compressed_length(_input_size)

    _out_data = ffi.new('char[]', max_compressed)
    _out_size = ffi.new('size_t*', max_compressed)

    rc = C.snappy_compress(_input_data, _input_size, _out_data, _out_size)

    if rc != C.SNAPPY_OK:
        raise SnappyBufferSmallError()

    value = DataWrapper(_out_data, _out_size[0], unicode=uni)

    return value

def uncompress(data):
    _out_data, _out_size, _unicode = _check_data(data)

    result = ffi.new('size_t*', 0)

    rc = C.snappy_validate_compressed_buffer(_out_data, _out_size)

    if not rc == C.SNAPPY_OK:
        raise UncompressError()

    rc = C.snappy_uncompressed_length(_out_data,
                                      _out_size,
                                      result)

    if not rc == C.SNAPPY_OK:
        raise UncompressError()

    _uncompressed_data = ffi.new('char[]', result[0])

    rc = C.snappy_uncompress(_out_data, _out_size, _uncompressed_data, result)

    if rc != C.SNAPPY_OK:
        raise UncompressError()

    buf =  ffi.buffer(ffi.cast('char*', _uncompressed_data), result[0])

    if _unicode:
        return buf[:].decode('utf-8')
    return buf[:]


def isValidCompressed(data):
    _out_data, _out_size, _ = _check_data(data)

    rc = C.snappy_validate_compressed_buffer(_out_data, _out_size)

    return rc == C.SNAPPY_OK

decompress = uncompress
