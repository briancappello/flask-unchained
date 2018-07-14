import datetime
import os
import re

from flask import current_app
from importlib import import_module

_missing = type('_missing', (), {'__bool__': lambda s: False})()


class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self):
        return f'AttrDict({super().__repr__()})'


class ConfigProperty:
    """
    Used in conjunction with ConfigPropertyMeta, allows extension classes to
    create properties that proxy to the config value, eg app.config.get(key)

    If key is left unspecified, in will be injected by ConfigPropertyMeta,
    defaulting to '{ext_class_name}_{property_name}'.upper()
    """
    def __init__(self, key=None):
        self.key = key

    def __get__(self, instance, cls):
        return current_app.config.get(self.key)


class ConfigPropertyMeta(type):
    """
    Use this metaclass to enable config properties on extension classes. I'm not
    sold on this being a good idea for *new* extensions, but for backwards
    compatibility with existing extensions that have silly __getattr__ magic, I
    think it's a big improvement. (NOTE: this only works when the application
    context is available, but that's no different than the behavior of what it's
    meant to replace)

    Example usage::

        class MyExtension(metaclass=ConfigPropertyMeta):
            __config_prefix__ = 'MY_EXTENSION'
            # if __config_prefix__ is unspecified, default is class_name.upper()

            foobar: Optional[FunctionType] = ConfigProperty()
            _custom: Optional[str] = ConfigProperty('MY_EXTENSION_CUSTOM')

        my_extension = MyExtension(app)
        my_extension.foobar == current_app.config.get('MY_EXTENSION_FOOBAR')
        my_extension._custom == current_app.config.get('MY_EXTENSION_CUSTOM')
    """
    def __init__(cls, class_name, bases, clsdict):
        super().__init__(class_name, bases, clsdict)
        config_prefix = clsdict.get('__config_prefix__', class_name).strip('_')
        for property_name, descriptor in clsdict.items():
            if isinstance(descriptor, ConfigProperty) and not descriptor.key:
                descriptor.key = f'{config_prefix}_{property_name}'.upper()


class _OptionalClassAttributes(type):
    __optional_class = None

    def __new__(mcs, name, bases, clsdict):
        if mcs.__optional_class is None:
            mcs.__optional_class = super().__new__(mcs, name, bases, clsdict)
        return mcs.__optional_class

    def __getattr__(self, item):
        return self.__optional_class

    def __setattr__(self, key, value):
        pass

    def __call__(self, *args, **kwargs):
        return self.__optional_class

    def __getitem__(self, item):
        return self.__optional_class

    def __setitem__(self, key, value):
        pass


class OptionalClass(metaclass=_OptionalClassAttributes):
    """
    Use this as a generic base class if you have classes that depend on an
    optional bundle. For example, if you want to define a serializer but not
    depend on flask_api_bundle, you should do something like this::

        try:
            from flask_api_bundle import ma
        except ImportError:
            from flask_unchained import OptionalClass as ma

        class MySerializer(ma.ModelSerializer):
            class Meta:
                model = 'MyModel'
    """
    def __init__(self, *args, **kwargs):
        pass


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
