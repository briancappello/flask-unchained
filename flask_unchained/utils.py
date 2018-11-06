import datetime
import os
import re

from flask import current_app
from importlib import import_module


class AttrDict(dict):
    """
    A dictionary subclass that implements attribute access, ie using the dot operator
    to get and set keys.
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        return f'{self.__class__.__name__}({dict.__repr__(self)})'


class ConfigProperty:
    """
    Used in conjunction with ConfigPropertyMetaclass, allows extension classes to
    create properties that proxy to the config value, eg app.config.get(key)

    If key is left unspecified, in will be injected by ``ConfigPropertyMetaclass``,
    defaulting to ``f'{ext_class_name}_{property_name}'.upper()``.
    """
    def __init__(self, key=None):
        self.key = key

    def __get__(self, instance, cls):
        return current_app.config[self.key]


class ConfigPropertyMetaclass(type):
    """
    Use this metaclass to enable config properties on extension classes. I'm not
    sold on this being a good idea for *new* extensions, but for backwards
    compatibility with existing extensions that have silly ``__getattr__`` magic, I
    think it's a big improvement. (NOTE: this only works when the application
    context is available, but that's no different than the behavior of what it's
    meant to replace.)

    Example usage::

        class MyExtension(metaclass=ConfigPropertyMetaclass):
            __config_prefix__ = 'MY_EXTENSION'
            # if __config_prefix__ is unspecified, default is class_name.upper()

            foobar: Optional[FunctionType] = ConfigProperty()
            _custom: Optional[str] = ConfigProperty('MY_EXTENSION_CUSTOM')

        my_extension = MyExtension(app)
        my_extension.foobar == current_app.config.MY_EXTENSION_FOOBAR
        my_extension._custom == current_app.config.MY_EXTENSION_CUSTOM
    """
    def __init__(cls, class_name, bases, clsdict):
        super().__init__(class_name, bases, clsdict)
        config_prefix = clsdict.get('__config_prefix__', class_name).rstrip('_')
        for property_name, descriptor in clsdict.items():
            if isinstance(descriptor, ConfigProperty) and not descriptor.key:
                descriptor.key = f'{config_prefix}_{property_name}'.upper()


def format_docstring(docstring):
    """
    Strips whitespace from docstrings (both on the ends, and in the middle, replacing
    all sequential occurrences of whitespace with a single space).
    """
    if not docstring:
        return ''
    return re.sub(r'\s+', ' ', docstring).strip()


def get_boolean_env(name, default):
    """
    Converts environment variables to boolean values, where truthy is defined as:
    ``value.lower() in {'true', 'yes', 'y', '1'}`` (everything else is falsy).
    """
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in {'true', 'yes', 'y', '1'}


def safe_import_module(module_name):
    """
    Like :func:`importlib.import_module`, except it does not raise ``ImportError``
    if the requested ``module_name`` was not found.
    """
    try:
        return import_module(module_name)
    except ImportError as e:
        m = re.match(r"No module named '([\w\.]+)'", str(e))
        if not m or not module_name.startswith(m.group(1)):
            raise e


def utcnow():
    """
    Returns a current timezone-aware datetime.datetime in UTC
    """
    return datetime.datetime.now(datetime.timezone.utc)


__all__ = [
    'AttrDict',
    'ConfigProperty',
    'ConfigPropertyMetaclass',
    'format_docstring',
    'get_boolean_env',
    'safe_import_module',
    'utcnow',
]
