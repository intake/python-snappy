import ast
import os
import platform
import subprocess
import sys
import tempfile

from distutils import log
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist
from distutils.errors import DistutilsError

from .utils import exec_process, makedirs, rmtree
from .detect import detect_snappy


def download_snappy(snappy_dir, snappy_version, snappy_url):
    log.info('Downloading snappy...')
    makedirs(snappy_dir)
    url = snappy_url.format(version=snappy_version)
    base_dir = tempfile.mkdtemp()
    release = 'snappy-{version}'.format(version=snappy_version)
    archive = '{release}.tar.gz'.format(release=release)
    archive_path = os.path.join(base_dir, archive)
    release_path = os.path.join(base_dir, release)
    try:
        exec_process(['wget', '-O', archive_path, url])
        exec_process(['tar', '-xzf', archive_path, '-C', base_dir])
        exec_process(['cp', '-RT', release_path, snappy_dir])
    finally:
        rmtree(base_dir)


class snappy_build_ext(build_ext):
    snappy_dir = os.path.join('deps', 'snappy')
    snappy_version = '1.1.1'
    snappy_url = 'https://snappy.googlecode.com/files/snappy-{version}.tar.gz'

    user_options = build_ext.user_options
    user_options.extend([
        ("snappy-clean-compile", None, "Clean snappy tree before compilation"),
        ("snappy-force-fetch", None, "Remove snappy (if present) and fetch it again"),
        ("snappy-verbose-build", None, "Print output of snappy build process")
    ])
    boolean_options = build_ext.boolean_options
    boolean_options.extend(["snappy-clean-compile", "snappy-force-fetch", "snappy-verbose-build"])

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.snappy_clean_compile = 0
        self.snappy_force_fetch = 0
        self.snappy_verbose_build = 0

    def build_extensions(self):
        self.force = self.snappy_force_fetch or self.snappy_clean_compile
        use_builtin_snappy = False
        if sys.platform != 'win32':
            version = detect_snappy()
            if version is None or version < (1, 0, 4):
                self.snappy_lib = os.path.join(self.snappy_dir, '.libs', 'libsnappy.a')
                self.get_snappy()
                # Set compiler options
                self.extensions[0].extra_objects.extend([self.snappy_lib])
                self.compiler.add_include_dir(self.snappy_dir)
                use_builtin_snappy = True
        if not use_builtin_snappy:
            self.extensions[0].libraries.append('snappy')
        build_ext.build_extensions(self)

    def get_snappy(self):
        def build_snappy():
            cppflags = '-fPIC'
            env = os.environ.copy()
            env['CPPFLAGS'] = ' '.join(x for x in (cppflags, env.get('CPPFLAGS', None)) if x)
            log.info('Building snappy...')
            exec_process(['sh', 'autogen.sh'], cwd=self.snappy_dir, env=env, silent=not self.snappy_verbose_build)
            exec_process(['./configure'], cwd=self.snappy_dir, env=env, silent=not self.snappy_verbose_build)
            exec_process(['make'], cwd=self.snappy_dir, env=env, silent=not self.snappy_verbose_build)
        if self.snappy_force_fetch:
            rmtree('deps')
        if not os.path.exists(self.snappy_dir):
            try:
                download_snappy(self.snappy_dir, self.snappy_version, self.snappy_url)
            except BaseException:
                rmtree('deps')
                raise
            build_snappy()
        else:
            if self.snappy_clean_compile:
                exec_process(['make', 'clean'], cwd=self.snappy_dir)
                exec_process(['make', 'distclean'], cwd=self.snappy_dir)
            if not os.path.exists(self.snappy_lib):
                log.info('snappy needs to be compiled.')
                build_snappy()
            else:
                log.info('No need to build snappy.')


class snappy_sdist(sdist):
    snappy_dir = os.path.join('deps', 'snappy')
    snappy_version = snappy_build_ext.snappy_version
    snappy_url = snappy_build_ext.snappy_url

    def initialize_options(self):
        sdist.initialize_options(self)
        rmtree('deps')
        download_snappy(self.snappy_dir, self.snappy_version, self.snappy_url)
