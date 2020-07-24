import os
import re
import sys

from datetime import datetime, timezone
from importlib import import_module

from flask import current_app


class AttrDict(dict):
    """
    A dictionary that allows using the dot operator to get and set keys.
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        return f'{self.__class__.__name__}({dict.__repr__(self)})'


class ConfigProperty:
    """
    Allows extension classes to create properties that proxy to the config value,
    eg ``app.config[key]``.

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


def cwd_import(module_name):
    """
    Attempt to import a module from the current working directory.

    Raises ``ImportError`` if not found, or the found module isn't from the current
    working directory.
    """
    if not sys.path or sys.path[0] != os.getcwd():
        sys.path.insert(0, os.getcwd())

    module = import_module(module_name)
    expected_path = os.path.join(os.getcwd(), module_name.replace('.', os.sep))
    expected_paths = [f'{expected_path}.py', os.path.join(expected_path, '__init__.py')]
    if module.__file__ not in expected_paths:
        raise ImportError(f'expected {expected_paths[0]}, got {module.__file__}')
    return module


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
    Converts environment variables to boolean values. Truthy is defined as:
    ``value.lower() in {'true', 'yes', 'y', '1'}`` (everything else is falsy).
    """
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in {'true', 'yes', 'y', '1'}


def safe_import_module(module_name):
    """
    Like :func:`importlib.import_module`, except it does not raise ``ImportError``
    if the requested ``module_name`` is not found.
    """
    try:
        return import_module(module_name)
    except ImportError as e:
        m = re.match(r"No module named '([\w\.]+)'", str(e))
        if not m or not module_name.startswith(m.group(1)):
            raise e


def utcnow():
    """
    Returns a current timezone-aware ``datetime.datetime`` in UTC.
    """
    # timeit shows that datetime.now(tz=timezone.utc) is 24% slower
    return datetime.utcnow().replace(tzinfo=timezone.utc)


__all__ = [
    'AttrDict',
    'ConfigProperty',
    'ConfigPropertyMetaclass',
    'cwd_import',
    'format_docstring',
    'get_boolean_env',
    'safe_import_module',
    'utcnow',
]
