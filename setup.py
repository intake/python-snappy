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
    ext_modules = [snappymodule]
)

