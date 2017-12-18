import argparse
import io
import sys

from .snappy import stream_compress, stream_decompress
from .hadoop_snappy import (
    stream_compress as hadoop_stream_compress,
    stream_decompress as hadoop_stream_decompress)


FRAMING_FORMAT = 'framing'

HADOOP_FORMAT = 'hadoop_snappy'

DEFAULT_FORMAT = FRAMING_FORMAT

COMPRESS_METHODS = {
    FRAMING_FORMAT: stream_compress,
    HADOOP_FORMAT: hadoop_stream_compress,
}

DECOMPRESS_METHODS = {
    FRAMING_FORMAT: stream_decompress,
    HADOOP_FORMAT: hadoop_stream_decompress,
}


def cmdline_main():
    """This method is what is run when invoking snappy via the commandline.
    Try python -m snappy --help
    """
    stdin = sys.stdin
    if hasattr(sys.stdin, "buffer"):
        stdin = sys.stdin.buffer
    stdout = sys.stdout
    if hasattr(sys.stdout, "buffer"):
        stdout = sys.stdout.buffer

    parser = argparse.ArgumentParser(
        description="Compress or decompress snappy archive"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-c',
        dest='compress',
        action='store_true',
        help='Compress'
    )
    group.add_argument(
        '-d',
        dest='decompress',
        action='store_true',
        help='Decompress'
    )

    parser.add_argument(
        '-t',
        dest='target_format',
        default=DEFAULT_FORMAT,
        choices=[FRAMING_FORMAT, HADOOP_FORMAT],
        help='Target format, default is {}'.format(DEFAULT_FORMAT)
    )

    parser.add_argument(
        'infile',
        nargs='?',
        type=argparse.FileType(mode='rb'),
        default=stdin,
        help="Input file (or stdin)"
    )
    parser.add_argument(
        'outfile',
        nargs='?',
        type=argparse.FileType(mode='wb'),
        default=stdout,
        help="Output file (or stdout)"
    )

    args = parser.parse_args()
    if args.compress:
        method = COMPRESS_METHODS[args.target_format]
    else:
        method = DECOMPRESS_METHODS[args.target_format]

    # workaround for https://bugs.python.org/issue14156
    if isinstance(args.infile, io.TextIOWrapper):
        args.infile = stdin
    if isinstance(args.outfile, io.TextIOWrapper):
        args.outfile = stdout

    method(args.infile, args.outfile)


if __name__ == "__main__":
    cmdline_main()
