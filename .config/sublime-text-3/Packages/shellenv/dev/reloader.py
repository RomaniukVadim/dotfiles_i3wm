# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys


pkg_name = 'shellenv'

# For hot-reloading to work, we need to know all of the files in the package
# listed in their dependency order
pkg_files = [
    '._types',
    '._osx.core_foundation',
    '._osx.open_directory',
    '._linux.getent',
    '._posix',
    '._osx',
    '._linux',
    '._win',
]

if sys.version_info >= (3,):
    from imp import reload

for pkg_file in pkg_files + ['']:
    pkg_file_path = pkg_name + pkg_file
    if pkg_file_path in sys.modules:
        reload(sys.modules[pkg_file_path])
