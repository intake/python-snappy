import os
import sys
import platform
import shutil

from distutils import ccompiler
from distutils.sysconfig import customize_compiler
from distutils.errors import CompileError

from .utils import exec_process, tempdir


def test_compilation(basedir, cfile):
    """Test simple compilation with given settings"""
    cc = ccompiler.new_compiler()
    customize_compiler(cc)
    efile, ext = os.path.splitext(os.path.basename(cfile))
    cpreargs = lpreargs = None
    if sys.platform == 'darwin':
        # use appropriate arch for compiler
        if platform.architecture()[0] == '32bit':
            if platform.processor() == 'powerpc':
                cpu = 'ppc'
            else:
                cpu = 'i386'
            cpreargs = ['-arch', cpu]
            lpreargs = ['-arch', cpu, '-undefined', 'dynamic_lookup']
        else:
            # allow for missing UB arch, since it will still work:
            lpreargs = ['-undefined', 'dynamic_lookup']
    objs = cc.compile([cfile],
                      output_dir=basedir, extra_preargs=cpreargs)
    cc.link_executable(objs, efile,
                       output_dir=basedir, extra_preargs=lpreargs, target_lang="c++")
    return os.path.join(basedir, efile)


def detect_snappy():
    """Compile, link & execute a test program."""
    with tempdir() as basedir:
        try:
            efile = test_compilation(
                basedir, os.path.join('buildutils', 'vers.cpp'))
        except CompileError:
            return None
        stdout = exec_process(efile)
        version = int(stdout)
        major = (version & 0xff0000) >> 16
        minor = (version & 0x00ff00) >> 8
        patch = (version & 0x0000ff)
        return (major, minor, patch)
