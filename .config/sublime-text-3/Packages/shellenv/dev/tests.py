# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import unittest

import os
import sys
import locale
from os import path

if sys.version_info < (3,):
    str_cls = unicode  # noqa
else:
    str_cls = str

from .unittest_data import data, data_class

import shellenv
import os


@data_class
class ShellenvTests(unittest.TestCase):

    @staticmethod
    def shells():
        if sys.platform == 'win32':
            return [(None,)]

        output = [(None,)]

        shell_map = {}
        with open('/etc/shells', 'rb') as f:
            contents = f.read().decode('utf-8')

            for line in contents.splitlines():
                line = line.strip()
                if len(line) < 1:
                    continue
                if line[0] == '#':
                    continue

                if not os.path.exists(line):
                    continue

                name = path.basename(line)
                # rbash is a really limited shell, so we don't
                # even bother trying to test it and screen isn't
                # really a shell
                if name in set(['rbash', 'screen']):
                    continue
                shell_map[name] = line

        for name in shell_map:
            to_add = (shell_map[name],)
            output.append(to_add)

        return output

    @data('shells')
    def get_env(self, shell):
        shell, env = shellenv.get_env(shell)

        self.assertEqual(str_cls, type(shell))

        if sys.platform == 'win32':
            home_var = 'HOMEPATH'
        else:
            home_var = 'HOME'

        home_val = os.environ[home_var]
        if sys.version_info < (3,):
            home_val = home_val.decode('mbcs' if sys.platform == 'win32' else 'utf-8')

        self.assertEqual(home_val, env[home_var])

        if sys.platform == 'win32':
            user_var = 'USERNAME'
        else:
            user_var = 'USER'

        user_val = os.environ[user_var]
        if sys.version_info < (3,):
            user_val = user_val.decode(locale.getpreferredencoding() if sys.platform == 'win32' else 'utf-8')

        self.assertEqual(user_val, env[user_var])

        self.assertTrue(len(env) > 5)

        for key in env:
            self.assertEqual(str_cls, type(key))
            self.assertEqual(str_cls, type(env[key]))

    @data('shells')
    def get_env_for_subprocess(self, shell):
        shell, env = shellenv.get_env(shell, for_subprocess=True)

        self.assertEqual(str, type(shell))

        self.assertTrue(len(env) > 5)

        for key in env:
            self.assertEqual(str, type(key))
            self.assertEqual(str, type(env[key]))

    @data('shells')
    def path_types(self, shell):
        shell, dirs = shellenv.get_path(shell)

        self.assertEqual(str_cls, type(shell))

        self.assertTrue(len(dirs) > 1)

        for dir_ in dirs:
            self.assertEqual(str_cls, type(dir_))

    def test_get_login_shell(self):
        username = shellenv.get_user()
        shell = shellenv.get_user_login_shell(username)

        self.assertEqual(str_cls, type(username))
        self.assertTrue(len(username) > 0)
        self.assertEqual(str_cls, type(shell))
        self.assertTrue(len(shell) > 0)

    def test_get_env_ensure_copy(self):
        shell, env = shellenv.get_env()
        env['FOOBAR'] = 'test'
        shell2, env2 = shellenv.get_env()

        self.assertEqual(None, env2.get('FOOBAR'))

    def test_env_encode(self):
        value = shellenv.env_encode('env value')
        if sys.version_info < (3,):
            self.assertEqual(b'env value', value)
        else:
            self.assertEqual('env value', value)

    def test_env_decode(self):
        if sys.version_info < (3,):
            source = b'env value'
        else:
            source = 'env value'
        value = shellenv.env_decode(source)
        self.assertEqual('env value', value)

    def test_path_encode(self):
        value = shellenv.path_encode(os.path.expanduser('~'))
        if sys.version_info < (3,):
            self.assertEqual(os.path.expanduser(b'~'), value)
        else:
            self.assertEqual(os.path.expanduser('~'), value)

    def test_path_decode(self):
        if sys.version_info < (3,):
            source = os.path.expanduser(b'~')
        else:
            source = os.path.expanduser('~')
        value = shellenv.path_decode(source)
        self.assertEqual(os.path.expanduser('~'), value)
