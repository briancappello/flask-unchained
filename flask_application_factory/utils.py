import inspect
import os

from importlib import import_module

# alias these to the utils module
from .inflect import de_camel, pluralize, singularize


def get_boolean_env(name, default):
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in ['true', 'yes', '1']


def get_members(module, predicate):
    """
    Like inspect.getmembers except predicate is passed both name and object
    """
    for name, obj in inspect.getmembers(module):
        if predicate(name, obj):
            yield (name, obj)


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


def title_case(string):
    return de_camel(string).replace('_', ' ').title()
