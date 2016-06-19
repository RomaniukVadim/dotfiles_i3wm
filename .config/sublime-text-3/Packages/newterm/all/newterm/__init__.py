# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys

if sys.platform == 'win32':
    from ._win import launch_powershell, launch_cmd, launch_executable

elif sys.platform == 'darwin':
    from ._osx import launch_terminal_app, launch_iterm_app
    from ._posix import launch_executable

else:
    from ._linux import get_default_terminal
    from ._posix import launch_executable

from ._types import verify_unicode, verify_unicode_list, verify_unicode_dict


__version__ = '1.0.0'
__version_info__ = (1, 0, 0)


def launch_terminal(cwd, env=None, terminal=None, args=None, width=1024, use_tabs=False):
    """
    Launches a terminal at the directory specified

    :param cwd:
        A unicode string of the working directory to open the terminal to

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :param terminal:
        A unicode string of the name of the terminal to execute. If None, uses
        the OS default. Special OS X values include: "Terminal.app" and
        "iTerm.app". Special Windows values include: "powershell.exe" and
        "cmd.exe". All others are launched as a subprocess and must pick up the
        cwd and env from the Python subprocess module.

    :param args:
        A list of unicode strings of the arguments to pass to the terminal
        executable. Ignored when terminal is set to any of:

         - "Terminal.app"
         - "iTerm.app",
         - "cmd.exe"
         - "powershell.exe"

    :param width:
        Windows only: an integer of the width of the terminal window when
        terminal is None, "powershell.exe" or "cmd.exe"

    :param use_tabss:
        OS X only: a boolean if tabs should be used instead of new windows when
        terminal is None, "Terminal.app" or "iTerm.app"
    """

    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')
    verify_unicode(terminal, 'terminal', allow_none=True)
    verify_unicode_list(args, 'args', allow_none=True)

    if sys.platform == 'darwin':
        if terminal is None or terminal == 'Terminal.app':
            launch_terminal_app(cwd, env=env, use_tabs=use_tabs)
        elif terminal == 'iTerm.app':
            launch_iterm_app(cwd, env=env, use_tabs=use_tabs)
        else:
            launch_executable(terminal, args, cwd, env=env)

    elif sys.platform == 'win32':
        if terminal is None or terminal == 'powershell.exe':
            launch_powershell(cwd, env=env, width=width)
        elif terminal == 'cmd.exe':
            launch_cmd(cwd, env=env, width=width)
        else:
            launch_executable(terminal, args, cwd, env=env)

    else:
        if terminal is None:
            terminal = get_default_terminal()
        launch_executable(terminal, args, cwd, env=env)
