# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import re
import ctypes
import time
import threading
from ctypes import wintypes

if sys.version_info < (3,):
    import _winreg as winreg
else:
    import winreg

from ._types import verify_unicode, verify_unicode_list, verify_unicode_dict


def launch_powershell(cwd, env=None, width=1024):
    """
    Launches PowerShell in such a way that is mimics the shortcut from the start
    menu, using a dark blue background and light grey text

    :param cwd:
        A unicode string of the working directory to open PowerShell to

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :param width:
        An integer of the width of the window in pixels - this it not easy to
        change once the program is opened
    """

    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')

    # Make sure the registry settings are set so that PowerShell looks correct
    key_string = 'Console\\%SystemRoot%_system32_WindowsPowerShell_v1.0_powershell.exe'
    try:
        # If the key is already present, don't do anything since we may
        # override the user's customizations
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_string)
    except (WindowsError):
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_string)
        winreg.SetValueEx(key, 'FaceName', 0, winreg.REG_SZ, "Lucida Console")
        winreg.SetValueEx(key, 'FontFamily', 0, winreg.REG_DWORD, 0x00000036)
        winreg.SetValueEx(key, 'FontSize', 0, winreg.REG_DWORD, 0x000c0000)
        winreg.SetValueEx(key, 'FontWeight', 0, winreg.REG_DWORD, 0x00000190)
        winreg.SetValueEx(key, 'HistoryNoDup', 0, winreg.REG_DWORD, 0x00000000)
        winreg.SetValueEx(key, 'QuickEdit', 0, winreg.REG_DWORD, 0x00000001)
        winreg.SetValueEx(key, 'ScreenBufferSize', 0, winreg.REG_DWORD, 0x0bb80078)
        winreg.SetValueEx(key, 'WindowSize', 0, winreg.REG_DWORD, 0x00320078)
        winreg.SetValueEx(key, 'ColorTable05', 0, winreg.REG_DWORD, 0x00562401)
        winreg.SetValueEx(key, 'ColorTable06', 0, winreg.REG_DWORD, 0x00f0edee)

    env_bytes, existing_env = _build_env(env)

    startupinfo = _build_startupinfo(width, 768, FOREGROUND_YELLOW | BACKGROUND_MAGENTA)

    process_info = PROCESS_INFORMATION()

    # We use a buffer here since CreateProcess can modify it
    command_line = ctypes.create_unicode_buffer(32768)
    command_line.value = '%s\\system32\\WindowsPowerShell\\v1.0\\powershell.exe' % existing_env['WINDIR']

    kernel32.CreateProcessW(
        None,
        command_line,
        None,
        None,
        False,
        CREATE_NEW_CONSOLE | CREATE_UNICODE_ENVIRONMENT,
        env_bytes,
        cwd,
        ctypes.byref(startupinfo),
        ctypes.byref(process_info)
    )

    kernel32.CloseHandle(process_info.hProcess)
    kernel32.CloseHandle(process_info.hThread)

    # To set the window title, we can't use startupinfo.lpTitle because it
    # breaks the functionality where PowerShell will read configuration
    # information from the registry, which is how we emulate the settings of
    # the default Windows PowerShell shortcut. Instead, we run a thread waiting
    # for a window to appear from the new process and manually set the title.
    threading.Thread(
        target=_set_window_text,
        args=(
            process_info.dwProcessId,
            'Windows PowerShell'
        )
    ).start()


def launch_cmd(cwd, env=None, width=1024):
    """
    Launches cmd.exe with a custom width and a unicode environment

    :param cwd:
        A unicode string of the working directory to open cmd.exe to

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :param width:
        An integer of the width of the window in pixels - this it not easy to
        change once the program is opened
    """

    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')

    env_bytes, existing_env = _build_env(env)

    startupinfo = _build_startupinfo(width, 768, 0)

    process_info = PROCESS_INFORMATION()

    # We use a buffer here since CreateProcess can modify it
    command_line = ctypes.create_unicode_buffer(32768)
    command_line.value = existing_env['COMSPEC']

    kernel32.CreateProcessW(
        None,
        command_line,
        None,
        None,
        False,
        CREATE_NEW_CONSOLE | CREATE_UNICODE_ENVIRONMENT,
        env_bytes,
        cwd,
        ctypes.byref(startupinfo),
        ctypes.byref(process_info)
    )

    kernel32.CloseHandle(process_info.hProcess)
    kernel32.CloseHandle(process_info.hThread)


def launch_executable(executable, args, cwd, env=None):
    """
    Launches an executable with optional arguments inside of a unicode
    environment

    :param executable:
        A unicode string of an executable

    :param args:
        A list of unicode strings to pass as arguments to the executable

    :param cwd:
        A unicode string of the working directory to open the executable to

    :param env:
        A dict of unicode strings for a custom environmental variables to set
    """

    verify_unicode(executable, 'executable')
    verify_unicode_list(args, 'args', allow_none=True)
    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')

    env_bytes, existing_env = _build_env(env)
    startupinfo = _build_startupinfo(0, 0, 0)
    process_info = PROCESS_INFORMATION()

    temp_command_line = '"' + executable + '"'
    if args is None:
        args = []
    if os.path.basename(executable).lower() == 'cmder.exe':
        args = ['/START', cwd] + args
    if args:
        for arg in args:
            if re.search('[ \t"]', arg) is not None:
                arg = '"' + arg.replace('"', '\\"') + '"'
            temp_command_line += ' ' + arg

    # We use a buffer here since CreateProcess can modify it
    command_line = ctypes.create_unicode_buffer(32768)
    command_line.value = temp_command_line

    kernel32.CreateProcessW(
        None,
        command_line,
        None,
        None,
        False,
        CREATE_NEW_CONSOLE | CREATE_UNICODE_ENVIRONMENT,
        env_bytes,
        cwd,
        ctypes.pointer(startupinfo),
        ctypes.byref(process_info)
    )

    kernel32.CloseHandle(process_info.hProcess)
    kernel32.CloseHandle(process_info.hThread)


def _build_env(env):
    """
    Builds a unicode environment string for CreateProcessW(), overlaying custom
    values that the user provided

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :return:
        A two-element tuple

         - [0] None or a byte string to pass to CreateProcessW()
         - [1] A dict of unicode keys and values, with keys being all uppercase
    """

    str_pointer = kernel32.GetEnvironmentStringsW()

    system_drive_string = None
    string = ctypes.wstring_at(str_pointer)
    existing_env = {}
    while string != '':
        # The first entry is the system drive string, which is in a weird
        # format, so we just copy it since it is required by CreateProcess()
        if not system_drive_string:
            system_drive_string = string

        elif string[0].isalpha():
            name, value = string.split('=', 1)
            existing_env[name.upper()] = value

        # Include the trailing null byte, and measure each
        # char as 2 bytes since Windows uses UTF-16 for
        # wide chars
        str_pointer += (len(string) + 1) * 2
        string = ctypes.wstring_at(str_pointer)

    if env:
        for key, value in env.items():
            if value is None:
                if key.upper() in existing_env:
                    del existing_env[key.upper()]
            else:
                existing_env[key.upper()] = value

        env_string = '%s\x00' % system_drive_string
        for name in sorted(existing_env.keys(), key=lambda s: s.lower()):
            env_string += '%s=%s\x00' % (name, existing_env[name])
        env_string += '\x00'
        env_bytes = env_string.encode('utf-16le')

    else:
        env_bytes = None

    return env_bytes, existing_env


def _build_startupinfo(width, height, custom_colors=0):
    """
    Creates a STARTUPINFO ctypes.Structure with setting to control the
    appearance

    :param width:
        The width of the new window

    :param heigh:
        The height of the new window

    :param custom_colors:
        An integer from the FOREGROUND_* and BACKGROUND_* constants

    :return:
        A STARTUPINFO object
    """

    flags = 0
    if width or height:
        flags |= STARTF_USESIZE
    if custom_colors:
        flags |= STARTF_USEFILLATTRIBUTE

    startupinfo = STARTUPINFO(
        0,
        None,
        None,
        None,
        0,
        0,
        width,
        height,
        0,
        0,
        custom_colors,
        flags,
        0,
        0,
        None,
        None,
        None,
        None
    )
    startupinfo.cb = ctypes.sizeof(startupinfo)

    return startupinfo


def _set_window_text(process_id, text):
    """
    Set the title of a window based on the process id

    RUNS IN A THREAD

    :param process_id:
        An integer of the process id

    :param text:
        A unicode string of the new window title
    """

    process_details = {
        'window_handle': None,
        'process_id': process_id
    }

    window_process_id = wintypes.DWORD(0)

    def find_window_handle(handle, _):
        user32.GetWindowThreadProcessId(handle, ctypes.byref(window_process_id))
        if window_process_id.value == process_details['process_id']:
            process_details['window_handle'] = handle
        return 1
    enum_windows_callback = EnumWindowsProc(find_window_handle)

    user32.EnumWindows(enum_windows_callback, 1)
    while process_details['window_handle'] is None:
        time.sleep(0.1)
        user32.EnumWindows(enum_windows_callback, None)

    user32.SetWindowTextW(process_details['window_handle'], text)


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


if not hasattr(wintypes, 'LPBYTE'):
    setattr(wintypes, 'LPBYTE', ctypes.POINTER(wintypes.BYTE))

if sys.maxsize > 2 ** 32:
    LONG_PTR = ctypes.c_int64
else:
    LONG_PTR = ctypes.c_long


class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', wintypes.LPBYTE),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE),
    ]


class PROCESS_INFORMATION(ctypes.Structure):  # noqa
    _fields_ = [
        ('hProcess', wintypes.HANDLE),
        ('hThread', wintypes.HANDLE),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD),
    ]


kernel32.CreateProcessW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    wintypes.LPVOID,
    wintypes.LPVOID,
    wintypes.BOOL,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.LPCWSTR,
    ctypes.POINTER(STARTUPINFO),
    ctypes.POINTER(PROCESS_INFORMATION)
]
kernel32.CreateProcessW.restype = wintypes.BOOL

kernel32.GetEnvironmentStringsW.argtypes = []
kernel32.GetEnvironmentStringsW.restype = ctypes.c_void_p

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HANDLE, LONG_PTR)
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPVOID]
user32.EnumWindows.restype = wintypes.BOOL

user32.GetWindowThreadProcessId.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.DWORD)
]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD

user32.SetWindowTextW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL

CREATE_NEW_CONSOLE = 0x00000010
CREATE_UNICODE_ENVIRONMENT = 0x00000400

STARTF_USESIZE = 0x00000002
STARTF_USEFILLATTRIBUTE = 0x00000010

FOREGROUND_GREEN = 2
FOREGROUND_RED = 4
BACKGROUND_BLUE = 16
BACKGROUND_RED = 64
FOREGROUND_YELLOW = FOREGROUND_RED + FOREGROUND_GREEN
BACKGROUND_MAGENTA = BACKGROUND_RED + BACKGROUND_BLUE
