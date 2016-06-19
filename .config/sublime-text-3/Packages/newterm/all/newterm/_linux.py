# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import subprocess


_window_manager = None

_terminal_mapping = {
    'gnome': 'gnome-terminal',
    'cinnamon': 'gnome-terminal',
    'xfce': 'xfce4-terminal',
    'kde': 'konsole',
    'lxde': 'lxterminal',
    'mate': 'mate-terminal',
    'unknown': 'xterm',
}


def get_default_terminal():
    """
    Searches the list of running processes to see what window manager is running
    and uses that to pick the default terminal program

    :return:
        A unicode string of the name of the terminal executable
    """

    return _terminal_mapping.get(_get_window_manager(), 'xterm')


def _get_window_manager():
    """
    Returns the currently running window manager

    :return:
        A unicode string of one of the following:

         - "gnome"
         - "cinnamon"
         - "xfce"
         - "kde"
         - "lxde"
         - "mate"
         - "unknown"
    """

    global _window_manager

    if _window_manager is None:
        proc = subprocess.Popen(
            ['ps', '-eo', 'comm'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = proc.communicate()

        if stderr:
            raise OSError(stderr.decode('utf-8'))

        output = stdout.decode('utf-8')

        for line in output.splitlines():
            if line.startswith('gnome-session'):
                _window_manager = 'gnome'
                break

            if line.startswith('cinnamon-sessio'):
                _window_manager = 'cinnamon'
                break

            if line.startswith('xfce4-session'):
                _window_manager = 'xfce'
                break

            if line.startswith('ksmserver'):
                _window_manager = 'kde'
                break

            if line.startswith('lxsession'):
                _window_manager = 'lxde'
                break

            if line.startswith('mate-panel'):
                _window_manager = 'mate'
                break

        if _window_manager is None:
            _window_manager = 'unknown'

    return _window_manager
