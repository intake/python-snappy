# Copyright (c) 2011, Andres Moreira <andres@andresmoreira.com>
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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import os

version = '0.6.0'
long_description = """
Python bindings for the snappy compression library from Google.

More details about Snappy library: http://google.github.io/snappy
"""

library_dirs, include_dirs = [], []
if os.environ.get("CIBUILDWHEEL", False) and sys.version_info[:2] == (3, 9) and sys.platform =="darwin":
    library_dirs = ["/usr/local/lib/"]
    include_dirs = ["/usr/local/include/"]
homebrew_prefix = os.environ.get("HOMEBREW_PREFIX")
if homebrew_prefix:
    library_dirs.append(os.path.join(homebrew_prefix, "lib"))
    include_dirs.append(os.path.join(homebrew_prefix, "include"))


snappymodule = Extension('snappy._snappy',
                         libraries=['snappy'],
                         sources=['src/snappy/snappymodule.cc', 'src/snappy/crc32c.c'],
                         library_dirs=library_dirs,
                         include_dirs=include_dirs)

ext_modules = [snappymodule]
packages = ['snappy']
install_requires = []
setup_requires = []
cffi_modules = []

if 'PyPy' in sys.version:
    from setuptools import setup
    ext_modules = []
    install_requires = ['cffi>=1.0.0']
    setup_requires = ['cffi>=1.0.0']
    cffi_modules = ['./src/snappy/snappy_cffi_builder.py:ffi']

setup(
    name='python-snappy',
    version=version,
    author='Andres Moreira',
    author_email='andres@andresmoreira.com',
    url='http://github.com/andrix/python-snappy',
    description='Python library for the snappy compression library from Google',
    long_description=long_description,
    keywords='snappy, compression, google',
    license='BSD',
    classifiers=['Development Status :: 4 - Beta',
                 'Topic :: Internet',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: System :: Archiving :: Compression',
                 'License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'Operating System :: MacOS :: MacOS X',
                 # 'Operating System :: Microsoft :: Windows', -- Not tested yet
                 'Operating System :: POSIX',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9'
                 ],
    ext_modules=ext_modules,
    packages=packages,
    install_requires=install_requires,
    setup_requires=setup_requires,
    cffi_modules=cffi_modules,
    package_dir={'': 'src'},
)
