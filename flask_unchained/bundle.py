import importlib
import sys

from flask import Flask
from os import path
from typing import *

from .string_utils import right_replace, slugify, snake_case
from .utils import safe_import_module


def _normalize_module_name(module_name):
    if module_name.endswith('.bundle'):
        return right_replace(module_name, '.bundle', '')
    return module_name


class ModuleNameDescriptor:
    def __get__(self, instance, cls):
        return _normalize_module_name(cls.__module__)


class FolderDescriptor:
    def __get__(self, instance, cls):
        module = importlib.import_module(cls.module_name)
        return path.dirname(module.__file__)


class RootFolderDescriptor:
    def __get__(self, instance, cls):
        return path.dirname(cls.folder)


class NameDescriptor:
    def __get__(self, instance, cls):
        if issubclass(cls, AppBundle):
            return snake_case(right_replace(cls.__name__, 'Bundle', ''))
        return snake_case(cls.__name__)


class StaticFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(cls, '_static_folder'):
            bundle_dir = path.dirname(sys.modules[cls.module_name].__file__)
            cls._static_folder = path.join(bundle_dir, 'static')
            if not path.exists(cls._static_folder):
                cls._static_folder = None
        return cls._static_folder


class StaticUrlPathDescriptor:
    def __get__(self, instance, cls):
        if cls.static_folder:
            return f'/{slugify(cls.name)}/static'


class TemplateFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(cls, '_template_folder'):
            bundle_dir = path.dirname(sys.modules[cls.module_name].__file__)
            cls._template_folder = path.join(bundle_dir, 'templates')
            if not path.exists(cls._template_folder):
                cls._template_folder = None
        return cls._template_folder


class BundleMeta(type):
    def __new__(mcs, name, bases, clsdict):
        # check if the user explicitly set module_name
        module_name = clsdict.get('module_name')
        if isinstance(module_name, str):
            clsdict['module_name'] = _normalize_module_name(module_name)
        return super().__new__(mcs, name, bases, clsdict)

    def __repr__(cls):
        return f'class <Bundle name={cls.name!r} module={cls.module_name!r}>'


class Bundle(metaclass=BundleMeta):
    module_name: str = ModuleNameDescriptor()
    """Top-level module name of the bundle (dot notation)"""

    name: str = NameDescriptor()
    """Name of the bundle. Defaults to the snake cased class name"""

    folder: str = FolderDescriptor()
    """Root directory path of the bundle's package."""

    root_folder: str = RootFolderDescriptor()
    """Root directory path of the bundle."""

    template_folder: Optional[str] = TemplateFolderDescriptor()
    static_folder: Optional[str] = StaticFolderDescriptor()
    static_url_path: Optional[str] = StaticUrlPathDescriptor()

    _deferred_functions = []

    @classmethod
    def iter_class_hierarchy(cls, include_self=True, reverse=True):
        """
        Iterate over the bundle classes in the hierarchy. Yields base-most
        super classes first (aka opposite of Method Resolution Order).

        :param include_self: Whether or not to yield the top-level bundle.
        :param reverse: Pass False to yield bundles in Method Resolution Order.
        """
        supers = cls.__mro__[(0 if include_self else 1):]
        for bundle in (supers if not reverse else reversed(supers)):
            if issubclass(bundle, Bundle) and bundle not in {AppBundle, Bundle}:
                yield bundle

    @classmethod
    def before_init_app(cls, app: Flask):
        """
        Give bundles an opportunity to modify attributes on the Flask instance
        """
        pass

    @classmethod
    def after_init_app(cls, app: Flask):
        """
        Give bundles an opportunity to finalize app initialization
        """
        pass

    @classmethod
    def before_request(cls, fn):
        cls._defer(lambda bp: bp.before_request(fn))

    @classmethod
    def after_request(cls, fn):
        cls._defer(lambda bp: bp.after_request(fn))

    @classmethod
    def teardown_request(cls, fn):
        cls._defer(lambda bp: bp.teardown_request(fn))

    @classmethod
    def context_processor(cls, fn):
        cls._defer(lambda bp: bp.context_processor(fn))
        return fn

    @classmethod
    def url_defaults(cls, fn):
        cls._defer(lambda bp: bp.url_defaults(fn))
        return fn

    @classmethod
    def url_value_preprocessor(cls, fn):
        cls._defer(lambda bp: bp.url_value_preprocessor(fn))
        return fn

    @classmethod
    def errorhandler(cls, code_or_exception):
        def decorator(fn):
            cls._defer(lambda bp: bp.register_error_handler(code_or_exception, fn))
            return fn
        return decorator

    @classmethod
    def _has_views_module(cls):
        views_module_name = getattr(cls, 'views_module_name', 'views')
        return bool(safe_import_module(f'{cls.module_name}.{views_module_name}'))

    @classmethod
    def has_views(cls):
        for bundle in cls.iter_class_hierarchy():
            if bundle._has_views_module():
                return True
        return False

    @classmethod
    def _defer(cls, fn):
        cls._deferred_functions.append(fn)


class AppBundle(Bundle):
    pass
