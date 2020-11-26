import importlib
import os

from types import FunctionType
from typing import *

from ..flask_unchained import FlaskUnchained
from ..string_utils import right_replace, slugify, snake_case
from ..unchained import unchained


def _normalize_module_name(module_name):
    if module_name.endswith('.bundle'):
        return right_replace(module_name, '.bundle', '')
    return module_name


class BundleMetaclass(type):
    def __new__(mcs, name, bases, clsdict):
        # check if the user explicitly set module_name
        module_name = clsdict.get('module_name')
        if isinstance(module_name, str):
            clsdict['module_name'] = _normalize_module_name(module_name)
        return super().__new__(mcs, name, bases, clsdict)


class _BundleModuleNameDescriptor:
    def __get__(self, instance, cls):
        return _normalize_module_name(cls.__module__)

    def __set__(self, instance, value):
        raise AttributeError


class _BundleIsSingleModuleDescriptor:
    def __get__(self, instance, cls):
        return not importlib.util.find_spec(cls.module_name).submodule_search_locations

    def __set__(self, instance, value):
        raise AttributeError


class _BundleRootPathDescriptor:
    def __get__(self, instance, cls):
        module = importlib.import_module(cls.module_name)
        return os.path.dirname(module.__file__)

    def __set__(self, instance, value):
        raise AttributeError


class _BundleNameDescriptor:
    def __init__(self, *, strip_bundle_suffix: bool = False):
        self.strip_bundle_suffix = strip_bundle_suffix

    def __get__(self, instance, cls):
        if self.strip_bundle_suffix:
            return snake_case(right_replace(cls.__name__, 'Bundle', ''))
        return snake_case(cls.__name__)


class _BundleStaticFolderDescriptor:
    def __get__(self, instance, cls):
        if cls.is_single_module and issubclass(cls, AppBundle):
            return None  # this would be the same as the top-level static folder registered with Flask
        if not hasattr(instance, '_static_folder'):
            instance._static_folder = os.path.join(instance.root_path, 'static')
            if not os.path.exists(instance._static_folder):
                instance._static_folder = None
        return instance._static_folder


class _BundleStaticUrlPathDescriptor:
    def __get__(self, instance, cls):
        if instance._static_folders:
            return f'/{slugify(cls.name)}/static'


class _BundleTemplateFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(instance, '_template_folder'):
            instance._template_folder = os.path.join(instance.root_path, 'templates')
            if not os.path.exists(instance._template_folder):
                instance._template_folder = None
        return instance._template_folder


class Bundle(metaclass=BundleMetaclass):
    """
    Base class for bundles.

    Should be placed in your package's root or its ``bundle`` module::

        # your_bundle_package/__init__.py or your_bundle_package/bundle.py

        class YourBundle(Bundle):
            pass
    """

    name: str = _BundleNameDescriptor(strip_bundle_suffix=False)
    """
    Name of the bundle. Defaults to the snake_cased class name.
    """

    module_name: str = _BundleModuleNameDescriptor()
    """
    Top-level module name of the bundle (dot notation).

    Automatically determined; read-only.
    """

    root_path: str = _BundleRootPathDescriptor()
    """
    Root directory path of the bundle's package.

    Automatically determined; read-only.
    """

    template_folder: Optional[str] = _BundleTemplateFolderDescriptor()
    """
    Root directory path of the bundle's template folder. By default, if there exists
    a folder named ``templates`` in the bundle package
    :attr:`~flask_unchained.Bundle.root_path`, it will be used, otherwise ``None``.
    """

    static_folder: Optional[str] = _BundleStaticFolderDescriptor()
    """
    Root directory path of the bundle's static assets folder. By default, if there exists
    a folder named ``static`` in the bundle package
    :attr:`~flask_unchained.Bundle.root_path`, it will be used, otherwise ``None``.
    """

    static_url_path: Optional[str] = _BundleStaticUrlPathDescriptor()
    """
    Url path where this bundle's static assets will be served from. If
    :attr:`~flask_unchained.Bundle.static_folder` is set, this will default to
    ``/<bundle.name>/static``, otherwise ``None``.
    """

    is_single_module: bool = _BundleIsSingleModuleDescriptor()
    """
    Whether or not the bundle is a single module (Python file).

    Automatically determined; read-only.
    """

    default_load_from_module_name: Optional[str] = None
    """
    The default module name for hooks to load from. Set hooks' bundle modules override
    attributes for the modules you want in separate files.

    .. admonition:: WARNING - EXPERIMENTAL
        :class: danger

        Using this feature may cause mysterious exceptions to be thrown!!

        Best practice is to organize your code in separate modules.
    """

    _deferred_functions: List[FunctionType] = []
    """
    Deferred functions to be registered with the
    :class:`~flask_unchained.bundles.controller.bundle_blueprint.BundleBlueprint`
    that gets created for this bundle.

    The :class:`~flask_unchained.Unchained` extension copies these values from the
    :class:`DeferredBundleBlueprintFunctions` instance it created for this bundle.
    """

    def before_init_app(self, app: FlaskUnchained) -> None:
        """
        Override this method to perform actions on the
        :class:`~flask_unchained.FlaskUnchained` app instance *before* the
        ``unchained`` extension has initialized the application.
        """
        pass

    def after_init_app(self, app: FlaskUnchained) -> None:
        """
        Override this method to perform actions on the
        :class:`~flask_unchained.FlaskUnchained` app instance *after* the
        ``unchained`` extension has initialized the application.
        """
        pass

    def _iter_class_hierarchy(self, include_self: bool = True, mro: bool = False):
        """
        Iterate over the bundle classes in the hierarchy. Yields base-most
        instances first (aka opposite of Method Resolution Order).

        For internal use only.

        :param include_self: Whether or not to yield the top-level bundle.
        :param mro: Pass True to yield bundles in Method Resolution Order.
        """
        supers = self.__class__.__mro__[(0 if include_self else 1):]
        for bundle_cls in (supers if mro else reversed(supers)):
            if bundle_cls not in {object, AppBundle, Bundle}:
                if bundle_cls == self.__class__:
                    yield self
                else:
                    yield bundle_cls()

    @property
    def _has_views(self) -> bool:
        """
        Returns True if any of the bundles in the hierarchy has a views module.

        For internal use only.
        """
        if self.is_single_module and isinstance(self, AppBundle):
            return True

        from ..hooks.views_hook import ViewsHook

        for bundle in self._iter_class_hierarchy():
            if ViewsHook.import_bundle_modules(bundle):
                return True
        return False

    @property
    def _blueprint_name(self) -> str:
        """
        Get the name to use for the blueprint for this bundle.

        For internal use only.
        """
        if self._is_top_bundle or not self._has_hierarchy_name_conflicts:
            return self.name

        for i, bundle in enumerate(self._iter_class_hierarchy()):
            if bundle.__class__ == self.__class__:
                return f'{self.name}_{i}'

    @property
    def _static_folders(self) -> List[str]:
        """
        Get the list of static folders for this bundle.

        For internal use only.
        """
        if not self._has_hierarchy_name_conflicts:
            return [self.static_folder] if self.static_folder else []
        elif not self._is_top_bundle:
            return []

        return [b.static_folder for b in self._iter_class_hierarchy(mro=True)
                if b.static_folder and b.name == self.name]

    @property
    def _is_top_bundle(self) -> bool:
        """
        Whether or not this bundle is the top-most bundle in the hierarchy.

        For internal use only.
        """
        return not self.__class__.__subclasses__()

    @property
    def _has_hierarchy_name_conflicts(self) -> bool:
        """
        Whether or not there are any name conflicts between bundles in the hierarchy.

        For internal use only.
        """
        top_bundle = self.__class__
        subclasses = top_bundle.__subclasses__()
        while subclasses:
            top_bundle = subclasses[0]
            subclasses = top_bundle.__subclasses__()

        return any(b.name == self.name and b.__class__ != self.__class__
                   for b in top_bundle()._iter_class_hierarchy())

    def __getattr__(self, name):
        if name in {'before_request', 'after_request', 'teardown_request',
                    'context_processor', 'url_defaults', 'url_value_preprocessor',
                    'errorhandler'}:
            from warnings import warn
            warn('The app has already been initialized. Please register '
                 f'{name} sooner.')
            return

        raise AttributeError(name)

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} '
                f'name={self.name!r} '
                f'module={self.module_name!r}>')


class AppBundleMetaclass(BundleMetaclass):
    """
    Metaclass for :class:`~flask_unchained.AppBundle` to automatically set the
    user's subclass on the :class:`~flask_unchained.Unchained` extension instance.
    """
    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        unchained._app_bundle_cls = cls


class AppBundle(Bundle, metaclass=AppBundleMetaclass):
    """
    Like :class:`~flask_unchained.Bundle`, except used for the top-most
    application bundle.
    """

    name: str = _BundleNameDescriptor(strip_bundle_suffix=True)
    """
    Name of the bundle. Defaults to the snake_cased class name, excluding any
    "Bundle" suffix.
    """


__all__ = [
    'AppBundle',
    'AppBundleMetaclass',
    'Bundle',
    'BundleMetaclass',
]
