import importlib
import os
import sys

from typing import *

from .flask_unchained import FlaskUnchained
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
        return os.path.dirname(module.__file__)


class RootFolderDescriptor:
    def __get__(self, instance, cls):
        return os.path.dirname(cls.folder)


class NameDescriptor:
    def __get__(self, instance, cls):
        if issubclass(cls, AppBundle):
            return snake_case(right_replace(cls.__name__, 'Bundle', ''))
        return snake_case(cls.__name__)


class StaticFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(instance, '_static_folder'):
            bundle_dir = os.path.dirname(sys.modules[instance.module_name].__file__)
            instance._static_folder = os.path.join(bundle_dir, 'static')
            if not os.path.exists(instance._static_folder):
                instance._static_folder = None
        return instance._static_folder


class StaticUrlPathDescriptor:
    def __get__(self, instance, cls):
        if cls.static_folders:
            return f'/{slugify(cls.name)}/static'


class TemplateFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(cls, '_template_folder'):
            bundle_dir = os.path.dirname(sys.modules[cls.module_name].__file__)
            cls._template_folder = os.path.join(bundle_dir, 'templates')
            if not os.path.exists(cls._template_folder):
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
        return f'<{cls.__name__} name={cls.name!r} module={cls.module_name!r}>'


class Bundle(metaclass=BundleMeta):
    """
    Base class for bundles.
    """

    module_name: str = ModuleNameDescriptor()
    """
    Top-level module name of the bundle (dot notation). Automatically determined.
    """

    name: str = NameDescriptor()
    """
    Name of the bundle. Defaults to the snake cased class name, unless it's your app
    bundle, in which case :python:`snake_case(right_replace(cls.__name__, 'Bundle', ''))`
    gets used instead.
    """

    folder: str = FolderDescriptor()
    """
    Root directory path of the bundle's package. Automatically determined.
    """

    root_folder: str = RootFolderDescriptor()
    """
    Root directory path of the bundle. Automatically determined.
    """

    template_folder: Optional[str] = TemplateFolderDescriptor()
    """
    Root directory path of the bundle's template folder. By default, if there exists
    a folder named ``templates`` in the bundle package
    :attr:`~flask_unchained.Bundle.folder`, it will be used, otherwise ``None``.
    """

    static_folder: Optional[str] = StaticFolderDescriptor()
    """
    Root directory path of the bundle's static assets folder. By default, if there exists
    a folder named ``static`` in the bundle package
    :attr:`~flask_unchained.Bundle.folder`, it will be used, otherwise ``None``.
    """

    static_url_path: Optional[str] = StaticUrlPathDescriptor()
    """
    Url path where this bundle's static assets will be served from. If
    :attr:`~flask_unchained.Bundle.static_folder` is set, this will default to
    ``/<bundle.name>/static``, otherwise ``None``.
    """

    _deferred_functions = []

    def before_init_app(self, app: FlaskUnchained):
        """
        Override this method to perform actions on the
        :class:`~flask_unchained.FlaskUnchained` app instance *before* the
        ``unchained`` extension has initialized the application.
        """
        pass

    def after_init_app(self, app: FlaskUnchained):
        """
        Override this method to perform actions on the
        :class:`~flask_unchained.FlaskUnchained` app instance *after* the
        ``unchained`` extension has initialized the application.
        """
        pass

    def iter_class_hierarchy(self, include_self=True, reverse=True):
        """
        Iterate over the bundle classes in the hierarchy. Yields base-most
        super classes first (aka opposite of Method Resolution Order).

        For internal use only.

        :param include_self: Whether or not to yield the top-level bundle.
        :param reverse: Pass False to yield bundles in Method Resolution Order.
        """
        supers = self.__class__.__mro__[(0 if include_self else 1):]
        for bundle in (supers if not reverse else reversed(supers)):
            if issubclass(bundle, Bundle) and bundle not in {AppBundle, Bundle}:
                if bundle == self.__class__:
                    yield self
                else:
                    yield bundle()

    def has_views(self):
        """
        Returns True if any of the bundles in the hierarchy has a views module.

        For internal use only.
        """
        for bundle in self.iter_class_hierarchy():
            if bundle._has_views_module():
                return True
        return False

    @property
    def blueprint_name(self):
        if self._is_top_bundle() or not self._has_hierarchy_name_conflicts():
            return self.name

        for i, bundle in enumerate(self.iter_class_hierarchy()):
            if bundle.__class__ == self.__class__:
                break
        return f'{self.name}_{i}'

    @property
    def static_folders(self):
        if not self._has_hierarchy_name_conflicts():
            return [self.static_folder] if self.static_folder else []
        elif not self._is_top_bundle():
            return []

        return [b.static_folder for b in self.iter_class_hierarchy(reverse=False)
                if b.static_folder and b.name == self.name]

    def _is_top_bundle(self):
        return not self.__class__.__subclasses__()

    def _has_hierarchy_name_conflicts(self):
        top_bundle = self.__class__
        subclasses = top_bundle.__subclasses__()
        while subclasses:
            top_bundle = subclasses[0]
            subclasses = top_bundle.__subclasses__()

        return any([b.name == self.name and b.__class__ != self.__class__
                    for b in top_bundle().iter_class_hierarchy()])

    def _has_views_module(self):
        views_module_name = getattr(self, 'views_module_name', 'views')
        return bool(safe_import_module(f'{self.module_name}.{views_module_name}'))


class AppBundle(Bundle):
    """
    Like :class:`Bundle`, except used to specify your bundle is the top-most application
    bundle.
    """
    pass
