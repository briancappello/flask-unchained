import datetime
import os
import re

from importlib import import_module

_missing = object()


class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        return f'AttrDict({super().__repr__()})'


def deep_getattr(clsdict, bases, name, default=_missing):
    value = clsdict.get(name, _missing)
    if value != _missing:
        return value
    for base in bases:
        value = getattr(base, name, _missing)
        if value != _missing:
            return value
    if default != _missing:
        return default
    raise AttributeError(name)


def format_docstring(docstring):
    if not docstring:
        return ''
    return re.sub(r'\s+', ' ', docstring).strip()


def get_boolean_env(name, default):
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in {'true', 'yes', 'y', '1'}


def safe_import_module(module_name):
    """
    Like importlib's import_module, except it does not raise ImportError
    if the requested module_name was not found
    """
    try:
        return import_module(module_name)
    except ImportError as e:
        if module_name not in str(e):
            raise e


def utcnow():
    """
    Returns a current timezone-aware datetime.datetime in UTC
    """
    return datetime.datetime.now(datetime.timezone.utc)
