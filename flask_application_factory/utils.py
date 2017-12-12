import inspect
import os
import re

from importlib import import_module


camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def camel_to_snake_case(name):  # from flask_sqlalchemy.model
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')


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
    return camel_to_snake_case(string).replace('_', ' ').title()
