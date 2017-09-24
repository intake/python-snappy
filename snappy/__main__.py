from .snappy import stream_compress, stream_decompress

def cmdline_main():
    """This method is what is run when invoking snappy via the commandline.
    Try python -m snappy --help
    """
    import sys
    if (len(sys.argv) < 2 or len(sys.argv) > 4 or "--help" in sys.argv or
            "-h" in sys.argv or sys.argv[1] not in ("-c", "-d")):
        print("Usage: python -m snappy <-c/-d> [src [dst]]")
        print("             -c      compress")
        print("             -d      decompress")
        print("output is stdout if dst is omitted or '-'")
        print("input is stdin if src and dst are omitted or src is '-'.")
        sys.exit(1)

    if len(sys.argv) >= 4 and sys.argv[3] != "-":
        dst = open(sys.argv[3], "wb")
    elif hasattr(sys.stdout, 'buffer'):
        dst = sys.stdout.buffer
    else:
        dst = sys.stdout

    if len(sys.argv) >= 3 and sys.argv[2] != "-":
        src = open(sys.argv[2], "rb")
    elif hasattr(sys.stdin, "buffer"):
        src = sys.stdin.buffer
    else:
        src = sys.stdin

    if sys.argv[1] == "-c":
        method = stream_compress
    else:
        method = stream_decompress

    method(src, dst)


if __name__ == "__main__":
    cmdline_main()
