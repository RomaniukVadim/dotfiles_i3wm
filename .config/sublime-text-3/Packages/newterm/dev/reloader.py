# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys


# The name of the package
pkg_name = 'newterm'

# A list of all python files in subdirectories, listed in their dependency order
pkg_files = [
    '._types',
    '._osx',
    '._linux',
    '._posix',
    '._win',
    '',
]

if sys.version_info >= (3,):
    from imp import reload

for pkg_file in pkg_files:
    if pkg_file in sys.modules:
        reload(sys.modules[pkg_file])
