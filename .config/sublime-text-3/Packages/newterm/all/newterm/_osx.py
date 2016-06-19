# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import ctypes
from ctypes import c_void_p
from ctypes.util import find_library

import shellenv

from ._types import str_cls, verify_unicode, verify_unicode_dict


def launch_terminal_app(cwd, env=None, use_tabs=False):
    """
    Launches Terminal.app

    :param cwd:
        A unicode string of the working directory to open Terminal to

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :param use_tabs:
        If Terminal is already open, create a new tab instead of a new window
    """

    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')

    # If no tab is required, the fastest tab to get to a dir is to use "open"
    if not use_tabs:
        _open_file_with_application(cwd, 'Terminal')

    else:
        cd_command = 'do script ' + _applescript_quote('cd ' + _shell_quote(cwd)) + ' in window 1'
        clear_command = ''
        if not env:
            clear_command = 'do script "clear" in window 1'
        script = NSAppleScript("""
            tell application "System Events"
                if (count(processes whose name is "Terminal")) is 0 then
                    tell application "Terminal"
                        activate
                    end tell
                else
                    tell application "Terminal"
                        activate
                    end tell
                    tell application "System Events" to tell process "Terminal" to keystroke "t" using command down
                end if
                tell application "Terminal"
                    %s
                    %s
                end tell
            end tell
        """ % (cd_command, clear_command))
        script.execute()

    if not env:
        return

    if env:
        lines = []
        for set_command in _build_set_commands(env):
            lines.append('do script ' + _applescript_quote(set_command) + ' in window 1')
        set_commands = "\n".join(lines)
    else:
        set_commands = ''

    clear_command = 'do script "clear" in window 1'

    script = NSAppleScript("""
        try
            tell application "System Events"
                tell application "Terminal"
                    %s
                    %s
                end tell
            end tell
        end try
    """ % (set_commands, clear_command))

    script.execute()


def launch_iterm_app(cwd, env=None, use_tabs=False):
    """
    Launches iTerm.app

    :param cwd:
        A unicode string of the working directory to open iTerm to

    :param env:
        A dict of unicode strings for a custom environmental variables to set

    :param use_tabs:
        If iTerm is already open, create a new tab instead of a new window
    """

    verify_unicode(cwd, 'cwd')
    verify_unicode_dict(env, 'env')

    if env:
        lines = []
        for set_command in _build_set_commands(env):
            lines.append('write text ' + _applescript_quote(set_command))
        set_commands = "\n".join(lines)
    else:
        set_commands = ''

    cd_command = 'write text ' + _applescript_quote('cd ' + _shell_quote(cwd))
    clear_command = 'write text "clear"'

    setup_commands = """
        write ""
        delay 0.25
        %s
        %s
        %s
    """ % (set_commands, cd_command, clear_command)
    setup_commands = setup_commands.strip()

    running = NSAppleScript("""
       tell application "System Events"
           count(processes whose name is "iTerm")
       end tell
    """).execute()

    if int(running) < 1:
        script = NSAppleScript("""
                tell application "iTerm"
                    activate
                    set term to current terminal
                    tell term
                        tell the last session
                            %s
                        end tell
                    end tell
                end tell
        """ % setup_commands)
    else:
        if use_tabs:
            script = NSAppleScript("""
                tell application "iTerm"

                    if (count of terminals) = 0 then
                        set term to (make new terminal)
                    else
                        set term to current terminal
                    end if
                    tell term
                        launch session "Default Session"
                        tell the last session
                            %s
                        end tell
                    end tell
                end tell
            """ % setup_commands)
        else:
            script = NSAppleScript("""
                tell application "iTerm"
                    set term to (make new terminal)
                    tell term
                        launch session "Default Session"
                        tell the last session
                            %s
                        end tell
                    end tell
                end tell
            """ % setup_commands)
    script.execute()


def _open_file_with_application(file, application):
    """
    Replicates the OS X command line tool "open -a" by using the AppKit API

    :param file:
        A unicode string of the file/folder to open

    :param application:
        A unicode string of the name of the application to use
    """

    _SHARED_WORKSPACE.open_file_with_application(file, application)


def _build_set_commands(env):
    """
    Constructs a list of unicode strings containing shell commands to set
    environmental variables
    """

    shell_name = os.path.basename(shellenv.get_user_login_shell())

    if shell_name == 'fish':
        set_command = "set -gx %s %s"
    elif shell_name in set(['tcsh', 'csh']):
        set_command = "setenv %s %s"
    else:
        set_command = "export %s=%s"

    if shell_name == 'fish':
        unset_command = "set -e %s"
    elif shell_name in set(['tcsh', 'csh']):
        unset_command = "unset %s"
    else:
        unset_command = "unset -v %s"

    output = []
    for key, value in env.items():
        if value is None:
            output.append(unset_command % key)
        else:
            output.append(set_command % (key, _shell_quote(value)))
    return output


def _shell_quote(string):
    """
    Create a single-quoted string for a shell

    :param string:
        A unicode string to quote

    :return:
        A unicode string quoted for a shell
    """

    return "'" + string.replace("'", "'\\''") + "'"


def _applescript_quote(string):
    """
    Creates a double-quoted string for AppleScript

    :param string:
        A unicode string to quote

    :return:
        A unicode string quoted for AppleScript
    """

    return '"' + string.replace('"', '\\"') + '"'


# Load AppKit since that makes NSWorkspace and NSAppleScript available
AppKit = ctypes.CDLL(find_library('AppKit'))
objc = ctypes.CDLL(find_library('objc'))

objc.objc_getClass.argtypes = [ctypes.c_char_p]
objc.objc_getClass.restype = c_void_p

objc.sel_registerName.argtypes = [ctypes.c_char_p]
objc.sel_registerName.restype = c_void_p

objc.objc_msgSend.argtypes = [c_void_p, c_void_p]
objc.objc_msgSend.restype = c_void_p


def _objc_get_class(name):
    """
    Obtains a reference to an Objective C class

    :param name:
        A unicode string of the name of the class

    :return:
        A ctypes.c_void_p object referencing the class
    """

    return c_void_p(objc.objc_getClass(name.encode('ascii')))


def _sel_register_name(name):
    """
    Obtains a reference to an Objective C selector

    :param name:
        A unicode string of the name of the selector

    :return:
        A ctypes.c_void_p object referencing the selector
    """

    return c_void_p(objc.sel_registerName(name.encode('ascii')))


def _objc_msg_send(*args, **kwargs):
    """
    Sends a message to an object. All params must be ctypes objects since there
    is no enforced argtypes since different messages can have different
    signatures.

    :params result_type:
        A ctypes type that the result should be

    :return:
        A ctypes.c_void_p object
    """

    if not kwargs or 'result_type' not in kwargs:
        result_type = c_void_p
    else:
        result_type = kwargs['result_type']

    result = objc.objc_msgSend(*args)
    if result is None and result_type == ctypes.c_int32:
        result = 0
    return result_type(result)


class NSAutoreleasePool():
    _class_ref = _objc_get_class('NSAutoreleasePool')
    _alloc_sel = _sel_register_name('alloc')
    _init_sel = _sel_register_name('init')
    _instance_ref = None

    def __init__(self):
        self._instance_ref = _objc_msg_send(
            self._class_ref,
            self._alloc_sel
        )
        _objc_msg_send(
            self._instance_ref,
            self._init_sel
        )


_POOL = NSAutoreleasePool()


class NSString():
    _class_ref = _objc_get_class('NSString')
    _string_with_utf8_string_sel = _sel_register_name('stringWithUTF8String:')
    _utf8string_sel = _sel_register_name('UTF8String')
    _instance_ref = None

    def __init__(self, initializer):
        if isinstance(initializer, str_cls):
            self._instance_ref = _objc_msg_send(
                self._class_ref,
                self._string_with_utf8_string_sel,
                ctypes.c_char_p(initializer.encode('utf-8'))
            )
        else:
            self._instance_ref = initializer

    @property
    def pointer(self):
        return self._instance_ref

    def __str__(self):
        if sys.version_info < (3,):
            raise NotImplementedError('Byte string support is not implemented - use unicode strings instead')
        return self.__unicode__()

    def __unicode__(self):
        output = _objc_msg_send(
            self._instance_ref,
            self._utf8string_sel,
            result_type=ctypes.c_char_p
        ).value
        if output is not None:
            output = output.decode('utf-8')
        return output or ''


class NSApplication():
    _class_ref = _objc_get_class('NSApplication')
    _shared_application_sel = _sel_register_name('sharedApplication')
    _set_activation_policy_sel = _sel_register_name('setActivationPolicy:')

    @classmethod
    def shared(cls):
        output = NSApplication()
        output._instance_ref = _objc_msg_send(
            cls._class_ref,
            cls._shared_application_sel
        )
        return output

    def set_activation_policy(self, policy):
        _objc_msg_send(
            self._instance_ref,
            self._set_activation_policy_sel,
            policy
        )


if sys.maxsize > 2 ** 32:
    NSInteger = ctypes.c_int64
else:
    NSInteger = ctypes.c_int32

NSApplicationActivationPolicyProhibited = NSInteger(2)


# When interacting with AppKit by using NSWorkspace or NSAppleScript, OS X
# adds plugin_host to the dock with the Sublime Text icon. This hides the icon
# so that there aren't two ST icons in the dock.
if sys.version_info >= (3,):
    _SHARED_APPLICATION = NSApplication.shared()
    _SHARED_APPLICATION.set_activation_policy(NSApplicationActivationPolicyProhibited)


class NSWorkspace():
    _class_ref = _objc_get_class('NSWorkspace')
    _shared_workspace_sel = _sel_register_name('sharedWorkspace')
    _open_file_with_application_sel = _sel_register_name('openFile:withApplication:')

    @classmethod
    def shared(cls):
        output = NSWorkspace()
        output._instance_ref = _objc_msg_send(
            cls._class_ref,
            cls._shared_workspace_sel
        )
        return output

    def open_file_with_application(self, filename, application):
        _objc_msg_send(
            self._instance_ref,
            self._open_file_with_application_sel,
            NSString(filename).pointer,
            NSString(application).pointer
        )


_SHARED_WORKSPACE = NSWorkspace.shared()


class NSAppleEventDescriptor():
    _int32_value_sel = _sel_register_name('int32Value')
    _string_value_sel = _sel_register_name('stringValue')
    _instance_ref = None

    def __init__(self, instance_ref):
        self._instance_ref = instance_ref

    def __int__(self):
        return _objc_msg_send(
            self._instance_ref,
            self._int32_value_sel,
            result_type=ctypes.c_int32
        ).value

    def __unicode__(self):
        return NSString(_objc_msg_send(
            self._instance_ref,
            self._string_value_sel
        )).__unicode__()

    def __str__(self):
        if sys.version_info < (3,):
            raise NotImplementedError('Byte string support is not implemented - use unicode strings instead')
        return self.__unicode__()


class NSAppleScript():
    _class_ref = _objc_get_class('NSAppleScript')
    _alloc_sel = _sel_register_name('alloc')
    _init_with_source_sel = _sel_register_name('initWithSource:')
    _execute_and_return_error_sel = _sel_register_name('executeAndReturnError:')
    _instance_ref = None

    def __init__(self, source):
        self._instance_ref = _objc_msg_send(
            self._class_ref,
            self._alloc_sel
        )
        _objc_msg_send(
            self._instance_ref,
            self._init_with_source_sel,
            NSString(source).pointer
        )

    def execute(self, error_dictionary=None):
        return NSAppleEventDescriptor(_objc_msg_send(
            self._instance_ref,
            self._execute_and_return_error_sel,
            c_void_p(None)
        ))
