#!/usr/bin/env python
#
# Copyright (c) 2011, Andres Moreira <andres@andresmoreira.com>
#               2011, Felipe Cruz <felipecruz@loogica.net>
#               2012, JT Olds <jt@spacemonkey.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the authors nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""python-snappy

Python library for the snappy compression library from Google.
Expected usage like:

    import snappy

    compressed = snappy.compress("some data")
    assert "some data" == snappy.uncompress(compressed)

"""
from __future__ import absolute_import

import struct

import cramjam

_CHUNK_MAX = 65536
_STREAM_TO_STREAM_BLOCK_SIZE = _CHUNK_MAX
_STREAM_IDENTIFIER = b"sNaPpY"
_IDENTIFIER_CHUNK = 0xff
_STREAM_HEADER_BLOCK = b"\xff\x06\x00\x00sNaPpY"

_compress = cramjam.snappy.compress_raw
_uncompress = cramjam.snappy.decompress_raw


class UncompressError(Exception):
    pass


def isValidCompressed(data):
    if isinstance(data, str):
        data = data.encode('utf-8')

    ok = True
    try:
        decompress(data)
    except UncompressError as err:
        ok = False
    return ok


def compress(data, encoding='utf-8'):
    if isinstance(data, str):
        data = data.encode(encoding)

    return bytes(_compress(data))

def uncompress(data, decoding=None):
    if isinstance(data, str):
        raise UncompressError("It's only possible to uncompress bytes")
    try:
        out = bytes(_uncompress(data))
    except cramjam.DecompressionError as err:
        raise UncompressError from err
    if decoding:
        return out.decode(decoding)
    return out


decompress = uncompress

class StreamCompressor():

    """This class implements the compressor-side of the proposed Snappy framing
    format, found at

        http://code.google.com/p/snappy/source/browse/trunk/framing_format.txt
            ?spec=svn68&r=71

    This class matches the interface found for the zlib module's compression
    objects (see zlib.compressobj), but also provides some additions, such as
    the snappy framing format's ability to intersperse uncompressed data.

    Keep in mind that this compressor object does no buffering for you to
    appropriately size chunks. Every call to StreamCompressor.compress results
    in a unique call to the underlying snappy compression method.
    """

    def __init__(self):
        self.c = cramjam.snappy.Compressor()

    def add_chunk(self, data: bytes, compress=None):
        """Add a chunk, returning a string that is framed and compressed. 
        
        Outputs a single snappy chunk; if it is the very start of the stream,
        will also contain the stream header chunk.
        """
        self.c.compress(data)
        return self.flush()

    compress = add_chunk

    def flush(self):
        return bytes(self.c.flush())

    def copy(self):
        """This method exists for compatibility with the zlib compressobj.
        """
        return self


class StreamDecompressor():

    """This class implements the decompressor-side of the proposed Snappy
    framing format, found at

        http://code.google.com/p/snappy/source/browse/trunk/framing_format.txt
            ?spec=svn68&r=71

    This class matches a subset of the interface found for the zlib module's
    decompression objects (see zlib.decompressobj). Specifically, it currently
    implements the decompress method without the max_length option, the flush
    method without the length option, and the copy method.
    """
    def __init__(self):
        self.c = cramjam.snappy.Decompressor()
        self.remains = None
    
    @staticmethod
    def check_format(fin):
        """Does this stream start with a stream header block?

        True indicates that the stream can likely be decoded using this class.
        """
        try:
            return fin.read(len(_STREAM_HEADER_BLOCK)) == _STREAM_HEADER_BLOCK
        except:
            return False

    def decompress(self, data: bytes):
        """Decompress 'data', returning a string containing the uncompressed
        data corresponding to at least part of the data in string. This data
        should be concatenated to the output produced by any preceding calls to
        the decompress() method. Some of the input data may be preserved in
        internal buffers for later processing.
        """
        if self.remains:
            data = self.remains + data
            self.remains = None
        if not data.startswith(_STREAM_HEADER_BLOCK):
            data = _STREAM_HEADER_BLOCK + data
        ldata = len(data)
        bsize = len(_STREAM_HEADER_BLOCK)
        if bsize + 4 > ldata:
            # not even enough for one block
            self.remains = data
            return b""
        while True:
            this_size = int.from_bytes(data[bsize + 1: bsize + 4], "little") + 4
            if bsize == ldata:
                # ended on a block boundary
                break
            if this_size + bsize > ldata:
                # last block incomplete
                self.remains = data[bsize:]
                data = data[:bsize]
                break
            bsize += this_size
        self.c.decompress(data)
        return self.flush()

    def flush(self):
        return bytes(self.c.flush())

    def copy(self):
        return self


class HadoopStreamCompressor():
    def add_chunk(self, data: bytes, compress=None):
        """Add a chunk, returning a string that is framed and compressed. 
        
        Outputs a single snappy chunk; if it is the very start of the stream,
        will also contain the stream header chunk.
        """
        cdata = _compress(data)
        return b"".join((len(data).to_bytes(4, "big"), len(cdata).to_bytes(4, "big"), cdata))

    compress = add_chunk

    def flush(self):
        # never maintains a buffer
        return b""

    def copy(self):
        """This method exists for compatibility with the zlib compressobj.
        """
        return self


class HadoopStreamDecompressor():
    def __init__(self):
        self.remains = b""
    
    @staticmethod
    def check_format(fin):
        """Does this look like a hadoop snappy stream?
        """
        try:
            from snappy.snappy_formats import check_unframed_format
            size = fin.seek(0, 2)
            fin.seek(0)
            assert size >= 8

            chunk_length = int.from_bytes(fin.read(4), "big")
            assert chunk_length < size
            fin.read(4)
            return check_unframed_format(fin)
        except:
            return False

    def decompress(self, data: bytes):
        """Decompress 'data', returning a string containing the uncompressed
        data corresponding to at least part of the data in string. This data
        should be concatenated to the output produced by any preceding calls to
        the decompress() method. Some of the input data may be preserved in
        internal buffers for later processing.
        """
        if self.remains:
            data = self.remains + data
            self.remains = None
        if len(data) < 8:
            self.remains = data
            return b""
        out = []
        while True:
            chunk_length = int.from_bytes(data[4:8], "big")
            if len(data) < 8 + chunk_length:
                self.remains = data
                break
            out.append(_uncompress(data[8:8 + chunk_length]))
            data = data[8 + chunk_length:]
        return b"".join(out)

    def flush(self):
        return b""

    def copy(self):
        return self
        


def stream_compress(src,
                    dst,
                    blocksize=_STREAM_TO_STREAM_BLOCK_SIZE,
                    compressor_cls=StreamCompressor):
    """Takes an incoming file-like object and an outgoing file-like object,
    reads data from src, compresses it, and writes it to dst. 'src' should
    support the read method, and 'dst' should support the write method.

    The default blocksize is good for almost every scenario.
    """
    compressor = compressor_cls()
    while True:
        buf = src.read(blocksize)
        if not buf: break
        buf = compressor.add_chunk(buf)
        if buf: dst.write(buf)


def stream_decompress(src,
                      dst,
                      blocksize=_STREAM_TO_STREAM_BLOCK_SIZE,
                      decompressor_cls=StreamDecompressor,
                      start_chunk=None):
    """Takes an incoming file-like object and an outgoing file-like object,
    reads data from src, decompresses it, and writes it to dst. 'src' should
    support the read method, and 'dst' should support the write method.

    The default blocksize is good for almost every scenario.
    :param decompressor_cls: class that implements `decompress` method like
        StreamDecompressor in the module
    :param start_chunk: start block of data that have already been read from
        the input stream (to detect the format, for example)
    """
    decompressor = decompressor_cls()
    while True:
        if start_chunk:
            buf = start_chunk
            start_chunk = None
        else:
            buf = src.read(blocksize)
            if not buf: break
        buf = decompressor.decompress(buf)
        if buf: dst.write(buf)
    decompressor.flush()  # makes sure the stream ended well


def hadoop_stream_decompress(
    src,
    dst,
    blocksize=_STREAM_TO_STREAM_BLOCK_SIZE,
):
    c = HadoopStreamDecompressor()
    while True:
        data = src.read(blocksize)
        if not data:
            break
        buf = c.decompress(data)
        if buf:
            dst.write(buf)
    dst.flush()


def hadoop_stream_compress(
    src,
    dst,
    blocksize=_STREAM_TO_STREAM_BLOCK_SIZE,
):
    c = HadoopStreamCompressor()
    while True:
        data = src.read(blocksize)
        if not data:
            break
        buf = c.compress(data)
        if buf:
            dst.write(buf)
    dst.flush()


def raw_stream_decompress(src, dst):
    data = src.read()
    dst.write(decompress(data))


def raw_stream_compress(src, dst):
    data = src.read()
    dst.write(compress(data))
