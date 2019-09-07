import importlib
import os

from typing import *

from flask import Blueprint as _Blueprint, current_app
from flask.helpers import safe_join, send_file
from flask.blueprints import BlueprintSetupState as _BlueprintSetupState
from flask.helpers import _endpoint_from_view_func
from werkzeug.exceptions import BadRequest, NotFound

from ..flask_unchained import FlaskUnchained
from ..string_utils import right_replace, slugify, snake_case
from ..utils import safe_import_module


def _normalize_module_name(module_name):
    if module_name.endswith('.bundle'):
        return right_replace(module_name, '.bundle', '')
    return module_name


class _BundleMetaclass(type):
    def __new__(mcs, name, bases, clsdict):
        # check if the user explicitly set module_name
        module_name = clsdict.get('module_name')
        if isinstance(module_name, str):
            clsdict['module_name'] = _normalize_module_name(module_name)
        return super().__new__(mcs, name, bases, clsdict)


class _BundleModuleNameDescriptor:
    def __get__(self, instance, cls):
        return _normalize_module_name(cls.__module__)


class _BundleFolderDescriptor:
    def __get__(self, instance, cls):
        module = importlib.import_module(cls.module_name)
        return os.path.dirname(module.__file__)


class _BundleNameDescriptor:
    def __get__(self, instance, cls):
        if issubclass(cls, AppBundle):
            return snake_case(right_replace(cls.__name__, 'Bundle', ''))
        return snake_case(cls.__name__)


class _BundleStaticFolderDescriptor:
    def __get__(self, instance, cls):
        if not hasattr(instance, '_static_folder'):
            instance._static_folder = os.path.join(instance.folder, 'static')
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
            instance._template_folder = os.path.join(instance.folder, 'templates')
            if not os.path.exists(instance._template_folder):
                instance._template_folder = None
        return instance._template_folder


class _DeferredBundleFunctions:
    """
    The public interface for replacing Blueprints with Bundles.
    """

    def __init__(self):
        self._deferred_functions = []

    def _defer(self, fn):
        self._deferred_functions.append(fn)

    def before_request(self, fn):
        """
        Like :meth:`flask.Blueprint.before_request` but for a bundle. This function
        is only executed before each request that is handled by a view function
        of that bundle.
        """
        self._defer(lambda bp: bp.before_request(fn))

    def after_request(self, fn):
        """
        Like :meth:`flask.Blueprint.after_request` but for a bundle. This function
        is only executed after each request that is handled by a function of
        that bundle.
        """
        self._defer(lambda bp: bp.after_request(fn))

    def teardown_request(self, fn):
        """
        Like :meth:`flask.Blueprint.teardown_request` but for a bundle. This
        function is only executed when tearing down requests handled by a
        function of that bundle.  Teardown request functions are executed
        when the request context is popped, even when no actual request was
        performed.
        """
        self._defer(lambda bp: bp.teardown_request(fn))

    def context_processor(self, fn):
        """
        Like :meth:`flask.Blueprint.context_processor` but for a bundle. This
        function is only executed for requests handled by a bundle.
        """
        self._defer(lambda bp: bp.context_processor(fn))
        return fn

    def url_defaults(self, fn):
        """
        Callback function for URL defaults for this bundle. It's called
        with the endpoint and values and should update the values passed
        in place.
        """
        self._defer(lambda bp: bp.url_defaults(fn))
        return fn

    def url_value_preprocessor(self, fn):
        """
        Registers a function as URL value preprocessor for this
        bundle. It's called before the view functions are called and
        can modify the url values provided.
        """
        self._defer(lambda bp: bp.url_value_preprocessor(fn))
        return fn

    def errorhandler(self, code_or_exception):
        """
        Registers an error handler that becomes active for this bundle
        only.  Please be aware that routing does not happen local to a
        bundle so an error handler for 404 usually is not handled by
        a bundle unless it is caused inside a view function.  Another
        special case is the 500 internal server error which is always looked
        up from the application.

        Otherwise works as the :meth:`flask.Blueprint.errorhandler` decorator.
        """
        def decorator(fn):
            self._defer(lambda bp: bp.register_error_handler(code_or_exception, fn))
            return fn
        return decorator


class Bundle(metaclass=_BundleMetaclass):
    """
    Base class for bundles.
    """

    module_name: str = _BundleModuleNameDescriptor()
    """
    Top-level module name of the bundle (dot notation). Automatically determined.
    """

    name: str = _BundleNameDescriptor()
    """
    Name of the bundle. Defaults to the snake cased class name, unless it's your app
    bundle, in which case we strip off the "Bundle" suffix from the snake cased class
    name.
    """

    folder: str = _BundleFolderDescriptor()
    """
    Root directory path of the bundle's package. Automatically determined.
    """

    template_folder: Optional[str] = _BundleTemplateFolderDescriptor()
    """
    Root directory path of the bundle's template folder. By default, if there exists
    a folder named ``templates`` in the bundle package
    :attr:`~flask_unchained.Bundle.folder`, it will be used, otherwise ``None``.
    """

    static_folder: Optional[str] = _BundleStaticFolderDescriptor()
    """
    Root directory path of the bundle's static assets folder. By default, if there exists
    a folder named ``static`` in the bundle package
    :attr:`~flask_unchained.Bundle.folder`, it will be used, otherwise ``None``.
    """

    static_url_path: Optional[str] = _BundleStaticUrlPathDescriptor()
    """
    Url path where this bundle's static assets will be served from. If
    :attr:`~flask_unchained.Bundle.static_folder` is set, this will default to
    ``/<bundle.name>/static``, otherwise ``None``.
    """

    _deferred_functions = []
    """
    Deferred functions to be registered with the
    :class:`~flask_unchained.bundles.BundleBlueprint` that gets created
    for this bundle.

    The :class:`~flask_unchained.Unchained` extension copies these values from the
    :class:`_DeferredBundleFunctions` instance it created for this bundle.
    """

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

    def _iter_class_hierarchy(self, include_self=True, reverse=True):
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

    def _has_views(self):
        """
        Returns True if any of the bundles in the hierarchy has a views module.

        For internal use only.
        """
        for bundle in self._iter_class_hierarchy():
            if bundle._has_views_module():
                return True
        return False

    def _has_views_module(self):
        views_module_name = getattr(self, 'views_module_name', 'views')
        return bool(safe_import_module(f'{self.module_name}.{views_module_name}'))

    @property
    def _blueprint_name(self):
        if self._is_top_bundle() or not self._has_hierarchy_name_conflicts():
            return self.name

        for i, bundle in enumerate(self._iter_class_hierarchy()):
            if bundle.__class__ == self.__class__:
                break
        return f'{self.name}_{i}'

    @property
    def _static_folders(self):
        if not self._has_hierarchy_name_conflicts():
            return [self.static_folder] if self.static_folder else []
        elif not self._is_top_bundle():
            return []

        return [b.static_folder for b in self._iter_class_hierarchy(reverse=False)
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
                    for b in top_bundle()._iter_class_hierarchy()])

    def __getattr__(self, name):
        if name in {'before_request', 'after_request', 'teardown_request',
                    'context_processor', 'url_defaults', 'url_value_preprocessor',
                    'errorhandler'}:
            from warnings import warn
            warn('The app has already been initialized. Please register '
                 f'{name} sooner.')
            return

        raise AttributeError(name)

    def __repr__(self):
        return (f'<{self.__class__.__name__} '
                f'name={self.name!r} '
                f'module={self.module_name!r}>')


class AppBundle(Bundle):
    """
    Like :class:`Bundle`, except used to specify your bundle is the top-most
    application bundle.
    """
    pass


class _BundleBlueprintSetupState(_BlueprintSetupState):
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        A helper method to register a rule (and optionally a view function)
        to the application.  The endpoint is automatically prefixed with the
        blueprint's name.
        """
        if self.url_prefix:
            rule = self.url_prefix + rule
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, endpoint, view_func, defaults=defaults, **options)


class BundleBlueprint(_Blueprint):
    """
    This is a semi-private class to make blueprints compatible with bundles and
    their hierarchies. Bundle blueprints are created automatically for each bundle
    tht has a template folder and/or static folder. If *any* bundle in the hierarchy
    has views/routes that should be registered with the app, then those views/routes
    will get registered *only* with the :class:`BundleBlueprint` for the *top-most*
    bundle in the hierarchy.
    """
    url_prefix = None

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        super().__init__(bundle._blueprint_name, bundle.module_name,
                         static_url_path=bundle.static_url_path,
                         template_folder=bundle.template_folder)

    @property
    def has_static_folder(self):
        return bool(self.bundle._static_folders)

    def send_static_file(self, filename):
        if not self.has_static_folder:
            raise RuntimeError(f'No static folder found for {self.bundle.name}')
        # Ensure get_send_file_max_age is called in all cases.
        # Here, we ensure get_send_file_max_age is called for Blueprints.
        cache_timeout = self.get_send_file_max_age(filename)
        return _send_from_directories(self.bundle._static_folders, filename,
                                      cache_timeout=cache_timeout)

    def make_setup_state(self, app, options, first_registration=False):
        return _BundleBlueprintSetupState(self, app, options, first_registration)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        Like :meth:`~flask.Flask.add_url_rule` but for a blueprint.  The endpoint for
        the :func:`url_for` function is prefixed with the name of the blueprint.

        Overridden to allow dots in endpoint names
        """
        self.record(lambda s: s.add_url_rule(rule, endpoint, view_func,
                                             register_with_babel=False, **options))

    def register(self, app, options, first_registration=False):
        """
        Called by :meth:`~flask.Flask.register_blueprint` to register a blueprint
        on the application.  This can be overridden to customize the register
        behavior.  Keyword arguments from
        :func:`~flask.Flask.register_blueprint` are directly forwarded to this
        method in the `options` dictionary.
        """
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_registration)
        if self.has_static_folder:
            state.add_url_rule(self.static_url_path + '/<path:filename>',
                               view_func=self.send_static_file,
                               endpoint=f'{self.bundle._blueprint_name}.static',
                               register_with_babel=False)

        for deferred in self.bundle._deferred_functions:
            deferred(self)

        for deferred in self.deferred_functions:
            deferred(state)

    def __repr__(self):
        return f'BundleBlueprint(name={self.name!r}, bundle={self.bundle!r})'


def _send_from_directories(directories, filename, **options):
    """
    Send a file from the first directory it's found in with :func:`send_file`.
    This is a secure way to quickly expose static files from an upload folder
    or something similar.

    Example usage::

        @app.route('/uploads/<path:filename>')
        def download_file(filename):
            return send_from_directory(app.config.UPLOAD_FOLDER,
                                       filename, as_attachment=True)

    .. admonition:: Sending files and Performance

       It is strongly recommended to activate either ``X-Sendfile`` support in
       your webserver or (if no authentication happens) to tell the webserver
       to serve files for the given path on its own without calling into the
       web application for improved performance.

    :param directories: the list of directories to look for filename.
    :param filename: the filename relative to that directory to
                     download.
    :param options: optional keyword arguments that are directly
                    forwarded to :func:`send_file`.
    """
    for directory in directories:
        filename = safe_join(directory, filename)
        if not os.path.isabs(filename):
            filename = os.path.join(current_app.root_path, filename)
        try:
            if not os.path.isfile(filename):
                continue
        except (TypeError, ValueError):
            raise BadRequest()
        options.setdefault('conditional', True)
        return send_file(filename, **options)
    raise NotFound()


__all__ = [
    'AppBundle',
    'Bundle',
    'BundleBlueprint',
]
