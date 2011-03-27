# python bindings for the snappy compression library from Google (c)
# Copyright (C) 2011  Andres Moreira
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup, Extension

snappymodule = Extension('snappy', 
                         include_dirs = ['/usr/local/include'],
                         libraries = ['snappy'],
                         library_dirs = ['/usr/local/lib', '/usr/lib'],
                         language='c++',
                         sources=['snappymodule.cc'])

setup(
    name='Snappy',
    version='0.1',
    description='Python bindings for the snappy google library ('
                'http://code.google.com/p/snappy)',
    author='Andres Moreira',
    author_email='andres@andresmoreira.com',
    url='http://github.com/andrix/python-snappy',
    license="GPL",
    ext_modules = [snappymodule]
)

