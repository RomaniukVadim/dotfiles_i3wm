# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import sys


if sys.version_info < (3,):
    str_cls = unicode  # noqa
    byte_cls = str

else:
    str_cls = str
    byte_cls = bytes


def verify_unicode(value, param_name, allow_none=False):
    """
    Raises a TypeError if the value is not a unicode string

    :param value:
        The value that should be a unicode string

    :param param_name:
        The unicode string of the name of the parameter, for use in the
        exception message

    :param allow_none:
        If None is a valid value
    """

    if allow_none and value is None:
        return

    if not isinstance(value, str_cls):
            raise TypeError('%s must be a unicode string, not %s' % (param_name, type_name(value)))


def verify_unicode_list(value, param_name, allow_none=False):
    """
    Raises a TypeError if the value is not a list or tuple of unicode strings

    :param value:
        The value that should be a list/tuple of unicode strings

    :param param_name:
        The unicode string of the name of the parameter, for use in the
        exception message

    :param allow_none:
        If None is a valid value
    """

    if allow_none and value is None:
        return

    if not isinstance(value, (list, tuple)):
        raise TypeError('%s must be a list or tuple of unicode strings, not %s' % (param_name, type_name(value)))

    for arg in value:
        if not isinstance(arg, str_cls):
            raise TypeError('%s must be a list or tuple containing only unicode strings, not %s' % (param_name, type_name(arg)))


def verify_unicode_dict(value, param_name):
    """
    Raises a TypeError if the value is not a dict with unicode string keys and
    unicode string or None values

    :param value:
        The value that should be a dict of unicode strings

    :param param_name:
        The unicode string of the name of the parameter, for use in the
        exception message
    """

    if value is None:
        return

    if not isinstance(value, dict):
        raise TypeError('%s must be a dict of unicode strings, not %s' % (param_name, type_name(value)))

    for key, value in value.items():
        if not isinstance(key, str_cls):
            raise TypeError('%s must be a dict containing only unicode strings for keys, not %s' % (param_name, type_name(key)))
        if value is not None and not isinstance(value, str_cls):
            raise TypeError('%s must be a dict containing only unicode strings or None for values, not %s' % (param_name, type_name(value)))


def type_name(value):
    """
    Returns a user-readable name for the type of an object

    :param value:
        A value to get the type name of

    :return:
        A unicode string of the object's type name
    """

    cls = value.__class__
    if cls.__module__ in set(['builtins', '__builtin__']):
        return cls.__name__
    return '%s.%s' % (cls.__module__, cls.__name__)
