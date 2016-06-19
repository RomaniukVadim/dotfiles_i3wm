# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import threading
import unittest
from os import path

import sublime

import newterm

from .unittest_data import data, data_class


PACKAGE_PATH = path.dirname(path.dirname(__file__))
if sys.version_info < (3,):
    PACKAGE_PATH = PACKAGE_PATH.decode('mbcs' if sys.platform == 'win32' else 'utf-8')


@data_class
class NewtermTests(unittest.TestCase):

    @staticmethod
    def terminal_app_configs():
        if sys.platform != 'darwin':
            return []

        return (
            (
                'basic',
                PACKAGE_PATH,
                None,
                {},
                'Terminal.app open to %s' % PACKAGE_PATH
            ),
            (
                'env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {},
                'Terminal.app open to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
            ),
            (
                'new_tab',
                PACKAGE_PATH,
                None,
                {'use_tabs': True},
                'Terminal.app open a new tab to %s' % PACKAGE_PATH
            ),
            (
                'new_tab_env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {'use_tabs': True},
                'Terminal.app open a new tab to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
            ),
        )

    @data('terminal_app_configs', True)
    def terminal_app(self, cwd, env, kwargs, description):
        ensure_ui_thread()

        newterm._osx.launch_terminal_app(cwd, env, **kwargs)

        self.assertTrue(sublime.ok_cancel_dialog('Did %s?' % description, 'Yes'))

    @staticmethod
    def iterm_app_configs():
        if sys.platform != 'darwin':
            return []

        return (
            (
                'basic',
                PACKAGE_PATH,
                None,
                {},
                'iTerm.app open to %s' % PACKAGE_PATH
            ),
            (
                'env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {},
                'iTerm.app open to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
            ),
            (
                'new_tab',
                PACKAGE_PATH,
                None,
                {'use_tabs': True},
                'iTerm.app open a new tab to %s' % PACKAGE_PATH
            ),
            (
                'new_tab_env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {'use_tabs': True},
                'iTerm.app open a new tab to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
            ),
        )

    @data('iterm_app_configs', True)
    def iterm_app(self, cwd, env, kwargs, description):
        ensure_ui_thread()

        newterm._osx.launch_iterm_app(cwd, env, **kwargs)

        self.assertTrue(sublime.ok_cancel_dialog('Did %s?' % description, 'Yes'))

    @staticmethod
    def powershell_configs():
        if sys.platform != 'win32':
            return []

        return (
            (
                'basic',
                PACKAGE_PATH,
                None,
                {},
                'Powershell open to %s' % PACKAGE_PATH
            ),
            (
                'env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {},
                'Powershell open to %s with $env:TEST_VAL set to "123"' % PACKAGE_PATH
            ),
        )

    @data('powershell_configs', True)
    def powershell(self, cwd, env, kwargs, description):
        ensure_ui_thread()

        newterm._win.launch_powershell(cwd, env, **kwargs)

        self.assertTrue(sublime.ok_cancel_dialog('Did %s?' % description, 'Yes'))

    @staticmethod
    def cmd_configs():
        if sys.platform != 'win32':
            return []

        return (
            (
                'basic',
                PACKAGE_PATH,
                None,
                {},
                'cmd.exe open to %s' % PACKAGE_PATH
            ),
            (
                'env',
                PACKAGE_PATH,
                {'TEST_VAL': '123'},
                {},
                'cmd.exe open to %s with %%TEST_VAL%% set to "123"' % PACKAGE_PATH
            ),
        )

    @data('cmd_configs', True)
    def cmd(self, cwd, env, kwargs, description):
        ensure_ui_thread()

        newterm._win.launch_cmd(cwd, env, **kwargs)

        self.assertTrue(sublime.ok_cancel_dialog('Did %s?' % description, 'Yes'))

    @staticmethod
    def public_configs():
        if sys.platform == 'win32':
            return (
                (
                    'basic',
                    PACKAGE_PATH,
                    None,
                    {},
                    'Powershell open to %s' % PACKAGE_PATH
                ),
                (
                    'env',
                    PACKAGE_PATH,
                    {'TEST_VAL': '123'},
                    {},
                    'Powershell open to %s with $env:TEST_VAL set to "123"' % PACKAGE_PATH
                ),
                (
                    'powershell',
                    PACKAGE_PATH,
                    None,
                    {'terminal': 'powershell.exe'},
                    'Powershell open to %s' % PACKAGE_PATH
                ),
                (
                    'cmd',
                    PACKAGE_PATH,
                    None,
                    {'terminal': 'cmd.exe'},
                    'cmd open to %s' % PACKAGE_PATH
                ),
            )

        elif sys.platform == 'darwin':
            return (
                (
                    'basic',
                    PACKAGE_PATH,
                    None,
                    {},
                    'Terminal.app open to %s' % PACKAGE_PATH
                ),
                (
                    'env',
                    PACKAGE_PATH,
                    {'TEST_VAL': '123'},
                    {},
                    'Terminal.app open to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
                ),
                (
                    'terminal_app',
                    PACKAGE_PATH,
                    None,
                    {'terminal': 'Terminal.app'},
                    'Terminal.app open to %s' % PACKAGE_PATH
                ),
                (
                    'iterm_app',
                    PACKAGE_PATH,
                    None,
                    {'terminal': 'iTerm.app'},
                    'iTerm.app open to %s' % PACKAGE_PATH
                ),
            )

        else:
            return (
                (
                    'basic',
                    PACKAGE_PATH,
                    None,
                    {},
                    'Terminal open to %s' % PACKAGE_PATH
                ),
                (
                    'env',
                    PACKAGE_PATH,
                    {'TEST_VAL': '123'},
                    {},
                    'Terminal open to %s with $TEST_VAL set to "123"' % PACKAGE_PATH
                ),
            )

    @data('public_configs', True)
    def public(self, cwd, env, kwargs, description):
        ensure_ui_thread()

        newterm.launch_terminal(cwd, env, **kwargs)

        self.assertTrue(sublime.ok_cancel_dialog('Did %s?' % description, 'Yes'))

    def test_bytes_cwd(self):
        def do_test():
            newterm.launch_terminal(PACKAGE_PATH.encode('utf-8'))
        self.assertRaises(TypeError, do_test)

    def test_bytes_env_key(self):
        def do_test():
            newterm.launch_terminal(PACKAGE_PATH, {b'key': 'value'})
        self.assertRaises(TypeError, do_test)

    def test_bytes_env_value(self):
        def do_test():
            newterm.launch_terminal(PACKAGE_PATH, {'key': b'value'})
        self.assertRaises(TypeError, do_test)


def ensure_ui_thread():
    if not isinstance(threading.current_thread(), threading._MainThread):
        raise RuntimeError('Tests must be run in the UI thread')
