# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import subprocess

from ._types import verify_unicode, verify_unicode_list, verify_unicode_dict


def launch_executable(executable, args, cwd, env=None):
    """
    Launches an executable with optional arguments

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

    subprocess_args = [executable]
    if args is not None:
        subprocess_args.extend(args)

    if sys.version_info >= (3,):
        subprocess_env = dict(os.environ)
    else:
        subprocess_env = {}
        for key, value in os.environ.items():
            subprocess_env[key.decode('utf-8', 'replace')] = value.decode('utf-8', 'replace')

    if env:
        for key, value in env.items():
            if value is None:
                if key in subprocess_env:
                    del subprocess_env[key]
            else:
                subprocess_env[key] = value

    if sys.version_info < (3,):
        encoded_args = []
        for arg in subprocess_args:
            encoded_args.append(arg.encode('utf-8'))
        subprocess_args = encoded_args

        encoded_env = {}
        for key, value in subprocess_env.items():
            encoded_env[key.encode('utf-8')] = value.encode('utf-8')
        subprocess_env = encoded_env

        cwd = cwd.encode('utf-8')

    subprocess.Popen(subprocess_args, env=subprocess_env, cwd=cwd)
