import sys

try:
    from _snappy import *
except ImportError:
    from snappy_cffi import *

_compress = compress
_uncompress = uncompress

py3k = False
if sys.hexversion > 0x03000000:
    unicode = str
    py3k = True

def compress(data, encoding='utf-8'):
    if isinstance(data, unicode):
        data = data.encode(encoding)

    return _compress(data)

def uncompress(data, decoding=None):
    if isinstance(data, unicode):
        raise UncompressError("It's only possible to uncompress bytes")
    if decoding:
        return _uncompress(data).decode(decoding)
    return _uncompress(data)

decompress = uncompress
